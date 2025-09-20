"""
Fix the persistent 13 drafts issue by cleaning MongoDB directly
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def connect_to_mongodb():
    """Connect to MongoDB Atlas"""
    uri = os.getenv('MONGODB_URI')
    if not uri:
        print("ERROR: MONGODB_URI not found in environment")
        return None

    try:
        client = MongoClient(uri)
        db = client.atlasnexus
        # Test connection
        client.server_info()
        print("✅ Connected to MongoDB Atlas")
        return db
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return None

def analyze_drafts():
    """Find and analyze all draft projects"""
    db = connect_to_mongodb()
    if not db:
        return

    print("\n=== ANALYZING DRAFT PROJECTS ===")

    # Check projects collection
    total_drafts = 0
    draft_details = []

    try:
        cursor = db.projects.find()

        for doc in cursor:
            user = doc.get('user_email', 'Unknown')
            projects = doc.get('projects', [])

            # Find drafts
            drafts = [p for p in projects if 'draft' in str(p.get('title', '')).lower()]

            if drafts:
                print(f"\n📧 User: {user}")
                print(f"   Total projects: {len(projects)}")
                print(f"   Draft projects: {len(drafts)}")

                for draft in drafts[:3]:  # Show first 3 drafts
                    print(f"   - {draft.get('title', 'No title')} (ID: {draft.get('id', 'No ID')[:8]}...)")

                total_drafts += len(drafts)
                draft_details.append({
                    'user': user,
                    'draft_count': len(drafts),
                    'drafts': drafts
                })

        print(f"\n🔍 TOTAL DRAFTS FOUND: {total_drafts}")

        # If we found exactly 13 drafts, they might be from the same user
        if total_drafts == 13:
            print("\n⚠️ Found exactly 13 drafts - checking if they're from same source...")
            for detail in draft_details:
                if detail['draft_count'] == 13:
                    print(f"   ✓ All 13 drafts belong to: {detail['user']}")
                    print("   Draft titles:")
                    for draft in detail['drafts']:
                        print(f"     - {draft.get('title', 'No title')}")

        return draft_details

    except Exception as e:
        print(f"Error analyzing drafts: {e}")
        return []

def clean_all_drafts():
    """Remove all draft projects from MongoDB"""
    db = connect_to_mongodb()
    if not db:
        return

    print("\n=== CLEANING ALL DRAFTS ===")

    total_removed = 0

    try:
        cursor = db.projects.find()

        for doc in cursor:
            user = doc.get('user_email', 'Unknown')
            projects = doc.get('projects', [])

            # Filter out drafts
            non_drafts = [p for p in projects if 'draft' not in str(p.get('title', '')).lower()]
            drafts_removed = len(projects) - len(non_drafts)

            if drafts_removed > 0:
                print(f"Removing {drafts_removed} drafts from {user}")

                # Update the document
                db.projects.update_one(
                    {'user_email': user},
                    {'$set': {'projects': non_drafts}}
                )

                total_removed += drafts_removed

        print(f"\n✅ Successfully removed {total_removed} drafts from MongoDB")

    except Exception as e:
        print(f"❌ Error cleaning drafts: {e}")

def check_trash_for_drafts():
    """Check if drafts exist in trash collection"""
    db = connect_to_mongodb()
    if not db:
        return

    print("\n=== CHECKING TRASH FOR DRAFTS ===")

    try:
        trash_cursor = db.trash.find()

        for doc in trash_cursor:
            user = doc.get('user_email', 'Unknown')
            items = doc.get('items', [])

            # Find draft items
            draft_items = [item for item in items if 'draft' in str(item.get('title', '')).lower()]

            if draft_items:
                print(f"\n📧 User: {user}")
                print(f"   Draft items in trash: {len(draft_items)}")
                for item in draft_items[:3]:
                    print(f"   - {item.get('title', 'No title')}")

    except Exception as e:
        print(f"Error checking trash: {e}")

def main():
    """Main function"""
    print("=" * 70)
    print("DRAFT PERSISTENCE FIX TOOL")
    print("=" * 70)

    # First analyze what's there
    draft_details = analyze_drafts()

    # Check trash too
    check_trash_for_drafts()

    # Ask user if they want to clean
    if draft_details:
        response = input("\n🗑️ Do you want to remove all drafts? (yes/no): ")
        if response.lower() == 'yes':
            clean_all_drafts()

            # Verify they're gone
            print("\n=== VERIFICATION ===")
            remaining = analyze_drafts()
            if not remaining or sum(d['draft_count'] for d in remaining) == 0:
                print("✅ All drafts successfully removed!")
            else:
                print("⚠️ Some drafts still remain")
    else:
        print("\n✅ No drafts found in MongoDB")

if __name__ == "__main__":
    main()