"""
Authentication Helper Module
============================
Decorators and utilities for authentication and authorization
"""

from functools import wraps
from flask import session, redirect, url_for, request, jsonify

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
        return request.remote_addr or 'unknown'

def require_site_auth(f):
    """Decorator to require site authentication (Gate1)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip_address = get_real_ip()
        if not session.get(f'site_authenticated_{ip_address}'):
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def require_user_auth(f):
    """Decorator to require user authentication (Gate2)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip_address = get_real_ip()
        if not session.get(f'site_authenticated_{ip_address}'):
            return redirect(url_for('index'))
        if not session.get(f'user_authenticated_{ip_address}'):
            return redirect(url_for('secure_login'))
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip_address = get_real_ip()
        if not session.get(f'is_admin_{ip_address}'):
            # Check if it's an API call
            if request.path.startswith('/api/') or request.path.startswith('/admin/'):
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def require_internal_or_admin(f):
    """Decorator to require internal account or admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip_address = get_real_ip()
        
        # Check basic auth first
        if not session.get(f'user_authenticated_{ip_address}'):
            return redirect(url_for('secure_login'))
        
        # Check if admin
        if session.get(f'is_admin_{ip_address}'):
            return f(*args, **kwargs)
        
        # Check account type
        from utils import load_json_db
        import os
        users = load_json_db(os.path.join('data', 'users.json'))
        username = session.get(f'username_{ip_address}')
        
        if username in users:
            account_type = users[username].get('account_type', 'external')
            if account_type == 'internal':
                return f(*args, **kwargs)
        
        # Not authorized
        return redirect(url_for('dashboard'))
    return decorated_function

def check_auth_status():
    """Check current authentication status"""
    ip_address = get_real_ip()
    return {
        'ip_address': ip_address,
        'site_authenticated': session.get(f'site_authenticated_{ip_address}', False),
        'user_authenticated': session.get(f'user_authenticated_{ip_address}', False),
        'is_admin': session.get(f'is_admin_{ip_address}', False),
        'username': session.get(f'username_{ip_address}'),
        'user_email': session.get(f'user_email_{ip_address}'),
        'account_type': session.get(f'account_type_{ip_address}', 'external')
    }

def clear_session(ip_address=None):
    """Clear all session data for an IP"""
    if not ip_address:
        ip_address = get_real_ip()
    
    # List of session keys to clear
    keys_to_clear = [
        f'site_authenticated_{ip_address}',
        f'user_authenticated_{ip_address}',
        f'is_admin_{ip_address}',
        f'username_{ip_address}',
        f'user_email_{ip_address}',
        f'access_level_{ip_address}',
        f'account_type_{ip_address}',
        f'blocked_until_{ip_address}',
        f'login_time_{ip_address}',
        f'registration_pending_{ip_address}'
    ]
    
    for key in keys_to_clear:
        if key in session:
            session.pop(key)
    
    # Also clear any dynamic keys
    for key in list(session.keys()):
        if ip_address in key:
            session.pop(key)

def set_user_session(ip_address, user_data):
    """Set user session data after successful authentication"""
    session[f'user_authenticated_{ip_address}'] = True
    session[f'username_{ip_address}'] = user_data.get('full_name', user_data.get('email'))
    session[f'user_email_{ip_address}'] = user_data.get('email')
    session[f'account_type_{ip_address}'] = user_data.get('account_type', 'external')
    session[f'login_time_{ip_address}'] = user_data.get('login_time')
    
    # Set admin flag if applicable
    if user_data.get('email') == 'spikemaz8@aol.com':
        session[f'is_admin_{ip_address}'] = True
        session[f'access_level_{ip_address}'] = 'admin'
    elif user_data.get('account_type') == 'internal':
        session[f'access_level_{ip_address}'] = 'internal'
    else:
        session[f'access_level_{ip_address}'] = 'external'
    
    # Make session permanent
    session.permanent = True
    session.modified = True