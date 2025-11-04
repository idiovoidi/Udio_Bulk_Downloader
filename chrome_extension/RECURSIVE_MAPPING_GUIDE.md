# Recursive Library Mapping Guide

## What's New in V2

The extension now **recursively maps your entire library structure**:

✅ **Folders** - All root-level folders  
✅ **Subfolders** - Nested folders within folders  
✅ **Sub-subfolders** - Any depth of nesting  
✅ **Songs** - All songs at every level  
✅ **Hierarchy** - Complete tree structure preserved  

## How It Works

1. **Finds all root folders** in your library
2. **Clicks each folder** to expand it
3. **Discovers subfolders** and songs inside
4. **Recursively processes** each subfolder
5. **Builds complete tree** with all relationships

## Usage

### Step 1: Reload the Extension

Since we updated the code:

1. Go to `chrome://extensions/`
2. Find "Udio Library Mapper"
3. Click the **refresh icon** (🔄)

### Step 2: Navigate to Library

1. Go to https://www.udio.com/library
2. Make sure you're logged in
3. **Expand some folders manually** first (optional, helps the extension)

### Step 3: Run the Mapper

1. Click the extension icon
2. Click **"Map Library Structure"**
3. **Wait patiently** - this will take longer now!
   - It needs to click into each folder
   - Typical time: 30 seconds to 2 minutes
   - Depends on how many folders you have

### Step 4: Export

Once complete, you'll see:
- Total folders (including subfolders)
- Total songs (across all folders)
- Root folder count

Export options:
- **JSON** - Complete hierarchical structure
- **Text** - Human-readable tree view

## Output Format

### JSON Structure
```json
{
  "rootFolders": [
    {
      "name": "My Music",
      "depth": 0,
      "songCount": 10,
      "songs": [
        {
          "title": "Song 1",
          "artist": "Artist",
          "url": "..."
        }
      ],
      "subfolders": [
        {
          "name": "Rock",
          "depth": 1,
          "songs": [...],
          "subfolders": [...]
        }
      ]
    }
  ],
  "totalFolders": 25,
  "totalSongs": 150
}
```

### Text Structure
```
FOLDER STRUCTURE
--------------------------------------------------
1. My Music (10 songs) (2 subfolders)
  • Song 1 - Artist [3:45]
  • Song 2 - Artist [4:20]
  1.1 Rock (5 songs) (1 subfolder)
    • Rock Song 1 - Band [3:30]
    1.1.1 Hard Rock (3 songs)
      • Heavy Song - Band [4:00]
  1.2 Jazz (8 songs)
    • Jazz Song 1 - Artist [5:15]
```

## Troubleshooting

### Extension Takes Too Long

**Problem:** Mapping is taking forever

**Solutions:**
1. You have a LOT of folders - this is normal
2. Check the browser console for progress:
   - Right-click page → Inspect → Console
   - Look for "Processing folder X/Y" messages
3. If stuck, refresh and try again

### No Subfolders Found

**Problem:** Extension only finds root folders

**Solutions:**
1. **Manually expand folders first** - Click a few folders to open them
2. The extension might not be clicking correctly
3. Check console for errors

### Songs Not Found

**Problem:** Folders show 0 songs

**Solutions:**
1. Songs might be in a different view
2. Try clicking into a folder manually first
3. The song selector might need adjustment

## What Gets Captured

For each folder:
- ✅ Folder name
- ✅ Depth level (0 = root, 1 = subfolder, etc.)
- ✅ Song count
- ✅ All subfolders (recursive)
- ✅ All songs in that folder

For each song:
- ✅ Title
- ✅ Artist (if available)
- ✅ Duration (if available)
- ✅ URL
- ✅ Has download button
- ✅ Has play button

## Next Steps

Once you have the hierarchical JSON:

1. **Review the structure** - Make sure it captured everything
2. **Use for bulk download** - Python script can use this structure
3. **Preserve organization** - Downloads will maintain folder hierarchy

## Performance Notes

- **18 root folders** → ~30 seconds
- **50+ folders total** → 1-2 minutes
- **100+ folders** → 2-5 minutes

The extension adds small delays to avoid overwhelming the page.

## Known Limitations

1. **Requires page interaction** - Extension must click folders
2. **Takes time** - Can't be instant with many folders
3. **May miss dynamically loaded content** - If Udio lazy-loads songs
4. **Browser must stay focused** - Don't switch tabs during mapping

## Tips for Best Results

1. ✅ **Expand a few folders manually first** - Helps extension understand structure
2. ✅ **Keep browser window visible** - Don't minimize during mapping
3. ✅ **Wait for completion** - Don't interrupt the process
4. ✅ **Check console for progress** - See what's happening in real-time
5. ✅ **Export immediately** - Don't navigate away before exporting

---

**Ready?** Reload the extension and start mapping! 🚀