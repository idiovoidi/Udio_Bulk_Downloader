# Project Structure

## Directory Organization

```
udio_downloader/          # Main package
├── models/               # Data models
│   ├── download_config.py    # Download configuration settings
│   ├── folder_node.py        # Hierarchical folder structure
│   └── song_info.py          # Song metadata model
├── services/             # Business logic services
│   ├── authentication.py     # Udio login and session management
│   ├── credential_manager.py # Secure credential storage
│   └── folder_mapper.py      # Library structure mapping
├── utils/                # Utility functions
├── cli.py                # Click-based CLI interface
├── __init__.py           # Package initialization
└── __main__.py           # Entry point for python -m execution

scripts/                  # Standalone utility scripts
├── map_udio_library_structure.py  # Library structure analyzer
├── chrome_debug_final_solution.py # Chrome debugging setup
├── ui_mapper_direct.py            # Direct UI mapping via CDP
├── open_udio_for_login.py         # Login helper
└── *.bat                          # Windows batch scripts for Chrome

config/                   # Configuration files
└── chrome_dev_config.json

docs/                     # Documentation
├── chrome_debugging_solution.md
├── chrome_dev_setup.md
└── chrome_setup.md

ui_mapping_direct/        # UI analysis results (JSON)
ui_analysis/              # UI analysis reports
udio_library_structure/   # Library mapping output
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
Two approaches used:
1. **Selenium WebDriver** - Full browser automation with driver management
2. **Chrome DevTools Protocol** - Direct CDP via WebSocket for logged-in sessions

### Script Organization
- Production code in `udio_downloader/` package
- Development/diagnostic scripts in `scripts/` directory
- Scripts are standalone and can be run directly
- Batch files (`.bat`) for Windows-specific Chrome launching

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
- Downloads default to `./downloads`
- Library structure output to `./udio_library_structure`
- UI analysis output to `./ui_mapping_direct` and `./ui_analysis`
