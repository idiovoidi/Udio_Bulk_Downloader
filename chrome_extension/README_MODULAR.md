# Udio Library Mapper - Modular Architecture

## Overview

This is a refactored, modular version of the Udio Library Mapper Chrome extension. The code has been reorganized into logical modules with clear separation of concerns.

## Architecture

### Directory Structure

```
chrome_extension/
├── manifest.json              # Original manifest
├── manifest-modular.json      # New modular manifest
├── popup.html                 # Popup UI (unchanged)
├── background.js              # Background service worker
├── logger.js                  # Logging system (moved from root)
│
├── modules/                   # Shared modules
│   ├── storage.js            # State persistence
│   ├── dom-utils.js          # DOM manipulation helpers
│   ├── folder-mapper.js      # Core folder mapping logic
│   ├── song-extractor.js     # Song extraction logic
│   ├── export-utils.js       # Export functionality (JSON, text, checklist)
│   └── ui-controller.js      # UI state management
│
├── content/                   # Content script modules
│   ├── content-main.js       # Entry point
│   ├── message-handler.js    # Message routing
│   └── diagnostics.js        # Debug utilities
│
└── popup/                     # Popup script modules
    ├── popup-main.js         # Entry point
    └── popup-controller.js   # Popup logic
```

## Module Responsibilities

### Core Modules (`modules/`)

#### `storage.js` - StorageManager
- Manages chrome.storage.local operations
- Handles mapping state persistence
- Manages log storage

#### `dom-utils.js` - DOMUtils
- Sleep/delay utilities
- Element waiting
- Scroll management
- DOM query helpers

#### `folder-mapper.js` - FolderMapper
- Core folder tree traversal logic
- Recursive folder processing
- Progress tracking
- State management during mapping

#### `song-extractor.js` - SongExtractor
- Song data extraction from DOM
- Scroll-based pagination
- Metadata parsing (title, duration, tags, likes)
- Duplicate detection

#### `export-utils.js` - ExportUtils
- JSON export
- Hierarchical text export
- Checklist generation
- File download management

#### `ui-controller.js` - UIController
- Status message updates
- Progress bar management
- Results display
- Button state management
- Log viewer

### Content Script (`content/`)

#### `content-main.js`
- Entry point for content script
- Module initialization
- State restoration
- Page load detection

#### `message-handler.js` - MessageHandler
- Routes messages from popup
- Handles action dispatching
- Manages async responses

#### `diagnostics.js` - Diagnostics
- Tree structure debugging
- DOM inspection utilities
- Expansion testing

### Popup Script (`popup/`)

#### `popup-main.js`
- Entry point for popup
- DOM element binding
- Controller initialization

#### `popup-controller.js` - PopupController
- Orchestrates popup functionality
- Manages mapping workflow
- Handles export operations
- Progress polling
- Tab communication

## Benefits of Modular Architecture

### 1. **Separation of Concerns**
- Each module has a single, well-defined responsibility
- Business logic separated from UI logic
- DOM operations isolated from data processing

### 2. **Testability**
- Modules can be tested independently
- Dependencies are explicit and injectable
- Mock-friendly interfaces

### 3. **Maintainability**
- Easy to locate and fix bugs
- Changes are localized to specific modules
- Clear module boundaries

### 4. **Reusability**
- Modules can be reused across content and popup scripts
- Shared utilities reduce code duplication
- Consistent behavior across contexts

### 5. **Scalability**
- Easy to add new features
- Simple to extend existing modules
- Clear patterns for new functionality

## Migration Guide

### From Old to New

The old monolithic files have been split as follows:

**Old `content_v3.js` → New Structure:**
- Mapping logic → `modules/folder-mapper.js`
- Song extraction → `modules/song-extractor.js`
- Message handling → `content/message-handler.js`
- Diagnostics → `content/diagnostics.js`
- Entry point → `content/content-main.js`

**Old `popup.js` → New Structure:**
- Export functions → `modules/export-utils.js`
- UI updates → `modules/ui-controller.js`
- Storage operations → `modules/storage.js`
- Main logic → `popup/popup-controller.js`
- Entry point → `popup/popup-main.js`

### Using the Modular Version

1. **Update manifest.json** to use the new module structure (or use `manifest-modular.json`)
2. **Load as unpacked extension** in Chrome
3. **Test functionality** to ensure all features work

### Backward Compatibility

The old files (`content_v3.js`, `popup.js`) are preserved for reference. You can switch between versions by updating the manifest.json file.

## Development Guidelines

### Adding New Features

1. **Identify the appropriate module** or create a new one
2. **Keep modules focused** on a single responsibility
3. **Use dependency injection** for testability
4. **Export classes/functions** using ES6 modules
5. **Document public APIs** with JSDoc comments

### Module Communication

- Use **message passing** between content and popup scripts
- Use **shared modules** for common functionality
- Use **storage** for persistent state
- Use **events** for UI updates

### Error Handling

- Each module should handle its own errors
- Propagate errors up to the caller when appropriate
- Log errors using the logger module
- Provide user-friendly error messages in the UI

## Testing

### Unit Testing
Each module can be tested independently:

```javascript
import { DOMUtils } from './modules/dom-utils.js';

// Test sleep function
await DOMUtils.sleep(100);
```

### Integration Testing
Test module interactions:

```javascript
import { FolderMapper } from './modules/folder-mapper.js';
import { StorageManager } from './modules/storage.js';

const storage = new StorageManager();
const mapper = new FolderMapper(null, storage);
await mapper.startMapping();
```

## Performance Considerations

- **Lazy loading**: Modules are loaded only when needed
- **Efficient DOM queries**: Cached selectors where possible
- **Debounced storage**: State saves are debounced to reduce I/O
- **Progress updates**: Throttled to avoid UI jank

## Future Improvements

1. **TypeScript migration** for better type safety
2. **Unit test suite** with Jest or Vitest
3. **Build system** for bundling and minification
4. **Linting** with ESLint for code quality
5. **Documentation** with JSDoc and auto-generated docs

## Troubleshooting

### Module Loading Issues

If you see "Cannot use import statement outside a module":
- Ensure `"type": "module"` is set in manifest.json
- Check that all script tags use `type="module"`

### Import Path Issues

- Use relative paths: `./module.js` or `../module.js`
- Include `.js` extension in imports
- Check file paths match directory structure

### Chrome Extension Limitations

- ES6 modules work in Manifest V3
- Service workers must be modules
- Content scripts can use modules with proper configuration

## License

Same as the original Udio Library Mapper project.
