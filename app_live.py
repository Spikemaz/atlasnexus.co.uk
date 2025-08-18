"""
AtlasNexus - Local Testing Version
Only includes the 3 essential pages: /, /secure-login, /dashboard
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import timedelta
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.permanent_session_lifetime = timedelta(minutes=45)

# TESTING MODE - No passwords required for local development
TESTING_MODE = False

@app.route('/')
def index():
    """Gate 1 - Site Authentication"""
    return render_template('site_auth.html')

@app.route('/auth', methods=['POST'])
def authenticate():
    """Handle Gate 1 authentication"""
    password = request.form.get('site_password', '')
    
    if TESTING_MODE:
        # Accept any input in testing mode
        session['gate1_passed'] = True
        session['site_authenticated'] = True
        session.permanent = True
        return jsonify({'success': True, 'redirect': '/secure-login'})
    
    # Production mode - check actual passwords
    if password in ['SpikeMaz', 'RedAMC', 'PartnerAccess']:
        session['gate1_passed'] = True
        session['site_authenticated'] = True
        session.permanent = True
        return jsonify({'success': True, 'redirect': '/secure-login'})
    else:
        return jsonify({'success': False, 'message': 'Invalid password'})

@app.route('/secure-login')
def secure_login():
    """Gate 2 - Secure Login with Live Ticker"""
    if TESTING_MODE:
        session['gate1_passed'] = True
        session['site_authenticated'] = True
    elif not session.get('gate1_passed'):
        return redirect(url_for('index'))
    
    return render_template('secure_login.html')

@app.route('/secure-login-submit', methods=['POST'])
def secure_login_submit():
    """Handle Gate 2 login submission"""
    if TESTING_MODE:
        session['authenticated'] = True
        session['username'] = 'testuser'
        session.permanent = True
        return redirect(url_for('dashboard'))
    
    # Production mode - for now just authenticate (you can add real login later)
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    
    # Simple authentication for production
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
    if TESTING_MODE:
        if not session.get('authenticated'):
            session['authenticated'] = True
            session['username'] = 'testuser'
    elif not session.get('authenticated'):
        return redirect(url_for('index'))
    
    return render_template('dashboard.html')

@app.route('/site-auth', methods=['POST'])
def site_auth():
    """Alternative endpoint for Gate 1"""
    password = request.form.get('site_password', '')
    
    if TESTING_MODE:
        session['gate1_passed'] = True
        session['site_authenticated'] = True
        session.permanent = True
        return redirect(url_for('secure_login'))
    
    # Production mode - check actual passwords
    if password in ['SpikeMaz', 'RedAMC', 'PartnerAccess']:
        session['gate1_passed'] = True
        session['site_authenticated'] = True
        session.permanent = True
        return redirect(url_for('secure_login'))
    else:
        # Return back to login with error
        return render_template('site_auth.html', error='Invalid password')

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
    app.run(debug=False, host='0.0.0.0', port=5000)