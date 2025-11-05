# Chrome Remote Debugging Setup

Remote debugging connects Python to an authenticated Chrome session, avoiding bot detection.

## Quick Start

1. Close Chrome: `taskkill /F /IM chrome.exe`

2. Start with debugging enabled:
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%USERPROFILE%\AppData\Local\Google\Chrome\User Data\Udio"
```

3. Navigate to Udio library in Chrome

4. Run scripts: `python analyze_udio.py`

## Verify Connection

Visit `http://localhost:9222/json` - should show JSON with open tabs.

## Troubleshooting

**Cannot connect**: Ensure Chrome started with `--remote-debugging-port=9222`

**Session expired**: Log into Udio in the Chrome window

**Port conflict**: Check `netstat -ano | findstr :9222` or use different port
