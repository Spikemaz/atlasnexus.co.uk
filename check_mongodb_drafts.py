"""
Check MongoDB for draft projects
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
    print("CHECKING MONGODB FOR DRAFTS")
    print("=" * 70)

    # Check projects collection
    print("\n📁 Projects Collection:")
    projects = db.projects.find()

    for proj_doc in projects:
        user_email = proj_doc.get('user_email', 'Unknown')
        print(f"\n👤 User: {user_email}")

        # Check for drafts in projects array
        projects_list = proj_doc.get('projects', [])
        draft_count = 0

        for project in projects_list:
            if 'draft' in str(project.get('title', '')).lower():
                draft_count += 1
                print(f"  📝 Draft found: {project.get('title')} (ID: {project.get('id')})")

        print(f"  Total projects: {len(projects_list)}, Drafts: {draft_count}")

    # Check trash collection
    print("\n🗑️ Trash Collection:")
    trash_items = db.trash.find()
    trash_count = 0

    for item in trash_items:
        trash_count += 1
        project_data = item.get('project_data', {})
        title = project_data.get('title', 'Unknown')
        deleted_by = item.get('deleted_by', 'Unknown')
        deleted_at = item.get('deleted_at', 'Unknown')
        print(f"  🗑️ {title} - deleted by {deleted_by} at {deleted_at}")

    print(f"\nTotal items in trash: {trash_count}")

    print("\n" + "=" * 70)

    # Ask if we should clean drafts
    response = input("\n⚠️ Do you want to PERMANENTLY DELETE all drafts from MongoDB? (yes/no): ")

    if response.lower() == 'yes':
        for proj_doc in db.projects.find():
            user_email = proj_doc.get('user_email')
            projects_list = proj_doc.get('projects', [])

            # Filter out drafts
            non_drafts = [p for p in projects_list if 'draft' not in str(p.get('title', '')).lower()]

            if len(non_drafts) < len(projects_list):
                print(f"\n🧹 Removing {len(projects_list) - len(non_drafts)} drafts for {user_email}")

                # Update the document
                proj_doc['projects'] = non_drafts
                db.projects.update_one(
                    {'user_email': user_email},
                    {'$set': {'projects': non_drafts}}
                )

        print("\n✅ Drafts cleaned from MongoDB!")
    else:
        print("\n❌ No changes made")

    client.close()

except Exception as e:
    print(f"Error: {e}")