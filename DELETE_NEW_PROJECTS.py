"""
DELETE ALL "New Project" DRAFTS FROM MONGODB
"""

from pymongo import MongoClient

# Direct connection to MongoDB
MONGODB_URI = "mongodb+srv://marcusbmoore1992_db_user:w6SbBmfO0MQhbXud@cluster0.oduikdo.mongodb.net/atlasnexus?retryWrites=true&w=majority&appName=Cluster0"

print("DELETING ALL 'New Project' DRAFTS")
print("=" * 70)

try:
    # Connect
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    print("Connected to MongoDB!")

    db = client.atlasnexus

    total_deleted = 0

    for doc in db.projects.find():
        user = doc.get('user_email', 'Unknown')
        projects = doc.get('projects', [])

        # Filter out all "New Project" drafts
        clean_projects = []
        deleted = 0

        for p in projects:
            title = p.get('title', '')
            status = p.get('status', '')

            # Delete if it's "New Project" and status is "draft"
            if title == 'New Project' and status == 'draft':
                print(f"  DELETING: '{title}' (status: {status}) from {user}")
                deleted += 1
                total_deleted += 1
            else:
                clean_projects.append(p)

        if deleted > 0:
            # UPDATE MongoDB
            result = db.projects.update_one(
                {'user_email': user},
                {'$set': {'projects': clean_projects}}
            )
            print(f"  --> Deleted {deleted} 'New Project' drafts from {user}")

    print(f"\n{'=' * 70}")
    print(f"TOTAL DELETED: {total_deleted} 'New Project' drafts")
    print("=" * 70)

    # Verify
    print("\nVERIFYING...")
    remaining = 0
    for doc in db.projects.find():
        projects = doc.get('projects', [])
        for p in projects:
            if p.get('title') == 'New Project' and p.get('status') == 'draft':
                remaining += 1

    if remaining == 0:
        print("SUCCESS! All 'New Project' drafts have been deleted!")
    else:
        print(f"WARNING: {remaining} 'New Project' drafts still remain!")

    client.close()

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()