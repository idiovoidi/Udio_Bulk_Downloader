# 🔐 Stay Logged In While Debugging

## Problem Solved! ✅

You can now debug while staying logged in to Udio!

## Quick Answer

**Use this debug configuration:**
```
F5 → "Launch Chrome Extension (Keep Login)"
```

**First time:**
1. Press F5
2. Select "Launch Chrome Extension (Keep Login)"
3. Log in to Udio
4. Debug!

**Every time after:**
1. Press F5
2. Select "Launch Chrome Extension (Keep Login)"
3. **Already logged in!** ✅
4. Debug!

## How It Works

### Persistent Profile
- Uses `.chrome-debug-persistent/` folder
- Keeps cookies, sessions, and login state
- Separate from your main Chrome profile
- Gitignored (not committed)

### Your Login Persists
- Log in once
- Stays logged in across debug sessions
- No need to re-login each time
- Fast iteration!

## 3 Options Available

### Option 1: Persistent Debug Profile (Recommended) ⭐
```
Config: "Launch Chrome Extension (Keep Login)"

Pros:
✅ Login persists
✅ Fast F5 debugging
✅ No manual steps
✅ Best for rapid development

Setup:
1. F5 → "Launch Chrome Extension (Keep Login)"
2. Log in to Udio (first time)
3. Done! Login persists
```

### Option 2: Attach to Your Actual Chrome Profile ⭐⭐
```
Config: "Attach to Chrome (Your Profile)"

Pros:
✅ Your actual Chrome profile
✅ All extensions and settings
✅ Already logged in

Setup:
1. Start Chrome with debugging:
   Ctrl+Shift+P → "Tasks: Run Task" → 
   "Start Chrome with Remote Debugging (Your Profile)"
2. Load extension at chrome://extensions
3. F5 → "Attach to Chrome (Your Profile)"
4. Debug!
```

### Option 3: Temp Profile (Clean Slate)
```
Config: "Launch Chrome Extension (Temp Profile)"

Pros:
✅ Clean slate each time
✅ No leftover data

Cons:
❌ Must log in each time
❌ Slower for rapid debugging
```

## Comparison

| Method | Login Persists | Setup | Speed |
|--------|---------------|-------|-------|
| **Keep Login** ⭐ | ✅ Yes | Easy | Fast |
| **Your Profile** | ✅ Yes | Medium | Fast |
| **Temp Profile** | ❌ No | Easy | Slow |

## Recommended Workflow

### For You (Rapid Debugging)
```
Use: "Launch Chrome Extension (Keep Login)"

Workflow:
1. F5 → "Launch Chrome Extension (Keep Login)"
2. First time: Log in to Udio
3. Set breakpoints
4. Debug!
5. Make changes
6. F5 again → Still logged in! ✅
7. Repeat steps 5-6 rapidly
```

### Benefits
- ✅ No re-login needed
- ✅ Fast iteration
- ✅ Simple workflow
- ✅ Persistent session

## Step-by-Step

### First Debug Session
```
1. Press F5
2. Select "Launch Chrome Extension (Keep Login)"
3. Chrome opens at udio.com/library
4. Log in to Udio
5. Set breakpoints in VS Code
6. Click extension → "Map Library Structure"
7. Breakpoints hit! 🎯
8. Debug away!
```

### Subsequent Sessions
```
1. Press F5
2. Select "Launch Chrome Extension (Keep Login)"
3. Chrome opens at udio.com/library
4. Already logged in! ✅
5. Set breakpoints
6. Use extension
7. Debug!
```

### After Code Changes
```
1. Save files (Ctrl+S)
2. Shift+F5 (stop debugging)
3. F5 (start debugging)
4. Select "Launch Chrome Extension (Keep Login)"
5. Still logged in! ✅
6. Test changes
```

## Profile Locations

```
Temp Profile:
.chrome-debug-profile/
- Cleared each time
- Must log in each time

Persistent Profile:
.chrome-debug-persistent/
- Kept across sessions ✅
- Login persists ✅
- Gitignored

Your Profile:
Default Chrome location
- Your actual profile
- Requires manual setup
```

## Troubleshooting

### Lost Login?

**Problem:** Had to log in again

**Cause:** Used "Temp Profile" instead of "Keep Login"

**Solution:** Use "Launch Chrome Extension (Keep Login)"

### Can't Find "Keep Login" Config?

**Problem:** Don't see the option

**Solution:** 
1. Check `.vscode/launch.json` exists
2. Reload VS Code window
3. Press F5 → Should see all configs

### Profile Corrupted?

**Problem:** Login not working, errors

**Solution:**
1. Delete `.chrome-debug-persistent` folder
2. F5 → "Launch Chrome Extension (Keep Login)"
3. Log in again
4. Fresh start!

## Advanced: Use Your Actual Profile

If you want to use your actual Chrome profile with all your extensions:

### Setup
```
1. Close ALL Chrome windows
2. Ctrl+Shift+P → "Tasks: Run Task"
3. Select "Start Chrome with Remote Debugging (Your Profile)"
4. Chrome opens with debugging enabled
5. Go to chrome://extensions
6. Load unpacked → Select chrome_extension folder
7. Navigate to udio.com/library (already logged in!)
8. F5 → "Attach to Chrome (Your Profile)"
9. Debug!
```

### Benefits
- ✅ Your actual profile
- ✅ All your extensions
- ✅ All your bookmarks
- ✅ Already logged in

### Drawbacks
- ⚠️ More setup steps
- ⚠️ Must manually load extension
- ⚠️ Can't use other Chrome while debugging

## Quick Reference

### Stay Logged In (Recommended)
```
F5 → "Launch Chrome Extension (Keep Login)"
```

### Use Your Actual Profile
```
1. Task: "Start Chrome with Remote Debugging (Your Profile)"
2. Load extension at chrome://extensions
3. F5 → "Attach to Chrome (Your Profile)"
```

### Clean Slate (No Login)
```
F5 → "Launch Chrome Extension (Temp Profile)"
```

## Summary

**Problem:** Temp profile loses login each time
**Solution:** Use persistent profile or attach to your Chrome

**Recommended:**
```
F5 → "Launch Chrome Extension (Keep Login)"
```

**Benefits:**
- ✅ Login persists
- ✅ Fast debugging
- ✅ No manual steps
- ✅ Perfect for rapid development

**First time:** Log in to Udio
**Every time after:** Already logged in! ✅

---

**See Also:**
- [DEBUGGING_WITH_YOUR_PROFILE.md](DEBUGGING_WITH_YOUR_PROFILE.md) - Complete guide
- [DEBUGGING_QUICKSTART.md](DEBUGGING_QUICKSTART.md) - Quick start

**Recommendation:** Use **"Launch Chrome Extension (Keep Login)"** for best experience!
