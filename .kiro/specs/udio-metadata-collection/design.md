# Design Document

## Overview

This design extends the existing Udio Library Mapper Chrome extension and creates a new Python-based download management system. The solution consists of three main components:

1. **Enhanced Chrome Extension** - Collects comprehensive song metadata from the Udio web interface
2. **SQLite Database** - Stores folder hierarchy, song metadata, tags, and lyrics with incremental update support
3. **Python Download Manager** - Orchestrates concurrent downloads of audio files, lyrics, and cover art with resume capability

The system builds upon the existing modular extension architecture (folder-mapper.js, song-extractor.js) and adds database persistence and download orchestration capabilities.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Chrome Extension (MV3)                        │
│  ┌──────────────┐         ┌──────────────┐                      │
│  │   Service    │◄────────┤  Content     │                      │
│  │   Worker     │         │  Script      │                      │
│  │ (orchestrate)│         │ (long scans) │                      │
│  └──────────────┘         └──────┬───────┘                      │
│                                   │                               │
│                                   ▼                               │
│                          ┌────────────────┐                      │
│                          │ Folder Mapper  │                      │
│                          │ Song Extractor │                      │
│                          │ (virtualized   │                      │
│                          │  scroll loop)  │                      │
│                          └────────┬───────┘                      │
│                                   │                               │
│                                   ▼                               │
│                          chrome.storage.local                     │
│                          (seen IDs + hashes)                      │
│                                   │                               │
│                                   ▼                               │
│                          chrome.downloads API                     │
│                          (JSON export with                        │
│                           stable IDs only)                        │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Python Downloader (Playwright-based)                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Playwright Persistent Context (userDataDir)             │   │
│  │  - Reuses authenticated session                          │   │
│  │  - Resolves fresh audio/lyrics/cover URLs at runtime     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                     │
│                             ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              SQLite Database (metadata.db)                │   │
│  │  - Single writer thread (work queue)                     │   │
│  │  - Numeric fields (duration_seconds, play_count)         │   │
│  │  - Stable song IDs as primary keys                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                     │
│                             ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Download Workers (HTTP Range resume)             │   │
│  │  - Accept-Ranges detection                               │   │
│  │  - ETag/Content-Length validation                        │   │
│  │  - Partial file continuation                             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                     │
│                             ▼                                     │
│                    Local File System                              │
│         downloads/                                                │
│         ├── metadata.db                                           │
│         ├── Folder1/                                              │
│         │   ├── Song1.mp3                                         │
│         │   ├── Song1_lyrics.txt                                  │
│         │   ├── Song1_metadata.json                               │
│         │   └── Song1_cover.jpg                                   │
│         └── Folder2/                                              │
└─────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
1. User clicks extension → Service Worker schedules scan via chrome.alarms
2. Content Script injected → runs virtualized scroll loop
3. Folder Mapper + Song Extractor collect stable IDs + metadata hashes
4. Results stored in chrome.storage.local (seen IDs cache)
5. User triggers export → chrome.downloads API saves JSON (IDs only, no URLs)
6. Python Downloader starts with Playwright persistent context (authenticated)
7. Reads JSON → imports stable IDs into SQLite (single writer thread)
8. For each song: Playwright resolves fresh audio/lyrics/cover URLs
9. Download workers fetch with HTTP Range resume + ETag validation
10. Database updated with download status (thread-safe queue)
11. Resume capability: partial files continued, failed items retried
```

## Components and Interfaces

### 1. Enhanced Chrome Extension (MV3 Architecture)

#### 1.0 MV3 Service Worker and Content Script Coordination

**Service Worker Role (background.js):**
- Orchestrate scans via chrome.alarms (not setTimeout/setInterval)
- Handle messages from popup and content scripts
- Manage chrome.storage.local for seen IDs cache
- Trigger chrome.downloads for export (requires user gesture forwarding)

**Content Script Role (content-main.js):**
- Execute long-running folder/song scans (not in service worker)
- Implement virtualized scroll loop with viewport-sized increments
- Maintain idempotent, resumable scan state
- Send progress updates to service worker

**Key MV3 Constraints:**
- Service worker terminates after ~30s inactivity
- No long-running timers in service worker
- Use chrome.alarms for periodic work
- Content script handles heavy DOM work

```javascript
// background.js (Service Worker)
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'scan-library') {
    chrome.tabs.query({ url: 'https://www.udio.com/library*' }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, { action: 'startMapping' });
      }
    });
  }
});

// content-main.js (Content Script)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'startMapping') {
    // Long-running scan happens here, not in service worker
    folderMapper.startMapping().then(() => {
      sendResponse({ status: 'completed' });
    });
    return true;  // Async response
  }
});
```

### 1.1 Enhanced Chrome Extension Components

#### 1.1 Song Extractor Enhancement (song-extractor.js)

**Current Capabilities:**
- Extracts: title, URL, ID, duration, image URL, tags, plays, likes, isLiked, isDisliked

**New Capabilities:**
- Extract creation date from song page or metadata
- Extract lyrics availability indicator
- Extract artist name (if available)
- Add metadata collection timestamp
- Generate content hash for change detection

**Modified Methods:**

```javascript
class SongExtractor {
  extractSongData(element) {
    const data = {
      // Stable ID (primary key)
      id: this._extractId(element),
      
      // Core metadata
      title: this._extractTitle(element),
      artist: this._extractArtist(element),
      duration: this._extractDuration(element),
      createdDate: this._extractCreationDate(element),
      
      // User interaction data
      isLiked: this._checkLiked(element),
      isDisliked: this._checkDisliked(element),
      playCount: this._extractPlayCount(element),
      likesCount: this._extractLikesCount(element),
      
      // Content flags
      lyricsAvailable: this._checkLyricsAvailability(element),
      tags: this._extractTags(element),
      
      // Metadata tracking
      metadataCollectedAt: new Date().toISOString()
    };
    
    // Generate hash for change detection (exclude timestamp)
    data.metadataHash = this._generateHash(data);
    
    return data;
  }
  
  _generateHash(data) {
    // Hash all fields except metadataCollectedAt for change detection
    const hashInput = JSON.stringify({
      title: data.title,
      artist: data.artist,
      duration: data.duration,
      isLiked: data.isLiked,
      isDisliked: data.isDisliked,
      playCount: data.playCount,
      tags: data.tags
    });
    return this._simpleHash(hashInput);
  }
  
  _extractArtist(element) { /* Implementation */ }
  _extractCreationDate(element) { /* Implementation */ }
  _checkLyricsAvailability(element) { /* Implementation */ }
}
```

#### 1.2 Metadata Exporter (new module: metadata-exporter.js)

**Purpose:** Export stable IDs and metadata hashes (no transient URLs)

**Interface:**

```javascript
class MetadataExporter {
  constructor(logger, storage) {
    this.logger = logger;
    this.storage = storage;
  }
  
  /**
   * Convert folder structure to export format with stable IDs only
   * @param {Object} structure - Folder structure from FolderMapper
   * @returns {Object} - Compact export with IDs and hashes
   */
  async prepareForExport(structure) {
    const folders = this._flattenFolders(structure.folders);
    const songs = this._extractAllSongs(structure);
    const tags = this._extractAllTags(songs);
    
    // Load seen IDs from chrome.storage for incremental detection
    const seenCache = await this.storage.getSeenCache();
    
    // Mark new/changed songs
    songs.forEach(song => {
      const cached = seenCache[song.id];
      song.isNew = !cached;
      song.isChanged = cached && cached.hash !== song.metadataHash;
    });
    
    // Update seen cache
    const newCache = {};
    songs.forEach(song => {
      newCache[song.id] = {
        hash: song.metadataHash,
        lastSeen: song.metadataCollectedAt
      };
    });
    await this.storage.saveSeenCache(newCache);
    
    return {
      exportVersion: '2.0',
      exportDate: new Date().toISOString(),
      folders,
      songs: songs.map(s => ({
        // Stable ID only (no transient URLs)
        id: s.id,
        title: s.title,
        artist: s.artist,
        folderId: s.folderId,
        duration: s.duration,
        createdDate: s.createdDate,
        isLiked: s.isLiked,
        isDisliked: s.isDisliked,
        playCount: s.playCount,
        likesCount: s.likesCount,
        lyricsAvailable: s.lyricsAvailable,
        metadataHash: s.metadataHash,
        metadataCollectedAt: s.metadataCollectedAt,
        isNew: s.isNew,
        isChanged: s.isChanged
      })),
      tags
    };
  }
  
  /**
   * Trigger download via chrome.downloads API (requires user gesture)
   */
  async exportToFile(data) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const filename = `udio_metadata_${new Date().toISOString().split('T')[0]}.json`;
    
    // Must be called from user gesture context
    chrome.downloads.download({
      url: url,
      filename: filename,
      saveAs: true
    }, (downloadId) => {
      this.logger?.success(`Export started: ${filename}`);
      // Clean up blob URL after download starts
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
  }
  
  _flattenFolders(folders, parentId = null, parentPath = []) {
    // Recursively flatten folder tree with stable IDs
  }
  
  _extractAllSongs(structure) {
    // Extract all songs from folders and root
  }
  
  _extractAllTags(songs) {
    // Extract tag relationships
  }
}
```

### 2. SQLite Database Schema

#### 2.1 Database Structure

```sql
-- Folders table
CREATE TABLE folders (
    id TEXT PRIMARY KEY,              -- Generated UUID or hash of path
    name TEXT NOT NULL,
    parent_id TEXT,                   -- NULL for top-level folders
    path TEXT NOT NULL,               -- Full path as JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES folders(id)
);

CREATE INDEX idx_folders_parent ON folders(parent_id);
CREATE INDEX idx_folders_path ON folders(path);

-- Songs table
CREATE TABLE songs (
    id TEXT PRIMARY KEY,              -- Stable song ID from Udio
    title TEXT NOT NULL,
    artist TEXT,
    folder_id TEXT,                   -- NULL for root songs
    duration_seconds INTEGER,         -- Numeric for calculations
    created_date TEXT,
    is_liked BOOLEAN DEFAULT 0,
    is_disliked BOOLEAN DEFAULT 0,
    play_count INTEGER DEFAULT 0,     -- Numeric field
    likes_count INTEGER DEFAULT 0,    -- Numeric field
    lyrics_available BOOLEAN DEFAULT 0,
    metadata_hash TEXT,               -- For change detection
    metadata_collected_at TIMESTAMP,
    download_status TEXT DEFAULT 'pending',  -- pending, downloading, completed, failed, partial
    download_error TEXT,
    downloaded_at TIMESTAMP,
    local_audio_path TEXT,
    local_audio_size INTEGER,         -- For partial file validation
    local_audio_etag TEXT,            -- For HTTP resume validation
    local_lyrics_path TEXT,
    local_cover_path TEXT,
    local_metadata_path TEXT,
    FOREIGN KEY (folder_id) REFERENCES folders(id)
);

CREATE INDEX idx_songs_folder ON songs(folder_id);
CREATE INDEX idx_songs_status ON songs(download_status);
CREATE INDEX idx_songs_hash ON songs(metadata_hash);

-- Tags table
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE,
    UNIQUE(song_id, tag)
);

CREATE INDEX idx_tags_song ON tags(song_id);
CREATE INDEX idx_tags_tag ON tags(tag);

-- Lyrics table
CREATE TABLE lyrics (
    song_id TEXT PRIMARY KEY,
    lyrics_text TEXT,
    downloaded_at TIMESTAMP,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
);

-- Metadata tracking table
CREATE TABLE metadata_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    songs_processed INTEGER DEFAULT 0,
    songs_added INTEGER DEFAULT 0,
    songs_updated INTEGER DEFAULT 0,
    songs_failed INTEGER DEFAULT 0,
    status TEXT DEFAULT 'in_progress'  -- in_progress, completed, failed
);
```

#### 2.2 Database Manager Interface

```python
class DatabaseManager:
    """Manages SQLite database operations with single-writer thread safety"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.write_queue = queue.Queue()
        self.writer_thread = None
        self._start_writer_thread()
    
    def _start_writer_thread(self):
        """Start single writer thread for thread-safe DB operations"""
        self.writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
        self.writer_thread.start()
    
    def _writer_loop(self):
        """Process write operations from queue with single connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        while True:
            operation = self.write_queue.get()
            if operation is None:  # Poison pill
                break
            try:
                operation(conn)
                conn.commit()
            except Exception as e:
                conn.rollback()
                logging.error(f"DB write failed: {e}")
    
    def initialize_database(self) -> None:
        """Create tables if they don't exist"""
        
    def import_metadata(self, json_data: dict) -> dict:
        """
        Import metadata from JSON export (uses write queue)
        Returns: {added: int, updated: int, skipped: int, failed: int}
        """
        
    def get_pending_downloads(self, limit: int = None) -> List[dict]:
        """Get songs with download_status in ('pending', 'failed', 'partial')"""
        
    def update_download_status(self, song_id: str, status: str, 
                               error: str = None, paths: dict = None,
                               etag: str = None, size: int = None) -> None:
        """Update song download status, file paths, and resume metadata (queued write)"""
        
    def get_download_statistics(self) -> dict:
        """Get download progress statistics"""
        
    def mark_song_as_processed(self, song_id: str, metadata_hash: str) -> None:
        """Mark song as cataloged with hash (for incremental updates)"""
        
    def get_songs_needing_update(self, current_hashes: dict) -> List[str]:
        """Get song IDs where metadata_hash differs from current"""
```

### 3. Python Metadata Importer

**Purpose:** Import JSON exports from extension into SQLite database

**Module:** `udio_downloader/services/metadata_importer.py`

```python
class MetadataImporter:
    """Imports metadata from Chrome extension JSON exports"""
    
    def __init__(self, db_manager: DatabaseManager, logger):
        self.db = db_manager
        self.logger = logger
    
    def import_from_json(self, json_path: str) -> dict:
        """
        Import metadata from JSON file
        
        Process:
        1. Load and validate JSON
        2. Import folders (with parent relationships)
        3. Import songs (with folder references)
        4. Import tags
        5. Return statistics
        
        Returns: {
            folders_added: int,
            songs_added: int,
            songs_updated: int,
            tags_added: int,
            errors: List[str]
        }
        """
        
    def _import_folders(self, folders: List[dict]) -> int:
        """Import folders with parent relationships"""
        
    def _import_songs(self, songs: List[dict]) -> Tuple[int, int]:
        """Import songs, return (added, updated)"""
        
    def _import_tags(self, tags: List[dict]) -> int:
        """Import tag relationships"""
        
    def _should_update_song(self, existing: dict, new: dict) -> bool:
        """Determine if song metadata should be updated"""
```

### 4. Python Download Manager

**Purpose:** Orchestrate concurrent downloads of audio, lyrics, and cover art

**Module:** `udio_downloader/services/download_manager.py`

#### 4.1 Download Manager Core

```python
class DownloadManager:
    """Orchestrates concurrent downloads with Playwright URL resolution"""
    
    def __init__(self, db_manager: DatabaseManager, 
                 output_dir: str,
                 playwright_context,  # Authenticated Playwright context
                 concurrent_workers: int = 3,
                 rate_limit_delay: float = 1.0):
        self.db = db_manager
        self.output_dir = Path(output_dir)
        self.playwright_context = playwright_context
        self.concurrent_workers = concurrent_workers
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        
    def start_downloads(self, resume: bool = True) -> dict:
        """
        Start download process
        
        Process:
        1. Query database for pending/failed/partial songs
        2. Create folder structure
        3. Start worker threads
        4. For each song: resolve fresh URLs via Playwright
        5. Download audio (with Range resume), lyrics, cover art
        6. Update database with results (via write queue)
        7. Return statistics
        
        Returns: {
            total: int,
            completed: int,
            failed: int,
            skipped: int,
            resumed: int,
            duration: float
        }
        """
        
    async def _resolve_song_urls(self, song_id: str) -> dict:
        """
        Use Playwright to navigate to song page and extract fresh URLs
        Returns: {audio_url, lyrics_url, cover_url}
        """
        page = await self.playwright_context.new_page()
        try:
            await page.goto(f'https://www.udio.com/songs/{song_id}')
            await page.wait_for_load_state('networkidle')
            
            # Extract fresh URLs from page
            audio_url = await page.evaluate('() => document.querySelector("audio")?.src')
            cover_url = await page.evaluate('() => document.querySelector("img[alt]")?.src')
            lyrics_url = await self._extract_lyrics_url(page)
            
            return {
                'audio_url': audio_url,
                'lyrics_url': lyrics_url,
                'cover_url': cover_url
            }
        finally:
            await page.close()
    
    def _download_song(self, song: dict) -> bool:
        """Download all assets for a single song"""
        
    def _download_audio_with_resume(self, url: str, output_path: Path, 
                                    existing_size: int = 0, 
                                    existing_etag: str = None) -> Tuple[Path, str, int]:
        """
        Download MP3 with HTTP Range resume support
        
        Returns: (path, etag, size)
        """
        # Check if server supports Range requests
        head_response = self.session.head(url, allow_redirects=True)
        accept_ranges = head_response.headers.get('Accept-Ranges', 'none')
        content_length = int(head_response.headers.get('Content-Length', 0))
        etag = head_response.headers.get('ETag')
        
        # Validate existing partial file
        if existing_size > 0 and output_path.exists():
            actual_size = output_path.stat().st_size
            if actual_size == content_length:
                # Already complete
                return (output_path, etag, actual_size)
            
            if accept_ranges == 'bytes' and actual_size < content_length:
                # Resume from partial
                headers = {'Range': f'bytes={actual_size}-'}
                if existing_etag:
                    headers['If-Range'] = existing_etag
                
                response = self.session.get(url, headers=headers, stream=True)
                if response.status_code == 206:  # Partial Content
                    # Append to existing file
                    with open(output_path, 'ab') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    return (output_path, etag, output_path.stat().st_size)
        
        # Full download
        response = self.session.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return (output_path, etag, output_path.stat().st_size)
    
    def _download_lyrics(self, lyrics_url: str, folder_path: Path) -> Optional[Path]:
        """Download and save lyrics as TXT file"""
        
    def _download_cover_art(self, cover_url: str, folder_path: Path) -> Optional[Path]:
        """Download cover art image"""
        
    def _save_metadata_json(self, song: dict, folder_path: Path) -> Path:
        """Save song metadata as JSON file"""
        
    def _create_folder_structure(self, folder_path: str) -> Path:
        """Create local folder matching database path"""
```

#### 4.2 Download Worker

```python
class DownloadWorker:
    """Worker thread for concurrent downloads"""
    
    def __init__(self, worker_id: int, 
                 download_manager: DownloadManager,
                 queue: Queue,
                 results: Queue):
        self.worker_id = worker_id
        self.manager = download_manager
        self.queue = queue
        self.results = results
        
    def run(self):
        """Process songs from queue"""
        while True:
            try:
                song = self.queue.get(timeout=1)
                if song is None:  # Poison pill
                    break
                    
                result = self._process_song(song)
                self.results.put(result)
                
                # Rate limiting
                time.sleep(self.manager.rate_limit_delay)
                
            except Empty:
                continue
            except Exception as e:
                self.results.put({
                    'song_id': song['id'],
                    'status': 'failed',
                    'error': str(e)
                })
```

#### 4.3 Progress Tracker

```python
class ProgressTracker:
    """Track and display download progress"""
    
    def __init__(self, total_songs: int):
        self.total = total_songs
        self.completed = 0
        self.failed = 0
        self.start_time = time.time()
        self.pbar = tqdm(total=total_songs, desc="Downloading")
        
    def update(self, result: dict):
        """Update progress based on download result"""
        if result['status'] == 'completed':
            self.completed += 1
        else:
            self.failed += 1
        
        self.pbar.update(1)
        self.pbar.set_postfix({
            'completed': self.completed,
            'failed': self.failed,
            'rate': self._calculate_rate()
        })
        
    def _calculate_rate(self) -> str:
        """Calculate songs per minute"""
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            rate = (self.completed + self.failed) / elapsed * 60
            return f"{rate:.1f}/min"
        return "0/min"
```

### 5. CLI Interface

**Module:** `udio_downloader/cli.py`

```python
@click.group()
def cli():
    """Udio Library Downloader CLI"""
    pass

@cli.command()
@click.option('--json-file', required=True, help='Path to metadata JSON export')
@click.option('--db-path', default='./downloads/metadata.db', help='Database path')
def import_metadata(json_file, db_path):
    """Import metadata from Chrome extension JSON export"""
    # Implementation

@cli.command()
@click.option('--output', default='./downloads', help='Output directory')
@click.option('--concurrent', default=3, help='Concurrent download workers')
@click.option('--resume/--no-resume', default=True, help='Resume interrupted downloads')
@click.option('--db-path', default='./downloads/metadata.db', help='Database path')
def download(output, concurrent, resume, db_path):
    """Download all songs from database"""
    # Implementation

@cli.command()
@click.option('--db-path', default='./downloads/metadata.db', help='Database path')
def status(db_path):
    """Show download statistics"""
    # Implementation
```

## Data Models

### Folder Model

```python
@dataclass
class Folder:
    id: str
    name: str
    parent_id: Optional[str]
    path: List[str]
    created_at: datetime
```

### Song Model

```python
@dataclass
class Song:
    id: str
    title: str
    artist: Optional[str]
    folder_id: Optional[str]
    url: str
    duration: Optional[str]
    created_date: Optional[str]
    is_liked: bool
    is_disliked: bool
    play_count: int
    likes_count: int
    cover_art_url: Optional[str]
    lyrics_available: bool
    metadata_collected_at: datetime
    download_status: str
    download_error: Optional[str]
    downloaded_at: Optional[datetime]
    local_audio_path: Optional[str]
    local_lyrics_path: Optional[str]
    local_cover_path: Optional[str]
    local_metadata_path: Optional[str]
    tags: List[str]
```

### Download Result Model

```python
@dataclass
class DownloadResult:
    song_id: str
    status: str  # 'completed', 'failed', 'skipped'
    error: Optional[str]
    audio_path: Optional[Path]
    lyrics_path: Optional[Path]
    cover_path: Optional[Path]
    metadata_path: Optional[Path]
    duration: float
```

## Error Handling

### Extension Error Handling

1. **DOM Element Not Found**
   - Log warning and skip song
   - Continue processing remaining songs
   - Track failed songs for retry

2. **Network Timeout**
   - Retry up to 3 times with exponential backoff
   - Log failure after max retries
   - Continue with next song

3. **Export Failure**
   - Show user-friendly error message
   - Preserve partial data
   - Allow retry

### Database Error Handling

1. **Connection Errors**
   - Retry connection with backoff
   - Fail gracefully with clear message
   - Preserve data integrity

2. **Constraint Violations**
   - Log duplicate entries
   - Skip and continue
   - Report in statistics

3. **Transaction Failures**
   - Rollback transaction
   - Log error details
   - Retry operation

### Download Error Handling

1. **Network Errors**
   - Retry up to 3 times
   - Mark as failed in database
   - Continue with next song
   - Allow resume later

2. **File System Errors**
   - Check disk space
   - Verify permissions
   - Log error and fail gracefully

3. **Rate Limiting**
   - Detect 429 responses
   - Pause worker for 60 seconds
   - Retry request
   - Adjust rate limit dynamically

## Testing Strategy

### Unit Tests

1. **Database Manager**
   - Test CRUD operations
   - Test transaction handling
   - Test query performance

2. **Metadata Importer**
   - Test JSON parsing
   - Test data validation
   - Test incremental updates

3. **Download Manager**
   - Test file download logic
   - Test concurrent workers
   - Test resume capability

### Integration Tests

1. **End-to-End Flow**
   - Extension export → Import → Download
   - Verify data integrity
   - Verify file structure

2. **Resume Capability**
   - Interrupt download mid-process
   - Restart and verify continuation
   - Check no duplicate downloads

3. **Error Recovery**
   - Simulate network failures
   - Verify retry logic
   - Verify database consistency

### Manual Testing

1. **Extension Testing**
   - Test on various library sizes
   - Test with different folder structures
   - Verify metadata accuracy

2. **Download Testing**
   - Test with small subset
   - Test with full library
   - Verify file quality

## Performance Considerations

### Extension Performance

1. **Caching**
   - Cache processed folders and songs
   - Skip already-processed items
   - Clear cache on demand

2. **Scroll Optimization**
   - Adaptive scroll speed based on library size
   - Efficient DOM queries
   - Debounced progress updates

### Database Performance

1. **Indexing**
   - Index foreign keys
   - Index frequently queried columns
   - Composite indexes for complex queries

2. **Batch Operations**
   - Batch inserts for songs and tags
   - Use transactions for consistency
   - Commit in reasonable chunks

### Download Performance

1. **Concurrency**
   - Configurable worker count (default 3)
   - Thread-safe queue management
   - Efficient resource pooling

2. **Rate Limiting**
   - Minimum 1-second delay between requests
   - Adaptive rate limiting on 429 errors
   - Per-worker rate limiting

3. **File I/O**
   - Stream large files
   - Async file writes
   - Efficient path operations

## Security Considerations

1. **File System Safety**
   - Sanitize filenames
   - Validate paths
   - Check disk space before download

2. **Network Safety**
   - Validate URLs
   - Use HTTPS only
   - Timeout on long requests

3. **Data Privacy**
   - Store database locally
   - No external data transmission
   - User controls all data

## Deployment and Usage

### Installation

```bash
# Install Python package
pip install -r requirements.txt
pip install -e .

# Load Chrome extension
chrome://extensions → Load unpacked → Select chrome_extension/
```

### Workflow

```bash
# Step 1: Map library with extension
# - Open Udio library page
# - Click extension icon
# - Click "Map Library"
# - Export JSON when complete

# Step 2: Import metadata
python -m udio_downloader import-metadata --json-file library_export.json

# Step 3: Download all content
python -m udio_downloader download --output ./downloads --concurrent 3

# Step 4: Check status
python -m udio_downloader status

# Step 5: Resume if interrupted
python -m udio_downloader download --output ./downloads --resume
```

## Future Enhancements

1. **Incremental Metadata Updates**
   - Track last collection date
   - Only process new/changed songs
   - Efficient delta updates

2. **Advanced Download Features**
   - Parallel chunk downloads for large files
   - Bandwidth throttling
   - Download scheduling

3. **Local UI (Phase 4)**
   - Web-based interface
   - Search and filter
   - Playback capability
   - Lyrics display

4. **Cloud Backup Integration**
   - Optional cloud sync
   - Encrypted backups
   - Multi-device access
