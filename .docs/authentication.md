# Authentication Guide

## Quick Start (Recommended)

Run the download command - it handles authentication automatically:

```bash
python -m udio_downloader download
```

If not authenticated, a browser opens for login. Session persists across runs.

## Alternative: Pre-authenticate

```bash
python login_helper.py
```

## Session Storage

Session saved to: `~/.udio_downloader/browser_profile/`

Login once - session persists until expiration (several days).

## Troubleshooting

**Session expired:** Re-run download command, log in when prompted.

**Browser won't open:** Ensure Playwright installed: `playwright install chromium`

**Start fresh:** Delete `~/.udio_downloader/browser_profile/` and re-authenticate.

## Multiple Accounts

```bash
python -m udio_downloader download --user-data-dir ~/.udio_account1
python -m udio_downloader download --user-data-dir ~/.udio_account2
```
