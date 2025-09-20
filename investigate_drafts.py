#!/usr/bin/env python3
"""
Comprehensive investigation of the 13 draft projects issue
"""
import os
import json
from pathlib import Path

def main():
    print("=" * 70)
    print("INVESTIGATING THE 13 DRAFT PROJECTS ISSUE")
    print("=" * 70)

    # 1. Check undefined variables issue
    print("\n1. CHECKING UNDEFINED VARIABLES:")
    print("-" * 40)
    try:
        exec("print('PROJECT_SPECS_FILE:', PROJECT_SPECS_FILE)")
    except NameError as e:
        print(f"[X] {e}")

    try:
        exec("print('PROJECT_DRAFTS_FILE:', PROJECT_DRAFTS_FILE)")
    except NameError as e:
        print(f"[X] {e}")

    # 2. Check local data files
    print("\n2. CHECKING LOCAL DATA FILES:")
    print("-" * 40)
    data_dir = Path('data')
    if data_dir.exists():
        for json_file in data_dir.glob('*.json'):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        print(f"[F] {json_file.name}: {len(data)} items")
                        # Check for projects with draft in title
                        if 'projects' in json_file.name.lower():
                            for user, user_data in data.items():
                                if isinstance(user_data, dict) and 'projects' in user_data:
                                    projects = user_data['projects']
                                    drafts = [p for p in projects if 'draft' in str(p.get('title', '')).lower()]
                                    if drafts:
                                        print(f"  -> {user}: {len(drafts)} drafts")
                    elif isinstance(data, list):
                        print(f"[F] {json_file.name}: {len(data)} items (list)")
            except Exception as e:
                print(f"[F] {json_file.name}: Error - {e}")
    else:
        print("[F] No data directory found")

    # 3. Check current directory for project files
    print("\n3. CHECKING ROOT DIRECTORY FILES:")
    print("-" * 40)
    for json_file in Path('.').glob('*.json'):
        if json_file.name not in ['vercel.json']:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    print(f"[J] {json_file.name}: {type(data).__name__}")
                    if isinstance(data, dict) and any('draft' in str(v).lower() for v in data.values() if isinstance(v, str)):
                        print(f"  -> Contains 'draft' text")
            except Exception as e:
                print(f"[J] {json_file.name}: Error - {e}")

    # 4. Check cloud database connection
    print("\n4. CHECKING CLOUD DATABASE:")
    print("-" * 40)
    try:
        from cloud_database import cloud_db
        print(f"Connected: {cloud_db.connected if cloud_db else False}")
        if cloud_db and cloud_db.connected:
            print("MongoDB is connected - checking for drafts...")
            projects = cloud_db.load_projects()
            total_drafts = 0
            for user, data in projects.items():
                user_projects = data.get('projects', [])
                drafts = [p for p in user_projects if 'draft' in str(p.get('title', '')).lower()]
                if drafts:
                    print(f"  [U] {user}: {len(drafts)} drafts")
                    total_drafts += len(drafts)
                    for draft in drafts[:3]:  # Show first 3
                        print(f"    -> {draft.get('title', 'Untitled')}")
            print(f"[T] Total drafts found: {total_drafts}")
        else:
            print("Not connected to MongoDB")
    except Exception as e:
        print(f"Error checking cloud DB: {e}")

    # 5. Code analysis findings
    print("\n5. CODE ANALYSIS FINDINGS:")
    print("-" * 40)
    print("[X] PROJECT_SPECS_FILE and PROJECT_DRAFTS_FILE are undefined variables")
    print("[X] This causes NameError when draft-related code tries to run")
    print("[X] The undefined variables affect project specifications system")
    print("[O] Main project creation defaults status='draft' (not title)")
    print("[O] Draft detection looks for 'draft' in project title (case-insensitive)")

    # 6. Recommendations
    print("\n6. RECOMMENDATIONS:")
    print("-" * 40)
    print("[1] FIX 1: Define missing variables in app.py:")
    print("   PROJECT_SPECS_FILE = DATA_DIR / 'project_specs.json'")
    print("   PROJECT_DRAFTS_FILE = DATA_DIR / 'project_drafts.json'")
    print("")
    print("[2] FIX 2: Connect to MongoDB to see actual draft data:")
    print("   - Set MONGODB_URI environment variable")
    print("   - Or create mongodb_uri.txt file")
    print("")
    print("[3] FIX 3: After connecting, run clean_mongodb_drafts.py")
    print("   - This will remove projects with 'draft' in title")
    print("")
    print("[4] FIX 4: Add logging to project creation to track source:")
    print("   - Log where projects with 'draft' in title come from")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()