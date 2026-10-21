# Implementation Plan

- [x] 1. Set up database infrastructure with thread-safe writes





  - Create SQLite schema with numeric fields (duration_seconds, play_count) and resume metadata (etag, size)
  - Implement DatabaseManager class with single-writer thread pattern using work queue
  - Add indexes for performance optimization (folder_id, download_status, metadata_hash)
  - Implement connection management with check_same_thread configuration
  - _Requirements: 1.2, 1.3, 6.4_

- [x] 2. Refactor extension for MV3 compliance and robustness





  - [x] 2.1 Implement MV3 service worker orchestration


    - Move long-running scans from service worker to content script
    - Replace setTimeout/setInterval with chrome.alarms for periodic work
    - Implement message routing between service worker and content script
    - Add chrome.storage.local management for seen IDs cache
    - _Requirements: 2.1, 2.2_
  
  - [x] 2.2 Enhance content script for long-running scans


    - Refactor FolderMapper to run in content script context
    - Implement idempotent, resumable scan state
    - Add virtualized scroll loop with viewport-sized increments
    - Implement deduplication and stabilization detection
    - _Requirements: 2.1, 2.2, 2.5_
  
  - [x] 2.3 Extend SongExtractor with metadata hash and additional fields


    - Add artist extraction method
    - Add creation date extraction method
    - Add lyrics availability detection
    - Implement metadata hash generation for change detection
    - Add metadata collection timestamp
    - _Requirements: 1.1, 1.3, 1.4_
  
  - [x] 2.4 Create MetadataExporter with incremental update support


    - Implement folder tree flattening with stable IDs
    - Implement song extraction with metadata hashes
    - Integrate chrome.storage.local seen cache for incremental detection
    - Export stable IDs only (no transient URLs)
    - Implement chrome.downloads API export (requires user gesture)
    - _Requirements: 1.1, 1.3, 1.4, 1.5_
  
  - [x] 2.5 Update popup UI for export workflow


    - Add export button with user gesture handling
    - Wire export button to MetadataExporter
    - Display export progress and completion status
    - Show incremental update statistics (new/changed songs)



    - _Requirements: 1.1, 2.5_



- [ ] 3. Build Python metadata importer with hash-based updates

  - [ ] 3.1 Create MetadataImporter service class
    - Implement JSON file loading and validation (export version 2.0)
    - Implement folder import with stable ID handling


    - Implement song import with metadata hash comparison for updates
    - Implement tag relationship import
    - Use DatabaseManager write queue for thread-safe operations
    - _Requirements: 1.2, 1.3, 1.4_
  
  - [ ] 3.2 Add CLI command for metadata import
    - Create `import-metadata` command with JSON file parameter
    - Add database path configuration option
    - Display import statistics (added, updated, skipped, failed)
    - Show incremental update summary (new vs changed songs)
    - _Requirements: 1.2, 1.3, 1.4_

- [x] 4. Implement download manager with Playwright URL resolution



  - [x] 4.1 Create DownloadManager service class with Playwright integration


    - Initialize Playwright persistent context with userDataDir for authenticated session
    - Implement database query for pending/failed/partial songs
    - Implement folder structure creation matching database paths
    - Implement concurrent worker thread management with configurable worker count
    - Implement rate limiting with configurable delay
    - _Requirements: 3.1, 3.5, 4.1, 5.1, 5.2_
  
  - [x] 4.2 Implement Playwright URL resolution


    - Create method to navigate to song page and extract fresh URLs
    - Extract audio URL from page DOM
    - Extract lyrics URL from page DOM
    - Extract cover art URL from page DOM
    - Handle page load and network idle states
    - _Requirements: 2.1, 3.1, 3.2, 3.3_
  
  - [x] 4.3 Implement audio download with HTTP Range resume


    - Create audio download method with HEAD request for Accept-Ranges detection
    - Implement partial file validation with ETag and Content-Length
    - Implement HTTP Range request for resuming partial downloads
    - Save files as MP3 format in correct folder path
    - Update database with local file path, ETag, and size
    - _Requirements: 3.2, 4.2, 4.3_
  
  - [x] 4.4 Implement lyrics download functionality


    - Create lyrics extraction and download method using resolved URL
    - Save lyrics as TXT files with matching base filename
    - Update database lyrics table with content and timestamp
    - _Requirements: 3.3, 4.2_
  
  - [x] 4.5 Implement cover art and metadata download


    - Create cover art download method using resolved URL
    - Create metadata JSON file generation
    - Save cover art with appropriate image extension
    - Save metadata JSON with all song details
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 5. Add resume capability and comprehensive error handling





  - [x] 5.1 Implement robust resume logic


    - Query database for incomplete downloads (pending, failed, partial) on startup
    - Validate existing partial files with size and ETag comparison
    - Continue partial downloads using HTTP Range requests
    - Update download status for failed items to allow retry
    - Track resumed downloads separately in statistics
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [x] 5.2 Implement comprehensive error handling


    - Add retry logic with exponential backoff for network errors
    - Detect and handle rate limiting (429 responses) with worker pause
    - Handle Playwright page navigation failures with retry
    - Update database with error details for failed downloads (via write queue)
    - Log all errors with context for debugging
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 5.3_
  
  - [x] 5.3 Create progress tracking and reporting


    - Implement ProgressTracker class with tqdm integration
    - Display real-time progress with completed, failed, resumed, and rate statistics
    - Calculate and display estimated time remaining
    - Show per-worker status and active downloads
    - Provide summary report on completion with resume statistics
    - _Requirements: 2.5, 4.5, 5.4_


- [x] 6. Create CLI interface for download operations



  - [x] 6.1 Add download command


    - Create `download` command with output directory parameter
    - Add concurrent workers configuration option
    - Add resume flag (default enabled)
    - Wire command to DownloadManager
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.4, 5.1, 5.2_
  
  - [x] 6.2 Add status command


    - Create `status` command to query database statistics
    - Display total songs, completed, pending, and failed counts
    - Show folder structure summary
    - Display last run information
    - _Requirements: 4.5_

- [x] 7. Set up Playwright for authenticated session management




  - [x] 7.1 Add Playwright infrastructure


    - Add playwright Python dependency to requirements.txt
    - Run `playwright install` to download browser binaries
    - Create PlaywrightSessionManager service class
    - _Requirements: 2.1, 2.2_
  
  - [x] 7.2 Implement persistent context authentication


    - Create one-time login flow using launchPersistentContext with userDataDir
    - Implement session validation by checking for auth cookies
    - Add session refresh logic for expired sessions
    - Store persistent context path in configuration
    - _Requirements: 2.1, 2.2_
  
  - [x] 7.3 Integrate Playwright with DownloadManager


    - Pass authenticated Playwright context to DownloadManager
    - Implement page pooling for concurrent URL resolution
    - Enable Playwright debug mode (DEBUG=pw:api) for IDE logging
    - Add network request interception for debugging
    - _Requirements: 2.1, 2.2_
  
  - [ ]* 7.4 Add Playwright codegen and trace viewer integration
    - Document how to use `playwright codegen` for updating selectors
    - Create helper script to record new flows
    - Add trace viewer integration for debugging failed runs
    - Document how to use `playwright show-trace` for analysis
    - _Requirements: 2.2_

- [ ]* 8. Add incremental update support
  - Track last metadata collection run in database
  - Implement change detection for updated songs
  - Skip already-processed songs during collection
  - _Requirements: 1.3, 1.4_

- [ ]* 9. Create database export utility
  - Implement JSON export from database for backup
  - Add export command to CLI
  - Include all tables in portable format
  - _Requirements: 6.5_
