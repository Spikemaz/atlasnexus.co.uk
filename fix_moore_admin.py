import cloud_database
import json

# Initialize database
db = cloud_database.CloudDatabase()

# Load all users
users = db.load_users()

# Fix moore2marcus@gmail.com if it exists
email = 'moore2marcus@gmail.com'

if email in users:
    print(f"Found user: {email}")
    print(f"Current account_type: {users[email].get('account_type')}")
    print(f"Current is_admin: {users[email].get('is_admin')}")
    
    # Fix the account
    users[email]['is_admin'] = False
    users[email]['account_type'] = 'external'  # Ensure it's set to external
    
    # Save the fix
    if db.save_user(email, users[email]):
        print(f"\n[FIXED] Set is_admin=False and account_type=external for {email}")
    else:
        print(f"\n[ERROR] Could not save changes for {email}")
else:
    print(f"User {email} not found in database")

# Also check and fix ALL users to ensure only spikemaz8@aol.com has admin access
print("\n" + "=" * 50)
print("Checking all users for incorrect admin access...")
print("-" * 50)

fixed_count = 0
for user_email, user_data in users.items():
    if user_email == 'spikemaz8@aol.com':
        # This is the only legitimate admin
        if not user_data.get('is_admin'):
            user_data['is_admin'] = True
            user_data['account_type'] = 'admin'
            db.save_user(user_email, user_data)
            print(f"[OK] Ensured admin access for {user_email}")
    else:
        # All other users should NOT have admin access
        if user_data.get('is_admin') or user_data.get('account_type') == 'admin':
            print(f"[WARNING] Found incorrect admin access for {user_email}")
            user_data['is_admin'] = False
            if user_data.get('account_type') == 'admin':
                user_data['account_type'] = 'external'  # Default to external
            db.save_user(user_email, user_data)
            fixed_count += 1
            print(f"   [FIXED] Removed admin access from {user_email}")

if fixed_count > 0:
    print(f"\n[SUCCESS] Fixed {fixed_count} users with incorrect admin access")
else:
    print(f"\n[SUCCESS] No users found with incorrect admin access")

print("\nAdmin access is now properly restricted to spikemaz8@aol.com only")