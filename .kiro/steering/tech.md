---
inclusion: always
---

# Technology Stack

## Python package (`udio_downloader/`)

- Python 3.10+, `pip` with `requirements.txt`, tests with `pytest`
- Click (CLI), Playwright async API (browser automation), SQLite (metadata and download state), Requests, tqdm, Pydantic
- Playwright needs its browser binary: `playwright install chromium` (re-run after upgrading the package)

## Chrome extension (`chrome_extension/`)

- Manifest V3, vanilla JavaScript, no bundler or npm. Load unpacked at `chrome://extensions/`.

## Common commands

```bash
pip install -r requirements.txt
playwright install chromium
python -m udio_downloader import-metadata --json-file udio_metadata_<date>.json
python -m udio_downloader download --no-headless   # log in on first run
python -m udio_downloader status
pytest tests
```
