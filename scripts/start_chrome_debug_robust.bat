@echo off
echo Chrome Dev Debug Launcher (Robust Version)
echo ==========================================
echo.

REM Kill all Chrome processes thoroughly
echo Step 1: Terminating all Chrome processes...
taskkill /f /im chrome.exe 2>nul
wmic process where "name='chrome.exe'" delete 2>nul

REM Wait longer for processes to fully terminate
echo Waiting for processes to terminate...
timeout /t 5 /nobreak >nul

REM Verify no Chrome processes remain
echo Checking for remaining Chrome processes...
for /f %%i in ('tasklist /fi "imagename eq chrome.exe" 2^>nul ^| find /c "chrome.exe"') do set CHROME_COUNT=%%i
if %CHROME_COUNT% gtr 0 (
    echo Warning: %CHROME_COUNT% Chrome processes still running
    echo Attempting force kill...
    taskkill /f /im chrome.exe /t 2>nul
    timeout /t 3 /nobreak >nul
)

echo.
echo Step 2: Starting Chrome Dev with debugging...
echo Command: "C:\Program Files\Google\Chrome Dev\Application\chrome.exe"
echo Flags: --remote-debugging-port=9222 --user-data-dir="C:\Users\Mitchell\AppData\Local\Google\Chrome Dev\User Data" --profile-directory="Profile 2"
echo URL: https://www.udio.com/library
echo.

REM Start Chrome with debugging - using start /wait to ensure proper execution
start "" "C:\Program Files\Google\Chrome Dev\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\Mitchell\AppData\Local\Google\Chrome Dev\User Data" --profile-directory="Profile 2" --no-first-run --no-default-browser-check "https://www.udio.com/library"

REM Wait for Chrome to start
echo Waiting for Chrome to initialize...
timeout /t 5 /nobreak >nul

REM Test debugging connection
echo.
echo Step 3: Testing debugging connection...
curl -s http://localhost:9222/json >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Debugging connection successful!
    echo Port 9222 is active and responding
) else (
    echo ❌ Debugging connection failed
    echo Port 9222 is not responding
    echo.
    echo Troubleshooting:
    echo 1. Check if Chrome started properly
    echo 2. Verify no firewall is blocking port 9222
    echo 3. Try running as administrator
)

echo.
echo Chrome Dev should now be running with:
echo - Remote debugging on port 9222
echo - Profile 2 active
echo - Udio library page loaded
echo.
echo Test the connection with: python scripts/check_chrome_debug.py
echo Then run UI mapper with: python scripts/ui_mapper_attach.py
echo.
pause