# Chrome extension: Udio Library Mapper

Runs inside your logged-in Udio tab, walks the folder tree and exports the library's metadata as JSON. It does **not** download audio; the Python package does that. See the [root README](../README.md) for how the two fit together.

## Install

1. Open `chrome://extensions/` and enable **Developer mode**.
2. **Load unpacked** and choose this `chrome_extension` folder.
3. After editing code, click the refresh icon on the extension card and reload the Udio tab.

## Use

1. Go to `https://www.udio.com/library` and log in.
2. Click the folder icon (📁) at the top right so the folder tree is open.
3. Click the extension icon, then **Map Library Structure** and wait for it to finish.
4. Click **📦 Export Metadata (JSON)** to save `udio_metadata_<date>.json`. This is the file the Python importer reads.
5. Import that file with the Python CLI (`python -m udio_downloader import-metadata --json-file ...`).

The other buttons (song checklist, "Export as JSON (Legacy)", text export, debug logs) are for manual use and are not importable.

## Files

| File | Role |
|---|---|
| `manifest.json` | Manifest V3 config |
| `content.js` | Content script on udio.com: maps folders/songs, builds the export |
| `popup.html`, `popup.js` | Extension popup UI |
| `background.js` | Service worker |
| `logger.js` | Shared logger (loaded in the content script and popup) |

There is no build step and no module system: scripts are loaded in the order listed in `manifest.json`.

## Contract with the Python side

`content.js` (`exportMetadataWithIncrementalSupport`) writes `exportVersion: "2.0"`; the importer warns on any other major version. Field details and the hash rule are in [../docs/EXPORT_FORMAT.md](../docs/EXPORT_FORMAT.md). If you change the export shape, update that doc and `udio_downloader/services/metadata_importer.py`.

## Troubleshooting

| Issue | Fix |
|---|---|
| "Could not establish connection" | Reload the Udio tab (F5) |
| "Folder tree panel not found" | Click the folder icon (📁) |
| Songs missing | Make sure the folder tree is open before mapping |
| Extension greyed out | You must be on udio.com |

Open DevTools (F12) on the Udio tab for the content-script log.
