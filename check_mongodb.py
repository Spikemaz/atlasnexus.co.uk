#!/usr/bin/env python3
"""
MongoDB Connection Tester for AtlasNexus
Run this script to test your MongoDB connection
"""

import os
import sys
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Fix Unicode output on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def test_mongodb_connection():
    """Test MongoDB connection"""
    
    print("=" * 60)
    print("MongoDB Connection Test for AtlasNexus")
    print("=" * 60)
    
    # Check for MongoDB URI
    mongodb_uri = os.environ.get('MONGODB_URI', '')
    
    # Also check for a local file (for testing)
    if not mongodb_uri and os.path.exists('mongodb_uri.txt'):
        try:
            with open('mongodb_uri.txt', 'r') as f:
                mongodb_uri = f.read().strip()
                print("[OK] MongoDB URI loaded from local file")
        except Exception as e:
            print(f"[ERROR] Error reading mongodb_uri.txt: {e}")
    
    if not mongodb_uri:
        print("\n[ERROR] MongoDB URI not found!")
        print("\nTo fix this:")
        print("1. For Vercel deployment:")
        print("   - Go to your Vercel project settings")
        print("   - Add MONGODB_URI environment variable")
        print("   - Use format: mongodb+srv://username:password@cluster.mongodb.net/database")
        print("\n2. For local testing:")
        print("   - Create a file 'mongodb_uri.txt' in this directory")
        print("   - Add your MongoDB URI to that file")
        print("\n3. Get your MongoDB URI from:")
        print("   - https://cloud.mongodb.com")
        print("   - Click 'Connect' on your cluster")
        print("   - Choose 'Connect your application'")
        print("   - Copy the connection string")
        return False
    
    # Mask the URI for display
    parts = mongodb_uri.split('@')
    if len(parts) > 1:
        masked_uri = "mongodb+srv://***:***@" + parts[1]
    else:
        masked_uri = "***configured***"
    
    print(f"[OK] MongoDB URI found: {masked_uri}")
    
    # Try to connect
    print("\nAttempting to connect to MongoDB...")
    try:
        client = MongoClient(mongodb_uri, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000)
        
        # Test connection with ping
        client.admin.command('ping')
        print("[OK] Successfully connected to MongoDB Atlas!")
        
        # Get database
        db = client.atlasnexus
        print(f"[OK] Using database: {db.name}")
        
        # List collections
        collections = db.list_collection_names()
        print(f"\nCollections in database:")
        for coll in collections:
            count = db[coll].count_documents({})
            print(f"  - {coll}: {count} documents")
        
        # Check database stats
        stats = db.command('dbStats')
        storage_bytes = stats.get('dataSize', 0) + stats.get('indexSize', 0)
        storage_mb = round(storage_bytes / (1024 * 1024), 2)
        print(f"\nStorage used: {storage_mb} MB / 512 MB (free tier limit)")
        
        # Test write operation
        print("\nTesting write operation...")
        test_doc = {'test': True, 'message': 'Connection test successful'}
        result = db.test_collection.insert_one(test_doc)
        print(f"[OK] Write test successful (ID: {result.inserted_id})")
        
        # Clean up test document
        db.test_collection.delete_one({'_id': result.inserted_id})
        print("[OK] Cleanup successful")
        
        print("\n" + "=" * 60)
        print("SUCCESS: All tests passed! MongoDB is properly configured.")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Failed to connect to MongoDB: {e}")
        print("\nPossible issues:")
        print("1. Check your MongoDB URI is correct")
        print("2. Ensure your IP address is whitelisted in MongoDB Atlas")
        print("   - Go to MongoDB Atlas > Network Access")
        print("   - Add 0.0.0.0/0 to allow access from anywhere")
        print("3. Check your username and password are correct")
        print("4. Ensure your cluster is active and not paused")
        
        return False

if __name__ == "__main__":
    success = test_mongodb_connection()
    sys.exit(0 if success else 1)