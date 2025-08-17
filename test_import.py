#!/usr/bin/env python3
"""Test what Flask is actually loading"""
import sys
import os

# Clear any cached modules
if 'app' in sys.modules:
    del sys.modules['app']
if 'app_vercel' in sys.modules:
    del sys.modules['app_vercel']

# Import and check
from app import app

print("\n" + "="*60)
print("MODULE CHECK")
print("="*60)
print(f"App module file: {app.__module__}")
print(f"App name: {app.name}")

# Check routes
print("\nRegistered routes:")
for rule in app.url_map.iter_rules():
    methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
    if methods and 'site-auth' in rule.rule:
        print(f"  {rule.rule} [{methods}] -> {rule.endpoint}")

# Test the actual function
print("\nChecking site_auth function:")
site_auth = app.view_functions.get('site_auth')
if site_auth:
    print(f"  Function: {site_auth}")
    print(f"  Module: {site_auth.__module__}")
    import inspect
    source = inspect.getsource(site_auth)
    # Check if it has our debug code
    if 'debug.log' in source:
        print("  [OK] Has debug.log code (CORRECT)")
    else:
        print("  [ERROR] Missing debug.log code (WRONG)")
else:
    print("  [ERROR] site_auth function not found!")

print("="*60)