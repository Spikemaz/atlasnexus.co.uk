"""
NUCLEAR OPTION - PERMANENTLY DELETE ALL DRAFTS FROM MONGODB
This will connect directly to MongoDB and remove ALL drafts
"""

import os
from pymongo import MongoClient

# MongoDB URI - taken from your cloud_database.py
MONGODB_URI = "mongodb+srv://atlasnexus:WangChung83@cluster0.ojqryyp.mongodb.net/atlasnexus?retryWrites=true&w=majority"

def nuclear_clean():
    """Directly connect to MongoDB and DESTROY all drafts"""

    print("=" * 70)
    print("NUCLEAR DRAFT CLEANER - DIRECT MONGODB CONNECTION")
    print("=" * 70)

    try:
        # Direct connection
        print("Connecting to MongoDB Atlas...")
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)

        # Force connection test
        client.server_info()
        print("✓ Connected successfully!")

        db = client.atlasnexus

        # 1. Clean projects collection
        print("\n=== CLEANING PROJECTS COLLECTION ===")
        projects_cursor = db.projects.find()

        total_removed = 0
        for doc in projects_cursor:
            user = doc.get('user_email', 'Unknown')
            projects = doc.get('projects', [])

            # Show what we found
            drafts = [p for p in projects if 'draft' in str(p.get('title', '')).lower()]

            if drafts:
                print(f"\nUser: {user}")
                print(f"  Found {len(drafts)} drafts out of {len(projects)} total projects")

                # List all draft titles
                for d in drafts:
                    print(f"  - DELETING: {d.get('title', 'No title')}")

                # REMOVE ALL DRAFTS
                clean_projects = [p for p in projects if 'draft' not in str(p.get('title', '')).lower()]

                # UPDATE DATABASE
                result = db.projects.update_one(
                    {'user_email': user},
                    {'$set': {'projects': clean_projects}}
                )

                if result.modified_count > 0:
                    print(f"  ✓ REMOVED {len(drafts)} drafts from {user}")
                    total_removed += len(drafts)

        # 2. Clean trash collection
        print("\n=== CLEANING TRASH COLLECTION ===")
        trash_cursor = db.trash.find()

        trash_removed = 0
        for doc in trash_cursor:
            user = doc.get('user_email', 'Unknown')
            items = doc.get('items', [])

            # Remove draft items from trash
            draft_items = [item for item in items if 'draft' in str(item.get('title', '')).lower()]

            if draft_items:
                print(f"\nUser: {user}")
                print(f"  Found {len(draft_items)} drafts in trash")

                clean_items = [item for item in items if 'draft' not in str(item.get('title', '')).lower()]

                result = db.trash.update_one(
                    {'user_email': user},
                    {'$set': {'items': clean_items}}
                )

                if result.modified_count > 0:
                    print(f"  ✓ REMOVED {len(draft_items)} drafts from trash")
                    trash_removed += len(draft_items)

        # 3. VERIFICATION
        print("\n=== VERIFICATION ===")

        # Count remaining drafts
        remaining = 0
        for doc in db.projects.find():
            projects = doc.get('projects', [])
            drafts = [p for p in projects if 'draft' in str(p.get('title', '')).lower()]
            remaining += len(drafts)

        print(f"\nRESULTS:")
        print(f"  Total drafts removed from projects: {total_removed}")
        print(f"  Total drafts removed from trash: {trash_removed}")
        print(f"  Remaining drafts in database: {remaining}")

        if remaining == 0:
            print("\n✓✓✓ SUCCESS! ALL DRAFTS HAVE BEEN ELIMINATED ✓✓✓")
        else:
            print(f"\n!!! WARNING: {remaining} drafts still remain !!!")

            # Show what's left
            for doc in db.projects.find():
                projects = doc.get('projects', [])
                drafts = [p for p in projects if 'draft' in str(p.get('title', '')).lower()]
                if drafts:
                    print(f"User {doc.get('user_email')}: {len(drafts)} drafts")
                    for d in drafts[:3]:
                        print(f"  - {d.get('title')}")

        client.close()

    except Exception as e:
        print(f"\n!!! ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    nuclear_clean()

    print("\n" + "=" * 70)
    print("OPERATION COMPLETE")
    print("=" * 70)