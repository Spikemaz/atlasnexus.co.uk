"""
CHECK WHAT'S IN TRASH VS PROJECTS IN MONGODB
"""

from pymongo import MongoClient

# MongoDB URI from .env.local
MONGODB_URI = 'mongodb+srv://marcusbmoore1992_db_user:w6SbBmfO0MQhbXud@cluster0.oduikdo.mongodb.net/atlasnexus?retryWrites=true&w=majority&appName=Cluster0'

print('CHECKING TRASH AND PROJECTS IN MONGODB')
print('=' * 70)

# Connect to MongoDB
client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
client.server_info()
print('[OK] Connected to MongoDB!')

db = client.atlasnexus

# Check projects collection
print('\n[1] PROJECTS COLLECTION:')
print('-' * 40)
for doc in db.projects.find():
    user = doc.get('user_email', 'Unknown')
    projects = doc.get('projects', [])
    print(f'\n   User: {user}')
    print(f'   Total projects: {len(projects)}')
    if projects:
        for i, p in enumerate(projects[:5], 1):  # Show first 5
            title = p.get('title', 'No title')
            status = p.get('status', 'No status')
            proj_id = p.get('id', p.get('projectId', 'No ID'))
            print(f'      {i}. "{title}" (status: {status}, id: {proj_id[:20] if proj_id else "None"}...)')

# Check trash collection
print('\n[2] TRASH COLLECTION:')
print('-' * 40)
trash_count = 0
for doc in db.trash.find():
    trash_count += 1
    print(f'\n   Trash Item #{trash_count}:')
    print(f'   ID: {doc.get("_id")}')
    print(f'   Original Owner: {doc.get("original_owner", "Unknown")}')
    print(f'   Deleted By: {doc.get("deleted_by", "Unknown")}')
    print(f'   Deleted At: {doc.get("deleted_at", "Unknown")}')

    project_data = doc.get('project_data', {})
    if project_data:
        print(f'   Project Title: {project_data.get("title", "No title")}')
        print(f'   Project ID: {project_data.get("id", "No ID")}')

if trash_count == 0:
    print('   [EMPTY] No items in trash')

client.close()

print('\n' + '=' * 70)
print('CHECK COMPLETE')
print('=' * 70)