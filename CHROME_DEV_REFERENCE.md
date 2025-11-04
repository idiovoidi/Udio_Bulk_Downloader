# Chrome Dev Quick Reference

**Generated:** November 4, 2025  
**System:** Windows (64bit)

## Key Information

### Test Account
- **Email:** Your Udio account
- **Platform:** Udio.com
- **Purpose:** Development and testing

### Chrome Dev Installation
- **Path:** `C:\Program Files\Google\Chrome Dev\Application\chrome.exe`
- **Version:** Latest Dev Channel
- **Profiles:** 4 profiles found (Default profile recommended)

### Quick Start Commands

#### Start Chrome Dev with Debugging
```bash
# Use the custom script (recommended)
scripts/start_chrome_dev_custom.bat

# Or manual command
"C:\Program Files\Google\Chrome Dev\Application\chrome.exe" --remote-debugging-port=9222 --restore-last-session --user-data-dir="C:\Users\[USERNAME]\AppData\Local\Google\Chrome Dev\User Data" "https://www.udio.com/library"
```

#### Check Debugging Status
```bash
python scripts/check_chrome_debug.py
```

#### Map Udio UI
```bash
python scripts/ui_mapper_attach.py
```

### Target URLs
- **Library:** https://www.udio.com/library (primary target)
- **My Creations:** https://www.udio.com/my-creations
- **Create:** https://www.udio.com/create

### Debugging Port
- **Port:** 9222
- **Status:** Available ✅
- **Test URL:** http://localhost:9222/json

## Workflow

1. **Start Chrome Dev with debugging:**
   ```bash
   scripts/start_chrome_dev_custom.bat
   ```

2. **Log into Udio:**
   - Navigate to https://www.udio.com/login
   - Use your Udio account
   - Verify access to library page

3. **Run UI mapping:**
   ```bash
   python scripts/ui_mapper_attach.py
   ```

4. **Develop scraping logic based on findings**

## Files Reference

- **Full Documentation:** `docs/chrome_dev_setup.md`
- **System Config:** `config/chrome_dev_config.json`
- **Custom Batch File:** `scripts/start_chrome_dev_custom.bat`
- **Debug Checker:** `scripts/check_chrome_debug.py`
- **UI Mapper:** `scripts/ui_mapper_attach.py`

## Troubleshooting

### Common Issues
- **Port 9222 in use:** Run `taskkill /f /im chrome.exe`
- **Session expired:** Re-authenticate in Chrome Dev window
- **Cannot connect:** Ensure Chrome started with `--remote-debugging-port=9222`

### Debug Commands
```bash
# Check port status
netstat -an | findstr :9222

# List Chrome processes
tasklist | findstr chrome.exe

# Test debugging endpoint
curl http://localhost:9222/json
```

---
*This reference was auto-generated based on your system configuration.*