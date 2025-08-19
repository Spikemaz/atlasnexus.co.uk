#!/usr/bin/env python3
"""
IP Lockout Manager - Failsafe tool to manage IP lockouts
Run this script to clear IP addresses or view lockout status
"""

import json
import os
import sys
from datetime import datetime

LOCKOUT_FILE = 'ip_lockouts.json'
ATTEMPT_LOG_FILE = 'ip_attempts_log.json'

def load_lockouts():
    """Load IP lockout data"""
    if not os.path.exists(LOCKOUT_FILE):
        return {}
    try:
        with open(LOCKOUT_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_lockouts(lockouts):
    """Save IP lockout data"""
    try:
        with open(LOCKOUT_FILE, 'w') as f:
            json.dump(lockouts, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error saving: {e}")
        return False

def clear_ip(ip_address):
    """Clear a specific IP from lockouts"""
    lockouts = load_lockouts()
    if ip_address in lockouts:
        del lockouts[ip_address]
        if save_lockouts(lockouts):
            print(f"[SUCCESS] Successfully cleared IP: {ip_address}")
            return True
        else:
            print(f"[ERROR] Failed to save changes")
            return False
    else:
        print(f"[INFO] IP {ip_address} was not in lockout list")
        return True

def clear_all():
    """Clear ALL IP lockouts"""
    if save_lockouts({}):
        print("[SUCCESS] All IP lockouts cleared!")
        return True
    else:
        print("[ERROR] Failed to clear lockouts")
        return False

def list_lockouts():
    """List all current IP lockouts"""
    lockouts = load_lockouts()
    if not lockouts:
        print("No IP addresses are currently locked out")
        return
    
    print("\n" + "="*60)
    print("CURRENT IP LOCKOUTS")
    print("="*60)
    
    for ip, info in lockouts.items():
        print(f"\nIP: {ip}")
        if info.get('permanent'):
            print("  Status: PERMANENT BAN")
        else:
            if 'locked_until' in info:
                locked_until = datetime.fromisoformat(info['locked_until'])
                if datetime.now() < locked_until:
                    remaining = locked_until - datetime.now()
                    print(f"  Status: TEMPORARY BLOCK")
                    print(f"  Expires: {locked_until.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"  Remaining: {str(remaining).split('.')[0]}")
                else:
                    print(f"  Status: EXPIRED (can be cleaned)")
        
        if info.get('reason'):
            print(f"  Reason: {info['reason']}")
        if info.get('failed_passwords'):
            print(f"  Failed passwords: {', '.join(info['failed_passwords'])}")
        if info.get('reference_code'):
            print(f"  Reference: {info['reference_code']}")
    
    print("\n" + "="*60)

def main():
    print("\n" + "="*60)
    print("IP LOCKOUT MANAGER - FAILSAFE TOOL")
    print("="*60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'list':
            list_lockouts()
        
        elif command == 'clear':
            if len(sys.argv) > 2:
                ip = sys.argv[2]
                if ip == 'all':
                    confirm = input("[WARNING] Clear ALL IP lockouts? (yes/no): ")
                    if confirm.lower() == 'yes':
                        clear_all()
                    else:
                        print("Cancelled")
                else:
                    clear_ip(ip)
            else:
                print("Usage: python ip_manager.py clear <IP_ADDRESS or 'all'>")
        
        elif command == 'help':
            print("\nCommands:")
            print("  python ip_manager.py list              - List all lockouts")
            print("  python ip_manager.py clear <IP>        - Clear specific IP")
            print("  python ip_manager.py clear all         - Clear ALL lockouts")
            print("  python ip_manager.py help              - Show this help")
        
        else:
            print(f"Unknown command: {command}")
            print("Use 'python ip_manager.py help' for available commands")
    
    else:
        # Interactive mode
        while True:
            print("\nOptions:")
            print("  1. List all IP lockouts")
            print("  2. Clear specific IP")
            print("  3. Clear ALL lockouts")
            print("  4. Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                list_lockouts()
            
            elif choice == '2':
                ip = input("Enter IP address to clear: ").strip()
                if ip:
                    clear_ip(ip)
            
            elif choice == '3':
                confirm = input("[WARNING] Clear ALL IP lockouts? (yes/no): ")
                if confirm.lower() == 'yes':
                    clear_all()
                else:
                    print("Cancelled")
            
            elif choice == '4':
                print("Goodbye!")
                break
            
            else:
                print("Invalid option")

if __name__ == "__main__":
    main()