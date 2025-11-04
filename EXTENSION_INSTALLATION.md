# 🎵 Udio Library Mapper - Chrome Extension Installation Guide

## Quick Start (5 minutes)

### Step 1: Load the Extension

1. **Open Chrome Extensions Page**
   ```
   chrome://extensions/
   ```
   Or: Click the puzzle icon (⋮) → "Extensions" → "Manage Extensions"

2. **Enable Developer Mode**
   - Look for the toggle switch in the **top right corner**
   - Turn it **ON** (it should turn blue)

3. **Load the Extension**
   - Click the **"Load unpacked"** button (top left)
   - Navigate to your project folder
   - Select the **`chrome_extension`** folder
   - Click **"Select Folder"**

4. **Verify Installation**
   - You should see "Udio Library Mapper" in your extensions list
   - Status should show "Enabled"
   - You'll see the extension icon in your toolbar

### Step 2: Use the Extension

1. **Navigate to Udio**
   - Go to https://www.udio.com/library
   - Log in with your Udio account
   - Wait for your library to load

2. **Open the Extension**
   - Click the **Udio Library Mapper** icon in your toolbar
   - (If you don't see it, click the puzzle icon and find it there)

3. **Map Your Library**
   - Click **"📁 Map Library Structure"**
   - Wait a few seconds for analysis
   - You'll see a summary of folders and songs found

4. **Export Your Data**
   - Click **"💾 Export as JSON"** for machine-readable format
   - Or **"📄 Export as Text"** for human-readable format
   - Choose where to save the file

## What You'll Get

### JSON Export Example
```json
{
  "timestamp": "2025-11-04T23:30:00.000Z",
  "pageUrl": "https://www.udio.com/library",
  "folders": [
    {
      "name": "My Beats",
      "path": "/folder/123",
      "songCount": 15
    }
  ],
  "songs": [
    {
      "title": "Summer Vibes",
      "artist": "DJ Cool",
      "duration": "3:45",
      "folder": "My Beats"
    }
  ]
}
```

### Text Export Example
```
UDIO LIBRARY STRUCTURE
==================================================

Total Folders: 5
Total Songs: 42

FOLDERS
--------------------------------------------------
1. My Beats (15 songs)
2. Chill Tracks (8 songs)
...

SONGS
--------------------------------------------------
1. Summer Vibes
   Artist: DJ Cool
   Duration: 3:45
   Folder: My Beats
...
```

## Troubleshooting

### Extension Not Showing Up

**Problem:** Can't find the extension icon

**Solution:**
1. Click the puzzle icon in Chrome toolbar
2. Find "Udio Library Mapper"
3. Click the pin icon to keep it visible

### Extension Grayed Out

**Problem:** Extension icon is gray/disabled

**Solution:**
1. Make sure you're on https://www.udio.com
2. Refresh the page
3. The extension only works on Udio.com

### No Folders/Songs Found

**Problem:** Mapping shows 0 results

**Solutions:**
1. **Make sure you're logged in** - You should see your library content
2. **Wait for page to load** - Give it 5-10 seconds after page loads
3. **Check the page** - Are you on `/library` or `/my-creations`?
4. **Try refreshing** - Reload the Udio page and try again

### Export Not Working

**Problem:** Export buttons don't download

**Solutions:**
1. Check Chrome's download settings (chrome://settings/downloads)
2. Make sure downloads aren't blocked for this site
3. Try the other export format

## Advanced: Viewing Console Logs

If you want to see what the extension is doing:

1. **Right-click on the Udio page** → "Inspect"
2. Go to the **"Console"** tab
3. Look for messages starting with "Udio Library Mapper:"
4. This shows what the extension found

## Privacy & Security

- ✅ **All processing is local** - Nothing sent to external servers
- ✅ **No tracking** - No analytics or data collection
- ✅ **Open source** - You can inspect all the code
- ✅ **Minimal permissions** - Only accesses Udio.com

## Next Steps

After exporting your library structure:

1. **Save the files** - Keep them in a safe location
2. **Review the data** - Make sure everything was captured
3. **Use with Python scripts** - The JSON can be used by the downloader scripts

## Need Help?

Check the console for error messages:
1. Right-click on Udio page → "Inspect"
2. Go to "Console" tab
3. Look for red error messages
4. Share these for troubleshooting

## Files in the Extension

```
chrome_extension/
├── manifest.json       # Extension configuration
├── popup.html          # User interface
├── popup.js            # UI logic
├── content.js          # Page analysis (the magic happens here)
├── background.js       # Background tasks
├── icons/              # Extension icons
│   ├── icon16.svg
│   ├── icon48.svg
│   └── icon128.svg
└── README.md           # Detailed documentation
```

## Success Checklist

- [ ] Extension loaded in Chrome
- [ ] Developer mode enabled
- [ ] Extension icon visible in toolbar
- [ ] Logged into Udio.com
- [ ] On library page with content visible
- [ ] Clicked "Map Library Structure"
- [ ] Saw results (folders and songs count)
- [ ] Successfully exported data

---

**🎉 You're all set!** The extension is much simpler than the Chrome debugging approach and works with your existing logged-in session.