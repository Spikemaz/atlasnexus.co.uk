#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean up databases and ensure only admin account remains
"""

import json
import os
import sys
import io
from datetime import datetime, timedelta

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# File paths
USERS_FILE = 'data/users.json'
REGISTRATIONS_FILE = 'data/registrations.json'
LOGIN_ATTEMPTS_FILE = 'data/login_attempts.json'
IP_TRACKING_FILE = 'data/ip_tracking.json'

def clean_databases():
    """Clean all databases except admin account"""
    
    print("=" * 60)
    print("DATABASE CLEANUP SCRIPT")
    print("=" * 60)
    
    # 1. Clean users.json - keep only admin
    print("\n1. Cleaning users.json...")
    admin_user = {
        "spikemaz8@aol.com": {
            "email": "spikemaz8@aol.com",
            "username": "Admin",
            "full_name": "Administrator",
            "account_type": "admin",
            "created_at": "2025-08-20T01:39:46.674704",
            "is_admin": True,
            "admin_approved": True,
            "password": "SpikeMaz",
            "password_expiry": (datetime.now() + timedelta(days=365)).isoformat(),
            "email_verified": True,
            "last_login": datetime.now().isoformat(),
            "login_count": 0,
            "login_history": [],
            "ip_history": []
        }
    }
    
    # Save clean users file
    with open(USERS_FILE, 'w') as f:
        json.dump(admin_user, f, indent=2)
    print(f"   ✓ Kept admin account: spikemaz8@aol.com")
    print(f"   ✓ Password: SpikeMaz")
    
    # 2. Clean registrations.json
    print("\n2. Cleaning registrations.json...")
    empty_registrations = {}
    with open(REGISTRATIONS_FILE, 'w') as f:
        json.dump(empty_registrations, f, indent=2)
    print(f"   ✓ Cleared all pending registrations")
    
    # 3. Clean login_attempts.json
    print("\n3. Cleaning login_attempts.json...")
    if os.path.exists(LOGIN_ATTEMPTS_FILE):
        with open(LOGIN_ATTEMPTS_FILE, 'w') as f:
            json.dump({}, f, indent=2)
        print(f"   ✓ Cleared all login attempts")
    
    # 4. Clean ip_tracking.json
    print("\n4. Cleaning ip_tracking.json...")
    if os.path.exists(IP_TRACKING_FILE):
        with open(IP_TRACKING_FILE, 'w') as f:
            json.dump({}, f, indent=2)
        print(f"   ✓ Cleared all IP tracking data")
    
    print("\n" + "=" * 60)
    print("CLEANUP COMPLETE")
    print("=" * 60)
    print("\n✅ All databases cleaned")
    print("✅ Admin account preserved:")
    print("   Email: spikemaz8@aol.com")
    print("   Password: SpikeMaz")
    print("\nThe system is now ready for fresh testing.")

if __name__ == "__main__":
    clean_databases()