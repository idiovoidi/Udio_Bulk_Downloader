# Project Structure

## Directory Organization

```
udio_downloader/          # Main package
├── models/               # Data models (download_config, folder_node, song_info)
├── services/             # Business logic (authentication, credential_manager, folder_mapper)
├── utils/                # Utility functions
├── cli.py                # Click-based CLI interface
└── __main__.py           # Entry point for python -m execution

scripts/                  # Standalone utility scripts and batch files
config/                   # Configuration files
docs/                     # Documentation
chrome_extension/         # Chrome extension for library mapping
```

## Architecture Patterns

### Service Layer Pattern
Business logic is organized into service classes:
- `AuthenticationHandler` - Manages Udio authentication and sessions
- `FolderMapper` - Maps library folder hierarchy
- `CredentialManager` - Handles secure credential storage

### Data Models
- Use `dataclasses` for simple data structures (DownloadConfig, FolderNode)
- Use `Pydantic` models for validation-heavy structures
- Models are in `udio_downloader/models/` directory

### CLI Structure
- Main CLI defined in `cli.py` using Click decorators
- Commands: `map`, `download`, `resume`
- Entry point via `__main__.py` for `python -m udio_downloader`

### Browser Automation Strategy
- **Selenium WebDriver** - Full browser automation with driver management
- **Chrome DevTools Protocol** - Direct CDP via WebSocket for logged-in sessions
- **Chrome Extension** - Browser extension for direct library access

## Key Conventions

### File Naming
- Python modules: lowercase with underscores (`folder_mapper.py`)
- Classes: PascalCase (`AuthenticationHandler`, `FolderNode`)
- Scripts: descriptive lowercase with underscores (`map_udio_library_structure.py`)

### Import Organization
- Standard library imports first
- Third-party imports second
- Local imports last
- Grouped with blank lines between sections

### Error Handling
- Custom exceptions defined in service modules (`AuthenticationError`, `SessionExpiredError`)
- Logging via Python's `logging` module
- User-friendly error messages in CLI

### Session Management
- Session cookies saved to `~/.udio_downloader/session.json`
- 24-hour session expiry
- Automatic session renewal on expiry

### Output Directories
- Downloads: `./downloads`
- Library structure: `./udio_library_structure`
- UI analysis: `./ui_mapping_direct` and `./ui_analysis`
