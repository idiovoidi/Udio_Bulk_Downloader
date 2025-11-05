# Tree Scraper Quick Reference

## Usage

```bash
python scrape_udio_tree.py
```

## Two Strategies

**Strategy 1: Automatic Scroll (Recommended)**
- Scrolls page to load all content
- Extracts all visible songs at once
- Fast (2-5 minutes)
- May miss folder structure details

**Strategy 2: Manual Navigation**
- You click each folder manually
- Script extracts songs after each click
- Preserves folder organization
- Slower but more accurate

## Workflow

1. Browser opens to Udio library
2. Log in if needed
3. Ensure folder tree is visible (click folder icon if needed)
4. Press Enter when ready
5. Choose strategy (1 or 2)
6. Wait for completion
7. Export saved to `udio_library_export.json`

## Tips

- **Strategy 1**: Expand all folders manually first for best results
- **Strategy 2**: Wait for each folder to load before pressing Enter
- Script automatically deduplicates songs by ID

## Troubleshooting

- **No folders found**: Make folder tree visible, refresh page
- **Fewer songs than expected**: Expand all folders, run again
- **Could not click folder**: Use Strategy 2 (manual navigation)

## Next Steps

```bash
python -m udio_downloader import-metadata --json-file udio_library_export.json
python -m udio_downloader status
python -m udio_downloader download
```
