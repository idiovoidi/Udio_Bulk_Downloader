# Complete Scraper

Recursively navigates all folders/subfolders, extracts every song with full hierarchy.

## Usage

```bash
python scrape_udio_complete.py
```

## How It Works

1. Finds all root folders
2. Clicks each folder
3. Scrolls to load all songs (up to 50 scrolls)
4. Recursively processes subfolders (max depth: 10)
5. Navigates back and continues
6. Deduplicates by song ID

## Expected Time

- Small library (<500 songs): 5-10 min
- Medium library (500-2000 songs): 15-30 min  
- Large library (2000+ songs): 30-60 min

## Comparison

| Feature | Complete | Main Window | Tree |
|---------|----------|-------------|------|
| All songs | ✅ | ✅ | ⚠️ |
| Folder hierarchy | ✅ Perfect | ❌ Basic | ✅ Good |
| Subfolders | ✅ Auto | ❌ No | ⚠️ Manual |
| Time | 20-30 min | 5-10 min | 10-20 min |

## Troubleshooting

- **No folders found**: Ensure you're on library page with folders visible
- **Could not click folder**: Script will skip and continue
- **Taking too long**: Normal for large libraries (1-3 min per folder)
- **Interrupted**: Tracks progress, skips processed folders on re-run
