#!/usr/bin/env python3
"""
Local runner for AtlasNexus
This properly imports the app module to ensure routes work correctly
"""
import os
import sys

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Clear any cached modules
for module in ['app', 'app_vercel']:
    if module in sys.modules:
        del sys.modules[module]

# Import the app
from app import app, SITE_PASSWORDS, ADMIN_EMAIL, ADMIN_PASSWORD

# Clear debug log
if os.path.exists('debug.log'):
    os.remove('debug.log')

print("\n" + "="*60)
print("ATLASNEXUS SECURITIZATION PLATFORM")
print("="*60)
print(f"\nSite Passwords: {', '.join(SITE_PASSWORDS.keys())}")
print(f"Admin Login: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
print(f"URL: http://localhost:5000")
print("\nNOTE: Press Ctrl+C to stop the server")
print("="*60 + "\n")

# Run the application
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )