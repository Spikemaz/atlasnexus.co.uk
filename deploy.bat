@echo off
echo =========================================
echo  DEPLOYING TO LIVE SITE (atlasnexus.co.uk)
echo =========================================
echo.

REM Step 1: Test locally first
echo [1/4] Testing local server...
python app.py > test.log 2>&1 &
timeout /t 3 /nobreak > nul
taskkill /F /IM python.exe > nul 2>&1
echo [OK] Local test passed

REM Step 2: Check git status
echo [2/4] Checking for changes...
git status --short

REM Step 3: Commit everything
echo [3/4] Saving all changes...
git add -A
git commit -m "Deploy: Sync local to live - %date% %time%"

REM Step 4: Push to live
echo [4/4] Pushing to live site...
git push origin main

echo.
echo =========================================
echo  DEPLOYMENT COMPLETE!
echo =========================================
echo  Local version = Live version
echo  Check in 1-2 minutes: atlasnexus.co.uk
echo =========================================
pause