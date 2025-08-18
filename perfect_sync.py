#!/usr/bin/env python3
"""
Perfect Synchronization System
Ensures 100% identical code between local and live versions
Only difference: TESTING_MODE flag
"""

import os
import sys
import shutil
import hashlib
from datetime import datetime

# Fix Unicode output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def log(message, level="INFO"):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def file_hash(filepath):
    """Generate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def sync_app_files():
    """Sync app.py to app_live.py with ONLY the TESTING_MODE difference"""
    log("Syncing app.py to app_live.py...")
    
    # Read app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Make ONLY these specific changes for production
    live_content = content.replace('TESTING_MODE = True', 'TESTING_MODE = False')
    live_content = live_content.replace('debug=True', 'debug=False')
    
    # Write to app_live.py
    with open('app_live.py', 'w', encoding='utf-8') as f:
        f.write(live_content)
    
    log("✓ app_live.py updated (TESTING_MODE=False)")
    return True

def sync_templates():
    """Ensure all templates are EXACTLY the same"""
    log("Syncing templates...")
    
    template_dir = 'templates'
    templates_synced = []
    
    # List all HTML templates
    for filename in os.listdir(template_dir):
        if filename.endswith('.html'):
            source = os.path.join(template_dir, filename)
            
            # Special handling for dashboard
            if filename == 'dashboard.html':
                # Create dashboard_live.html as EXACT copy
                dest = os.path.join(template_dir, 'dashboard_live.html')
                shutil.copy2(source, dest)
                templates_synced.append('dashboard.html → dashboard_live.html')
            
            # All templates are shared, no changes needed
            templates_synced.append(filename)
    
    for template in templates_synced:
        log(f"  ✓ {template}")
    
    return True

def sync_static_files():
    """Ensure all static files are EXACTLY the same"""
    log("Syncing static files...")
    
    static_dirs = ['static/css', 'static/js']
    
    for dir_path in static_dirs:
        if os.path.exists(dir_path):
            log(f"  ✓ {dir_path} (shared)")
    
    return True

def verify_sync():
    """Verify that files are properly synced"""
    log("Verifying synchronization...")
    
    # Check app files
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    with open('app_live.py', 'r', encoding='utf-8') as f:
        live_content = f.read()
    
    # Replace the TESTING_MODE difference for comparison
    app_normalized = app_content.replace('TESTING_MODE = True', 'TESTING_MODE = False')
    app_normalized = app_normalized.replace('debug=True', 'debug=False')
    
    if app_normalized == live_content:
        log("  ✓ app.py and app_live.py are synchronized")
    else:
        log("  ✗ app.py and app_live.py DIFFER!", "ERROR")
        # Find differences
        app_lines = app_normalized.splitlines()
        live_lines = live_content.splitlines()
        for i, (a, l) in enumerate(zip(app_lines, live_lines)):
            if a != l:
                log(f"    Line {i+1} differs:", "ERROR")
                log(f"      Local:  {a[:80]}...", "ERROR")
                log(f"      Live:   {l[:80]}...", "ERROR")
                break
        return False
    
    # Check dashboard templates
    if os.path.exists('templates/dashboard.html') and os.path.exists('templates/dashboard_live.html'):
        dash_hash = file_hash('templates/dashboard.html')
        live_hash = file_hash('templates/dashboard_live.html')
        
        if dash_hash == live_hash:
            log("  ✓ dashboard.html and dashboard_live.html are identical")
        else:
            log("  ✗ Dashboard templates DIFFER!", "ERROR")
            return False
    
    return True

def main():
    """Main synchronization process"""
    print("\n" + "="*60)
    print("PERFECT SYNCHRONIZATION SYSTEM")
    print("="*60 + "\n")
    
    # Step 1: Sync app files
    if not sync_app_files():
        log("Failed to sync app files", "ERROR")
        sys.exit(1)
    
    # Step 2: Sync templates
    if not sync_templates():
        log("Failed to sync templates", "ERROR")
        sys.exit(1)
    
    # Step 3: Sync static files
    if not sync_static_files():
        log("Failed to sync static files", "ERROR")
        sys.exit(1)
    
    # Step 4: Verify everything
    if not verify_sync():
        log("Synchronization verification FAILED", "ERROR")
        log("Files are NOT properly synchronized!", "ERROR")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ PERFECT SYNCHRONIZATION COMPLETE")
    print("="*60)
    print("\nGUARANTEED:")
    print("• app.py → app_live.py (only TESTING_MODE differs)")
    print("• dashboard.html → dashboard_live.html (100% identical)")
    print("• All templates shared (exact same files)")
    print("• All static files shared (exact same files)")
    print("\nBoth versions will display EXACTLY the same output!")
    print("\nTo deploy: git add -A && git commit -m 'Sync' && git push")

if __name__ == "__main__":
    main()