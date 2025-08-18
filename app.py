"""
AtlasNexus - Local Testing Version
Only includes the 3 essential pages: /, /secure-login, /dashboard
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.permanent_session_lifetime = timedelta(minutes=15)  # Gate 1 timer: 15 minutes

# TESTING MODE - No passwords required for local development
TESTING_MODE = False  # Both local and live use same security now

@app.route('/')
def index():
    """Gate 1 - Site Authentication"""
    ip_address = request.remote_addr
    
    # Check if blacklisted
    if session.get(f'blackscreen_{ip_address}'):
        return render_template('blackscreen.html', ip_address=ip_address)
    
    # Check if temporarily blocked
    blocked_until = session.get(f'blocked_until_{ip_address}')
    if blocked_until:
        from datetime import datetime
        if isinstance(blocked_until, str):
            blocked_until = datetime.fromisoformat(blocked_until)
        if datetime.now() < blocked_until:
            remaining_minutes = int((blocked_until - datetime.now()).total_seconds() / 60)
            return render_template('blocked.html', 
                                 blocked_until=blocked_until,
                                 remaining_minutes=remaining_minutes,
                                 ip_address=ip_address)
    
    attempt_count = session.get(f'attempt_count_{ip_address}', 0)
    return render_template('site_auth.html', attempt_count=attempt_count)

@app.route('/auth', methods=['POST'])
def authenticate():
    """Handle Gate 1 authentication with security tracking"""
    from datetime import datetime, timedelta
    password = request.form.get('site_password', '')
    ip_address = request.remote_addr
    
    # Get attempt count for this IP
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
    if password in ['SpikeMaz', 'RedAMC', 'PartnerAccess']:
        # Reset attempts on success
        session.pop(f'attempt_count_{ip_address}', None)
        session.pop(f'blocked_until_{ip_address}', None)
        session['gate1_passed'] = True
        session['site_authenticated'] = True
        session.permanent = True
        return jsonify({'success': True, 'redirect': '/secure-login'})
    else:
        # Increment attempt count
        attempt_count += 1
        session[f'attempt_count_{ip_address}'] = attempt_count
        
        # Handle security escalation
        if attempt_count >= 5:
            # Permanent blacklist after 5 attempts
            session[f'blackscreen_{ip_address}'] = True
            return jsonify({'success': False, 'redirect': '/', 'blackscreen': True})
        elif attempt_count == 4:
            # 30-minute block after 4 attempts
            blocked_until = datetime.now() + timedelta(minutes=30)
            session[f'blocked_until_{ip_address}'] = blocked_until.isoformat()
            return jsonify({'success': False, 'redirect': '/', 'blocked': True})
        else:
            # Show remaining attempts
            remaining = 4 - attempt_count
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
    
    # Get attempt count for this IP
    attempt_count = session.get(f'attempt_count_{ip_address}', 0)
    
    # Check if already blacklisted
    if session.get(f'blackscreen_{ip_address}'):
        return render_template('blackscreen.html', ip_address=ip_address)
    
    # Check if temporarily blocked
    blocked_until = session.get(f'blocked_until_{ip_address}')
    if blocked_until:
        if isinstance(blocked_until, str):
            blocked_until = datetime.fromisoformat(blocked_until)
        if datetime.now() < blocked_until:
            remaining_minutes = int((blocked_until - datetime.now()).total_seconds() / 60)
            return render_template('blocked.html', 
                                 blocked_until=blocked_until,
                                 remaining_minutes=remaining_minutes,
                                 ip_address=ip_address)
    
    # Check actual passwords
    if password in ['SpikeMaz', 'RedAMC', 'PartnerAccess']:
        # Reset attempts on success
        session.pop(f'attempt_count_{ip_address}', None)
        session.pop(f'blocked_until_{ip_address}', None)
        session['gate1_passed'] = True
        session['site_authenticated'] = True
        session.permanent = True
        return redirect(url_for('secure_login'))
    else:
        # Increment attempt count
        attempt_count += 1
        session[f'attempt_count_{ip_address}'] = attempt_count
        
        # Handle security escalation
        if attempt_count >= 5:
            # Permanent blacklist after 5 attempts
            session[f'blackscreen_{ip_address}'] = True
            return render_template('blackscreen.html', ip_address=ip_address)
        elif attempt_count == 4:
            # 30-minute block after 4 attempts
            blocked_until = datetime.now() + timedelta(minutes=30)
            session[f'blocked_until_{ip_address}'] = blocked_until.isoformat()
            remaining_minutes = 30
            return render_template('blocked.html', 
                                 blocked_until=blocked_until,
                                 remaining_minutes=remaining_minutes,
                                 ip_address=ip_address)
        else:
            # Show error with remaining attempts
            remaining = 4 - attempt_count
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
    app.run(debug=True, host='0.0.0.0', port=5000)