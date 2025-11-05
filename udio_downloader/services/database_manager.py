"""Database manager with thread-safe write operations."""

import sqlite3
import threading
import queue
import logging
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Callable
from datetime import datetime


logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations with single-writer thread safety."""
    
    def __init__(self, db_path: str):
        """
        Initialize database manager with single-writer thread pattern.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.write_queue: queue.Queue = queue.Queue()
        self.writer_thread: Optional[threading.Thread] = None
        self._shutdown = threading.Event()
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self.initialize_database()
        
        # Start writer thread
        self._start_writer_thread()
    
    def _start_writer_thread(self):
        """Start single writer thread for thread-safe DB operations."""
        self.writer_thread = threading.Thread(
            target=self._writer_loop,
            daemon=True,
            name="DatabaseWriter"
        )
        self.writer_thread.start()
        logger.info("Database writer thread started")
    
    def _writer_loop(self):
        """Process write operations from queue with single connection."""
        conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            timeout=30.0
        )
        conn.row_factory = sqlite3.Row
        
        try:
            while not self._shutdown.is_set():
                try:
                    # Get operation from queue with timeout
                    operation = self.write_queue.get(timeout=0.5)
                    
                    if operation is None:  # Poison pill
                        break
                    
                    try:
                        operation(conn)
                        conn.commit()
                    except Exception as e:
                        conn.rollback()
                        logger.error(f"DB write failed: {e}", exc_info=True)
                    finally:
                        self.write_queue.task_done()
                        
                except queue.Empty:
                    continue
                    
        finally:
            conn.close()
            logger.info("Database writer thread stopped")
    
    def _execute_write(self, operation: Callable[[sqlite3.Connection], None]):
        """
        Queue a write operation for execution by writer thread.
        
        Args:
            operation: Callable that takes a connection and performs write operations
        """
        self.write_queue.put(operation)
    
    def _get_read_connection(self) -> sqlite3.Connection:
        """Get a new connection for read operations."""
        conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            timeout=30.0
        )
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize_database(self) -> None:
        """Create tables and indexes if they don't exist."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # Folders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS folders (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    parent_id TEXT,
                    path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES folders(id)
                )
            """)
            
            # Songs table with numeric fields and resume metadata
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS songs (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    artist TEXT,
                    folder_id TEXT,
                    duration_seconds INTEGER,
                    created_date TEXT,
                    is_liked BOOLEAN DEFAULT 0,
                    is_disliked BOOLEAN DEFAULT 0,
                    play_count INTEGER DEFAULT 0,
                    likes_count INTEGER DEFAULT 0,
                    lyrics_available BOOLEAN DEFAULT 0,
                    metadata_hash TEXT,
                    metadata_collected_at TIMESTAMP,
                    download_status TEXT DEFAULT 'pending',
                    download_error TEXT,
                    downloaded_at TIMESTAMP,
                    local_audio_path TEXT,
                    local_audio_size INTEGER,
                    local_audio_etag TEXT,
                    local_lyrics_path TEXT,
                    local_cover_path TEXT,
                    local_metadata_path TEXT,
                    FOREIGN KEY (folder_id) REFERENCES folders(id)
                )
            """)
            
            # Tags table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    song_id TEXT NOT NULL,
                    tag TEXT NOT NULL,
                    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE,
                    UNIQUE(song_id, tag)
                )
            """)
            
            # Lyrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lyrics (
                    song_id TEXT PRIMARY KEY,
                    lyrics_text TEXT,
                    downloaded_at TIMESTAMP,
                    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
                )
            """)
            
            # Metadata tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    songs_processed INTEGER DEFAULT 0,
                    songs_added INTEGER DEFAULT 0,
                    songs_updated INTEGER DEFAULT 0,
                    songs_failed INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'in_progress'
                )
            """)
            
            # Create indexes for performance optimization
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_folders_parent 
                ON folders(parent_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_folders_path 
                ON folders(path)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_songs_folder 
                ON songs(folder_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_songs_status 
                ON songs(download_status)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_songs_hash 
                ON songs(metadata_hash)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tags_song 
                ON tags(song_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tags_tag 
                ON tags(tag)
            """)
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
            
        finally:
            conn.close()
    
    def import_metadata(self, json_data: dict) -> dict:
        """
        Import metadata from JSON export (uses write queue).
        
        Args:
            json_data: Parsed JSON data from extension export
            
        Returns:
            Dictionary with statistics: {added, updated, skipped, failed}
        """
        stats = {
            'folders_added': 0,
            'songs_added': 0,
            'songs_updated': 0,
            'songs_skipped': 0,
            'tags_added': 0,
            'failed': 0
        }
        
        # Import folders first
        if 'folders' in json_data:
            stats['folders_added'] = self._import_folders_sync(json_data['folders'])
        
        # Import songs
        if 'songs' in json_data:
            added, updated, skipped = self._import_songs_sync(json_data['songs'])
            stats['songs_added'] = added
            stats['songs_updated'] = updated
            stats['songs_skipped'] = skipped
        
        # Import tags
        if 'tags' in json_data:
            stats['tags_added'] = self._import_tags_sync(json_data['tags'])
        
        return stats
    
    def _import_folders_sync(self, folders: List[dict]) -> int:
        """Import folders synchronously."""
        conn = self._get_read_connection()
        cursor = conn.cursor()
        added = 0
        
        try:
            for folder in folders:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO folders (id, name, parent_id, path)
                        VALUES (?, ?, ?, ?)
                    """, (
                        folder['id'],
                        folder['name'],
                        folder.get('parent_id'),
                        folder['path'] if isinstance(folder['path'], str) else str(folder['path'])
                    ))
                    if cursor.rowcount > 0:
                        added += 1
                except Exception as e:
                    logger.error(f"Failed to import folder {folder.get('id')}: {e}")
            
            conn.commit()
            
        finally:
            conn.close()
        
        return added
    
    def _import_songs_sync(self, songs: List[dict]) -> Tuple[int, int, int]:
        """Import songs synchronously. Returns (added, updated, skipped)."""
        conn = self._get_read_connection()
        cursor = conn.cursor()
        added = 0
        updated = 0
        skipped = 0
        
        try:
            for song in songs:
                try:
                    # Check if song exists
                    cursor.execute("SELECT metadata_hash FROM songs WHERE id = ?", (song['id'],))
                    existing = cursor.fetchone()
                    
                    if existing is None:
                        # Insert new song
                        cursor.execute("""
                            INSERT INTO songs (
                                id, title, artist, folder_id, duration_seconds,
                                created_date, is_liked, is_disliked, play_count,
                                likes_count, lyrics_available, metadata_hash,
                                metadata_collected_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            song['id'],
                            song['title'],
                            song.get('artist'),
                            song.get('folderId'),
                            song.get('duration'),
                            song.get('createdDate'),
                            song.get('isLiked', False),
                            song.get('isDisliked', False),
                            song.get('playCount', 0),
                            song.get('likesCount', 0),
                            song.get('lyricsAvailable', False),
                            song.get('metadataHash'),
                            song.get('metadataCollectedAt')
                        ))
                        added += 1
                        
                    elif existing['metadata_hash'] != song.get('metadataHash'):
                        # Update existing song if hash changed
                        cursor.execute("""
                            UPDATE songs SET
                                title = ?, artist = ?, folder_id = ?,
                                duration_seconds = ?, created_date = ?,
                                is_liked = ?, is_disliked = ?, play_count = ?,
                                likes_count = ?, lyrics_available = ?,
                                metadata_hash = ?, metadata_collected_at = ?
                            WHERE id = ?
                        """, (
                            song['title'],
                            song.get('artist'),
                            song.get('folderId'),
                            song.get('duration'),
                            song.get('createdDate'),
                            song.get('isLiked', False),
                            song.get('isDisliked', False),
                            song.get('playCount', 0),
                            song.get('likesCount', 0),
                            song.get('lyricsAvailable', False),
                            song.get('metadataHash'),
                            song.get('metadataCollectedAt'),
                            song['id']
                        ))
                        updated += 1
                    else:
                        skipped += 1
                        
                except Exception as e:
                    logger.error(f"Failed to import song {song.get('id')}: {e}")
            
            conn.commit()
            
        finally:
            conn.close()
        
        return added, updated, skipped
    
    def _import_tags_sync(self, tags: List[dict]) -> int:
        """Import tags synchronously."""
        conn = self._get_read_connection()
        cursor = conn.cursor()
        added = 0
        
        try:
            for tag_entry in tags:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO tags (song_id, tag)
                        VALUES (?, ?)
                    """, (tag_entry['song_id'], tag_entry['tag']))
                    if cursor.rowcount > 0:
                        added += 1
                except Exception as e:
                    logger.error(f"Failed to import tag: {e}")
            
            conn.commit()
            
        finally:
            conn.close()
        
        return added
    
    def get_pending_downloads(self, limit: Optional[int] = None) -> List[dict]:
        """
        Get songs with download_status in ('pending', 'failed', 'partial').
        
        Args:
            limit: Optional limit on number of results
            
        Returns:
            List of song dictionaries
        """
        conn = self._get_read_connection()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT * FROM songs 
                WHERE download_status IN ('pending', 'failed', 'partial')
                ORDER BY created_date DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        finally:
            conn.close()
    
    def update_download_status(
        self,
        song_id: str,
        status: str,
        error: Optional[str] = None,
        paths: Optional[dict] = None,
        etag: Optional[str] = None,
        size: Optional[int] = None
    ) -> None:
        """
        Update song download status, file paths, and resume metadata (queued write).
        
        Args:
            song_id: Song ID to update
            status: New download status (pending, downloading, completed, failed, partial)
            error: Optional error message
            paths: Optional dict with local_audio_path, local_lyrics_path, etc.
            etag: Optional ETag for resume validation
            size: Optional file size for resume validation
        """
        def operation(conn: sqlite3.Connection):
            cursor = conn.cursor()
            
            update_fields = ["download_status = ?"]
            params = [status]
            
            if error is not None:
                update_fields.append("download_error = ?")
                params.append(error)
            
            if paths:
                if 'local_audio_path' in paths:
                    update_fields.append("local_audio_path = ?")
                    params.append(paths['local_audio_path'])
                if 'local_lyrics_path' in paths:
                    update_fields.append("local_lyrics_path = ?")
                    params.append(paths['local_lyrics_path'])
                if 'local_cover_path' in paths:
                    update_fields.append("local_cover_path = ?")
                    params.append(paths['local_cover_path'])
                if 'local_metadata_path' in paths:
                    update_fields.append("local_metadata_path = ?")
                    params.append(paths['local_metadata_path'])
            
            if etag is not None:
                update_fields.append("local_audio_etag = ?")
                params.append(etag)
            
            if size is not None:
                update_fields.append("local_audio_size = ?")
                params.append(size)
            
            if status == 'completed':
                update_fields.append("downloaded_at = ?")
                params.append(datetime.now().isoformat())
            
            params.append(song_id)
            
            query = f"UPDATE songs SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, params)
        
        self._execute_write(operation)
    
    def mark_download_as_partial(
        self,
        song_id: str,
        partial_path: str,
        etag: Optional[str],
        size: int
    ) -> None:
        """
        Mark a download as partial for future resume.
        
        Args:
            song_id: Song ID
            partial_path: Path to partial file
            etag: ETag for validation
            size: Current file size
        """
        def operation(conn: sqlite3.Connection):
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE songs 
                SET download_status = 'partial',
                    local_audio_path = ?,
                    local_audio_etag = ?,
                    local_audio_size = ?
                WHERE id = ?
            """, (partial_path, etag, size, song_id))
        
        self._execute_write(operation)
    
    def get_download_statistics(self) -> dict:
        """
        Get download progress statistics.
        
        Returns:
            Dictionary with total, completed, pending, failed, partial counts
        """
        conn = self._get_read_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN download_status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN download_status = 'pending' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN download_status = 'failed' THEN 1 ELSE 0 END) as failed,
                    SUM(CASE WHEN download_status = 'partial' THEN 1 ELSE 0 END) as partial
                FROM songs
            """)
            
            row = cursor.fetchone()
            
            return {
                'total': row['total'] or 0,
                'completed': row['completed'] or 0,
                'pending': row['pending'] or 0,
                'failed': row['failed'] or 0,
                'partial': row['partial'] or 0
            }
            
        finally:
            conn.close()
    
    def mark_song_as_processed(self, song_id: str, metadata_hash: str) -> None:
        """
        Mark song as cataloged with hash (for incremental updates).
        
        Args:
            song_id: Song ID
            metadata_hash: Hash of metadata for change detection
        """
        def operation(conn: sqlite3.Connection):
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE songs 
                SET metadata_hash = ?, metadata_collected_at = ?
                WHERE id = ?
            """, (metadata_hash, datetime.now().isoformat(), song_id))
        
        self._execute_write(operation)
    
    def get_songs_needing_update(self, current_hashes: dict) -> List[str]:
        """
        Get song IDs where metadata_hash differs from current.
        
        Args:
            current_hashes: Dict mapping song_id to current metadata_hash
            
        Returns:
            List of song IDs that need updating
        """
        conn = self._get_read_connection()
        cursor = conn.cursor()
        
        try:
            song_ids = list(current_hashes.keys())
            placeholders = ','.join('?' * len(song_ids))
            
            cursor.execute(f"""
                SELECT id, metadata_hash FROM songs
                WHERE id IN ({placeholders})
            """, song_ids)
            
            rows = cursor.fetchall()
            
            needs_update = []
            for row in rows:
                if row['metadata_hash'] != current_hashes.get(row['id']):
                    needs_update.append(row['id'])
            
            return needs_update
            
        finally:
            conn.close()
    
    def get_folder_statistics(self) -> Optional[dict]:
        """
        Get folder structure statistics.
        
        Returns:
            Dictionary with folder statistics or None if no data
        """
        conn = self._get_read_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_folders
                FROM folders
            """)
            folder_row = cursor.fetchone()
            
            cursor.execute("""
                SELECT COUNT(*) as root_songs
                FROM songs
                WHERE folder_id IS NULL
            """)
            songs_row = cursor.fetchone()
            
            if folder_row['total_folders'] == 0 and songs_row['root_songs'] == 0:
                return None
            
            return {
                'total_folders': folder_row['total_folders'] or 0,
                'root_songs': songs_row['root_songs'] or 0
            }
            
        finally:
            conn.close()
    
    def get_last_metadata_run(self) -> Optional[dict]:
        """
        Get information about the last metadata import run.
        
        Returns:
            Dictionary with last run information or None if no runs
        """
        conn = self._get_read_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    run_date,
                    songs_processed,
                    songs_added,
                    songs_updated,
                    songs_failed,
                    status
                FROM metadata_runs
                ORDER BY run_date DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return dict(row)
            
        finally:
            conn.close()
    
    def shutdown(self):
        """Gracefully shutdown the database manager."""
        logger.info("Shutting down database manager...")
        self._shutdown.set()
        
        # Send poison pill to writer thread
        self.write_queue.put(None)
        
        # Wait for writer thread to finish
        if self.writer_thread and self.writer_thread.is_alive():
            self.writer_thread.join(timeout=5.0)
        
        logger.info("Database manager shutdown complete")
