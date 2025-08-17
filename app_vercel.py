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

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'AtlasNexus_2024_Secure_Key_For_Production_Live'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'secure_login'

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
    
    # If user is already logged in, go to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Show main login page
    return render_template('secure_login.html')

@app.route('/site_auth', methods=['POST'])
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
        
        # Store access code
        session['access_code'] = 'RedAMC' if password == SITE_PASSWORD_INTERNAL else 'PartnerAccess'
        session['site_authenticated'] = True
        
        return redirect(url_for('secure_login'))
    else:
        # Failed attempt - log it (simplified for production)
        print(f"Security attempt: IP={ip_address}, attempt={attempt_count}, password={password}")
        
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

@app.route('/secure_login', methods=['GET', 'POST'])
def secure_login():
    """Main login and registration page."""
    if 'site_authenticated' not in session:
        return redirect(url_for('index'))
    
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
                    return redirect(url_for('dashboard'))
            
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

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with admin panel access for Marcus."""
    show_admin_link = current_user.email == ADMIN_EMAIL
    return render_template('dashboard.html', user=current_user, show_admin_link=show_admin_link)

@app.route('/market-updates')
def market_updates():
    """Market intelligence preview page."""
    return render_template('market_updates.html')

@app.route('/admin')
@login_required
def admin_panel():
    """Admin panel - only accessible to Marcus after login."""
    if current_user.email != ADMIN_EMAIL:
        flash('Access denied. Admin access required.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Simple admin view - no database operations for serverless
    return render_template('admin_simple.html')

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