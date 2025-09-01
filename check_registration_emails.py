"""
Check if registration emails are being sent properly
"""
import json
from pathlib import Path
from datetime import datetime, timedelta

# Load registrations
REGISTRATIONS_FILE = Path('data/registrations.json')

if REGISTRATIONS_FILE.exists():
    with open(REGISTRATIONS_FILE, 'r') as f:
        registrations = json.load(f)
else:
    registrations = {}

print(f"\n{'='*70}")
print("REGISTRATION EMAIL STATUS CHECK")
print(f"{'='*70}\n")

# Check recent registrations
recent_count = 0
for email, data in registrations.items():
    created_at = data.get('created_at', '')
    if created_at:
        try:
            reg_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            time_diff = datetime.now() - reg_time.replace(tzinfo=None)
            if time_diff < timedelta(days=1):  # Last 24 hours
                recent_count += 1
                print(f"\nRecent Registration: {email}")
                print(f"  Created: {created_at}")
                print(f"  Email Verified: {data.get('email_verified', False)}")
                print(f"  Admin Approved: {data.get('admin_approved', False)}")
                print(f"  Credentials Sent: {data.get('credentials_sent', False)}")
                
                # Check for admin notification markers
                if data.get('approval_token'):
                    print(f"  Has Approval Token: Yes (admin email should have been sent)")
                else:
                    print(f"  Has Approval Token: No")
        except Exception as e:
            pass

if recent_count == 0:
    print("No registrations in the last 24 hours")

print(f"\n{'='*70}")
print("EMAIL SENDING CHECKLIST:")
print(f"{'='*70}")
print("\n1. Check email_config.py:")
print("   - SENDER_EMAIL = atlasnexushelp@gmail.com")
print("   - SENDER_PASSWORD = [App Password configured]")
print("   - ADMIN_EMAIL = atlasnexushelp@gmail.com")

print("\n2. When a user registers, TWO emails should be sent:")
print("   a) Verification email to the USER")
print("   b) Admin notification to atlasnexushelp@gmail.com")

print("\n3. Check these locations in Gmail:")
print("   - Primary inbox")
print("   - Promotions tab")
print("   - Spam folder")
print("   - All Mail")

print("\n4. Search Gmail for:")
print('   - Subject: "New Registration - Action Required"')
print('   - From: atlasnexushelp@gmail.com')

print("\n5. If emails are not arriving:")
print("   - Run: python test_email.py (to verify email config)")
print("   - Check Flask console for [EMAIL] logs when registering")
print("   - Ensure 2FA is enabled on Gmail account")
print("   - Verify App Password is correct (no spaces)")

print(f"\n{'='*70}")
print("RECOMMENDATION:")
print(f"{'='*70}")
print("\nTo properly test if admin emails are being sent:")
print("1. Monitor the Flask console output")
print("2. Register a new test user")
print("3. Look for these log lines:")
print('   [REGISTRATION] Sending admin notification for...')
print('   [EMAIL SUCCESS] ✅ Sent to atlasnexushelp@gmail.com...')
print("\nIf you see these logs but no email arrives, check Gmail spam/filters.")
print(f"\n{'='*70}\n")