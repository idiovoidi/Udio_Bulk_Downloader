# Simple Main Window Scraper

## Quick Start

```bash
python scrape_udio_main.py
```

1. Browser opens to Udio library
2. Log in if needed
3. Click "All Songs" to see everything
4. Press Enter when songs are visible
5. Script scrolls and extracts automatically
6. Export saved to `udio_library_export.json`

## How It Works

1. Opens main library view
2. Scrolls to load all songs (lazy loading)
3. Extracts visible songs
4. Saves to JSON

## Troubleshooting

**No songs found:**
- Ensure you're on the library page
- Click "All Songs" or a folder
- Verify songs are visible before pressing Enter

**Browser doesn't open:**
```bash
pip install playwright
playwright install chromium
```

## Performance

- Small library (< 100 songs): 1-2 minutes
- Medium (100-500): 2-5 minutes
- Large (500-2000): 5-10 minutes
- Very large (> 2000): 10-20 minutes

## Advantages

- Simpler than folder tree navigation
- More reliable
- Single pass through page
- Works with any folder layout
