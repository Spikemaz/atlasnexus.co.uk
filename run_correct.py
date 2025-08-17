#!/usr/bin/env python3
"""Run the app using module import like the original working version"""
import sys
import os

# Clear cache
if 'app' in sys.modules:
    del sys.modules['app']

# Import app
from app import app

# Clear debug log
if os.path.exists('debug.log'):
    os.remove('debug.log')

print("\n" + "="*60)
print("ATLASNEXUS - RUNNING WITH MODULE IMPORT")
print("="*60)
print("Site Passwords: RedAMC, PartnerAccess")
print("URL: http://localhost:5000")
print("="*60 + "\n")

# Run
app.run(host='0.0.0.0', port=5000, debug=False)