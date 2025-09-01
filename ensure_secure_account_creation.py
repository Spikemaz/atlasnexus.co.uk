"""
Script to check all user creation points in app.py to ensure they properly set is_admin
"""

import re

# Read the app.py file
with open('app.py', 'r') as f:
    content = f.read()

# Find all places where users are created (users[email] = {)
pattern = r'users\[.*?\] = \{[^}]+\}'
matches = re.findall(pattern, content, re.DOTALL)

print("=" * 60)
print("CHECKING ALL USER CREATION POINTS")
print("=" * 60)

issues_found = []
for i, match in enumerate(matches, 1):
    print(f"\n--- User Creation Point {i} ---")
    # Check if is_admin is set
    if "'is_admin'" in match or '"is_admin"' in match:
        # Check what it's set to
        if "is_admin': True" in match or 'is_admin": True' in match:
            if "'account_type': 'admin'" not in match and '"account_type": "admin"' not in match:
                issues_found.append(f"Point {i}: Sets is_admin=True without checking account_type='admin'")
                print("[ISSUE] Sets is_admin=True without proper account_type check")
            else:
                print("[OK] Properly sets is_admin=True only for admin account_type")
        else:
            print("[OK] Sets is_admin=False or conditional")
    else:
        issues_found.append(f"Point {i}: Missing is_admin field")
        print("[ISSUE] Missing is_admin field - vulnerable to default behavior")
    
    # Check account_type
    if "'account_type'" in match or '"account_type"' in match:
        print("[OK] Sets account_type")
    else:
        issues_found.append(f"Point {i}: Missing account_type field")
        print("[ISSUE] Missing account_type field")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if issues_found:
    print(f"Found {len(issues_found)} issues that need fixing:")
    for issue in issues_found:
        print(f"  - {issue}")
else:
    print("All user creation points properly set is_admin and account_type!")

print("\n" + "=" * 60)
print("RECOMMENDED SECURITY PATTERN")
print("=" * 60)
print("""
When creating ANY user, ALWAYS include:
    'account_type': account_type,  # Must be 'external', 'internal', or 'admin'
    'is_admin': (account_type == 'admin'),  # Only True if account_type is 'admin'

This ensures:
1. is_admin is ALWAYS explicitly set (never undefined)
2. is_admin is ONLY True when account_type is 'admin'
3. No user can get admin access without proper account_type
""")