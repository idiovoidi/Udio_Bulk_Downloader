# Tree Scraper Usage

## Quick Start

```bash
python scrape_udio_tree.py
```

## Two Strategies

**Strategy 1 (Automatic)**: Fast scroll-based extraction. Gets all songs in 3-5 minutes but folder organization may be imperfect.

**Strategy 2 (Manual)**: Click each folder manually. Takes 15-20 minutes but preserves exact folder structure.

## Folder Detection

Scraper identifies folders by:
- Class: `.group/folder`
- Icon: `lucide-folder` SVG
- Song count display

If wrong folders appear, ensure you're on the library page with the folder panel visible.
