# Finding Udio Song Selectors

## Quick Methods

### 1. Debug Script
```bash
python scrape_udio_simple.py
```
Analyzes page structure, saves HTML to `udio_page_dump.html`, shows classes/test IDs.

### 2. Browser Console
Run `inspect_udio_page.js` in browser console (F12) for detailed analysis.

### 3. Manual Inspection
F12 → Click selector tool → Click song → Right-click element → Copy selector

## What to Look For

Song elements typically have:
- Link: `<a href="/songs/abc123">`
- Title: `<span class="title">My Song</span>`
- Container: `<div class="song-card">...</div>`

Common selectors:
- `a[href*="/songs/"]` - Direct links
- `.song-card`, `.track-item` - Container classes
- `[data-testid="song-item"]` - Test IDs

## Testing Selectors

Browser console:
```javascript
document.querySelectorAll('YOUR_SELECTOR').length
```

## Updating Scraper

In `scrape_udio_library.py`, update `extract_songs()`:
```python
elements = document.querySelectorAll('.your-selector-here');
```

## Common Issues

- **React/Vue app**: Wait longer, check data attributes
- **Shadow DOM**: Access via `element.shadowRoot`
- **Dynamic classes**: Use data attributes or structural selectors
