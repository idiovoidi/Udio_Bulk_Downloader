# Folder Tree Mapping Update

## What Changed

Updated the Chrome extension to use the **folder tree side panel** instead of trying to parse the main library view. This should fix the "Cannot read properties of undefined (reading 'length')" error.

## Key Changes

### 1. content_v3.js - Complete Rewrite

**Old approach:**
- Tried to find folders in the main library view
- Used generic selectors that didn't match actual structure
- Failed with undefined errors

**New approach:**
- Targets the folder tree panel specifically: `[role="tree"][aria-label="Folder structure"]`
- Identifies folders by their HTML structure (expand button vs leaf folder)
- Recursively expands folders to discover children
- Clicks leaf folders to count songs
- Uses padding levels to determine parent-child relationships

### 2. popup.js - Updated Message Handling

- Changed from `mapLibrary` action to `startMapping`
- Added progress polling every 500ms
- Better progress display with folder count and song count
- Handles the new message structure from content_v3.js

### 3. README.md - Updated Instructions

- Added requirement to open folder tree panel BEFORE mapping
- Clarified that mapping may take several minutes
- Explained the recursive expansion process

## How to Test

### 1. Reload the Extension

1. Go to `chrome://extensions/`
2. Find "Udio Library Mapper"
3. Click the refresh icon (🔄)

### 2. Open Udio Library

1. Navigate to https://www.udio.com/library
2. Make sure you're logged in
3. **IMPORTANT:** Click the folder icon (📁) in the top right to open the folder tree panel
4. You should see a list of your folders in the side panel

### 3. Start Mapping

1. Click the extension icon
2. Click "Map Library Structure"
3. Watch the progress in the popup
4. Check browser console (F12) for detailed logs

### 4. Expected Behavior

You should see in the console:
```
Udio Folder Mapper v3 loaded
Message received: startMapping
Starting folder tree mapping...
Found folder tree panel
Found X top-level folders
Processing: Folder Name
Expanding folder: Folder Name
Found Y children for Folder Name
Processing: Folder Name > Subfolder
Leaf folder: Subfolder, clicking to view songs
Found Z songs in Subfolder
...
Mapping complete!
```

In the popup:
```
Mapping in progress...
Folders: 5/20 (25%)
Songs found: 42
```

When complete:
```
Mapping complete!
Total folders: 20
Total songs: 156
```

## Folder Structure Detection

### Expandable Folders

These have children and can be expanded:
```html
<div role="button" aria-expanded="false">
  <button aria-label="Expand">▶</button>
  <button title="Folder Name">Folder Name</button>
</div>
```

The script will:
1. Click the expand button
2. Wait 600ms for animation
3. Find children by padding level
4. Recursively process each child
5. Collapse the folder

### Leaf Folders

These have no children:
```html
<div role="button">
  <svg><!-- folder icon --></svg>
  <button title="Folder Name">Folder Name</button>
</div>
```

The script will:
1. Click the folder name
2. Wait 1000ms for songs to load
3. Count song elements in main view
4. Record the count

## Troubleshooting

### Error: "Folder tree panel not found"

**Cause:** The folder tree side panel is not open.

**Solution:** Click the folder icon (📁) in the top right of the library page before starting the mapping.

### Mapping gets stuck

**Cause:** Timing issues or page not responding.

**Solution:**
1. Refresh the Udio page
2. Reload the extension
3. Try again with a smaller test (expand one folder manually first)

### Song count is 0 or wrong

**Cause:** The song element selectors don't match the actual HTML.

**Solution:** 
1. Open a leaf folder manually
2. Inspect the song elements (F12)
3. Update the selectors in `countSongsInView()` function

### Children not detected

**Cause:** Padding-based detection isn't working.

**Solution:**
1. Inspect the folder tree HTML
2. Check the padding values
3. Adjust the threshold in `processFolderItem()` (currently 30px)

## Next Steps

If this works:
1. Test with your full library
2. Export the results
3. Verify the folder hierarchy is correct
4. Check song counts are accurate

If this doesn't work:
1. Share the console errors
2. Share a sample of the folder tree HTML
3. We can adjust the selectors and logic

## Files Modified

- `chrome_extension/content_v3.js` - Complete rewrite
- `chrome_extension/popup.js` - Updated message handling
- `chrome_extension/README.md` - Updated instructions
- `chrome_extension/FOLDER_TREE_GUIDE.md` - New technical guide
- `FOLDER_TREE_UPDATE.md` - This file
