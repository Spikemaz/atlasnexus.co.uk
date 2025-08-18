@echo off
echo =====================================
echo  PUSH TO LIVE (atlasnexus.co.uk)
echo =====================================
echo.

REM Commit and push everything
git add -A
git commit -m "Live sync: %date% %time%"
git push origin main

echo.
echo =====================================
echo  DONE! Live site will update in 1-2 min
echo  Check: atlasnexus.co.uk
echo =====================================
pause