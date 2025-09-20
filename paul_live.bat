@echo off
title PAUL LIVE MONITOR - Real-time Stream
echo ======================================================================
echo  PAUL DEVELOPER AI - LIVE MONITOR (Real-time)
echo ======================================================================
echo.
echo Streaming Paul's activity as it happens...
echo Press Ctrl+C to stop
echo ----------------------------------------------------------------------
echo.
powershell -Command "Get-Content 'paul_developer.log' -Wait -Tail 20"