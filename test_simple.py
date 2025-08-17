#!/usr/bin/env python3
"""Simple test to verify routing works"""
from flask import Flask, request, redirect, session
import sys

app = Flask(__name__)
app.secret_key = 'test_key_123'

@app.route('/')
def index():
    return '<form method="POST" action="/site-auth"><input name="site_password"><button>Submit</button></form>'

@app.route('/site-auth', methods=['POST'])
def site_auth():
    print(f"[SITE-AUTH] Route hit!", file=sys.stderr, flush=True)
    password = request.form.get('site_password', '')
    print(f"[SITE-AUTH] Password: {password}", file=sys.stderr, flush=True)
    
    if password == 'RedAMC':
        session['authenticated'] = True
        print(f"[SITE-AUTH] Redirecting to /login", file=sys.stderr, flush=True)
        return redirect('/login')
    
    return 'Wrong password'

@app.route('/login')
def login():
    print(f"[LOGIN] Session: {dict(session)}", file=sys.stderr, flush=True)
    if not session.get('authenticated'):
        print(f"[LOGIN] Not authenticated, redirecting to /", file=sys.stderr, flush=True)
        return redirect('/')
    return 'LOGIN PAGE - SUCCESS!'

if __name__ == '__main__':
    print("\n" + "="*50, file=sys.stderr)
    print("SIMPLE TEST SERVER", file=sys.stderr)
    print("="*50 + "\n", file=sys.stderr)
    app.run(host='0.0.0.0', port=5000, debug=False)