# Login Guide

## OAuth Redirect Behavior

Udio uses Google OAuth which causes multiple redirects:
1. `udio.com/library` → login page → Google OAuth → back to Udio

The "Navigation interrupted" error during this flow is **normal and expected**.

## Usage

1. Run scraper: `python scrape_udio_simple.py`
2. Browser opens and may redirect through login/OAuth
3. Complete login if prompted (Google account selection, permissions)
4. **Wait for library page to fully load** (you should see your songs)
5. Press Enter in terminal only when on library page
6. Script continues automatically

## Session Persistence

Session saved to: `~/.udio_downloader/browser_profile`

After first login, future runs reuse the session unless expired.

## Troubleshooting

**Stuck on OAuth**: Complete the flow in browser, wait for library page, then press Enter

**Session expired**: Delete `~/.udio_downloader/browser_profile` and re-run

**Alternative**: Use your Chrome profile by editing scraper:
```python
scraper = UdioLibraryScraper(
    user_data_dir="C:\\Users\\YourName\\AppData\\Local\\Google\\Chrome\\User Data",
    headless=False
)
```
