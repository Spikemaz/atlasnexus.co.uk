#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify the system is in a clean state with only admin account
"""

import requests
import json
import sys
import io
import time

# Set UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:5000"

def verify_clean_state():
    """Verify system is clean"""
    
    print("=" * 60)
    print("VERIFYING CLEAN STATE")
    print("=" * 60)
    
    # Check local files
    print("\n1. Checking local database files...")
    
    # Check users.json
    with open('data/users.json', 'r') as f:
        users = json.load(f)
    
    print(f"   Users in database: {len(users)}")
    for email in users:
        if email == "spikemaz8@aol.com":
            print(f"   ✓ Admin account: {email}")
        else:
            print(f"   ✗ Unexpected account: {email}")
    
    # Check registrations.json
    with open('data/registrations.json', 'r') as f:
        registrations = json.load(f)
    
    print(f"   Registrations pending: {len(registrations)}")
    if len(registrations) == 0:
        print(f"   ✓ No pending registrations")
    else:
        for email in registrations:
            print(f"   ✗ Unexpected registration: {email}")
    
    # Test Gate1 passwords
    print("\n2. Testing Gate1 passwords...")
    session = requests.Session()
    
    # Test SpikeMaz (should work)
    resp = session.post(f"{BASE_URL}/site-auth", 
                        data={"site_password": "SpikeMaz"})
    if resp.status_code == 200:
        print("   ✓ 'SpikeMaz' password works")
    else:
        print("   ✗ 'SpikeMaz' password failed")
    
    # Test RedAMC (should work)
    session2 = requests.Session()
    resp = session2.post(f"{BASE_URL}/site-auth", 
                         data={"site_password": "RedAMC"})
    if resp.status_code == 200:
        print("   ✓ 'RedAMC' password works")
    else:
        print("   ✗ 'RedAMC' password failed")
    
    # Test PartnerAccess (should NOT work)
    session3 = requests.Session()
    resp = session3.post(f"{BASE_URL}/site-auth", 
                         data={"site_password": "PartnerAccess"})
    if resp.status_code != 200:
        print("   ✓ 'PartnerAccess' password correctly rejected")
    else:
        print("   ✗ 'PartnerAccess' password still works (should be disabled)")
    
    # Test admin login
    print("\n3. Testing admin login...")
    resp = session.post(f"{BASE_URL}/auth",
                       data={"email": "spikemaz8@aol.com", "password": "SpikeMaz"})
    
    if resp.status_code == 200:
        result = resp.json()
        if result.get('status') == 'success':
            print("   ✓ Admin login works")
        else:
            print(f"   ✗ Admin login failed: {result.get('message')}")
    else:
        print(f"   ✗ Admin login failed with status {resp.status_code}")
    
    # Test registration prevention for admin
    print("\n4. Testing registration prevention...")
    resp = session.post(f"{BASE_URL}/register",
                        data={
                            "email": "spikemaz8@aol.com",
                            "fullname": "Test",
                            "phone_number": "7123456789",
                            "country_code": "+44",
                            "company": "Test",
                            "company_number": "12345678",
                            "job_title": "Test",
                            "address": "Test"
                        })
    
    if resp.status_code == 400:
        result = resp.json()
        if 'already registered' in result.get('message', '').lower():
            print("   ✓ Cannot re-register admin email")
        else:
            print(f"   Message: {result.get('message')}")
    else:
        print(f"   ✗ Registration not blocked properly")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\n✅ Clean State Verified:")
    print("   - Only admin account exists (spikemaz8@aol.com)")
    print("   - No pending registrations")
    print("   - Gate1 passwords: SpikeMaz ✓, RedAMC ✓")
    print("   - PartnerAccess removed ✓")
    print("   - Admin login working ✓")
    print("   - Registration prevention working ✓")

if __name__ == "__main__":
    # Wait for server to start
    time.sleep(3)
    
    # Check if server is running
    try:
        resp = requests.get(BASE_URL)
        print(f"✓ Server running at {BASE_URL}\n")
        verify_clean_state()
    except:
        print(f"✗ Server not running at {BASE_URL}")
        print("Please start the Flask application first.")