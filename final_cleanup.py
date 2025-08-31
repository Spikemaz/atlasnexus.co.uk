#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final cleanup - Remove ALL accounts except admin, update passwords
"""

import json
import os
import sys
import io
from datetime import datetime, timedelta

# Set UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def cleanup_everything():
    """Clean all databases and keep only admin"""
    
    print("=" * 60)
    print("FINAL CLEANUP - REMOVING ALL TEST ACCOUNTS")
    print("=" * 60)
    
    # 1. Clean users.json - ONLY keep admin
    print("\n1. Cleaning users.json...")
    admin_only = {
        "spikemaz8@aol.com": {
            "email": "spikemaz8@aol.com",
            "username": "Admin",
            "full_name": "Administrator",
            "account_type": "admin",
            "created_at": datetime.now().isoformat(),
            "is_admin": True,
            "admin_approved": True,
            "password": "SpikeMaz",
            "password_expiry": (datetime.now() + timedelta(days=365)).isoformat(),
            "email_verified": True,
            "last_login": None,
            "login_count": 0,
            "login_history": [],
            "ip_history": []
        }
    }
    
    with open('data/users.json', 'w') as f:
        json.dump(admin_only, f, indent=2)
    print("   ✓ Kept ONLY admin account: spikemaz8@aol.com")
    
    # 2. Clear ALL registrations
    print("\n2. Cleaning registrations.json...")
    with open('data/registrations.json', 'w') as f:
        json.dump({}, f, indent=2)
    print("   ✓ Cleared ALL registrations")
    
    # 3. Clear login attempts
    print("\n3. Cleaning login_attempts.json...")
    if os.path.exists('data/login_attempts.json'):
        with open('data/login_attempts.json', 'w') as f:
            json.dump({}, f, indent=2)
    print("   ✓ Cleared all login attempts")
    
    # 4. Clear IP tracking
    print("\n4. Cleaning ip_tracking.json...")
    if os.path.exists('data/ip_tracking.json'):
        with open('data/ip_tracking.json', 'w') as f:
            json.dump({}, f, indent=2)
    print("   ✓ Cleared all IP tracking")
    
    # 5. Clear IP lockouts
    print("\n5. Cleaning ip_lockouts.json...")
    if os.path.exists('data/ip_lockouts.json'):
        with open('data/ip_lockouts.json', 'w') as f:
            json.dump({}, f, indent=2)
    print("   ✓ Cleared all IP lockouts")
    
    # 6. Clear admin actions
    print("\n6. Cleaning admin_actions.json...")
    if os.path.exists('data/admin_actions.json'):
        with open('data/admin_actions.json', 'w') as f:
            json.dump([], f, indent=2)
    print("   ✓ Cleared all admin actions")
    
    print("\n" + "=" * 60)
    print("CLEANUP COMPLETE")
    print("=" * 60)
    print("\n✅ ALL test accounts removed")
    print("✅ ONLY admin account remains:")
    print("   Email: spikemaz8@aol.com")
    print("   Password: SpikeMaz")
    print("\n⚠️  Gate1 passwords will be updated in app.py to:")
    print("   - SpikeMaz (working)")
    print("   - RedAMC (working)")
    print("   - PartnerAccess (removed)")

if __name__ == "__main__":
    cleanup_everything()