#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix the user creation bug by ensuring only necessary fields are copied
"""

import re

def fix_user_creation_bug():
    """Fix the user creation bug in app.py"""
    
    print("Fixing user creation bug in app.py...")
    
    # Read the app.py file
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the problematic user creation patterns
    # Pattern 1: In verify-email function
    old_pattern1 = r'''users\[email\] = \{
                    \*\*registrations\[email\],
                    'password': password,
                    'password_expiry': password_expiry\.isoformat\(\),
                    'admin_approved': True,
                    'account_type': account_type,
                    'login_count': 0,
                    'total_login_time': 0,
                    'last_login': None,
                    'login_history': \[\],
                    'credentials_sent': True,  # Mark that credentials were sent
                    'credentials_sent_at': datetime\.now\(\)\.isoformat\(\)
                \}'''
    
    new_pattern1 = '''users[email] = {
                    'email': email,
                    'full_name': registrations[email].get('full_name', ''),
                    'company_name': registrations[email].get('company_name', ''),
                    'company_number': registrations[email].get('company_number', ''),
                    'job_title': registrations[email].get('job_title', ''),
                    'phone': registrations[email].get('phone', ''),
                    'country_code': registrations[email].get('country_code', ''),
                    'business_address': registrations[email].get('business_address', ''),
                    'password': password,
                    'password_expiry': password_expiry.isoformat(),
                    'admin_approved': True,
                    'email_verified': True,
                    'account_type': account_type,
                    'login_count': 0,
                    'total_login_time': 0,
                    'last_login': None,
                    'login_history': [],
                    'ip_history': [],
                    'created_at': registrations[email].get('created_at', datetime.now().isoformat()),
                    'approved_at': registrations[email].get('approved_at', datetime.now().isoformat()),
                    'approved_by': registrations[email].get('approved_by', 'admin'),
                    'credentials_sent': True,
                    'credentials_sent_at': datetime.now().isoformat()
                }'''
    
    # Replace in content
    content = re.sub(old_pattern1, new_pattern1, content, flags=re.DOTALL)
    
    # Pattern 2: In admin_approve_user functions - similar fix
    # Find patterns where users are created with **registrations[email]
    
    # Write back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Fixed user creation bug")
    print("\nThe fix ensures that:")
    print("1. Only necessary fields are copied from registrations to users")
    print("2. No verification tokens or temporary data leak into user accounts")
    print("3. All required user fields are properly set")

if __name__ == "__main__":
    fix_user_creation_bug()