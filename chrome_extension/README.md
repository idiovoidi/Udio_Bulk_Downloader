# Udio Library Mapper - Chrome Extension

A Chrome extension to map and export your Udio library structure (folders and songs) before the platform shuts down.

## Features

- 📁 **Map Library Structure** - Automatically detect folders and songs
- 💾 **Export as JSON** - Machine-readable format for further processing
- 📄 **Export as Text** - Human-readable format for documentation
- 🎵 **Works with your existing session** - No need for complex authentication
- ⚡ **Simple and fast** - Just click and export

## Installation

### Method 1: Load Unpacked Extension (Recommended)

1. **Open Chrome Extensions Page**
   - Navigate to `chrome://extensions/`
   - Or click the puzzle icon → "Manage Extensions"

2. **Enable Developer Mode**
   - Toggle the "Developer mode" switch in the top right corner

3. **Load the Extension**
   - Click "Load unpacked"
   - Navigate to the `chrome_extension` folder in this project
   - Click "Select Folder"

4. **Verify Installation**
   - You should see "Udio Library Mapper" in your extensions list
   - The extension icon should appear in your Chrome toolbar

### Method 2: Pin the Extension (Optional)

1. Click the puzzle icon in Chrome toolbar
2. Find "Udio Library Mapper"
3. Click the pin icon to keep it visible

## Usage

### Step 1: Log in to Udio

1. Navigate to https://www.udio.com/library
2. Log in with your account (idiovoidi@gmail.com)
3. Make sure your library page is fully loaded

### Step 2: Open the Folder Tree Panel

**IMPORTANT:** Before mapping, you must open the folder tree panel:

1. Look for the **folder icon** (📁) button in the top right of the library page
2. Click it to open the folder tree side panel
3. You should see a list of all your folders in the panel

### Step 3: Map Your Library

1. Click the **Udio Library Mapper** extension icon
2. Click the **"📁 Map Library Structure"** button
3. Wait for the mapping to complete (this may take several minutes for large libraries)
   - The extension will automatically expand each folder
   - It will click into leaf folders to count songs
   - Progress will be shown in the popup

### Step 4: Export Your Data

Once mapping is complete, you'll see:
- Total number of folders found
- Total number of songs found
- Preview of your library structure

Choose your export format:
- **💾 Export as JSON** - For programmatic processing
- **📄 Export as Text** - For human reading

## What Gets Exported

### JSON Format
```json
{
  "timestamp": "2025-11-04T...",
  "pageUrl": "https://www.udio.com/library",
  "pageType": "library",
  "folders": [
    {
      "name": "My Folder",
      "path": "/folder/123",
      "songCount": 5
    }
  ],
  "songs": [
    {
      "title": "My Song",
      "artist": "Artist Name",
      "duration": "3:45",
      "folder": "My Folder",
      "url": "https://www.udio.com/songs/..."
    }
  ]
}
```

### Text Format
```
UDIO LIBRARY STRUCTURE
==================================================

Mapped: 11/4/2025, 10:30:00 PM
Page: https://www.udio.com/library
Type: library

SUMMARY
--------------------------------------------------
Total Folders: 5
Total Songs: 42

FOLDERS
--------------------------------------------------
1. My Folder
   Path: /folder/123
   Songs: 8

SONGS
--------------------------------------------------
1. My Song
   Artist: Artist Name
   Duration: 3:45
   Folder: My Folder
```

## Troubleshooting

### Common Issues

**"Could not establish connection" error:**
- **Solution:** Refresh the Udio page (F5) and try again
- The content script needs to load after the page loads

**"Folder tree panel not found" error:**
- **Solution:** Click the folder icon (📁) in the top right to open the folder tree panel
- The panel must be open before starting the mapping

**Mapping gets stuck:**
- **Solution:** Check browser console (F12) for errors
- Large libraries take time (10+ minutes for 200+ folders)
- Refresh and try again if truly stuck

**Song count is 0 or wrong:**
- **Solution:** Songs may take time to load
- Check that songs appear when you manually click folders
- May need to adjust wait times for slow connections

For detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Technical Details

### How It Works

1. **Content Script** - Runs on Udio.com pages and analyzes the DOM
2. **Popup Interface** - Provides the user interface for mapping and exporting
3. **Background Worker** - Handles extension lifecycle events

### Selectors Used

The extension tries multiple CSS selectors to find content:

**Folders:**
- `[data-testid*="folder"]`
- `[class*="folder"]`
- `[role="treeitem"]`

**Songs:**
- `[data-testid*="song"]`
- `[data-testid*="track"]`
- `[class*="card"]`
- `article`

### Permissions

The extension requires:
- `activeTab` - To analyze the current Udio page
- `storage` - To save mapping results temporarily
- `downloads` - To export files
- `https://www.udio.com/*` - To run on Udio pages

## Privacy

- **No data is sent to external servers**
- All processing happens locally in your browser
- Exports are saved directly to your computer
- No tracking or analytics

## Support

If you encounter issues:

1. Check the browser console for errors:
   - Right-click on the page → "Inspect"
   - Go to the "Console" tab
   - Look for messages from "Udio Library Mapper"

2. Check the extension console:
   - Go to `chrome://extensions/`
   - Find "Udio Library Mapper"
   - Click "Inspect views: service worker"

3. Share error messages for troubleshooting

## Development

### File Structure
```
chrome_extension/
├── manifest.json       # Extension configuration
├── popup.html          # Extension popup UI
├── popup.js            # Popup logic
├── content.js          # Page analysis script
├── background.js       # Background service worker
├── icons/              # Extension icons
└── README.md           # This file
```

### Testing Changes

1. Make your changes to the extension files
2. Go to `chrome://extensions/`
3. Click the refresh icon on the extension card
4. Test the changes on Udio.com

## License

This extension is provided as-is for personal use to backup your Udio library before platform shutdown.

## Version History

- **1.0.0** (2025-11-04) - Initial release
  - Library structure mapping
  - JSON and text export
  - Support for folders and songs