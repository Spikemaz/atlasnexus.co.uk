"""
INSPECT WHAT'S IN MONGODB
"""

from pymongo import MongoClient

# Direct connection to MongoDB
MONGODB_URI = "mongodb+srv://marcusbmoore1992_db_user:w6SbBmfO0MQhbXud@cluster0.oduikdo.mongodb.net/atlasnexus?retryWrites=true&w=majority&appName=Cluster0"

print("INSPECTING MONGODB PROJECTS")
print("=" * 70)

try:
    # Connect
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    print("Connected to MongoDB!")

    db = client.atlasnexus

    # Get all projects
    print("\n=== ALL PROJECTS IN DATABASE ===")

    for doc in db.projects.find():
        user = doc.get('user_email', 'Unknown')
        projects = doc.get('projects', [])

        print(f"\nUser: {user}")
        print(f"Total projects: {len(projects)}")

        # Show first 5 projects for this user
        for i, p in enumerate(projects[:20]):  # Show up to 20 projects
            title = p.get('title', 'No title')
            project_id = p.get('id', p.get('projectId', 'No ID'))
            status = p.get('status', 'Unknown')
            print(f"  {i+1}. Title: '{title}' | Status: {status} | ID: {project_id[:20] if project_id else 'None'}...")

    client.close()

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()