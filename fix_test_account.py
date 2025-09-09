"""
Fix the test account by properly moving it from registrations to users
"""
import os
from datetime import datetime
from cloud_database import CloudDatabase

# Initialize database connection
db = CloudDatabase()

def fix_test_account():
    """Move test account from registrations to users"""
    email = "claude.test.2025@example.com"
    
    print("FIX TEST ACCOUNT")
    print("=" * 50)
    
    if not db.connected:
        print("[ERROR] Database not connected!")
        return False
    
    print(f"\n1. Checking registration for {email}...")
    
    # Load registrations
    registrations = db.load_registrations()
    
    if email not in registrations:
        print("   [!] Not found in registrations")
        
        # Check if already in users
        users = db.load_users()
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
                db.save_user(email, users[email])
                print("   [OK] User flags updated")
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
        'approved_by': 'fix_script',
        'login_count': 0,
        'last_login': None,
        'is_admin': False
    }
    
    # Save to users
    success = db.save_user(email, user_data)
    
    if success:
        print("   [OK] User account created")
        
        # Delete from registrations
        print("\n3. Removing from registrations...")
        del_success = db.delete_registration(email)
        if del_success:
            print("   [OK] Removed from registrations")
        else:
            print("   [!] Could not remove from registrations")
        
        print("\n" + "=" * 50)
        print("SUCCESS!")
        print(f"Account {email} is now ready to login")
        print(f"Password: TestPassword123!")
        print("=" * 50)
        
        return True
    else:
        print("   [ERROR] Failed to create user account")
        return False

if __name__ == "__main__":
    fix_test_account()