# Chrome Dev Setup for Udio Downloader

This document provides detailed instructions for setting up Chrome Dev with remote debugging for the Udio Downloader project.

## User Configuration

**Primary Test Account:**
- Email: `idiovoidi@gmail.com`
- Platform: Udio.com
- Purpose: Testing and development of the Udio Downloader

## Chrome Dev Installation Paths

### Windows Locations
Chrome Dev is typically installed in one of these locations:

1. **User Installation (Most Common):**
   ```
   %LOCALAPPDATA%\Google\Chrome Dev\Application\chrome.exe
   C:\Users\[USERNAME]\AppData\Local\Google\Chrome Dev\Application\chrome.exe
   ```

2. **System-wide Installation:**
   ```
   %PROGRAMFILES%\Google\Chrome Dev\Application\chrome.exe
   C:\Program Files\Google\Chrome Dev\Application\chrome.exe
   ```

3. **32-bit on 64-bit System:**
   ```
   %PROGRAMFILES(X86)%\Google\Chrome Dev\Application\chrome.exe
   C:\Program Files (x86)\Google\Chrome Dev\Application\chrome.exe
   ```

### Profile Locations
Chrome Dev profiles are stored at:
```
%LOCALAPPDATA%\Google\Chrome Dev\User Data\
C:\Users\[USERNAME]\AppData\Local\Google\Chrome Dev\User Data\
```

## Remote Debugging Setup

### Method 1: Automated Setup (Recommended)
Use the provided batch script:
```bash
scripts/start_chrome_dev_debug.bat
```

### Method 2: Manual Command Line
```bash
# Close all Chrome instances first
taskkill /f /im chrome.exe

# Start Chrome Dev with debugging
chrome --remote-debugging-port=9222 --restore-last-session
```

### Method 3: With Specific Profile
```bash
chrome --remote-debugging-port=9222 --user-data-dir="C:\Users\[USERNAME]\AppData\Local\Google\Chrome Dev\User Data" --restore-last-session
```

## Required Chrome Flags

For optimal debugging and automation:

```bash
--remote-debugging-port=9222    # Enable remote debugging
--restore-last-session          # Restore previous tabs/login
--disable-web-security          # Optional: for CORS issues
--disable-features=VizDisplayCompositor  # Optional: for stability
--no-first-run                  # Skip first-run setup
--no-default-browser-check      # Skip default browser prompt
```

## Verification Steps

### 1. Check if Debugging is Enabled
```bash
python scripts/check_chrome_debug.py
```

### 2. Manual Verification
Open in browser: `http://localhost:9222/json`

Should return JSON with open tabs information.

### 3. Test Selenium Connection
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_experimental_option("debuggerAddress", "localhost:9222")
driver = webdriver.Chrome(options=options)
print(f"Connected to: {driver.current_url}")
```

## Udio-Specific Setup

### Login Process
1. Navigate to: `https://www.udio.com/login`
2. Use account: `idiovoidi@gmail.com`
3. Complete authentication
4. Verify access to: `https://www.udio.com/library`

### Key Pages for Testing
- **Library:** `https://www.udio.com/library` (main target for scraping)
- **My Creations:** `https://www.udio.com/my-creations` (user's songs)
- **Create:** `https://www.udio.com/create` (song creation interface)

## Troubleshooting

### Common Issues

#### 1. "Chrome not found"
**Solution:** Update the path in scripts or install Chrome Dev:
```bash
# Download from: https://www.google.com/chrome/dev/
```

#### 2. "Port 9222 already in use"
**Solution:** Kill existing Chrome processes:
```bash
taskkill /f /im chrome.exe
netstat -an | findstr :9222
```

#### 3. "Session expired" or "Redirected to login"
**Solution:** 
- Re-authenticate in the Chrome Dev window
- Check if cookies are preserved
- Verify the correct profile is being used

#### 4. "Cannot connect to debugging port"
**Solution:**
- Ensure Chrome was started with `--remote-debugging-port=9222`
- Check Windows Firewall settings
- Verify no antivirus is blocking the connection

### Debug Commands

```bash
# Check if Chrome is running with debugging
netstat -an | findstr :9222

# List Chrome processes
tasklist | findstr chrome.exe

# Check Chrome version
chrome --version

# Test debugging endpoint
curl http://localhost:9222/json
```

## Security Considerations

### Development Environment
- Remote debugging should only be enabled in development
- The debugging port (9222) should not be exposed to external networks
- Use a separate Chrome profile for development/testing

### Production Notes
- Never enable remote debugging in production
- Use headless mode for production scraping
- Implement proper authentication handling

## Scripts Reference

### Available Scripts
- `scripts/check_chrome_debug.py` - Verify debugging setup
- `scripts/start_chrome_dev_debug.bat` - Start Chrome Dev with debugging
- `scripts/ui_mapper_attach.py` - Map Udio UI using existing session
- `scripts/find_chrome_profile.py` - Locate Chrome profiles and paths

### Usage Examples
```bash
# Check current setup
python scripts/check_chrome_debug.py

# Start Chrome with debugging
scripts/start_chrome_dev_debug.bat

# Map Udio UI
python scripts/ui_mapper_attach.py

# Find Chrome installation
python scripts/find_chrome_profile.py
```

## Environment Variables

You can set these for consistent behavior:

```bash
# Windows
set CHROME_DEV_PATH="C:\Users\[USERNAME]\AppData\Local\Google\Chrome Dev\Application\chrome.exe"
set CHROME_DEBUG_PORT=9222
set UDIO_TEST_EMAIL=idiovoidi@gmail.com

# PowerShell
$env:CHROME_DEV_PATH = "C:\Users\[USERNAME]\AppData\Local\Google\Chrome Dev\Application\chrome.exe"
$env:CHROME_DEBUG_PORT = "9222"
$env:UDIO_TEST_EMAIL = "idiovoidi@gmail.com"
```

## Best Practices

### Development Workflow
1. Start Chrome Dev with debugging enabled
2. Manually log into Udio with test account
3. Run UI mapping scripts to analyze structure
4. Develop scraping logic based on findings
5. Test with authentication system

### Profile Management
- Use dedicated profile for Udio testing
- Keep login credentials saved in profile
- Backup profile data periodically
- Document any profile-specific settings

### Session Management
- Always verify authentication before scraping
- Handle session expiration gracefully
- Implement session renewal logic
- Monitor for login redirects

## Updates and Maintenance

### Chrome Dev Updates
- Chrome Dev updates automatically
- WebDriver may need updates after Chrome updates
- Test scripts after Chrome updates
- Update documentation if paths change

### Profile Maintenance
- Clear cache periodically
- Update saved passwords as needed
- Monitor for profile corruption
- Backup important profile data

---

**Last Updated:** November 2025  
**Chrome Dev Version:** Latest  
**Test Account:** idiovoidi@gmail.com  
**Primary Use Case:** Udio music platform automation