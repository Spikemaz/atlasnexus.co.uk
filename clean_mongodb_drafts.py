"""
Automatically clean draft projects from MongoDB
"""
import os
from pymongo import MongoClient
from datetime import datetime

# Get MongoDB URI from environment
MONGODB_URI = os.environ.get('MONGODB_URI')

if not MONGODB_URI:
    print("MongoDB URI not configured")
    exit(1)

try:
    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)
    db = client.atlasnexus

    print("=" * 70)
    print("CLEANING DRAFTS FROM MONGODB")
    print("=" * 70)

    total_drafts_removed = 0

    # Check projects collection
    projects = db.projects.find()

    for proj_doc in projects:
        user_email = proj_doc.get('user_email', 'Unknown')
        projects_list = proj_doc.get('projects', [])

        # Filter out drafts
        original_count = len(projects_list)
        non_drafts = [p for p in projects_list if 'draft' not in str(p.get('title', '')).lower()]
        drafts_removed = original_count - len(non_drafts)

        if drafts_removed > 0:
            print(f"\n👤 User: {user_email}")
            print(f"   🗑️ Removing {drafts_removed} drafts")
            print(f"   ✅ Keeping {len(non_drafts)} real projects")

            # Update the document
            db.projects.update_one(
                {'user_email': user_email},
                {'$set': {'projects': non_drafts}}
            )

            total_drafts_removed += drafts_removed

    if total_drafts_removed > 0:
        print(f"\n✅ SUCCESS: Removed {total_drafts_removed} drafts from MongoDB!")
    else:
        print("\n✅ No drafts found in MongoDB - all clean!")

    print("\n" + "=" * 70)

    client.close()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()