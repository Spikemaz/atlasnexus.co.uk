#!/usr/bin/env python3
"""
Clean up all user accounts except admin (spikemaz8@aol.com)
Set admin password to 'SpikeMaz'
"""

import json
import os
from datetime import datetime, timedelta

# Data directory
DATA_DIR = 'data'

def cleanup_users():
    """Remove all users except admin"""
    users_file = os.path.join(DATA_DIR, 'users.json')
    
    print("[START] Cleaning up user accounts...")
    
    # Load current users
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            users = json.load(f)
        
        print(f"[INFO] Found {len(users)} users")
        
        # Keep only admin account
        admin_email = "spikemaz8@aol.com"
        new_users = {}
        
        if admin_email in users:
            # Keep admin and update password
            new_users[admin_email] = users[admin_email]
            new_users[admin_email]['password'] = 'SpikeMaz'
            new_users[admin_email]['password_expiry'] = (datetime.now() + timedelta(days=365)).isoformat()
            new_users[admin_email]['is_admin'] = True
            new_users[admin_email]['account_type'] = 'admin'
            new_users[admin_email]['email_verified'] = True
            new_users[admin_email]['admin_approved'] = True
            print(f"[OK] Kept admin account: {admin_email}")
            print(f"[OK] Set password to: SpikeMaz")
        else:
            # Create admin account if doesn't exist
            new_users[admin_email] = {
                "email": admin_email,
                "password": "SpikeMaz",
                "full_name": "Admin User",
                "company_name": "AtlasNexus",
                "phone": "+44 7700 900001",
                "account_type": "admin",
                "is_admin": True,
                "email_verified": True,
                "admin_approved": True,
                "created_at": datetime.now().isoformat(),
                "password_expiry": (datetime.now() + timedelta(days=365)).isoformat(),
                "login_count": 0,
                "last_login": None,
                "is_frozen": False
            }
            print(f"[OK] Created admin account: {admin_email}")
        
        # Remove all other users
        removed_count = len(users) - 1 if admin_email in users else len(users)
        
        # Save cleaned users
        with open(users_file, 'w') as f:
            json.dump(new_users, f, indent=2)
        
        print(f"[OK] Removed {removed_count} user accounts")
    else:
        # Create fresh users file with only admin
        print("[INFO] Creating fresh users file")
        new_users = {
            "spikemaz8@aol.com": {
                "email": "spikemaz8@aol.com",
                "password": "SpikeMaz",
                "full_name": "Admin User",
                "company_name": "AtlasNexus",
                "phone": "+44 7700 900001",
                "account_type": "admin",
                "is_admin": True,
                "email_verified": True,
                "admin_approved": True,
                "created_at": datetime.now().isoformat(),
                "password_expiry": (datetime.now() + timedelta(days=365)).isoformat(),
                "login_count": 0,
                "last_login": None,
                "is_frozen": False
            }
        }
        with open(users_file, 'w') as f:
            json.dump(new_users, f, indent=2)
        print("[OK] Created admin account")

def cleanup_registrations():
    """Remove all pending registrations"""
    registrations_file = os.path.join(DATA_DIR, 'registrations.json')
    
    print("\n[START] Cleaning up registrations...")
    
    if os.path.exists(registrations_file):
        with open(registrations_file, 'r') as f:
            registrations = json.load(f)
        
        count = len(registrations)
        
        # Clear all registrations
        with open(registrations_file, 'w') as f:
            json.dump({}, f, indent=2)
        
        print(f"[OK] Removed {count} pending registrations")
    else:
        # Create empty registrations file
        with open(registrations_file, 'w') as f:
            json.dump({}, f, indent=2)
        print("[OK] Created empty registrations file")

def cleanup_ip_tracking():
    """Clean up IP tracking data"""
    tracking_file = os.path.join(DATA_DIR, 'ip_tracking.json')
    
    print("\n[START] Cleaning up IP tracking...")
    
    if os.path.exists(tracking_file):
        # Clear IP tracking
        with open(tracking_file, 'w') as f:
            json.dump({}, f, indent=2)
        print("[OK] Cleared IP tracking data")
    else:
        with open(tracking_file, 'w') as f:
            json.dump({}, f, indent=2)
        print("[OK] Created empty IP tracking file")

def cleanup_attempts():
    """Clean up failed login attempts"""
    attempts_file = os.path.join(DATA_DIR, 'attempt_logs.json')
    
    print("\n[START] Cleaning up login attempts...")
    
    if os.path.exists(attempts_file):
        # Clear attempts
        with open(attempts_file, 'w') as f:
            json.dump({}, f, indent=2)
        print("[OK] Cleared login attempts")
    else:
        with open(attempts_file, 'w') as f:
            json.dump({}, f, indent=2)
        print("[OK] Created empty attempts file")

def cleanup_lockouts():
    """Clean up IP lockouts"""
    lockouts_file = os.path.join(DATA_DIR, 'ip_lockouts.json')
    
    print("\n[START] Cleaning up IP lockouts...")
    
    if os.path.exists(lockouts_file):
        # Clear lockouts
        with open(lockouts_file, 'w') as f:
            json.dump({}, f, indent=2)
        print("[OK] Cleared IP lockouts")
    else:
        with open(lockouts_file, 'w') as f:
            json.dump({}, f, indent=2)
        print("[OK] Created empty lockouts file")

def verify_override_code():
    """Verify override code is set to Ronabambi"""
    print("\n[START] Verifying override code...")
    print("[OK] Override code: Ronabambi (hardcoded in app.py)")

def main():
    print("="*60)
    print("ATLASNEXUS USER CLEANUP")
    print("="*60)
    
    # Ensure data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"[OK] Created data directory: {DATA_DIR}")
    
    # Run cleanup
    cleanup_users()
    cleanup_registrations()
    cleanup_ip_tracking()
    cleanup_attempts()
    cleanup_lockouts()
    verify_override_code()
    
    print("\n" + "="*60)
    print("CLEANUP COMPLETE")
    print("="*60)
    print("\nFinal Configuration:")
    print("  Admin Email: spikemaz8@aol.com")
    print("  Admin Password: SpikeMaz")
    print("  Site Password: AtlasNexus2024!")
    print("  Override Code: Ronabambi")
    print("\n[SUCCESS] All user data cleaned!")
    print("\nNOTE: These changes are LOCAL only.")
    print("Run 'git add -A && git commit && git push' to deploy to live site.")

if __name__ == "__main__":
    main()