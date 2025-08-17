#!/usr/bin/env python3
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
    print("\nSECURITY GATE 1 - Site Access:")
    print("  Internal Access: RedAMC")
    print("  Partner Access: PartnerAccess")
    print("  Secret Unlock: Ronabambi (bottom-left corner, 4 clicks)")
    print("\nSECURITY GATE 2 - User Login:")
    print("  Admin: marcus@atlasnexus.co.uk")
    print("  Password: MarcusAdmin2024")
    print("=" * 60)
    print("\nStarting server at: http://localhost:5000")
    print("Opening browser in 3 seconds...")
    print("=" * 60)
    
    # Open browser after short delay
    time.sleep(3)
    webbrowser.open('http://localhost:5000')
    
    # Run Flask app
    app.run(debug=True, host='127.0.0.1', port=5000)
