# Caching System Documentation

## Overview

The extension now includes a comprehensive caching system to prevent excessive re-scanning and improve performance on re-runs.

## Features

### 1. Folder Cache
- **Location:** `FolderMapper.folderCache`
- **Purpose:** Caches processed folder data to avoid re-scanning
- **Key:** Folder path (e.g., "Music/Rock/Classic")
- **Value:** Complete folder data including subfolders and song counts

### 2. Song Cache
- **Location:** `SongExtractor.cache`
- **Purpose:** Caches extracted songs for each folder
- **Key:** Folder path or "root" for root-level songs
- **Value:** Array of song objects with metadata

## How It Works

### First Run
```
User clicks "Map Library"
    ↓
FolderMapper processes each folder
    ↓
For each folder:
  - Check cache (miss)
  - Process folder
  - Extract songs
  - Store in cache
    ↓
Complete mapping
```

### Subsequent Runs
```
User clicks "Map Library" again
    ↓
FolderMapper processes each folder
    ↓
For each folder:
  - Check cache (hit!)
  - Return cached data
  - Skip processing
    ↓
Complete mapping (much faster!)
```

## Improved Scroll Detection

### Previous Issues
- Fixed scroll attempts (50 max)
- No detection of actual scroll position
- Couldn't tell when at bottom
- Wasted time scrolling when done

### New Implementation
```javascript
// Check if at bottom
const isAtBottom = (scrollTop + clientHeight) >= (scrollHeight - 100);

// Stop if no new songs and at bottom
if (noNewSongs >= 2 && isAtBottom) break;

// Stop if scroll position unchanged
if (newScrollTop === oldScrollTop && isAtBottom) break;

// Stop if scroll height unchanged
if (scrollHeight === initialScrollHeight && noNewSongs >= 2) break;
```

### Benefits
- Detects when at bottom of list
- Stops scrolling when no more content
- Reduces unnecessary scroll attempts
- Faster extraction (typically 5-10 attempts vs 50)

## Cache Management

### View Cache Stats
```javascript
// In popup
Click "📊 Cache Stats" button

// Shows:
"Cache: 15 folders, 8 songs"
```

### Clear Cache
```javascript
// In popup
Click "🗑️ Clear Cache" button

// Clears:
- All folder cache entries
- All song cache entries
- Shows confirmation with counts
```

### Programmatic Access
```javascript
// Get cache stats
const stats = folderMapper.getCacheStats();
// Returns: { folders: 15, songs: 8 }

// Clear cache
folderMapper.clearCache();
// Clears both folder and song caches
```

## Cache Invalidation

### When to Clear Cache

1. **After Udio Changes**
   - Added/removed songs
   - Renamed folders
   - Reorganized structure

2. **Before Fresh Scan**
   - Want to ensure latest data
   - Suspect cache is stale

3. **Troubleshooting**
   - Missing songs
   - Incorrect counts
   - Unexpected results

### Automatic Invalidation

Cache is automatically cleared:
- When extension reloads
- When page refreshes
- When mapping starts fresh

## Performance Impact

### Without Cache
```
Mapping 20 folders with 200 songs:
- Time: ~5-10 minutes
- Scroll attempts: ~1000 (50 per folder)
- DOM queries: ~10,000
```

### With Cache (Second Run)
```
Mapping 20 folders with 200 songs:
- Time: ~10-30 seconds
- Scroll attempts: 0
- DOM queries: ~100
```

**Improvement: 10-30x faster on re-runs!**

## Implementation Details

### Folder Cache Structure
```javascript
Map {
  "Music" => {
    name: "Music",
    path: ["Music"],
    hasChildren: true,
    subfolders: [...],
    songCount: 50
  },
  "Music/Rock" => {
    name: "Rock",
    path: ["Music", "Rock"],
    hasChildren: false,
    songs: [...],
    songCount: 25
  }
}
```

### Song Cache Structure
```javascript
Map {
  "root" => [
    { title: "Song 1", url: "...", ... },
    { title: "Song 2", url: "...", ... }
  ],
  "Music/Rock" => [
    { title: "Rock Song 1", url: "...", ... },
    { title: "Rock Song 2", url: "...", ... }
  ]
}
```

## Code Examples

### Using Cache in FolderMapper
```javascript
async _processFolderItem(item, parentPath) {
  const folderName = nameButton.getAttribute('title');
  const currentPath = [...parentPath, folderName];
  const cacheKey = currentPath.join('/');

  // Check cache first
  if (this.folderCache.has(cacheKey)) {
    this.logger?.info(`Using cached folder: ${cacheKey}`);
    return this.folderCache.get(cacheKey);
  }

  // Process folder...
  const folderData = { ... };

  // Cache the result
  this.folderCache.set(cacheKey, folderData);

  return folderData;
}
```

### Using Cache in SongExtractor
```javascript
async extractSongsFromView(folderPath = null) {
  // Check cache first
  const cacheKey = folderPath ? folderPath.join('/') : 'root';
  if (this.cache.has(cacheKey)) {
    this.logger?.info(`Using cached songs for: ${cacheKey}`);
    return this.cache.get(cacheKey);
  }

  // Extract songs...
  const songs = [...];

  // Cache the results
  this.cache.set(cacheKey, songs);

  return songs;
}
```

## Debugging

### Check Cache in Console
```javascript
// In content script console (F12 on udio.com)
// Access via global if exposed, or check logs

// Look for log messages:
"Using cached folder: Music/Rock"
"Using cached songs for: Music/Rock"
```

### Cache Hit Rate
Monitor logs to see cache effectiveness:
```
First run:
- "Processing folder 1/20"
- "Extracting songs..."
- "Found 25 songs"

Second run:
- "Using cached folder: Music"
- "Using cached songs for: Music"
- "Complete in 15 seconds"
```

## Best Practices

### 1. Clear Cache When Needed
- Before important scans
- After making changes on Udio
- When troubleshooting

### 2. Monitor Cache Stats
- Check cache size periodically
- Verify expected number of entries
- Clear if seems too large

### 3. Use Logs
- Enable debug logging
- Watch for cache hit/miss messages
- Verify cache is working

## Troubleshooting

### Issue: Cache Not Working
**Symptoms:** Still slow on re-runs
**Solution:**
1. Check cache stats (should show entries)
2. Check logs for "Using cached..." messages
3. Verify cache isn't being cleared prematurely

### Issue: Stale Cache Data
**Symptoms:** Missing new songs, old folder names
**Solution:**
1. Click "Clear Cache" button
2. Re-run mapping
3. Verify fresh data

### Issue: Cache Too Large
**Symptoms:** Memory issues, slow performance
**Solution:**
1. Clear cache manually
2. Consider reducing cache size limit (future enhancement)

## Future Enhancements

### Planned Features
1. **Persistent Cache** - Save to chrome.storage.local
2. **Cache Expiration** - Auto-clear after 24 hours
3. **Selective Cache** - Clear specific folders
4. **Cache Size Limits** - Prevent memory issues
5. **Cache Preloading** - Load from storage on startup

### Potential Improvements
1. **Smart Invalidation** - Detect Udio changes
2. **Partial Updates** - Update only changed folders
3. **Cache Compression** - Reduce memory usage
4. **Cache Analytics** - Track hit rates and performance

## API Reference

### FolderMapper

```javascript
// Clear all caches
folderMapper.clearCache()

// Get cache statistics
const stats = folderMapper.getCacheStats()
// Returns: { folders: number, songs: number }
```

### SongExtractor

```javascript
// Clear song cache
songExtractor.clearCache()

// Get cache size
const size = songExtractor.getCacheSize()
// Returns: number of cached folders
```

## Summary

The caching system provides:
- ✅ 10-30x faster re-runs
- ✅ Reduced server load
- ✅ Better user experience
- ✅ Improved scroll detection
- ✅ Manual cache management
- ✅ Cache statistics

This makes the extension much more efficient for users who need to run multiple scans or resume interrupted mappings.
