#!/usr/bin/env python3
"""
Local runner for AtlasNexus Production Version
This properly imports the app_vercel module to ensure routes work correctly
DO NOT run app_vercel.py directly!
"""
import os
import sys

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Clear any cached modules
for module in ['app', 'app_vercel']:
    if module in sys.modules:
        del sys.modules[module]

# Import the production app
from app_vercel import app, SITE_PASSWORD_INTERNAL, SITE_PASSWORD_EXTERNAL, ADMIN_EMAIL

print("\n" + "="*60)
print("ATLASNEXUS PRODUCTION SERVER (LOCAL)")
print("="*60)
print(f"\nSite Passwords:")
print(f"  Internal: {SITE_PASSWORD_INTERNAL}")
print(f"  External: {SITE_PASSWORD_EXTERNAL}")
print(f"\nAdmin: {ADMIN_EMAIL} / MarcusAdmin2024")
print(f"\nURL: http://localhost:5000")
print("\nNOTE: Press Ctrl+C to stop the server")
print("="*60 + "\n")

# Run the application
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )