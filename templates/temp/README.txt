=====================================
TEMPORARY FILES FOLDER
=====================================

PURPOSE:
--------
This folder is for temporary test HTML files during development.

RULES:
------
1. ANY file in this folder is TEMPORARY
2. Files here should NEVER be referenced by app.py
3. Once testing is complete, code must be moved to proper template files
4. This folder should be EMPTIED regularly
5. Files here are NOT deployed to production

WORKFLOW:
---------
1. Create test HTML here during development
2. Test and verify the code works
3. Move working code to the proper template (Gate1.html, Gate2.html, Dashboard.html, or 404.html)
4. DELETE the temporary file immediately

IMPORTANT:
----------
* Never commit files from this folder to git
* Never reference these files in production code
* Always clean up after yourself

=====================================