"""
FINAL CLEANUP - DELETE ALL DRAFTS AND EMPTY TRASH
"""

from pymongo import MongoClient
from bson import ObjectId

# MongoDB URI from .env.local
MONGODB_URI = 'mongodb+srv://marcusbmoore1992_db_user:w6SbBmfO0MQhbXud@cluster0.oduikdo.mongodb.net/atlasnexus?retryWrites=true&w=majority&appName=Cluster0'

print('FINAL CLEANUP - REMOVING ALL DRAFTS AND TRASH')
print('=' * 70)

# Connect to MongoDB
client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
client.server_info()
print('[OK] Connected to MongoDB!')

db = client.atlasnexus

# 1. Clean projects collection
print('\n[1] CLEANING PROJECTS COLLECTION:')
print('-' * 40)
total_removed = 0
for doc in db.projects.find():
    user = doc.get('user_email', 'Unknown')
    projects = doc.get('projects', [])

    # Remove ALL "New Project" drafts
    clean_projects = [p for p in projects if not (p.get('title') == 'New Project' and p.get('status') == 'draft')]
    removed = len(projects) - len(clean_projects)

    if removed > 0:
        print(f'   Removing {removed} draft(s) from {user}')
        db.projects.update_one(
            {'user_email': user},
            {'$set': {'projects': clean_projects}}
        )
        total_removed += removed

print(f'   [OK] Removed {total_removed} drafts total')

# 2. Empty trash collection
print('\n[2] EMPTYING TRASH COLLECTION:')
print('-' * 40)
trash_count = db.trash.count_documents({})
if trash_count > 0:
    result = db.trash.delete_many({})
    print(f'   [OK] Deleted {result.deleted_count} items from trash')
else:
    print('   [EMPTY] Trash already empty')

# 3. Final verification
print('\n[3] FINAL VERIFICATION:')
print('-' * 40)

# Check projects
draft_count = 0
for doc in db.projects.find():
    user = doc.get('user_email', 'Unknown')
    projects = doc.get('projects', [])
    drafts = [p for p in projects if p.get('title') == 'New Project' and p.get('status') == 'draft']
    draft_count += len(drafts)
    print(f'   {user}: {len(projects)} projects ({len(drafts)} drafts)')

# Check trash
trash_count = db.trash.count_documents({})
print(f'\n   Trash items: {trash_count}')

client.close()

print('\n' + '=' * 70)
if draft_count == 0 and trash_count == 0:
    print('[SUCCESS] Database is completely clean!')
else:
    print(f'[WARNING] Still have {draft_count} drafts and {trash_count} trash items')
print('=' * 70)