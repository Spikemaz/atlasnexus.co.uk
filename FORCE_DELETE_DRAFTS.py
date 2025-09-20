"""
FORCE DELETE ALL DRAFTS DIRECTLY FROM MONGODB
"""

from pymongo import MongoClient

# Direct connection to MongoDB - from .env.local
MONGODB_URI = "mongodb+srv://marcusbmoore1992_db_user:w6SbBmfO0MQhbXud@cluster0.oduikdo.mongodb.net/atlasnexus?retryWrites=true&w=majority&appName=Cluster0"

print("FORCE DELETING ALL DRAFTS FROM MONGODB")
print("=" * 70)

try:
    # Connect
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    print("Connected to MongoDB!")

    db = client.atlasnexus

    # Get all projects
    total_before = 0
    total_after = 0

    for doc in db.projects.find():
        user = doc.get('user_email', 'Unknown')
        projects = doc.get('projects', [])
        total_before += len(projects)

        # Remove ALL drafts
        clean_projects = []
        removed = 0

        for p in projects:
            title = str(p.get('title', '')).lower()
            if 'draft' in title:
                print(f"  DELETING: {p.get('title')} from {user}")
                removed += 1
            else:
                clean_projects.append(p)

        if removed > 0:
            # UPDATE MongoDB
            result = db.projects.update_one(
                {'user_email': user},
                {'$set': {'projects': clean_projects}}
            )
            print(f"  --> Removed {removed} drafts from {user}")

        total_after += len(clean_projects)

    print(f"\nBEFORE: {total_before} total projects")
    print(f"AFTER: {total_after} total projects")
    print(f"DELETED: {total_before - total_after} drafts")

    # Also check trash
    print("\nChecking trash collection...")
    for doc in db.trash.find():
        user = doc.get('user_email', 'Unknown')
        items = doc.get('items', [])

        clean_items = []
        removed = 0

        for item in items:
            if 'draft' in str(item.get('title', '')).lower():
                print(f"  Removing draft from trash: {item.get('title')}")
                removed += 1
            else:
                clean_items.append(item)

        if removed > 0:
            db.trash.update_one(
                {'user_email': user},
                {'$set': {'items': clean_items}}
            )
            print(f"  --> Removed {removed} drafts from {user}'s trash")

    print("\nDONE! All drafts have been forcefully deleted.")

    client.close()

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()