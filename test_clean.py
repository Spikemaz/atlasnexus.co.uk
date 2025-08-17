#!/usr/bin/env python3
"""Test the clean implementation"""
import requests
import time

session = requests.Session()
base = "http://localhost:5000"

print("\n" + "="*50)
print("TESTING ATLASNEXUS CLEAN IMPLEMENTATION")
print("="*50)

time.sleep(2)

print("\n[1] Accessing site...")
r = session.get(base)
print(f"    Status: {r.status_code}")
print(f"    Gate 1 displayed: {'site_password' in r.text}")

print("\n[2] Submitting password 'RedAMC'...")
r = session.post(f"{base}/site-auth", 
                 data={"site_password": "RedAMC"},
                 allow_redirects=False)
print(f"    Status: {r.status_code}")
if r.status_code == 302:
    location = r.headers.get('Location', '')
    print(f"    Redirects to: {location}")
    
    if 'login' in location or 'secure-login' in location:
        print("\n[3] Following to login page...")
        # Follow the actual redirect location
        r = session.get(f"{base}{location}")
        print(f"    Status: {r.status_code}")
        print(f"    Login page displayed: {'email' in r.text or 'Login' in r.text}")
        
        if r.status_code == 200:
            print("\n" + "="*50)
            print("SUCCESS! Flow works correctly:")
            print("- Gate 1 (password) ✓")
            print("- Gate 2 (login) ✓")
            print("="*50)
        else:
            print(f"\n[ERROR] Login page returned {r.status_code}")
    else:
        print(f"\n[ERROR] Wrong redirect: {location}")
else:
    print(f"\n[ERROR] Expected redirect, got {r.status_code}")