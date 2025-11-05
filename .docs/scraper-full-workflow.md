# Full Library Scrape Workflow

## Quick Start

```bash
python scrape_udio_library.py
```

**Prerequisites:**
- Logged into Udio
- Library page accessible
- Songs visible in browser

## What It Does

1. **Folder Expansion** - Clicks all expand buttons to reveal nested folders
2. **Lazy Loading** - Scrolls to load all songs (max 100 attempts)
3. **Data Extraction** - Collects songs and folder hierarchy
4. **Export** - Saves to `udio_library_export.json`

## Troubleshooting

### No Songs Found
- Manually expand folders before running
- Increase scroll attempts: change `max_attempts = 100` to `200`
- Slow down scrolling: change `await asyncio.sleep(1.5)` to `3`

### Manual Folder Expansion
Browser console (F12):
```javascript
document.querySelectorAll('[aria-expanded="false"]').forEach(el => el.click());
```

## Next Steps

```bash
# Import to database
python -m udio_downloader import-metadata --json-file udio_library_export.json

# Download all
python -m udio_downloader download
```
