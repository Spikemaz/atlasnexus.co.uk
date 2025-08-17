#!/usr/bin/env python3
"""
AtlasNexus - Professional Securitization Platform
Clean, production-ready implementation
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
# ProxyFix not needed for basic setup
from datetime import datetime, timedelta
import os
import secrets

# Initialize Flask application
app = Flask(__name__)

# Security configuration
app.secret_key = os.environ.get('SECRET_KEY', 'AtlasNexus_2024_Production_Key_' + secrets.token_hex(16))
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# App is ready for production use

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Security tracking
try:
    from security_tracker import security_tracker
    SECURITY_TRACKING = True
except ImportError:
    SECURITY_TRACKING = False

# Site access passwords
SITE_PASSWORDS = {
    'RedAMC': 'internal',
    'PartnerAccess': 'external'
}

# Admin credentials (in production, use environment variables)
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'marcus@atlasnexus.co.uk')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'MarcusAdmin2024')

# Simple user store (in production, use a database)
users_db = {
    ADMIN_EMAIL: {
        'id': 1,
        'name': 'Marcus Moore',
        'password_hash': generate_password_hash(ADMIN_PASSWORD),
        'role': 'admin'
    }
}

class User(UserMixin):
    """User model for Flask-Login"""
    def __init__(self, user_id, email, name, role):
        self.id = user_id
        self.email = email
        self.name = name
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    for email, user_data in users_db.items():
        if str(user_data['id']) == str(user_id):
            return User(user_data['id'], email, user_data['name'], user_data['role'])
    return None

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Landing page - Security Gate 1"""
    # If already passed Gate 1, redirect to Gate 2
    if session.get('site_authenticated'):
        return redirect(url_for('login'))
    
    # Check for security blocks
    ip = request.remote_addr
    if session.get(f'blocked_until_{ip}'):
        blocked_until = session.get(f'blocked_until_{ip}')
        if isinstance(blocked_until, str):
            blocked_until = datetime.fromisoformat(blocked_until)
        if datetime.now() < blocked_until:
            return render_template('site_auth.html', blocked=True, blocked_until=blocked_until)
    
    # Show password form
    attempts = session.get(f'attempts_{ip}', 0)
    return render_template('site_auth.html', attempts=attempts)

@app.route('/site-auth', methods=['POST'])
def site_auth():
    """Handle site password verification"""
    import sys
    print(f"[SITE-AUTH] Route called with method {request.method}", file=sys.stderr, flush=True)
    password = request.form.get('site_password', '').strip()
    ip = request.remote_addr
    print(f"[SITE-AUTH] Password: '{password}', IP: {ip}", file=sys.stderr, flush=True)
    print(f"[SITE-AUTH] Valid passwords: {list(SITE_PASSWORDS.keys())}", file=sys.stderr, flush=True)
    
    # Check if password is correct
    if password in SITE_PASSWORDS:
        print(f"[SITE-AUTH] Password CORRECT! Setting session and redirecting to /login", file=sys.stderr, flush=True)
        # Clear any blocks
        session.pop(f'attempts_{ip}', None)
        session.pop(f'blocked_until_{ip}', None)
        
        # Set authentication
        session['site_authenticated'] = True
        session['access_type'] = SITE_PASSWORDS[password]
        session.permanent = True
        
        # Log successful access if tracking enabled
        if SECURITY_TRACKING:
            security_tracker.clear_successful_login(ip)
        
        # Redirect to login page (Gate 2) - using direct path
        print(f"[SITE-AUTH] About to redirect to /login", file=sys.stderr, flush=True)
        return redirect('/login')
    
    # Wrong password - increment attempts
    attempts = session.get(f'attempts_{ip}', 0) + 1
    session[f'attempts_{ip}'] = attempts
    
    # Log failed attempt if tracking enabled
    if SECURITY_TRACKING:
        security_tracker.log_failed_attempt(
            ip_address=ip,
            password=password,
            user_agent=request.headers.get('User-Agent', 'Unknown'),
            session_id=session.get('session_id', secrets.token_hex(16))
        )
    
    # Check if should block
    if attempts >= 4:
        session[f'blocked_until_{ip}'] = datetime.now() + timedelta(minutes=45)
        return render_template('site_auth.html', blocked=True)
    
    # Show error and form again
    flash('Invalid password. Please try again.', 'error')
    return render_template('site_auth.html', attempts=attempts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page - Security Gate 2"""
    import sys
    print(f"[LOGIN] Session data: {dict(session)}", file=sys.stderr, flush=True)
    # Check if passed Gate 1
    if not session.get('site_authenticated'):
        print(f"[LOGIN] No site_authenticated in session, redirecting to /", file=sys.stderr, flush=True)
        return redirect(url_for('index'))
    
    # If already logged in, go to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        
        # Check credentials
        if email in users_db:
            user_data = users_db[email]
            if check_password_hash(user_data['password_hash'], password):
                user = User(user_data['id'], email, user_data['name'], user_data['role'])
                login_user(user, remember=True)
                
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        
        flash('Invalid email or password.', 'danger')
    
    return render_template('secure_login.html')

@app.route('/register', methods=['POST'])
def register():
    """Handle registration requests"""
    if not session.get('site_authenticated'):
        return redirect(url_for('index'))
    
    # Get form data
    email = request.form.get('email', '').strip().lower()
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    
    # Log registration request
    print(f"Registration request: {email} ({first_name} {last_name})")
    
    flash('Registration submitted for review. We will contact you soon.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html', user=current_user)

@app.route('/admin')
@login_required
def admin():
    """Admin panel"""
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get security data if available
    incidents = []
    if SECURITY_TRACKING:
        try:
            incidents = security_tracker.get_recent_incidents(limit=50)
        except:
            pass
    
    return render_template('admin_simple.html', 
                         user=current_user,
                         security_incidents=incidents)

@app.route('/logout')
@login_required
def logout():
    """Logout and clear session"""
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/settings')
@login_required
def settings():
    """User settings"""
    return render_template('settings.html', user=current_user)

@app.route('/market-updates')
@login_required
def market_updates():
    """Market intelligence"""
    return render_template('market_updates.html', user=current_user)

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    print(f"404 ERROR: {request.url} - {request.method}", flush=True)
    # Don't redirect, just show 404 page
    if request.method == 'POST':
        return jsonify({'error': 'Not found'}), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500

# ==================== HEALTH CHECK ====================

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

# ==================== MAIN ====================

# For Vercel deployment
application = app

if __name__ == '__main__':
    # Only runs locally, not on Vercel
    print("\n" + "="*60)
    print("ATLASNEXUS SECURITIZATION PLATFORM")
    print("="*60)
    print(f"\nSite Passwords: {', '.join(SITE_PASSWORDS.keys())}")
    print(f"Admin Login: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print(f"URL: http://localhost:5000")
    print("="*60 + "\n")
    
    # Run with proper configuration
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )