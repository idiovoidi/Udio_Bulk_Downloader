# Udio Library Scraper

Alternative to Chrome extension - uses Playwright to scrape library directly.

## Files

- `scrape_udio_library.py` - Main scraper
- `scrape_udio_simple.py` - Debug version

## Quick Start

```bash
# 1. Test (debug version)
python scrape_udio_simple.py

# 2. Scrape library
python scrape_udio_library.py

# 3. Import to downloader
python -m udio_downloader import-metadata --json-file udio_library_export.json

# 4. Download
python -m udio_downloader download
```

## How It Works

1. Launches browser with persistent session
2. Navigates to https://www.udio.com/library
3. Scrolls to trigger lazy loading
4. Extracts songs and folders
5. Exports to `udio_library_export.json`

## Configuration

Edit `scrape_udio_library.py`:

```python
output_file = "my_custom_export.json"  # Change output
headless = True  # Run hidden
user_data_dir = "/path/to/profile"  # Custom profile
```

## Troubleshooting

**No songs found:**
- Run debug version first
- Verify logged in
- Check page loaded completely

**Playwright not installed:**
```bash
pip install playwright
playwright install chromium
```

**Only finds few songs:**
- Increase scroll attempts in code
- Add longer delays between scrolls

## Export Format

```json
{
  "exportDate": "2025-11-05T12:00:00Z",
  "totalSongs": 100,
  "folders": [...],
  "songs": [
    {
      "id": "abc123",
      "title": "Song Title",
      "url": "https://www.udio.com/songs/abc123",
      "folderId": null,
      "folderPath": "/",
      "createdAt": "2025-11-05T12:00:00Z",
      "duration": 180
    }
  ]
}
```

Compatible with `udio_downloader import-metadata`.
