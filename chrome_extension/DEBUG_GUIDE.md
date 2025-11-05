# Chrome Extension Debugging Guide

## VS Code F5 Debugging Setup

This project is configured for F5 debugging in VS Code!

## Prerequisites

1. **Install Chrome Debugger Extension**
   - VS Code will prompt you to install "Debugger for Chrome"
   - Or install manually: `msjsdiag.debugger-for-chrome`

2. **Close All Chrome Instances**
   - Chrome must not be running when you start debugging
   - Close all Chrome windows before pressing F5

## Quick Start

### Method 1: Launch & Debug (Recommended)
1. Press **F5** or click "Run > Start Debugging"
2. Select "Launch Chrome Extension" from dropdown
3. Chrome will open with extension loaded
4. Navigate to https://www.udio.com/library
5. Set breakpoints in your code
6. Use the extension - breakpoints will hit!

### Method 2: Attach to Running Chrome
1. Run task: "Start Chrome with Remote Debugging"
   - Press **Ctrl+Shift+P** → "Tasks: Run Task" → "Start Chrome with Remote Debugging"
2. Navigate to udio.com in the opened Chrome
3. Press **F5** and select "Attach to Chrome Extension"
4. Set breakpoints and debug!

## Debug Configurations

### 1. Launch Chrome Extension
**Use when:** Starting fresh debugging session

**What it does:**
- Launches Chrome with extension loaded
- Opens udio.com/library
- Enables source maps
- Creates clean debug profile

**How to use:**
```
1. Press F5
2. Select "Launch Chrome Extension"
3. Chrome opens automatically
4. Set breakpoints in VS Code
5. Use extension
```

### 2. Attach to Chrome Extension
**Use when:** Chrome already running with debugging enabled

**What it does:**
- Attaches to existing Chrome instance
- Debugs content scripts on udio.com
- Requires Chrome started with --remote-debugging-port=9222

**How to use:**
```
1. Start Chrome with debugging (use task)
2. Press F5
3. Select "Attach to Chrome Extension"
4. Set breakpoints
```

### 3. Debug Extension Popup
**Use when:** Debugging popup.js

**What it does:**
- Attaches to popup window
- Debugs popup scripts
- Requires Chrome with debugging enabled

**How to use:**
```
1. Start Chrome with debugging
2. Open extension popup
3. Press F5
4. Select "Debug Extension Popup"
5. Set breakpoints in popup code
```

### 4. Debug Content Script
**Use when:** Debugging content scripts on udio.com

**What it does:**
- Attaches to udio.com page
- Debugs content scripts
- Best for folder mapping and song extraction

**How to use:**
```
1. Start Chrome with debugging
2. Navigate to udio.com/library
3. Press F5
4. Select "Debug Content Script"
5. Set breakpoints in content scripts
```

### 5. Debug Extension (Full)
**Use when:** Debugging everything at once

**What it does:**
- Launches Chrome
- Attaches to popup
- Attaches to content scripts
- All-in-one debugging

**How to use:**
```
1. Press F5
2. Select "Debug Extension (Full)"
3. All debuggers attach
4. Debug any part of extension
```

## Setting Breakpoints

### In Content Scripts
```javascript
// chrome_extension/modules/folder-mapper.js
async startMapping() {
  debugger; // Breakpoint will hit here
  this.logger?.info('Starting folder tree mapping');
  // ...
}
```

### In Popup Scripts
```javascript
// chrome_extension/popup/popup-controller.js
async mapLibrary() {
  debugger; // Breakpoint will hit here
  this.ui.updateStatus('Starting mapping...', 'info');
  // ...
}
```

### In Song Extractor
```javascript
// chrome_extension/modules/song-extractor.js
async extractSongsFromView(folderPath = null) {
  debugger; // Breakpoint will hit here
  const songs = [];
  // ...
}
```

## Debugging Workflow

### Typical Session
```
1. Set breakpoints in VS Code
2. Press F5 → "Launch Chrome Extension"
3. Chrome opens with extension
4. Navigate to udio.com/library
5. Click extension icon
6. Click "Map Library Structure"
7. Breakpoints hit in VS Code!
8. Step through code (F10, F11)
9. Inspect variables
10. Continue (F5)
```

### Hot Reload
After making code changes:
```
1. Save files (Ctrl+S)
2. Go to chrome://extensions
3. Click reload button on extension
4. Refresh udio.com page
5. Continue debugging
```

## Debug Console

### Available in VS Code Debug Console
```javascript
// Inspect variables
this.folderCache
this.songExtractor.cache
this.structure

// Call methods
this.getCacheStats()
this.clearCache()

// Check state
this.inProgress
this.structure.totalSongs
```

### Chrome DevTools (Parallel)
You can also use Chrome DevTools:
```
1. Right-click extension icon → "Inspect popup"
2. F12 on udio.com page
3. Use Console, Network, Elements tabs
4. Works alongside VS Code debugger
```

## Common Debugging Scenarios

### Debug Folder Mapping
```javascript
// Set breakpoint in folder-mapper.js
async _processFolderItem(item, parentPath) {
  debugger; // Hit here for each folder
  const folderName = nameButton.getAttribute('title');
  // Step through to see folder processing
}
```

### Debug Song Extraction
```javascript
// Set breakpoint in song-extractor.js
async extractSongsFromView(folderPath = null) {
  debugger; // Hit here when extracting songs
  
  // Watch variables:
  // - songs array
  // - seenUrls set
  // - attempts counter
}
```

### Debug Scroll Logic
```javascript
// Set breakpoint in scroll loop
while (attempts < maxAttempts) {
  debugger; // Hit here each scroll
  
  // Inspect:
  // - currentCount
  // - distanceFromBottom
  // - isAtBottom
}
```

### Debug Cache
```javascript
// Set breakpoint in cache check
if (this.cache.has(cacheKey)) {
  debugger; // Hit here on cache hit
  return this.cache.get(cacheKey);
}
```

## Troubleshooting

### Breakpoints Not Hitting

**Problem:** Breakpoints show as gray/unverified

**Solutions:**
1. Check source maps are enabled
2. Verify file paths match
3. Reload extension in Chrome
4. Restart debugging session

### Chrome Won't Launch

**Problem:** "Cannot connect to runtime process"

**Solutions:**
1. Close all Chrome instances
2. Kill Chrome processes in Task Manager
3. Delete `.chrome-debug-profile` folder
4. Try again

### Can't Attach to Chrome

**Problem:** "Cannot connect to the target"

**Solutions:**
1. Verify Chrome started with `--remote-debugging-port=9222`
2. Check no other process using port 9222
3. Try different port (9223, 9224)
4. Restart Chrome with debugging

### Source Maps Not Working

**Problem:** Can't see original source code

**Solutions:**
1. Verify `"sourceMaps": true` in launch.json
2. Check file paths in pathMapping
3. Ensure no build step modifying files
4. Use ES6 modules (already configured)

## Advanced Debugging

### Conditional Breakpoints
```javascript
// Right-click breakpoint → Edit Breakpoint
// Condition: attempts > 50
// Only breaks when condition is true
```

### Logpoints
```javascript
// Right-click line → Add Logpoint
// Message: "Song count: {currentCount}"
// Logs without stopping execution
```

### Watch Expressions
```
Add to Watch panel:
- this.structure.totalSongs
- this.folderCache.size
- this.songExtractor.cache.size
- attempts
```

### Call Stack
```
When breakpoint hits:
1. View Call Stack panel
2. See function call hierarchy
3. Click frames to navigate
4. Inspect variables at each level
```

## Performance Profiling

### Using Chrome DevTools
```
1. Open DevTools (F12)
2. Go to Performance tab
3. Click Record
4. Use extension
5. Stop recording
6. Analyze timeline
```

### Memory Profiling
```
1. Open DevTools
2. Go to Memory tab
3. Take heap snapshot
4. Use extension
5. Take another snapshot
6. Compare to find leaks
```

## Tips & Tricks

### Quick Debugging
```
1. Use `debugger;` statement for quick breakpoints
2. Use console.log() for quick inspection
3. Use logger for persistent logs
4. Check "Pause on exceptions" for errors
```

### Efficient Workflow
```
1. Set breakpoints before starting
2. Use "Continue to here" (right-click line)
3. Use "Restart frame" to re-run function
4. Use "Step over" (F10) for quick navigation
5. Use "Step into" (F11) for deep dive
```

### Multi-File Debugging
```
1. Set breakpoints in multiple files
2. Use "Debug Extension (Full)" config
3. All breakpoints will hit
4. Navigate between files easily
```

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Start Debugging | F5 |
| Stop Debugging | Shift+F5 |
| Restart | Ctrl+Shift+F5 |
| Continue | F5 |
| Step Over | F10 |
| Step Into | F11 |
| Step Out | Shift+F11 |
| Toggle Breakpoint | F9 |

## Resources

- [VS Code Debugging](https://code.visualstudio.com/docs/editor/debugging)
- [Chrome DevTools](https://developer.chrome.com/docs/devtools/)
- [Chrome Extension Debugging](https://developer.chrome.com/docs/extensions/mv3/tut_debugging/)

## Quick Reference

### Start Debugging
```
F5 → "Launch Chrome Extension"
```

### Set Breakpoint
```
Click left margin or press F9
```

### Inspect Variable
```
Hover over variable or add to Watch
```

### Continue Execution
```
Press F5 or click Continue button
```

### Stop Debugging
```
Press Shift+F5 or click Stop button
```

---

**Happy Debugging!** 🐛🔍

**Tip:** Start with "Launch Chrome Extension" config for easiest setup!
