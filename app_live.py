"""
AtlasNexus - Unified Application
Works for both local development and production
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime, timedelta
import secrets
from config import config, IS_LOCAL, IS_PRODUCTION

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.permanent_session_lifetime = timedelta(minutes=config.PERMANENT_SESSION_LIFETIME)

# Apply configuration
app.config['SESSION_COOKIE_HTTPONLY'] = config.SESSION_COOKIE_HTTPONLY
app.config['SESSION_COOKIE_SAMESITE'] = config.SESSION_COOKIE_SAMESITE
app.config['SESSION_COOKIE_SECURE'] = config.SESSION_COOKIE_SECURE
app.config['DEBUG'] = config.DEBUG

# Optional: Add environment indicator for debugging
if config.SHOW_DEBUG_INFO:
    print(f"[INFO] Running in {'LOCAL' if IS_LOCAL else 'PRODUCTION'} mode")
    print(f"[INFO] Debug: {config.DEBUG}, Secure Cookies: {config.SESSION_COOKIE_SECURE}")

@app.route('/')
def index():
    """Gate 1 - Site Authentication"""
    ip_address = request.remote_addr
    session.permanent = True
    
    # Debug logging only in local mode
    if config.SHOW_DEBUG_INFO:
        print(f"[DEBUG] IP: {ip_address}")
        print(f"[DEBUG] Session data: {dict(session)}")
        print(f"[DEBUG] Attempt count: {session.get(f'attempt_count_{ip_address}', 0)}")
        print(f"[DEBUG] Blocked until: {session.get(f'blocked_until_{ip_address}')}")
    
    # Check for 24-hour lockout (after global unlock failure)
    lockout_24h = session.get(f'lockout_24h_{ip_address}')
    if lockout_24h:
        from datetime import datetime
        if isinstance(lockout_24h, str):
            lockout_24h = datetime.fromisoformat(lockout_24h)
        if datetime.now() < lockout_24h:
            remaining_hours = int((lockout_24h - datetime.now()).total_seconds() / 3600)
            remaining_minutes = int(((lockout_24h - datetime.now()).total_seconds() % 3600) / 60)
            return render_template('blocked.html', 
                                 blocked_until=lockout_24h,
                                 remaining_minutes=remaining_hours * 60 + remaining_minutes,
                                 ip_address=ip_address,
                                 no_hidden_menu=True,
                                 lockout_24h=True)
    
    # Check if using global unlock FIRST (before any blocking checks)
    if request.args.get('global_unlock') == 'true':
        session.pop(f'blocked_30min_{ip_address}', None)
        session.pop(f'blocked_until_{ip_address}', None)
        session.pop(f'blackscreen_{ip_address}', None)
        session['global_unlock_active'] = True
        session[f'global_unlock_attempts_{ip_address}'] = 0
        session.pop(f'attempt_count_{ip_address}', None)
    
    # Check for blackscreen parameter (from failed global unlock)
    if request.args.get('blackscreen') == 'true':
        session[f'blackscreen_{ip_address}'] = True
        session.permanent = True
        return render_template('blackscreen.html', ip_address=ip_address)
    
    # Check if blacklisted (but skip if global_unlock was just activated)
    if session.get(f'blackscreen_{ip_address}') and not request.args.get('global_unlock'):
        return render_template('blackscreen.html', ip_address=ip_address)
    
    # Check if in 30-minute block (but skip if global_unlock was just activated)
    if session.get(f'blocked_30min_{ip_address}') and not request.args.get('global_unlock'):
        from datetime import datetime, timedelta
        blocked_until = session.get(f'blocked_until_{ip_address}')
        if blocked_until:
            if isinstance(blocked_until, str):
                blocked_until = datetime.fromisoformat(blocked_until)
            remaining_minutes = int((blocked_until - datetime.now()).total_seconds() / 60)
            if remaining_minutes <= 0:
                session.pop(f'blocked_30min_{ip_address}', None)
                session.pop(f'blocked_until_{ip_address}', None)
                session[f'blackscreen_{ip_address}'] = True
                return render_template('blackscreen.html', ip_address=ip_address)
            else:
                return render_template('blocked.html',
                                     blocked_until=blocked_until,
                                     remaining_minutes=remaining_minutes,
                                     ip_address=ip_address,
                                     no_hidden_menu=False)
    
    attempt_count = session.get(f'attempt_count_{ip_address}', 0)
    global_unlock_active = session.get('global_unlock_active', False)
    global_attempts = session.get(f'global_unlock_attempts_{ip_address}', 0)
    
    return render_template('site_auth.html', 
                         attempt_count=attempt_count, 
                         ip_address=ip_address,
                         global_unlock_active=global_unlock_active,
                         global_attempts=global_attempts)

@app.route('/auth', methods=['POST'])
def authenticate():
    """Handle Gate 1 authentication with security tracking"""
    from datetime import datetime, timedelta
    password = request.form.get('site_password', '')
    ip_address = request.remote_addr
    
    # Check if using global unlock (limited to 3 attempts)
    if session.get('global_unlock_active'):
        global_attempts = session.get(f'global_unlock_attempts_{ip_address}', 0)
        
        if password in config.VALID_PASSWORDS:
            # Success with global unlock - reset ALL security tracking
            session.pop('global_unlock_active', None)
            session.pop(f'global_unlock_attempts_{ip_address}', None)
            session.pop(f'attempt_count_{ip_address}', None)
            session.pop(f'blocked_until_{ip_address}', None)
            session.pop(f'blackscreen_{ip_address}', None)
            session.pop(f'lockout_24h_{ip_address}', None)
            session['gate1_passed'] = True
            session['site_authenticated'] = True
            session.permanent = True
            return jsonify({'success': True, 'redirect': '/secure-login'})
        else:
            # Failed attempt with global unlock
            global_attempts += 1
            session[f'global_unlock_attempts_{ip_address}'] = global_attempts
            
            if global_attempts >= config.MAX_GLOBAL_UNLOCK_ATTEMPTS:
                # Failed 3 times with global unlock - 24 hour lockout
                lockout_until = datetime.now() + timedelta(hours=config.LOCKOUT_DURATION_HOURS)
                session[f'lockout_24h_{ip_address}'] = lockout_until.isoformat()
                session.pop('global_unlock_active', None)
                return jsonify({'success': False, 'redirect': '/', 'lockout_24h': True})
            else:
                remaining = config.MAX_GLOBAL_UNLOCK_ATTEMPTS - global_attempts
                return jsonify({'success': False, 'message': f'Global unlock: {remaining} attempts remaining'})
    
    # Regular attempt handling
    attempt_count = session.get(f'attempt_count_{ip_address}', 0)
    
    # Check if already blacklisted
    if session.get(f'blackscreen_{ip_address}'):
        return jsonify({'success': False, 'redirect': '/', 'blackscreen': True})
    
    # Check if temporarily blocked
    blocked_until = session.get(f'blocked_until_{ip_address}')
    if blocked_until:
        if isinstance(blocked_until, str):
            blocked_until = datetime.fromisoformat(blocked_until)
        if datetime.now() < blocked_until:
            return jsonify({'success': False, 'redirect': '/', 'blocked': True})
    
    # Check actual passwords
    if password in config.VALID_PASSWORDS:
        # Reset ALL security tracking on successful login
        session.pop(f'attempt_count_{ip_address}', None)
        session.pop(f'blocked_until_{ip_address}', None)
        session.pop(f'blocked_30min_{ip_address}', None)
        session.pop(f'blackscreen_{ip_address}', None)
        session.pop(f'lockout_24h_{ip_address}', None)
        session.pop('global_unlock_active', None)
        session.pop(f'global_unlock_attempts_{ip_address}', None)
        session['gate1_passed'] = True
        session['site_authenticated'] = True
        session.permanent = True
        return jsonify({'success': True, 'redirect': '/secure-login'})
    else:
        # Increment attempt count
        attempt_count += 1
        session[f'attempt_count_{ip_address}'] = attempt_count
        
        # Handle security escalation
        if attempt_count >= config.MAX_ATTEMPTS_BEFORE_BLACKLIST:
            # Permanent blacklist after 5 attempts
            session[f'blackscreen_{ip_address}'] = True
            return jsonify({'success': False, 'redirect': '/', 'blackscreen': True})
        elif attempt_count == config.MAX_ATTEMPTS_BEFORE_BLOCK:
            # 30-minute block after 4 attempts
            blocked_until = datetime.now() + timedelta(minutes=config.BLOCK_DURATION_MINUTES)
            session[f'blocked_until_{ip_address}'] = blocked_until.isoformat()
            session[f'blocked_30min_{ip_address}'] = True
            session.permanent = True
            return jsonify({'success': False, 'redirect': '/', 'blocked': True})
        else:
            # Show remaining attempts
            remaining = config.MAX_ATTEMPTS_BEFORE_BLOCK - attempt_count
            return jsonify({'success': False, 'message': f'Invalid password. {remaining} attempts remaining'})

@app.route('/secure-login')
def secure_login():
    """Gate 2 - Secure Login with Live Ticker"""
    if not session.get('gate1_passed'):
        return redirect(url_for('index'))
    
    return render_template('secure_login.html')

@app.route('/secure-login-submit', methods=['POST'])
def secure_login_submit():
    """Handle Gate 2 login submission"""
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    
    # Simple authentication
    if email and password:
        session['authenticated'] = True
        session['username'] = email
        session.permanent = True
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('secure_login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """Main Dashboard"""
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    
    return render_template('dashboard.html')

@app.route('/site-auth', methods=['POST'])
def site_auth():
    """Alternative endpoint for Gate 1 with security tracking"""
    from datetime import datetime, timedelta
    password = request.form.get('site_password', '')
    ip_address = request.remote_addr
    
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Get attempt count for this IP
    attempt_count = session.get(f'attempt_count_{ip_address}', 0)
    
    # Check if already blacklisted
    if session.get(f'blackscreen_{ip_address}'):
        if is_ajax:
            return jsonify({'success': False, 'redirect': '/', 'blackscreen': True})
        return render_template('blackscreen.html', ip_address=ip_address)
    
    # Check if temporarily blocked
    blocked_until = session.get(f'blocked_until_{ip_address}')
    if blocked_until:
        if isinstance(blocked_until, str):
            blocked_until = datetime.fromisoformat(blocked_until)
        if datetime.now() < blocked_until:
            remaining_minutes = int((blocked_until - datetime.now()).total_seconds() / 60)
            if is_ajax:
                return jsonify({'success': False, 'redirect': '/', 'blocked': True})
            return render_template('blocked.html', 
                                 blocked_until=blocked_until,
                                 remaining_minutes=remaining_minutes,
                                 ip_address=ip_address,
                                 no_hidden_menu=False)
    
    # Check actual passwords
    if password in config.VALID_PASSWORDS:
        # Reset ALL security tracking on successful login
        session.pop(f'attempt_count_{ip_address}', None)
        session.pop(f'blocked_until_{ip_address}', None)
        session.pop(f'blocked_30min_{ip_address}', None)
        session.pop(f'blackscreen_{ip_address}', None)
        session.pop(f'lockout_24h_{ip_address}', None)
        session.pop('global_unlock_active', None)
        session.pop(f'global_unlock_attempts_{ip_address}', None)
        session['gate1_passed'] = True
        session['site_authenticated'] = True
        session.permanent = True
        if is_ajax:
            return jsonify({'success': True, 'redirect': '/secure-login'})
        return redirect(url_for('secure_login'))
    else:
        # Increment attempt count
        attempt_count += 1
        session[f'attempt_count_{ip_address}'] = attempt_count
        
        # Handle security escalation
        if attempt_count >= config.MAX_ATTEMPTS_BEFORE_BLACKLIST:
            session[f'blackscreen_{ip_address}'] = True
            session.permanent = True
            if is_ajax:
                return jsonify({'success': False, 'redirect': '/', 'blackscreen': True})
            return render_template('blackscreen.html', ip_address=ip_address)
        elif attempt_count == config.MAX_ATTEMPTS_BEFORE_BLOCK:
            blocked_until = datetime.now() + timedelta(minutes=config.BLOCK_DURATION_MINUTES)
            session[f'blocked_until_{ip_address}'] = blocked_until.isoformat()
            session[f'blocked_30min_{ip_address}'] = True
            session.permanent = True
            remaining_minutes = config.BLOCK_DURATION_MINUTES
            if is_ajax:
                return jsonify({'success': False, 'redirect': '/', 'blocked': True})
            return render_template('blocked.html', 
                                 blocked_until=blocked_until,
                                 remaining_minutes=remaining_minutes,
                                 ip_address=ip_address,
                                 no_hidden_menu=False)
        else:
            remaining = config.MAX_ATTEMPTS_BEFORE_BLOCK - attempt_count
            if is_ajax:
                return jsonify({'success': False, 'message': f'Invalid password. {remaining} attempts remaining'})
            return render_template('site_auth.html', 
                                 error=f'Invalid password. {remaining} attempts remaining',
                                 attempt_count=attempt_count)

# Minimal API endpoints for functionality
@app.route('/api/log-password-attempt', methods=['POST'])
def log_password_attempt():
    return jsonify({'success': True})

@app.route('/api/log_blocked_access', methods=['POST'])
def log_blocked_access():
    return jsonify({'success': True})

@app.route('/upload_data', methods=['POST'])
def upload_data():
    """Handle file uploads"""
    return jsonify({'success': True, 'message': 'Upload functionality not implemented in test mode'})

@app.route('/api/market-data')
def api_market_data():
    """API endpoint for market data"""
    return jsonify({
        'success': True,
        'data': {
            'performance': '+2.4%',
            'yield': '3.8%',
            'rating': 'AA+'
        }
    })

@app.route('/api/portfolio-data')
def api_portfolio_data():
    """API endpoint for portfolio data"""
    return jsonify({
        'success': True,
        'data': {
            'total_assets': '€2.4B',
            'portfolios': 127,
            'active_deals': 42
        }
    })

@app.route('/api/password_status')
def api_password_status():
    """API endpoint for password status"""
    return jsonify({
        'success': True,
        'expires_in': '45 minutes',
        'strength': 'strong',
        'last_changed': '2025-01-15'
    })

@app.route('/api/renew_password', methods=['POST'])
def api_renew_password():
    """API endpoint for password renewal"""
    return jsonify({
        'success': True,
        'message': 'Password renewed successfully'
    })

@app.route('/account')
def account():
    """Account page"""
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    return render_template('account.html')

@app.route('/analysis')
def analysis():
    """Analysis page"""
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    return render_template('analysis.html')

@app.route('/market-updates')
def market_updates():
    """Market updates page"""
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    return render_template('market_updates.html')

@app.route('/settings')
def settings():
    """Settings page"""
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    return render_template('settings.html')

@app.route('/results')
def results():
    """Results page"""
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    return render_template('results.html')

@app.route('/pending-approval')
def pending_approval():
    """Pending approval page"""
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    return render_template('pending_approval.html')

@app.route('/admin')
def admin():
    """Admin page"""
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    return render_template('admin.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Use configuration values for running the app
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)