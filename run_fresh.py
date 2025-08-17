#!/usr/bin/env python3
"""
Fresh runner that ensures module reload
"""
import os
import sys

# Clear ALL cached modules
for key in list(sys.modules.keys()):
    if 'app' in key or 'flask' in key.lower():
        del sys.modules[key]

# Reimport Flask first
import flask

# Now import our app
from app_vercel import app

# Verify the route exists
print("\n" + "="*60)
print("VERIFYING ROUTES BEFORE STARTING:")
print("="*60)
verify_exists = False
for rule in app.url_map.iter_rules():
    if 'verify-access-code' in rule.rule:
        print(f"[OK] Found route: {rule.rule}")
        verify_exists = True
        break

if not verify_exists:
    print("[ERROR] verify-access-code route NOT found!")
    sys.exit(1)

if 'verify_access_code' not in app.view_functions:
    print("[ERROR] verify_access_code function NOT found!")
    sys.exit(1)

print("[OK] verify_access_code function exists")
print("="*60)
print("\nStarting server on http://localhost:5000")
print("Press Ctrl+C to stop\n")

# Run the app
app.run(host='0.0.0.0', port=5000, debug=False)