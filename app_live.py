"""
AtlasNexus - LIVE PRODUCTION VERSION
Deployed to atlasnexus.co.uk with full security enabled
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import secrets
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'AtlasNexus_Live_2024_' + secrets.token_hex(32))
app.permanent_session_lifetime = timedelta(minutes=45)

# Custom Jinja2 filters
@app.template_filter('datetime')
def datetime_filter(value, format_string='%B %d, %Y'):
    """Format a datetime object or 'now' string"""
    if value == 'now':
        dt = datetime.now()
    elif isinstance(value, str):
        dt = datetime.now()
    else:
        dt = value
    
    # Convert Django-style format to Python strftime format
    if format_string == 'l, F d, Y':
        return dt.strftime('%A, %B %d, %Y')
    return dt.strftime(format_string)

# PRODUCTION MODE - Full security enabled
TESTING_MODE = False

# Gate 1 Password
SITE_PASSWORD = 'SpikeMaz'

# Gate 2 Credentials
AUTHORIZED_USER = {
    'email': 'spikemaz8@aol.com',  # Case-insensitive
    'password': 'SpikeMaz'
}

# Security tracking
failed_attempts = {}
blocked_ips = set()

@app.context_processor
def inject_user():
    """Inject current_user into all templates"""
    class User:
        def __init__(self, authenticated):
            self.is_authenticated = authenticated
            self.username = session.get('username', 'Guest')
    
    current_user = User(session.get('authenticated', False))
    return dict(current_user=current_user)

@app.route('/')
def index():
    """Gate 1 - Site Authentication"""
    client_ip = request.remote_addr
    
    # Check if IP is blocked
    if client_ip in blocked_ips:
        return render_template('site_auth.html', blocked=True)
    
    attempts = failed_attempts.get(client_ip, [])
    recent_attempts = [a for a in attempts if a > datetime.now() - timedelta(minutes=15)]
    
    if len(recent_attempts) >= 5:
        blocked_ips.add(client_ip)
        return render_template('site_auth.html', blocked=True)
    
    return render_template('site_auth.html')

@app.route('/auth', methods=['POST'])
def authenticate():
    """Handle Gate 1 authentication"""
    # Check both field names since the form might use either
    password = request.form.get('site_password') or request.form.get('password', '')
    client_ip = request.remote_addr
    
    # Check if password is correct (SpikeMaz)
    if password == SITE_PASSWORD:
        # Clear failed attempts
        if client_ip in failed_attempts:
            failed_attempts[client_ip] = []
        
        # Set session
        session['gate1_passed'] = True
        session['site_authenticated'] = True
        session.permanent = True
        
        return jsonify({'success': True, 'redirect': '/secure-login'})
    
    # Wrong password - track attempt
    if client_ip not in failed_attempts:
        failed_attempts[client_ip] = []
    failed_attempts[client_ip].append(datetime.now())
    
    # Check recent attempts
    recent_attempts = [
        a for a in failed_attempts[client_ip]
        if a > datetime.now() - timedelta(minutes=15)
    ]
    
    if len(recent_attempts) >= 5:
        blocked_ips.add(client_ip)
        return jsonify({'success': False, 'blocked': True})
    
    return jsonify({
        'success': False,
        'attempts': len(recent_attempts),
        'message': 'Invalid password'
    })

@app.route('/secure-login')
def secure_login():
    """Gate 2 - Secure Login with Live Ticker"""
    # Must pass Gate 1 first
    if not session.get('gate1_passed'):
        return redirect(url_for('index'))
    
    return render_template('secure_login.html')

@app.route('/secure-login-submit', methods=['POST'])
def secure_login_submit():
    """Handle Gate 2 login submission"""
    if not session.get('gate1_passed'):
        return jsonify({'success': False, 'message': 'Access denied'})
    
    # Get credentials
    email = request.form.get('email', '').lower().strip()
    password = request.form.get('password', '')
    
    # Check credentials (case-insensitive email)
    if email == AUTHORIZED_USER['email'].lower() and password == AUTHORIZED_USER['password']:
        session['authenticated'] = True
        session['username'] = email
        session.permanent = True
        return redirect(url_for('dashboard'))
    
    # Invalid credentials
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """Main Dashboard - Requires full authentication"""
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    
    # Use standalone dashboard for live version
    return render_template('dashboard_live.html')

@app.route('/site-auth', methods=['POST'])
def site_auth():
    """Alternative endpoint for Gate 1"""
    return authenticate()

# Security API endpoints
@app.route('/api/log-password-attempt', methods=['POST'])
def log_password_attempt():
    """Log failed password attempts"""
    data = request.get_json()
    password = data.get('password', '')
    client_ip = request.remote_addr
    
    # Log the attempt
    if client_ip not in failed_attempts:
        failed_attempts[client_ip] = []
    failed_attempts[client_ip].append(datetime.now())
    
    # Log to file for monitoring
    with open('security_log.txt', 'a') as f:
        f.write(f"[{datetime.now()}] Failed attempt from {client_ip}: {password}\n")
    
    return jsonify({'success': True})

@app.route('/api/log_blocked_access', methods=['POST'])
def log_blocked_access():
    """Log blocked access attempts"""
    client_ip = request.remote_addr
    blocked_ips.add(client_ip)
    
    # Log to file
    with open('security_log.txt', 'a') as f:
        f.write(f"[{datetime.now()}] Blocked IP: {client_ip}\n")
    
    return jsonify({'success': True})

@app.route('/verify-access-code', methods=['POST'])
def verify_access_code():
    """Verify access code for login"""
    if not session.get('gate1_passed'):
        return jsonify({'success': False, 'message': 'Access denied'})
    
    # For now, just redirect to dashboard if Gate 1 was passed
    return jsonify({'success': False, 'message': 'Invalid code'})

@app.route('/register-user', methods=['POST'])
def register_user():
    """Handle user registration"""
    if not session.get('gate1_passed'):
        flash('Access denied. Please authenticate first.', 'danger')
        return redirect(url_for('index'))
    
    # For now, just redirect back with a message
    flash('Registration is currently disabled', 'info')
    return redirect(url_for('secure_login'))

@app.route('/market-updates')
def market_updates():
    """Market updates page"""
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    return render_template('market_updates.html')

@app.route('/logout')
def logout():
    """Clear session and logout"""
    session.clear()
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# For deployment
application = app

if __name__ == '__main__':
    # Production settings
    app.run(debug=False, host='0.0.0.0', port=5000)