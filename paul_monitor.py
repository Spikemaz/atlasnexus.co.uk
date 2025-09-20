"""
Paul Developer AI - Live Monitoring Dashboard
Shows real-time status of what Paul is doing
"""

import os
import json
import time
import requests
from datetime import datetime
from colorama import init, Fore, Back, Style
import sys

# Initialize colorama for Windows color support
init()

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
    print(f"{Back.BLUE}{Fore.WHITE} PAUL DEVELOPER AI - LIVE MONITOR {Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Site Status
    status_code = check_site_status()
    if status_code == 200:
        print(f"{Fore.GREEN}✓ SITE STATUS: {status_code} - All Good!{Style.RESET_ALL}")
    elif status_code == 'ERROR':
        print(f"{Fore.RED}✗ SITE STATUS: Connection Error{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠ SITE STATUS: {status_code} - Issue Detected{Style.RESET_ALL}")

    print(f"{Fore.CYAN}{'-'*60}{Style.RESET_ALL}")

    # Paul's Last Communication
    paul_status = read_paul_status()
    print(f"{Fore.YELLOW}📨 PAUL'S LAST MESSAGE:{Style.RESET_ALL}")
    print(f"  Time: {paul_status['timestamp']}")
    print(f"  Type: {paul_status['last_action']}")
    print(f"  Message: {paul_status['last_message']}")

    print(f"{Fore.CYAN}{'-'*60}{Style.RESET_ALL}")

    # Recent Log Activity
    print(f"{Fore.MAGENTA}📜 RECENT PAUL ACTIVITY:{Style.RESET_ALL}")

    # Try to read Paul's log
    log_lines = read_log_tail('paul_developer.log', 5)
    if log_lines:
        for line in log_lines:
            line = line.strip()
            if 'ERROR' in line or 'CRITICAL' in line:
                print(f"  {Fore.RED}{line[:80]}...{Style.RESET_ALL}" if len(line) > 80 else f"  {Fore.RED}{line}{Style.RESET_ALL}")
            elif 'SUCCESS' in line or '✓' in line:
                print(f"  {Fore.GREEN}{line[:80]}...{Style.RESET_ALL}" if len(line) > 80 else f"  {Fore.GREEN}{line}{Style.RESET_ALL}")
            elif 'WARNING' in line or '⚠' in line:
                print(f"  {Fore.YELLOW}{line[:80]}...{Style.RESET_ALL}" if len(line) > 80 else f"  {Fore.YELLOW}{line}{Style.RESET_ALL}")
            else:
                print(f"  {line[:80]}..." if len(line) > 80 else f"  {line}")
    else:
        print("  No recent log entries")

    print(f"{Fore.CYAN}{'-'*60}{Style.RESET_ALL}")

    # Claude to Paul Messages
    try:
        with open('claude_to_paul.json', 'r') as f:
            claude_msg = json.load(f)
            print(f"{Fore.BLUE}💬 CLAUDE'S LAST INSTRUCTION:{Style.RESET_ALL}")
            print(f"  Type: {claude_msg.get('type', 'Unknown')}")
            print(f"  Message: {claude_msg.get('data', {}).get('message', 'None')}")
    except:
        print(f"{Fore.BLUE}💬 CLAUDE'S LAST INSTRUCTION: None{Style.RESET_ALL}")

    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Press Ctrl+C to exit | Refreshing every 3 seconds...{Style.RESET_ALL}")

def main():
    """Main monitoring loop"""
    print(f"{Fore.GREEN}Starting Paul Monitor Dashboard...{Style.RESET_ALL}")

    try:
        while True:
            display_dashboard()
            time.sleep(3)  # Refresh every 3 seconds
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Monitoring stopped.{Style.RESET_ALL}")
        sys.exit(0)

if __name__ == "__main__":
    main()