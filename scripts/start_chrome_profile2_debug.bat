@echo off
echo Starting Chrome Dev Profile 2 with Remote Debugging
echo Target: https://www.udio.com/library
echo Profile: Profile 2 (1.5GB - likely has Udio login saved)
echo Debug Port: 9222
echo.

REM Close existing Chrome instances
echo Closing existing Chrome instances...
taskkill /f /im chrome.exe 2>nul

REM Wait for processes to close
timeout /t 3 /nobreak >nul

REM Start Chrome Dev with Profile 2 and debugging
echo Starting Chrome Dev with Profile 2 and debugging enabled...
"C:\Program Files\Google\Chrome Dev\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\Mitchell\AppData\Local\Google\Chrome Dev\User Data" --profile-directory="Profile 2" "https://www.udio.com/library"

echo.
echo Chrome Dev started with:
echo   - Remote debugging on port 9222
echo   - Profile 2 active
echo   - Udio library page loading
echo.
echo If you're not logged in, use account: idiovoidi@gmail.com
echo Then test with: python scripts/check_chrome_debug.py
echo.
pause