# Browser Setup

## Chrome Version

Playwright automatically downloads and manages its own Chromium browser. No manual Chrome installation needed.

## Why It Works

**Persistent Context**: Uses `launch_persistent_context()` with a profile directory (`~/.udio_downloader/browser_profile`). This:
- Saves cookies and login sessions between runs
- Reuses your authenticated Udio session
- Acts like a normal browser, not automation

**Stealth Mode**: Hides automation flags:
- `--disable-blink-features=AutomationControlled`
- `--ignore-default-args=['--enable-automation']`
- JavaScript patches for `navigator.webdriver`

**Result**: Udio sees a regular browser with a persistent session, not a bot.

## Usage

Just run the script - Playwright handles everything:
```bash
python map_udio.py
```

First run: Log in to Udio
Subsequent runs: Already logged in
