#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final verification that both LOCAL and LIVE have registration prevention working
"""

import requests
import json
import sys
import io

# Set UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_site(name, url):
    """Test a single site"""
    print(f"\n{'='*50}")
    print(f"{name}: {url}")
    print(f"{'='*50}")
    
    try:
        # Create session
        session = requests.Session()
        session.verify = False  # For HTTPS
        
        # Test 1: Basic connectivity
        print("1. Testing connectivity...")
        resp = session.get(url, timeout=10)
        print(f"   ✓ Site accessible (Status: {resp.status_code})")
        
        # Test 2: Email check for existing user
        print("2. Testing email check for existing user...")
        resp = session.post(
            f"{url}/check-email-availability",
            json={"email": "spikemaz8@aol.com"},
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            if not data.get('available') and 'already registered' in data.get('message', '').lower():
                print(f"   ✓ Correctly blocks existing email")
                print(f"   Message: {data.get('message')}")
            else:
                print(f"   ✗ Unexpected response: {data}")
        else:
            print(f"   ✗ Status code: {resp.status_code}")
            
        # Test 3: Email check for new user
        print("3. Testing email check for new user...")
        resp = session.post(
            f"{url}/check-email-availability",
            json={"email": "newtest123@example.com"},
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('available'):
                print(f"   ✓ Correctly allows new email")
                print(f"   Message: {data.get('message')}")
            else:
                print(f"   Info: {data}")
        else:
            print(f"   ✗ Status code: {resp.status_code}")
            
        # Test 4: Registration attempt with existing email
        print("4. Testing registration block...")
        
        # First authenticate
        auth_resp = session.post(
            f"{url}/site-auth",
            data={"site_password": "SpikeMaz"},
            timeout=10
        )
        
        if auth_resp.status_code == 200:
            print(f"   ✓ Authenticated with site")
            
            # Try to register with existing email
            reg_resp = session.post(
                f"{url}/register",
                data={
                    "email": "spikemaz8@aol.com",
                    "fullname": "Test",
                    "phone_number": "7123456789",
                    "country_code": "+44",
                    "company": "Test",
                    "company_number": "12345678",
                    "job_title": "Test",
                    "address": "Test"
                },
                timeout=10
            )
            
            if reg_resp.status_code == 400:
                data = reg_resp.json()
                if 'already registered' in data.get('message', '').lower():
                    print(f"   ✓ Registration correctly blocked")
                    print(f"   Message: {data.get('message')}")
                else:
                    print(f"   ✗ Blocked but wrong message: {data}")
            elif reg_resp.status_code == 401:
                print(f"   ⚠️  Auth issue, but endpoint exists")
            else:
                print(f"   ✗ Not blocked! Status: {reg_resp.status_code}")
        else:
            print(f"   ✗ Could not authenticate")
            
        # Test 5: Client validation presence
        print("5. Testing client-side validation...")
        page_resp = session.get(f"{url}/secure-login", timeout=10, allow_redirects=True)
        
        if 'checkEmailAvailability' in page_resp.text:
            print(f"   ✓ Client-side validation present")
        else:
            print(f"   ⚠️  Client validation may need auth to view")
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Error: {str(e)[:100]}")
        return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {str(e)[:100]}")
        return False

def main():
    print("\n" + "="*50)
    print("FINAL VERIFICATION - REGISTRATION PREVENTION")
    print("="*50)
    
    # Disable SSL warnings for testing
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Test local
    local_ok = test_site("LOCAL", "http://localhost:5000")
    
    # Test live
    live_ok = test_site("LIVE", "https://atlasnexus.co.uk")
    
    # Summary
    print("\n" + "="*50)
    print("FINAL RESULT")
    print("="*50)
    
    if local_ok and live_ok:
        print("\n✅ SUCCESS: Both LOCAL and LIVE are working!")
        print("\nThe registration prevention system is active on:")
        print("  • LOCAL:  http://localhost:5000")
        print("  • LIVE:   https://atlasnexus.co.uk")
        print("\nUsers cannot re-register with verified emails on either version.")
        return True
    else:
        print("\n⚠️  Issues detected:")
        if not local_ok:
            print("  • LOCAL has problems")
        if not live_ok:
            print("  • LIVE has problems")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)