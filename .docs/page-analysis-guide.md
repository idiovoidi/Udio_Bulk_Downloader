# Page Analysis Guide

## Quick Start

```bash
python scrape_udio_simple.py
```

Wait for browser to open, ensure songs are visible, then press Enter.

## What the Script Does

- Saves HTML to `udio_page_dump.html`
- Extracts all CSS classes and data-testid attributes
- Attempts to find song elements using multiple selectors
- Shows element counts and structure

## Key Checks

Before pressing Enter:
- Songs are visible in browser
- Page fully loaded (no spinners)
- You're logged in

## Analyzing Output

Look for patterns in terminal output:
- Classes containing 'song', 'track', 'item', 'card'
- Data-testid attributes
- Links containing '/songs/'

## Manual Analysis

If automatic detection fails:

1. **DevTools Method**: F12 → Elements → Find song → Right-click → Copy selector
2. **HTML Dump**: Search `udio_page_dump.html` for song titles
3. **Console**: Run `document.querySelectorAll('a[href*="/songs/"]')` in browser console

## Common Issues

- **0 songs found**: Content may be in Shadow DOM, iframe, or not loaded yet
- **Page blank**: Wait longer, scroll, or refresh (F5)
- **Small HTML dump**: Not logged in or page didn't load

## Next Steps

If songs found → Run `python scrape_udio_library.py`

If not found → Share terminal output and relevant HTML dump sections
