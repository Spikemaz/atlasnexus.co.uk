#!/usr/bin/env python3
"""Test the full flow"""
import requests

session = requests.Session()
base = "http://localhost:5000"

print("\n[1] GET / (Site Auth page)")
r1 = session.get(base)
print(f"    Status: {r1.status_code}")
print(f"    Password form present: {'site_password' in r1.text}")

print("\n[2] POST /site-auth with RedAMC")
r2 = session.post(f"{base}/site-auth", data={"site_password": "RedAMC"}, allow_redirects=False)
print(f"    Status: {r2.status_code}")
print(f"    Location: {r2.headers.get('Location', 'No redirect')}")
print(f"    Session cookie: {session.cookies.get('session', 'None')[:50]}...")

print("\n[3] GET /secure-login (following redirect)")
r3 = session.get(f"{base}/secure-login", allow_redirects=False)
print(f"    Status: {r3.status_code}")

if r3.status_code == 302:
    print(f"    Redirected to: {r3.headers.get('Location')}")
    print("    [ERROR] Being redirected away from login page!")
elif r3.status_code == 200:
    print(f"    Page loaded successfully")
    if 'verify_access_code' in r3.text:
        print("    [SUCCESS] Login page contains verify_access_code reference")
    else:
        print("    [OK] Login page loaded without verify_access_code issues")
else:
    print(f"    [ERROR] Unexpected status: {r3.status_code}")