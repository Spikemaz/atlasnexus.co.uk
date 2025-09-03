#!/usr/bin/env python3
"""Ensure admin account exists with proper settings"""

import os
import json
from datetime import datetime
import hashlib

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.local')

# MongoDB setup
MONGODB_URI = os.environ.get('MONGODB_URI')
if MONGODB_URI:
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client.atlasnexus
        
        # Admin user data
        admin_email = "spikemaz8@aol.com"
        admin_password = "SpikeMaz"
        
        # Hash the password
        password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
        
        admin_user = {
            "email": admin_email,
            "username": "Admin",
            "password": password_hash,
            "account_type": "admin",
            "is_admin": True,
            "full_name": "Marcus Moore",
            "company": "Atlas Nexus",
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat(),
            "email_verified": True,
            "admin_verified": True,
            "approved_by": "system",
            "credentials_sent": True,
            "account_status": "active"
        }
        
        # Update or insert the admin user
        result = db.users.update_one(
            {"email": admin_email},
            {"$set": admin_user},
            upsert=True
        )
        
        if result.upserted_id:
            print(f"[OK] Admin account created: {admin_email}")
        elif result.modified_count > 0:
            print(f"[OK] Admin account updated: {admin_email}")
        else:
            print(f"[OK] Admin account already exists with correct settings: {admin_email}")
            
        # Verify the account
        user = db.users.find_one({"email": admin_email})
        if user:
            print(f"  Account Type: {user.get('account_type')}")
            print(f"  Is Admin: {user.get('is_admin')}")
            print(f"  Status: {user.get('account_status')}")
        
        print("\nAdmin account is ready!")
        
    except Exception as e:
        print(f"MongoDB Error: {e}")
        print("Creating local users.json file instead...")
        
        # Create local users.json
        os.makedirs('data', exist_ok=True)
        users_file = 'data/users.json'
        
        users = {}
        if os.path.exists(users_file):
            try:
                with open(users_file, 'r') as f:
                    users = json.load(f)
            except:
                pass
        
        # Add admin user
        users[admin_email] = {
            "username": "Admin",
            "password": password_hash,
            "account_type": "admin",
            "is_admin": True,
            "full_name": "Marcus Moore",
            "company": "Atlas Nexus",
            "created_at": datetime.now().isoformat(),
            "email_verified": True,
            "admin_verified": True,
            "account_status": "active"
        }
        
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)
        
        print(f"[OK] Admin account created in local file: {admin_email}")
else:
    print("MongoDB URI not configured")
    print("Please set MONGODB_URI in .env.local")