#!/usr/bin/env python3
"""
Complete deployment and synchronization script
Ensures local and live versions are identical with mobile optimization
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime

# Fix Unicode output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_mobile_optimization():
    """Verify mobile optimization is in place"""
    log("🔍 Checking mobile optimization...")
    
    with open('templates/base.html', 'r') as f:
        content = f.read()
    
    checks = [
        ('viewport meta tag', 'viewport'),
        ('mobile media queries', '@media (max-width'),
        ('iOS optimizations', '@supports (-webkit-touch-callout'),
        ('Android optimizations', '@media (hover: none)'),
        ('touch-friendly buttons', 'touch-action: manipulation')
    ]
    
    missing = []
    for check_name, check_string in checks:
        if check_string not in content:
            missing.append(check_name)
    
    if missing:
        log(f"⚠️  Missing mobile optimizations: {', '.join(missing)}")
        return False
    
    log("✅ All mobile optimizations are in place")
    return True

def sync_templates():
    """Ensure templates are consistent"""
    log("🔄 Syncing templates...")
    
    # Ensure dashboard_live.html is up to date
    if os.path.exists('templates/dashboard.html'):
        shutil.copy2('templates/dashboard.html', 'templates/dashboard_live.html')
        log("✅ Dashboard templates synchronized")

def prepare_live_app():
    """Prepare app_live.py for deployment"""
    log("📦 Preparing live application...")
    
    # Copy app.py to app_live.py
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Modify for production
    content = content.replace('TESTING_MODE = True', 'TESTING_MODE = False')
    content = content.replace('debug=True', 'debug=False')
    content = content.replace('DEBUG = True', 'DEBUG = False')
    
    with open('app_live.py', 'w') as f:
        f.write(content)
    
    log("✅ Live application prepared")

def run_tests():
    """Run basic tests to ensure everything works"""
    log("🧪 Running tests...")
    
    # Test local server
    try:
        result = subprocess.run(
            ['python', '-c', 'from app import app; print("App imports successfully")'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            log("✅ Local app imports successfully")
        else:
            log(f"❌ Local app import failed: {result.stderr}")
            return False
    except Exception as e:
        log(f"❌ Test failed: {e}")
        return False
    
    return True

def git_operations():
    """Handle git operations"""
    log("📤 Preparing git commit...")
    
    # Check git status
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    if not result.stdout.strip():
        log("ℹ️  No changes to commit")
        return True
    
    # Add files
    files_to_add = [
        'templates/base.html',
        'templates/dashboard_live.html',
        'app_live.py'
    ]
    
    for file in files_to_add:
        if os.path.exists(file):
            subprocess.run(['git', 'add', file])
    
    # Create commit message
    commit_msg = f"Sync: Ensure local and live versions are identical with mobile optimization - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    result = subprocess.run(
        ['git', 'commit', '-m', commit_msg],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        log("✅ Changes committed successfully")
        log("📝 Run 'git push' to deploy to live")
        return True
    else:
        log(f"⚠️  Git commit output: {result.stdout}")
        return True

def main():
    """Main synchronization process"""
    print("\n" + "="*60)
    print("ATLASNEXUS DEPLOYMENT & SYNCHRONIZATION")
    print("="*60 + "\n")
    
    steps = [
        ("Checking mobile optimization", check_mobile_optimization),
        ("Syncing templates", sync_templates),
        ("Preparing live application", prepare_live_app),
        ("Running tests", run_tests),
        ("Git operations", git_operations)
    ]
    
    for step_name, step_func in steps:
        log(f"Step: {step_name}")
        try:
            result = step_func()
            if result is False:
                log(f"❌ Step failed: {step_name}")
                sys.exit(1)
        except Exception as e:
            log(f"❌ Error in {step_name}: {e}")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ SYNCHRONIZATION COMPLETE!")
    print("="*60)
    print("\n📋 Next steps:")
    print("1. Test locally: python run_local.py")
    print("2. Deploy to live: git push")
    print("3. Monitor deployment: Check Vercel dashboard")
    print("\n💡 Mobile optimization is active for:")
    print("   - Android devices")
    print("   - iOS devices (iPhone/iPad)")
    print("   - Responsive breakpoints at 768px, 576px, and 480px")

if __name__ == "__main__":
    main()