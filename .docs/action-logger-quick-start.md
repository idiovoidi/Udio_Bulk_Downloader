# Action Logger Quick Start

## Usage

```bash
python action_logger.py
```

1. Press Enter to start recording
2. Interact with Udio (click folders, songs, etc.)
3. Press Ctrl+C when done
4. Log saved to `action_log.json`

## What It Captures

```json
{
  "type": "click",
  "timestamp": 1699200000000,
  "element": {
    "tagName": "BUTTON",
    "className": "group/folder flex grow...",
    "textContent": "Downloaded",
    "outerHTML": "<button class=\"...\">..."
  },
  "position": {"x": 150, "y": 300},
  "url": "https://www.udio.com/library"
}
```

Captures clicks, scrolls, keyboard input, and navigation to identify correct selectors for automation.

## Tips

- Record 1-2 minute sessions
- Focus on one workflow at a time
- Share `action_log.json` to debug selector issues
