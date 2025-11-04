@echo off
echo Starting Chrome Dev with Remote Debugging
echo System: Windows 10.0.26200
echo User: Mitchell Local
echo Generated: 2025-11-04T22:58:20.706943
echo.

REM Close existing Chrome instances
echo Closing existing Chrome instances...
taskkill /f /im chrome.exe 2>nul

REM Wait for processes to close
timeout /t 2 /nobreak >nul

REM Start Chrome Dev with debugging
echo Starting Chrome Dev with debugging enabled...
"C:\Program Files\Google\Chrome Dev\Application\chrome.exe" --remote-debugging-port=9222 --restore-last-session --user-data-dir="C:\Users\Mitchell\AppData\Local\Google\Chrome Dev\User Data" "https://www.udio.com/library"

echo.
echo Chrome Dev started with remote debugging on port 9222
echo Navigate to Udio and log in with: idiovoidi@gmail.com
echo Then run: python scripts/ui_mapper_attach.py
echo.
pause