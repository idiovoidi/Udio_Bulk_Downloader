"""Download manager service with Playwright URL resolution and concurrent downloads."""

import asyncio
import logging
import time
import threading
import sqlite3
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
import random
import os

import requests
from playwright.async_api import BrowserContext, Page, TimeoutError as PlaywrightTimeoutError

from .database_manager import DatabaseManager
from .progress_tracker import ProgressTracker
from .playwright_session_manager import PlaywrightSessionManager


logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry logic with exponential backoff."""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delays
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number.
        
        Args:
            attempt: Attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        delay = min(
            self.initial_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        
        if self.jitter:
            # Add random jitter (±25%)
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)


class RateLimitHandler:
    """Handles rate limiting detection and worker pausing."""
    
    def __init__(self, pause_duration: float = 60.0):
        """
        Initialize rate limit handler.
        
        Args:
            pause_duration: How long to pause workers when rate limited (seconds)
        """
        self.pause_duration = pause_duration
        self.is_paused = threading.Event()
        self.pause_until = 0.0
        self.lock = threading.Lock()
    
    def trigger_rate_limit(self):
        """Trigger rate limit pause for all workers."""
        with self.lock:
            self.pause_until = time.time() + self.pause_duration
            self.is_paused.set()
            logger.warning(
                f"Rate limit detected! Pausing all workers for {self.pause_duration}s"
            )
    
    def check_and_wait(self):
        """Check if rate limited and wait if necessary."""
        if self.is_paused.is_set():
            with self.lock:
                remaining = self.pause_until - time.time()
                
                if remaining > 0:
                    logger.info(f"Worker paused due to rate limit, waiting {remaining:.1f}s")
                    time.sleep(remaining)
                
                # Clear pause if time has elapsed
                if time.time() >= self.pause_until:
                    self.is_paused.clear()
                    logger.info("Rate limit pause ended, resuming workers")
    
    def is_rate_limited(self) -> bool:
        """Check if currently rate limited."""
        return self.is_paused.is_set()


class DownloadManager:
    """Orchestrates concurrent downloads with Playwright URL resolution."""
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        output_dir: str,
        session_manager: PlaywrightSessionManager,
        concurrent_workers: int = 3,
        rate_limit_delay: float = 1.0,
        retry_config: Optional[RetryConfig] = None
    ):
        """
        Initialize download manager.
        
        Args:
            db_manager: DatabaseManager instance for database operations
            output_dir: Base directory for downloaded files
            session_manager: PlaywrightSessionManager for authenticated browser context
            concurrent_workers: Number of concurrent download workers
            rate_limit_delay: Minimum delay between downloads in seconds
            retry_config: Optional retry configuration (uses defaults if None)
        """
        self.db = db_manager
        self.output_dir = Path(output_dir)
        self.session_manager = session_manager
        self.concurrent_workers = concurrent_workers
        self.rate_limit_delay = rate_limit_delay
        
        # Retry and rate limit handling
        self.retry_config = retry_config or RetryConfig()
        self.rate_limit_handler = RateLimitHandler()
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # HTTP session for downloads
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Playwright context (from session manager)
        self.browser_context: Optional[BrowserContext] = None
        
        # Page pool for concurrent URL resolution
        self.page_pool: List[Page] = []
        self.page_pool_lock = threading.Lock()
        
        # Worker management
        self.work_queue: Queue = Queue()
        self.results_queue: Queue = Queue()
        self.workers: List[DownloadWorker] = []
        
        # Progress tracking
        self.progress_tracker: Optional[ProgressTracker] = None
        
        # Debug mode
        self.debug_mode = os.getenv('DEBUG', '').lower().startswith('pw')
        
        logger.info(f"DownloadManager initialized with {concurrent_workers} workers")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Retry config: max_retries={self.retry_config.max_retries}")
        logger.info(f"Debug mode: {self.debug_mode}")
    
    async def _initialize_playwright(self):
        """Initialize Playwright with persistent authenticated context."""
        logger.info("Initializing Playwright browser context...")
        
        # Get browser context from session manager
        self.browser_context = await self.session_manager.get_context()
        
        if not self.browser_context:
            raise RuntimeError("Failed to initialize Playwright browser context")
        
        # Validate session
        if not self.session_manager.is_authenticated:
            logger.warning("Session not authenticated, attempting to refresh...")
            success = await self.session_manager.refresh_session()
            if not success:
                raise RuntimeError(
                    "Failed to authenticate Playwright session. "
                    "Please ensure you are logged in to Udio."
                )
        
        # Enable debug mode if requested
        if self.debug_mode:
            logger.info("Playwright debug mode enabled (DEBUG=pw:api)")
            # Network request interception for debugging
            await self._setup_network_interception()
        
        # Initialize page pool for concurrent URL resolution
        await self._initialize_page_pool()
        
        logger.info("Playwright browser context initialized and authenticated")
    
    async def _setup_network_interception(self):
        """Setup network request interception for debugging."""
        if not self.browser_context:
            return
        
        async def log_request(route, request):
            """Log network requests for debugging."""
            logger.debug(f"Request: {request.method} {request.url}")
            await route.continue_()
        
        # Intercept all requests for logging
        await self.browser_context.route('**/*', log_request)
        logger.info("Network request interception enabled for debugging")
    
    async def _initialize_page_pool(self):
        """Initialize page pool for concurrent URL resolution."""
        logger.info(f"Initializing page pool with {self.concurrent_workers} pages...")
        
        for i in range(self.concurrent_workers):
            page = await self.browser_context.new_page()
            self.page_pool.append(page)
            logger.debug(f"Created page {i + 1}/{self.concurrent_workers}")
        
        logger.info(f"Page pool initialized with {len(self.page_pool)} pages")
    
    async def _get_page_from_pool(self) -> Optional[Page]:
        """
        Get a page from the pool for URL resolution.
        
        Returns:
            Page instance or None if pool is empty
        """
        with self.page_pool_lock:
            if self.page_pool:
                return self.page_pool.pop()
            return None
    
    async def _return_page_to_pool(self, page: Page):
        """
        Return a page to the pool after use.
        
        Args:
            page: Page instance to return
        """
        with self.page_pool_lock:
            self.page_pool.append(page)
    
    async def _cleanup_playwright(self):
        """Cleanup Playwright resources."""
        logger.info("Cleaning up Playwright resources...")
        
        # Close all pages in pool
        for page in self.page_pool:
            try:
                await page.close()
            except Exception as e:
                logger.error(f"Error closing page: {e}")
        
        self.page_pool.clear()
        
        # Note: We don't cleanup the session manager here as it may be reused
        # The session manager should be cleaned up by the caller
        
        logger.info("Playwright resources cleaned up")
    
    def start_downloads(self, resume: bool = True) -> Dict[str, any]:
        """
        Start download process.
        
        Process:
        1. Query database for pending/failed/partial songs
        2. Validate existing partial files with size and ETag comparison
        3. Create folder structure
        4. Initialize Playwright context
        5. Start worker threads
        6. For each song: resolve fresh URLs via Playwright
        7. Download audio (with Range resume), lyrics, cover art
        8. Update database with results (via write queue)
        9. Return statistics with resumed downloads tracked separately
        
        Args:
            resume: If True, include failed and partial downloads
            
        Returns:
            Dictionary with statistics: {
                total: int,
                completed: int,
                failed: int,
                skipped: int,
                resumed: int,
                duration: float
            }
        """
        start_time = time.time()
        
        # Get songs to download (includes pending, failed, partial)
        songs = self.db.get_pending_downloads()
        
        if not songs:
            logger.info("No songs to download")
            return {
                'total': 0,
                'completed': 0,
                'failed': 0,
                'skipped': 0,
                'resumed': 0,
                'duration': 0.0
            }
        
        # Validate and categorize songs for resume
        pending_count = sum(1 for s in songs if s['download_status'] == 'pending')
        failed_count = sum(1 for s in songs if s['download_status'] == 'failed')
        partial_count = sum(1 for s in songs if s['download_status'] == 'partial')
        
        logger.info(
            f"Found {len(songs)} songs to download: "
            f"{pending_count} pending, {failed_count} failed, {partial_count} partial"
        )
        
        # Reset failed items to allow retry
        if resume and failed_count > 0:
            logger.info(f"Resetting {failed_count} failed downloads for retry")
            self._reset_failed_downloads()
        
        # Initialize progress tracker
        self.progress_tracker = ProgressTracker(
            total_songs=len(songs),
            concurrent_workers=self.concurrent_workers,
            show_worker_status=True
        )
        
        # Initialize Playwright in async context
        asyncio.run(self._initialize_playwright())
        
        try:
            # Create folder structure
            self._create_all_folders(songs)
            
            # Populate work queue
            for song in songs:
                self.work_queue.put(song)
            
            # Add poison pills for workers
            for _ in range(self.concurrent_workers):
                self.work_queue.put(None)
            
            # Start worker threads
            self._start_workers()
            
            # Process results
            processed = 0
            while processed < len(songs):
                try:
                    result = self.results_queue.get(timeout=1)
                    processed += 1
                    
                    # Update progress tracker
                    self.progress_tracker.update(result)
                    
                    # Periodically show worker status
                    if processed % 20 == 0:
                        self.progress_tracker.print_worker_status()
                
                except Empty:
                    continue
            
            # Wait for all workers to finish
            for worker in self.workers:
                worker.thread.join()
            
        finally:
            # Cleanup Playwright
            asyncio.run(self._cleanup_playwright())
            
            # Close progress tracker
            if self.progress_tracker:
                self.progress_tracker.close()
        
        # Get final statistics from progress tracker
        summary = self.progress_tracker.get_summary()
        
        # Print final summary
        self.progress_tracker.print_summary()
        
        # Return statistics in expected format
        stats = {
            'total': summary['total'],
            'completed': summary['completed'],
            'failed': summary['failed'],
            'skipped': summary['skipped'],
            'resumed': summary['resumed'],
            'duration': summary['elapsed_seconds']
        }
        
        logger.info(
            f"Download complete: {stats['completed']} completed, "
            f"{stats['failed']} failed, {stats['skipped']} skipped "
            f"in {stats['duration']:.1f}s"
        )
        
        return stats
    
    def _create_all_folders(self, songs: List[dict]):
        """
        Create local folder structure for all songs.
        
        Args:
            songs: List of song dictionaries
        """
        folders_created = set()
        
        for song in songs:
            folder_id = song.get('folder_id')
            if folder_id and folder_id not in folders_created:
                folder_path = self._get_folder_path(folder_id)
                if folder_path:
                    folder_path.mkdir(parents=True, exist_ok=True)
                    folders_created.add(folder_id)
        
        logger.info(f"Created {len(folders_created)} folders")
    
    def _get_folder_path(self, folder_id: str) -> Optional[Path]:
        """
        Get local folder path for a folder ID.
        
        Args:
            folder_id: Folder ID from database
            
        Returns:
            Path object for the folder, or None if not found
        """
        # Query database for folder path
        conn = self.db._get_read_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT path FROM folders WHERE id = ?", (folder_id,))
            row = cursor.fetchone()
            
            if row:
                import json
                path_parts = json.loads(row['path']) if isinstance(row['path'], str) else row['path']
                return self.output_dir / Path(*path_parts)
            
            return None
            
        finally:
            conn.close()
    
    def _start_workers(self):
        """Start download worker threads."""
        self.workers = []
        
        for worker_id in range(self.concurrent_workers):
            worker = DownloadWorker(
                worker_id=worker_id,
                download_manager=self,
                work_queue=self.work_queue,
                results_queue=self.results_queue
            )
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Started {len(self.workers)} download workers")
    
    def _reset_failed_downloads(self):
        """Reset failed downloads to pending status to allow retry."""
        def operation(conn: sqlite3.Connection):
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE songs 
                SET download_status = 'pending', download_error = NULL
                WHERE download_status = 'failed'
            """)
            logger.info(f"Reset {cursor.rowcount} failed downloads to pending")
        
        self.db._execute_write(operation)
        # Wait for write to complete
        self.db.write_queue.join()
    
    def _validate_partial_file(
        self,
        file_path: Path,
        expected_etag: Optional[str],
        expected_size: Optional[int]
    ) -> Tuple[bool, int]:
        """
        Validate existing partial file for resume capability.
        
        Checks:
        1. File exists
        2. File size matches database record (if available)
        3. File size is less than expected total size
        
        Args:
            file_path: Path to partial file
            expected_etag: Expected ETag from database
            expected_size: Expected file size from database
            
        Returns:
            Tuple of (is_valid, actual_size)
        """
        if not file_path.exists():
            return False, 0
        
        actual_size = file_path.stat().st_size
        
        # File with 0 bytes is not valid
        if actual_size == 0:
            logger.debug(f"Partial file {file_path.name} has 0 bytes, invalid")
            return False, 0
        
        # If we have expected size, validate it
        if expected_size is not None:
            if actual_size == expected_size:
                # File is complete
                logger.debug(f"Partial file {file_path.name} is complete ({actual_size} bytes)")
                return True, actual_size
            elif actual_size > expected_size:
                # File is corrupted (larger than expected)
                logger.warning(
                    f"Partial file {file_path.name} is corrupted "
                    f"(actual: {actual_size}, expected: {expected_size})"
                )
                return False, actual_size
        
        # Partial file is valid for resume
        logger.debug(f"Partial file {file_path.name} is valid for resume ({actual_size} bytes)")
        return True, actual_size
    
    async def resolve_song_urls(self, song_id: str) -> Dict[str, Optional[str]]:
        """
        Use Playwright to navigate to song page and extract fresh URLs with retry logic.
        
        This method resolves transient URLs at download time by:
        1. Getting a page from the pool (or creating new if pool empty)
        2. Navigating to the song page (with retries)
        3. Waiting for page to load and network to be idle
        4. Extracting audio, lyrics, and cover art URLs from DOM
        5. Returning page to pool for reuse
        
        Args:
            song_id: Udio song ID
            
        Returns:
            Dictionary with keys: audio_url, lyrics_url, cover_url
            Values are None if not found
        """
        if not self.browser_context:
            raise RuntimeError("Playwright browser context not initialized")
        
        last_error = None
        
        # Get page from pool or create new one
        page = await self._get_page_from_pool()
        if not page:
            logger.debug("Page pool empty, creating new page")
            page = await self.browser_context.new_page()
            from_pool = False
        else:
            from_pool = True
        
        try:
            # Retry with exponential backoff
            for attempt in range(self.retry_config.max_retries):
                try:
                    song_url = f'https://www.udio.com/songs/{song_id}'
                    
                    if attempt > 0:
                        logger.info(f"Retry attempt {attempt + 1}/{self.retry_config.max_retries} for {song_id}")
                    
                    logger.debug(f"Navigating to {song_url}")
                    
                    # Navigate to song page
                    await page.goto(song_url, wait_until='domcontentloaded', timeout=30000)
                    
                    # Wait for network to be idle (content loaded)
                    await page.wait_for_load_state('networkidle', timeout=30000)
                    
                    # Extract audio URL
                    audio_url = await self._extract_audio_url(page)
                    
                    # Extract cover art URL
                    cover_url = await self._extract_cover_url(page)
                    
                    # Extract lyrics URL
                    lyrics_url = await self._extract_lyrics_url(page)
                    
                    logger.debug(
                        f"Resolved URLs for {song_id}: "
                        f"audio={bool(audio_url)}, "
                        f"cover={bool(cover_url)}, "
                        f"lyrics={bool(lyrics_url)}"
                    )
                    
                    return {
                        'audio_url': audio_url,
                        'lyrics_url': lyrics_url,
                        'cover_url': cover_url
                    }
                    
                except PlaywrightTimeoutError as e:
                    last_error = e
                    logger.warning(f"Timeout resolving URLs for {song_id} (attempt {attempt + 1}): {e}")
                    
                    if attempt < self.retry_config.max_retries - 1:
                        delay = self.retry_config.get_delay(attempt)
                        logger.info(f"Waiting {delay:.1f}s before retry...")
                        await asyncio.sleep(delay)
                    
                except Exception as e:
                    last_error = e
                    logger.error(f"Error resolving URLs for {song_id} (attempt {attempt + 1}): {e}")
                    
                    if attempt < self.retry_config.max_retries - 1:
                        delay = self.retry_config.get_delay(attempt)
                        logger.info(f"Waiting {delay:.1f}s before retry...")
                        await asyncio.sleep(delay)
            
            # All retries failed
            logger.error(
                f"Failed to resolve URLs for song {song_id} after "
                f"{self.retry_config.max_retries} attempts: {last_error}"
            )
            
            return {
                'audio_url': None,
                'lyrics_url': None,
                'cover_url': None
            }
            
        finally:
            # Return page to pool if it came from pool
            if from_pool:
                await self._return_page_to_pool(page)
            else:
                # Close page if it was created ad-hoc
                await page.close()
    
    async def _extract_audio_url(self, page: Page) -> Optional[str]:
        """
        Extract audio URL from page DOM.
        
        Looks for:
        - <audio> element src attribute
        - <source> element within audio tag
        - Data attributes containing audio URL
        
        Args:
            page: Playwright page object
            
        Returns:
            Audio URL or None if not found
        """
        try:
            # Try audio element src
            audio_url = await page.evaluate('''() => {
                const audio = document.querySelector('audio');
                if (audio && audio.src) return audio.src;
                
                // Try source element
                const source = document.querySelector('audio source');
                if (source && source.src) return source.src;
                
                // Try data attributes
                const audioWithData = document.querySelector('[data-audio-url]');
                if (audioWithData) return audioWithData.getAttribute('data-audio-url');
                
                return null;
            }''')
            
            return audio_url if audio_url else None
            
        except Exception as e:
            logger.error(f"Error extracting audio URL: {e}")
            return None
    
    async def _extract_lyrics_url(self, page: Page) -> Optional[str]:
        """
        Extract lyrics URL from page DOM.
        
        Looks for:
        - Links with 'lyrics' in href or text
        - Data attributes containing lyrics URL
        - API endpoints for lyrics
        
        Args:
            page: Playwright page object
            
        Returns:
            Lyrics URL or None if not found
        """
        try:
            lyrics_url = await page.evaluate('''() => {
                // Try data attribute
                const lyricsElement = document.querySelector('[data-lyrics-url]');
                if (lyricsElement) return lyricsElement.getAttribute('data-lyrics-url');
                
                // Try link with 'lyrics' in href
                const lyricsLink = document.querySelector('a[href*="lyrics"]');
                if (lyricsLink) return lyricsLink.href;
                
                // Try to find lyrics content directly (may be embedded)
                const lyricsContent = document.querySelector('.lyrics, [class*="lyrics"]');
                if (lyricsContent) return 'embedded';
                
                return null;
            }''')
            
            return lyrics_url if lyrics_url else None
            
        except Exception as e:
            logger.error(f"Error extracting lyrics URL: {e}")
            return None
    
    async def _extract_cover_url(self, page: Page) -> Optional[str]:
        """
        Extract cover art URL from page DOM.
        
        Looks for:
        - Main song image/cover art
        - og:image meta tag
        - Data attributes containing cover URL
        
        Args:
            page: Playwright page object
            
        Returns:
            Cover art URL or None if not found
        """
        try:
            cover_url = await page.evaluate('''() => {
                // Try og:image meta tag
                const ogImage = document.querySelector('meta[property="og:image"]');
                if (ogImage) return ogImage.getAttribute('content');
                
                // Try main image with alt text
                const mainImage = document.querySelector('img[alt*="cover"], img[alt*="artwork"]');
                if (mainImage && mainImage.src) return mainImage.src;
                
                // Try data attribute
                const coverElement = document.querySelector('[data-cover-url]');
                if (coverElement) return coverElement.getAttribute('data-cover-url');
                
                // Try first large image (fallback)
                const images = document.querySelectorAll('img');
                for (const img of images) {
                    if (img.naturalWidth >= 300 && img.src && !img.src.includes('icon')) {
                        return img.src;
                    }
                }
                
                return null;
            }''')
            
            return cover_url if cover_url else None
            
        except Exception as e:
            logger.error(f"Error extracting cover URL: {e}")
            return None
    
    def download_audio_with_resume(
        self,
        url: str,
        output_path: Path,
        existing_size: int = 0,
        existing_etag: Optional[str] = None
    ) -> Tuple[Path, Optional[str], int, bool]:
        """
        Download MP3 with HTTP Range resume support.
        
        Process:
        1. Send HEAD request to check Accept-Ranges and get Content-Length/ETag
        2. Validate existing partial file with size and ETag comparison
        3. If file exists and matches size, skip download
        4. If partial file exists and server supports Range, resume from offset
        5. Otherwise, perform full download
        6. Return path, etag, final size, and whether it was resumed
        
        Args:
            url: Audio file URL
            output_path: Local path to save file
            existing_size: Size of existing partial file from database (0 if none)
            existing_etag: ETag of existing partial file from database (None if none)
            
        Returns:
            Tuple of (path, etag, size, was_resumed)
            
        Raises:
            requests.RequestException: On download failure
        """
        was_resumed = False
        last_error = None
        
        # Send HEAD request to get file metadata with retry
        head_response = None
        for attempt in range(self.retry_config.max_retries):
            try:
                head_response = self.session.head(url, allow_redirects=True, timeout=10)
                
                # Check for rate limiting
                if head_response.status_code == 429:
                    logger.warning(f"Rate limit detected (429) on HEAD request")
                    self.rate_limit_handler.trigger_rate_limit()
                    
                    if attempt < self.retry_config.max_retries - 1:
                        delay = self.retry_config.get_delay(attempt)
                        logger.info(f"Waiting {delay:.1f}s before retry...")
                        time.sleep(delay)
                        continue
                
                head_response.raise_for_status()
                break  # Success
                
            except requests.RequestException as e:
                last_error = e
                logger.warning(f"HEAD request failed (attempt {attempt + 1}): {e}")
                
                if attempt < self.retry_config.max_retries - 1:
                    delay = self.retry_config.get_delay(attempt)
                    logger.info(f"Waiting {delay:.1f}s before retry...")
                    time.sleep(delay)
                else:
                    logger.error(f"HEAD request failed after {self.retry_config.max_retries} attempts: {e}")
                    raise
        
        # Get server metadata
        accept_ranges = head_response.headers.get('Accept-Ranges', 'none')
        content_length = int(head_response.headers.get('Content-Length', 0))
        server_etag = head_response.headers.get('ETag')
        
        logger.debug(
            f"Server metadata: Accept-Ranges={accept_ranges}, "
            f"Content-Length={content_length}, ETag={server_etag}"
        )
        
        # Validate existing partial file
        if output_path.exists():
            is_valid, actual_size = self._validate_partial_file(
                output_path,
                existing_etag,
                content_length
            )
            
            # File is complete
            if actual_size == content_length and is_valid:
                logger.info(f"File already complete: {output_path.name}")
                return (output_path, server_etag, actual_size, False)
            
            # File is corrupted or invalid
            if not is_valid and actual_size > 0:
                logger.warning(f"Removing corrupted partial file: {output_path.name}")
                output_path.unlink()
                actual_size = 0
            
            # Try to resume if server supports Range requests
            if is_valid and accept_ranges == 'bytes' and 0 < actual_size < content_length:
                # Validate ETag matches if available
                if existing_etag and server_etag and existing_etag != server_etag:
                    logger.warning(
                        f"ETag mismatch (local: {existing_etag}, server: {server_etag}), "
                        "cannot resume, starting fresh"
                    )
                    output_path.unlink()
                else:
                    logger.info(
                        f"Resuming download from byte {actual_size} "
                        f"({actual_size / content_length * 100:.1f}% complete)"
                    )
                    
                    headers = {'Range': f'bytes={actual_size}-'}
                    
                    # Add If-Range header if we have matching ETag
                    if existing_etag and server_etag and existing_etag == server_etag:
                        headers['If-Range'] = existing_etag
                    
                    # Try resume with retry logic
                    for attempt in range(self.retry_config.max_retries):
                        try:
                            response = self.session.get(
                                url,
                                headers=headers,
                                stream=True,
                                timeout=30
                            )
                            
                            # Check for rate limiting
                            if response.status_code == 429:
                                logger.warning(f"Rate limit detected (429) on resume request")
                                self.rate_limit_handler.trigger_rate_limit()
                                
                                if attempt < self.retry_config.max_retries - 1:
                                    delay = self.retry_config.get_delay(attempt)
                                    logger.info(f"Waiting {delay:.1f}s before retry...")
                                    time.sleep(delay)
                                    continue
                            
                            # Check if server accepted range request
                            if response.status_code == 206:  # Partial Content
                                logger.info("Server accepted range request, resuming download")
                                was_resumed = True
                                
                                # Append to existing file
                                with open(output_path, 'ab') as f:
                                    for chunk in response.iter_content(chunk_size=8192):
                                        if chunk:
                                            f.write(chunk)
                                
                                final_size = output_path.stat().st_size
                                
                                # Verify final size matches expected
                                if final_size != content_length:
                                    logger.error(
                                        f"Resume download size mismatch: "
                                        f"expected {content_length}, got {final_size}"
                                    )
                                    raise ValueError("Downloaded file size mismatch")
                                
                                logger.info(
                                    f"Resume download complete: {output_path.name} ({final_size} bytes)"
                                )
                                return (output_path, server_etag, final_size, was_resumed)
                            
                            else:
                                logger.warning(
                                    f"Server returned {response.status_code}, "
                                    "falling back to full download"
                                )
                                output_path.unlink()
                                break  # Exit retry loop, fall through to full download
                                
                        except requests.RequestException as e:
                            logger.warning(f"Resume failed (attempt {attempt + 1}): {e}")
                            
                            if attempt < self.retry_config.max_retries - 1:
                                delay = self.retry_config.get_delay(attempt)
                                logger.info(f"Waiting {delay:.1f}s before retry...")
                                time.sleep(delay)
                            else:
                                logger.warning("Resume failed after all retries, falling back to full download")
                                if output_path.exists():
                                    output_path.unlink()
                                break
        
        # Full download with retry logic
        logger.info(f"Starting full download: {output_path.name}")
        
        for attempt in range(self.retry_config.max_retries):
            try:
                response = self.session.get(url, stream=True, timeout=30)
                
                # Check for rate limiting
                if response.status_code == 429:
                    logger.warning(f"Rate limit detected (429) on download request")
                    self.rate_limit_handler.trigger_rate_limit()
                    
                    if attempt < self.retry_config.max_retries - 1:
                        delay = self.retry_config.get_delay(attempt)
                        logger.info(f"Waiting {delay:.1f}s before retry...")
                        time.sleep(delay)
                        continue
                
                response.raise_for_status()
                
                # Ensure parent directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Download file
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                final_size = output_path.stat().st_size
                
                # Verify final size matches expected
                if content_length > 0 and final_size != content_length:
                    logger.error(
                        f"Download size mismatch: expected {content_length}, got {final_size}"
                    )
                    
                    if attempt < self.retry_config.max_retries - 1:
                        logger.info("Retrying download due to size mismatch...")
                        delay = self.retry_config.get_delay(attempt)
                        time.sleep(delay)
                        continue
                    else:
                        raise ValueError("Downloaded file size mismatch after all retries")
                
                logger.info(f"Full download complete: {output_path.name} ({final_size} bytes)")
                
                return (output_path, server_etag, final_size, was_resumed)
                
            except requests.RequestException as e:
                logger.warning(f"Download failed (attempt {attempt + 1}): {e}")
                
                if attempt < self.retry_config.max_retries - 1:
                    delay = self.retry_config.get_delay(attempt)
                    logger.info(f"Waiting {delay:.1f}s before retry...")
                    time.sleep(delay)
                else:
                    logger.error(f"Download failed after {self.retry_config.max_retries} attempts: {e}")
                    # Mark as partial if we have some data
                    if output_path.exists() and output_path.stat().st_size > 0:
                        logger.info("Marking download as partial for future resume")
                    raise
    
    async def download_lyrics(
        self,
        song_id: str,
        lyrics_url: Optional[str],
        output_path: Path,
        page: Optional[Page] = None
    ) -> Optional[Path]:
        """
        Download and save lyrics as TXT file.
        
        Handles two cases:
        1. lyrics_url is a URL: fetch lyrics from URL
        2. lyrics_url is 'embedded': extract lyrics from page DOM
        
        Args:
            song_id: Song ID for database update
            lyrics_url: Lyrics URL or 'embedded' or None
            output_path: Local path to save lyrics file
            page: Optional Playwright page (needed for embedded lyrics)
            
        Returns:
            Path to saved lyrics file, or None if no lyrics available
        """
        if not lyrics_url:
            logger.debug(f"No lyrics available for song {song_id}")
            return None
        
        try:
            lyrics_text = None
            
            # Case 1: Embedded lyrics in page
            if lyrics_url == 'embedded':
                if not page:
                    logger.warning("Cannot extract embedded lyrics without page object")
                    return None
                
                lyrics_text = await page.evaluate('''() => {
                    const lyricsElement = document.querySelector('.lyrics, [class*="lyrics"]');
                    return lyricsElement ? lyricsElement.textContent.trim() : null;
                }''')
            
            # Case 2: Lyrics from URL
            else:
                try:
                    response = self.session.get(lyrics_url, timeout=10)
                    response.raise_for_status()
                    
                    # Check content type
                    content_type = response.headers.get('Content-Type', '')
                    
                    if 'json' in content_type:
                        # Lyrics might be in JSON format
                        data = response.json()
                        lyrics_text = data.get('lyrics') or data.get('text')
                    else:
                        # Plain text lyrics
                        lyrics_text = response.text
                        
                except requests.RequestException as e:
                    logger.error(f"Failed to fetch lyrics from {lyrics_url}: {e}")
                    return None
            
            # Save lyrics if we got any
            if lyrics_text:
                # Ensure parent directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save as UTF-8 text file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(lyrics_text)
                
                logger.info(f"Lyrics saved: {output_path.name}")
                
                # Update database lyrics table
                self._update_lyrics_in_db(song_id, lyrics_text)
                
                return output_path
            else:
                logger.debug(f"No lyrics text found for song {song_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to download lyrics for song {song_id}: {e}")
            return None
    
    def _update_lyrics_in_db(self, song_id: str, lyrics_text: str):
        """
        Update lyrics table in database.
        
        Args:
            song_id: Song ID
            lyrics_text: Lyrics content
        """
        def operation(conn):
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO lyrics (song_id, lyrics_text, downloaded_at)
                VALUES (?, ?, ?)
            """, (song_id, lyrics_text, time.strftime('%Y-%m-%d %H:%M:%S')))
        
        self.db._execute_write(operation)
    
    def download_cover_art(
        self,
        cover_url: Optional[str],
        output_path: Path
    ) -> Optional[Path]:
        """
        Download cover art image.
        
        Args:
            cover_url: Cover art URL
            output_path: Base path (extension will be determined from content type)
            
        Returns:
            Path to saved cover art file, or None if download failed
        """
        if not cover_url:
            logger.debug("No cover art URL provided")
            return None
        
        try:
            response = self.session.get(cover_url, timeout=10)
            response.raise_for_status()
            
            # Determine file extension from content type
            content_type = response.headers.get('Content-Type', '')
            extension = self._get_image_extension(content_type)
            
            # Update output path with correct extension
            final_path = output_path.with_suffix(extension)
            
            # Ensure parent directory exists
            final_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save image
            with open(final_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Cover art saved: {final_path.name}")
            return final_path
            
        except requests.RequestException as e:
            logger.error(f"Failed to download cover art from {cover_url}: {e}")
            return None
    
    def _get_image_extension(self, content_type: str) -> str:
        """
        Get file extension from content type.
        
        Args:
            content_type: HTTP Content-Type header value
            
        Returns:
            File extension with dot (e.g., '.jpg')
        """
        content_type = content_type.lower()
        
        if 'jpeg' in content_type or 'jpg' in content_type:
            return '.jpg'
        elif 'png' in content_type:
            return '.png'
        elif 'webp' in content_type:
            return '.webp'
        elif 'gif' in content_type:
            return '.gif'
        else:
            # Default to jpg
            return '.jpg'
    
    def save_metadata_json(
        self,
        song: dict,
        output_path: Path,
        tags: Optional[List[str]] = None
    ) -> Path:
        """
        Save song metadata as JSON file.
        
        Args:
            song: Song dictionary from database
            output_path: Path to save JSON file
            tags: Optional list of tags for the song
            
        Returns:
            Path to saved metadata file
        """
        import json
        
        # Build metadata dictionary
        metadata = {
            'id': song['id'],
            'title': song['title'],
            'artist': song.get('artist'),
            'duration_seconds': song.get('duration_seconds'),
            'created_date': song.get('created_date'),
            'is_liked': bool(song.get('is_liked')),
            'is_disliked': bool(song.get('is_disliked')),
            'play_count': song.get('play_count', 0),
            'likes_count': song.get('likes_count', 0),
            'lyrics_available': bool(song.get('lyrics_available')),
            'tags': tags or [],
            'metadata_collected_at': song.get('metadata_collected_at'),
            'downloaded_at': song.get('downloaded_at')
        }
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as formatted JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Metadata saved: {output_path.name}")
        return output_path
    
    def get_song_tags(self, song_id: str) -> List[str]:
        """
        Get tags for a song from database.
        
        Args:
            song_id: Song ID
            
        Returns:
            List of tag strings
        """
        conn = self.db._get_read_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT tag FROM tags WHERE song_id = ?", (song_id,))
            rows = cursor.fetchall()
            return [row['tag'] for row in rows]
        finally:
            conn.close()


class DownloadWorker:
    """Worker thread for concurrent downloads."""
    
    def __init__(
        self,
        worker_id: int,
        download_manager: DownloadManager,
        work_queue: Queue,
        results_queue: Queue
    ):
        """
        Initialize download worker.
        
        Args:
            worker_id: Unique worker identifier
            download_manager: Parent DownloadManager instance
            work_queue: Queue of songs to download
            results_queue: Queue for download results
        """
        self.worker_id = worker_id
        self.manager = download_manager
        self.work_queue = work_queue
        self.results_queue = results_queue
        self.thread: Optional[threading.Thread] = None
        
        logger.debug(f"Worker {worker_id} initialized")
    
    def start(self):
        """Start the worker thread."""
        self.thread = threading.Thread(
            target=self.run,
            name=f"DownloadWorker-{self.worker_id}",
            daemon=True
        )
        self.thread.start()
    
    def run(self):
        """Process songs from work queue."""
        logger.info(f"Worker {self.worker_id} started")
        
        while True:
            try:
                # Check for rate limiting and wait if necessary
                self.manager.rate_limit_handler.check_and_wait()
                
                # Get song from queue
                song = self.work_queue.get(timeout=1)
                
                if song is None:  # Poison pill
                    logger.info(f"Worker {self.worker_id} received shutdown signal")
                    break
                
                # Process song
                result = self._process_song(song)
                self.results_queue.put(result)
                
                # Rate limiting delay
                time.sleep(self.manager.rate_limit_delay)
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Worker {self.worker_id} error: {e}", exc_info=True)
        
        logger.info(f"Worker {self.worker_id} stopped")
    
    def _process_song(self, song: dict) -> Dict[str, any]:
        """
        Process a single song download.
        
        Args:
            song: Song dictionary from database
            
        Returns:
            Result dictionary with status and details
        """
        song_id = song['id']
        title = song['title']
        
        logger.info(f"Worker {self.worker_id}: Processing song {song_id} - {title}")
        
        # Update progress tracker with worker status
        if self.manager.progress_tracker:
            self.manager.progress_tracker.update_worker_status(
                worker_id=self.worker_id,
                song_title=title,
                song_id=song_id,
                status='downloading'
            )
        
        result = {
            'song_id': song_id,
            'status': 'failed',
            'error': None,
            'resumed': False,
            'worker_id': self.worker_id
        }
        
        try:
            # Check if already completed
            if song['download_status'] == 'completed':
                logger.info(f"Song {song_id} already completed, skipping")
                result['status'] = 'skipped'
                return result
            
            # Determine output folder
            folder_id = song.get('folder_id')
            if folder_id:
                folder_path = self.manager._get_folder_path(folder_id)
            else:
                folder_path = self.manager.output_dir
            
            if not folder_path:
                raise ValueError(f"Could not determine folder path for song {song_id}")
            
            # Sanitize filename
            safe_title = self._sanitize_filename(title)
            base_filename = f"{safe_title}_{song_id}"
            
            # Define output paths
            audio_path = folder_path / f"{base_filename}.mp3"
            lyrics_path = folder_path / f"{base_filename}_lyrics.txt"
            cover_path = folder_path / f"{base_filename}_cover"  # Extension added by download
            metadata_path = folder_path / f"{base_filename}_metadata.json"
            
            # Check for partial download and validate
            existing_size = song.get('local_audio_size', 0)
            existing_etag = song.get('local_audio_etag')
            
            # Validate existing partial file if present
            if audio_path.exists():
                is_valid, actual_size = self.manager._validate_partial_file(
                    audio_path,
                    existing_etag,
                    existing_size
                )
                
                if is_valid and actual_size > 0:
                    logger.info(
                        f"Found valid partial download: {actual_size} bytes "
                        f"({actual_size / (existing_size or 1) * 100:.1f}% if size known)"
                    )
                    existing_size = actual_size
                elif not is_valid and actual_size > 0:
                    logger.warning(f"Found invalid partial file, will restart download")
                    existing_size = 0
                    existing_etag = None
            
            # Resolve URLs using Playwright (async operation)
            urls = asyncio.run(self.manager.resolve_song_urls(song_id))
            
            if not urls['audio_url']:
                raise ValueError(f"Could not resolve audio URL for song {song_id}")
            
            # Download audio with resume support
            logger.info(f"Downloading audio: {audio_path.name}")
            audio_final_path, etag, size, was_resumed = self.manager.download_audio_with_resume(
                url=urls['audio_url'],
                output_path=audio_path,
                existing_size=existing_size,
                existing_etag=existing_etag
            )
            
            # Track if this was a resumed download
            if was_resumed:
                result['resumed'] = True
                logger.info(f"Successfully resumed download for {title}")
            
            # Download lyrics if available
            lyrics_final_path = None
            if song.get('lyrics_available') and urls['lyrics_url']:
                logger.info(f"Downloading lyrics: {lyrics_path.name}")
                lyrics_final_path = asyncio.run(
                    self.manager.download_lyrics(
                        song_id=song_id,
                        lyrics_url=urls['lyrics_url'],
                        output_path=lyrics_path
                    )
                )
            
            # Download cover art
            cover_final_path = None
            if urls['cover_url']:
                logger.info(f"Downloading cover art: {cover_path.name}")
                cover_final_path = self.manager.download_cover_art(
                    cover_url=urls['cover_url'],
                    output_path=cover_path
                )
            
            # Get tags and save metadata JSON
            tags = self.manager.get_song_tags(song_id)
            metadata_final_path = self.manager.save_metadata_json(
                song=song,
                output_path=metadata_path,
                tags=tags
            )
            
            # Update database with success
            paths = {
                'local_audio_path': str(audio_final_path),
                'local_lyrics_path': str(lyrics_final_path) if lyrics_final_path else None,
                'local_cover_path': str(cover_final_path) if cover_final_path else None,
                'local_metadata_path': str(metadata_final_path)
            }
            
            self.manager.db.update_download_status(
                song_id=song_id,
                status='completed',
                paths=paths,
                etag=etag,
                size=size
            )
            
            result['status'] = 'completed'
            logger.info(f"Worker {self.worker_id}: Successfully downloaded {title}")
            
            # Update worker status to idle
            if self.manager.progress_tracker:
                self.manager.progress_tracker.update_worker_status(
                    worker_id=self.worker_id,
                    status='idle'
                )
            
        except Exception as e:
            # Log error with full context
            error_context = {
                'song_id': song_id,
                'title': title,
                'worker_id': self.worker_id,
                'error_type': type(e).__name__,
                'error_message': str(e)
            }
            
            logger.error(
                f"Failed to process song {song_id} ({title}): {e}",
                extra=error_context,
                exc_info=True
            )
            
            result['error'] = str(e)
            result['status'] = 'failed'
            
            # Check if we have a partial download to preserve
            if audio_path.exists() and audio_path.stat().st_size > 0:
                partial_size = audio_path.stat().st_size
                logger.info(
                    f"Marking download as partial for future resume "
                    f"({partial_size} bytes downloaded)"
                )
                
                # Try to get ETag from last attempt if available
                partial_etag = song.get('local_audio_etag')
                
                # Build detailed error message for database
                error_detail = f"{type(e).__name__}: {str(e)}"
                
                self.manager.db.mark_download_as_partial(
                    song_id=song_id,
                    partial_path=str(audio_path),
                    etag=partial_etag,
                    size=partial_size
                )
                
                # Also update error field
                self.manager.db.update_download_status(
                    song_id=song_id,
                    status='partial',
                    error=error_detail
                )
            else:
                # No partial data, mark as failed with detailed error
                error_detail = f"{type(e).__name__}: {str(e)}"
                
                self.manager.db.update_download_status(
                    song_id=song_id,
                    status='failed',
                    error=error_detail
                )
            
            # Update worker status to idle
            if self.manager.progress_tracker:
                self.manager.progress_tracker.update_worker_status(
                    worker_id=self.worker_id,
                    status='idle'
                )
        
        return result
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename by removing invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename safe for filesystem
        """
        import re
        
        # Remove invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return sanitized.strip()
