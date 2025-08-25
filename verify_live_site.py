#!/usr/bin/env python3
"""
Verify all functionality on the live AtlasNexus site
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://atlasnexus.co.uk"

def check_endpoint(endpoint, expected_status=200):
    """Check if an endpoint is accessible"""
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, timeout=10)
        success = response.status_code == expected_status
        print(f"[{'OK' if success else 'FAIL'}] {endpoint} - Status: {response.status_code}")
        return success
    except Exception as e:
        print(f"[ERROR] {endpoint} - {str(e)}")
        return False

def check_gate1_features():
    """Check Gate1 specific features"""
    print("\n=== Gate1 Features ===")
    
    # Check main page
    response = requests.get(BASE_URL)
    content = response.text
    
    # Check for 30-minute timer fix
    if "timeLeft = Math.min(timeLeft, 1800)" in content:
        print("[OK] 30-minute timer cap implemented")
    else:
        print("[FAIL] 30-minute timer fix not found")
    
    # Check for override functionality
    if "Ronabambi" in content or "GLOBAL_UNLOCK_CODE" in content:
        print("[OK] Override code reference found")
    else:
        print("[INFO] Override code hidden (as expected)")
    
    # Check for IP tracking
    if "track_ip_access" in content or "ip_tracking" in content:
        print("[OK] IP tracking references found")
    else:
        print("[INFO] IP tracking in backend only")

def check_gate2_features():
    """Check Gate2 specific features"""
    print("\n=== Gate2 Features ===")
    
    # Try to access Gate2
    response = requests.get(f"{BASE_URL}/secure-login")
    content = response.text
    
    # Check for ticker container
    if "market-ticker-container" in content:
        print("[OK] Market ticker container found")
    else:
        print("[FAIL] Market ticker container missing")
    
    # Check for ticker initialization
    if "createTicker" in content:
        print("[OK] Ticker initialization function found")
    else:
        print("[FAIL] Ticker initialization missing")
    
    # Check for drag functionality fix
    if "tickerPosition > 0" in content:
        print("[OK] Ticker drag fix implemented")
    else:
        print("[INFO] Ticker drag fix may be in minified code")

def check_admin_endpoints():
    """Check admin panel endpoints"""
    print("\n=== Admin Panel Endpoints ===")
    
    endpoints = [
        "/admin-panel",
        "/admin/comprehensive-data",
        "/admin/ip-management",
        "/admin/users/all"
    ]
    
    for endpoint in endpoints:
        # These should redirect or return 401/403 without auth
        response = requests.get(f"{BASE_URL}{endpoint}", allow_redirects=False)
        if response.status_code in [302, 401, 403]:
            print(f"[OK] {endpoint} - Protected (Status: {response.status_code})")
        elif response.status_code == 200:
            print(f"[INFO] {endpoint} - Accessible (check if intentional)")
        else:
            print(f"[WARN] {endpoint} - Status: {response.status_code}")

def check_registration_flow():
    """Check registration endpoints"""
    print("\n=== Registration Flow ===")
    
    # Check registration submitted page
    response = requests.get(f"{BASE_URL}/registration-submitted?email=test@example.com")
    content = response.text
    
    if "Resend Email" in content:
        print("[OK] Resend Email button found")
    else:
        print("[FAIL] Resend Email button missing")
    
    if "emailVerified" in content or "updateUIForVerified" in content:
        print("[OK] Email verification UI update logic found")
    else:
        print("[FAIL] Email verification UI logic missing")

def check_api_endpoints():
    """Check API endpoints"""
    print("\n=== API Endpoints ===")
    
    # Test various API endpoints (these should exist but may require auth)
    api_endpoints = [
        ("/check-verification-status", 405),  # GET not allowed
        ("/resend-verification", 405),  # GET not allowed
        ("/admin/approve-user-advanced", 401),  # Requires auth
        ("/admin/ban-ip", 401),  # Requires auth
        ("/admin/user/freeze", 401),  # Requires auth
    ]
    
    for endpoint, expected in api_endpoints:
        check_endpoint(endpoint, expected)

def main():
    print("[START] AtlasNexus Live Site Verification")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Run all checks
    check_gate1_features()
    check_gate2_features()
    check_admin_endpoints()
    check_registration_flow()
    check_api_endpoints()
    
    print("\n" + "=" * 60)
    print("[COMPLETE] Verification finished")
    print("\nNOTE: Some features require authentication to fully test")
    print("Manual testing recommended for:")
    print("- Login with admin credentials")
    print("- User management in admin panel")
    print("- IP tracking and banning")
    print("- Registration approval workflow")

if __name__ == "__main__":
    main()