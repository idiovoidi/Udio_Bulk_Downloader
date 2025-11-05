# Udio Scraper Quick Start

## Usage

```bash
# Test scraper
python scrape_udio_simple.py

# Scrape library
python scrape_udio_library.py

# Import and download
python -m udio_downloader import-metadata --json-file udio_library_export.json
python -m udio_downloader download
```

## Scripts

**scrape_udio_simple.py** - Debug tool that opens browser and shows what it finds
**scrape_udio_library.py** - Main scraper that extracts entire library to JSON

## Troubleshooting

**No songs found**: Log in when browser opens, ensure you're on /library page
**Playwright not found**: `pip install playwright && playwright install chromium`
**Browser doesn't open**: Set `headless = False` in script

## Output

Creates `udio_library_export.json` with songs and folder structure, ready for import.
