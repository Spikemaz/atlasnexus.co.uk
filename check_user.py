import cloud_database
import json

# Initialize database
db = cloud_database.CloudDatabase()

# Load all users
users = db.load_users()

# Check for moore2marcus@gmail.com
email = 'moore2marcus@gmail.com'

if email in users:
    user_data = users[email]
    print(f"\nUser found: {email}")
    print("-" * 50)
    for key, value in user_data.items():
        print(f"{key}: {value}")
    
    # Check specifically for admin-related fields
    print("\n" + "=" * 50)
    print("ADMIN STATUS CHECK:")
    print(f"account_type: {user_data.get('account_type', 'NOT SET')}")
    print(f"is_admin: {user_data.get('is_admin', False)}")
    print(f"admin_approved: {user_data.get('admin_approved', False)}")
    
    # Check if this user should NOT have admin access
    if user_data.get('account_type') == 'admin' or user_data.get('is_admin'):
        print("\n⚠️  WARNING: This external user has admin privileges!")
        print("This is a critical security issue that needs immediate fixing!")
else:
    print(f"\nUser {email} not found in database")

# Also check all users with admin access
print("\n" + "=" * 50)
print("ALL USERS WITH ADMIN ACCESS:")
print("-" * 50)
admin_count = 0
for user_email, user_data in users.items():
    if user_data.get('account_type') == 'admin' or user_data.get('is_admin'):
        admin_count += 1
        print(f"{admin_count}. {user_email}")
        print(f"   - account_type: {user_data.get('account_type')}")
        print(f"   - is_admin: {user_data.get('is_admin')}")