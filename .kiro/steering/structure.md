---
inclusion: always
---

# Project Structure & Architecture

## Directory Layout

```
udio_downloader/          # Main package
├── models/               # Data models (download_config, folder_node, song_info)
├── services/             # Business logic services
│   ├── authentication.py
│   ├── credential_manager.py
│   └── folder_mapper.py
├── utils/                # Utility functions
├── cli.py                # Click-based CLI commands
└── __main__.py           # Entry point for python -m execution

chrome_extension/         # Browser extension for library mapping
├── background.js         # Service worker
├── content.js            # Content script
├── popup.html/js         # Extension UI
└── manifest.json         # Extension config

downloads/                # Default download output directory
docs/                     # Project documentation
```

## Architecture Patterns

### Service Layer
Business logic organized into focused service classes:
- `AuthenticationHandler` - Session management, login flow, cookie handling
- `FolderMapper` - Library hierarchy extraction and JSON structure generation
- `CredentialManager` - Secure credential storage via keyring

When adding features, extend existing services or create new ones in `udio_downloader/services/`.

### Data Models
- **dataclasses** for simple DTOs: `DownloadConfig`, `FolderNode`
- **Pydantic** for validation-heavy models with complex rules
- All models in `udio_downloader/models/` directory
- Keep models immutable where possible (frozen dataclasses)

### Browser Automation
Three approaches used depending on context:
1. **Selenium WebDriver** - Full automation, driver auto-managed via webdriver-manager
2. **Chrome DevTools Protocol** - Direct WebSocket connection to Chrome on port 9222
3. **Chrome Extension** - Runs in authenticated browser context for library access

Use CDP when Chrome is already running with `--remote-debugging-port=9222`.

## Code Conventions

### Naming
- Modules: `lowercase_with_underscores.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`

### Import Order
```python
# Standard library
import os
from pathlib import Path

# Third-party
import click
from selenium import webdriver

# Local
from udio_downloader.models import FolderNode
from udio_downloader.services import AuthenticationHandler
```

### Error Handling
- Define custom exceptions in service modules where they're raised
- Use descriptive exception names: `AuthenticationError`, `SessionExpiredError`
- Log errors with context using Python's `logging` module
- CLI should catch exceptions and display user-friendly messages

### Logging
- Use module-level loggers: `logger = logging.getLogger(__name__)`
- Log levels: DEBUG for detailed flow, INFO for user actions, WARNING for recoverable issues, ERROR for failures
- Include context in log messages (user ID, file paths, operation names)

## File Paths & Storage

### Session Data
- Session cookies: `~/.udio_downloader/session.json`
- 24-hour expiry, auto-renewed on CLI operations
- Contains authentication tokens and user context

### Output Directories
- Downloads: `./downloads` (configurable via `--output`)
- Metadata database: `./downloads/metadata.db` (SQLite)
- Library structure JSON: `./udio_library_structure`

### Path Handling
- Use `pathlib.Path` for all path operations
- Resolve paths relative to user's working directory
- Create parent directories automatically when writing files

## CLI Design

### Command Structure
```bash
python -m udio_downloader <command> [options]
```

Commands: `map`, `download`, `resume`

### Options Pattern
- Use Click decorators for all CLI commands
- Provide sensible defaults (e.g., `--concurrent 3`)
- Include `--help` text for all options
- Validate inputs early with Click's built-in validators

### Progress Feedback
- Use `tqdm` for progress bars during long operations
- Print clear status messages for each major step
- Show summary statistics on completion (files downloaded, errors, duration)
