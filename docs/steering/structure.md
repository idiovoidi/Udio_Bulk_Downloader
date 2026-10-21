---
inclusion: always
---

# Project Structure

Two independent programs joined by one JSON file. See the root `README.md` and `docs/EXPORT_FORMAT.md`.

```
chrome_extension/      Chrome extension (Manifest V3, plain JS, no build step). Maps the library, exports JSON.
udio_downloader/       Python package: Click CLI, SQLite database, importer, Playwright download manager
  cli.py               Commands: import-metadata, download, status
  services/            database_manager, metadata_importer, download_manager, playwright_session_manager, progress_tracker
  utils/               metadata_hash (mirrors the extension's hash)
  dev_tools/           Developer-only Playwright exploration scripts; NOT used by the CLI
docs/                  EXPORT_FORMAT.md (the contract), Website_Structure.md (Udio DOM samples)
tests/                 pytest
```

## Boundaries

- The extension and the Python package share no code. The only coupling is the export format (`exportVersion` 2.x). Change the format in both places and in `docs/EXPORT_FORMAT.md` together.
- The extension maps metadata only; it never downloads audio. The Python package downloads; it never scrapes the library tree (that is the extension's job).
- `udio_downloader/dev_tools` must not be imported by the rest of the package.
- Extension scripts are loaded in manifest order as classic scripts (no ES modules in content scripts).

## Conventions

- Python: `snake_case` modules/functions, `PascalCase` classes, `UPPER_SNAKE_CASE` constants.
- Browser automation is Playwright (async) with a persistent profile at `~/.udio_downloader/browser_profile`. Selenium is no longer used.
