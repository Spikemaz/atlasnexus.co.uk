#!/usr/bin/env python3
"""
Test script to verify security gate functionality
"""

import requests
import time

BASE_URL = "http://localhost:5000"

def test_security_gates():
    """Test the enhanced security gates"""
    session = requests.Session()
    
    print("Testing AtlasNexus Security Gates...")
    print("=" * 50)
    
    # Test 1: Access root without authentication
    print("\n1. Testing access without authentication...")
    response = session.get(BASE_URL)
    if "Security Gate 1" in response.text or "ATLAS" in response.text:
        print("✓ Security Gate 1 displayed correctly")
    else:
        print("✗ Security Gate 1 not displayed")
    
    # Test 2: Try incorrect password
    print("\n2. Testing incorrect password...")
    response = session.post(f"{BASE_URL}/site_auth", data={"site_password": "wrongpass"})
    if response.status_code == 200 or response.status_code == 403:
        print("✓ Incorrect password handled")
    
    # Test 3: Try correct password
    print("\n3. Testing correct password (RedAMC)...")
    response = session.post(f"{BASE_URL}/site_auth", data={"site_password": "RedAMC"})
    
    # Check if we're redirected to secure_login
    if response.status_code == 302:  # Redirect
        print("✓ Password accepted, redirecting...")
        
        # Follow redirect
        response = session.get(f"{BASE_URL}/secure_login")
        if "Security Gate 2" in response.text or "Login" in response.text or "financial" in response.text.lower():
            print("✓ Successfully reached Security Gate 2")
        else:
            print("✗ Security Gate 2 not displayed properly")
    else:
        print(f"✗ Unexpected response: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("Test complete!")

if __name__ == "__main__":
    test_security_gates()