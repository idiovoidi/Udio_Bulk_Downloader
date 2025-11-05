# Browser Debugging Options

## Chrome Stable vs Chrome Dev vs Edge

The debugging configuration now uses **Chrome Stable** (standard Chrome) instead of Chrome Dev to avoid bugs and issues.

## Available Browsers

### Chrome Stable (Recommended) ⭐
**What:** Your regular Chrome installation

**Pros:**
- ✅ Most stable
- ✅ Fewer bugs
- ✅ What users actually use
- ✅ Best compatibility

**Cons:**
- ⚠️ May need to close other Chrome windows

**Configurations:**
- `Launch Chrome Extension (Keep Login)`
- `Launch Chrome Extension (Temp Profile)`
- `Attach to Chrome (Your Profile)`

### Microsoft Edge (Alternative) ⭐⭐
**What:** Microsoft Edge (Chromium-based)

**Pros:**
- ✅ Very stable
- ✅ Excellent debugging tools
- ✅ Can run alongside Chrome
- ✅ Same extension compatibility

**Cons:**
- ⚠️ Need to install Edge DevTools extension

**Configurations:**
- `Launch Edge Extension (Keep Login)`
- `Attach to Edge (Your Profile)`

## Quick Start

### Option 1: Chrome Stable (Recommended)

```
1. Close all Chrome windows
2. Press F5
3. Select "Launch Chrome Extension (Keep Login)"
4. Chrome opens with extension
5. Log in to Udio (first time)
6. Debug! ✅
```

### Option 2: Microsoft Edge

```
1. Install Edge DevTools extension (VS Code will prompt)
2. Press F5
3. Select "Launch Edge Extension (Keep Login)"
4. Edge opens with extension
5. Log in to Udio (first time)
6. Debug! ✅
```

### Option 3: Attach to Your Chrome

```
1. Close all Chrome windows
2. Ctrl+Shift+P → "Tasks: Run Task"
3. Select "Start Chrome with Remote Debugging (Your Profile)"
4. Load extension at chrome://extensions
5. Press F5
6. Select "Attach to Chrome (Your Profile)"
7. Already logged in! ✅
8. Debug!
```

## Comparison

| Browser | Stability | Debugging | Can Run Alongside |
|---------|-----------|-----------|-------------------|
| **Chrome Stable** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ No |
| **Edge** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Yes |
| **Chrome Dev** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Yes |

## Why Chrome Stable?

### Issues with Chrome Dev
- Experimental features can cause bugs
- Less stable than stable channel
- May have compatibility issues
- Not what users actually use

### Benefits of Chrome Stable
- Most stable version
- What users actually use
- Best compatibility
- Fewer bugs and issues

## Using Edge Instead

If Chrome Stable has issues, Edge is an excellent alternative:

### Setup Edge Debugging

1. **Install Edge DevTools Extension**
   ```
   VS Code will prompt you
   Or: Extensions → Search "Edge DevTools"
   ```

2. **Launch Edge**
   ```
   F5 → "Launch Edge Extension (Keep Login)"
   ```

3. **Debug**
   ```
   Set breakpoints
   Use extension
   Debug! ✅
   ```

### Benefits of Edge
- ✅ Can run alongside Chrome
- ✅ Very stable
- ✅ Excellent debugging
- ✅ Same extension compatibility
- ✅ Built-in dev tools

## Configuration Details

### Chrome Stable Paths

**Windows:**
```
chrome.exe (in PATH)
or
C:\Program Files\Google\Chrome\Application\chrome.exe
```

**Mac:**
```
/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
```

**Linux:**
```
google-chrome-stable
or
/usr/bin/google-chrome-stable
```

### Edge Paths

**Windows:**
```
msedge.exe (in PATH)
or
C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
```

**Mac:**
```
/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge
```

**Linux:**
```
microsoft-edge-stable
```

## Troubleshooting

### Chrome Won't Launch?

**Problem:** "Cannot find Chrome"

**Solutions:**

1. **Check Chrome is installed:**
   ```cmd
   where chrome
   ```

2. **Specify full path in launch.json:**
   ```json
   "runtimeExecutable": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
   ```

3. **Try Edge instead:**
   ```
   F5 → "Launch Edge Extension (Keep Login)"
   ```

### Chrome Has Bugs?

**Problem:** Chrome crashing or buggy

**Solutions:**

1. **Use Edge instead:**
   ```
   F5 → "Launch Edge Extension (Keep Login)"
   ```

2. **Update Chrome:**
   ```
   chrome://settings/help
   ```

3. **Clear debug profile:**
   ```
   Delete .chrome-debug-persistent folder
   ```

### Can't Close Chrome?

**Problem:** Need Chrome open for other work

**Solutions:**

1. **Use Edge for debugging:**
   ```
   F5 → "Launch Edge Extension (Keep Login)"
   Keep Chrome open for other work ✅
   ```

2. **Use separate Chrome profile:**
   ```
   F5 → "Launch Chrome Extension (Keep Login)"
   Uses separate profile
   ```

## Recommended Setup

### For Most Users
```
Browser: Chrome Stable
Config: "Launch Chrome Extension (Keep Login)"

Why:
✅ Most stable
✅ What users use
✅ Login persists
✅ Fast debugging
```

### If Chrome Has Issues
```
Browser: Microsoft Edge
Config: "Launch Edge Extension (Keep Login)"

Why:
✅ Very stable
✅ Can run alongside Chrome
✅ Excellent debugging
✅ Login persists
```

### For Advanced Users
```
Browser: Chrome Stable
Config: "Attach to Chrome (Your Profile)"

Why:
✅ Use actual profile
✅ Already logged in
✅ All extensions
✅ All settings
```

## Quick Reference

### Launch Chrome (Keep Login)
```
F5 → "Launch Chrome Extension (Keep Login)"
```

### Launch Edge (Keep Login)
```
F5 → "Launch Edge Extension (Keep Login)"
```

### Attach to Your Chrome
```
1. Task: "Start Chrome with Remote Debugging (Your Profile)"
2. Load extension at chrome://extensions
3. F5 → "Attach to Chrome (Your Profile)"
```

### Attach to Your Edge
```
1. Task: "Start Edge with Remote Debugging (Your Profile)"
2. Load extension at edge://extensions
3. F5 → "Attach to Edge (Your Profile)"
```

## Browser-Specific Tips

### Chrome Stable
- Close all Chrome windows before debugging
- Uses standard Chrome installation
- Most compatible with extensions
- Best for production testing

### Microsoft Edge
- Can run alongside Chrome
- Excellent DevTools integration
- Very stable for debugging
- Good for parallel development

## Summary

**Default:** Chrome Stable (most stable, what users use)

**Alternative:** Microsoft Edge (can run alongside Chrome)

**Recommended:**
```
F5 → "Launch Chrome Extension (Keep Login)"
```

**If Chrome has issues:**
```
F5 → "Launch Edge Extension (Keep Login)"
```

**Benefits:**
- ✅ Stable browsers
- ✅ Fewer bugs
- ✅ Login persists
- ✅ Fast debugging
- ✅ Multiple options

---

**Note:** Configuration now uses Chrome Stable by default instead of Chrome Dev for better stability!
