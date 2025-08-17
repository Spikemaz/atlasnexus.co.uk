#!/usr/bin/env python3
"""Direct test of the Flask app"""
from app import app
from flask import Flask
import os

# Clear debug log
if os.path.exists('debug.log'):
    os.remove('debug.log')

print("\nTesting Flask app directly...")

# Use Flask test client
with app.test_client() as client:
    # Test GET /
    print("\n[1] GET /")
    response = client.get('/')
    print(f"    Status: {response.status_code}")
    
    # Test POST /site-auth
    print("\n[2] POST /site-auth with RedAMC")
    response = client.post('/site-auth', data={'site_password': 'RedAMC'}, follow_redirects=False)
    print(f"    Status: {response.status_code}")
    print(f"    Location: {response.headers.get('Location', 'No redirect')}")
    
    # Check if debug.log was created
    if os.path.exists('debug.log'):
        print("\n[3] Debug log contents:")
        with open('debug.log', 'r') as f:
            for line in f:
                print(f"    {line.strip()}")
    else:
        print("\n[3] No debug.log created - route not executing!")