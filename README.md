# Udio Bulk Downloader

Back up your Udio library: map your folders and songs, then download the audio, lyrics and cover art.

The project is two separate programs that meet at one JSON file.

```
 ┌────────────────────────┐   udio_metadata_<date>.json   ┌─────────────────────────────┐
 │  chrome_extension/     │ ────────────────────────────► │  udio_downloader/ (Python)  │
 │  Maps the library      │   exportVersion "2.0"         │  Imports, tracks, downloads │
 │  inside your browser   │   (docs/EXPORT_FORMAT.md)     │  to disk                    │
 └────────────────────────┘                               └─────────────────────────────┘
```

| | Chrome extension | Python package |
|---|---|---|
| Folder | [chrome_extension/](chrome_extension/) | [udio_downloader/](udio_downloader/) |
| Job | Scrape folder tree + song metadata from the page you're logged in to | Import that JSON into SQLite, then download media with Playwright |
| Needs | Chrome | Python 3.10+, Playwright Chromium |
| Output | `udio_metadata_<date>.json` | `downloads/` (audio, lyrics, covers, per-song JSON) and `downloads/metadata.db` |

They share **no code**. The only coupling is the export format in [docs/EXPORT_FORMAT.md](docs/EXPORT_FORMAT.md): change one side and you must check the other.

## Workflow

1. **Map**: load [chrome_extension/](chrome_extension/) in Chrome, open `udio.com/library`, map the library and export the JSON ([instructions](chrome_extension/README.md)).
2. **Import**: `python -m udio_downloader import-metadata --json-file udio_metadata_<date>.json`
3. **Download**: `python -m udio_downloader download --no-headless` (log in to Udio in the window on first run; the login is kept in `~/.udio_downloader/browser_profile`)
4. **Check**: `python -m udio_downloader status`

## Python setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium   # re-run after upgrading the playwright package
pytest tests
```

## Repository layout

```
chrome_extension/      Chrome extension (self-contained, no build step)
udio_downloader/       Python package: CLI, database, importer, download manager
  dev_tools/           Developer-only Playwright scripts for exploring Udio's DOM (not used by the CLI)
docs/                  Cross-cutting docs: export format, Udio page structure
tests/                 Python tests
.kiro/                 Kiro IDE specs and steering files (historical, partly outdated)
```
