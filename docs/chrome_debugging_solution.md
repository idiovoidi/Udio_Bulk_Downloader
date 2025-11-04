# Chrome Debugging Solution

## Problem Identified
- Chrome Dev has 42 processes running
- None have remote debugging enabled
- The `--remote-debugging-port=9222` flag is not taking effect
- Port 9222 is not listening

## Root Cause
When Chrome is already running, starting a new Chrome process with debugging flags often fails because:
1. Chrome uses a single-instance model
2. New processes become "helper" processes rather than main processes
3. The debugging flag only works on the main browser process

## Solution Steps

### Step 1: Complete Chrome Shutdown
```bash
# Kill all Chrome processes
taskkill /f /im chrome.exe
```

### Step 2: Start Chrome with Debugging (Administrator Command Prompt)
```bash
# Test 1: Minimal command
"C:\Program Files\Google\Chrome Dev\Application\chrome.exe" --remote-debugging-port=9222

# Test 2: With fresh profile (if Test 1 fails)
"C:\Program Files\Google\Chrome Dev\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug
```

### Step 3: Verify Debugging is Working
```bash
# Test the debugging endpoint
curl http://localhost:9222/json
# Or visit http://localhost:9222 in another browser
```

### Step 4: Navigate to Udio and Login
Once debugging is confirmed working:
1. Navigate to https://www.udio.com/login
2. Login with idiovoidi@gmail.com
3. Go to https://www.udio.com/library

### Step 5: Run UI Mapper
```bash
python scripts/ui_mapper_attach.py
```

## Alternative: Use Regular Chrome
If Chrome Dev continues to have issues:
```bash
# Close all Chrome
taskkill /f /im chrome.exe

# Start regular Chrome with debugging
chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug
```

## Verification Commands
- Check processes: `tasklist | findstr chrome`
- Check port: `netstat -an | findstr :9222`
- Test endpoint: `curl http://localhost:9222/json`