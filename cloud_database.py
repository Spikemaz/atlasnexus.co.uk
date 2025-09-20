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
def get_mongodb_uri():
    """Get MongoDB URI dynamically"""
    # Check environment variable first, then use hardcoded for testing
    uri = os.environ.get('MONGODB_URI', '')
    if not uri and os.path.exists('mongodb_uri.txt'):
        # For local testing, read from file if exists
        try:
            with open('mongodb_uri.txt', 'r') as f:
                uri = f.read().strip()
        except:
            pass
    return uri

def should_use_mongodb():
    """Check if MongoDB should be used"""
    uri = get_mongodb_uri()
    return bool(uri)

class CloudDatabase:
    """Cloud-based persistent database"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.connected = False
        
        # Check for MongoDB URI at initialization time
        MONGODB_URI = get_mongodb_uri()
        
        if MONGODB_URI:
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
            print(f"[DATABASE] MONGODB_URI env var present: {bool(get_mongodb_uri())}")
    
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
            return {}
        
        try:
            users = {}
            for user in self.db.users.find():
                user.pop('_id', None)  # Remove MongoDB ID
                users[user['email']] = user
            return users
        except Exception as e:
            print(f"[DATABASE] Error loading users: {e}")
            return {}
    
    def save_user(self, email, user_data):
        """Save or update a user"""
        if not self.connected:
            print(f"[DATABASE] Not connected - cannot save user {email}")
            return False
        
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
            print(f"[DATABASE] Not connected - cannot delete user {email}")
            return False
        
        try:
            self.db.users.delete_one({'email': email})
            return True
        except Exception as e:
            print(f"[DATABASE] Error deleting user: {e}")
            return False
    
    def load_registrations(self):
        """Load all registrations from database"""
        if not self.connected:
            return {}
        
        try:
            registrations = {}
            for reg in self.db.registrations.find():
                reg.pop('_id', None)
                registrations[reg['email']] = reg
            return registrations
        except Exception as e:
            print(f"[DATABASE] Error loading registrations: {e}")
            return {}
    
    def save_registration(self, email, reg_data):
        """Save or update a registration"""
        if not self.connected:
            print(f"[DATABASE] Not connected - cannot save registration {email}")
            return False
        
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
            print(f"[DATABASE] Not connected - cannot delete registration {email}")
            return False
        
        try:
            self.db.registrations.delete_one({'email': email})
            return True
        except Exception as e:
            print(f"[DATABASE] Error deleting registration: {e}")
            return False
    
    def load_admin_actions(self):
        """Load admin actions log"""
        if not self.connected:
            print("[DATABASE] Not connected - returning empty admin actions")
            return []
        
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
            print("[DATABASE] Not connected - cannot add admin action")
            return False
        
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
    
    def load_projects(self):
        """Load all projects from database"""
        if not self.connected:
            return {}
        
        try:
            projects = {}
            for proj in self.db.projects.find():
                user_email = proj.get('user_email')
                if user_email:
                    proj.pop('_id', None)
                    proj.pop('user_email', None)
                    if user_email not in projects:
                        projects[user_email] = {'projects': [], 'series': [], 'order': []}
                    # Reconstruct the data structure
                    if 'projects' in proj:
                        projects[user_email]['projects'] = proj['projects']
                    if 'series' in proj:
                        projects[user_email]['series'] = proj['series']
                    if 'order' in proj:
                        projects[user_email]['order'] = proj['order']
            return projects
        except Exception as e:
            print(f"[DATABASE] Error loading projects: {e}")
            return {}
    
    def save_projects(self, user_email, project_data):
        """Save or update projects for a user"""
        if not self.connected:
            print(f"[DATABASE] Not connected - cannot save projects for {user_email}")
            return False
        
        try:
            # Add user_email to the document
            doc = {
                'user_email': user_email,
                'projects': project_data.get('projects', []),
                'series': project_data.get('series', []),
                'order': project_data.get('order', []),
                'updated_at': datetime.now().isoformat()
            }
            
            self.db.projects.update_one(
                {'user_email': user_email},
                {'$set': doc},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"[DATABASE] Error saving projects: {e}")
            return False
    
    def save_permutation_snapshot(self, project_id, snapshot_data):
        """Save a snapshot of project data when loaded into permutation engine"""
        if not self.connected:
            return False
        
        try:
            doc = {
                'project_id': project_id,
                'snapshot_data': snapshot_data,
                'created_at': datetime.now().isoformat(),
                'approved': True,  # Initial snapshot is auto-approved
                'version': 1
            }
            
            # Check if snapshot exists and increment version
            existing = self.db.permutation_snapshots.find_one({'project_id': project_id})
            if existing:
                doc['version'] = existing.get('version', 1) + 1
            
            self.db.permutation_snapshots.insert_one(doc)
            return True
        except Exception as e:
            print(f"[DATABASE] Error saving permutation snapshot: {e}")
            return False
    
    def get_permutation_snapshot(self, project_id):
        """Get the latest approved snapshot for a project"""
        if not self.connected:
            return None
        
        try:
            # Get the latest approved snapshot
            snapshot = self.db.permutation_snapshots.find_one(
                {'project_id': project_id, 'approved': True},
                sort=[('version', -1)]
            )
            return snapshot
        except Exception as e:
            print(f"[DATABASE] Error loading permutation snapshot: {e}")
            return None
    
    def save_project_change_request(self, project_id, user_email, changes):
        """Save a change request when client modifies project"""
        if not self.connected:
            return False
        
        try:
            doc = {
                'project_id': project_id,
                'user_email': user_email,
                'changes': changes,
                'status': 'pending',  # pending, approved, rejected
                'created_at': datetime.now().isoformat(),
                'reviewed_at': None,
                'reviewed_by': None
            }
            
            self.db.project_changes.insert_one(doc)
            return True
        except Exception as e:
            print(f"[DATABASE] Error saving change request: {e}")
            return False
    
    def get_pending_changes(self):
        """Get all pending change requests"""
        if not self.connected:
            return []
        
        try:
            changes = list(self.db.project_changes.find({'status': 'pending'}))
            return changes
        except Exception as e:
            print(f"[DATABASE] Error loading pending changes: {e}")
            return []
    
    def load_ip_tracking(self):
        """Load IP tracking data"""
        if not self.connected:
            return {}
        try:
            tracking = self.db.ip_tracking.find_one({'_id': 'tracking'})
            return tracking.get('data', {}) if tracking else {}
        except Exception as e:
            print(f"[DATABASE] Error loading IP tracking: {e}")
            return {}
    
    def save_ip_tracking(self, tracking_data):
        """Save IP tracking data"""
        if not self.connected:
            return False
        try:
            self.db.ip_tracking.replace_one(
                {'_id': 'tracking'},
                {'_id': 'tracking', 'data': tracking_data},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"[DATABASE] Error saving IP tracking: {e}")
            return False
    
    def load_login_attempts(self):
        """Load login attempts data"""
        if not self.connected:
            return {}
        try:
            attempts = self.db.login_attempts.find_one({'_id': 'attempts'})
            return attempts.get('data', {}) if attempts else {}
        except Exception as e:
            print(f"[DATABASE] Error loading login attempts: {e}")
            return {}
    
    def save_login_attempts(self, attempts_data):
        """Save login attempts data"""
        if not self.connected:
            return False
        try:
            self.db.login_attempts.replace_one(
                {'_id': 'attempts'},
                {'_id': 'attempts', 'data': attempts_data},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"[DATABASE] Error saving login attempts: {e}")
            return False
    
    def get_database_stats(self):
        """Get MongoDB database statistics including storage usage"""
        if not self.connected:
            return {
                'connected': False,
                'storage_used_mb': 0,
                'storage_limit_mb': 512,
                'storage_percentage': 0,
                'collections': {}
            }

        try:
            # Get database stats with scale=1 for bytes
            stats = self.db.command('dbStats', 1)

            # MongoDB Atlas shows the total data size across all databases
            # We need to get stats from all databases in the cluster
            total_data_size = 0
            total_storage_size = 0

            # Get list of all databases
            database_list = self.client.list_database_names()

            for db_name in database_list:
                if db_name not in ['admin', 'local', 'config']:  # Skip system databases
                    try:
                        db_stats = self.client[db_name].command('dbStats', 1)
                        # Atlas "Data Size" is the sum of dataSize (uncompressed data)
                        total_data_size += db_stats.get('dataSize', 0)
                        total_storage_size += db_stats.get('storageSize', 0)
                    except:
                        pass

            # If we couldn't get cluster-wide stats, use current database
            if total_data_size == 0:
                total_data_size = stats.get('dataSize', 0)
                total_storage_size = stats.get('storageSize', 0)

            # Convert to MB - Atlas shows Data Size (uncompressed)
            # This should match the 116.23 MB shown in Atlas
            storage_mb = round(total_data_size / (1024 * 1024), 2)
            storage_limit_mb = 512  # Free tier limit
            storage_percentage = round((storage_mb / storage_limit_mb) * 100, 1)

            # Get detailed collection stats for current database
            collection_stats = {}
            total_collections_data = 0

            for coll_name in self.db.list_collection_names():
                try:
                    coll_stats = self.db.command('collStats', coll_name, scale=1)
                    # Use dataSize for actual data (matches Atlas reporting)
                    data_size_mb = round(coll_stats.get('size', 0) / (1024 * 1024), 2)
                    total_collections_data += coll_stats.get('size', 0)
                    collection_stats[coll_name] = {
                        'count': coll_stats.get('count', 0),
                        'size_mb': data_size_mb
                    }
                except:
                    # Fallback to simple count if collStats fails
                    collection_stats[coll_name] = {
                        'count': self.db[coll_name].count_documents({}),
                        'size_mb': 0
                    }

            return {
                'connected': True,
                'storage_used_mb': storage_mb,
                'storage_limit_mb': storage_limit_mb,
                'storage_percentage': storage_percentage,
                'storage_remaining_mb': round(storage_limit_mb - storage_mb, 2),
                'collections': collection_stats,
                'database_name': self.db.name,
                'data_size_mb': storage_mb,  # This is the actual data size
                'storage_size_mb': round(total_storage_size / (1024 * 1024), 2),  # Compressed storage
                'index_size_mb': round(stats.get('indexSize', 0) / (1024 * 1024), 2)
            }
        except Exception as e:
            print(f"[DATABASE] Error getting database stats: {e}")
            return {
                'connected': self.connected,
                'storage_used_mb': 0,
                'storage_limit_mb': 512,
                'storage_percentage': 0,
                'error': str(e)
            }
    
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

# Global database instance - initialize as None first
cloud_db = None

def get_db():
    """Get or create database instance"""
    global cloud_db
    if cloud_db is None:
        cloud_db = CloudDatabase()
    return cloud_db

def reinitialize_db():
    """Reinitialize database connection"""
    global cloud_db
    cloud_db = CloudDatabase()
    return cloud_db.connected

# Initialize on first import
cloud_db = get_db()

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

def load_projects():
    """Load all projects"""
    return cloud_db.load_projects()

def save_project_data(user_email, project_data):
    """Save project data for a user"""
    return cloud_db.save_projects(user_email, project_data)