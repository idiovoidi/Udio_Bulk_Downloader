# Technology Stack

## Core Technologies

- **Language**: Python 3.10+
- **Package Manager**: pip with requirements.txt
- **CLI Framework**: Click for command-line interface
- **Browser Automation**: Selenium WebDriver with Chrome/Firefox support
- **Web Scraping**: BeautifulSoup4 for HTML parsing
- **Data Models**: Pydantic for validation, dataclasses for simple models
- **HTTP Client**: Requests library
- **Credential Storage**: keyring for secure credential management

## Key Dependencies

- `selenium>=4.38.0` - Browser automation
- `webdriver-manager>=4.0.2` - Automatic driver management
- `click>=8.3.0` - CLI framework
- `beautifulsoup4>=4.14.2` - HTML parsing
- `requests>=2.32.5` - HTTP requests
- `pydantic>=2.12.3` - Data validation
- `tqdm>=4.67.1` - Progress bars
- `keyring>=25.6.0` - Secure credential storage

## Chrome DevTools Protocol

The project uses Chrome DevTools Protocol (CDP) for advanced browser control:
- Remote debugging on port 9222
- WebSocket connections for real-time DOM inspection
- JavaScript execution in browser context
- Session persistence without re-authentication

## Common Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Running the Tool
```bash
# Map library structure without downloading
python -m udio_downloader map --output ./downloads

# Download all songs
python -m udio_downloader download --output ./downloads --concurrent 3

# Resume interrupted download
python -m udio_downloader resume --output ./downloads
```

### Development Scripts
```bash
# Map Udio library structure (requires Chrome debugging)
python scripts/map_udio_library_structure.py

# Start Chrome with debugging enabled
scripts/start_chrome_debug_robust.bat

# Update ChromeDriver to match Chrome version
python scripts/update_chromedriver.py
```

## Chrome Debugging Setup

Chrome must be started with remote debugging enabled:
```bash
chrome.exe --remote-debugging-port=9222 --user-data-dir="path/to/profile"
```

For headless mode (required on some systems):
```bash
chrome.exe --headless --remote-debugging-port=9222
```

## Testing

Development dependencies include pytest for testing:
```bash
pytest
```
