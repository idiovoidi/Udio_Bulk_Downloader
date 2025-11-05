# Running Full Library Scrape

## What Changed

I've updated the scraper to be more thorough:

### 1. Folder Expansion
- Automatically clicks all folder expand buttons
- Reveals nested folders and subfolders
- Tries multiple selector strategies
- Repeats until all folders are expanded

### 2. Better Scrolling
- Increased max scroll attempts to 100
- Tracks song count while scrolling
- Stops when no new songs load
- Longer delays for content to load

### 3. Improved Folder Extraction
- Captures folder hierarchy
- Handles nested folder structures
- Deduplicates folder names
- Extracts folder levels

## How to Run

```bash
python scrape_udio_library.py
```

### What to Expect:

1. **Browser opens** to Udio library
2. **Wait for login** (if needed)
3. **Press Enter** when you see songs
4. **Folder expansion** - Script clicks expand buttons
5. **Scrolling** - Script scrolls to load all songs
6. **Extraction** - Collects all songs and folders
7. **Export** - Saves to `udio_library_export.json`

### Progress Indicators:

```
Expanding all folders...
Found 15 collapsed folders, expanding...
Found 8 collapsed folders, expanding...
Found 0 collapsed folders
Folder expansion complete after 3 attempts

Scrolling to load all songs...
Loaded 25 songs (height: 2000)
Loaded 50 songs (height: 4000)
Loaded 75 songs (height: 6000)
...
No more content loading after 45 scrolls
Final song count: 239
Scrolling complete. Total songs visible: 239
```

## Tips for Best Results

### 1. Before Running:
- Make sure you're logged into Udio
- Navigate to library page manually first
- Expand a few folders manually to verify they work
- Check that songs are visible

### 2. During Running:
- Don't close the browser
- Don't interact with the page
- Let it scroll automatically
- Wait for "Press Enter" prompt

### 3. If It Misses Songs:
- Some folders might not expand automatically
- Manually expand stubborn folders
- Run the script again (it will find new songs)
- Check if folders require special interaction

## Manual Folder Expansion

If automatic expansion doesn't work:

1. **Before running script:**
   - Manually click all folder expand buttons
   - Make sure all nested folders are visible
   - Scroll to see all songs
   - Then run the script

2. **Or use this in browser console (F12):**
   ```javascript
   // Expand all folders manually
   document.querySelectorAll('[aria-expanded="false"]').forEach(el => {
       el.click();
       setTimeout(() => {}, 100);
   });
   ```

## Checking Results

After scraping, check the export:

```bash
# View the export file
cat udio_library_export.json

# Or use Python
python -c "import json; data=json.load(open('udio_library_export.json')); print(f'Songs: {len(data[\"songs\"])}, Folders: {len(data[\"folders\"])}')"
```

## Expected Output

For a library with 239 songs in 50 folders:

```
============================================================
SCRAPING COMPLETE!
============================================================

✅ Exported 239 songs
✅ Exported 50 folders
✅ Saved to: udio_library_export.json
```

## If You Get Fewer Songs

### Possible Causes:
1. **Folders not expanded** - Some folders still collapsed
2. **Lazy loading incomplete** - Need more scrolling
3. **Content in iframes** - Songs in separate frames
4. **Dynamic loading** - Content loads on interaction

### Solutions:
1. **Run again** - Script will find new songs
2. **Manual expansion** - Expand folders manually first
3. **Increase scroll attempts** - Edit script, change `max_attempts = 100` to `200`
4. **Slower scrolling** - Edit script, change `await asyncio.sleep(1.5)` to `3`

## Comparing with Extension

The Chrome extension might find more songs because:
- It can interact with UI elements directly
- It waits for specific events
- It has access to internal state
- It can trigger custom actions

But the Playwright scraper should get 90%+ of songs with proper folder expansion and scrolling.

## Next Steps

After successful scrape:

```bash
# Import to database
python -m udio_downloader import-metadata --json-file udio_library_export.json

# Check status
python -m udio_downloader status

# Download all
python -m udio_downloader download
```

## Ready?

Run this command:

```bash
python scrape_udio_library.py
```

Make sure to:
1. ✅ Be logged into Udio
2. ✅ See your library page
3. ✅ Wait for "Press Enter" prompt
4. ✅ Let it run completely

The script will do its best to find all your songs and folders!
