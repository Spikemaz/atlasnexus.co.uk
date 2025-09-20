"""
Claude Fix Monitor - Watches for Paul's fix requests and creates response files
This helps demonstrate the collaboration loop between Claude and Paul
"""

import json
import os
import time
from datetime import datetime

def check_paul_requests():
    """Check if Paul has sent any fix requests"""
    try:
        if os.path.exists('paul_to_claude.json'):
            with open('paul_to_claude.json', 'r') as f:
                data = json.load(f)

            if data.get('type') == 'FIX_REQUEST':
                return data
    except:
        pass
    return None

def create_fix_response(request):
    """Create a response for Paul's fix request"""
    failures = request.get('failures', [])

    # Analyze the failures and create fix plan
    fix_plan = {
        "type": "FIX_RESPONSE",
        "from": "CLAUDE",
        "timestamp": datetime.now().isoformat(),
        "message": f"Received fix request for: {', '.join(failures)}. Analyzing and fixing...",
        "action": "fixing",
        "fixes": []
    }

    # Analyze each failure
    for failure in failures:
        if "Projects tab missing" in failure:
            fix_plan["fixes"].append({
                "issue": "Projects tab missing",
                "diagnosis": "The Projects & Trash tab text might not be visible without authentication",
                "solution": "Testing requires admin authentication to see the tab",
                "status": "needs_auth_test"
            })

    # Write response
    with open('claude_to_paul.json', 'w') as f:
        json.dump(fix_plan, f, indent=2)

    print(f"[CLAUDE MONITOR] Fix response sent to Paul for: {', '.join(failures)}")

    # Log to Paul's log
    with open('paul_developer.log', 'a') as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CLAUDE: Analyzing failures: {', '.join(failures)}\n")
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CLAUDE: Fix plan created and sent to Paul\n")

def main():
    print("=" * 70)
    print("CLAUDE FIX MONITOR")
    print("Watching for Paul's fix requests...")
    print("=" * 70)

    last_request = None

    while True:
        try:
            request = check_paul_requests()

            if request and request != last_request:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] New fix request from Paul!")
                print(f"Failures: {request.get('failures', [])}")

                # Create fix response
                create_fix_response(request)
                last_request = request

                # Clear Paul's request file
                with open('paul_to_claude.json', 'w') as f:
                    json.dump({"processed": True}, f)

            time.sleep(5)  # Check every 5 seconds

        except KeyboardInterrupt:
            print("\nClaude Fix Monitor stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()