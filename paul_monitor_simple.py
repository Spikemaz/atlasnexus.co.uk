"""
Paul Developer AI - Live Monitoring Dashboard (Simple Version)
Shows real-time status of what Paul is doing
"""

import os
import json
import time
import requests
from datetime import datetime
import sys

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def check_site_status():
    """Check if the site is up"""
    try:
        response = requests.get('https://atlasnexus.co.uk', timeout=5)
        return response.status_code
    except:
        return 'ERROR'

def read_paul_status():
    """Read Paul's current status from communication files"""
    status = {
        'last_message': None,
        'last_action': None,
        'timestamp': None
    }

    # Check Paul to Claude communication
    try:
        with open('paul_to_claude.json', 'r') as f:
            data = json.load(f)
            status['last_message'] = data.get('data', {}).get('message', 'No message')
            status['last_action'] = data.get('type', 'Unknown')
            status['timestamp'] = data.get('timestamp', 'Unknown')
    except:
        pass

    return status

def read_log_tail(logfile, lines=10):
    """Read the last N lines from a log file"""
    try:
        with open(logfile, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            return all_lines[-lines:] if len(all_lines) > lines else all_lines
    except:
        return []

def display_dashboard():
    """Display the monitoring dashboard"""
    clear_screen()

    # Header
    print("=" * 60)
    print(" PAUL DEVELOPER AI - LIVE MONITOR")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Site Status
    status_code = check_site_status()
    if status_code == 200:
        print(f"[OK] SITE STATUS: {status_code} - All Good!")
    elif status_code == 'ERROR':
        print(f"[ERROR] SITE STATUS: Connection Error")
    else:
        print(f"[WARNING] SITE STATUS: {status_code} - Issue Detected")

    print("-" * 60)

    # Paul's Last Communication
    paul_status = read_paul_status()
    print("PAUL'S LAST MESSAGE:")
    print(f"  Time: {paul_status['timestamp']}")
    print(f"  Type: {paul_status['last_action']}")
    print(f"  Message: {paul_status['last_message']}")

    print("-" * 60)

    # Recent Log Activity
    print("RECENT PAUL ACTIVITY:")

    # Try to read Paul's log
    log_lines = read_log_tail('paul_developer.log', 5)
    if log_lines:
        for line in log_lines:
            line = line.strip()
            if line:
                # Truncate long lines
                if len(line) > 75:
                    print(f"  {line[:75]}...")
                else:
                    print(f"  {line}")
    else:
        print("  No recent log entries")

    print("-" * 60)

    # Claude to Paul Messages
    try:
        with open('claude_to_paul.json', 'r') as f:
            claude_msg = json.load(f)
            print("CLAUDE'S LAST INSTRUCTION:")
            print(f"  Type: {claude_msg.get('type', 'Unknown')}")
            print(f"  Message: {claude_msg.get('data', {}).get('message', 'None')}")
    except:
        print("CLAUDE'S LAST INSTRUCTION: None")

    print("=" * 60)
    print("Press Ctrl+C to exit | Refreshing every 3 seconds...")

def main():
    """Main monitoring loop"""
    print("Starting Paul Monitor Dashboard...")
    print("Loading...")

    try:
        while True:
            display_dashboard()
            time.sleep(3)  # Refresh every 3 seconds
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()