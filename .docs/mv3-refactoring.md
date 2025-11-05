# MV3 Extension Refactoring

## Key Changes

**MV3 Compliance:**
- Service worker uses `chrome.alarms` (not setTimeout/setInterval)
- Long-running scans moved to content script
- Message routing between service worker and content script

**Incremental Updates:**
- Metadata hash tracking in chrome.storage.local
- Detects new/changed/unchanged songs
- Export format v2.0 with statistics

**Resume Capability:**
- Periodic state saving during scans
- Deduplication by folder path and song ID
- Can resume interrupted mappings

**Performance:**
- Virtualized scrolling with viewport increments
- Adaptive wait times based on library size
- Browser yield points to prevent blocking

## Export Format v2.0

```json
{
  "exportVersion": "2.0",
  "statistics": {
    "totalSongs": 500,
    "newSongs": 10,
    "changedSongs": 5,
    "unchangedSongs": 485
  },
  "folders": [...],  // Stable IDs only
  "songs": [...],    // No transient URLs
  "tags": [...]
}
```

## New Modules

- `modules/metadata-exporter.js` - Export with incremental detection
- `modules/storage-manager.js` - chrome.storage.local wrapper

## Status

✅ Tasks 2.1-2.5 complete
→ Ready for Python metadata importer (Task 3)
