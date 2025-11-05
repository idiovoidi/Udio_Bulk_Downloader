# Architecture Documentation

## System Overview

The Udio Library Mapper is a Chrome extension that maps and exports the folder structure and songs from a user's Udio library. The extension has been refactored from a monolithic architecture to a modular, maintainable structure.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Chrome Extension                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │   Popup UI   │◄────────┤  Background  │                  │
│  │  (popup.html)│         │   Worker     │                  │
│  └──────┬───────┘         └──────────────┘                  │
│         │                                                     │
│         │ Messages                                            │
│         ▼                                                     │
│  ┌──────────────────────────────────────┐                   │
│  │        Content Script                 │                   │
│  │    (Runs on udio.com pages)          │                   │
│  └──────────────────────────────────────┘                   │
│         │                                                     │
│         │ DOM Manipulation                                    │
│         ▼                                                     │
│  ┌──────────────────────────────────────┐                   │
│  │         Udio.com Website              │                   │
│  │    (Folder Tree, Song Lists)          │                   │
│  └──────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

## Module Architecture

### Layer 1: Core Modules (Shared)

```
modules/
├── storage.js          # Data persistence layer
├── dom-utils.js        # DOM manipulation utilities
├── folder-mapper.js    # Business logic: folder mapping
├── song-extractor.js   # Business logic: song extraction
├── export-utils.js     # Business logic: export operations
└── ui-controller.js    # Presentation: UI state management
```

**Responsibilities:**
- Encapsulate business logic
- Provide reusable functionality
- No direct DOM dependencies (except dom-utils)
- Testable in isolation

### Layer 2: Content Script

```
content/
├── content-main.js     # Entry point, initialization
├── message-handler.js  # Message routing from popup
└── diagnostics.js      # Debug and diagnostic tools
```

**Responsibilities:**
- Initialize modules
- Handle messages from popup
- Interact with page DOM
- Coordinate folder mapping workflow

### Layer 3: Popup Script

```
popup/
├── popup-main.js       # Entry point, DOM binding
└── popup-controller.js # Orchestration, user interactions
```

**Responsibilities:**
- Handle user interactions
- Display results and progress
- Coordinate export operations
- Manage UI state

### Layer 4: Infrastructure

```
logger.js               # Logging system (global)
background.js           # Background service worker
manifest.json           # Extension configuration
popup.html              # UI markup
```

## Data Flow

### 1. Mapping Workflow

```
User clicks "Map Library"
    ↓
popup-controller.js
    ↓ chrome.tabs.sendMessage
content-main.js (receives message)
    ↓
message-handler.js (routes to mapper)
    ↓
folder-mapper.js (starts mapping)
    ├─→ dom-utils.js (DOM queries)
    ├─→ song-extractor.js (extract songs)
    └─→ storage.js (save state)
    ↓
folder-mapper.js (sends progress updates)
    ↓ chrome.runtime.sendMessage
popup-controller.js (updates UI)
    ↓
ui-controller.js (renders progress)
```

### 2. Export Workflow

```
User clicks "Export Checklist"
    ↓
popup-controller.js
    ↓
export-utils.js (formats data)
    ↓
chrome.downloads.download
    ↓
File saved to disk
```

## Module Dependencies

```
┌─────────────────┐
│  popup-main.js  │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ popup-controller.js │
└────────┬────────────┘
         │
         ├─→ ui-controller.js
         ├─→ export-utils.js
         └─→ storage.js

┌──────────────────┐
│ content-main.js  │
└────────┬─────────┘
         │
         ├─→ folder-mapper.js
         │   ├─→ song-extractor.js
         │   │   └─→ dom-utils.js
         │   └─→ storage.js
         │
         ├─→ message-handler.js
         └─→ diagnostics.js
             └─→ dom-utils.js
```

## State Management

### Storage Keys

| Key | Scope | Purpose |
|-----|-------|---------|
| `mappingState` | Popup | Tracks mapping progress for UI |
| `contentMappingState` | Content | Persists mapping state across page reloads |
| `extensionLogs` | Global | Stores debug logs |

### State Flow

```
Content Script State:
    ↓ storage.saveContentState()
chrome.storage.local
    ↓ storage.loadContentState()
Content Script State (restored)

Popup State:
    ↓ storage.saveMappingState()
chrome.storage.local
    ↓ storage.loadMappingState()
Popup State (restored)
```

## Communication Patterns

### 1. Popup → Content Script

```javascript
// popup-controller.js
chrome.tabs.sendMessage(tabId, { 
  action: 'startMapping' 
});

// message-handler.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'startMapping') {
    folderMapper.startMapping();
    sendResponse({ status: 'started' });
  }
});
```

### 2. Content Script → Popup

```javascript
// folder-mapper.js
chrome.runtime.sendMessage({
  action: 'progressUpdate',
  progress: { ... }
});

// popup-main.js
chrome.runtime.onMessage.addListener((message) => {
  if (message.action === 'progressUpdate') {
    controller.handleProgress(message.progress);
  }
});
```

### 3. Module → Module

```javascript
// folder-mapper.js
import { SongExtractor } from './song-extractor.js';

class FolderMapper {
  constructor(logger, storage) {
    this.songExtractor = new SongExtractor(logger);
  }
}
```

## Design Patterns

### 1. Dependency Injection

```javascript
// Inject dependencies for testability
class FolderMapper {
  constructor(logger, storage) {
    this.logger = logger;
    this.storage = storage;
  }
}

// Usage
const mapper = new FolderMapper(logger, storage);
```

### 2. Single Responsibility Principle

Each module has one clear purpose:
- `folder-mapper.js` - Only maps folders
- `song-extractor.js` - Only extracts songs
- `export-utils.js` - Only handles exports

### 3. Facade Pattern

```javascript
// export-utils.js provides simple interface
ExportUtils.exportAsJson(data);
ExportUtils.exportAsText(data);
ExportUtils.exportChecklist(data);

// Hides complex formatting logic
```

### 4. Observer Pattern

```javascript
// Content script sends progress updates
chrome.runtime.sendMessage({ action: 'progressUpdate', ... });

// Popup listens for updates
chrome.runtime.onMessage.addListener((message) => {
  // React to updates
});
```

## Error Handling Strategy

### 1. Module Level

```javascript
class FolderMapper {
  async startMapping() {
    try {
      // Mapping logic
    } catch (error) {
      this.logger?.error('Mapping failed', { error: error.message });
      this._sendErrorMessage(error.message);
      throw error; // Propagate up
    }
  }
}
```

### 2. Controller Level

```javascript
class PopupController {
  async mapLibrary() {
    try {
      await this.startMapping();
    } catch (error) {
      this.ui.updateStatus(`Error: ${error.message}`, 'error');
      this.ui.hideProgress();
    }
  }
}
```

### 3. User Level

```javascript
// Show user-friendly messages
this.ui.updateStatus('⚠️ Please REFRESH the page (F5) and try again', 'warning');
```

## Performance Considerations

### 1. Lazy Loading
- Modules loaded only when needed
- ES6 modules enable tree-shaking

### 2. Debouncing
```javascript
// storage.js
debouncedSave = this.debounce(() => this.saveLogs(), 1000);
```

### 3. Efficient DOM Queries
```javascript
// Cache selectors
const container = DOMUtils.getScrollContainer();

// Batch DOM updates
songs.forEach(song => song.folderPath = currentPath);
```

### 4. Progress Throttling
```javascript
// Update UI every 500ms, not on every change
this.ui.startPolling(callback, 500);
```

## Security Considerations

### 1. Content Security Policy
- No inline scripts
- All scripts loaded from extension files

### 2. Permissions
```json
{
  "permissions": ["activeTab", "storage", "downloads"],
  "host_permissions": ["https://www.udio.com/*"]
}
```

### 3. Data Sanitization
```javascript
// Sanitize filenames
function sanitizeFilename(filename) {
  return filename
    .replace(/[<>:"/\\|?*]/g, '_')
    .substring(0, 200);
}
```

## Testing Strategy

### 1. Unit Tests (Future)
```javascript
// Test individual modules
import { DOMUtils } from './dom-utils.js';

test('sleep waits correct duration', async () => {
  const start = Date.now();
  await DOMUtils.sleep(100);
  const duration = Date.now() - start;
  expect(duration).toBeGreaterThanOrEqual(100);
});
```

### 2. Integration Tests (Future)
```javascript
// Test module interactions
const storage = new StorageManager();
const mapper = new FolderMapper(null, storage);
await mapper.startMapping();
expect(mapper.structure.folders.length).toBeGreaterThan(0);
```

### 3. Manual Testing
- Load extension in Chrome
- Test on udio.com/library
- Verify all features work
- Check console for errors

## Deployment

### 1. Development
```bash
# Load unpacked extension
chrome://extensions → Load unpacked → Select chrome_extension/
```

### 2. Production
```bash
# Package extension
zip -r udio-mapper.zip chrome_extension/
# Upload to Chrome Web Store
```

## Future Enhancements

### 1. TypeScript Migration
- Add type safety
- Better IDE support
- Catch errors at compile time

### 2. Build System
- Webpack/Rollup for bundling
- Minification for production
- Source maps for debugging

### 3. Automated Testing
- Jest for unit tests
- Playwright for E2E tests
- CI/CD pipeline

### 4. Advanced Features
- Batch download automation
- Folder synchronization
- Cloud backup integration

## Conclusion

The modular architecture provides:
- ✅ Clear separation of concerns
- ✅ Testable, maintainable code
- ✅ Scalable structure
- ✅ Reusable components
- ✅ Better error handling
- ✅ Improved developer experience

This architecture supports long-term maintenance and feature development while keeping the codebase organized and understandable.
