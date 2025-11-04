# Udio Downloader Design Document

## Overview

The Udio Downloader is a Python-based utility that automates the extraction and download of all user content from the Udio platform before its shutdown. The system uses web scraping techniques to navigate the platform's interface, map folder structures, and download content while preserving organization.

## Architecture

The system follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Interface │────│  Main Controller│────│  Config Manager │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│Authentication   │    │  Folder Mapper  │    │Content Downloader│
│    Handler      │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────────────┐
                    │Progress Tracker │
                    └─────────────────┘
```

## Components and Interfaces

### 1. Authentication Handler
**Purpose:** Manages user authentication and session management
**Key Methods:**
- `login(username, password)` - Authenticate with Udio platform
- `maintain_session()` - Keep session alive during long operations
- `get_session_cookies()` - Retrieve current session cookies
- `is_authenticated()` - Check authentication status

**Dependencies:** requests, selenium (for handling JavaScript-heavy auth)

### 2. Folder Mapper
**Purpose:** Discovers and maps the complete folder hierarchy
**Key Methods:**
- `scan_folders()` - Recursively traverse all folders
- `build_folder_tree()` - Create hierarchical representation
- `get_folder_contents(folder_id)` - List songs in specific folder
- `export_structure(format)` - Save structure as JSON/text

**Data Structure:**
```python
FolderNode = {
    'id': str,
    'name': str,
    'path': str,
    'parent_id': str,
    'children': List[FolderNode],
    'songs': List[SongInfo],
    'song_count': int
}
```

### 3. Content Downloader
**Purpose:** Downloads individual songs and maintains folder structure
**Key Methods:**
- `download_song(song_info, local_path)` - Download single song
- `create_local_structure(folder_tree)` - Create local directories
- `batch_download(song_list)` - Download multiple songs with threading
- `verify_download(file_path, expected_size)` - Validate downloaded files

**Download Strategy:**
- Concurrent downloads (max 3 simultaneous to avoid rate limiting)
- Retry mechanism for failed downloads
- File integrity verification using size comparison
- Automatic filename sanitization for filesystem compatibility

### 4. Progress Tracker
**Purpose:** Tracks progress and handles resumption
**Key Methods:**
- `update_progress(completed, total)` - Update progress metrics
- `save_checkpoint(state)` - Save current state for resumption
- `load_checkpoint()` - Resume from saved state
- `log_completion(item)` - Record successful downloads

**State Management:**
```python
DownloadState = {
    'total_songs': int,
    'completed_songs': int,
    'failed_songs': List[str],
    'current_folder': str,
    'start_time': datetime,
    'last_checkpoint': datetime
}
```

### 5. Main Controller
**Purpose:** Orchestrates the entire download process
**Key Methods:**
- `run_full_download()` - Execute complete download workflow
- `run_mapping_only()` - Only map folder structure
- `resume_download()` - Continue interrupted download
- `generate_report()` - Create completion summary

## Data Models

### Song Information
```python
@dataclass
class SongInfo:
    id: str
    title: str
    filename: str
    download_url: str
    folder_path: str
    file_size: Optional[int]
    created_date: Optional[datetime]
    metadata: Dict[str, Any]
```

### Download Configuration
```python
@dataclass
class DownloadConfig:
    output_directory: str
    max_concurrent_downloads: int = 3
    retry_attempts: int = 3
    timeout_seconds: int = 30
    preserve_metadata: bool = True
    create_folder_structure: bool = True
```

## Error Handling

### Authentication Errors
- **Session Expiry:** Automatic re-authentication with stored credentials
- **Invalid Credentials:** Prompt user for credential re-entry
- **Rate Limiting:** Implement exponential backoff

### Download Errors
- **Network Timeouts:** Retry with exponential backoff (max 3 attempts)
- **File System Errors:** Log error and continue with next item
- **Disk Space:** Check available space before downloads, warn user

### Platform Changes
- **UI Changes:** Graceful degradation with user notification
- **API Changes:** Fallback to alternative scraping methods
- **Access Restrictions:** Clear error messages with suggested actions

## Testing Strategy

### Unit Tests
- Authentication flow validation
- Folder structure parsing accuracy
- Download verification logic
- Progress tracking calculations

### Integration Tests
- End-to-end folder mapping with mock Udio responses
- Download workflow with test files
- Resume functionality with simulated interruptions
- Error handling scenarios

### Manual Testing
- Real Udio account testing (with backup account)
- Large folder structure handling
- Network interruption scenarios
- Cross-platform compatibility (Windows/Mac/Linux)

## Implementation Considerations

### Web Scraping Approach
- **Primary Method:** Selenium WebDriver for JavaScript-heavy pages
- **Fallback Method:** Direct HTTP requests with session cookies
- **Rate Limiting:** 1-2 second delays between requests to avoid detection
- **User Agent Rotation:** Mimic real browser behavior

### Performance Optimization
- **Concurrent Downloads:** Use ThreadPoolExecutor for parallel downloads
- **Memory Management:** Stream large files to disk instead of loading in memory
- **Caching:** Cache folder structure to avoid repeated API calls
- **Compression:** Optional compression of downloaded files to save space

### Security Considerations
- **Credential Storage:** Use keyring library for secure credential storage
- **Session Management:** Automatic session cleanup on exit
- **File Permissions:** Set appropriate permissions on downloaded files
- **Input Validation:** Sanitize all user inputs and file paths

### Cross-Platform Compatibility
- **Path Handling:** Use pathlib for cross-platform path operations
- **File Naming:** Handle filesystem-specific character restrictions
- **Dependencies:** Ensure all dependencies work across platforms
- **Packaging:** Create standalone executables for easy distribution