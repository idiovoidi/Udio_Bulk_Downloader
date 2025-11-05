# Quick Reference Guide

## Module Cheat Sheet

### Import Patterns

```javascript
// Importing a class
import { FolderMapper } from '../modules/folder-mapper.js';
const mapper = new FolderMapper(logger, storage);

// Importing static utilities
import { DOMUtils } from '../modules/dom-utils.js';
await DOMUtils.sleep(1000);

// Importing from multiple modules
import { StorageManager } from '../modules/storage.js';
import { ExportUtils } from '../modules/export-utils.js';
```

### Common Tasks

#### Task: Add a new export format

1. Open `modules/export-utils.js`
2. Add new static method:
```javascript
static exportAsXML(libraryData) {
  // Your XML formatting logic
  const xml = this._buildXML(libraryData);
  const blob = new Blob([xml], { type: 'application/xml' });
  const url = URL.createObjectURL(blob);
  chrome.downloads.download({ url, filename: 'library.xml', saveAs: true });
}
```
3. Call from popup-controller.js:
```javascript
exportXML() {
  ExportUtils.exportAsXML(this.libraryData);
  this.ui.updateStatus('XML export started', 'success');
}
```

#### Task: Modify song extraction logic

1. Open `modules/song-extractor.js`
2. Find the relevant method (e.g., `_extractTitle`)
3. Modify the logic
4. Test with `dumpStructure` button

#### Task: Add new UI element

1. Add HTML to `popup-modular.html`
2. Add element reference in `popup/popup-main.js`:
```javascript
const elements = {
  // ... existing elements
  myNewButton: document.getElementById('myNewButton')
};
```
3. Add handler in `popup/popup-controller.js`:
```javascript
setupEventListeners() {
  // ... existing listeners
  this.ui.elements.myNewButton.addEventListener('click', () => this.handleNewButton());
}

handleNewButton() {
  // Your logic here
}
```

#### Task: Add new content script action

1. Open `content/message-handler.js`
2. Add new case:
```javascript
async handleMessage(request, sender, sendResponse) {
  const { action } = request;
  
  switch (action) {
    // ... existing cases
    
    case 'myNewAction':
      await this.handleMyNewAction(request.data);
      sendResponse({ status: 'success' });
      break;
  }
}

async handleMyNewAction(data) {
  // Your logic here
}
```
3. Call from popup:
```javascript
const response = await chrome.tabs.sendMessage(tabId, { 
  action: 'myNewAction',
  data: { /* ... */ }
});
```

## Module API Reference

### StorageManager

```javascript
const storage = new StorageManager();

// Save/load mapping state (popup)
await storage.saveMappingState({ inProgress: true, ... });
const state = await storage.loadMappingState();
await storage.clearMappingState();

// Save/load content state (content script)
await storage.saveContentState({ structure: { ... } });
const state = await storage.loadContentState();
await storage.clearContentState();

// Logs
await storage.saveLogs([...]);
const logs = await storage.loadLogs();
await storage.clearLogs();
```

### DOMUtils

```javascript
// Sleep/delay
await DOMUtils.sleep(1000); // 1 second

// Wait for element
const element = await DOMUtils.waitForElement('.my-selector', 5000);

// Get scroll container
const container = DOMUtils.getScrollContainer();

// Scroll to bottom with pagination
await DOMUtils.scrollToBottom(container, 50);

// Extract attributes/text
const attr = DOMUtils.extractAttribute(element, 'data-id');
const text = DOMUtils.extractText(element, '.title');
```

### FolderMapper

```javascript
const mapper = new FolderMapper(logger, storage);

// Start mapping
const structure = await mapper.startMapping();

// Get progress
const progress = mapper.getProgress();
// Returns: { inProgress: boolean, structure: {...} }
```

### SongExtractor

```javascript
const extractor = new SongExtractor(logger);

// Extract songs from current view
const songs = await extractor.extractSongsFromView();

// Extract data from single element
const song = extractor.extractSongData(element);
```

### ExportUtils

```javascript
// Export as JSON
ExportUtils.exportAsJson(libraryData);

// Export as text
ExportUtils.exportAsText(libraryData);

// Export checklist
ExportUtils.exportChecklist(libraryData);
```

### UIController

```javascript
const ui = new UIController(elements);

// Status messages
ui.updateStatus('Message', 'info');    // blue
ui.updateStatus('Success!', 'success'); // green
ui.updateStatus('Warning', 'warning');  // orange
ui.updateStatus('Error', 'error');      // red

// Progress
ui.updateProgress(50, 'Mapping 5/10 folders');
ui.hideProgress();

// Results
ui.displayResults(libraryData);

// Buttons
ui.setButtonState(button, true);  // disable
ui.setButtonState(button, false); // enable

// Polling
ui.startPolling(() => { /* callback */ }, 500);
ui.stopPolling();

// Logs
ui.showLogs(logs, stats);
ui.hideLogs();
const isHidden = ui.toggleLogs();
```

## Message Passing

### Popup → Content Script

```javascript
// popup-controller.js
const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
const response = await chrome.tabs.sendMessage(tab.id, {
  action: 'startMapping'
});
```

### Content Script → Popup

```javascript
// folder-mapper.js
chrome.runtime.sendMessage({
  action: 'progressUpdate',
  progress: { ... }
});

// popup-main.js
chrome.runtime.onMessage.addListener((message) => {
  if (message.action === 'progressUpdate') {
    // Handle update
  }
});
```

## Common Patterns

### Error Handling

```javascript
try {
  await someOperation();
} catch (error) {
  this.logger?.error('Operation failed', { error: error.message });
  this.ui.updateStatus(`Error: ${error.message}`, 'error');
  throw error; // Re-throw if needed
}
```

### Async/Await

```javascript
// Always use async/await for Chrome APIs
async function myFunction() {
  const [tab] = await chrome.tabs.query({ active: true });
  const response = await chrome.tabs.sendMessage(tab.id, { ... });
  await chrome.storage.local.set({ ... });
}
```

### Optional Chaining for Logger

```javascript
// Logger might not be available in all contexts
this.logger?.info('Message');
this.logger?.error('Error', { data });
```

### Dependency Injection

```javascript
// Good: Inject dependencies
class MyClass {
  constructor(logger, storage) {
    this.logger = logger;
    this.storage = storage;
  }
}

// Bad: Use globals
class MyClass {
  doSomething() {
    logger.info('...');  // Hard-coded dependency
  }
}
```

## Debugging Tips

### View Console Logs

```javascript
// Content script logs
// 1. Open udio.com
// 2. Press F12
// 3. Go to Console tab

// Popup logs
// 1. Right-click extension icon
// 2. Click "Inspect popup"
// 3. Go to Console tab

// Background logs
// 1. Go to chrome://extensions
// 2. Click "Inspect views: service worker"
```

### Use Diagnostics

```javascript
// Click "Dump Tree Structure" button
// Check console for detailed output
```

### Check Storage

```javascript
// In console
chrome.storage.local.get(null, (items) => {
  console.log('Storage:', items);
});
```

### Enable Verbose Logging

```javascript
// In logger.js, change log level
const logger = new ExtensionLogger(1000); // maxLogs

// Log everything
logger.debug('Debug message');
logger.info('Info message');
logger.success('Success message');
logger.warning('Warning message');
logger.error('Error message');
```

## File Locations

```
Need to modify...          Open this file...
─────────────────────────  ──────────────────────────────────
Folder mapping logic       modules/folder-mapper.js
Song extraction            modules/song-extractor.js
Export formats             modules/export-utils.js
UI updates                 modules/ui-controller.js
Storage operations         modules/storage.js
DOM utilities              modules/dom-utils.js
Content script entry       content/content-main.js
Message routing            content/message-handler.js
Debug tools                content/diagnostics.js
Popup entry                popup/popup-main.js
Popup logic                popup/popup-controller.js
Extension config           manifest-modular.json
UI layout                  popup-modular.html
Logging system             logger.js
```

## Testing Checklist

```
□ Extension loads without errors
□ Popup opens correctly
□ Content script loads on udio.com
□ "Map Library Structure" works
□ Progress updates display
□ Results show correctly
□ "Export as JSON" downloads file
□ "Export as Text" downloads file
□ "Export Checklist" downloads file
□ "Dump Tree Structure" logs to console
□ Logs display in popup
□ "Export Logs" downloads file
□ "Clear Logs" clears logs
□ No console errors
□ Page refresh preserves state
```

## Common Issues

### Issue: "Cannot use import statement outside a module"
**Fix:** Ensure manifest has `"type": "module"` for scripts

### Issue: "Module not found"
**Fix:** Check import path includes `.js` extension

### Issue: "logger is not defined"
**Fix:** Ensure logger.js is loaded before modules in manifest

### Issue: Extension doesn't work after changes
**Fix:** 
1. Go to chrome://extensions
2. Click reload button
3. Refresh udio.com page

### Issue: Popup doesn't update
**Fix:**
1. Close popup
2. Reload extension
3. Reopen popup

## Performance Tips

1. **Debounce storage writes**
   ```javascript
   debouncedSave = this.debounce(() => this.save(), 1000);
   ```

2. **Cache DOM queries**
   ```javascript
   const container = DOMUtils.getScrollContainer();
   // Reuse container, don't query again
   ```

3. **Throttle progress updates**
   ```javascript
   ui.startPolling(callback, 500); // Update every 500ms
   ```

4. **Use async/await properly**
   ```javascript
   // Good: Parallel
   const [a, b] = await Promise.all([fetchA(), fetchB()]);
   
   // Bad: Sequential
   const a = await fetchA();
   const b = await fetchB();
   ```

## Resources

- **Chrome Extension Docs:** https://developer.chrome.com/docs/extensions/
- **Manifest V3:** https://developer.chrome.com/docs/extensions/mv3/intro/
- **ES6 Modules:** https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules

## Quick Commands

```bash
# Load extension
chrome://extensions → Load unpacked → Select chrome_extension/

# Reload extension
chrome://extensions → Click reload button

# View logs
F12 → Console tab

# Clear storage
chrome.storage.local.clear()

# Package extension
zip -r udio-mapper.zip chrome_extension/
```

---

**Need more help?** Check the full documentation:
- `README_MODULAR.md` - Overview
- `ARCHITECTURE.md` - Detailed architecture
- `MIGRATION.md` - Migration guide
- `COMPARISON.md` - Before/after comparison
