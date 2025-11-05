# Modern Scraper Architecture - Best Practices

## Core Principles

### 1. Separation of Concerns
**Good scrapers separate:**
- **Browser Management** - Playwright/Selenium initialization, context management
- **Navigation Logic** - URL routing, page transitions, authentication
- **Element Location** - Selector strategies, element finding, waiting
- **Data Extraction** - Parsing HTML, extracting structured data
- **Data Storage** - Saving to files, databases, queues
- **Error Handling** - Retries, logging, graceful degradation
- **Configuration** - Settings, credentials, rate limits

### 2. Modularity & Reusability

**Component Structure:**
```
scraper/
├── core/
│   ├── browser.py          # Browser lifecycle management
│   ├── session.py          # Session & authentication
│   └── waiter.py           # Smart waiting strategies
├── selectors/
│   ├── base.py             # Selector interface
│   ├── folder_selectors.py # Folder-specific selectors
│   └── song_selectors.py   # Song-specific selectors
├── extractors/
│   ├── base.py             # Extractor interface
│   ├── folder_extractor.py # Folder data extraction
│   └── song_extractor.py   # Song data extraction
├── strategies/
│   ├── scroll_strategy.py  # Lazy loading handling
│   └── navigation_strategy.py # Folder navigation
├── models/
│   ├── folder.py           # Folder data model
│   └── song.py             # Song data model
└── utils/
    ├── retry.py            # Retry decorators
    └── logger.py           # Logging utilities
```

### 3. Robustness

**Key Features:**
- **Multiple selector strategies** - Fallback if primary fails
- **Smart waiting** - Wait for elements, not arbitrary timeouts
- **Retry logic** - Exponential backoff on failures
- **Error recovery** - Continue on partial failures
- **State management** - Track progress, enable resume
- **Validation** - Verify extracted data quality

### 4. Maintainability

**Best Practices:**
- **Type hints** - Clear interfaces and contracts
- **Docstrings** - Document purpose and usage
- **Configuration files** - Externalize selectors and settings
- **Logging** - Structured, leveled logging
- **Testing** - Unit tests for extractors, integration tests for flows
- **Version control** - Track selector changes over time

### 5. Performance

**Optimization Strategies:**
- **Concurrent execution** - Parallel processing where safe
- **Connection pooling** - Reuse browser contexts
- **Caching** - Cache page state, avoid redundant requests
- **Lazy evaluation** - Load data only when needed
- **Resource cleanup** - Proper context managers

### 6. Observability

**Monitoring & Debugging:**
- **Structured logging** - JSON logs with context
- **Metrics** - Success rates, timing, error counts
- **Screenshots** - Capture on errors
- **HTML dumps** - Save page state for debugging
- **Progress tracking** - Real-time status updates

## Anti-Patterns to Avoid

❌ **Hardcoded selectors** - Use configuration files
❌ **Sleep-based waiting** - Use explicit waits
❌ **Monolithic functions** - Break into small, focused functions
❌ **Silent failures** - Log and handle errors explicitly
❌ **No state tracking** - Can't resume on failure
❌ **Tight coupling** - Components depend on each other directly
❌ **Magic numbers** - Use named constants

## Modern Scraper Patterns

### 1. Strategy Pattern
Different approaches for different scenarios:
```python
class ScrollStrategy(ABC):
    @abstractmethod
    async def load_all(self, page: Page) -> int:
        pass

class InfiniteScrollStrategy(ScrollStrategy):
    async def load_all(self, page: Page) -> int:
        # Implementation for infinite scroll
        pass

class PaginationStrategy(ScrollStrategy):
    async def load_all(self, page: Page) -> int:
        # Implementation for pagination
        pass
```

### 2. Selector Chain Pattern
Fallback selectors:
```python
class SelectorChain:
    def __init__(self, selectors: List[str]):
        self.selectors = selectors
    
    async def find(self, page: Page):
        for selector in self.selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=5000)
                if element:
                    return element
            except:
                continue
        raise ElementNotFoundError()
```

### 3. Extractor Pattern
Separate finding from extracting:
```python
class SongExtractor:
    def __init__(self, selectors: SelectorConfig):
        self.selectors = selectors
    
    async def extract(self, element: ElementHandle) -> Song:
        title = await self._extract_title(element)
        url = await self._extract_url(element)
        return Song(title=title, url=url)
```

### 4. State Machine Pattern
Track scraping progress:
```python
class ScraperState(Enum):
    INITIALIZING = "initializing"
    AUTHENTICATING = "authenticating"
    DISCOVERING = "discovering"
    EXTRACTING = "extracting"
    COMPLETED = "completed"
    FAILED = "failed"

class StatefulScraper:
    def __init__(self):
        self.state = ScraperState.INITIALIZING
        self.checkpoint = None
    
    async def run(self):
        if self.checkpoint:
            await self.resume_from(self.checkpoint)
        else:
            await self.start_fresh()
```

### 5. Observer Pattern
Progress notifications:
```python
class ProgressObserver(ABC):
    @abstractmethod
    def on_folder_start(self, folder: str): pass
    
    @abstractmethod
    def on_song_extracted(self, song: Song): pass

class ConsolePrinter(ProgressObserver):
    def on_folder_start(self, folder: str):
        print(f"Processing: {folder}")
```

## Configuration Management

### Externalized Selectors
```yaml
# selectors.yaml
folders:
  button:
    primary: "button.group\\/label"
    fallback: "button[aria-label*='folder']"
  name: "span"
  count: ".text-muted-foreground"

songs:
  container:
    primary: ".lucide-play"
    fallback: "[data-testid='song-item']"
  link: "a[href*='/songs/']"
  title: "span, h3, h4"
```

### Environment-based Config
```python
# config.py
from pydantic import BaseSettings

class ScraperConfig(BaseSettings):
    headless: bool = False
    timeout: int = 30000
    max_retries: int = 3
    rate_limit: float = 1.0
    concurrent_workers: int = 3
    
    class Config:
        env_prefix = "SCRAPER_"
```

## Error Handling Strategy

### Hierarchical Error Handling
```python
class ScraperError(Exception):
    """Base scraper error"""
    pass

class NavigationError(ScraperError):
    """Failed to navigate"""
    pass

class ExtractionError(ScraperError):
    """Failed to extract data"""
    pass

class AuthenticationError(ScraperError):
    """Failed to authenticate"""
    pass
```

### Retry Decorator
```python
def retry(max_attempts=3, backoff=2.0):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(backoff ** attempt)
        return wrapper
    return decorator
```

## Testing Strategy

### Unit Tests
- Test extractors with mock HTML
- Test selectors with sample pages
- Test retry logic
- Test data models

### Integration Tests
- Test full scraping flow
- Test error recovery
- Test resume functionality
- Test with real (cached) pages

### Fixtures
```python
@pytest.fixture
async def browser_context():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(...)
        yield context
        await context.close()

@pytest.fixture
def sample_folder_html():
    return Path("fixtures/folder.html").read_text()
```

## Documentation Standards

### Module Docstrings
```python
"""
Folder extraction module.

This module provides functionality for extracting folder metadata
from Udio library pages. It handles folder name extraction,
song count parsing, and folder hierarchy detection.

Example:
    extractor = FolderExtractor(selectors)
    folders = await extractor.extract_all(page)
"""
```

### Function Docstrings
```python
async def extract_folder_name(element: ElementHandle) -> str:
    """
    Extract folder name from folder element.
    
    Args:
        element: Playwright element handle for folder container
        
    Returns:
        Folder name as string
        
    Raises:
        ExtractionError: If name cannot be extracted
        
    Example:
        name = await extract_folder_name(folder_element)
    """
```

## Summary: What Makes a Good Scraper

✅ **Modular** - Small, focused components
✅ **Robust** - Handles failures gracefully
✅ **Maintainable** - Easy to update selectors
✅ **Observable** - Clear logging and progress
✅ **Testable** - Unit and integration tests
✅ **Configurable** - Externalized settings
✅ **Documented** - Clear purpose and usage
✅ **Performant** - Efficient resource usage
✅ **Recoverable** - Can resume on failure
✅ **Extensible** - Easy to add new features
