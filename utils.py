"""
AtlasNexus Utilities Module
===========================
Common utility functions used throughout the application
"""

import json
import os
import secrets
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import configuration
try:
    from config import *
except ImportError:
    # Fallback if config.py doesn't exist
    DATA_DIR = 'data'
    SENDER_EMAIL = 'atlasnexushelp@gmail.com'
    SENDER_PASSWORD = ''
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587

# ====================
# File Operations
# ====================

def ensure_data_dir():
    """Ensure data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)

def load_json_db(file_path):
    """Load JSON database file with proper error handling"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle both list and dict returns
                if isinstance(data, list):
                    return data
                return data if data else {}
        return {}
    except json.JSONDecodeError:
        print(f"[ERROR] Corrupted JSON file: {file_path}")
        return {}
    except Exception as e:
        print(f"[ERROR] Failed to load {file_path}: {e}")
        return {}

def save_json_db(file_path, data):
    """Save JSON database file with proper error handling"""
    try:
        ensure_data_dir()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save {file_path}: {e}")
        return False

# ====================
# Security Functions
# ====================

def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)

def generate_secure_password():
    """Generate a secure password in format: word + 5 digits"""
    words = [
        'rabbit', 'tiger', 'eagle', 'falcon', 'dragon', 'phoenix', 
        'thunder', 'storm', 'ocean', 'mountain', 'forest', 'desert',
        'silver', 'golden', 'crystal', 'diamond', 'shadow', 'bright',
        'swift', 'strong', 'brave', 'noble', 'royal', 'mystic',
        'alpha', 'delta', 'gamma', 'omega', 'sigma', 'nexus'
    ]
    word = random.choice(words)
    digits = ''.join(str(random.randint(0, 9)) for _ in range(5))
    return f"{word}{digits}"

def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify a password against its hash"""
    return hash_password(password) == hashed

# ====================
# Email Functions
# ====================

def send_email(to_email, subject, html_content, retry_count=1):
    """Send email notification with retry logic"""
    if not SENDER_PASSWORD:
        print(f"[EMAIL] Would send to {to_email}: {subject}")
        return True  # Simulate success in development
    
    for attempt in range(retry_count + 1):
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = SENDER_EMAIL
            msg['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=5)
            try:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
                print(f"[EMAIL] Sent successfully to {to_email} (attempt {attempt + 1})")
                return True
            finally:
                try:
                    server.quit()
                except:
                    pass
                    
        except smtplib.SMTPAuthenticationError:
            print(f"[EMAIL ERROR] Authentication failed - check email credentials")
            return False
        except smtplib.SMTPException as e:
            print(f"[EMAIL ERROR] SMTP error on attempt {attempt + 1}: {e}")
            if attempt < retry_count:
                continue
        except Exception as e:
            print(f"[EMAIL ERROR] Unexpected error on attempt {attempt + 1}: {e}")
            if attempt < retry_count:
                continue
    
    return False

def send_email_async(to_email, subject, html_content):
    """Send email asynchronously in background thread"""
    try:
        thread = threading.Thread(target=send_email, args=(to_email, subject, html_content))
        thread.daemon = True
        thread.start()
        print(f"[EMAIL] Queued email to {to_email} for background sending")
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to queue email: {e}")

# ====================
# Date/Time Functions
# ====================

def is_expired(timestamp_str, hours=24):
    """Check if a timestamp is expired"""
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
        return datetime.now() > timestamp + timedelta(hours=hours)
    except:
        return True

def format_datetime(dt):
    """Format datetime for display"""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return dt
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def get_time_ago(timestamp_str):
    """Get human-readable time ago string"""
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
        delta = datetime.now() - timestamp
        
        if delta.days > 365:
            return f"{delta.days // 365} year{'s' if delta.days // 365 > 1 else ''} ago"
        elif delta.days > 30:
            return f"{delta.days // 30} month{'s' if delta.days // 30 > 1 else ''} ago"
        elif delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600} hour{'s' if delta.seconds // 3600 > 1 else ''} ago"
        elif delta.seconds > 60:
            return f"{delta.seconds // 60} minute{'s' if delta.seconds // 60 > 1 else ''} ago"
        else:
            return "just now"
    except:
        return "unknown"

# ====================
# Validation Functions
# ====================

def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Basic phone validation"""
    import re
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    # Check if it's mostly digits and reasonable length
    return cleaned.isdigit() and 7 <= len(cleaned) <= 15

def sanitize_input(text, max_length=None):
    """Sanitize user input"""
    if not text:
        return ""
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
    # Limit length if specified
    if max_length:
        text = text[:max_length]
    return text.strip()

# ====================
# IP Address Functions
# ====================

def get_ip_location(ip_address):
    """Get approximate location from IP (placeholder for future implementation)"""
    # This would typically use a geolocation API
    return "Unknown Location"

def is_private_ip(ip_address):
    """Check if IP is private/local"""
    private_ranges = [
        '10.',
        '172.16.', '172.17.', '172.18.', '172.19.',
        '172.20.', '172.21.', '172.22.', '172.23.',
        '172.24.', '172.25.', '172.26.', '172.27.',
        '172.28.', '172.29.', '172.30.', '172.31.',
        '192.168.',
        '127.',
        'localhost'
    ]
    return any(ip_address.startswith(range) for range in private_ranges)

# ====================
# Logging Functions
# ====================

def log_event(event_type, details, severity='INFO'):
    """Log an event with timestamp"""
    timestamp = datetime.now().isoformat()
    log_entry = {
        'timestamp': timestamp,
        'type': event_type,
        'severity': severity,
        'details': details
    }
    
    # In production, this would write to a proper logging service
    print(f"[{severity}] {event_type}: {details}")
    
    # Optionally save to file
    if os.environ.get('SAVE_LOGS') == 'true':
        log_file = os.path.join(DATA_DIR, 'events.log')
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except:
            pass
    
    return log_entry

# ====================
# Data Formatting Functions
# ====================

def format_currency(amount, currency='£'):
    """Format number as currency"""
    try:
        return f"{currency}{amount:,.2f}"
    except:
        return f"{currency}0.00"

def format_percentage(value, decimals=2):
    """Format number as percentage"""
    try:
        return f"{value:.{decimals}f}%"
    except:
        return "0.00%"

def format_number(value, decimals=0):
    """Format number with thousand separators"""
    try:
        if decimals > 0:
            return f"{value:,.{decimals}f}"
        return f"{value:,.0f}"
    except:
        return "0"

# ====================
# Session Management
# ====================

def create_session_id():
    """Create a unique session ID"""
    return secrets.token_urlsafe(32)

def is_session_valid(session_data, max_age_hours=24):
    """Check if a session is still valid"""
    if not session_data:
        return False
    
    created_at = session_data.get('created_at')
    if not created_at:
        return False
    
    try:
        created = datetime.fromisoformat(created_at)
        return datetime.now() < created + timedelta(hours=max_age_hours)
    except:
        return False

# ====================
# Rate Limiting
# ====================

class RateLimiter:
    """Simple in-memory rate limiter"""
    def __init__(self):
        self.attempts = {}
    
    def is_allowed(self, key, max_attempts=5, window_minutes=60):
        """Check if an action is allowed based on rate limits"""
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        if key not in self.attempts:
            self.attempts[key] = []
        
        # Clean old attempts
        self.attempts[key] = [
            attempt for attempt in self.attempts[key]
            if attempt > window_start
        ]
        
        # Check if under limit
        if len(self.attempts[key]) < max_attempts:
            self.attempts[key].append(now)
            return True
        
        return False
    
    def reset(self, key):
        """Reset attempts for a key"""
        if key in self.attempts:
            del self.attempts[key]

# Create global rate limiter instance
rate_limiter = RateLimiter()

# ====================
# HTML Template Helpers
# ====================

def generate_email_template(title, content, button_text=None, button_url=None):
    """Generate consistent email HTML template"""
    button_html = ""
    if button_text and button_url:
        button_html = f"""
        <div style="text-align: center; margin: 30px 0;">
            <a href="{button_url}" style="display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                {button_text}
            </a>
        </div>
        """
    
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; text-align: center;">{title}</h2>
                <div style="color: #666; line-height: 1.6;">
                    {content}
                </div>
                {button_html}
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px; text-align: center;">
                    AtlasNexus - Institutional Securitisation Platform<br>
                    This is an automated message, please do not reply.
                </p>
            </div>
        </body>
    </html>
    """

def escape_html(text):
    """Escape HTML special characters"""
    if not text:
        return ""
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text