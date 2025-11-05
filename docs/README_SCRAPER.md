# Scraper Framework

Reusable scraping framework with platform-specific implementations and centralized logging/output management.

## Structure

```
scraper/
├── core/           # BaseExtractor, ScrollableExtractor, BaseMapper, BrowserConnection
├── platforms/      # Platform implementations (udio/)
└── utils/          # OutputFormatter, ScraperLogger, PathManager

output/             # All outputs organized by platform
├── exports/        # JSON exports (timestamped)
├── downloads/      # Downloaded files
└── metadata/       # Metadata files

logs/               # All log files (timestamped)
```

## Key Classes

- **BrowserConnection**: Chrome DevTools Protocol connection
- **BaseExtractor**: Content extraction with caching
- **ScrollableExtractor**: Adds infinite-scroll handling
- **BaseMapper**: Hierarchical structure mapping (folders, categories)
- **PathManager**: Centralized output directory management
- **ScraperLogger**: Dual console/file logging with levels

## Output Management

All outputs are automatically organized:

```python
from scraper.utils import PathManager

paths = PathManager(base_dir='output', platform='udio')

# Get paths with automatic timestamping
export_path = paths.get_export_path('data.json', timestamped=True)
download_path = paths.get_download_path('folder', 'file.mp3')

# Utilities
paths.clean_old_exports(keep_count=5)  # Keep only 5 most recent
latest = paths.get_latest_export()
paths.print_summary()
```

## Logging

Centralized logging to both console and file:

```python
from scraper.utils import get_logger

logger = get_logger('my_scraper', log_dir='logs')

logger.info("Starting process")
logger.success("Operation completed")  # ✓ prefix
logger.warning("Potential issue")
logger.error("Something failed")
logger.debug("Detailed info", extra_data="value")
```

## Adding Platforms

1. Create `scraper/platforms/myplatform/`
2. Implement `extractors.py` and `mapper.py`
3. Create entry script `map_myplatform.py`
4. Use PathManager with your platform name

## Usage

```bash
# Start Chrome with debugging
chrome.exe --remote-debugging-port=9222 --user-data-dir="path/to/profile"

# Run mapper
python map_udio.py
```

### Output Structure

```
output/
├── exports/
│   └── udio/
│       └── library_structure_20250105_143022.json
├── downloads/
│   └── udio/
└── metadata/
    └── udio/

logs/
└── udio_mapper_20250105_143022.log
```

Features:
- Timestamped exports and logs
- Automatic cleanup (keeps 5 most recent)
- Platform-specific organization
- Detailed logging to file, clean output to console
