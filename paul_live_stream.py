"""
Paul Developer AI - Live Stream Monitor
Shows Paul's activity in real-time as it happens
"""

import os
import sys
import time
import subprocess
from datetime import datetime
import threading
import queue

def follow_log(filename, output_queue):
    """Follow a log file and output new lines as they appear"""
    try:
        # Use PowerShell Get-Content -Wait for real-time tailing on Windows
        cmd = f'powershell -Command "Get-Content -Path \'{filename}\' -Wait -Tail 10"'
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

        for line in iter(process.stdout.readline, ''):
            if line:
                output_queue.put(('LOG', line.strip()))
    except Exception as e:
        output_queue.put(('ERROR', f"Error reading {filename}: {e}"))

def monitor_paul_processes(output_queue):
    """Monitor Paul processes"""
    while True:
        try:
            # Check if Paul processes are running
            result = subprocess.run('tasklist | findstr /i "python"',
                                  capture_output=True, text=True, shell=True)
            paul_count = result.stdout.lower().count('paul')
            output_queue.put(('STATUS', f"Paul processes running: {paul_count}"))
        except:
            pass
        time.sleep(10)  # Check every 10 seconds

def display_output(output_queue):
    """Display output from the queue"""
    print("=" * 70)
    print(" PAUL DEVELOPER AI - LIVE STREAM MONITOR")
    print("=" * 70)
    print(f" Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(" Streaming live output from Paul...")
    print("-" * 70)
    print()

    while True:
        try:
            msg_type, message = output_queue.get(timeout=0.1)

            timestamp = datetime.now().strftime("%H:%M:%S")

            if msg_type == 'LOG':
                # Color code based on content
                if 'ERROR' in message or 'CRITICAL' in message or '✗' in message:
                    print(f"[{timestamp}] ❌ {message}")
                elif 'SUCCESS' in message or 'OK' in message or '✓' in message:
                    print(f"[{timestamp}] ✅ {message}")
                elif 'WARNING' in message or '⚠' in message:
                    print(f"[{timestamp}] ⚠️  {message}")
                elif 'FIXING' in message or 'DEPLOYING' in message:
                    print(f"[{timestamp}] 🔧 {message}")
                elif 'CHECKING' in message or 'MONITORING' in message:
                    print(f"[{timestamp}] 👀 {message}")
                else:
                    print(f"[{timestamp}]    {message}")
            elif msg_type == 'STATUS':
                # Status updates in different format
                print(f"\n[{timestamp}] 📊 {message}\n")
            elif msg_type == 'ERROR':
                print(f"[{timestamp}] ⚠️  {message}")

        except queue.Empty:
            continue
        except KeyboardInterrupt:
            print("\n" + "=" * 70)
            print(" Live monitoring stopped")
            print("=" * 70)
            sys.exit(0)

def main():
    """Main function to start all monitoring threads"""
    output_queue = queue.Queue()

    # Start log following thread
    log_thread = threading.Thread(target=follow_log,
                                 args=('paul_developer.log', output_queue),
                                 daemon=True)
    log_thread.start()

    # Start process monitoring thread
    process_thread = threading.Thread(target=monitor_paul_processes,
                                     args=(output_queue,),
                                     daemon=True)
    process_thread.start()

    # Display output in main thread
    try:
        display_output(output_queue)
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        sys.exit(0)

if __name__ == "__main__":
    main()