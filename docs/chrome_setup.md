# Chrome Dev Setup Documentation

## System Information

**Chrome Dev Path:** `C:\Program Files\Google\Chrome Dev\Application\chrome.exe`

**Target User Account:** `user@example.com`

**User Data Directory:** `C:\Users\user\AppData\Local\Google\Chrome Dev\User Data`

## Profile Analysis Results

From profile analysis, `user@example.com` is found in:

1. **Default Profile** - Contains both `user@example.com` and `other-user@example.com`
2. **Profile 2** - Contains only `user@example.com` (Display Name: Example User)

**Recommended Profile:** Profile 2 (cleaner, single account)

## Remote Debugging Requirements

For Selenium to attach to Chrome, Chrome must be started with:
- `--remote-debugging-port=9222` flag
- Specific profile directory if multiple profiles exist
- User data directory specification

## Command Template

```bash
"C:\Program Files\Google\Chrome Dev\Application\chrome.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="C:\Users\user\AppData\Local\Google\Chrome Dev\User Data" \
  --profile-directory="Profile 2" \
  --new-window "https://www.udio.com/library"
```

## Troubleshooting Notes

### Issue Analysis Needed
- Commands appear to execute but debugging port 9222 is not accessible
- Chrome processes are running but remote debugging is not enabled
- Need to investigate why the debugging flag is not taking effect

### Potential Causes
1. Chrome Dev may handle flags differently than regular Chrome
2. Existing Chrome processes may interfere with new debugging-enabled process
3. Windows security/firewall may block the debugging port
4. Chrome may require complete shutdown before enabling debugging