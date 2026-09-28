@echo off
title Skill Gap Analyzer
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
  python server.py
  goto :eof
)
where py >nul 2>nul
if %errorlevel%==0 (
  py server.py
  goto :eof
)

echo Python was not found, so the local server cannot start.
echo Opening the page directly. Some job sources may be blocked by the browser.
echo Install Python from https://www.python.org/downloads/ for full live data.
start "" "%~dp0skill-gap-analyzer.html"
pause
