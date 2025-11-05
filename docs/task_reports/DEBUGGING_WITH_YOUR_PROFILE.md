# Debugging With Your Chrome Profile (Stay Logged In)

## Problem
The default debug configuration uses a temporary profile, so you lose your Udio login each time.

## Solution: 3 Options

### Option 1: Persistent Debug Profile (Recommended) ⭐

**Best for:** Rapid debugging while staying logged in

**Setup (One Time):**
1. Press **F5**
2. Select **"Launch Chrome Extension (Keep Login)"**
3. Chrome opens with extension
4. Log in to Udio
5. Your login persists across debug sessions!

**Usage:**
```
1. Press F5
2. Select "Launch Chrome Extension (Keep Login)"
3. Already logged in! ✅
4. Debug away!
```

**Profile Location:** `.chrome-debug-persistent/` (gitignored)

---

### Option 2: Attach to Your Existing Chrome ⭐⭐

**Best for:** Using your actual Chrome profile with all extensions and settings

**Setup:**

#### Step 1: Close ALL Chrome Windows
```
Close every Chrome window
Check Task Manager - kill any Chrome processes
```

#### Step 2: Start Chrome with Remote Debugging

**Windows:**
```cmd
# Option A: Use VS Code Task (Easiest)
Ctrl+Shift+P → "Tasks: Run Task" → "Start Chrome with Remote Debugging (Your Profile)"

# Option B: Command Line
start chrome --remote-debugging-port=9222
```

**Mac:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 &
```

**Linux:**
```bash
google-chrome --remote-debugging-port=9222 &
```

#### Step 3: Load Extension Manually
```
1. Go to chrome://extensions
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select: chrome_extension folder
```

#### Step 4: Attach Debugger
```
1. Navigate to udio.com/library
2. Press F5 in VS Code
3. Select "Attach to Chrome (Your Profile)"
4. Set breakpoints
5. Debug! ✅
```

**Advantages:**
- ✅ Use your actual Chrome profile
- ✅ Already logged in to Udio
- ✅ All your extensions available
- ✅ All your bookmarks and settings

**Disadvantages:**
- ⚠️ Must manually load extension
- ⚠️ Must start Chrome with special flag
- ⚠️ Can't use other Chrome instances while debugging

---

### Option 3: Manual Extension Load

**Best for:** Quick testing without debugger

**Setup:**
```
1. Open your normal Chrome
2. Go to chrome://extensions
3. Enable "Developer mode"
4. Click "Load unpacked"
5. Select: chrome_extension folder
6. Use extension normally (already logged in!)
```

**For debugging:**
- Use Chrome DevTools (F12)
- Right-click extension icon → "Inspect popup"
- Console logs and breakpoints work
- No VS Code integration

---

## Comparison

| Method | Login Persists | VS Code Debug | Your Profile | Setup |
|--------|---------------|---------------|--------------|-------|
| **Temp Profile** | ❌ No | ✅ Yes | ❌ No | Easy |
| **Persistent Profile** | ✅ Yes | ✅ Yes | ⚠️ Separate | Easy |
| **Attach to Your Chrome** | ✅ Yes | ✅ Yes | ✅ Yes | Medium |
| **Manual Load** | ✅ Yes | ⚠️ DevTools only | ✅ Yes | Easy |

## Recommended Workflow

### For Rapid Development (Recommended)
```
Use: "Launch Chrome Extension (Keep Login)"

1. First time: Log in to Udio
2. Every debug session: Already logged in!
3. Fast iteration with F5
```

### For Testing with Real Profile
```
Use: "Attach to Chrome (Your Profile)"

1. Start Chrome with debugging (one-time per session)
2. Load extension manually (one-time per session)
3. Attach debugger (F5)
4. Debug with your actual profile
```

## Step-by-Step: Attach to Your Chrome

### 1. Close All Chrome
```
- Close all Chrome windows
- Check Task Manager
- Kill any Chrome.exe processes
```

### 2. Start Chrome with Debugging

**Easy Way (VS Code Task):**
```
1. Press Ctrl+Shift+P
2. Type "Tasks: Run Task"
3. Select "Start Chrome with Remote Debugging (Your Profile)"
4. Chrome opens with debugging enabled
```

**Manual Way (Command Line):**
```cmd
# Windows
start chrome --remote-debugging-port=9222

# Mac
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 &

# Linux
google-chrome --remote-debugging-port=9222 &
```

### 3. Load Extension
```
1. Go to chrome://extensions
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Navigate to: chrome_extension folder
5. Click "Select Folder"
6. Extension loaded! ✅
```

### 4. Navigate to Udio
```
1. Go to https://www.udio.com/library
2. You're already logged in! ✅
```

### 5. Attach Debugger
```
1. In VS Code, press F5
2. Select "Attach to Chrome (Your Profile)"
3. Debugger attaches
4. Set breakpoints
5. Use extension - breakpoints hit! 🎯
```

### 6. Debug!
```
- Set breakpoints in VS Code
- Click extension icon
- Click "Map Library Structure"
- Breakpoints hit in VS Code
- Step through code
- Inspect variables
```

## Troubleshooting

### Can't Attach to Chrome?

**Error:** "Cannot connect to the target"

**Solutions:**
1. Verify Chrome started with `--remote-debugging-port=9222`
2. Check no other process using port 9222:
   ```cmd
   netstat -ano | findstr :9222
   ```
3. Try different port (9223):
   ```cmd
   start chrome --remote-debugging-port=9223
   ```
   Then update launch.json port to 9223

### Extension Not Loading?

**Problem:** Extension doesn't appear in chrome://extensions

**Solutions:**
1. Check "Developer mode" is enabled
2. Verify path to chrome_extension folder
3. Check manifest.json is valid
4. Look for errors in chrome://extensions

### Breakpoints Not Hitting?

**Problem:** Breakpoints gray/unverified

**Solutions:**
1. Reload extension in chrome://extensions
2. Refresh udio.com page
3. Restart debugger (Shift+F5, then F5)
4. Check source maps enabled

### Chrome Won't Start with Debugging?

**Problem:** Chrome opens but debugging doesn't work

**Solutions:**
1. Close ALL Chrome windows first
2. Kill Chrome processes in Task Manager
3. Try command line instead of task
4. Check firewall not blocking port 9222

## Quick Reference

### Start Chrome with Your Profile + Debugging
```cmd
# Windows
start chrome --remote-debugging-port=9222

# Then load extension manually at chrome://extensions
```

### Attach Debugger
```
F5 → "Attach to Chrome (Your Profile)"
```

### Reload Extension After Changes
```
1. chrome://extensions → Click reload
2. Refresh udio.com page
3. Continue debugging
```

## Best Practices

### For Daily Development
1. Use **"Launch Chrome Extension (Keep Login)"**
2. Log in once
3. Debug sessions keep you logged in
4. Fast iteration

### For Testing with Real Data
1. Use **"Attach to Chrome (Your Profile)"**
2. Start Chrome with debugging
3. Load extension manually
4. Attach debugger
5. Test with your actual profile

### For Quick Tests
1. Load extension in normal Chrome
2. Use Chrome DevTools (F12)
3. No VS Code needed
4. Quick and simple

## Summary

**Recommended for You:**
```
Use: "Launch Chrome Extension (Keep Login)"

Why:
✅ Login persists across sessions
✅ Fast F5 debugging
✅ No manual steps
✅ Best for rapid development

Setup:
1. F5 → "Launch Chrome Extension (Keep Login)"
2. Log in to Udio (first time only)
3. Debug away!
```

**Alternative (Your Actual Profile):**
```
Use: "Attach to Chrome (Your Profile)"

Why:
✅ Your actual Chrome profile
✅ All extensions and settings
✅ Already logged in

Setup:
1. Start Chrome with debugging (task or command)
2. Load extension at chrome://extensions
3. F5 → "Attach to Chrome (Your Profile)"
4. Debug!
```

---

**Profile Locations:**
- Temp: `.chrome-debug-profile/` (cleared each time)
- Persistent: `.chrome-debug-persistent/` (kept, gitignored)
- Your Profile: Default Chrome location (untouched)

**Recommendation:** Start with **"Launch Chrome Extension (Keep Login)"** for easiest workflow!
