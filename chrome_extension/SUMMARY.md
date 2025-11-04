# Udio Library Mapper - Summary

## What This Does

Maps your entire Udio library structure (folders and songs) and exports it to JSON or text format before the platform shuts down.

## How It Works

1. **Opens folder tree panel** - Uses the side panel that shows your folder hierarchy
2. **Recursively expands folders** - Automatically expands each folder to discover subfolders
3. **Counts songs** - Clicks leaf folders and counts songs in the main view
4. **Preserves hierarchy** - Maintains the complete folder structure with parent-child relationships
5. **Exports data** - Saves everything as JSON (machine-readable) or text (human-readable)

## Key Features

✅ **Automatic** - No manual clicking required
✅ **Recursive** - Handles nested folders of any depth
✅ **Progress tracking** - Shows real-time progress in popup
✅ **Error handling** - Gracefully handles issues and provides clear error messages
✅ **Two export formats** - JSON for processing, text for reading

## Requirements

- Chrome browser with Developer Mode enabled
- Logged into Udio.com
- On the library page (`/library`)
- **Folder tree panel must be open** (click folder icon 📁)

## Installation

```
1. chrome://extensions/
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select chrome_extension folder
```

## Usage

```
1. Open https://www.udio.com/library
2. Click folder icon (📁) to open tree panel
3. Click extension icon → "Map Library Structure"
4. Wait for completion
5. Export as JSON or Text
```

## Files

| File | Purpose |
|------|---------|
| `manifest.json` | Extension configuration |
| `popup.html` | Extension popup UI |
| `popup.js` | Popup logic and progress tracking |
| `content_v3.js` | Main mapping logic (runs on Udio page) |
| `background.js` | Extension lifecycle management |
| `README.md` | Full documentation |
| `QUICK_START.md` | Simple 5-step guide |
| `TROUBLESHOOTING.md` | Detailed error solutions |
| `FOLDER_TREE_GUIDE.md` | Technical implementation details |
| `TEST_CHECKLIST.md` | Testing procedures |

## Technical Details

### Folder Detection

**Expandable folders** (have children):
- Identified by `button[aria-label="Expand"]`
- Have `aria-expanded` attribute
- Script clicks expand button, finds children, processes recursively

**Leaf folders** (no children):
- No expand button, just folder icon
- Script clicks folder name to view songs
- Counts song elements in main view

### Hierarchy Detection

Children are identified by:
- Appearing as siblings after parent in DOM
- Having greater `paddingLeft` CSS value
- Typically 16-24px more padding per level

### Timing

- Expand animation: 600ms wait
- Collapse animation: 200ms wait
- Song loading: 1000ms wait
- Song count check: 500ms additional wait

### Selectors

```javascript
// Tree container
'[role="tree"][aria-label="Folder structure"]'

// Folder name
'button[title]'

// Expand button
'button[aria-label="Expand"]'

// Song elements (tries multiple)
'[data-testid*="song"]'
'[data-song-id]'
'[role="article"]'
'.song-item'
```

## Output Format

### JSON Structure
```json
{
  "folders": [
    {
      "name": "Folder Name",
      "path": ["Parent", "Child", "Folder Name"],
      "hasChildren": true,
      "isLeaf": false,
      "subfolders": [...],
      "songCount": 0
    }
  ],
  "totalFolders": 50,
  "totalSongs": 234
}
```

### Text Structure
```
1. Parent Folder (3 subfolders) (0 songs)
  1.1 Child Folder (0 subfolders) (12 songs)
  1.2 Another Child (1 subfolders) (5 songs)
    1.2.1 Grandchild (0 subfolders) (8 songs)
```

## Common Issues

| Issue | Solution |
|-------|----------|
| "Could not establish connection" | Refresh Udio page (F5) |
| "Folder tree panel not found" | Click folder icon (📁) |
| Mapping gets stuck | Check console, refresh, retry |
| Song count is 0 | Increase wait times, check selectors |
| Children not detected | Adjust padding threshold |

## Performance

| Library Size | Time Required |
|--------------|---------------|
| 10 folders   | ~30 seconds   |
| 50 folders   | ~3 minutes    |
| 100 folders  | ~6 minutes    |
| 200+ folders | 10+ minutes   |

Time increases with:
- Number of folders
- Depth of nesting
- Number of songs per folder
- Page load speed

## Limitations

1. **Must have folder tree open** - Cannot auto-open (yet)
2. **Sequential processing** - One folder at a time (for reliability)
3. **Song counting is approximate** - Depends on finding song elements
4. **No song metadata** - Only counts songs, doesn't extract titles/artists
5. **Requires page interaction** - Cannot run in background

## Future Improvements

- Auto-open folder tree panel
- Better song element detection
- Extract song metadata (title, artist, duration, URL)
- Parallel processing for speed
- Resume capability for interrupted mapping
- Direct API access (if available)

## Version History

- **v1.0** - Initial release with basic folder detection
- **v2.0** - Improved selectors and error handling
- **v3.0** - Folder tree panel mapping (current)

## Support

For issues:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Open console (F12) and look for errors
3. Share console output and HTML samples

## License

Provided as-is for personal use to backup Udio libraries before platform shutdown.
