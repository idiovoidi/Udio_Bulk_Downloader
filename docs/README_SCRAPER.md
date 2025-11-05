# Scraper Framework

Reusable scraping framework with platform-specific implementations.

## Structure

```
scraper/
├── core/           # BaseExtractor, ScrollableExtractor, BaseMapper
├── platforms/      # Platform implementations (udio/)
└── utils/          # PathManager, ScraperLogger, OutputFormatter
```

## Core Classes

- **BaseExtractor**: Content extraction with caching
- **ScrollableExtractor**: Infinite-scroll handling
- **BaseMapper**: Hierarchical structure mapping
- **PathManager**: Output directory management (output/exports, output/downloads, logs/)

## Usage

```python
from scraper.utils import PathManager, get_logger

paths = PathManager(platform='udio')
logger = get_logger('scraper')

export_path = paths.get_export_path('data.json', timestamped=True)
```

## Adding Platforms

1. Create `scraper/platforms/myplatform/`
2. Implement `extractors.py` and `mapper.py`
3. Create entry script using PathManager
