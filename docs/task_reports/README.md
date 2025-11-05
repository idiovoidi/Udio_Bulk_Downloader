# Udio Library Downloader

A comprehensive tool for downloading and backing up your Udio music library before platform shutdown.

## 🎉 New: F5 Debugging Configured!

You can now debug the Chrome extension directly from VS Code! See **[DEBUGGING_QUICKSTART.md](DEBUGGING_QUICKSTART.md)** for setup.

## Components

### 1. Chrome Extension (Recommended)
**Location:** `chrome_extension/`

A Chrome extension for mapping and exporting your Udio library structure.

**Features:**
- ✅ Folder tree mapping
- ✅ Song extraction with metadata
- ✅ Caching system (10-30x faster re-runs)
- ✅ Smart scroll detection (handles 2000+ songs)
- ✅ Multiple export formats (JSON, Text, Checklist)
- ✅ F5 debugging support

**Quick Start:**
1. Load extension: `chrome://extensions` → Load unpacked → Select `chrome_extension/`
2. Navigate to `udio.com/library`
3. Click extension icon → "Map Library Structure"
4. Export your library

**Documentation:**
- 📖 [INDEX.md](chrome_extension/INDEX.md) - Documentation hub
- 🚀 [PROJECT_SUMMARY.md](chrome_extension/PROJECT_SUMMARY.md) - Overview
- 🐛 [DEBUGGING_QUICKSTART.md](DEBUGGING_QUICKSTART.md) - F5 debugging
- 📊 [PERFORMANCE_IMPROVEMENTS.md](chrome_extension/PERFORMANCE_IMPROVEMENTS.md) - Performance guide

### 2. Python Scripts
**Location:** `udio_downloader/`

Python-based downloader with CLI interface.

**Features:**
- Automated authentication
- Bulk download
- Resume capability
- Metadata preservation

**Setup:**
```bash
pip install -r requirements.txt
pip install -e .
```

**Usage:**
```bash
# Map library
python -m udio_downloader map --output ./downloads

# Download all
python -m udio_downloader download --output ./downloads --concurrent 3
```

## Development

### Debugging the Extension

**Option 1: Use Your Actual Chrome Profile (Recommended)** ⭐
```bash
1. Close all Chrome windows
2. Press F5 in VS Code
3. Select "Launch Chrome Extension (Your Default Profile)"
4. Already logged in to Udio! ✅
5. Debug with your actual profile!
```

**Option 2: Separate Profile (Keep Chrome Open)**
```bash
1. Press F5 in VS Code
2. Select "Launch Chrome Extension (Keep Login)"
3. Log in to Udio (first time only)
4. Debug! (login persists across sessions ✅)
```

**Guides:**
- **[USE_YOUR_CHROME_PROFILE.md](USE_YOUR_CHROME_PROFILE.md)** - Use your actual Chrome profile ⭐
- **[STAY_LOGGED_IN.md](STAY_LOGGED_IN.md)** - Stay logged in while debugging
- **[DEBUGGING_QUICKSTART.md](DEBUGGING_QUICKSTART.md)** - Quick start guide
- **[BROWSER_DEBUGGING.md](BROWSER_DEBUGGING.md)** - Browser options

### Project Structure
```
.
├── chrome_extension/       # Chrome extension (modular v2.1.1)
│   ├── modules/           # Shared business logic
│   ├── content/           # Content scripts
│   ├── popup/             # Popup scripts
│   └── docs/              # Comprehensive documentation
├── udio_downloader/       # Python downloader
├── scripts/               # Utility scripts
├── .vscode/               # VS Code debugging config
└── docs/                  # Project documentation
```

## Recent Updates

### v2.1.1 - Scroll Detection Fix
- ✅ Fixed scroll detection (now finds all 2000+ songs)
- ✅ Increased max scroll attempts (50 → 200)
- ✅ More patient stop conditions
- ✅ Better virtual scrolling support

### v2.1.0 - Performance & Caching
- ✅ Caching system (10-30x faster re-runs)
- ✅ Smart scroll detection
- ✅ Cache management UI

### v2.0.0 - Modular Architecture
- ✅ Refactored into 11 focused modules
- ✅ Comprehensive documentation
- ✅ 3-4x easier to maintain

## Documentation

### Chrome Extension
- [INDEX.md](chrome_extension/INDEX.md) - Documentation hub
- [QUICK_REFERENCE.md](chrome_extension/QUICK_REFERENCE.md) - API reference
- [ARCHITECTURE.md](chrome_extension/ARCHITECTURE.md) - Technical details
- [CACHING_SYSTEM.md](chrome_extension/CACHING_SYSTEM.md) - Caching guide
- [DEBUG_GUIDE.md](chrome_extension/DEBUG_GUIDE.md) - Full debugging guide

### Development
- [DEBUGGING_QUICKSTART.md](DEBUGGING_QUICKSTART.md) - F5 debugging setup
- [CHANGELOG.md](chrome_extension/CHANGELOG.md) - Version history

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly (use F5 debugging!)
5. Submit a pull request

## Support

- Check documentation in [chrome_extension/INDEX.md](chrome_extension/INDEX.md)
- Review [QUICK_REFERENCE.md](chrome_extension/QUICK_REFERENCE.md)
- See [DEBUGGING_QUICKSTART.md](DEBUGGING_QUICKSTART.md) for debugging

## License

See LICENSE file for details.

## Acknowledgments

Built to help users backup their Udio libraries before platform shutdown.

---

**Current Version:** 2.1.1
**Status:** Production Ready
**Debugging:** F5 Configured ✅
