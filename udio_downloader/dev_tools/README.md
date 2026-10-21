# dev_tools

Developer-only Playwright scripts for exploring Udio's DOM and prototyping a mapper in Python. **Not used by the `udio-downloader` CLI**, and their output is not the extension's export format; use [chrome_extension/](../../chrome_extension/) to produce the file `import-metadata` reads.

Run from the repo root:

```
python -m udio_downloader.dev_tools.map_udio
python -m udio_downloader.dev_tools.map_single_folder
python -m udio_downloader.dev_tools.map_folder_recursive
python -m udio_downloader.dev_tools.inspect_song
```

They open Chromium with the shared profile in `~/.udio_downloader/browser_profile` and write to `./output` and `./logs` (git-ignored). `scraper/` is the helper package they use; [BEST_PRACTICES.md](BEST_PRACTICES.md) has notes on scraping Udio.
