#!/usr/bin/env python3
"""
Test script to verify new hyphenated URL structure
"""

import requests
import time

BASE_URL = "http://localhost:5000"

def test_new_urls():
    """Test the new hyphenated URL structure"""
    session = requests.Session()
    
    print("Testing New AtlasNexus URL Structure...")
    print("=" * 50)
    
    # Test 1: Root URL
    print("\n1. Testing root URL (/)...")
    response = session.get(BASE_URL)
    print(f"   Status: {response.status_code}")
    if "ATLAS" in response.text or "Security Gate" in response.text:
        print("   ✓ Security Gate 1 accessible")
    
    # Test 2: Site auth endpoint
    print("\n2. Testing /site-auth endpoint...")
    response = session.post(f"{BASE_URL}/site-auth", data={"site_password": "RedAMC"})
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:  # Redirect expected
        print("   ✓ Site auth endpoint working")
    
    # Test 3: Secure login page
    print("\n3. Testing /secure-login...")
    response = session.get(f"{BASE_URL}/secure-login")
    print(f"   Status: {response.status_code}")
    
    # Test 4: API endpoints
    print("\n4. Testing API endpoints...")
    api_endpoints = [
        "/api/security-incidents",
        "/api/log-password-attempt"
    ]
    
    for endpoint in api_endpoints:
        try:
            response = session.get(BASE_URL + endpoint)
            print(f"   {endpoint}: {response.status_code}")
        except:
            print(f"   {endpoint}: Failed to connect")
    
    print("\n" + "=" * 50)
    print("URL structure test complete!")
    
    # Test authenticated routes
    print("\nAuthenticated routes (will redirect to login):")
    auth_routes = [
        "/dashboard",
        "/market-updates", 
        "/settings",
        "/account",
        "/admin-console"
    ]
    
    for route in auth_routes:
        response = session.get(BASE_URL + route)
        print(f"   {route}: {response.status_code}")

if __name__ == "__main__":
    # Wait a moment for server to start
    time.sleep(2)
    test_new_urls()