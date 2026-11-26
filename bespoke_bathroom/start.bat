@echo off
rem Bespoke Bathroom UK - Social Studio (Windows): double-click to start.
cd /d "%~dp0"
where /q node
if errorlevel 1 goto nonode
if not exist node_modules call npm install --no-fund --no-audit
start "" /b powershell -NoProfile -Command "Start-Sleep -Seconds 3; Start-Process 'http://localhost:4321'"
node server.js
pause
exit /b 0

:nonode
echo Node.js is not installed. Download the LTS version from https://nodejs.org and then double-click this file again.
pause
exit /b 1
