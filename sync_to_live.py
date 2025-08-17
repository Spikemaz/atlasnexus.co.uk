#!/usr/bin/env python3
"""
Sync local development to live version
This script updates app_live.py with routes from app.py while maintaining security settings
"""

import re
import os

def sync_apps():
    """Sync app.py routes to app_live.py while keeping security settings"""
    
    print("🔄 Syncing local app.py to app_live.py...")
    
    # Read app.py
    with open('app.py', 'r') as f:
        local_content = f.read()
    
    # Read app_live.py
    with open('app_live.py', 'r') as f:
        live_content = f.read()
    
    # Extract all route definitions from app.py
    route_pattern = r'(@app\.route.*?)(?=@app\.route|if __name__|$)'
    local_routes = re.findall(route_pattern, local_content, re.DOTALL)
    
    # Routes to exclude from sync (security-specific)
    exclude_routes = ['/auth', '/site-auth', '/secure-login', '/secure-login-submit']
    
    # Process each route
    updated_count = 0
    for route in local_routes:
        # Extract route path
        route_match = re.search(r"@app\.route\('([^']+)'", route)
        if route_match:
            route_path = route_match.group(1)
            
            # Skip excluded routes
            if route_path in exclude_routes:
                continue
            
            # Check if route exists in live
            if route_path not in live_content:
                print(f"  ✅ Adding route: {route_path}")
                # Add the route before the error handlers
                live_content = live_content.replace(
                    "# Error handlers",
                    f"{route}\n# Error handlers"
                )
                updated_count += 1
    
    # Update TESTING_MODE to False for live
    live_content = re.sub(
        r'TESTING_MODE = True',
        'TESTING_MODE = False',
        live_content
    )
    
    # Write updated app_live.py
    with open('app_live.py', 'w') as f:
        f.write(live_content)
    
    print(f"✅ Sync complete! Updated {updated_count} routes.")
    print("📝 Remember: app_live.py keeps TESTING_MODE = False for security")
    print("📝 Templates are shared between both versions")
    
    # Git add and commit
    os.system('git add app_live.py')
    os.system('git commit -m "Sync app_live.py with local development"')
    print("✅ Changes committed. Run 'git push' to deploy.")

if __name__ == "__main__":
    sync_apps()