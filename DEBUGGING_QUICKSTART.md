# 🐛 Debugging Quick Start

## F5 Debugging is Now Configured! 🎉

You can now debug the Chrome extension directly from VS Code.

## Quick Start (30 seconds)

### 1. Install Chrome Debugger
VS Code will prompt you to install the recommended extension:
- Click "Install" when prompted
- Or: Extensions → Search "Debugger for Chrome" → Install

### 2. Close Chrome
- Close ALL Chrome windows
- Check Task Manager to ensure Chrome is closed

### 3. Press F5
- Press **F5** in VS Code
- Select **"Launch Chrome Extension"** from dropdown
- Chrome will open with the extension loaded

### 4. Set Breakpoints
- Open any file (e.g., `chrome_extension/modules/folder-mapper.js`)
- Click left margin to set breakpoint (red dot)
- Or press **F9** on a line

### 5. Use Extension
- Chrome opens at udio.com/library
- Click extension icon
- Click "Map Library Structure"
- **Breakpoint hits in VS Code!** 🎯

## Debug Configurations

| Config | Use Case | How to Start |
|--------|----------|--------------|
| **Launch Chrome Extension** | Start fresh | F5 → Select this |
| **Attach to Chrome Extension** | Chrome already running | F5 → Select this |
| **Debug Extension Popup** | Debug popup.js | F5 → Select this |
| **Debug Content Script** | Debug content scripts | F5 → Select this |
| **Debug Extension (Full)** | Debug everything | F5 → Select this |

## Common Debugging Tasks

### Debug Folder Mapping
```javascript
// chrome_extension/modules/folder-mapper.js
async startMapping() {
  debugger; // ← Set breakpoint here
  // Step through folder processing
}
```

### Debug Song Extraction
```javascript
// chrome_extension/modules/song-extractor.js
async extractSongsFromView(folderPath = null) {
  debugger; // ← Set breakpoint here
  // Watch: songs, attempts, currentCount
}
```

### Debug Scroll Logic
```javascript
// In the scroll loop
while (attempts < maxAttempts) {
  debugger; // ← Set breakpoint here
  // Inspect: isAtBottom, noNewCount, distanceFromBottom
}
```

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Start Debugging | **F5** |
| Stop Debugging | **Shift+F5** |
| Continue | **F5** |
| Step Over | **F10** |
| Step Into | **F11** |
| Step Out | **Shift+F11** |
| Toggle Breakpoint | **F9** |

## Debugging Workflow

```
1. Set breakpoints (F9)
2. Press F5 → "Launch Chrome Extension"
3. Chrome opens with extension
4. Use extension
5. Breakpoint hits!
6. Inspect variables (hover or Watch panel)
7. Step through code (F10/F11)
8. Continue (F5)
```

## After Code Changes

```
1. Save files (Ctrl+S)
2. Go to chrome://extensions in Chrome
3. Click reload button on extension
4. Refresh udio.com page
5. Continue debugging
```

## Troubleshooting

### Breakpoints Not Hitting?
1. Reload extension in Chrome (chrome://extensions)
2. Refresh udio.com page
3. Restart debugging (Shift+F5, then F5)

### Chrome Won't Launch?
1. Close ALL Chrome windows
2. Check Task Manager - kill Chrome processes
3. Delete `.chrome-debug-profile` folder
4. Try again (F5)

### Can't Attach?
1. Make sure Chrome started with debugging enabled
2. Run task: "Start Chrome with Remote Debugging"
3. Then F5 → "Attach to Chrome Extension"

## Tips

### Quick Breakpoint
```javascript
debugger; // Add this line anywhere
```

### Watch Variables
```
Add to Watch panel:
- this.structure.totalSongs
- this.folderCache.size
- attempts
```

### Conditional Breakpoint
```
Right-click breakpoint → Edit Breakpoint
Condition: attempts > 50
```

### Logpoint (No Stop)
```
Right-click line → Add Logpoint
Message: "Songs: {currentCount}"
```

## Debug Console

When breakpoint hits, use Debug Console:
```javascript
// Inspect
this.structure
this.folderCache
this.songExtractor.cache

// Call methods
this.getCacheStats()
this.clearCache()

// Check state
this.inProgress
```

## Full Documentation

See **[chrome_extension/DEBUG_GUIDE.md](chrome_extension/DEBUG_GUIDE.md)** for complete guide.

## Example Session

```
1. Open folder-mapper.js
2. Set breakpoint on line: this.logger?.info('Starting folder tree mapping');
3. Press F5 → "Launch Chrome Extension"
4. Chrome opens at udio.com/library
5. Click extension icon
6. Click "Map Library Structure"
7. Breakpoint hits! 🎯
8. Inspect this.structure in Watch panel
9. Press F10 to step through
10. Press F5 to continue
```

## What You Can Debug

✅ Folder mapping logic
✅ Song extraction
✅ Scroll detection
✅ Cache operations
✅ Export functions
✅ UI updates
✅ Message passing
✅ Storage operations

## Resources

- **Full Guide:** [chrome_extension/DEBUG_GUIDE.md](chrome_extension/DEBUG_GUIDE.md)
- **VS Code Debugging:** https://code.visualstudio.com/docs/editor/debugging
- **Chrome DevTools:** https://developer.chrome.com/docs/devtools/

---

**Ready to debug?** Press **F5** and select **"Launch Chrome Extension"**! 🚀
