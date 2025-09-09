"""
Register a fresh test account
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://atlasnexus.co.uk"
SITE_PASSWORD = "RedAMC"

# Fresh test account with timestamp
timestamp = datetime.now().strftime("%Y%m%d%H%M")
TEST_ACCOUNT = {
    "email": f"test.{timestamp}@example.com",
    "username": f"TestUser{timestamp}",
    "full_name": "Test User Account",
    "company": "Test Company Ltd",
    "phone": "+44 7700 900000",
    "password": "TestPass2025!",
    "account_type": "external"
}

def register_fresh_account():
    """Register a fresh test account"""
    session = requests.Session()
    
    print("=" * 60)
    print("FRESH ACCOUNT REGISTRATION")
    print("=" * 60)
    
    # Step 1: Site auth
    print("\n[1] Site Authentication...")
    auth_data = {"site_password": SITE_PASSWORD}
    response = session.post(f"{BASE_URL}/site-auth", data=auth_data)
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            print("[OK] Site authentication successful")
    
    # Step 2: Navigate to registration
    print("\n[2] Accessing registration page...")
    response = session.get(f"{BASE_URL}/register")
    if response.status_code == 200:
        print("[OK] Registration page loaded")
    
    # Step 3: Register account
    print("\n[3] Registering new account...")
    print(f"    Email: {TEST_ACCOUNT['email']}")
    print(f"    Username: {TEST_ACCOUNT['username']}")
    print(f"    Company: {TEST_ACCOUNT['company']}")
    print(f"    Password: {TEST_ACCOUNT['password']}")
    
    response = session.post(f"{BASE_URL}/register", data=TEST_ACCOUNT)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            print("\n[OK] Registration successful!")
            print(f"    Message: {result.get('message')}")
            
            # Save credentials for later use
            creds = {
                "email": TEST_ACCOUNT['email'],
                "password": TEST_ACCOUNT['password'],
                "username": TEST_ACCOUNT['username'],
                "registered_at": datetime.now().isoformat()
            }
            
            with open('latest_test_account.json', 'w') as f:
                json.dump(creds, f, indent=2)
            
            print("\n" + "=" * 60)
            print("NEXT STEPS:")
            print("1. Go to admin panel at:")
            print("   https://atlasnexus.co.uk/admin-panel")
            print("2. Find this account in registrations:")
            print(f"   {TEST_ACCOUNT['email']}")
            print("3. Click 'Approve' and 'Verify'")
            print("4. Run: python test_approved_login.py")
            print("=" * 60)
            
            return True
        else:
            print(f"[!] Registration failed: {result.get('message')}")
    else:
        print(f"[X] Registration request failed: {response.status_code}")
        try:
            error = response.json()
            print(f"    Error: {error.get('message')}")
        except:
            print(f"    Response: {response.text[:200]}")
    
    return False

if __name__ == "__main__":
    register_fresh_account()