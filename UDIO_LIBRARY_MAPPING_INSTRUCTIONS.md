# Udio Library Mapping Instructions

## Current Situation

We've successfully set up Chrome debugging, but encountered a specific issue:
- **Chrome Dev requires `--headless` mode** for remote debugging to work on your system
- **Headless mode prevents manual login** (no visible browser window)
- **Your Profile 2 has login issues** when used with `--user-data-dir`

## Solution Options

### Option 1: Use Chrome Stable (Recommended)

Chrome Stable may not have the same debugging restrictions as Chrome Dev.

1. **Install Chrome Stable** (if not already installed)
2. **Start Chrome Stable with debugging:**
   ```bash
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\[USERNAME]\AppData\Local\Google\Chrome\User Data" --profile-directory="Default"
   ```
3. **Log in to Udio** in the visible Chrome window
4. **Run the mapper:**
   ```bash
   python scripts/map_udio_library_structure.py
   ```

### Option 2: Use Selenium with Manual ChromeDriver

Since ChromeDriver version 141 doesn't match Chrome Dev 144, we can:

1. **Download matching ChromeDriver manually:**
   - Visit: https://googlechromelabs.github.io/chrome-for-testing/
   - Download ChromeDriver for version 144
   - Place in a known location

2. **Update our scripts to use the manual ChromeDriver path**

### Option 3: Use API/Network Inspection (Advanced)

Instead of DOM scraping, we could:

1. **Monitor network requests** while browsing Udio
2. **Identify API endpoints** for library/folder data
3. **Use direct API calls** instead of browser automation

This would be more reliable but requires reverse-engineering Udio's API.

### Option 4: Use Your Existing Chrome Instance

You mentioned having Chrome Dev open with Profile 2. We can try:

1. **Find the Chrome process** that's already running
2. **Check if it has debugging enabled:**
   ```bash
   netstat -an | findstr :9222
   ```
3. **If not, restart it with debugging:**
   - Close Chrome completely
   - Start with: `chrome --remote-debugging-port=9222`
   - Log in to Udio
   - Run mapper

## Recommended Next Steps

### Immediate Action:

1. **Try Chrome Stable** (most likely to work):
   ```bash
   # Close all Chrome instances
   taskkill /f /im chrome.exe
   
   # Start Chrome Stable with debugging
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
   ```

2. **Log in to Udio** at https://www.udio.com/library

3. **Run the mapper:**
   ```bash
   python scripts/map_udio_library_structure.py
   ```

### Alternative: Manual DOM Inspection

If automation continues to fail, you can:

1. **Open Udio library** in any browser
2. **Open Developer Tools** (F12)
3. **Inspect the page structure** manually
4. **Document the selectors** you find:
   - Folder elements
   - Song/track cards
   - Play buttons
   - Download buttons
   - Navigation elements

5. **Share the findings** and we'll create scrapers based on that

## Technical Details

### Why Chrome Dev Has Issues:

- **Version mismatch**: Chrome Dev 144 vs ChromeDriver 141
- **Debugging restrictions**: Chrome Dev may have stricter security for remote debugging
- **Profile isolation**: Windows user account isolation prevents profile sharing

### What We've Confirmed Works:

✅ Chrome Dev with `--headless --remote-debugging-port=9222` (but can't login)
✅ Chrome DevTools Protocol access via HTTP/WebSocket
✅ Direct UI mapping without Selenium

### What Doesn't Work:

❌ Chrome Dev with profiles and debugging (port doesn't bind)
❌ Selenium with Chrome Dev 144 (ChromeDriver version mismatch)
❌ Non-headless Chrome Dev with debugging (port doesn't bind)

## Files Created

- `scripts/map_udio_library_structure.py` - Main library mapper
- `scripts/open_udio_for_login.py` - Login helper
- `scripts/chrome_debug_final_solution.py` - Comprehensive Chrome debug setup
- `scripts/comprehensive_debug_check.py` - Diagnostic tool
- `docs/chrome_dev_setup.md` - Complete documentation

## Contact Points

If you need to manually inspect and share findings:

1. **Folder structure**: What selectors identify folders?
2. **Song cards**: What selectors identify individual songs?
3. **Metadata**: Where is song title, artist, duration shown?
4. **Actions**: Where are play, download, share buttons?
5. **Navigation**: How is the folder tree structured?

Share screenshots or HTML snippets and we can build the scraper from that.