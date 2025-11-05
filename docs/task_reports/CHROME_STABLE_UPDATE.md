# ✅ Updated to Chrome Stable

## What Changed

The debugging configuration now uses **Chrome Stable** (standard Chrome) instead of Chrome Dev.

## Why?

Chrome Dev can have bugs and issues. Chrome Stable is:
- ✅ More stable
- ✅ Fewer bugs
- ✅ What users actually use
- ✅ Better compatibility

## What You Need to Know

### Nothing Changes for You!

The same commands work:
```
F5 → "Launch Chrome Extension (Keep Login)"
```

### It Just Works Better

- Uses your standard Chrome installation
- More stable debugging experience
- Fewer crashes and issues
- Same great debugging features

## Available Options

### Chrome Stable (Default) ⭐
```
F5 → "Launch Chrome Extension (Keep Login)"
```
- Uses standard Chrome
- Most stable
- Login persists

### Microsoft Edge (Alternative) ⭐⭐
```
F5 → "Launch Edge Extension (Keep Login)"
```
- Can run alongside Chrome
- Very stable
- Excellent debugging

### Attach to Your Chrome
```
1. Task: "Start Chrome with Remote Debugging (Your Profile)"
2. Load extension at chrome://extensions
3. F5 → "Attach to Chrome (Your Profile)"
```
- Use your actual profile
- Already logged in
- All your extensions

## Quick Start (Same as Before)

```
1. Close all Chrome windows
2. Press F5
3. Select "Launch Chrome Extension (Keep Login)"
4. Log in to Udio (first time)
5. Debug! ✅
```

## If Chrome Has Issues

Try Edge instead:
```
F5 → "Launch Edge Extension (Keep Login)"
```

## Configuration Details

### What Changed in launch.json
```json
// Added explicit runtime
"runtimeExecutable": "chrome"  // Uses stable Chrome

// Also added Edge support
{
  "name": "Launch Edge Extension (Keep Login)",
  "type": "msedge",
  ...
}
```

### What Changed in tasks.json
```json
// Uses chrome.exe explicitly
"command": "start chrome.exe --remote-debugging-port=9222 ..."

// Added Edge task
{
  "label": "Start Edge with Remote Debugging (Your Profile)",
  ...
}
```

## Browser Paths

### Chrome Stable
**Windows:** `chrome.exe` or `C:\Program Files\Google\Chrome\Application\chrome.exe`
**Mac:** `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
**Linux:** `google-chrome-stable`

### Edge
**Windows:** `msedge.exe` or `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`
**Mac:** `/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge`
**Linux:** `microsoft-edge-stable`

## Troubleshooting

### Chrome Won't Launch?

1. **Check Chrome is installed:**
   ```cmd
   where chrome
   ```

2. **Try Edge instead:**
   ```
   F5 → "Launch Edge Extension (Keep Login)"
   ```

3. **Specify full path:**
   Edit `.vscode/launch.json`:
   ```json
   "runtimeExecutable": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
   ```

### Chrome Still Buggy?

Use Edge:
```
F5 → "Launch Edge Extension (Keep Login)"
```

Edge is Chromium-based and works great for debugging!

## Summary

**What:** Now uses Chrome Stable instead of Chrome Dev

**Why:** More stable, fewer bugs

**Impact:** None! Same commands, better experience

**Alternative:** Edge available if Chrome has issues

**Recommended:**
```
F5 → "Launch Chrome Extension (Keep Login)"
```

---

**See Also:**
- [BROWSER_DEBUGGING.md](BROWSER_DEBUGGING.md) - Complete browser guide
- [DEBUGGING_QUICKSTART.md](DEBUGGING_QUICKSTART.md) - Quick start
- [STAY_LOGGED_IN.md](STAY_LOGGED_IN.md) - Stay logged in guide

**Status:** ✅ Updated and ready to use!
