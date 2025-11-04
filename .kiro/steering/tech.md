# Technology Stack

## Core Technologies

- **Language**: Python 3.10+
- **Package Manager**: pip with requirements.txt
- **CLI Framework**: Click for command-line interface
- **Browser Automation**: Selenium WebDriver + Chrome DevTools Protocol (CDP)
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

## Common Commands

### Setup
```bash
pip install -r requirements.txt
pip install -e .
```

### CLI Usage
```bash
# Map library structure
python -m udio_downloader map --output ./downloads

# Download all songs
python -m udio_downloader download --output ./downloads --concurrent 3

# Resume interrupted download
python -m udio_downloader resume --output ./downloads
```

### Chrome Debugging
Chrome must be started with remote debugging on port 9222:
```bash
chrome.exe --remote-debugging-port=9222 --user-data-dir="path/to/profile"
```
