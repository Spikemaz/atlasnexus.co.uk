"""
IP Management Module
====================
Centralized IP lockout, ban, and tracking functionality
"""

import os
import json
import secrets
from datetime import datetime, timedelta
from utils import load_json_db, save_json_db, send_email, log_event

# Configuration
DATA_DIR = 'data'
LOCKOUTS_FILE = os.path.join(DATA_DIR, 'ip_lockouts.json')
ATTEMPTS_FILE = os.path.join(DATA_DIR, 'ip_attempts_log.json')

class IPManager:
    """Manage IP addresses, lockouts, and bans"""
    
    def __init__(self):
        self.lockouts_file = LOCKOUTS_FILE
        self.attempts_file = ATTEMPTS_FILE
    
    def load_lockouts(self):
        """Load lockout data"""
        return load_json_db(self.lockouts_file)
    
    def save_lockouts(self, lockouts):
        """Save lockout data"""
        return save_json_db(self.lockouts_file, lockouts)
    
    def load_attempts(self):
        """Load attempt logs"""
        return load_json_db(self.attempts_file)
    
    def save_attempts(self, attempts):
        """Save attempt logs"""
        return save_json_db(self.attempts_file, attempts)
    
    def check_lockout(self, ip_address):
        """Check if an IP is locked out"""
        lockouts = self.load_lockouts()
        
        if ip_address not in lockouts:
            return None
        
        lockout_data = lockouts[ip_address]
        
        # Check permanent ban
        if lockout_data.get('is_banned'):
            return {
                'type': 'permanent',
                'reason': lockout_data.get('ban_reason', 'Banned'),
                'reference_code': lockout_data.get('reference_code')
            }
        
        # Check temporary lockout
        if lockout_data.get('locked_until'):
            locked_until = datetime.fromisoformat(lockout_data['locked_until'])
            if datetime.now() < locked_until:
                remaining = int((locked_until - datetime.now()).total_seconds())
                return {
                    'type': lockout_data.get('lockout_type', 'temporary'),
                    'remaining_seconds': remaining,
                    'remaining_minutes': remaining // 60,
                    'unlock_time': locked_until.isoformat(),
                    'reason': lockout_data.get('reason', 'Security lockout'),
                    'reference_code': lockout_data.get('reference_code')
                }
            else:
                # Lockout expired, clean it up
                del lockouts[ip_address]
                self.save_lockouts(lockouts)
        
        return None
    
    def apply_lockout(self, ip_address, duration_hours=24, reason='', lockout_type='temporary'):
        """Apply a lockout to an IP address"""
        lockouts = self.load_lockouts()
        
        # Generate reference code
        reference_code = f"REF-{secrets.token_hex(4).upper()}"
        
        # Calculate unlock time
        if duration_hours == 0:  # Permanent
            lockout_data = {
                'is_banned': True,
                'ban_reason': reason or 'Permanent ban',
                'banned_at': datetime.now().isoformat(),
                'reference_code': reference_code,
                'lockout_type': 'permanent'
            }
        else:
            unlock_time = datetime.now() + timedelta(hours=duration_hours)
            lockout_data = {
                'locked_until': unlock_time.isoformat(),
                'locked_at': datetime.now().isoformat(),
                'reason': reason or f'Locked for {duration_hours} hours',
                'lockout_type': lockout_type,
                'duration_hours': duration_hours,
                'reference_code': reference_code,
                'unlock_token': secrets.token_urlsafe(32)
            }
        
        lockouts[ip_address] = lockout_data
        self.save_lockouts(lockouts)
        
        # Log the event
        log_event('ip_lockout', {
            'ip_address': ip_address,
            'duration_hours': duration_hours,
            'reason': reason,
            'reference_code': reference_code
        })
        
        return lockout_data
    
    def unlock_ip(self, ip_address):
        """Remove lockout for an IP"""
        lockouts = self.load_lockouts()
        
        if ip_address in lockouts:
            lockout_data = lockouts[ip_address]
            del lockouts[ip_address]
            self.save_lockouts(lockouts)
            
            # Log the event
            log_event('ip_unlocked', {
                'ip_address': ip_address,
                'was_banned': lockout_data.get('is_banned', False)
            })
            
            return True
        
        return False
    
    def ban_ip(self, ip_address, reason='Manual ban', banned_by='admin'):
        """Permanently ban an IP"""
        return self.apply_lockout(ip_address, duration_hours=0, reason=reason, lockout_type='permanent')
    
    def unban_ip(self, ip_address):
        """Remove permanent ban from an IP"""
        return self.unlock_ip(ip_address)
    
    def log_attempt(self, ip_address, attempt_type='login', success=False, details=None):
        """Log an attempt from an IP"""
        attempts = self.load_attempts()
        
        if ip_address not in attempts:
            attempts[ip_address] = []
        
        attempt_data = {
            'timestamp': datetime.now().isoformat(),
            'type': attempt_type,
            'success': success,
            'details': details or {}
        }
        
        attempts[ip_address].append(attempt_data)
        
        # Keep only last 100 attempts per IP
        attempts[ip_address] = attempts[ip_address][-100:]
        
        self.save_attempts(attempts)
        return attempt_data
    
    def get_attempt_count(self, ip_address, window_minutes=60, attempt_type=None):
        """Get number of attempts from an IP in a time window"""
        attempts = self.load_attempts()
        
        if ip_address not in attempts:
            return 0
        
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        count = 0
        
        for attempt in attempts[ip_address]:
            try:
                attempt_time = datetime.fromisoformat(attempt['timestamp'])
                if attempt_time > cutoff_time:
                    if not attempt_type or attempt.get('type') == attempt_type:
                        if not attempt.get('success', False):
                            count += 1
            except:
                continue
        
        return count
    
    def clear_attempts(self, ip_address):
        """Clear all attempts for an IP"""
        attempts = self.load_attempts()
        
        if ip_address in attempts:
            del attempts[ip_address]
            self.save_attempts(attempts)
            return True
        
        return False
    
    def get_all_lockouts(self):
        """Get all current lockouts"""
        lockouts = self.load_lockouts()
        result = {
            'permanent_bans': [],
            'temporary_lockouts': [],
            'expired': []
        }
        
        now = datetime.now()
        
        for ip, data in lockouts.items():
            if data.get('is_banned'):
                result['permanent_bans'].append({
                    'ip': ip,
                    'reason': data.get('ban_reason'),
                    'banned_at': data.get('banned_at'),
                    'reference_code': data.get('reference_code')
                })
            elif data.get('locked_until'):
                locked_until = datetime.fromisoformat(data['locked_until'])
                if locked_until > now:
                    result['temporary_lockouts'].append({
                        'ip': ip,
                        'unlock_time': data['locked_until'],
                        'reason': data.get('reason'),
                        'reference_code': data.get('reference_code')
                    })
                else:
                    result['expired'].append(ip)
        
        # Clean up expired lockouts
        for ip in result['expired']:
            del lockouts[ip]
        
        if result['expired']:
            self.save_lockouts(lockouts)
        
        return result
    
    def send_lockout_notification(self, ip_address, reason, admin_email='atlasnexushelp@gmail.com'):
        """Send lockout notification to admin"""
        lockouts = self.load_lockouts()
        lockout_data = lockouts.get(ip_address, {})
        
        unlock_token = lockout_data.get('unlock_token', secrets.token_urlsafe(32))
        reference_code = lockout_data.get('reference_code', 'N/A')
        
        # Determine base URL
        from config import get_base_url
        base_url = get_base_url()
        unlock_link = f"{base_url}admin/unlock-ip?token={unlock_token}&ip={ip_address}"
        
        email_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #ef4444;">🚨 Security Alert - IP Lockout</h2>
                    <p><strong>IP Address:</strong> {ip_address}</p>
                    <p><strong>Reason:</strong> {reason}</p>
                    <p><strong>Reference Code:</strong> {reference_code}</p>
                    <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    
                    <div style="margin: 20px 0; padding: 15px; background: #fef2f2; border: 1px solid #fecaca; border-radius: 5px;">
                        <p style="color: #991b1b; margin: 0;">This IP has been automatically locked out due to suspicious activity.</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="{unlock_link}" style="display: inline-block; background: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                            Unlock This IP
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 12px; margin-top: 20px;">
                        If you did not expect this alert, please review your security settings immediately.
                    </p>
                </div>
            </body>
        </html>
        """
        
        return send_email(admin_email, f'Security Alert: IP {ip_address} Locked', email_html)

# Create global instance
ip_manager = IPManager()