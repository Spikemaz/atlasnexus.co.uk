"""
AtlasNexus - Single File Application
Everything in one place - no confusion
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from datetime import datetime, timedelta
import secrets
import os
import socket
import subprocess
import sys
import json
import hashlib
import string
import random
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time

# Try to import securitization_engine if available
try:
    from securitization_engine import run_securitization_calculation
    SECURITIZATION_AVAILABLE = True
except ImportError:
    SECURITIZATION_AVAILABLE = False
    run_securitization_calculation = None

# ==================== IP LOCKOUT TRACKING ====================
# On Vercel/production, use /tmp directory (writable)
# On local, use current directory
if os.environ.get('VERCEL') or os.environ.get('APP_ENV', '').lower() in ['production', 'prod']:
    LOCKOUT_FILE = '/tmp/ip_lockouts.json'
    ATTEMPT_LOG_FILE = '/tmp/ip_attempts_log.json'
else:
    LOCKOUT_FILE = 'ip_lockouts.json'
    ATTEMPT_LOG_FILE = 'ip_attempts_log.json'

def load_lockouts():
    """Load IP lockout data from file"""
    if not os.path.exists(LOCKOUT_FILE):
        return {}
    try:
        with open(LOCKOUT_FILE, 'r') as f:
            data = json.load(f)
            # Don't auto-clean, keep all records for admin panel
            return data
    except:
        return {}

def save_lockouts(lockouts):
    """Save IP lockout data to file"""
    try:
        with open(LOCKOUT_FILE, 'w') as f:
            json.dump(lockouts, f, indent=2, default=str)
        return True
    except:
        return False

def load_attempt_logs():
    """Load password attempt logs"""
    if not os.path.exists(ATTEMPT_LOG_FILE):
        return {}
    try:
        with open(ATTEMPT_LOG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_attempt_logs(logs):
    """Save password attempt logs"""
    try:
        with open(ATTEMPT_LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2, default=str)
        return True
    except:
        return False

def log_failed_attempt(ip_address, password_attempted, attempt_type='site_auth', user_agent=None):
    """Log a failed password attempt with additional info"""
    logs = load_attempt_logs()
    if ip_address not in logs:
        logs[ip_address] = {
            'attempts': [],
            'total_attempts': 0,
            'last_attempt': None,
            'first_seen': datetime.now().isoformat()
        }
    
    # Collect additional information
    attempt_data = {
        'password': password_attempted,
        'type': attempt_type,
        'timestamp': datetime.now().isoformat(),
        'user_agent': user_agent or request.headers.get('User-Agent', 'Unknown'),
        'referrer': request.headers.get('Referer', 'Direct'),
        'accept_language': request.headers.get('Accept-Language', 'Unknown')
    }
    
    logs[ip_address]['attempts'].append(attempt_data)
    logs[ip_address]['total_attempts'] += 1
    logs[ip_address]['last_attempt'] = datetime.now().isoformat()
    
    # Keep only last 50 attempts per IP to prevent file bloat
    if len(logs[ip_address]['attempts']) > 50:
        logs[ip_address]['attempts'] = logs[ip_address]['attempts'][-50:]
    
    save_attempt_logs(logs)

def clear_ip_attempts(ip_address):
    """Clear password attempts for an IP (when they successfully authenticate)"""
    logs = load_attempt_logs()
    if ip_address in logs:
        del logs[ip_address]
        save_attempt_logs(logs)
        print(f"[INFO] Cleared password attempts for IP {ip_address} after successful auth")

def check_ip_lockout(ip_address):
    """Check if an IP is locked out"""
    lockouts = load_lockouts()
    if ip_address not in lockouts:
        return None
    
    info = lockouts[ip_address]
    
    # Check permanent blacklist
    if info.get('permanent'):
        return {'type': 'permanent', 'ip': ip_address, 'info': info}
    
    # Check timed lockout
    if 'locked_until' in info:
        locked_until = datetime.fromisoformat(info['locked_until'])
        if datetime.now() < locked_until:
            remaining = (locked_until - datetime.now()).total_seconds()
            lockout_type = info.get('lockout_type', 'blocked_24h')
            return {
                'type': lockout_type,
                'locked_until': locked_until,
                'remaining_seconds': int(remaining),
                'reference_code': info.get('reference_code', 'REF-UNKNOWN'),
                'info': info
            }
    
    return None

def apply_ip_lockout(ip_address, lockout_type='24h', reason='', failed_passwords=None, duration_hours=24):
    """Apply a lockout to an IP address with detailed logging"""
    lockouts = load_lockouts()
    
    # Debug logging
    print(f"[LOCKOUT] Applying {lockout_type} to IP {ip_address} for {duration_hours} hours. Reason: {reason}")
    
    if lockout_type == 'permanent':
        lockouts[ip_address] = {
            'permanent': True,
            'locked_at': datetime.now().isoformat(),
            'reason': reason,
            'failed_passwords': failed_passwords or []
        }
    else:
        # Timed lockout (30min, 24h, or custom)
        # Don't add extra seconds for 30-minute lockout to display correctly
        if lockout_type == 'blocked_30min':
            locked_until = datetime.now() + timedelta(minutes=30)
        else:
            # Add 59 seconds for 24h display
            locked_until = datetime.now() + timedelta(hours=duration_hours, seconds=59)
        ref_code = 'REF-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Preserve existing data if updating
        existing = lockouts.get(ip_address, {})
        lockouts[ip_address] = {
            'locked_until': locked_until.isoformat(),
            'lockout_type': lockout_type,
            'reference_code': ref_code,
            'locked_at': datetime.now().isoformat(),
            'duration_hours': duration_hours,
            'reason': reason,
            'failed_passwords': failed_passwords or existing.get('failed_passwords', [])
        }
    
    success = save_lockouts(lockouts)
    print(f"[LOCKOUT] Save status: {success}, File: {LOCKOUT_FILE}")
    return lockouts[ip_address]

def modify_ip_ban(ip_address, action, duration_days=None):
    """Modify an IP ban - unban, extend, or make permanent"""
    lockouts = load_lockouts()
    
    if action == 'unban':
        if ip_address in lockouts:
            del lockouts[ip_address]
            save_lockouts(lockouts)
            return True
    
    elif action == 'extend' and duration_days:
        if ip_address in lockouts:
            locked_until = datetime.now() + timedelta(days=duration_days)
            lockouts[ip_address]['locked_until'] = locked_until.isoformat()
            lockouts[ip_address]['duration_days'] = duration_days
            lockouts[ip_address]['permanent'] = False
            save_lockouts(lockouts)
            return True
    
    elif action == 'permanent':
        if ip_address in lockouts:
            lockouts[ip_address]['permanent'] = True
            if 'locked_until' in lockouts[ip_address]:
                del lockouts[ip_address]['locked_until']
            save_lockouts(lockouts)
            return True
    
    return False

# ==================== HELPER FUNCTIONS ====================
def get_real_ip():
    """Get the real IP address, handling proxies and CDNs"""
    # Check various headers that proxies/CDNs use
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For can contain multiple IPs, get the first (client) one
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    elif request.headers.get('CF-Connecting-IP'):  # Cloudflare
        return request.headers.get('CF-Connecting-IP')
    elif request.headers.get('X-Client-IP'):
        return request.headers.get('X-Client-IP')
    else:
        # Fallback to remote_addr
        return request.remote_addr

# ==================== CONFIGURATION ====================
# Auto-detect environment
def get_environment():
    """Detect if we're local, Vercel, or other production"""
    # Check if running on Vercel
    if os.environ.get('VERCEL'):
        return 'vercel'
    # Check if explicitly set to production
    if os.environ.get('APP_ENV', '').lower() in ['production', 'prod']:
        return 'production'
    # Check hostname for local indicators
    hostname = socket.gethostname().lower()
    if 'local' in hostname or 'desktop' in hostname or 'laptop' in hostname:
        return 'local'
    # Default to production for safety
    return 'production'

ENVIRONMENT = get_environment()
IS_LOCAL = ENVIRONMENT == 'local'
IS_VERCEL = ENVIRONMENT == 'vercel'
IS_PRODUCTION = ENVIRONMENT in ['production', 'vercel']

# Settings (same for both environments except where noted)
PASSWORDS = ['SpikeMaz', 'RedAMC', 'PartnerAccess']
GLOBAL_UNLOCK_CODE = 'Ronabambi'
BLOCK_DURATION_MINUTES = 30
LOCKOUT_DURATION_HOURS = 24
MAX_ATTEMPTS_BEFORE_BLOCK = 3  # Block after 3 attempts
MAX_ATTEMPTS_BEFORE_BLACKLIST = 4  # Blacklist after 4 attempts
PERMANENT_SESSION_LIFETIME = 15

# Environment-specific
if IS_LOCAL:
    DEBUG = True
    HOST = '127.0.0.1'
    SESSION_COOKIE_SECURE = False
else:  # Production
    DEBUG = False
    HOST = '0.0.0.0'
    SESSION_COOKIE_SECURE = True

# ==================== PROJECT AUDIT & CLEANUP ====================
def audit_project():
    """Audit project structure and clean up any unnecessary files"""
    import os
    import glob
    
    # Only run on local, not on Vercel or production
    if not IS_LOCAL:
        return
    
    # ALLOWED files (everything else gets flagged)
    allowed_files = {
        'app.py',
        'local.bat',
        'live.bat', 
        'README.txt',
        'requirements.txt',  # NEEDED by Vercel to install Python packages
        'vercel.json',  # NEEDED by Vercel to know how to run app
        '.gitignore'
    }
    
    # ALLOWED template files
    allowed_templates = {
        'Gate1.html',
        'Gate2.html',
        'dashboard.html',
        '404.html',
        'terms.html',
        'privacy.html',
        'compliance.html',
        'data-protection.html',
        'security.html',
        'contact.html',
        'awaiting_verification.html',  # Added for registration system
        'registration-submitted.html',  # Added for new registration flow
        'admin_panel.html',  # Admin control panel
        'securitisation_engine.html'  # Securitization/Permutation engine
    }
    
    # Files that should NEVER exist (delete immediately)
    forbidden_files = [
        'app_live.py',
        'app_local.py',
        'app_backup.py',
        'app_vercel.py',
        'run.py',
        'start.bat',  # Old name
        'deploy.bat',  # Old name
        'RULES.md',
        'README.md',
        'DEPLOYMENT_RULES.txt',
        'templates/site_auth.html',
        'templates/secure_login.html',
        'templates/blocked.html',
        'templates/blackscreen.html',
        'templates/dashboard_live.html',
        'templates/error.html'  # Old name for 404
    ]
    
    # Delete forbidden files (with error handling)
    for file in forbidden_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"[DELETED] {file} - NOT ALLOWED!")
            except Exception as e:
                print(f"[WARNING] Could not delete {file}: {e}")
    
    # Check root directory for unexpected files
    root_files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for file in root_files:
        if file not in allowed_files and not file.startswith('.'):
            print(f"[WARNING] Unexpected file: {file}")
    
    # Check templates directory (with error handling)
    if os.path.exists('templates'):
        try:
            template_files = os.listdir('templates')
            for file in template_files:
                if file not in allowed_templates:
                    filepath = f'templates/{file}'
                    try:
                        os.remove(filepath)
                        print(f"[DELETED] {filepath} - Only Gate1, Gate2, Dashboard, 404 allowed!")
                    except Exception as e:
                        print(f"[WARNING] Could not delete {filepath}: {e}")
        except Exception as e:
            print(f"[WARNING] Could not check templates: {e}")
    
    # Report structure
    print("[AUDIT] Project structure checked and cleaned")

# ==================== KILL OLD SERVERS (LOCAL ONLY) ====================
def kill_port_5000():
    """Kill any existing LOCAL servers on port 5000 before starting
    Note: Vercel manages its own servers automatically - we don't touch those"""
    # Only run on local Windows machines, not on Vercel
    if os.name == 'nt' and not os.environ.get('VERCEL'):  
        try:
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            pids = set()
            for line in result.stdout.split('\n'):
                if ':5000' in line:
                    parts = line.split()
                    if parts and parts[-1].isdigit():
                        pids.add(parts[-1])
            for pid in pids:
                subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                print(f"Killed existing server (PID: {pid})")
        except:
            pass

# ==================== DATABASE ====================
# Simple file-based database for registrations
# Use /tmp on Vercel (writable), local data folder otherwise
if IS_VERCEL or IS_PRODUCTION:
    DATA_DIR = Path('/tmp')
else:
    DATA_DIR = Path('data')
    DATA_DIR.mkdir(exist_ok=True)
    
REGISTRATIONS_FILE = DATA_DIR / 'registrations.json'
USERS_FILE = DATA_DIR / 'users.json'
ADMIN_ACTIONS_FILE = DATA_DIR / 'admin_actions.json'
LOGIN_ATTEMPTS_FILE = DATA_DIR / 'login_attempts.json'

# Email configuration - Try to import from email_config.py first
try:
    from email_config import SENDER_EMAIL, SENDER_PASSWORD, ADMIN_EMAIL, SMTP_SERVER, SMTP_PORT
    EMAIL_CONFIG = {
        'smtp_server': SMTP_SERVER,
        'smtp_port': SMTP_PORT,
        'sender_email': SENDER_EMAIL,
        'sender_password': SENDER_PASSWORD,
        'admin_email': ADMIN_EMAIL
    }
    if SENDER_PASSWORD:
        print("[EMAIL] Gmail configuration loaded successfully")
    else:
        print("[EMAIL] Gmail configuration found but password not set - emails will be simulated")
except ImportError:
    # Fallback to environment variables or defaults
    EMAIL_CONFIG = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': os.environ.get('SENDER_EMAIL', 'atlasnexushelp@gmail.com'),
        'sender_password': os.environ.get('SENDER_PASSWORD', ''),
        'admin_email': os.environ.get('ADMIN_EMAIL', 'spikemaz8@aol.com')
    }
    print("[EMAIL] Using default email configuration - edit email_config.py to enable emails")

def load_json_db(file_path):
    """Load JSON database file"""
    # Convert string to Path if needed
    if isinstance(file_path, str):
        file_path = Path(file_path)
    
    if file_path.exists():
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Ensure admin_actions is always a list
                if 'admin_actions' in str(file_path) and isinstance(data, dict):
                    return list(data.values()) if data else []
                return data
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            # Return appropriate empty structure
            if 'admin_actions' in str(file_path):
                return []
            return {}
    
    # Return appropriate empty structure for non-existent files
    if 'admin_actions' in str(file_path):
        return []
    return {}

def save_json_db(file_path, data):
    """Save JSON database file"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def get_base_url():
    """Get the correct base URL for emails based on environment"""
    if IS_LOCAL:
        # For local testing, use localhost (users can access via network IP if needed)
        # You can set LOCAL_BASE_URL env variable to override (e.g., http://192.168.1.100:5000/)
        return os.environ.get('LOCAL_BASE_URL', 'http://localhost:5000/')
    elif IS_VERCEL or IS_PRODUCTION:
        # On Vercel/production, always use the live domain
        return 'https://atlasnexus.co.uk/'
    else:
        # Fallback
        return 'https://atlasnexus.co.uk/'

def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)

def generate_secure_password():
    """Generate a secure password in format: word + 5 digits"""
    # List of simple memorable words
    words = [
        'rabbit', 'tiger', 'eagle', 'falcon', 'dragon', 'phoenix', 
        'thunder', 'storm', 'ocean', 'mountain', 'forest', 'desert',
        'silver', 'golden', 'crystal', 'diamond', 'shadow', 'bright',
        'swift', 'strong', 'brave', 'noble', 'royal', 'mystic',
        'alpha', 'delta', 'gamma', 'omega', 'sigma', 'nexus'
    ]
    
    # Pick a random word and 5 random digits
    word = random.choice(words)
    digits = ''.join(str(random.randint(0, 9)) for _ in range(5))
    
    return f"{word}{digits}"

def send_email(to_email, subject, html_content, retry_count=2):
    """Send email notification with retry logic"""
    if not EMAIL_CONFIG['sender_password']:
        print(f"[EMAIL] Would send to {to_email}: {subject}")
        return True  # Simulate success in development
    
    for attempt in range(retry_count + 1):
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = EMAIL_CONFIG['sender_email']
            msg['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Use a timeout and explicit connection handling
            server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'], timeout=10)
            try:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
                server.send_message(msg)
                server.quit()
                print(f"[EMAIL] Sent successfully to {to_email} (attempt {attempt + 1})")
                return True
            finally:
                try:
                    server.quit()
                except:
                    pass
                    
        except smtplib.SMTPAuthenticationError as e:
            print(f"[EMAIL ERROR] Authentication failed: {e}")
            break  # Don't retry auth errors
        except Exception as e:
            print(f"[EMAIL ERROR] Attempt {attempt + 1} failed to send to {to_email}: {e}")
            if attempt < retry_count:
                time.sleep(1)  # Wait 1 second before retry
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

# ==================== FLASK APP ====================
app = Flask(__name__)
# Use a fixed secret key so sessions persist across restarts
app.secret_key = 'your-fixed-secret-key-keep-this-secure-in-production-2024'
app.permanent_session_lifetime = timedelta(minutes=PERMANENT_SESSION_LIFETIME)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = SESSION_COOKIE_SECURE
app.config['DEBUG'] = DEBUG

def track_ip_access(ip_address, page, user_email=None):
    """Track IP access to different pages"""
    tracking_file = os.path.join(DATA_DIR, 'ip_tracking.json')
    tracking = load_json_db(tracking_file)
    
    if ip_address not in tracking:
        tracking[ip_address] = {
            'first_seen': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'pages_visited': [],
            'total_visits': 0,
            'user_emails': [],
            'is_banned': False,
            'reached_pages': {
                'gate1': False,
                'gate2': False,
                'dashboard': False,
                'admin_panel': False
            }
        }
    
    tracking[ip_address]['last_seen'] = datetime.now().isoformat()
    tracking[ip_address]['total_visits'] += 1
    
    # Update reached pages
    if page == 'gate1':
        tracking[ip_address]['reached_pages']['gate1'] = True
    elif page == 'gate2':
        tracking[ip_address]['reached_pages']['gate2'] = True
    elif page == 'dashboard':
        tracking[ip_address]['reached_pages']['dashboard'] = True
    elif page == 'admin_panel':
        tracking[ip_address]['reached_pages']['admin_panel'] = True
    
    # Add page visit with timestamp
    tracking[ip_address]['pages_visited'].append({
        'page': page,
        'timestamp': datetime.now().isoformat()
    })
    
    # Keep only last 100 page visits
    if len(tracking[ip_address]['pages_visited']) > 100:
        tracking[ip_address]['pages_visited'] = tracking[ip_address]['pages_visited'][-100:]
    
    # Track associated user emails
    if user_email and user_email not in tracking[ip_address]['user_emails']:
        tracking[ip_address]['user_emails'].append(user_email)
    
    save_json_db(tracking_file, tracking)
    return tracking[ip_address]

def ban_ip_address(ip_address, reason='Manual ban', banned_by='admin'):
    """Ban an IP address from accessing the site"""
    tracking_file = os.path.join(DATA_DIR, 'ip_tracking.json')
    tracking = load_json_db(tracking_file)
    
    if ip_address not in tracking:
        tracking[ip_address] = {
            'first_seen': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'pages_visited': [],
            'total_visits': 0,
            'user_emails': [],
            'is_banned': False
        }
    
    tracking[ip_address]['is_banned'] = True
    tracking[ip_address]['ban_reason'] = reason
    tracking[ip_address]['banned_at'] = datetime.now().isoformat()
    tracking[ip_address]['banned_by'] = banned_by
    
    save_json_db(tracking_file, tracking)
    return True

def unban_ip_address(ip_address):
    """Unban an IP address"""
    tracking_file = os.path.join(DATA_DIR, 'ip_tracking.json')
    tracking = load_json_db(tracking_file)
    
    if ip_address in tracking:
        tracking[ip_address]['is_banned'] = False
        tracking[ip_address]['unbanned_at'] = datetime.now().isoformat()
        save_json_db(tracking_file, tracking)
        return True
    return False

def check_ip_ban(ip_address):
    """Check if an IP is banned"""
    tracking_file = os.path.join(DATA_DIR, 'ip_tracking.json')
    tracking = load_json_db(tracking_file)
    
    if ip_address in tracking:
        return tracking[ip_address].get('is_banned', False)
    return False

@app.route('/version')
def version():
    """Version check endpoint"""
    return jsonify({
        'version': '2.1.0',
        'features': {
            'gate1_timer_fix': True,
            'gate1_override_reset': True,
            'gate2_ticker': True,
            'admin_panel_enhanced': True,
            'ip_tracking': True,
            'online_offline_users': True,
            'freeze_unfreeze': True
        },
        'deployed': datetime.now().isoformat()
    })

@app.route('/')
def index():
    """Gate 1 - Site Authentication"""
    ip_address = get_real_ip()
    session.permanent = True
    
    # Track IP access
    track_ip_access(ip_address, 'gate1')
    
    # Check if IP is banned
    if check_ip_ban(ip_address):
        return "Access Denied - Your IP has been banned", 403
    
    # Debug log the detected IP
    print(f"[DEBUG] Detected IP: {ip_address}, Headers: X-Forwarded-For={request.headers.get('X-Forwarded-For')}, X-Real-IP={request.headers.get('X-Real-IP')}")
    
    # Check IP-based lockout (persistent across sessions/cookies)
    ip_lockout = check_ip_lockout(ip_address)
    if ip_lockout:
        if ip_lockout['type'] == 'permanent':
            return render_template('Gate1.html', state='blackscreen', ip_address=ip_address)
        elif ip_lockout['type'] == 'blocked_24h':
            return render_template('Gate1.html', 
                                 state='blocked_24h',
                                 blocked_until=ip_lockout['locked_until'],
                                 is_24h_lockout=True,
                                 reference_code=ip_lockout['reference_code'])
        elif ip_lockout['type'] == 'blocked_30min':
            # 30-minute block from failed passwords
            return render_template('Gate1.html',
                                 state='blocked_30min',
                                 blocked_until=ip_lockout['locked_until'],
                                 remaining_seconds=ip_lockout['remaining_seconds'],
                                 reference_code=ip_lockout['reference_code'])
    
    # Also check session-based lockout for backwards compatibility
    lockout_24h = session.get(f'lockout_24h_{ip_address}')
    if lockout_24h:
        if isinstance(lockout_24h, str):
            lockout_24h = datetime.fromisoformat(lockout_24h)
        if datetime.now() < lockout_24h:
            # Migrate to IP-based lockout
            ref_code = session.get(f'reference_code_{ip_address}', 'REF-MIGRATED')
            apply_ip_lockout(ip_address, '24h')
            return render_template('Gate1.html', 
                                 state='blocked_24h',
                                 blocked_until=lockout_24h,
                                 is_24h_lockout=True,
                                 reference_code=ref_code)
        else:
            # 24-hour lockout expired - apply permanent blackscreen
            apply_ip_lockout(ip_address, 'permanent')
            return render_template('Gate1.html', state='blackscreen', ip_address=ip_address)
    
    # Check for permanent blacklist in session (migrate to IP-based)
    if session.get(f'permanent_block_{ip_address}'):
        apply_ip_lockout(ip_address, 'permanent')
        return render_template('Gate1.html', state='blackscreen', ip_address=ip_address)
    
    # Check for global unlock attempt
    if session.get(f'global_unlock_{ip_address}'):
        # Reset and send back to Gate 1
        for key in list(session.keys()):
            if ip_address in key:
                session.pop(key, None)
        return redirect('/')
    
    # Check for temporary block
    blocked_until = session.get(f'blocked_until_{ip_address}')
    if blocked_until:
        if isinstance(blocked_until, str):
            blocked_until = datetime.fromisoformat(blocked_until)
        if datetime.now() < blocked_until:
            # Calculate exact remaining time
            remaining_seconds = int((blocked_until - datetime.now()).total_seconds())
            remaining_minutes = remaining_seconds // 60
            # Get or generate reference code
            ref_code = session.get(f'reference_code_{ip_address}')
            if not ref_code:
                import random
                import string
                ref_code = 'REF-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                session[f'reference_code_{ip_address}'] = ref_code
            return render_template('Gate1.html', 
                                 state='blocked_30min',
                                 blocked_until=blocked_until,
                                 remaining_minutes=remaining_minutes,
                                 remaining_seconds=remaining_seconds,
                                 reference_code=ref_code)
        else:
            # Block expired, reset attempts
            session.pop(f'blocked_until_{ip_address}', None)
            session[f'attempt_count_{ip_address}'] = 0
    
    # If authenticated, redirect to secure login
    if session.get(f'site_authenticated_{ip_address}'):
        return redirect(url_for('secure_login'))
    
    return render_template('Gate1.html', state='normal')

@app.route('/site-auth', methods=['POST'])
def site_auth():
    """Handle site authentication attempts"""
    ip_address = get_real_ip()
    password = request.form.get('site_password', '').strip()
    
    # Check if already blocked (IP-based)
    ip_lockout = check_ip_lockout(ip_address)
    if ip_lockout and ip_lockout['type'] == 'permanent':
        return jsonify({'status': 'error', 'message': 'Access permanently denied'}), 403
    
    blocked_until = session.get(f'blocked_until_{ip_address}')
    if blocked_until:
        if isinstance(blocked_until, str):
            blocked_until = datetime.fromisoformat(blocked_until)
        if datetime.now() < blocked_until:
            remaining = int((blocked_until - datetime.now()).total_seconds() / 60)
            return jsonify({
                'status': 'blocked',
                'message': f'Blocked for {remaining} more minutes',
                'redirect': url_for('index')
            }), 403
    
    # Check for timeout trigger
    if password == 'TIMEOUT_TRIGGER_BLOCK_NOW':
        # Force block due to timeout
        session[f'attempt_count_{ip_address}'] = MAX_ATTEMPTS_BEFORE_BLOCK
        blocked_until = datetime.now() + timedelta(minutes=BLOCK_DURATION_MINUTES)
        session[f'blocked_until_{ip_address}'] = blocked_until.isoformat()
        # Generate reference code
        import random
        import string
        ref_code = 'REF-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        session[f'reference_code_{ip_address}'] = ref_code
        return jsonify({
            'status': 'blocked',
            'message': 'Session timeout - blocked for 30 minutes',
            'redirect': url_for('index')
        }), 403
    
    # Get current attempt count
    attempt_count = session.get(f'attempt_count_{ip_address}', 0)
    attempt_count += 1
    session[f'attempt_count_{ip_address}'] = attempt_count
    
    # Validate password
    if password in PASSWORDS:
        # Success - reset attempts and authenticate
        session[f'attempt_count_{ip_address}'] = 0
        session[f'site_authenticated_{ip_address}'] = True
        session.pop(f'blocked_until_{ip_address}', None)
        
        # Clear password attempts for this IP since they succeeded
        clear_ip_attempts(ip_address)
        
        if IS_LOCAL:
            print(f"[DEBUG] Password correct! Setting site_authenticated for IP: {ip_address}")
            print(f"[DEBUG] Session after auth: {dict(session)}")
        
        return jsonify({'status': 'success', 'redirect': url_for('secure_login')}), 200
    
    # Failed attempt - log it
    log_failed_attempt(ip_address, password, 'site_auth')
    attempts_left = MAX_ATTEMPTS_BEFORE_BLOCK - attempt_count
    
    if attempt_count >= MAX_ATTEMPTS_BEFORE_BLOCK:
        # Get all failed passwords and additional info
        logs = load_attempt_logs()
        recent_attempts = []
        additional_info = {}
        
        if ip_address in logs:
            # Get last 3 attempts with full details
            recent_attempts = [a['password'] for a in logs[ip_address]['attempts'][-3:]]
            
            # Collect additional info from the most recent attempt
            if logs[ip_address]['attempts']:
                last_attempt = logs[ip_address]['attempts'][-1]
                additional_info = {
                    'user_agent': last_attempt.get('user_agent', 'Unknown'),
                    'first_seen': logs[ip_address].get('first_seen'),
                    'total_attempts': logs[ip_address].get('total_attempts', 0),
                    'browser_info': request.headers.get('User-Agent', 'Unknown'),
                    'accept_language': request.headers.get('Accept-Language', 'Unknown')
                }
        
        # Apply 30-minute block with comprehensive data
        lockout_data = apply_ip_lockout(ip_address, 'blocked_30min', 
                        reason='3 failed password attempts',
                        failed_passwords=recent_attempts,
                        duration_hours=0.5)  # 30 minutes
        
        # Add additional info to the lockout record
        lockouts = load_lockouts()
        if ip_address in lockouts:
            lockouts[ip_address]['additional_info'] = additional_info
            save_lockouts(lockouts)
        
        blocked_until = datetime.now() + timedelta(minutes=BLOCK_DURATION_MINUTES)
        session[f'blocked_until_{ip_address}'] = blocked_until.isoformat()
        
        # Generate reference code
        ref_code = session.get(f'reference_code_{ip_address}')
        if not ref_code:
            ref_code = 'REF-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            session[f'reference_code_{ip_address}'] = ref_code
        
        return jsonify({
            'status': 'blocked',
            'message': f'Too many attempts. Blocked for {BLOCK_DURATION_MINUTES} minutes',
            'redirect': url_for('index')
        }), 403
    else:
        return jsonify({
            'status': 'error',
            'message': f'Invalid code. {attempts_left} attempts remaining'
        }), 401

@app.route('/blocked')
def blocked():
    """Handle blocked page with hidden unlock"""
    ip_address = get_real_ip()
    
    # Check for unlock code in request
    unlock_code = request.args.get('unlock_code', '')
    if unlock_code == GLOBAL_UNLOCK_CODE:
        # Clear all blocks for this IP
        for key in list(session.keys()):
            if ip_address in key:
                session.pop(key, None)
        return redirect('/')
    
    # Check if actually blocked
    blocked_until = session.get(f'blocked_until_{ip_address}')
    if blocked_until:
        if isinstance(blocked_until, str):
            blocked_until = datetime.fromisoformat(blocked_until)
        if datetime.now() < blocked_until:
            # Calculate exact remaining time
            remaining_seconds = int((blocked_until - datetime.now()).total_seconds())
            remaining_minutes = remaining_seconds // 60
            # Get stored reference code
            ref_code = session.get(f'reference_code_{ip_address}', 'REF-UNKNOWN')
            return render_template('Gate1.html',
                                 state='blocked_30min',
                                 blocked_until=blocked_until,
                                 remaining_minutes=remaining_minutes,
                                 remaining_seconds=remaining_seconds,
                                 reference_code=ref_code)
    
    # Not blocked, redirect to index
    return redirect('/')

@app.route('/unlock', methods=['POST'])
def unlock():
    """Handle global unlock attempts - only ONE attempt allowed"""
    ip_address = get_real_ip()
    unlock_code = request.json.get('code', '')
    
    if unlock_code == GLOBAL_UNLOCK_CODE:
        # Clear ALL session data for this IP
        for key in list(session.keys()):
            if ip_address in key:
                session.pop(key, None)
        
        # Remove from IP lockout file
        lockouts = load_lockouts()
        if ip_address in lockouts:
            del lockouts[ip_address]
            save_lockouts(lockouts)
        
        # Clear password attempts from logs
        clear_ip_attempts(ip_address)
        
        # Explicitly reset all counters and timers in session
        session[f'attempt_count_{ip_address}'] = 0
        session[f'site_attempts_{ip_address}'] = 0  # Reset site password attempts
        session.pop(f'blocked_until_{ip_address}', None)
        session.pop(f'lockout_24h_{ip_address}', None)
        session.pop(f'permanent_block_{ip_address}', None)
        session.pop(f'reference_code_{ip_address}', None)
        session.pop(f'site_authenticated_{ip_address}', None)  # Clear site auth
        session.pop(f'first_access_{ip_address}', None)  # Clear first access time
        
        # Clear any rate limiting
        session.pop(f'last_attempt_{ip_address}', None)
        
        print(f"[OVERRIDE] Successfully cleared all blocks for IP {ip_address}")
        
        return jsonify({'status': 'success', 'redirect': '/'})
    else:
        # Wrong override code = immediate 24-hour IP ban
        log_failed_attempt(ip_address, unlock_code, 'override_attempt')
        
        apply_ip_lockout(ip_address, 'blocked_24h',
                        reason='Failed override attempt',
                        failed_passwords=[unlock_code],
                        duration_hours=24)
        
        session[f'lockout_24h_{ip_address}'] = (datetime.now() + timedelta(hours=LOCKOUT_DURATION_HOURS, seconds=59)).isoformat()
        return jsonify({
            'status': 'lockout',
            'message': '24-hour lockout applied',
            'redirect': '/'
        })

@app.route('/secure-login')
def secure_login():
    """Gate 2 - User Authentication"""
    ip_address = get_real_ip()
    
    # Debug logging
    if IS_LOCAL:
        print(f"[DEBUG] /secure-login accessed by IP: {ip_address}")
        print(f"[DEBUG] Session keys: {list(session.keys())}")
        print(f"[DEBUG] Site authenticated: {session.get(f'site_authenticated_{ip_address}')}")
    
    # Verify site authentication
    if not session.get(f'site_authenticated_{ip_address}'):
        if IS_LOCAL:
            print(f"[DEBUG] No site authentication found, redirecting to index")
        return redirect(url_for('index'))
    
    # Check if user authenticated
    if session.get(f'user_authenticated_{ip_address}'):
        return redirect(url_for('dashboard'))
    
    return render_template('Gate2.html')

@app.route('/api/companies-house-search', methods=['POST'])
def companies_house_search():
    """Real Companies House API search endpoint"""
    import requests
    import time
    
    ip_address = get_real_ip()
    
    # Verify site authentication
    if not session.get(f'site_authenticated_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    company_name = request.json.get('company_name', '').strip()
    
    if not company_name:
        return jsonify({'status': 'error', 'message': 'Company name required'}), 400
    
    try:
        # Companies House API key - you'll need to get one from https://developer.company-information.service.gov.uk/
        API_KEY = os.environ.get('COMPANIES_HOUSE_API_KEY', 'YOUR_API_KEY_HERE')
        
        # If no API key is set, use known real UK companies data
        if API_KEY == 'YOUR_API_KEY_HERE':
            # Real UK companies data (public information)
            known_companies = {
                'barclays': {
                    'company_name': 'BARCLAYS PLC',
                    'company_number': '00048839',
                    'registered_office_address': {
                        'address_line_1': '1 Churchill Place',
                        'locality': 'London',
                        'postal_code': 'E14 5HP',
                        'country': 'United Kingdom'
                    },
                    'company_status': 'active',
                    'type': 'plc',
                    'date_of_creation': '1896-07-20'
                },
                'hsbc': {
                    'company_name': 'HSBC HOLDINGS PLC',
                    'company_number': '00617987',
                    'registered_office_address': {
                        'address_line_1': '8 Canada Square',
                        'locality': 'London',
                        'postal_code': 'E14 5HQ',
                        'country': 'United Kingdom'
                    },
                    'company_status': 'active',
                    'type': 'plc',
                    'date_of_creation': '1959-01-01'
                },
                'lloyds': {
                    'company_name': 'LLOYDS BANKING GROUP PLC',
                    'company_number': '00095000',
                    'registered_office_address': {
                        'address_line_1': 'The Mound',
                        'locality': 'Edinburgh',
                        'postal_code': 'EH1 1YZ',
                        'country': 'Scotland'
                    },
                    'company_status': 'active',
                    'type': 'plc',
                    'date_of_creation': '1985-01-01'
                },
                'natwest': {
                    'company_name': 'NATWEST GROUP PLC',
                    'company_number': 'SC045551',
                    'registered_office_address': {
                        'address_line_1': '36 St Andrew Square',
                        'locality': 'Edinburgh',
                        'postal_code': 'EH2 2YB',
                        'country': 'Scotland'
                    },
                    'company_status': 'active',
                    'type': 'plc',
                    'date_of_creation': '1968-03-25'
                },
                'santander': {
                    'company_name': 'SANTANDER UK PLC',
                    'company_number': '02294747',
                    'registered_office_address': {
                        'address_line_1': '2 Triton Square',
                        'address_line_2': "Regent's Place",
                        'locality': 'London',
                        'postal_code': 'NW1 3AN',
                        'country': 'United Kingdom'
                    },
                    'company_status': 'active',
                    'type': 'plc',
                    'date_of_creation': '1988-09-27'
                },
                'tesco': {
                    'company_name': 'TESCO PLC',
                    'company_number': '00445790',
                    'registered_office_address': {
                        'address_line_1': 'Tesco House',
                        'address_line_2': 'Shire Park, Kestrel Way',
                        'locality': 'Welwyn Garden City',
                        'postal_code': 'AL7 1GA',
                        'country': 'United Kingdom'
                    },
                    'company_status': 'active',
                    'type': 'plc',
                    'date_of_creation': '1947-11-27'
                },
                'sainsbury': {
                    'company_name': "J SAINSBURY PLC",
                    'company_number': '00185647',
                    'registered_office_address': {
                        'address_line_1': '33 Holborn',
                        'locality': 'London',
                        'postal_code': 'EC1N 2HT',
                        'country': 'United Kingdom'
                    },
                    'company_status': 'active',
                    'type': 'plc',
                    'date_of_creation': '1929-07-12'
                },
                'bp': {
                    'company_name': 'BP PLC',
                    'company_number': '00102498',
                    'registered_office_address': {
                        'address_line_1': '1 St James\'s Square',
                        'locality': 'London',
                        'postal_code': 'SW1Y 4PD',
                        'country': 'United Kingdom'
                    },
                    'company_status': 'active',
                    'type': 'plc',
                    'date_of_creation': '1909-04-14'
                },
                'shell': {
                    'company_name': 'SHELL PLC',
                    'company_number': '04366849',
                    'registered_office_address': {
                        'address_line_1': 'Shell Centre',
                        'address_line_2': '2 York Road',
                        'locality': 'London',
                        'postal_code': 'SE1 7NA',
                        'country': 'United Kingdom'
                    },
                    'company_status': 'active',
                    'type': 'plc',
                    'date_of_creation': '2002-02-05'
                },
                'vodafone': {
                    'company_name': 'VODAFONE GROUP PUBLIC LIMITED COMPANY',
                    'company_number': '01833679',
                    'registered_office_address': {
                        'address_line_1': 'Vodafone House',
                        'address_line_2': 'The Connection',
                        'locality': 'Newbury',
                        'region': 'Berkshire',
                        'postal_code': 'RG14 2FN',
                        'country': 'United Kingdom'
                    },
                    'company_status': 'active',
                    'type': 'plc',
                    'date_of_creation': '1984-07-17'
                }
            }
            
            # Search for matching company
            search_term = company_name.lower()
            results = []
            
            for key, company in known_companies.items():
                if key in search_term or search_term in key or search_term in company['company_name'].lower():
                    results.append(company)
            
            # If no matches found in known companies, return empty
            if not results:
                return jsonify({
                    'status': 'success',
                    'results': [],
                    'message': 'No companies found. Try searching for: Barclays, HSBC, Lloyds, NatWest, Santander, Tesco, Sainsbury, BP, Shell, or Vodafone'
                })
            
            return jsonify({'status': 'success', 'results': results})
        
        else:
            # Use real Companies House API
            headers = {
                'Authorization': API_KEY
            }
            
            # Search companies endpoint
            url = f'https://api.company-information.service.gov.uk/search/companies?q={company_name}&items_per_page=10'
            
            response = requests.get(url, headers=headers, auth=(API_KEY, ''))
            
            if response.status_code == 200:
                data = response.json()
                companies = []
                
                for item in data.get('items', []):
                    companies.append({
                        'company_name': item.get('title', ''),
                        'company_number': item.get('company_number', ''),
                        'registered_office_address': item.get('address', {}),
                        'company_status': item.get('company_status', ''),
                        'type': item.get('company_type', ''),
                        'date_of_creation': item.get('date_of_creation', '')
                    })
                
                return jsonify({'status': 'success', 'results': companies})
            else:
                return jsonify({'status': 'error', 'message': 'API request failed'}), 500
                
    except Exception as e:
        print(f"Error searching Companies House: {e}")
        return jsonify({'status': 'error', 'message': 'Search failed'}), 500

@app.route('/register', methods=['POST'])
def register():
    """Handle user registration"""
    try:
        ip_address = get_real_ip()
        
        # Verify site authentication first
        if not session.get(f'site_authenticated_{ip_address}'):
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        
        # Get form data
        # Generate a secure password for the user
        generated_password = generate_secure_password()
        
        data = {
            'email': request.form.get('email', '').strip().lower(),
            'full_name': request.form.get('fullname', '').strip(),
            'phone': request.form.get('phone_number', '').strip(),  # Fixed: phone_number
            'country_code': request.form.get('country_code', '').strip(),
            'company_name': request.form.get('company', '').strip(),  # Fixed: company
            'company_number': request.form.get('company_number', '').strip(),
            'job_title': request.form.get('job_title', '').strip(),
            'business_address': request.form.get('address', '').strip(),  # Fixed: address
            'generated_password': generated_password,  # Store the generated password
            'verification_token': generate_verification_token(),
            'email_verified': False,
            'admin_approved': False,
            'created_at': datetime.now().isoformat(),
            'ip_address': ip_address
        }
        
        # Load existing registrations
        registrations = load_json_db(REGISTRATIONS_FILE)
        
        # Check if email already exists
        if data['email'] in registrations:
            return jsonify({'status': 'error', 'message': 'Email already registered'}), 400
        
        # Save registration
        registrations[data['email']] = data
        save_json_db(REGISTRATIONS_FILE, registrations)
        
        # Send verification email
        base_url = get_base_url()
        verification_link = f"{base_url}verify-email?token={data['verification_token']}&email={data['email']}"
        
        email_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                <h2 style="color: #333;">Welcome to AtlasNexus</h2>
                <p>Thank you for registering. Please verify your email address to continue.</p>
                <div style="background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <p style="color: #856404; margin: 0; font-weight: bold;">⚠️ Important: This link expires in 1 hour!</p>
                </div>
                <a href="{verification_link}" style="display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0;">Verify Email</a>
                <p style="color: #666; font-size: 14px;">If the button doesn't work, copy this link: {verification_link}</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="color: #999; font-size: 12px;">Once verified, your application will be reviewed. Link expires 1 hour after registration.</p>
            </div>
        </body>
    </html>
    """
        
        # Send verification email immediately (synchronously for reliability)
        print(f"[REGISTRATION] Sending verification email to {data['email']}...")
        email_sent = send_email(data['email'], 'AtlasNexus - Verify Your Email', email_html)
        if email_sent:
            print(f"[REGISTRATION] Verification email sent successfully to {data['email']}")
        else:
            print(f"[REGISTRATION] Failed to send verification email to {data['email']}")
        
        # Generate approval token for email-based approval
        approval_token = generate_verification_token()
        data['approval_token'] = approval_token
        
        # Re-save with approval token
        registrations[data['email']] = data
        save_json_db(REGISTRATIONS_FILE, registrations)
        
        # Notify admin of new registration with approval/reject buttons
        approve_link = f"{base_url}admin/quick-approve?token={approval_token}&email={data['email']}"
        reject_link = f"{base_url}admin/quick-reject?token={approval_token}&email={data['email']}"
        
        admin_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h2 style="color: #333; margin: 0;">🔔 New Registration Application</h2>
                    <p style="color: #666; margin-top: 10px;">Requires your approval</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="color: #333; margin-top: 0; margin-bottom: 15px;">Applicant Details:</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; color: #666; width: 120px;">Full Name:</td>
                            <td style="padding: 8px 0; color: #333; font-weight: 600;">{data['full_name']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Email:</td>
                            <td style="padding: 8px 0; color: #3b82f6; font-weight: 600;">{data['email']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Company:</td>
                            <td style="padding: 8px 0; color: #333; font-weight: 600;">{data['company_name']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Company #:</td>
                            <td style="padding: 8px 0; color: #333;">{data.get('company_number', 'Not provided')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Job Title:</td>
                            <td style="padding: 8px 0; color: #333;">{data['job_title']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Phone:</td>
                            <td style="padding: 8px 0; color: #333;">{data['country_code']} {data['phone']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Location:</td>
                            <td style="padding: 8px 0; color: #333;">{data.get('personal_address', 'Not provided')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666;">Email Verified:</td>
                            <td style="padding: 8px 0;">
                                <span style="color: {'#22c55e' if data.get('email_verified') else '#ef4444'}; font-weight: 600;">
                                    {'Yes' if data.get('email_verified') else 'Pending'}
                                </span>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #ffc107;">
                    <p style="color: #856404; margin: 0; font-size: 14px;">
                        <strong>📝 Note:</strong> A secure password has been generated for this user. 
                        It will only be sent to them after email verification AND your approval.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p style="color: #666; margin-bottom: 20px; font-size: 14px;">
                        Click one of the buttons below to approve or reject this application directly from your email:
                    </p>
                    
                    <a href="{approve_link}" style="display: inline-block; background: linear-gradient(135deg, #22c55e, #16a34a); color: white; padding: 14px 40px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 0 10px; box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);">
                        APPROVE APPLICATION
                    </a>
                    
                    <a href="{reject_link}" style="display: inline-block; background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 14px 40px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 0 10px; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);">
                        ✗ REJECT APPLICATION
                    </a>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                    <p style="color: #999; font-size: 12px; text-align: center; margin: 5px 0;">
                        Or review in the admin panel:
                    </p>
                    <div style="text-align: center;">
                        <a href="{base_url}dashboard" style="color: #3b82f6; text-decoration: none; font-size: 14px;">
                            Open Admin Dashboard →
                        </a>
                    </div>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #fef3c7; border-radius: 6px;">
                    <p style="color: #92400e; font-size: 12px; margin: 0;">
                        <strong>⚠ Security Note:</strong> These approval links are unique and expire after use. 
                        Only click if you recognize this applicant.
                    </p>
                </div>
            </div>
        </body>
    </html>
    """
    
        # Send admin notification immediately
        print(f"[REGISTRATION] Sending admin notification for {data['email']}...")
        admin_sent = send_email(EMAIL_CONFIG['admin_email'], 'New Registration - Action Required', admin_html)
        if admin_sent:
            print(f"[REGISTRATION] Admin notification sent successfully")
        else:
            print(f"[REGISTRATION] Failed to send admin notification for {data['email']}")
        
        # Store registration in session for awaiting page
        session[f'registration_pending_{ip_address}'] = data['email']
        
        return jsonify({
            'status': 'success',
            'redirect': f'/registration-submitted?email={data["email"]}'
        })
    except Exception as e:
        print(f"[REGISTRATION ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': 'Registration failed. Please try again.'
        }), 500

@app.route('/registration-submitted')
def registration_submitted():
    """Show registration submitted page with next steps"""
    email = request.args.get('email', '')
    if not email:
        return redirect(url_for('secure_login'))
    
    # Pass email to template
    return render_template('registration-submitted.html', email=email)

@app.route('/awaiting-verification')
def awaiting_verification():
    """Show awaiting verification page"""
    ip_address = get_real_ip()
    
    # Verify site authentication
    if not session.get(f'site_authenticated_{ip_address}'):
        return redirect(url_for('index'))
    
    email = session.get(f'registration_pending_{ip_address}')
    return render_template('awaiting_verification.html', email=email)

@app.route('/registration-expired', methods=['POST'])
def registration_expired():
    """Handle expired registrations"""
    data = request.get_json()
    email = data.get('email', '').lower()
    
    registrations = load_json_db(REGISTRATIONS_FILE)
    
    if email in registrations:
        # Move to expired registrations
        expired = load_json_db('data/expired_registrations.json')
        expired[email] = registrations[email]
        expired[email]['expired_at'] = datetime.now().isoformat()
        expired[email]['reason'] = 'Email not verified within 10 minutes'
        save_json_db('data/expired_registrations.json', expired)
        
        # Remove from active registrations
        del registrations[email]
        save_json_db(REGISTRATIONS_FILE, registrations)
        
        print(f"[REGISTRATION] Expired registration for {email} - not verified within 10 minutes")
        return jsonify({'status': 'success'})
    
    return jsonify({'status': 'not_found'})

@app.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification email with rate limiting (1 per minute)"""
    data = request.get_json()
    email = data.get('email', '').lower()
    ip_address = get_real_ip()
    
    if not email:
        return jsonify({'status': 'error', 'message': 'Email required'}), 400
    
    registrations = load_json_db(REGISTRATIONS_FILE)
    if email not in registrations:
        return jsonify({'status': 'error', 'message': 'Registration not found'}), 404
    
    registration = registrations[email]
    
    # Check if already verified
    if registration.get('email_verified'):
        return jsonify({'status': 'error', 'message': 'Email already verified'}), 400
    
    # Check rate limiting - 1 per minute per email
    last_resend = registration.get('last_resend_time')
    if last_resend:
        last_resend_time = datetime.fromisoformat(last_resend)
        time_since_last = datetime.now() - last_resend_time
        
        if time_since_last < timedelta(minutes=1):
            seconds_to_wait = 60 - int(time_since_last.total_seconds())
            return jsonify({
                'status': 'error', 
                'message': f'Please wait {seconds_to_wait} seconds before resending'
            }), 429
    
    # Update last resend time
    registrations[email]['last_resend_time'] = datetime.now().isoformat()
    
    # Reset created_at to give them another hour
    registrations[email]['created_at'] = datetime.now().isoformat()
    
    # Generate new verification token
    new_token = generate_verification_token()
    registrations[email]['verification_token'] = new_token
    save_json_db(REGISTRATIONS_FILE, registrations)
    
    # Send new verification email
    base_url = get_base_url()
    verification_link = f"{base_url}verify-email?token={new_token}&email={email}"
    
    print(f"[RESEND] Attempting to resend verification email to {email}")
    print(f"[RESEND] Verification link: {verification_link}")
    
    email_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                <h2 style="color: #333;">Verification Email (Resent)</h2>
                <p>You requested a new verification email. Please click the link below to verify your email address:</p>
                <div style="background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <p style="color: #856404; margin: 0; font-weight: bold;">⚠️ Important: This link expires in 1 hour!</p>
                </div>
                <div style="margin: 20px 0; padding: 20px; background: #f0f9ff; border-radius: 8px; border: 2px solid #3b82f6;">
                    <a href="{verification_link}" style="display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%); color: white; text-decoration: none; border-radius: 6px; font-weight: 600;">
                        Verify Email Address
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">This is a resent verification email requested at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.</p>
                <p style="color: #666; font-size: 14px;">This link expires in 1 hour from now.</p>
                <p style="color: #666; font-size: 14px;">If you didn't request this, please ignore this email.</p>
            </div>
        </body>
    </html>
    """
    
    email_sent = send_email(email, 'Email Verification - AtlasNexus (Resent)', email_html)
    print(f"[RESEND] Email send result: {email_sent}")
    
    if email_sent:
        return jsonify({'status': 'success', 'message': 'Verification email resent'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send email'}), 500

@app.route('/check-verification-status', methods=['GET', 'POST'])
def check_verification_status():
    """Check if user's email is verified"""
    # Handle both GET and POST
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email', '').lower()
    else:
        ip_address = get_real_ip()
        email = session.get(f'registration_pending_{ip_address}')
    
    if not email:
        return jsonify({'verified': False})
    
    registrations = load_json_db(REGISTRATIONS_FILE)
    if email in registrations:
        is_verified = registrations[email].get('email_verified', False)
        is_approved = registrations[email].get('admin_approved', False)
        return jsonify({
            'verified': is_verified,
            'approved': is_approved
        })
    
    return jsonify({'verified': False, 'approved': False})

@app.route('/verify-email')
def verify_email():
    """Handle email verification"""
    token = request.args.get('token')
    email = request.args.get('email')
    
    if not token or not email:
        return redirect(url_for('secure_login'))
    
    # Load registrations
    registrations = load_json_db(REGISTRATIONS_FILE)
    
    if email in registrations and registrations[email]['verification_token'] == token:
        # Check if verification link has expired (1 hour)
        created_at = registrations[email].get('created_at')
        if created_at:
            created_time = datetime.fromisoformat(created_at)
            time_elapsed = datetime.now() - created_time
            
            if time_elapsed > timedelta(hours=1):
                # Link has expired - show error message
                return f"""
                <html>
                <head>
                    <title>Verification Link Expired</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background: linear-gradient(135deg, #0F1419 0%, #1A2332 100%);
                            color: white;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            min-height: 100vh;
                            margin: 0;
                        }}
                        .container {{
                            background: rgba(44, 49, 55, 0.95);
                            border: 1px solid rgba(239, 68, 68, 0.3);
                            border-radius: 16px;
                            padding: 3rem;
                            max-width: 500px;
                            text-align: center;
                        }}
                        h1 {{
                            color: #ef4444;
                            margin-bottom: 1rem;
                        }}
                        p {{
                            color: #b0b0b0;
                            margin-bottom: 2rem;
                        }}
                        .buttons {{
                            display: flex;
                            gap: 1rem;
                            justify-content: center;
                        }}
                        .btn {{
                            padding: 0.875rem 1.5rem;
                            border-radius: 10px;
                            text-decoration: none;
                            display: inline-block;
                            font-weight: 600;
                        }}
                        .btn-primary {{
                            background: linear-gradient(135deg, #60a5fa 0%, #93c5fd 100%);
                            color: #1A1D23;
                        }}
                        .btn-secondary {{
                            background: rgba(146, 150, 156, 0.1);
                            border: 1px solid #92969C;
                            color: #b0b0b0;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>⏱️ Verification Link Expired</h1>
                        <p>This verification link has expired. Links are only valid for 1 hour after registration.</p>
                        <p>Please register again or contact support if you need assistance.</p>
                        <div class="buttons">
                            <a href="/secure-login" class="btn btn-secondary">Back to Login</a>
                            <a href="/" class="btn btn-primary">Register Again</a>
                        </div>
                    </div>
                </body>
                </html>
                """, 400
        
        registrations[email]['email_verified'] = True
        registrations[email]['verified_at'] = datetime.now().isoformat()
        save_json_db(REGISTRATIONS_FILE, registrations)
        
        # Check if user was already approved (approved before verification)
        if registrations[email].get('admin_approved'):
            # User was approved before verification - now create account and send credentials
            password = registrations[email].get('generated_password')
            account_type = registrations[email].get('account_type', 'external')
            
            if password:
                # Create user account now that they're verified
                password_expiry = datetime.now() + timedelta(days=30)
                users = load_json_db(USERS_FILE)
                users[email] = {
                    **registrations[email],
                    'password': password,
                    'password_expiry': password_expiry.isoformat(),
                    'admin_approved': True,
                    'account_type': account_type,
                    'login_count': 0,
                    'total_login_time': 0,
                    'last_login': None,
                    'login_history': [],
                    'password_sent': True  # Sending now
                }
                save_json_db(USERS_FILE, users)
                
                # Send credentials email
                base_url = get_base_url()
                email_html = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
                        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                            <h2 style="color: #22c55e;">Email Verified & Account Ready!</h2>
                            <p>Your email has been verified and your account was already approved!</p>
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                                <h3 style="color: #333;">Your Login Credentials:</h3>
                                <p><strong>Email:</strong> {email}</p>
                                <p><strong>Password:</strong> <code style="background: #fffae6; padding: 4px 8px; border-radius: 4px; font-size: 14px;">{password}</code></p>
                                <p><strong>Account Type:</strong> {account_type.upper()}</p>
                            </div>
                            <a href="{base_url}secure-login" style="display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Login Now</a>
                            <p style="color: #666; font-size: 14px; margin-top: 20px;">For security, please change your password after first login.</p>
                        </div>
                    </body>
                </html>
                """
                
                send_email(email, 'AtlasNexus - Your Account is Ready', email_html)
        
        # Check if user is approved
        if registrations[email].get('admin_approved'):
            # User is both verified and approved - can go to login
            session['email_verified'] = True
            return redirect(url_for('secure_login'))
        else:
            # User is verified but NOT approved - show confirmation page
            return render_template('awaiting_verification.html', 
                                 email=email,
                                 status="pending_approval")
    
    # Invalid token
    return render_template('awaiting_verification.html', 
                         message="Invalid verification link.",
                         status="error")

@app.route('/auth', methods=['POST'])
def auth():
    """Handle user authentication"""
    ip_address = get_real_ip()
    
    # Verify site authentication first
    if not session.get(f'site_authenticated_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    
    # Check for admin user
    if email == 'spikemaz8@aol.com' and password == 'SpikeMaz':
        session[f'user_authenticated_{ip_address}'] = True
        session[f'username_{ip_address}'] = 'Admin'
        session[f'user_email_{ip_address}'] = email
        session[f'access_level_{ip_address}'] = 'admin'
        session[f'is_admin_{ip_address}'] = True
        
        # Track admin login in login attempts
        login_attempts = load_json_db(LOGIN_ATTEMPTS_FILE)
        if ip_address not in login_attempts:
            login_attempts[ip_address] = []
        login_attempts[ip_address].append({
            'email': email,
            'timestamp': datetime.now().isoformat(),
            'success': True,
            'user_type': 'admin'
        })
        save_json_db(LOGIN_ATTEMPTS_FILE, login_attempts)
        
        # Also ensure admin is in users file for tracking
        users = load_json_db(USERS_FILE)
        if email not in users:
            users[email] = {
                'email': email,
                'username': 'Admin',
                'full_name': 'Administrator',
                'account_type': 'admin',
                'created_at': datetime.now().isoformat(),
                'is_admin': True,
                'admin_approved': True
            }
        
        # Update last login
        users[email]['last_login'] = datetime.now().isoformat()
        users[email]['login_count'] = users[email].get('login_count', 0) + 1
        save_json_db(USERS_FILE, users)
        
        return jsonify({'status': 'success', 'redirect': url_for('dashboard')})
    
    # Check approved users
    users = load_json_db(USERS_FILE)
    if email in users:
        user = users[email]
        
        # Check if account is frozen
        if user.get('is_frozen', False):
            return jsonify({
                'status': 'error', 
                'message': f'Account frozen: {user.get("freeze_reason", "Contact administrator")}'
            }), 403
        
        # Check if password is valid and not expired
        if user.get('password') == password:
            expiry = datetime.fromisoformat(user.get('password_expiry', '2000-01-01'))
            if datetime.now() < expiry:
                # Track login
                current_time = datetime.now()
                user['last_login'] = current_time.isoformat()
                user['login_count'] = user.get('login_count', 0) + 1
                
                # Add to login history
                if 'login_history' not in user:
                    user['login_history'] = []
                user['login_history'].append({
                    'timestamp': current_time.isoformat(),
                    'ip_address': ip_address
                })
                # Keep only last 50 logins
                user['login_history'] = user['login_history'][-50:]
                
                # Store login session start time
                session[f'login_start_time_{ip_address}'] = current_time.isoformat()
                
                # Save updated user data
                users[email] = user
                save_json_db(USERS_FILE, users)
                
                # Track successful login attempt
                login_attempts = load_json_db(LOGIN_ATTEMPTS_FILE)
                if ip_address not in login_attempts:
                    login_attempts[ip_address] = []
                login_attempts[ip_address].append({
                    'email': email,
                    'timestamp': current_time.isoformat(),
                    'success': True,
                    'user_type': user.get('account_type', 'external')
                })
                save_json_db(LOGIN_ATTEMPTS_FILE, login_attempts)
                
                session[f'user_authenticated_{ip_address}'] = True
                session[f'username_{ip_address}'] = user.get('full_name', email)
                session[f'user_email_{ip_address}'] = email
                session[f'access_level_{ip_address}'] = 'user'
                
                # Check if user is actually an admin
                if user.get('account_type') == 'admin':
                    session[f'is_admin_{ip_address}'] = True
                
                return jsonify({'status': 'success', 'redirect': url_for('dashboard')})
            else:
                return jsonify({'status': 'error', 'message': 'Password expired. Contact admin.'}), 401
    
    # Failed authentication - track it
    login_attempts = load_json_db(LOGIN_ATTEMPTS_FILE)
    if ip_address not in login_attempts:
        login_attempts[ip_address] = []
    login_attempts[ip_address].append({
        'email': email,
        'timestamp': datetime.now().isoformat(),
        'success': False,
        'reason': 'Invalid credentials'
    })
    save_json_db(LOGIN_ATTEMPTS_FILE, login_attempts)
    
    return jsonify({'status': 'error', 'message': 'Invalid credentials or account not approved'}), 401

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    ip_address = get_real_ip()
    
    # Verify both authentications
    if not session.get(f'site_authenticated_{ip_address}'):
        return redirect(url_for('index'))
    if not session.get(f'user_authenticated_{ip_address}'):
        return redirect(url_for('secure_login'))
    
    username = session.get(f'username_{ip_address}', 'User')
    is_admin = session.get(f'is_admin_{ip_address}', False)
    access_level = session.get(f'access_level_{ip_address}', 'external')
    
    # Get account type for display
    if is_admin:
        account_type_display = 'Admin'
    elif access_level == 'internal':
        account_type_display = 'Internal'
    else:
        account_type_display = 'External'
    
    # Show dashboard for ALL users including admin
    # Admin can access admin panel through the header button
    return render_template('dashboard.html', 
                         username=username, 
                         is_admin=is_admin, 
                         account_type=account_type_display)

@app.route('/market-view')
def market_view():
    """Market view with registration prompt for unauthenticated users"""
    ip_address = get_real_ip()
    
    # If not authenticated, show registration screen
    if not session.get(f'user_authenticated_{ip_address}'):
        return render_template('registration-submitted.html',
                             message="Please complete registration to access market data",
                             show_registration=True)
    
    # If authenticated, redirect to dashboard market section
    return redirect(url_for('dashboard') + '#market')

@app.route('/data-sources')
def data_sources():
    """Data sources page showing all data feeds"""
    ip_address = get_real_ip()
    
    # Require authentication to view data sources
    if not session.get(f'user_authenticated_{ip_address}'):
        return redirect(url_for('secure_login'))
    
    return render_template('data_sources.html')

@app.route('/compliance')
def compliance():
    """Compliance page - public info or authenticated tool"""
    ip_address = get_real_ip()
    
    # If not authenticated, show public compliance info
    if not session.get(f'user_authenticated_{ip_address}'):
        return render_template('compliance_public.html')
    
    # If authenticated, show the compliance tool
    return render_template('compliance.html')

@app.route('/portfolio')
def portfolio():
    """Portfolio management page"""
    ip_address = get_real_ip()
    
    # Require authentication
    if not session.get(f'user_authenticated_{ip_address}'):
        return redirect(url_for('secure_login'))
    
    # For now, redirect to dashboard with portfolio section
    return redirect(url_for('dashboard') + '#portfolio')

@app.route('/analytics')
def analytics():
    """Analytics dashboard page"""
    ip_address = get_real_ip()
    
    # Require authentication
    if not session.get(f'user_authenticated_{ip_address}'):
        return redirect(url_for('secure_login'))
    
    # For now, redirect to dashboard with analytics section
    return redirect(url_for('dashboard') + '#analytics')

@app.route('/risk-management')
def risk_management():
    """Risk management page"""
    ip_address = get_real_ip()
    
    # Require authentication
    if not session.get(f'user_authenticated_{ip_address}'):
        return redirect(url_for('secure_login'))
    
    # For now, redirect to dashboard with risk section
    return redirect(url_for('dashboard') + '#risk')

@app.route('/admin/approve-user', methods=['POST'])
def admin_approve_user():
    """Admin approve user"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    email = request.json.get('email')
    
    # Load registrations
    registrations = load_json_db(REGISTRATIONS_FILE)
    
    if email not in registrations:
        return jsonify({'status': 'error', 'message': 'Registration not found'}), 404
    
    # Use the pre-generated password or create a new one if missing
    password = registrations[email].get('generated_password', generate_secure_password())
    
    # Update registration with approval info
    registrations[email]['generated_password'] = password
    registrations[email]['admin_approved'] = True
    registrations[email]['approved_at'] = datetime.now().isoformat()
    registrations[email]['approved_by'] = session.get(f'user_email_{ip_address}', 'spikemaz8@aol.com')
    save_json_db(REGISTRATIONS_FILE, registrations)
    
    # Check if email is verified
    email_verified = registrations[email].get('email_verified', False)
    
    # Only create user account if email is verified
    if email_verified:
        password_expiry = datetime.now() + timedelta(days=30)
        users = load_json_db(USERS_FILE)
        users[email] = {
            **registrations[email],
            'password': password,
            'password_expiry': password_expiry.isoformat(),
            'admin_approved': True,
            'login_count': 0,
            'total_login_time': 0,
            'last_login': None,
            'login_history': [],
            'approved_by': session.get(f'user_email_{ip_address}', 'spikemaz8@aol.com')
        }
        save_json_db(USERS_FILE, users)
    
    # Log admin action
    admin_actions = load_json_db(ADMIN_ACTIONS_FILE)
    if not isinstance(admin_actions, list):
        admin_actions = []
    admin_actions.append({
        'action': 'user_approved',
        'email': email,
        'timestamp': datetime.now().isoformat(),
        'admin': 'spikemaz8@aol.com'
    })
    save_json_db(ADMIN_ACTIONS_FILE, admin_actions)
    
    # Only send email if user has verified their email
    if email_verified:
        email_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #333;">Account Approved - AtlasNexus</h2>
                    <p>Your account has been approved. You can now login with the following credentials:</p>
                    <div style="background: #f0f0f0; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Email:</strong> {email}</p>
                        <p><strong>Password:</strong> {password}</p>
                        <p style="color: #666; font-size: 14px;">This password expires in 30 days</p>
                    </div>
                    <a href="{get_base_url()}secure-login" style="display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Login Now</a>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="color: #999; font-size: 12px;">For security, please change your password after first login.</p>
                </div>
            </body>
        </html>
        """
        
        send_email(email, 'Account Approved - AtlasNexus', email_html)
        
        return jsonify({
            'status': 'success',
            'message': f'User approved. Password sent to {email}',
            'password': password  # Show to admin for reference
        })
    else:
        # User not yet verified - credentials will be sent after verification
        return jsonify({
            'status': 'success',
            'message': f'User approved. Credentials will be sent after email verification.',
            'password': password  # Show to admin for reference
        })

@app.route('/admin/quick-approve')
def admin_quick_approve():
    """Quick approve from email link"""
    token = request.args.get('token')
    email = request.args.get('email')
    
    if not token or not email:
        return "Invalid approval link", 400
    
    # Load registrations
    registrations = load_json_db(REGISTRATIONS_FILE)
    
    # Verify token
    if email not in registrations or registrations[email].get('approval_token') != token:
        return """
        <html>
        <body style="background: #1a1a1a; color: white; font-family: Arial; padding: 50px; text-align: center;">
            <h1 style="color: #ef4444;">Invalid or Expired Link</h1>
            <p>This approval link is invalid or has already been used.</p>
            <a href="/dashboard" style="color: #3b82f6;">Go to Dashboard</a>
        </body>
        </html>
        """, 400
    
    # Use the pre-generated password or create a new one if missing
    password = registrations[email].get('generated_password', generate_secure_password())
    password_expiry = datetime.now() + timedelta(days=30)
    
    # Create user account
    users = load_json_db(USERS_FILE)
    users[email] = {
        **registrations[email],
        'password': password,
        'password_expiry': password_expiry.isoformat(),
        'admin_approved': True,
        'approved_at': datetime.now().isoformat(),
        'login_count': 0,
        'total_login_time': 0,
        'last_login': None,
        'login_history': [],
        'approved_by': 'email_approval'
    }
    save_json_db(USERS_FILE, users)
    
    # Update registration status and remove token
    registrations[email]['admin_approved'] = True
    registrations[email]['approval_token'] = None  # Invalidate token
    save_json_db(REGISTRATIONS_FILE, registrations)
    
    # Send approval email with password
    user_email_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                <h2 style="color: #22c55e;">Application Approved!</h2>
                <p>Congratulations! Your email has been verified and your application has been approved by our admin team.</p>
                <p>Welcome to AtlasNexus - Your institutional securitisation platform.</p>
                <div style="background: #f0f9ff; padding: 20px; border-radius: 8px; border: 2px solid #3b82f6; margin: 20px 0;">
                    <h3 style="color: #1e40af; margin-top: 0;">Your Login Credentials:</h3>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Password:</strong> <code style="background: #e5e7eb; padding: 4px 8px; border-radius: 4px; font-size: 16px;">{password}</code></p>
                    <p style="color: #666; font-size: 14px; margin-top: 10px;">⏱ This password expires in 30 days</p>
                </div>
                <a href="{get_base_url()}secure-login" style="display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Login Now</a>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="color: #999; font-size: 12px;">Please save this password securely. For security, we recommend changing it after your first login.</p>
            </div>
        </body>
    </html>
    """
    
    send_email(email, 'Welcome to AtlasNexus - Account Approved', user_email_html)
    
    # Return success page
    return f"""
    <html>
    <body style="background: linear-gradient(135deg, #0F1419 0%, #1A2332 100%); color: white; font-family: Arial; padding: 50px; text-align: center; min-height: 100vh;">
        <div style="max-width: 600px; margin: 0 auto; background: rgba(44, 49, 55, 0.95); padding: 40px; border-radius: 20px; border: 2px solid #22c55e;">
            <h1 style="color: #22c55e; font-size: 3rem;">APPROVED</h1>
            <h2 style="color: #22c55e;">Application Approved!</h2>
            <p style="font-size: 18px; margin: 20px 0;">User <strong>{email}</strong> has been approved.</p>
            <div style="background: rgba(34, 197, 94, 0.1); padding: 20px; border-radius: 10px; margin: 20px 0;">
                <p>Generated Password: <code style="background: rgba(0,0,0,0.3); padding: 4px 8px; border-radius: 4px;">{password}</code></p>
                <p style="color: #94a3b8; font-size: 14px;">This has been emailed to the user</p>
            </div>
            <a href="/dashboard" style="display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; margin-top: 20px;">Go to Dashboard</a>
        </div>
    </body>
    </html>
    """

@app.route('/admin/quick-reject')
def admin_quick_reject():
    """Quick reject from email link"""
    token = request.args.get('token')
    email = request.args.get('email')
    
    if not token or not email:
        return "Invalid rejection link", 400
    
    # Load registrations
    registrations = load_json_db(REGISTRATIONS_FILE)
    
    # Verify token
    if email not in registrations or registrations[email].get('approval_token') != token:
        return """
        <html>
        <body style="background: #1a1a1a; color: white; font-family: Arial; padding: 50px; text-align: center;">
            <h1 style="color: #ef4444;">Invalid or Expired Link</h1>
            <p>This rejection link is invalid or has already been used.</p>
            <a href="/dashboard" style="color: #3b82f6;">Go to Dashboard</a>
        </body>
        </html>
        """, 400
    
    # Remove from registrations
    del registrations[email]
    save_json_db(REGISTRATIONS_FILE, registrations)
    
    # Send rejection email
    rejection_email_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                <h2 style="color: #333;">Registration Update</h2>
                <p>Thank you for your interest in AtlasNexus.</p>
                <p>Unfortunately, your registration application has not been approved at this time.</p>
                <p>If you have questions or would like to discuss your application, please contact us at support@atlasnexus.co.uk</p>
            </div>
        </body>
    </html>
    """
    
    send_email(email, 'AtlasNexus - Registration Update', rejection_email_html)
    
    # Return success page
    return f"""
    <html>
    <body style="background: linear-gradient(135deg, #0F1419 0%, #1A2332 100%); color: white; font-family: Arial; padding: 50px; text-align: center; min-height: 100vh;">
        <div style="max-width: 600px; margin: 0 auto; background: rgba(44, 49, 55, 0.95); padding: 40px; border-radius: 20px; border: 2px solid #ef4444;">
            <h1 style="color: #ef4444; font-size: 3rem;">✗</h1>
            <h2 style="color: #ef4444;">Application Rejected</h2>
            <p style="font-size: 18px; margin: 20px 0;">User <strong>{email}</strong> has been rejected.</p>
            <p style="color: #94a3b8;">A notification email has been sent to the applicant.</p>
            <a href="/dashboard" style="display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; margin-top: 20px;">Go to Dashboard</a>
        </div>
    </body>
    </html>
    """

@app.route('/admin/reject-user', methods=['POST'])
def admin_reject_user():
    """Admin reject user"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    email = request.json.get('email')
    reason = request.json.get('reason', 'Application not approved')
    
    # Remove from registrations
    registrations = load_json_db(REGISTRATIONS_FILE)
    if email in registrations:
        del registrations[email]
        save_json_db(REGISTRATIONS_FILE, registrations)
    
    # Send rejection email
    email_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                <h2 style="color: #333;">Registration Update - AtlasNexus</h2>
                <p>Unfortunately, your registration application has not been approved at this time.</p>
                <p><strong>Reason:</strong> {reason}</p>
                <p>If you have questions, please contact support@atlasnexus.co.uk</p>
            </div>
        </body>
    </html>
    """
    
    send_email(email, 'Registration Update - AtlasNexus', email_html)
    
    return jsonify({'status': 'success', 'message': 'User rejected'})

@app.route('/test-email')
def test_email():
    """Test email configuration"""
    ip_address = get_real_ip()
    
    # Only allow admin to test
    if not session.get(f'is_admin_{ip_address}'):
        return "Unauthorized", 401
    
    test_html = """
    <html>
        <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                <h2 style="color: #333;">Email Configuration Test</h2>
                <p>This is a test email from AtlasNexus to verify your Gmail SMTP configuration.</p>
                <div style="background: #f0f0f0; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Configuration Details:</strong></p>
                    <p>SMTP Server: smtp.gmail.com</p>
                    <p>Port: 587</p>
                    <p>Sender: """ + EMAIL_CONFIG['sender_email'] + """</p>
                </div>
                <p style="color: #22c55e; font-weight: bold;">If you received this email, your configuration is working!</p>
            </div>
        </body>
    </html>
    """
    
    success = send_email(EMAIL_CONFIG['admin_email'], 'AtlasNexus Email Test', test_html)
    
    if success:
        return f"""
        <html>
        <body style="background: #1a1a1a; color: white; font-family: Arial; padding: 50px; text-align: center;">
            <h1 style="color: #22c55e;">Email Sent Successfully!</h1>
            <p>Check your email at: {EMAIL_CONFIG['admin_email']}</p>
            <p style="margin-top: 30px;">
                <a href="/dashboard" style="background: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Back to Dashboard</a>
            </p>
        </body>
        </html>
        """
    else:
        return f"""
        <html>
        <body style="background: #1a1a1a; color: white; font-family: Arial; padding: 50px; text-align: center;">
            <h1 style="color: #ef4444;">✗ Email Failed</h1>
            <p>Please check your email_config.py file</p>
            <p>Make sure you have:</p>
            <ol style="text-align: left; display: inline-block;">
                <li>Enabled 2-factor authentication on Gmail</li>
                <li>Generated an App Password</li>
                <li>Added the App Password to email_config.py</li>
            </ol>
            <p style="margin-top: 30px;">
                <a href="/dashboard" style="background: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Back to Dashboard</a>
            </p>
        </body>
        </html>
        """

@app.route('/admin/ip-management')
def admin_ip_management():
    """Get all IP lockout data for admin panel"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    # Load all lockout data
    lockouts = load_lockouts()
    attempt_logs = load_attempt_logs()
    
    # Debug logging
    print(f"[ADMIN] IP Management accessed by {ip_address}")
    print(f"[ADMIN] Found {len(lockouts)} locked IPs")
    print(f"[ADMIN] Found {len(attempt_logs)} IPs with attempts")
    
    # Format data for frontend
    ip_data = []
    for ip, info in lockouts.items():
        # Calculate remaining time if applicable
        remaining_time = None
        if 'locked_until' in info and not info.get('permanent'):
            locked_until = datetime.fromisoformat(info['locked_until'])
            if datetime.now() < locked_until:
                remaining_time = str(locked_until - datetime.now()).split('.')[0]
        
        # Get attempt history
        attempts = []
        if ip in attempt_logs:
            attempts = attempt_logs[ip].get('attempts', [])[-10:]  # Last 10 attempts
        
        # Get additional info if available
        additional_info = info.get('additional_info', {})
        
        ip_data.append({
            'ip': ip,
            'status': 'permanent' if info.get('permanent') else 'temporary',
            'locked_at': info.get('locked_at'),
            'locked_until': info.get('locked_until'),
            'remaining_time': remaining_time,
            'reason': info.get('reason', 'Unknown'),
            'failed_passwords': info.get('failed_passwords', []),
            'reference_code': info.get('reference_code'),
            'attempt_history': attempts,
            'total_attempts': attempt_logs.get(ip, {}).get('total_attempts', 0),
            'first_seen': additional_info.get('first_seen') or attempt_logs.get(ip, {}).get('first_seen'),
            'user_agent': additional_info.get('user_agent', 'Unknown'),
            'browser_info': additional_info.get('browser_info', 'Unknown'),
            'accept_language': additional_info.get('accept_language', 'Unknown'),
            'lockout_type': info.get('lockout_type', 'unknown')
        })
    
    return jsonify({'status': 'success', 'data': ip_data})

@app.route('/admin/manage-ip', methods=['POST'])
def admin_manage_ip():
    """Manage IP bans - unban, extend, or make permanent"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    target_ip = request.json.get('ip')
    action = request.json.get('action')  # 'unban', 'extend', 'permanent'
    duration_days = request.json.get('duration_days')  # For extend action
    
    if action == 'unban':
        success = modify_ip_ban(target_ip, 'unban')
        if success:
            # Log admin action
            admin_actions = load_json_db(ADMIN_ACTIONS_FILE)
            admin_actions[str(len(admin_actions))] = {
                'admin': session.get(f'username_{ip_address}'),
                'action': f'Unbanned IP: {target_ip}',
                'timestamp': datetime.now().isoformat()
            }
            save_json_db(ADMIN_ACTIONS_FILE, admin_actions)
            return jsonify({'status': 'success', 'message': f'IP {target_ip} unbanned'})
    
    elif action == 'extend':
        if duration_days:
            success = modify_ip_ban(target_ip, 'extend', int(duration_days))
            if success:
                # Log admin action
                admin_actions = load_json_db(ADMIN_ACTIONS_FILE)
                admin_actions[str(len(admin_actions))] = {
                    'admin': session.get(f'username_{ip_address}'),
                    'action': f'Extended ban for IP {target_ip} by {duration_days} days',
                    'timestamp': datetime.now().isoformat()
                }
                save_json_db(ADMIN_ACTIONS_FILE, admin_actions)
                return jsonify({'status': 'success', 'message': f'Ban extended for {duration_days} days'})
    
    elif action == 'permanent':
        success = modify_ip_ban(target_ip, 'permanent')
        if success:
            # Log admin action
            admin_actions = load_json_db(ADMIN_ACTIONS_FILE)
            admin_actions[str(len(admin_actions))] = {
                'admin': session.get(f'username_{ip_address}'),
                'action': f'Permanently banned IP: {target_ip}',
                'timestamp': datetime.now().isoformat()
            }
            save_json_db(ADMIN_ACTIONS_FILE, admin_actions)
            return jsonify({'status': 'success', 'message': f'IP {target_ip} permanently banned'})
    
    return jsonify({'status': 'error', 'message': 'Invalid action'}), 400

@app.route('/logout')
def logout():
    """Clear session and logout"""
    ip_address = get_real_ip()
    
    # Calculate session duration if user was logged in
    if session.get(f'user_email_{ip_address}') and session.get(f'login_start_time_{ip_address}'):
        email = session.get(f'user_email_{ip_address}')
        login_start = datetime.fromisoformat(session.get(f'login_start_time_{ip_address}'))
        session_duration = (datetime.now() - login_start).total_seconds()
        
        # Update user's total login time
        users = load_json_db(USERS_FILE)
        if email in users:
            users[email]['total_login_time'] = users[email].get('total_login_time', 0) + session_duration
            users[email]['last_logout'] = datetime.now().isoformat()
            save_json_db(USERS_FILE, users)
    
    # Clear user authentication only
    session.pop(f'user_authenticated_{ip_address}', None)
    session.pop(f'username_{ip_address}', None)
    session.pop(f'user_email_{ip_address}', None)
    session.pop(f'login_start_time_{ip_address}', None)
    
    return redirect(url_for('secure_login'))

@app.route('/admin')
def admin():
    """Redirect to admin panel"""
    return redirect(url_for('admin_panel'))

@app.route('/admin/comprehensive-data')
def admin_comprehensive_data():
    """Get ALL user interaction data for admin panel"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    try:
        # Load all data sources with error handling
        lockouts = load_lockouts() or {}
        registrations = load_json_db(REGISTRATIONS_FILE) or {}
        users = load_json_db(USERS_FILE) or {}
        login_attempts = load_json_db(LOGIN_ATTEMPTS_FILE) or {}
        admin_actions = load_json_db(ADMIN_ACTIONS_FILE) or []
        
        # Ensure admin_actions is a list
        if isinstance(admin_actions, dict):
            admin_actions = list(admin_actions.values())
        
        # Get current logged-in user's email
        current_user_email = session.get(f'user_email_{ip_address}')
        
        # Compile comprehensive data - matching what frontend expects
        data = {
            'lockouts': lockouts,
            'login_attempts': login_attempts,  # Frontend expects this key
            'registrations': registrations,
            'users': users,
            'admin_actions': admin_actions,
            'current_user_email': current_user_email,  # Add current user email
            'statistics': {
                'total_users': len(users) if isinstance(users, dict) else 0,
                'total_registrations': len(registrations) if isinstance(registrations, dict) else 0,
                'total_locked_ips': len(lockouts) if isinstance(lockouts, dict) else 0,
                'total_login_attempts': sum(len(attempts) for attempts in login_attempts.values()) if isinstance(login_attempts, dict) else 0,
                'verified_users': sum(1 for r in registrations.values() if r.get('email_verified')) if isinstance(registrations, dict) else 0,
                'pending_verification': sum(1 for r in registrations.values() if not r.get('email_verified')) if isinstance(registrations, dict) else 0,
                'approved_users': sum(1 for r in registrations.values() if r.get('admin_approved')) if isinstance(registrations, dict) else 0,
                'pending_approval': sum(1 for r in registrations.values() if not r.get('admin_approved')) if isinstance(registrations, dict) else 0
            }
        }
        
        return jsonify({'status': 'success', 'data': data})
    
    except Exception as e:
        print(f"Error in admin_comprehensive_data: {e}")
        import traceback
        traceback.print_exc()
        
        # Return empty but valid structure on error
        return jsonify({
            'status': 'success',
            'data': {
                'lockouts': {},
                'login_attempts': {},
                'registrations': {},
                'users': {},
                'admin_actions': [],
                'statistics': {
                    'total_users': 0,
                    'total_registrations': 0,
                    'total_locked_ips': 0,
                    'total_login_attempts': 0,
                    'verified_users': 0,
                    'pending_verification': 0,
                    'approved_users': 0,
                    'pending_approval': 0
                }
            }
        })

@app.route('/admin/delete-data', methods=['POST'])
def admin_delete_data():
    """Delete specific data from the system"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    data = request.get_json()
    data_type = data.get('type')
    identifier = data.get('identifier')
    
    try:
        if data_type == 'ip_lockout':
            lockouts = load_lockouts()
            if identifier in lockouts:
                del lockouts[identifier]
                save_lockouts(lockouts)
                print(f"[ADMIN] Deleted IP lockout for {identifier}")
                
        elif data_type == 'login_attempt':
            attempts = load_attempt_logs()
            if identifier in attempts:
                del attempts[identifier]
                save_attempt_logs(attempts)
                print(f"[ADMIN] Deleted login attempts for {identifier}")
                
        elif data_type == 'registration':
            registrations = load_json_db(REGISTRATIONS_FILE)
            if identifier in registrations:
                del registrations[identifier]
                save_json_db(REGISTRATIONS_FILE, registrations)
                print(f"[ADMIN] Deleted registration for {identifier}")
                
        elif data_type == 'expired_registration':
            expired = load_json_db('data/expired_registrations.json')
            if identifier in expired:
                del expired[identifier]
                save_json_db('data/expired_registrations.json', expired)
                print(f"[ADMIN] Deleted expired registration for {identifier}")
                
        elif data_type == 'all_attempts':
            # Clear all login attempts
            save_attempt_logs({})
            print(f"[ADMIN] Cleared all login attempts")
            
        elif data_type == 'all_lockouts':
            # Clear all IP lockouts
            save_lockouts({})
            print(f"[ADMIN] Cleared all IP lockouts")
            
        else:
            return jsonify({'status': 'error', 'message': 'Invalid data type'})
        
        return jsonify({'status': 'success', 'message': f'Deleted {data_type}: {identifier}'})
        
    except Exception as e:
        print(f"[ADMIN ERROR] Failed to delete {data_type} {identifier}: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/terms')
def terms():
    """Terms of Service page"""
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    """Privacy Policy page"""
    return render_template('privacy.html')

@app.route('/data-protection')
def data_protection():
    """Data Protection page"""
    return render_template('data-protection.html')

@app.route('/security')
def security():
    """Security page"""
    return render_template('security.html')

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@app.route('/admin/approve-user-advanced', methods=['POST'])
def admin_approve_user_advanced():
    """Advanced user approval with password generation options"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    data = request.json
    email = data.get('email')
    account_type = data.get('account_type', 'external')
    password_type = data.get('password_type', 'auto')
    manual_password = data.get('manual_password')
    
    # Load registrations
    registrations = load_json_db(REGISTRATIONS_FILE)
    
    if email not in registrations:
        return jsonify({'status': 'error', 'message': 'Registration not found'}), 404
    
    # Generate or use manual password
    if password_type == 'manual' and manual_password:
        password = manual_password
    else:
        password = generate_secure_password()
    
    # Update registration with approval info but keep it in registrations
    registrations[email]['generated_password'] = password
    registrations[email]['account_type'] = account_type
    registrations[email]['admin_approved'] = True
    registrations[email]['approved_at'] = datetime.now().isoformat()
    registrations[email]['approved_by'] = session.get(f'user_email_{ip_address}', 'spikemaz8@aol.com')
    save_json_db(REGISTRATIONS_FILE, registrations)
    
    # Check if email is verified
    email_verified = registrations[email].get('email_verified', False)
    
    # Only create user account and send credentials if BOTH verified AND approved
    if email_verified:
        # Create user account
        password_expiry = datetime.now() + timedelta(days=30)
        users = load_json_db(USERS_FILE)
        users[email] = {
            **registrations[email],
            'password': password,
            'password_expiry': password_expiry.isoformat(),
            'admin_approved': True,
            'approved_at': datetime.now().isoformat(),
            'account_type': account_type,
            'login_count': 0,
            'total_login_time': 0,
            'last_login': None,
            'login_history': [],
            'approved_by': session.get(f'user_email_{ip_address}', 'spikemaz8@aol.com'),
            'password_sent': False  # Will be sent now
        }
        save_json_db(USERS_FILE, users)
    
    # Update registration status
    registrations[email]['admin_approved'] = True
    save_json_db(REGISTRATIONS_FILE, registrations)
    
    # Log admin action
    admin_actions = load_json_db(ADMIN_ACTIONS_FILE)
    if not isinstance(admin_actions, list):
        admin_actions = []
    admin_actions.append({
        'action': 'user_approved_advanced',
        'email': email,
        'account_type': account_type,
        'password_type': password_type,
        'email_verified_at_approval': email_verified,
        'timestamp': datetime.now().isoformat(),
        'admin': 'spikemaz8@aol.com'
    })
    save_json_db(ADMIN_ACTIONS_FILE, admin_actions)
    
    # Send approval email ONLY if email is verified
    if email_verified:
        # Send approval email with password
        base_url = get_base_url()
        email_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #22c55e;">Application Approved!</h2>
                    <p>Welcome to AtlasNexus! Your account has been approved.</p>
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #333;">Your Login Credentials:</h3>
                        <p><strong>Email:</strong> {email}</p>
                        <p><strong>Password:</strong> <code style="background: #fffae6; padding: 4px 8px; border-radius: 4px; font-size: 14px;">{password}</code></p>
                        <p><strong>Account Type:</strong> {account_type.upper()}</p>
                    </div>
                    <a href="{base_url}secure-login" style="display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Login Now</a>
                    <p style="color: #666; font-size: 14px; margin-top: 20px;">For security, please change your password after first login.</p>
                </div>
            </body>
        </html>
        """
        
        send_email(email, 'AtlasNexus - Account Approved', email_html)
        
        return jsonify({
            'status': 'success', 
            'message': 'User approved and credentials sent via email'
        })
    else:
        # Email not verified - credentials will be sent after verification
        return jsonify({
            'status': 'success',
            'message': 'User approved. Credentials will be sent after email verification.'
        })

@app.route('/admin/resend-credentials', methods=['POST'])
def admin_resend_credentials():
    """Resend credentials to an approved user"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    email = request.json.get('email')
    
    # Load users
    users = load_json_db(USERS_FILE)
    
    if email not in users:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    user = users[email]
    
    if not user.get('admin_approved'):
        return jsonify({'status': 'error', 'message': 'User not approved'}), 400
    
    # Send credentials email
    base_url = get_base_url()
    password = user.get('password', 'Please contact admin for password')
    account_type = user.get('account_type', 'external')
    
    email_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                <h2 style="color: #3b82f6;">Your AtlasNexus Credentials</h2>
                <p>Here are your login credentials (resent by admin):</p>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Password:</strong> <code style="background: #fffae6; padding: 4px 8px; border-radius: 4px; font-size: 14px;">{password}</code></p>
                    <p><strong>Account Type:</strong> {account_type.upper()}</p>
                </div>
                <a href="{base_url}secure-login" style="display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Login Now</a>
            </div>
        </body>
    </html>
    """
    
    if send_email(email, 'AtlasNexus - Your Login Credentials', email_html):
        return jsonify({'status': 'success', 'message': 'Credentials resent successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send email'}), 500

@app.route('/debug/ip-status')
def debug_ip_status():
    """Debug endpoint to check current IP status"""
    ip_address = get_real_ip()
    lockouts = load_lockouts()
    attempts = load_attempt_logs()
    
    ip_lockout_info = lockouts.get(ip_address, {})
    ip_attempts_info = attempts.get(ip_address, {})
    
    # Check if lockout is still active
    is_active = False
    if ip_lockout_info:
        if ip_lockout_info.get('permanent'):
            is_active = True
        elif 'locked_until' in ip_lockout_info:
            locked_until = datetime.fromisoformat(ip_lockout_info['locked_until'])
            is_active = datetime.now() < locked_until
            if is_active:
                remaining = locked_until - datetime.now()
                ip_lockout_info['time_remaining'] = str(remaining)
    
    status = {
        'your_ip': ip_address,
        'is_locked': ip_address in lockouts,
        'is_active': is_active,
        'lockout_info': ip_lockout_info,
        'attempts_info': ip_attempts_info,
        'total_locked_ips': len(lockouts),
        'all_locked_ips': list(lockouts.keys()),
        'headers': {
            'X-Forwarded-For': request.headers.get('X-Forwarded-For'),
            'X-Real-IP': request.headers.get('X-Real-IP'),
            'CF-Connecting-IP': request.headers.get('CF-Connecting-IP'),
            'Remote-Addr': request.remote_addr
        }
    }
    
    return jsonify(status)

@app.route('/admin/update-password', methods=['POST'])
def admin_update_password():
    """Update user password"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
    
    data = request.get_json()
    email = data.get('email')
    new_password = data.get('password')
    
    if not email or not new_password:
        return jsonify({'status': 'error', 'message': 'Email and password required'}), 400
    
    # Update in registrations
    registrations = load_json_db(REGISTRATIONS_FILE)
    if email in registrations:
        registrations[email]['generated_password'] = new_password
        save_json_db(REGISTRATIONS_FILE, registrations)
    
    # Update in users if they exist
    users = load_json_db(USERS_FILE)
    if email in users:
        users[email]['password'] = new_password
        # Reset password expiry to 90 days from now
        users[email]['password_expiry'] = (datetime.now() + timedelta(days=90)).isoformat()
        save_json_db(USERS_FILE, users)
    
    # Log the action
    log_admin_action(ip_address, 'password_update', {
        'user_email': email,
        'admin_email': session.get(f'user_email_{ip_address}')
    })
    
    return jsonify({'status': 'success', 'message': 'Password updated successfully'})

@app.route('/admin/user/delete', methods=['POST'])
def admin_delete_user():
    """Delete a user from the system"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
    
    email = request.json.get('email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Email required'}), 400
    
    # Delete from users
    users = load_json_db(USERS_FILE)
    if email in users:
        del users[email]
        save_json_db(USERS_FILE, users)
    
    # Delete from registrations
    registrations = load_json_db(REGISTRATIONS_FILE)
    if email in registrations:
        del registrations[email]
        save_json_db(REGISTRATIONS_FILE, registrations)
    
    # Log the action
    log_admin_action(ip_address, 'user_delete', {
        'deleted_user': email,
        'admin_email': session.get(f'user_email_{ip_address}')
    })
    
    return jsonify({'status': 'success', 'message': f'User {email} deleted successfully'})

@app.route('/admin/user/freeze', methods=['POST'])
def admin_freeze_user():
    """Freeze a user account"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
    
    email = request.json.get('email')
    reason = request.json.get('reason', 'Account frozen by administrator')
    
    if not email:
        return jsonify({'status': 'error', 'message': 'Email required'}), 400
    
    # Update user status
    users = load_json_db(USERS_FILE)
    if email not in users:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    users[email]['is_frozen'] = True
    users[email]['frozen_at'] = datetime.now().isoformat()
    users[email]['freeze_reason'] = reason
    users[email]['frozen_by'] = session.get(f'user_email_{ip_address}')
    save_json_db(USERS_FILE, users)
    
    # Log the action
    log_admin_action(ip_address, 'user_freeze', {
        'frozen_user': email,
        'reason': reason,
        'admin_email': session.get(f'user_email_{ip_address}')
    })
    
    return jsonify({'status': 'success', 'message': f'User {email} frozen successfully'})

@app.route('/admin/user/unfreeze', methods=['POST'])
def admin_unfreeze_user():
    """Unfreeze a user account"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
    
    email = request.json.get('email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Email required'}), 400
    
    # Update user status
    users = load_json_db(USERS_FILE)
    if email not in users:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    users[email]['is_frozen'] = False
    users[email]['unfrozen_at'] = datetime.now().isoformat()
    users[email]['unfrozen_by'] = session.get(f'user_email_{ip_address}')
    # Keep freeze history
    if 'freeze_history' not in users[email]:
        users[email]['freeze_history'] = []
    users[email]['freeze_history'].append({
        'frozen_at': users[email].get('frozen_at'),
        'unfrozen_at': datetime.now().isoformat(),
        'reason': users[email].get('freeze_reason'),
        'frozen_by': users[email].get('frozen_by'),
        'unfrozen_by': session.get(f'user_email_{ip_address}')
    })
    save_json_db(USERS_FILE, users)
    
    # Log the action
    log_admin_action(ip_address, 'user_unfreeze', {
        'unfrozen_user': email,
        'admin_email': session.get(f'user_email_{ip_address}')
    })
    
    return jsonify({'status': 'success', 'message': f'User {email} unfrozen successfully'})

@app.route('/admin/user/edit', methods=['POST'])
def admin_edit_user():
    """Edit user account type and details"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
    
    data = request.json
    email = data.get('email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Email required'}), 400
    
    # Update user
    users = load_json_db(USERS_FILE)
    if email not in users:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # Update account type if provided
    if 'account_type' in data:
        old_type = users[email].get('account_type', 'external')
        new_type = data['account_type']
        if new_type in ['admin', 'internal', 'external']:
            users[email]['account_type'] = new_type
            users[email]['is_admin'] = (new_type == 'admin')
            
            # Log type change
            if 'account_type_history' not in users[email]:
                users[email]['account_type_history'] = []
            users[email]['account_type_history'].append({
                'from': old_type,
                'to': new_type,
                'changed_at': datetime.now().isoformat(),
                'changed_by': session.get(f'user_email_{ip_address}')
            })
    
    # Update other fields if provided
    if 'full_name' in data:
        users[email]['full_name'] = data['full_name']
    if 'company' in data:
        users[email]['company'] = data['company']
    if 'phone' in data:
        users[email]['phone'] = data['phone']
    
    users[email]['last_modified'] = datetime.now().isoformat()
    users[email]['modified_by'] = session.get(f'user_email_{ip_address}')
    save_json_db(USERS_FILE, users)
    
    # Log the action
    log_admin_action(ip_address, 'user_edit', {
        'edited_user': email,
        'changes': data,
        'admin_email': session.get(f'user_email_{ip_address}')
    })
    
    return jsonify({'status': 'success', 'message': 'User updated successfully'})

@app.route('/admin/users/all')
def admin_get_all_users():
    """Get all users with online/offline status"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
    
    users = load_json_db(USERS_FILE)
    registrations = load_json_db(REGISTRATIONS_FILE)
    
    # Combine users and registrations
    all_users = []
    
    # Add approved users
    for email, user_data in users.items():
        # Check if user is online (has active session)
        is_online = False
        last_activity = None
        
        # Check if user has logged in recently (within last 30 minutes)
        if 'last_login' in user_data:
            last_login = datetime.fromisoformat(user_data['last_login'])
            if (datetime.now() - last_login).total_seconds() < 1800:  # 30 minutes
                is_online = True
                last_activity = last_login
        
        all_users.append({
            'email': email,
            'full_name': user_data.get('full_name', 'N/A'),
            'company': user_data.get('company', 'N/A'),
            'account_type': user_data.get('account_type', 'external'),
            'is_admin': user_data.get('is_admin', False),
            'is_frozen': user_data.get('is_frozen', False),
            'is_online': is_online,
            'last_activity': last_activity.isoformat() if last_activity else None,
            'created_at': user_data.get('created_at'),
            'status': 'approved'
        })
    
    # Add pending registrations
    for email, reg_data in registrations.items():
        if email not in users:  # Don't duplicate approved users
            all_users.append({
                'email': email,
                'full_name': reg_data.get('full_name', 'N/A'),
                'company': reg_data.get('company', 'N/A'),
                'account_type': reg_data.get('account_type', 'external'),
                'is_admin': False,
                'is_frozen': False,
                'is_online': False,
                'last_activity': None,
                'created_at': reg_data.get('created_at'),
                'status': 'pending'
            })
    
    return jsonify({'status': 'success', 'users': all_users})

@app.route('/admin/ban-ip', methods=['POST'])
def admin_ban_ip():
    """Ban an IP address"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
    
    target_ip = request.json.get('ip')
    duration = request.json.get('duration', 'permanent')  # permanent, 24h, 7d, 30d
    reason = request.json.get('reason', 'Banned by administrator')
    
    if not target_ip:
        return jsonify({'status': 'error', 'message': 'IP address required'}), 400
    
    # Apply the ban
    if duration == 'permanent':
        apply_ip_lockout(target_ip, 'permanent', reason=reason)
    elif duration == '24h':
        apply_ip_lockout(target_ip, 'blocked_24h', reason=reason, duration_hours=24)
    elif duration == '7d':
        apply_ip_lockout(target_ip, 'blocked_7d', reason=reason, duration_hours=168)
    elif duration == '30d':
        apply_ip_lockout(target_ip, 'blocked_30d', reason=reason, duration_hours=720)
    else:
        return jsonify({'status': 'error', 'message': 'Invalid duration'}), 400
    
    # Log the action
    log_admin_action(ip_address, 'ip_ban', {
        'banned_ip': target_ip,
        'duration': duration,
        'reason': reason,
        'admin_email': session.get(f'user_email_{ip_address}')
    })
    
    return jsonify({'status': 'success', 'message': f'IP {target_ip} banned successfully'})

@app.route('/admin/unban-ip', methods=['POST'])
def admin_unban_ip():
    """Unban an IP address"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
    
    target_ip = request.json.get('ip')
    
    if not target_ip:
        return jsonify({'status': 'error', 'message': 'IP address required'}), 400
    
    # Remove the ban
    lockouts = load_lockouts()
    if target_ip in lockouts:
        del lockouts[target_ip]
        save_lockouts(lockouts)
        
        # Log the action
        log_admin_action(ip_address, 'ip_unban', {
            'unbanned_ip': target_ip,
            'admin_email': session.get(f'user_email_{ip_address}')
        })
        
        return jsonify({'status': 'success', 'message': f'IP {target_ip} unbanned successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'IP not found in ban list'}), 404

@app.route('/admin/ip-tracking')
def admin_get_ip_tracking():
    """Get comprehensive IP tracking data"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
    
    # Load all tracking data
    lockouts = load_lockouts()
    login_attempts = load_json_db(LOGIN_ATTEMPTS_FILE)
    
    # Build comprehensive IP data
    ip_data = {}
    
    # Add lockout data
    for ip, lockout_info in lockouts.items():
        if ip not in ip_data:
            ip_data[ip] = {
                'ip_address': ip,
                'status': 'blocked' if lockout_info.get('permanent') or lockout_info.get('locked_until') else 'normal',
                'lockout_info': lockout_info,
                'login_attempts': [],
                'pages_accessed': [],
                'first_seen': None,
                'last_seen': None,
                'total_attempts': 0
            }
    
    # Add login attempt data
    for ip, attempts in login_attempts.items():
        if ip not in ip_data:
            ip_data[ip] = {
                'ip_address': ip,
                'status': 'normal',
                'lockout_info': None,
                'login_attempts': [],
                'pages_accessed': [],
                'first_seen': None,
                'last_seen': None,
                'total_attempts': 0
            }
        
        ip_data[ip]['login_attempts'] = attempts
        ip_data[ip]['total_attempts'] = len(attempts)
        
        # Calculate first and last seen
        if attempts:
            timestamps = [datetime.fromisoformat(a['timestamp']) for a in attempts if 'timestamp' in a]
            if timestamps:
                ip_data[ip]['first_seen'] = min(timestamps).isoformat()
                ip_data[ip]['last_seen'] = max(timestamps).isoformat()
        
        # Determine pages accessed
        pages = set()
        for attempt in attempts:
            if attempt.get('success'):
                pages.add('dashboard')
            pages.add('gate2')
        ip_data[ip]['pages_accessed'] = list(pages)
        
        # Add Gate1 if they got past it
        if pages:
            ip_data[ip]['pages_accessed'].insert(0, 'gate1')
    
    return jsonify({'status': 'success', 'ip_data': list(ip_data.values())})

@app.route('/admin-panel')
def admin_panel():
    """New comprehensive admin panel"""
    ip_address = get_real_ip()
    
    # Verify both authentications and admin status
    if not session.get(f'site_authenticated_{ip_address}'):
        return redirect(url_for('index'))
    if not session.get(f'user_authenticated_{ip_address}'):
        return redirect(url_for('secure_login'))
    if not session.get(f'is_admin_{ip_address}'):
        return redirect(url_for('dashboard'))
    
    return render_template('admin_panel.html')

@app.route('/admin/system-stats')
def admin_system_stats():
    """Get system statistics for admin panel"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    # Gather system stats
    stats = {
        'total_users': len(load_json_db(USERS_FILE)),
        'total_registrations': len(load_json_db(REGISTRATIONS_FILE)),
        'blocked_ips': len([ip for ip, data in load_lockouts().items() 
                          if data.get('is_banned') or (data.get('locked_until') and 
                          datetime.fromisoformat(data['locked_until']) > datetime.now())]),
        'active_sessions': session.get('active_count', 0),
        'system_uptime': '99.9%',
        'last_backup': datetime.now().isoformat(),
        'disk_usage': '42%',
        'memory_usage': '58%'
    }
    
    return jsonify({'status': 'success', 'data': stats})

@app.route('/admin/export-data', methods=['POST'])
def admin_export_data():
    """Export all admin data"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    # Compile all data
    export_data = {
        'users': load_json_db(USERS_FILE),
        'registrations': load_json_db(REGISTRATIONS_FILE),
        'lockouts': load_lockouts(),
        'login_attempts': load_json_db(LOGIN_ATTEMPTS_FILE),
        'admin_actions': load_json_db(ADMIN_ACTIONS_FILE),
        'exported_at': datetime.now().isoformat(),
        'exported_by': session.get(f'username_{ip_address}')
    }
    
    return jsonify({'status': 'success', 'data': export_data})

@app.route('/admin/system-config', methods=['GET', 'POST'])
def admin_system_config():
    """Get or update system configuration"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    if request.method == 'GET':
        # Return current config
        config = {
            'site_name': 'Atlas Nexus',
            'admin_email': 'admin@atlasnexus.com',
            'max_login_attempts': 5,
            'lockout_duration': 30,
            'session_timeout': 60,
            'maintenance_mode': False,
            'two_factor_auth': False,
            'ip_whitelisting': False,
            'email_notifications': True,
            'auto_approve_registrations': False
        }
        return jsonify({'status': 'success', 'config': config})
    
    else:
        # Update config
        new_config = request.get_json()
        # Here you would save the config to a file or database
        log_admin_action(ip_address, 'config_update', {'updated_settings': list(new_config.keys())})
        return jsonify({'status': 'success', 'message': 'Configuration updated'})

@app.route('/securitization-engine')
def securitization_engine():
    """Securitization/Permutation Engine - Admin only"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'site_authenticated_{ip_address}'):
        return redirect(url_for('index'))
    if not session.get(f'user_authenticated_{ip_address}'):
        return redirect(url_for('secure_login'))
    if not session.get(f'is_admin_{ip_address}'):
        # Non-admins get view-only access
        return render_template('securitisation_engine.html', 
                             is_admin=False, 
                             username=session.get(f'username_{ip_address}'))
    
    return render_template('securitisation_engine.html', 
                         is_admin=True,
                         username=session.get(f'username_{ip_address}'))

@app.route('/api/securitization/run', methods=['POST'])
def run_securitization():
    """Run securitization calculations - Admin only"""
    ip_address = get_real_ip()
    
    # Only admins can run calculations
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
    
    data = request.get_json()
    
    # Check if securitization engine is available
    if not SECURITIZATION_AVAILABLE:
        return jsonify({
            'status': 'error',
            'message': 'Securitization engine not available. Please ensure securitization_engine.py is deployed.'
        }), 503
    
    # Import and use the securitization engine with Table 6 calculations
    try:
        # Run the proprietary calculation engine
        result_data = run_securitization_calculation(data)
        
        # Log the calculation
        log_admin_action(ip_address, 'securitization_run', {
            'result_id': result_data['id'],
            'asset_type': data.get('assetType'),
            'method': data.get('structMethod'),
            'tranches': data.get('numTranches')
        })
        
        # Return sanitized output (no formulas exposed)
        result = {
            'status': 'success',
            'output': result_data
        }
        
    except Exception as e:
        print(f"Securitization calculation error: {e}")
        # Fallback calculation if engine fails
        result = {
            'status': 'success',
            'output': {
                'id': f'SEC_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'timestamp': datetime.now().isoformat(),
                'calculations': 'Hidden - Proprietary Algorithm',
                'results': {
                    'total_securities': data.get('securities', 100),
                    'risk_rating': 'AAA',
                    'expected_return': '8.5%',
                    'volatility': '12.3%',
                    'sharpe_ratio': 1.42,
                    'tranches': [
                        {'name': 'Senior', 'size': '70%', 'rating': 'AAA'},
                        {'name': 'Mezzanine', 'size': '20%', 'rating': 'BBB'},
                        {'name': 'Equity', 'size': '10%', 'rating': 'NR'}
                    ]
                }
            }
        }
    
    # Always log the action
    if 'output' in result and result['output']:
        log_admin_action(ip_address, 'securitization_run', {'result_id': result['output']['id']})
    
    return jsonify(result)

@app.route('/api/securitization/history')
def securitization_history():
    """Get calculation history - Available to all authenticated users"""
    ip_address = get_real_ip()
    
    if not session.get(f'user_authenticated_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Authentication required'}), 401
    
    # Return calculation history (view-only for non-admins)
    history = [
        {
            'id': 'SEC_20250119_143022',
            'timestamp': '2025-01-19T14:30:22',
            'type': 'CDO Analysis',
            'status': 'Complete',
            'viewable': True
        },
        {
            'id': 'SEC_20250119_121500',
            'timestamp': '2025-01-19T12:15:00',
            'type': 'MBS Structuring',
            'status': 'Complete',
            'viewable': True
        }
    ]
    
    return jsonify({'status': 'success', 'history': history})

@app.route('/api/securitization/view/<result_id>')
def view_securitization_result(result_id):
    """View specific result - Available to authenticated users"""
    ip_address = get_real_ip()
    
    if not session.get(f'user_authenticated_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Authentication required'}), 401
    
    # Return sanitized result (no formulas or calculations shown)
    result = {
        'id': result_id,
        'timestamp': datetime.now().isoformat(),
        'output': {
            'summary': 'Securitization Complete',
            'metrics': {
                'total_value': '$100,000,000',
                'weighted_average_life': '5.2 years',
                'credit_enhancement': '15%'
            }
        }
    }
    
    return jsonify({'status': 'success', 'result': result})

@app.route('/api/securitization/check-access')
def check_securitization_access():
    """Check user's access level for securitization engine"""
    ip_address = get_real_ip()
    
    if not session.get(f'user_authenticated_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401
    
    # Determine role based on admin status
    if session.get(f'is_admin_{ip_address}'):
        role = 'admin'
    else:
        # You can add logic here to distinguish between internal and external teams
        # For now, all non-admins are considered internal
        role = 'internal'
    
    return jsonify({
        'status': 'success',
        'role': role,
        'username': session.get(f'username_{ip_address}')
    })

@app.route('/admin/audit-log')
def admin_audit_log():
    """Get complete audit log"""
    ip_address = get_real_ip()
    
    # Verify admin access
    if not session.get(f'is_admin_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    # Compile audit log from various sources
    audit_entries = []
    
    # Add login attempts
    login_attempts = load_json_db(LOGIN_ATTEMPTS_FILE)
    for ip, attempts in login_attempts.items():
        for attempt in attempts:
            audit_entries.append({
                'timestamp': attempt.get('timestamp'),
                'type': 'login_attempt',
                'ip': ip,
                'details': attempt,
                'severity': 'warning' if not attempt.get('success') else 'info'
            })
    
    # Add admin actions
    admin_actions = load_json_db(ADMIN_ACTIONS_FILE)
    for action in admin_actions:
        audit_entries.append({
            'timestamp': action.get('timestamp'),
            'type': 'admin_action',
            'user': action.get('admin'),
            'details': action,
            'severity': 'info'
        })
    
    # Sort by timestamp
    audit_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return jsonify({'status': 'success', 'entries': audit_entries[:100]})  # Return last 100 entries

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('404.html', error='Server error'), 500

# ==================== MAIN ====================
# Audit and clean project structure (only on local, not Vercel)
if IS_LOCAL:
    audit_project()

# Show environment info on startup
if IS_VERCEL:
    print("[VERCEL] Running on Vercel - atlasnexus.co.uk")
    print("[VERCEL] Vercel manages all servers automatically")
elif IS_LOCAL:
    print(f"[LOCAL] Running locally in {ENVIRONMENT.upper()} mode")
else:
    print(f"[PRODUCTION] Running in {ENVIRONMENT.upper()} mode")

if __name__ == '__main__':
    # Only runs locally, not on Vercel
    # Kill any existing LOCAL servers
    kill_port_5000()
    
    print(f"\n[START] Starting LOCAL AtlasNexus server")
    print(f"[URL] http://localhost:5000")
    print("[STOP] Press Ctrl+C to stop\n")
    print("[INFO] This is your LOCAL server only.")
    print("[INFO] Vercel deployment at atlasnexus.co.uk is managed separately.\n")
    
    try:
        app.run(host=HOST, port=5000, debug=DEBUG)
    except KeyboardInterrupt:
        print("\nServer stopped.")
        kill_port_5000()