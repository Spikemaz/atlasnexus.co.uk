#!/usr/bin/env python3
"""
Automatic sync from local to live
Watches for changes and updates app_live.py automatically
"""

import os
import time
import shutil
from datetime import datetime
import subprocess
import sys

# Fix Unicode output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def sync_files():
    """Sync app.py to app_live.py with production settings"""
    log("🔄 Syncing local to live...")
    
    # Read app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Modify for production
    content = content.replace('TESTING_MODE = True', 'TESTING_MODE = False')
    content = content.replace('debug=True', 'debug=False')
    content = content.replace('DEBUG = True', 'DEBUG = False')
    
    # Write to app_live.py
    with open('app_live.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    log("✅ app_live.py updated")
    
    # Copy dashboard templates if they exist
    templates_to_sync = [
        'dashboard.html',
        'dashboard_live.html',
        'base.html'
    ]
    
    for template in templates_to_sync:
        src = f'templates/{template}'
        if os.path.exists(src):
            # For dashboard.html, also create dashboard_live.html
            if template == 'dashboard.html':
                dst = 'templates/dashboard_live.html'
                shutil.copy2(src, dst)
                log(f"✅ Synced {template} to dashboard_live.html")
    
    return True

def git_commit_and_push():
    """Commit and push changes"""
    try:
        # Check if there are changes
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if not result.stdout.strip():
            return False
        
        # Add files
        subprocess.run(['git', 'add', 'app_live.py', 'templates/dashboard_live.html'])
        
        # Commit
        commit_msg = f"Auto-sync: Local to live - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(['git', 'commit', '-m', commit_msg], capture_output=True)
        
        log("📤 Changes committed")
        
        # Push (optional - uncomment if you want automatic push)
        # subprocess.run(['git', 'push'], capture_output=True)
        # log("☁️ Pushed to remote")
        
        return True
    except Exception as e:
        log(f"⚠️ Git operations failed: {e}")
        return False

def watch_and_sync():
    """Watch for changes and sync automatically"""
    log("👀 Watching for changes...")
    log("Press Ctrl+C to stop")
    
    last_modified = {}
    watch_files = ['app.py', 'templates/dashboard.html', 'templates/base.html']
    
    # Initial sync
    sync_files()
    
    while True:
        try:
            changed = False
            
            for file_path in watch_files:
                if os.path.exists(file_path):
                    mtime = os.path.getmtime(file_path)
                    
                    if file_path not in last_modified:
                        last_modified[file_path] = mtime
                    elif mtime > last_modified[file_path]:
                        log(f"📝 Change detected in {file_path}")
                        last_modified[file_path] = mtime
                        changed = True
            
            if changed:
                sync_files()
                git_commit_and_push()
            
            time.sleep(2)  # Check every 2 seconds
            
        except KeyboardInterrupt:
            log("\n🛑 Stopping auto-sync")
            break
        except Exception as e:
            log(f"❌ Error: {e}")
            time.sleep(5)

def main():
    """Main function"""
    print("\n" + "="*60)
    print("AUTO-SYNC: LOCAL TO LIVE")
    print("="*60 + "\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Run sync once
        sync_files()
        git_commit_and_push()
        log("✅ One-time sync complete")
    else:
        # Watch mode
        watch_and_sync()

if __name__ == "__main__":
    main()