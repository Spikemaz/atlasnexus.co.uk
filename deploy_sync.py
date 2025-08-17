#!/usr/bin/env python3
"""
AtlasNexus Deployment Synchronization Script
Ensures local and live versions match with proper security gates
"""

import os
import sys
import shutil
import json
import subprocess
from datetime import datetime
import time

class AtlasNexusDeployment:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.deployment_log = []
        
        # Core passwords and security settings
        self.security_config = {
            'site_passwords': {
                'internal': 'RedAMC',
                'external': 'PartnerAccess'  
            },
            'secret_unlock': 'Ronabambi',
            'admin_credentials': {
                'email': 'marcus@atlasnexus.co.uk',
                'password': 'MarcusAdmin2024'
            },
            'lockout_settings': {
                'max_attempts': 4,
                'lockout_duration_minutes': 45,
                'permanent_lockout_attempts': 5
            }
        }
        
        # GitHub and Vercel settings
        self.github_repo = "https://github.com/Spikemaz/atlasnexus.co.uk.git"
        self.vercel_project = "atlasnexus-securitization"
        self.live_url = "https://www.atlasnexus.co.uk"
        
    def log_action(self, action, status="INFO"):
        """Log deployment actions"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{status}] {action}"
        self.deployment_log.append(log_entry)
        try:
            print(log_entry)
        except UnicodeEncodeError:
            # Fallback for Windows console encoding issues
            print(log_entry.encode('ascii', 'replace').decode('ascii'))
        
    def verify_security_gates(self):
        """Verify all security gate implementations are correct"""
        self.log_action("Verifying security gate implementations...")
        
        all_checks_passed = True
        
        # Check Gate 1 - site_auth.html
        site_auth_path = os.path.join(self.project_root, 'templates', 'site_auth.html')
        if os.path.exists(site_auth_path):
            with open(site_auth_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Verify critical security features
                checks = [
                    ('Coat of arms present', 'coat-of-arms' in content.lower() or 'coat_of_arms' in content.lower()),
                    ('3 attempt warning system', 'attempt === 3' in content or 'attemptCount === 3' in content),
                    ('45-minute lockout timer', '45' in content and ('minute' in content or 'min' in content)),
                    ('Secret unlock password (Ronabambi)', 'Ronabambi' in content),
                    ('Black screen permanent lockout', 'blackscreen' in content.lower() or 'permanentLockout' in content),
                    ('RedAMC password check', 'RedAMC' in content),
                    ('PartnerAccess password check', 'PartnerAccess' in content or 'PartnerPass' in content)
                ]
                
                for check_name, check_result in checks:
                    status = "✓" if check_result else "✗"
                    self.log_action(f"  {status} {check_name}", "SUCCESS" if check_result else "WARNING")
                    if not check_result:
                        all_checks_passed = False
        else:
            self.log_action("  ✗ site_auth.html not found!", "ERROR")
            all_checks_passed = False
            
        # Check Gate 2 - secure_login.html  
        secure_login_path = os.path.join(self.project_root, 'templates', 'secure_login.html')
        if os.path.exists(secure_login_path):
            self.log_action("  ✓ secure_login.html (Gate 2) found", "SUCCESS")
        else:
            self.log_action("  ✗ secure_login.html not found!", "ERROR")
            all_checks_passed = False
            
        # Check Dashboard
        dashboard_path = os.path.join(self.project_root, 'templates', 'dashboard.html')
        if os.path.exists(dashboard_path):
            self.log_action("  ✓ dashboard.html found", "SUCCESS")
        else:
            self.log_action("  ✗ dashboard.html not found!", "ERROR")
            all_checks_passed = False
            
        # Check Admin Panel
        admin_path = os.path.join(self.project_root, 'templates', 'admin_simple.html')
        if os.path.exists(admin_path):
            self.log_action("  ✓ admin_simple.html found", "SUCCESS")
        else:
            self.log_action("  ✗ admin_simple.html not found!", "ERROR")
            all_checks_passed = False
            
        return all_checks_passed
        
    def update_app_vercel(self):
        """Update app_vercel.py with correct security settings"""
        self.log_action("Updating app_vercel.py with security configurations...")
        
        app_path = os.path.join(self.project_root, 'app_vercel.py')
        
        # Read current app_vercel.py
        with open(app_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Update security passwords if needed
        updated = False
        for i, line in enumerate(lines):
            if 'SITE_PASSWORD_INTERNAL' in line and 'RedAMC' not in line:
                lines[i] = 'SITE_PASSWORD_INTERNAL = "RedAMC"\n'
                updated = True
                self.log_action("  Updated internal password to RedAMC")
                
            if 'SITE_PASSWORD_EXTERNAL' in line:
                if 'PartnerAccess' not in line and 'PartnerPass' not in line:
                    lines[i] = 'SITE_PASSWORD_EXTERNAL = "PartnerAccess"\n'
                    updated = True
                    self.log_action("  Updated external password to PartnerAccess")
                
        if updated:
            with open(app_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            self.log_action("  ✓ app_vercel.py updated", "SUCCESS")
        else:
            self.log_action("  ✓ app_vercel.py already configured correctly", "SUCCESS")
            
    def check_git_status(self):
        """Check current Git status"""
        self.log_action("Checking Git status...")
        
        try:
            # Check for uncommitted changes
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            
            if result.stdout:
                self.log_action("  ⚠ Uncommitted changes detected:", "WARNING")
                for line in result.stdout.strip().split('\n'):
                    if line:
                        self.log_action(f"    {line}", "WARNING")
                return False
            else:
                self.log_action("  ✓ Working directory clean", "SUCCESS")
                return True
                
        except Exception as e:
            self.log_action(f"  ✗ Git check failed: {e}", "ERROR")
            return False
            
    def create_deployment_package(self):
        """Verify all necessary files for deployment"""
        self.log_action("Verifying deployment package...")
        
        # Essential files for Vercel deployment
        essential_files = [
            ('app_vercel.py', 'Main Flask application'),
            ('requirements.txt', 'Python dependencies'),
            ('vercel.json', 'Vercel configuration')
        ]
        
        # Essential directories
        essential_dirs = [
            ('templates', 'HTML templates'),
            ('static', 'Static assets (CSS/JS)')
        ]
        
        deployment_ready = True
        
        for file, description in essential_files:
            file_path = os.path.join(self.project_root, file)
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                self.log_action(f"  ✓ {file} - {description} ({size} bytes)", "SUCCESS")
            else:
                self.log_action(f"  ✗ {file} - {description} MISSING!", "ERROR")
                deployment_ready = False
                
        for dir_name, description in essential_dirs:
            dir_path = os.path.join(self.project_root, dir_name)
            if os.path.exists(dir_path):
                file_count = sum([len(files) for _, _, files in os.walk(dir_path)])
                self.log_action(f"  ✓ {dir_name}/ - {description} ({file_count} files)", "SUCCESS")
            else:
                self.log_action(f"  ✗ {dir_name}/ - {description} MISSING!", "ERROR")
                deployment_ready = False
                
        return deployment_ready
        
    def create_local_test_script(self):
        """Create a script to test locally before deployment"""
        self.log_action("Creating local test script...")
        
        test_script = '''#!/usr/bin/env python3
"""Local testing script for AtlasNexus"""

import os
import sys
import webbrowser
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the app
from app_vercel import app

if __name__ == '__main__':
    print("=" * 60)
    print("ATLASNEXUS LOCAL TESTING SERVER")
    print("=" * 60)
    print("\\nSECURITY GATE 1 - Site Access:")
    print("  Internal Access: RedAMC")
    print("  Partner Access: PartnerAccess")
    print("  Secret Unlock: Ronabambi (bottom-left corner, 4 clicks)")
    print("\\nSECURITY GATE 2 - User Login:")
    print("  Admin: marcus@atlasnexus.co.uk")
    print("  Password: MarcusAdmin2024")
    print("=" * 60)
    print("\\nStarting server at: http://localhost:5000")
    print("Opening browser in 3 seconds...")
    print("=" * 60)
    
    # Open browser after short delay
    time.sleep(3)
    webbrowser.open('http://localhost:5000')
    
    # Run Flask app
    app.run(debug=True, host='127.0.0.1', port=5000)
'''
        
        test_path = os.path.join(self.project_root, 'test_local.py')
        with open(test_path, 'w') as f:
            f.write(test_script)
            
        self.log_action(f"  ✓ test_local.py created", "SUCCESS")
        return test_path
        
    def deploy_to_vercel(self, auto_deploy=False):
        """Deploy to Vercel"""
        self.log_action("Preparing Vercel deployment...")
        
        if auto_deploy:
            self.log_action("Auto-deploying to Vercel...")
            try:
                # Deploy to production
                result = subprocess.run(['vercel', '--prod', '--yes'], 
                                      capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode == 0:
                    self.log_action("  ✓ Successfully deployed to Vercel!", "SUCCESS")
                    self.log_action(f"  Live at: {self.live_url}", "SUCCESS")
                else:
                    self.log_action(f"  ✗ Deployment failed: {result.stderr}", "ERROR")
                    
            except FileNotFoundError:
                self.log_action("  ✗ Vercel CLI not found. Install with: npm install -g vercel", "ERROR")
        else:
            self.log_action("\nManual deployment commands:")
            commands = [
                "# Deploy to Vercel production:",
                "vercel --prod",
                "",
                "# Or push to GitHub for auto-deployment:",
                "git add -A",
                'git commit -m "Sync security gates and update deployment"',
                "git push origin main"
            ]
            
            for cmd in commands:
                print(f"  {cmd}")
                
    def save_deployment_log(self):
        """Save deployment log to file"""
        log_file = os.path.join(self.project_root, 'logs', 'deployment_sync.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, 'w') as f:
            f.write('\n'.join(self.deployment_log))
        self.log_action(f"\n✓ Log saved to {log_file}", "SUCCESS")
        
    def run_full_sync(self, start_local=False, auto_deploy=False):
        """Run complete synchronization process"""
        print("=" * 60)
        print("ATLASNEXUS DEPLOYMENT SYNCHRONIZATION")
        print("=" * 60)
        print(f"GitHub Repo: {self.github_repo}")
        print(f"Vercel Project: {self.vercel_project}")
        print(f"Live URL: {self.live_url}")
        print("=" * 60)
        
        # Step 1: Verify security gates
        security_ok = self.verify_security_gates()
        
        # Step 2: Update app configuration
        self.update_app_vercel()
        
        # Step 3: Check Git status
        git_clean = self.check_git_status()
        
        # Step 4: Verify deployment package
        package_ready = self.create_deployment_package()
        
        # Step 5: Create local test script
        test_script = self.create_local_test_script()
        
        # Step 6: Save log
        self.save_deployment_log()
        
        print("\n" + "=" * 60)
        print("SYNCHRONIZATION SUMMARY")
        print("=" * 60)
        
        if security_ok and package_ready:
            print("✓ All security gates verified")
            print("✓ Deployment package ready")
            
            if not git_clean:
                print("⚠ Uncommitted changes need to be committed")
                
            print("\nNEXT STEPS:")
            print("1. Test locally: python test_local.py")
            print("2. Open browser to http://localhost:5000")
            print("3. Deploy to live: vercel --prod")
            print(f"4. Verify live site: {self.live_url}")
            
            if start_local:
                print("\n" + "=" * 60)
                print("Starting local server...")
                os.system('python test_local.py')
                
        else:
            print("✗ Issues detected - review log above")
            
        print("=" * 60)

if __name__ == '__main__':
    deployer = AtlasNexusDeployment()
    
    # Check for command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='AtlasNexus Deployment Sync')
    parser.add_argument('--local', action='store_true', help='Start local server after sync')
    parser.add_argument('--deploy', action='store_true', help='Auto-deploy to Vercel')
    
    args = parser.parse_args()
    
    deployer.run_full_sync(start_local=args.local, auto_deploy=args.deploy)