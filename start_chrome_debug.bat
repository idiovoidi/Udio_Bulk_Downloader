@echo off
echo ============================================
echo Chrome Remote Debugging Launcher
echo ============================================
echo.

echo [1/3] Closing existing Chrome instances...
taskkill /F /IM chrome.exe 2>nul
if %errorlevel% == 0 (
    echo   ^> Chrome closed
    timeout /t 2 /nobreak >nul
) else (
    echo   ^> No Chrome instances found
)

echo.
echo [2/3] Starting Chrome with remote debugging...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --remote-debugging-port=9222 ^
  --user-data-dir="%USERPROFILE%\AppData\Local\Google\Chrome\User Data\Udio"

timeout /t 3 /nobreak >nul

echo.
echo [3/3] Verifying connection...
curl -s http://localhost:9222/json >nul 2>&1
if %errorlevel% == 0 (
    echo   ^> SUCCESS! Chrome is running on port 9222
    echo.
    echo ============================================
    echo READY TO USE
    echo ============================================
    echo.
    echo You can now run:
    echo   - python analyze_udio.py
    echo   - python map_udio.py
    echo.
    echo Navigate to: https://udio.com/my-creations
    echo.
) else (
    echo   ^> WARNING: Could not verify connection
    echo   ^> Chrome may still be starting...
    echo.
    echo Try opening: http://localhost:9222/json
    echo.
)

pause
