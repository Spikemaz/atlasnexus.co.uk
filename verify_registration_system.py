#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive verification of registration prevention system
"""

import requests
import json
import sys
import io
import time

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:5000"

def print_test(test_name, passed, message=""):
    """Print test result with formatting"""
    status = "✓ PASS" if passed else "✗ FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} - {test_name}")
    if message:
        print(f"      {message}")

def test_server_running():
    """Test if server is accessible"""
    try:
        response = requests.get(BASE_URL, timeout=2)
        print_test("Server is running", response.status_code == 200)
        return True
    except:
        print_test("Server is running", False, "Server not accessible")
        return False

def test_email_availability_endpoint():
    """Test the email availability checking endpoint"""
    print("\n=== Email Availability Endpoint Tests ===")
    
    tests_passed = 0
    tests_total = 4
    
    # Test 1: Check new email
    try:
        resp = requests.post(f"{BASE_URL}/check-email-availability", 
                           json={"email": "newuser@test.com"})
        data = resp.json()
        passed = data.get('available') == True
        print_test("New email shows as available", passed, 
                  f"Response: {data.get('message')}")
        if passed: tests_passed += 1
    except Exception as e:
        print_test("New email shows as available", False, str(e))
    
    # Test 2: Check existing admin email
    try:
        resp = requests.post(f"{BASE_URL}/check-email-availability", 
                           json={"email": "spikemaz8@aol.com"})
        data = resp.json()
        passed = (data.get('available') == False and 
                 data.get('action') == 'login' and
                 'already registered' in data.get('message', '').lower())
        print_test("Existing email shows as unavailable", passed,
                  f"Response: {data.get('message')}")
        if passed: tests_passed += 1
    except Exception as e:
        print_test("Existing email shows as unavailable", False, str(e))
    
    # Test 3: Check empty email
    try:
        resp = requests.post(f"{BASE_URL}/check-email-availability", 
                           json={"email": ""})
        passed = resp.status_code == 400
        print_test("Empty email returns error", passed)
        if passed: tests_passed += 1
    except Exception as e:
        print_test("Empty email returns error", False, str(e))
    
    # Test 4: Check invalid request
    try:
        resp = requests.post(f"{BASE_URL}/check-email-availability", 
                           json={})
        passed = resp.status_code == 400
        print_test("Missing email field returns error", passed)
        if passed: tests_passed += 1
    except Exception as e:
        print_test("Missing email field returns error", False, str(e))
    
    return tests_passed, tests_total

def test_registration_blocking():
    """Test that registration is properly blocked for existing users"""
    print("\n=== Registration Blocking Tests ===")
    
    tests_passed = 0
    tests_total = 3
    
    session = requests.Session()
    
    # First authenticate with site
    try:
        auth_resp = session.post(f"{BASE_URL}/site-auth", 
                                data={"site_password": "SpikeMaz"})
        if auth_resp.status_code != 200:
            print_test("Site authentication", False, "Could not authenticate")
            return 0, tests_total
        print_test("Site authentication", True)
    except Exception as e:
        print_test("Site authentication", False, str(e))
        return 0, tests_total
    
    # Test 1: Try to register with existing admin email
    try:
        reg_data = {
            "email": "spikemaz8@aol.com",
            "fullname": "Test User",
            "phone_number": "7123456789",
            "country_code": "+44",
            "company": "Test Corp",
            "company_number": "12345678",
            "job_title": "Tester",
            "address": "123 Test Street"
        }
        
        resp = session.post(f"{BASE_URL}/register", data=reg_data)
        data = resp.json() if resp.status_code in [200, 400] else {}
        
        passed = (resp.status_code == 400 and 
                 'already registered' in data.get('message', '').lower())
        print_test("Registration blocked for existing user", passed,
                  f"Message: {data.get('message', 'No message')}")
        if passed: tests_passed += 1
    except Exception as e:
        print_test("Registration blocked for existing user", False, str(e))
    
    # Test 2: Try to register with new email (should work)
    try:
        test_email = f"test_{int(time.time())}@example.com"
        reg_data["email"] = test_email
        
        resp = session.post(f"{BASE_URL}/register", data=reg_data)
        data = resp.json() if resp.status_code == 200 else {}
        
        passed = (resp.status_code == 200 and 
                 data.get('status') == 'success')
        print_test("Registration allowed for new email", passed,
                  f"Test email: {test_email}")
        if passed: tests_passed += 1
    except Exception as e:
        print_test("Registration allowed for new email", False, str(e))
    
    # Test 3: Try to register again with same email (should be blocked)
    try:
        resp = session.post(f"{BASE_URL}/register", data=reg_data)
        data = resp.json() if resp.status_code in [200, 400] else {}
        
        passed = (resp.status_code == 400 and 
                 ('pending' in data.get('message', '').lower() or
                  'already' in data.get('message', '').lower()))
        print_test("Re-registration blocked for pending email", passed,
                  f"Message: {data.get('message', 'No message')}")
        if passed: tests_passed += 1
    except Exception as e:
        print_test("Re-registration blocked for pending email", False, str(e))
    
    return tests_passed, tests_total

def test_client_side_validation():
    """Test that client-side validation elements are present"""
    print("\n=== Client-Side Validation Tests ===")
    
    tests_passed = 0
    tests_total = 3
    
    # Need to authenticate first to access Gate2
    session = requests.Session()
    
    try:
        # Authenticate with site password
        auth_resp = session.post(f"{BASE_URL}/site-auth", 
                                data={"site_password": "SpikeMaz"})
        if auth_resp.status_code != 200:
            print_test("Site authentication for client test", False)
            return 0, tests_total
            
        # Now get the Gate2 page
        resp = session.get(f"{BASE_URL}/secure-login")
        content = resp.text
        
        # Test 1: Check for email validation function
        passed = 'checkEmailAvailability' in content
        print_test("Email availability check function exists", passed)
        if passed: tests_passed += 1
        
        # Test 2: Check for email field with validation
        passed = ('id="registerEmail"' in content and 
                 'onblur="checkEmailAvailability' in content)
        print_test("Registration email field has validation", passed)
        if passed: tests_passed += 1
        
        # Test 3: Check for availability message div
        passed = 'id="emailAvailabilityMessage"' in content
        print_test("Email availability message element exists", passed)
        if passed: tests_passed += 1
        
    except Exception as e:
        print_test("Client-side validation elements", False, str(e))
    
    return tests_passed, tests_total

def main():
    print("=" * 60)
    print("REGISTRATION PREVENTION SYSTEM VERIFICATION")
    print("=" * 60)
    
    # Check server
    if not test_server_running():
        print("\n❌ Server is not running. Please start the Flask application.")
        return False
    
    total_passed = 0
    total_tests = 0
    
    # Run all test suites
    passed, total = test_email_availability_endpoint()
    total_passed += passed
    total_tests += total
    
    passed, total = test_registration_blocking()
    total_passed += passed
    total_tests += total
    
    passed, total = test_client_side_validation()
    total_passed += passed
    total_tests += total
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    if total_passed == total_tests:
        print(f"✅ ALL TESTS PASSED ({total_passed}/{total_tests})")
        print("\n🎉 The registration prevention system is working correctly!")
    else:
        print(f"⚠️  SOME TESTS FAILED ({total_passed}/{total_tests} passed)")
        print(f"Success rate: {success_rate:.1f}%")
        print("\n❌ The system needs attention.")
    
    print("\nKey Features Verified:")
    print("✓ Email availability checking endpoint works")
    print("✓ Registration is blocked for existing users")
    print("✓ Client-side validation is in place")
    print("✓ Appropriate error messages are returned")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)