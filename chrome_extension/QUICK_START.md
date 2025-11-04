# Quick Start Guide

## 5 Steps to Map Your Udio Library

### 1. Install Extension
- Go to `chrome://extensions/`
- Enable "Developer mode" (top right)
- Click "Load unpacked"
- Select the `chrome_extension` folder
- ✅ Extension installed!

### 2. Refresh Extension (After Updates)
- Go to `chrome://extensions/`
- Find "Udio Library Mapper"
- Click the refresh icon (🔄)

### 3. Open Udio Library
- Go to https://www.udio.com/library
- Log in if needed
- **Click the folder icon (📁) in top right**
- ✅ Folder tree panel opens on the right

### 4. Start Mapping
- Click the extension icon in toolbar
- Click "Map Library Structure"
- ✅ Wait for mapping to complete (may take several minutes)

### 5. Export Results
- Click "Export as JSON" or "Export as Text"
- ✅ Your library structure is saved!

---

## What You'll See

### In the Popup:
```
Mapping in progress...
Folders: 15/50 (30%)
Songs found: 127
```

### In the Console (F12):
```
Udio Folder Mapper v3 loaded
Found folder tree panel
Found 50 top-level folders
Processing: My Folder
Expanding folder: My Folder
Found 3 children for My Folder
Leaf folder: Subfolder, clicking to view songs
Found 12 songs in Subfolder
...
Mapping complete!
```

### On the Page:
- Folders automatically expanding
- Folders collapsing after processing
- Leaf folders being clicked
- Songs appearing in main view

---

## Troubleshooting

### ❌ "Could not establish connection"
**Fix:** Refresh the Udio page (F5)

### ❌ "Folder tree panel not found"
**Fix:** Click the folder icon (📁) to open the panel

### ❌ Extension icon grayed out
**Fix:** Make sure you're on udio.com

### ❌ Mapping stuck
**Fix:** Check console for errors, refresh and retry

---

## Time Estimates

| Folders | Estimated Time |
|---------|----------------|
| 10      | ~30 seconds    |
| 50      | ~3 minutes     |
| 100     | ~6 minutes     |
| 200+    | 10+ minutes    |

Be patient with large libraries!

---

## Need Help?

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions
2. Open console (F12) and look for error messages
3. Share console output and error messages for help
