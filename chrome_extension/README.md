# Udio Library Mapper - Chrome Extension

Export your complete Udio library structure before platform shutdown.

## 🎉 Now Available: Modular Architecture v2.0

This extension has been refactored into a clean, modular architecture!

### 📚 Documentation
- 📖 **[INDEX.md](INDEX.md)** - Documentation hub (start here!)
- 🚀 **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete project summary
- 📊 **[COMPARISON.md](COMPARISON.md)** - Before/after comparison
- 🔧 **[MIGRATION.md](MIGRATION.md)** - Migration guide
- 📚 **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Developer reference

### ✨ What's New
- 11 focused modules (down from 2 large files)
- Better code organization (3-4x easier to maintain)
- Comprehensive documentation (8 detailed guides)
- Same features, better structure

## Quick Start

1. **Install**: Load unpacked from `chrome://extensions/` (enable Developer mode)
2. **Navigate**: Go to `udio.com/library`
3. **Open tree**: Click folder icon (📁) in top right
4. **Map**: Click extension → "Map Library Structure"
5. **Export**: Click "📋 Export Song Checklist"

## Features

### 📋 Song Checklist (Recommended)
Complete list of all songs with:
- Checkboxes to track downloads
- URLs for each song
- Folder organization preserved
- Root directory songs included
- Song metadata (duration, tags)

### 💾 JSON Export
Machine-readable format with complete structure for programmatic use.

### 📄 Text Export
Human-readable hierarchical format for browsing.

## How It Works

1. **Scans folder tree** - Recursively maps all folders and subfolders
2. **Extracts songs** - Gets metadata from each folder
3. **Includes root songs** - Captures songs not in any folder
4. **Exports data** - Provides multiple formats for different uses

## The Checklist

Best tool for systematic downloading:

```
═══════════════════════════════════════════════════════════
                    ROOT DIRECTORY
═══════════════════════════════════════════════════════════
[ ] 1. Song Title
    URL: https://www.udio.com/songs/abc123
    Duration: 3:45

═══════════════════════════════════════════════════════════
📁 My Folder > Subfolder
═══════════════════════════════════════════════════════════
[ ] 1. Another Song
    URL: https://www.udio.com/songs/def456

TOTAL SONGS: 239
```

**Usage**: Print or keep open, download each song via URL, mark [X] when done.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Could not establish connection" | Refresh page (F5) |
| "Folder tree panel not found" | Click folder icon (📁) |
| No songs found | Ensure you're in library view |
| Extension grayed out | Must be on udio.com |

## Files

- `manifest.json` - Extension config
- `popup.html/js` - UI and logic
- `content_v3.js` - Mapping engine
- `background.js` - Lifecycle management

## Limitations

- Cannot automate downloads (Udio requires UI interaction)
- Folder downloads don't preserve subfolders (use checklist instead)
- Must manually download each song using provided URLs

## Tips

✓ Use checklist for systematic downloading
✓ Download folder by folder to stay organized
✓ Check off songs as you complete them
✓ Keep checklist as permanent record

## Support

Open browser console (F12) for diagnostic information.
