#!/usr/bin/env python3
"""
AtlasNexus - Simplified Production Version for Vercel Deployment
Core security gates and authentication only
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
import secrets
try:
    from security_tracker import security_tracker
    SECURITY_TRACKING = True
except ImportError:
    SECURITY_TRACKING = False
    print("Security tracking module not available")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'AtlasNexus_2024_Secure_Key_For_Production_Live'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'secure-login'

# Site passwords
SITE_PASSWORD_INTERNAL = "RedAMC"
SITE_PASSWORD_EXTERNAL = "PartnerAccess"

# Admin credentials
ADMIN_EMAIL = "marcus@atlasnexus.co.uk"
ADMIN_PASSWORD_HASH = generate_password_hash("MarcusAdmin2024")

# Simple user database
users_db = {
    ADMIN_EMAIL: {
        'id': 1,
        'name': 'Marcus Moore',
        'password_hash': ADMIN_PASSWORD_HASH,
        'role': 'admin',
        'email': ADMIN_EMAIL
    }
}

class User(UserMixin):
    def __init__(self, user_id, email, name, role):
        self.id = user_id
        self.email = email
        self.name = name
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    for email, user_data in users_db.items():
        if str(user_data['id']) == str(user_id):
            return User(user_data['id'], email, user_data['name'], user_data['role'])
    return None

@app.route('/')
def index():
    """Main landing page with site password protection."""
    if 'site_authenticated' not in session:
        ip_address = request.remote_addr
        
        # Check blocking status
        blocked_until = session.get(f'blocked_until_{ip_address}')
        if blocked_until:
            # Convert to datetime if it's a string
            if isinstance(blocked_until, str):
                blocked_until = datetime.fromisoformat(blocked_until)
            # Make both naive for comparison
            if datetime.now().replace(tzinfo=None) < blocked_until.replace(tzinfo=None):
                return render_template('site_auth.html', show_blocked=True, blocked_until=blocked_until), 403
        
        if session.get(f'blackscreen_{ip_address}'):
            return render_template('site_auth.html', show_blackscreen=True), 403
            
        attempt_count = session.get(f'attempt_count_{ip_address}', 0)
        return render_template('site_auth.html', attempt_count=attempt_count)
    
    # Site is authenticated, redirect to secure-login (Security Gate 2)
    return redirect('/secure-login')

@app.route('/site-auth', methods=['POST'])
def site_auth():
    """Validate site-wide password with security tracking."""
    password = request.form.get('site_password')
    ip_address = request.remote_addr
    
    # Get attempt count for this IP
    attempt_count = session.get(f'attempt_count_{ip_address}', 0) + 1
    session[f'attempt_count_{ip_address}'] = attempt_count
    
    # Check if already blocked
    blocked_until = session.get(f'blocked_until_{ip_address}')
    if blocked_until:
        # Convert to datetime if it's a string
        if isinstance(blocked_until, str):
            blocked_until = datetime.fromisoformat(blocked_until)
        # Make both naive for comparison
        if datetime.now().replace(tzinfo=None) < blocked_until.replace(tzinfo=None):
            return render_template('site_auth.html', show_blocked=True, blocked_until=blocked_until), 403
    
    # Check if permanently blocked
    if session.get(f'blackscreen_{ip_address}'):
        return render_template('site_auth.html', show_blackscreen=True), 403
    
    if password in [SITE_PASSWORD_INTERNAL, SITE_PASSWORD_EXTERNAL]:
        # Success - clear attempts and store access code
        session.pop(f'attempt_count_{ip_address}', None)
        session.pop(f'blocked_until_{ip_address}', None)
        session.pop(f'blackscreen_{ip_address}', None)
        
        # Clear security tracking for successful login
        if SECURITY_TRACKING:
            security_tracker.clear_successful_login(ip_address)
        
        # Store access code
        session['access_code'] = 'RedAMC' if password == SITE_PASSWORD_INTERNAL else 'PartnerAccess'
        session['site_authenticated'] = True
        
        return redirect('/secure-login')
    else:
        # Failed attempt - log it with security tracking
        print(f"Security attempt: IP={ip_address}, attempt={attempt_count}, password={password}")
        
        # Track failed attempt in security system
        if SECURITY_TRACKING:
            user_agent = request.headers.get('User-Agent', 'Unknown')
            session_id = session.get('session_id', secrets.token_hex(16))
            session['session_id'] = session_id
            
            tracking_result = security_tracker.log_failed_attempt(
                ip_address=ip_address,
                password=password,
                user_agent=user_agent,
                session_id=session_id
            )
            
            # Log if security incident was triggered
            if tracking_result['incident_triggered']:
                print(f"SECURITY INCIDENT: IP {ip_address} triggered lockout after {attempt_count} attempts")
        
        if attempt_count >= 5:
            session[f'blackscreen_{ip_address}'] = True
            return render_template('site_auth.html', show_blackscreen=True), 403
        elif attempt_count == 4:
            blocked_until = datetime.now() + timedelta(minutes=45)
            session[f'blocked_until_{ip_address}'] = blocked_until
            return render_template('site_auth.html', show_blocked=True, blocked_until=blocked_until), 403
        else:
            flash('Invalid password. Please try again.', 'error')
            return render_template('site_auth.html', attempt_count=attempt_count)

@app.route('/secure-login', methods=['GET', 'POST'])
def secure_login():
    """Main login and registration page (Security Gate 2)."""
    # Check if site authentication is complete
    if 'site_authenticated' not in session:
        return redirect('/')
    
    # If already logged in as user, go to dashboard
    if current_user.is_authenticated:
        return redirect('/dashboard')
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'login':
            email = request.form.get('email', '').lower().strip()
            password = request.form.get('password', '')
            
            if email in users_db:
                user_data = users_db[email]
                if check_password_hash(user_data['password_hash'], password):
                    user = User(user_data['id'], email, user_data['name'], user_data['role'])
                    login_user(user, remember=True)
                    return redirect('/dashboard')
            
            flash('Invalid email or password.', 'danger')
        
        elif action == 'register':
            # Simple registration logging
            email = request.form.get('email', '').strip().lower()
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            access_code = session.get('access_code', 'Unknown')
            
            print(f"Registration: {email}, {first_name} {last_name}, access_code: {access_code}")
            flash('Registration submitted for review.', 'success')
    
    return render_template('secure_login.html')

@app.route('/verify-access-code', methods=['POST'])
def verify_access_code():
    """Handle verification code submission."""
    # For now, just redirect back to login
    # In production, this would validate the verification code
    return redirect('/secure-login')

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with admin panel access for Marcus."""
    show_admin_link = current_user.email == ADMIN_EMAIL
    return render_template('dashboard.html', user=current_user, show_admin_link=show_admin_link)

@app.route('/market-updates')
@login_required
def market_updates():
    """Market intelligence preview page."""
    return render_template('market_updates.html')

@app.route('/settings')
@login_required
def settings():
    """User settings and preferences page."""
    return render_template('settings.html', user=current_user)

@app.route('/account')
@app.route('/profile')
@login_required
def account():
    """User account/profile page."""
    return render_template('account.html', user=current_user)

@app.route('/admin-console')
@login_required
def admin_console():
    """Admin panel - only accessible to Marcus after login."""
    if current_user.email != ADMIN_EMAIL:
        flash('Access denied. Admin access required.', 'danger')
        return redirect('/dashboard')
    
    # Get security incidents if tracking is enabled
    security_incidents = []
    ip_reputation = []
    if SECURITY_TRACKING:
        try:
            security_incidents = security_tracker.get_recent_incidents(limit=50)
            ip_reputation = security_tracker.get_ip_reputation_report()
        except Exception as e:
            print(f"Error loading security data: {e}")
    
    return render_template('admin_simple.html', 
                         security_incidents=security_incidents,
                         ip_reputation=ip_reputation)

@app.route('/api/security-incidents')
@login_required
def get_security_incidents():
    """API endpoint for security incidents (admin only)"""
    if current_user.email != ADMIN_EMAIL:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if not SECURITY_TRACKING:
        return jsonify({'incidents': [], 'tracking_enabled': False})
    
    try:
        incidents = security_tracker.get_recent_incidents(limit=100)
        return jsonify({
            'incidents': incidents,
            'tracking_enabled': True,
            'total': len(incidents)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/log-password-attempt', methods=['POST'])
def log_password_attempt():
    """Log password attempts from client-side (secret menu attempts)"""
    if not SECURITY_TRACKING:
        return jsonify({'status': 'tracking_disabled'}), 200
    
    try:
        data = request.json
        ip_address = request.remote_addr
        password = data.get('password', '')
        context = data.get('context', 'unknown')
        user_agent = data.get('userAgent', request.headers.get('User-Agent', 'Unknown'))
        
        # Log the secret menu attempt
        security_tracker.log_failed_attempt(
            ip_address=ip_address,
            password=f"SECRET_MENU:{password}",
            user_agent=user_agent,
            session_id=f"context:{context}"
        )
        
        return jsonify({'status': 'logged'}), 200
    except Exception as e:
        print(f"Error logging password attempt: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    session.clear()
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("AtlasNexus Production Server Starting...")
    print(f"Site Password (Internal): {SITE_PASSWORD_INTERNAL}")
    print(f"Site Password (External): {SITE_PASSWORD_EXTERNAL}")
    print(f"Admin: {ADMIN_EMAIL} / MarcusAdmin2024")
    print("Ready for deployment to atlasnexus.co.uk")
    
    app.run(debug=False, host='0.0.0.0', port=5000)