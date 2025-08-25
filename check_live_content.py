#!/usr/bin/env python3
"""
Check exact content being served on live site
"""

import requests

def check_gate1_timer():
    """Check if Gate1 has the timer fix"""
    print("\n=== Checking Gate1 Timer Fix ===")
    response = requests.get("https://atlasnexus.co.uk/")
    content = response.text
    
    # Look for the specific timer fix
    if "timeLeft = Math.min(timeLeft, 1800)" in content:
        print("[OK] Timer fix found in live site")
    else:
        # Check for the original timer code
        if "remaining_seconds|default(1800)" in content:
            print("[INFO] Template variable for timer found")
        else:
            print("[FAIL] Timer code not found")
        
        # Check what timer code exists
        if "let timeLeft" in content:
            # Extract the timer section
            start = content.find("let timeLeft")
            end = content.find("updateCountdown", start)
            if start > 0 and end > 0:
                timer_section = content[start:end]
                print("\nTimer code found:")
                print(timer_section[:200])  # First 200 chars

def check_gate2_ticker():
    """Check if Gate2 has the ticker"""
    print("\n=== Checking Gate2 Ticker ===")
    
    # First need to authenticate to Gate1
    session = requests.Session()
    
    # Try to get Gate2
    response = session.get("https://atlasnexus.co.uk/secure-login")
    content = response.text
    
    # Check for ticker elements
    ticker_found = False
    
    if "market-ticker-container" in content:
        print("[OK] Ticker container found")
        ticker_found = True
    else:
        print("[FAIL] Ticker container not in HTML")
    
    if "createTicker" in content:
        print("[OK] CreateTicker function found")
        ticker_found = True
    else:
        print("[FAIL] CreateTicker function not found")
    
    if "marketTicker" in content:
        print("[OK] Market ticker element reference found")
        ticker_found = True
    
    if not ticker_found:
        # Check if we're redirected to Gate1
        if "Site Authentication Required" in content:
            print("[INFO] Redirected to Gate1 - need authentication")
        else:
            print("[WARN] Unexpected content on Gate2")

def check_admin_panel():
    """Check admin panel features"""
    print("\n=== Checking Admin Panel ===")
    
    session = requests.Session()
    response = session.get("https://atlasnexus.co.uk/admin-panel", allow_redirects=True)
    
    if response.status_code == 200:
        content = response.text
        
        # Check for admin panel features
        features = {
            "updateUsersTable": "Users table update function",
            "freezeUser": "Freeze user function",
            "unfreezeUser": "Unfreeze user function",
            "editUserAccount": "Edit user account function",
            "Online/Offline": "Online/Offline display",
            "saveAccountType": "Save account type function"
        }
        
        for feature, description in features.items():
            if feature in content:
                print(f"[OK] {description} found")
            else:
                print(f"[FAIL] {description} missing")
    else:
        print(f"[INFO] Admin panel returned status {response.status_code}")

def check_ip_tracking():
    """Check if IP tracking functions exist"""
    print("\n=== Checking IP Tracking ===")
    
    # Check if IP ban endpoint exists
    response = requests.post(
        "https://atlasnexus.co.uk/admin/ban-ip",
        json={"ip": "127.0.0.1"},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 401:
        print("[OK] IP ban endpoint exists (requires auth)")
    elif response.status_code == 403:
        print("[OK] IP ban endpoint protected")
    elif response.status_code == 405:
        print("[WARN] IP ban endpoint may not accept POST")
    else:
        print(f"[INFO] IP ban endpoint returned: {response.status_code}")

def main():
    print("[START] Live Content Verification")
    print("=" * 60)
    
    check_gate1_timer()
    check_gate2_ticker()
    check_admin_panel()
    check_ip_tracking()
    
    print("\n" + "=" * 60)
    print("[COMPLETE] Content check finished")
    print("\nRECOMMENDATION:")
    print("If features are missing, check:")
    print("1. Vercel deployment logs")
    print("2. Environment variables on Vercel")
    print("3. Build output on Vercel dashboard")

if __name__ == "__main__":
    main()