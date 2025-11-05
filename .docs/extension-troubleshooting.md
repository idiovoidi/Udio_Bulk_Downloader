# Extension Troubleshooting

## Quick Test

1. Go to `chrome://extensions/`
2. Find "Udio Library Mapper" and click refresh (🔄)
3. Visit `https://www.udio.com/library`
4. Click extension icon

## Common Issues

**"Could not load manifest"** - Load the `chrome_extension` folder, not parent folder

**Icon grayed out** - Must be on `https://www.udio.com/*` domain

**"Could not establish connection"** - Refresh the page (F5)

**Popup doesn't open** - Right-click icon → "Inspect popup" → check console

## Debug Checklist

- Check `chrome://extensions/` for errors
- Check page console (F12) on udio.com/library
- Check popup console (right-click popup → Inspect)

## Alternative: Playwright Direct Scraping

```python
import asyncio
from playwright.async_api import async_playwright

async def scrape_library():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await (await browser.new_context()).new_page()
        
        await page.goto('https://www.udio.com/library')
        input("Press Enter after logging in...")
        await page.wait_for_selector('[data-testid="song-item"]')
        
        songs = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('[data-testid="song-item"]')).map(el => ({
                title: el.querySelector('.song-title')?.textContent,
                url: el.querySelector('a')?.href
            }));
        }''')
        
        print(f"Found {len(songs)} songs")
        await browser.close()

asyncio.run(scrape_library())
```
