"""
Direct fix for test account - move from registrations to users
"""
import json
import os
from datetime import datetime

def fix_account():
    """Directly fix the test account in local JSON files"""
    email = "claude.test.2025@example.com"
    
    print("DIRECT ACCOUNT FIX")
    print("=" * 50)
    
    # Load registrations
    reg_file = os.path.join('data', 'registrations.json')
    users_file = os.path.join('data', 'users.json')
    
    # Read registrations
    try:
        with open(reg_file, 'r') as f:
            registrations = json.load(f)
    except:
        registrations = {}
    
    # Read users
    try:
        with open(users_file, 'r') as f:
            users = json.load(f)
    except:
        users = {}
    
    print(f"\n1. Checking registration for {email}...")
    
    if email not in registrations:
        print("   [!] Not found in registrations")
        
        # Check if already in users
        if email in users:
            print("   [OK] Already in users!")
            print(f"   Email verified: {users[email].get('email_verified')}")
            print(f"   Admin approved: {users[email].get('admin_approved')}")
            
            # Fix flags if needed
            if not users[email].get('email_verified') or not users[email].get('admin_approved'):
                print("\n2. Fixing user flags...")
                users[email]['email_verified'] = True
                users[email]['admin_approved'] = True
                users[email]['account_type'] = 'external'
                
                # Save users
                with open(users_file, 'w') as f:
                    json.dump(users, f, indent=2)
                print("   [OK] User flags updated")
        else:
            print("   [!] Account not found anywhere!")
        return
    
    print("   [OK] Found in registrations")
    reg_data = registrations[email]
    
    print("\n2. Creating user account...")
    
    # Create user data from registration
    user_data = {
        'email': email,
        'username': reg_data.get('username', 'ClaudeTest2025'),
        'full_name': reg_data.get('full_name', 'Claude AI Test User'),
        'company': reg_data.get('company', 'Anthropic Test Corp'),
        'phone': reg_data.get('phone', ''),
        'password': 'TestPassword123!',  # Set the password directly
        'account_type': 'external',
        'email_verified': True,
        'admin_approved': True,
        'created_at': reg_data.get('created_at', datetime.now().isoformat()),
        'approved_at': datetime.now().isoformat(),
        'approved_by': 'direct_fix',
        'login_count': 0,
        'last_login': None,
        'is_admin': False
    }
    
    # Save to users
    users[email] = user_data
    
    # Write users file
    os.makedirs('data', exist_ok=True)
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=2)
    
    print("   [OK] User account created")
    
    # Delete from registrations
    print("\n3. Removing from registrations...")
    del registrations[email]
    
    # Write registrations file
    with open(reg_file, 'w') as f:
        json.dump(registrations, f, indent=2)
    
    print("   [OK] Removed from registrations")
    
    print("\n" + "=" * 50)
    print("SUCCESS!")
    print(f"Account {email} is now ready to login")
    print(f"Password: TestPassword123!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    fix_account()