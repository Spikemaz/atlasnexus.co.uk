"""
AtlasNexus - Single File Application
Everything in one place - no confusion
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime, timedelta
import secrets
import os
import socket
import subprocess
import sys

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
        'Dashboard.html',
        '404.html'
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

# ==================== FLASK APP ====================
app = Flask(__name__)
# Use a fixed secret key so sessions persist across restarts
app.secret_key = 'your-fixed-secret-key-keep-this-secure-in-production-2024'
app.permanent_session_lifetime = timedelta(minutes=PERMANENT_SESSION_LIFETIME)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = SESSION_COOKIE_SECURE
app.config['DEBUG'] = DEBUG

@app.route('/')
def index():
    """Gate 1 - Site Authentication"""
    ip_address = request.remote_addr
    session.permanent = True
    
    # Check for 24-hour lockout
    lockout_24h = session.get(f'lockout_24h_{ip_address}')
    if lockout_24h:
        if isinstance(lockout_24h, str):
            lockout_24h = datetime.fromisoformat(lockout_24h)
        if datetime.now() < lockout_24h:
            # Get or generate reference code for 24h lockout
            ref_code = session.get(f'reference_code_{ip_address}')
            if not ref_code:
                import random
                import string
                ref_code = 'REF-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                session[f'reference_code_{ip_address}'] = ref_code
            return render_template('Gate1.html', 
                                 state='blocked_24h',
                                 blocked_until=lockout_24h,
                                 is_24h_lockout=True,
                                 reference_code=ref_code)
        else:
            # 24-hour lockout expired - apply permanent blackscreen
            session[f'permanent_block_{ip_address}'] = True
            return render_template('Gate1.html', state='blackscreen', ip_address=ip_address)
    
    # Check for permanent blacklist
    if session.get(f'permanent_block_{ip_address}'):
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
    ip_address = request.remote_addr
    password = request.form.get('site_password', '').strip()
    
    # Check if already blocked
    if session.get(f'permanent_block_{ip_address}'):
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
        return jsonify({'status': 'success', 'redirect': url_for('secure_login')}), 200
    
    # Failed attempt
    attempts_left = MAX_ATTEMPTS_BEFORE_BLOCK - attempt_count
    
    if attempt_count >= MAX_ATTEMPTS_BEFORE_BLACKLIST:
        # Permanent blacklist
        session[f'permanent_block_{ip_address}'] = True
        return jsonify({
            'status': 'blacklisted',
            'message': 'Access permanently denied',
            'redirect': url_for('index')
        }), 403
    elif attempt_count >= MAX_ATTEMPTS_BEFORE_BLOCK:
        # Temporary block
        blocked_until = datetime.now() + timedelta(minutes=BLOCK_DURATION_MINUTES)
        session[f'blocked_until_{ip_address}'] = blocked_until.isoformat()
        # Generate and store reference code once
        if not session.get(f'reference_code_{ip_address}'):
            import random
            import string
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
            'message': f'Invalid password. {attempts_left} attempts remaining'
        }), 401

@app.route('/blocked')
def blocked():
    """Handle blocked page with hidden unlock"""
    ip_address = request.remote_addr
    
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
    """Handle global unlock attempts"""
    ip_address = request.remote_addr
    unlock_code = request.json.get('code', '')
    
    if unlock_code == GLOBAL_UNLOCK_CODE:
        # Clear ALL session data for this IP
        for key in list(session.keys()):
            if ip_address in key:
                session.pop(key, None)
        return jsonify({'status': 'success', 'redirect': '/'})
    else:
        # Wrong code = immediate 24-hour lockout (only 1 attempt allowed)
        lockout_until = datetime.now() + timedelta(hours=LOCKOUT_DURATION_HOURS)
        session[f'lockout_24h_{ip_address}'] = lockout_until.isoformat()
        return jsonify({
            'status': 'lockout',
            'message': '24-hour lockout applied',
            'redirect': '/'
        })

@app.route('/secure-login')
def secure_login():
    """Gate 2 - User Authentication"""
    ip_address = request.remote_addr
    
    # Verify site authentication
    if not session.get(f'site_authenticated_{ip_address}'):
        return redirect(url_for('index'))
    
    # Check if user authenticated
    if session.get(f'user_authenticated_{ip_address}'):
        return redirect(url_for('dashboard'))
    
    return render_template('Gate2.html')

@app.route('/auth', methods=['POST'])
def auth():
    """Handle user authentication"""
    ip_address = request.remote_addr
    
    # Verify site authentication first
    if not session.get(f'site_authenticated_{ip_address}'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    
    # Simple validation (expand as needed)
    if email and password:
        session[f'user_authenticated_{ip_address}'] = True
        session[f'username_{ip_address}'] = email.split('@')[0]  # Use email prefix as username
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'success', 'redirect': url_for('dashboard')})
        else:
            # Regular form submission - redirect directly
            return redirect(url_for('dashboard'))
    
    # Failed authentication
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
    else:
        # Regular form submission - redirect back to login
        return redirect(url_for('secure_login'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    ip_address = request.remote_addr
    
    # Verify both authentications
    if not session.get(f'site_authenticated_{ip_address}'):
        return redirect(url_for('index'))
    if not session.get(f'user_authenticated_{ip_address}'):
        return redirect(url_for('secure_login'))
    
    username = session.get(f'username_{ip_address}', 'User')
    return render_template('Dashboard.html', username=username)

@app.route('/logout')
def logout():
    """Clear session and logout"""
    ip_address = request.remote_addr
    
    # Clear user authentication only
    session.pop(f'user_authenticated_{ip_address}', None)
    session.pop(f'username_{ip_address}', None)
    
    return redirect(url_for('secure_login'))

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