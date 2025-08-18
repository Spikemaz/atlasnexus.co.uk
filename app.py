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
TESTING_MODE = True

@app.route('/')
def index():
    """Gate 1 - Site Authentication"""
    return render_template('site_auth.html')

@app.route('/auth', methods=['POST'])
def authenticate():
    """Handle Gate 1 authentication"""
    if TESTING_MODE:
        # Accept any input in testing mode
        session['gate1_passed'] = True
        session['site_authenticated'] = True
        session.permanent = True
        return jsonify({'success': True, 'redirect': '/secure-login'})

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
    return authenticate()

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