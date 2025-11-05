# Action Logger Usage

Records user interactions with Udio to identify correct CSS selectors and interaction patterns.

## Quick Start

```bash
python action_logger.py
```

## Options

**Option 1: Monitor Session** - Records all actions for X minutes (recommended)
**Option 2: Analyze Element** - Inspect specific element by CSS selector
**Option 3: Get Page State** - View current page info (folders, songs, buttons visible)

## What It Logs

- Clicks (element details, position, HTML structure)
- Scrolls (position changes)
- Keyboard input
- Navigation (URL changes)

Output: `action_log.json` with session metadata and action array

## Use Cases

1. **Find selectors** - Click folders/songs, review log for correct classes/IDs
2. **Debug scrapers** - Compare manual actions vs scraper behavior
3. **Map workflows** - Document navigation patterns

## Analysis Example

```python
import json
from collections import Counter

with open('action_log.json') as f:
    log = json.load(f)

# Find most clicked classes
click_classes = [a['element']['className'] for a in log['actions'] if a['type'] == 'click']
common = Counter(click_classes).most_common(10)
```

## Integration

1. Record successful manual navigation
2. Extract selectors from log
3. Update scraper with correct selectors
4. Test and iterate
