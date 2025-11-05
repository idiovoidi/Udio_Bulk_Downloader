# Udio Downloader

Python utility for backing up Udio music libraries. Preserves folder structure, metadata, lyrics, and cover art.

## Installation

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

```bash
# 1. Export library using Chrome extension (see chrome_extension/README.md)
# 2. Import metadata
python -m udio_downloader import-metadata --json-file library_export.json

# 3. Download songs
python -m udio_downloader download

# Check status
python -m udio_downloader status
```

## Requirements

Python 3.10+, Chrome browser, Udio account

## Key Commands

```bash
python -m udio_downloader import-metadata --json-file <file.json>
python -m udio_downloader download --concurrent 3 --rate-limit 1.0
python -m udio_downloader status
```

Use `--help` on any command for options.

## Architecture

Stack: Python 3.10+, Click CLI, Playwright, SQLite, Requests

Services: database_manager, metadata_importer, playwright_session_manager, download_manager, progress_tracker

Output: `downloads/` with folder structure, MP3s, JSON metadata, lyrics, cover art

## Troubleshooting

- "Database not found" → Run `import-metadata` first
- "Not authenticated" → Browser opens automatically for login
- "Download failed" → Check `status`, re-run `download` to retry
- "Session expired" → Re-run command, browser will prompt for re-auth

## Testing

```bash
python test_full_workflow.py
```
