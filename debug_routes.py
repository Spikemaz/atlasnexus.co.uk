#!/usr/bin/env python3
"""Debug routes in the app"""
from app import app

print("\n" + "="*60)
print("REGISTERED ROUTES:")
print("="*60)

for rule in app.url_map.iter_rules():
    methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
    if methods:
        print(f"{rule.endpoint:20} {methods:8} {rule.rule}")

print("="*60)