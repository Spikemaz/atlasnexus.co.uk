#!/usr/bin/env python3
"""Test that verify_access_code route exists"""
from app_vercel import app

print("\nChecking routes in app_vercel:")
print("-" * 40)

for rule in app.url_map.iter_rules():
    if 'verify' in rule.rule or 'access' in rule.rule:
        methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
        print(f"{rule.rule:30} [{methods:8}] -> {rule.endpoint}")

print("\nChecking if verify_access_code exists:")
if 'verify_access_code' in app.view_functions:
    print("[OK] verify_access_code function exists")
else:
    print("[ERROR] verify_access_code function NOT found")
    print("\nAvailable endpoints:")
    for name in sorted(app.view_functions.keys()):
        if 'verify' in name or 'access' in name:
            print(f"  - {name}")