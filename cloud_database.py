"""
Cloud Database Module for AtlasNexus
Uses MongoDB Atlas for permanent, cloud-based storage
Free tier: 512MB storage, perfect for this application
"""

import os
import json
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.server_api import ServerApi
import time

# MongoDB Atlas connection
# For production, set MONGODB_URI in Vercel environment variables
# Format: mongodb+srv://username:password@cluster.mongodb.net/database
MONGODB_URI = os.environ.get('MONGODB_URI', '')

# Fallback to local file storage if MongoDB not configured
USE_MONGODB = bool(MONGODB_URI)

class CloudDatabase:
    """Cloud-based persistent database"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.connected = False
        
        if USE_MONGODB:
            try:
                print(f"[DATABASE] Attempting MongoDB connection...")
                print(f"[DATABASE] URI configured: {bool(MONGODB_URI)}")
                # Connect to MongoDB Atlas with ServerApi
                self.client = MongoClient(MONGODB_URI, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000)
                # Test connection
                self.client.admin.command('ping')
                self.db = self.client.atlasnexus
                self.connected = True
                print("[DATABASE] Connected to MongoDB Atlas successfully!")
                
                # Initialize collections
                self._init_collections()
            except Exception as e:
                print(f"[DATABASE] MongoDB connection failed: {str(e)}")
                print(f"[DATABASE] Error type: {type(e).__name__}")
                self.connected = False
        else:
            print(f"[DATABASE] MongoDB URI not configured - using local storage")
            print(f"[DATABASE] MONGODB_URI env var present: {bool(os.environ.get('MONGODB_URI'))}")
    
    def _init_collections(self):
        """Initialize database collections with indexes"""
        if not self.connected:
            return
        
        # Create indexes for better performance
        try:
            self.db.users.create_index("email", unique=True)
            self.db.registrations.create_index("email", unique=True)
            self.db.admin_actions.create_index("timestamp")
            
            # Ensure admin user exists
            admin_user = {
                'email': 'spikemaz8@aol.com',
                'username': 'Admin',
                'full_name': 'Administrator',
                'account_type': 'admin',
                'created_at': '2025-08-20T01:39:46.674704',
                'is_admin': True,
                'admin_approved': True,
                'password': 'SpikeMaz',
                'password_expiry': '2026-09-01T12:00:00',
                'email_verified': True,
                'login_count': 0
            }
            
            # Upsert admin user (update if exists, insert if not)
            self.db.users.update_one(
                {'email': 'spikemaz8@aol.com'},
                {'$setOnInsert': admin_user},
                upsert=True
            )
        except Exception as e:
            print(f"[DATABASE] Error initializing collections: {e}")
    
    def load_users(self):
        """Load all users from database"""
        if not self.connected:
            return self._load_local('users')
        
        try:
            users = {}
            for user in self.db.users.find():
                user.pop('_id', None)  # Remove MongoDB ID
                users[user['email']] = user
            return users
        except Exception as e:
            print(f"[DATABASE] Error loading users: {e}")
            return self._load_local('users')
    
    def save_user(self, email, user_data):
        """Save or update a user"""
        if not self.connected:
            return self._save_local_user(email, user_data)
        
        try:
            user_data['email'] = email
            self.db.users.update_one(
                {'email': email},
                {'$set': user_data},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"[DATABASE] Error saving user: {e}")
            return False
    
    def delete_user(self, email):
        """Delete a user (except admin)"""
        if email == 'spikemaz8@aol.com':
            return False  # Never delete admin
        
        if not self.connected:
            return self._delete_local_user(email)
        
        try:
            self.db.users.delete_one({'email': email})
            return True
        except Exception as e:
            print(f"[DATABASE] Error deleting user: {e}")
            return False
    
    def load_registrations(self):
        """Load all registrations from database"""
        if not self.connected:
            return self._load_local('registrations')
        
        try:
            registrations = {}
            for reg in self.db.registrations.find():
                reg.pop('_id', None)
                registrations[reg['email']] = reg
            return registrations
        except Exception as e:
            print(f"[DATABASE] Error loading registrations: {e}")
            return self._load_local('registrations')
    
    def save_registration(self, email, reg_data):
        """Save or update a registration"""
        if not self.connected:
            return self._save_local_registration(email, reg_data)
        
        try:
            reg_data['email'] = email
            self.db.registrations.update_one(
                {'email': email},
                {'$set': reg_data},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"[DATABASE] Error saving registration: {e}")
            return False
    
    def delete_registration(self, email):
        """Delete a registration"""
        if not self.connected:
            return self._delete_local_registration(email)
        
        try:
            self.db.registrations.delete_one({'email': email})
            return True
        except Exception as e:
            print(f"[DATABASE] Error deleting registration: {e}")
            return False
    
    def load_admin_actions(self):
        """Load admin actions log"""
        if not self.connected:
            return self._load_local('admin_actions')
        
        try:
            actions = []
            for action in self.db.admin_actions.find().sort('timestamp', -1).limit(100):
                action.pop('_id', None)
                actions.append(action)
            return actions
        except Exception as e:
            print(f"[DATABASE] Error loading admin actions: {e}")
            return []
    
    def add_admin_action(self, action):
        """Add an admin action to the log"""
        if not self.connected:
            return self._add_local_admin_action(action)
        
        try:
            action['timestamp'] = datetime.now().isoformat()
            self.db.admin_actions.insert_one(action)
            return True
        except Exception as e:
            print(f"[DATABASE] Error adding admin action: {e}")
            return False
    
    def upload_file(self, user_email, filename, file_data):
        """Store uploaded file data"""
        if not self.connected:
            return False
        
        try:
            file_doc = {
                'user_email': user_email,
                'filename': filename,
                'data': file_data,
                'uploaded_at': datetime.now().isoformat()
            }
            self.db.files.insert_one(file_doc)
            return True
        except Exception as e:
            print(f"[DATABASE] Error uploading file: {e}")
            return False
    
    def get_user_files(self, user_email):
        """Get all files for a user"""
        if not self.connected:
            return []
        
        try:
            files = []
            for file in self.db.files.find({'user_email': user_email}):
                file.pop('_id', None)
                files.append(file)
            return files
        except Exception as e:
            print(f"[DATABASE] Error getting user files: {e}")
            return []
    
    # Local fallback methods
    def _load_local(self, collection):
        """Load from local file as fallback"""
        from pathlib import Path
        file_path = Path('data') / f'{collection}.json'
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {} if collection != 'admin_actions' else []
    
    def _save_local_user(self, email, user_data):
        """Save user to local file"""
        users = self._load_local('users')
        users[email] = user_data
        return self._save_local('users', users)
    
    def _delete_local_user(self, email):
        """Delete user from local file"""
        if email == 'spikemaz8@aol.com':
            return False
        users = self._load_local('users')
        if email in users:
            del users[email]
            return self._save_local('users', users)
        return False
    
    def _save_local_registration(self, email, reg_data):
        """Save registration to local file"""
        registrations = self._load_local('registrations')
        registrations[email] = reg_data
        return self._save_local('registrations', registrations)
    
    def _delete_local_registration(self, email):
        """Delete registration from local file"""
        registrations = self._load_local('registrations')
        if email in registrations:
            del registrations[email]
            return self._save_local('registrations', registrations)
        return False
    
    def _add_local_admin_action(self, action):
        """Add admin action to local file"""
        actions = self._load_local('admin_actions')
        if not isinstance(actions, list):
            actions = []
        actions.append(action)
        return self._save_local('admin_actions', actions)
    
    def _save_local(self, collection, data):
        """Save to local file"""
        from pathlib import Path
        try:
            file_path = Path('data') / f'{collection}.json'
            file_path.parent.mkdir(exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except:
            return False

# Global database instance
cloud_db = CloudDatabase()

# Helper functions for backward compatibility
def load_users():
    """Load all users"""
    return cloud_db.load_users()

def save_users(users_dict):
    """Save all users"""
    for email, user_data in users_dict.items():
        cloud_db.save_user(email, user_data)
    return True

def load_registrations():
    """Load all registrations"""
    return cloud_db.load_registrations()

def save_registrations(regs_dict):
    """Save all registrations"""
    for email, reg_data in regs_dict.items():
        cloud_db.save_registration(email, reg_data)
    return True

def load_admin_actions():
    """Load admin actions"""
    return cloud_db.load_admin_actions()

def add_admin_action(action):
    """Add admin action"""
    return cloud_db.add_admin_action(action)