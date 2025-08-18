=====================================
ATLASNEXUS - SIMPLE RULES
=====================================

PROJECT STRUCTURE:
------------------
Project1/
├── app.py           # THE ONLY APP FILE
├── local.bat        # Start local server
├── live.bat         # Deploy to live site
├── README.txt       # This file
├── requirements.txt # Vercel needs this (Flask version)
├── vercel.json      # Vercel needs this (tells it to use app.py)
└── templates/       # 4 HTML files only
    ├── Gate1.html
    ├── Gate2.html
    ├── Dashboard.html
    └── 404.html

HOW TO WORK:
------------
1. EDIT: Make changes to app.py
2. TEST: Double-click local.bat
3. DEPLOY: Double-click live.bat

GOLDEN RULES:
-------------
✓ ONE app.py for everything
✓ What works locally = What goes live
✓ Always test before deploying

NEVER DO THIS:
--------------
❌ Don't create app_live.py
❌ Don't create app_local.py
❌ Don't edit on GitHub directly
❌ Don't have multiple versions

=====================================
Remember: local.bat → test
          live.bat → deploy
=====================================