import cloud_database
import json

# Initialize database
db = cloud_database.CloudDatabase()

# Load all users
users = db.load_users()

print("=" * 60)
print("FIXING ACCOUNT TYPES AND ADMIN ACCESS")
print("=" * 60)

# Fix specific accounts
fixes_needed = {
    'spi66666recovery@gmail.com': {
        'account_type': 'internal',
        'is_admin': False
    },
    'moore2marcus@gmail.com': {
        'account_type': 'external', 
        'is_admin': False
    },
    'spikemaz8@aol.com': {
        'account_type': 'admin',
        'is_admin': True
    }
}

for email, correct_settings in fixes_needed.items():
    if email in users:
        print(f"\nChecking {email}:")
        print(f"  Current: account_type={users[email].get('account_type')}, is_admin={users[email].get('is_admin')}")
        
        # Fix the account
        users[email]['account_type'] = correct_settings['account_type']
        users[email]['is_admin'] = correct_settings['is_admin']
        
        # Save the fix
        if db.save_user(email, users[email]):
            print(f"  [FIXED] Set account_type={correct_settings['account_type']}, is_admin={correct_settings['is_admin']}")
        else:
            print(f"  [ERROR] Could not save changes")
    else:
        print(f"\n{email} not found in database")

# Check all other users to ensure proper settings
print("\n" + "=" * 60)
print("VERIFYING ALL USER ACCOUNTS")
print("=" * 60)

for email, user_data in users.items():
    if email not in fixes_needed:
        # Ensure non-admin users don't have admin access
        if user_data.get('is_admin') and user_data.get('account_type') != 'admin':
            print(f"\n[WARNING] {email} has is_admin=True but account_type={user_data.get('account_type')}")
            user_data['is_admin'] = False
            db.save_user(email, user_data)
            print(f"  [FIXED] Set is_admin=False")

# Display final summary
print("\n" + "=" * 60)
print("FINAL ACCOUNT SUMMARY")
print("=" * 60)

admin_count = 0
internal_count = 0
external_count = 0

for email, user_data in db.load_users().items():
    account_type = user_data.get('account_type', 'external')
    is_admin = user_data.get('is_admin', False)
    
    if account_type == 'admin' and is_admin:
        admin_count += 1
        print(f"[ADMIN] {email}")
    elif account_type == 'internal':
        internal_count += 1
        print(f"[INTERNAL] {email}")
    elif account_type == 'external':
        external_count += 1
        print(f"[EXTERNAL] {email}")
    else:
        print(f"[UNKNOWN] {email} - account_type={account_type}, is_admin={is_admin}")

print(f"\nTotal Admins: {admin_count}")
print(f"Total Internal: {internal_count}")
print(f"Total External: {external_count}")
print("\nAccount types have been properly configured.")