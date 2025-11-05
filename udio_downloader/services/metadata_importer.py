"""Metadata importer service for importing JSON exports from Chrome extension."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from .database_manager import DatabaseManager


logger = logging.getLogger(__name__)


class MetadataImporter:
    """Imports metadata from Chrome extension JSON exports."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize metadata importer.
        
        Args:
            db_manager: DatabaseManager instance for database operations
        """
        self.db = db_manager
        self.logger = logger
    
    def import_from_json(self, json_path: str) -> Dict[str, int]:
        """
        Import metadata from JSON file.
        
        Process:
        1. Load and validate JSON
        2. Import folders (with parent relationships)
        3. Import songs (with folder references and hash comparison)
        4. Import tags
        5. Return statistics
        
        Args:
            json_path: Path to JSON export file
            
        Returns:
            Dictionary with statistics: {
                folders_added: int,
                songs_added: int,
                songs_updated: int,
                songs_skipped: int,
                tags_added: int,
                errors: List[str]
            }
        """
        json_path = Path(json_path)
        
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        
        # Load and validate JSON
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {e}")
        
        # Validate export version
        export_version = data.get('exportVersion', '1.0')
        if not export_version.startswith('2.'):
            self.logger.warning(
                f"Expected export version 2.x, got {export_version}. "
                "Import may not work correctly."
            )
        
        self.logger.info(f"Importing metadata from {json_path}")
        self.logger.info(f"Export version: {export_version}")
        self.logger.info(f"Export date: {data.get('exportDate', 'unknown')}")
        
        stats = {
            'folders_added': 0,
            'songs_added': 0,
            'songs_updated': 0,
            'songs_skipped': 0,
            'tags_added': 0,
            'errors': []
        }
        
        # Import folders first (they must exist before songs reference them)
        if 'folders' in data:
            try:
                folders_added = self._import_folders(data['folders'])
                stats['folders_added'] = folders_added
                self.logger.info(f"Imported {folders_added} folders")
            except Exception as e:
                error_msg = f"Failed to import folders: {e}"
                self.logger.error(error_msg, exc_info=True)
                stats['errors'].append(error_msg)
        
        # Import songs with hash-based update detection
        if 'songs' in data:
            try:
                added, updated, skipped = self._import_songs(data['songs'])
                stats['songs_added'] = added
                stats['songs_updated'] = updated
                stats['songs_skipped'] = skipped
                self.logger.info(
                    f"Imported songs: {added} added, {updated} updated, {skipped} skipped"
                )
            except Exception as e:
                error_msg = f"Failed to import songs: {e}"
                self.logger.error(error_msg, exc_info=True)
                stats['errors'].append(error_msg)
        
        # Import tags
        if 'tags' in data:
            try:
                tags_added = self._import_tags(data['tags'])
                stats['tags_added'] = tags_added
                self.logger.info(f"Imported {tags_added} tags")
            except Exception as e:
                error_msg = f"Failed to import tags: {e}"
                self.logger.error(error_msg, exc_info=True)
                stats['errors'].append(error_msg)
        
        return stats
    
    def _import_folders(self, folders: List[dict]) -> int:
        """
        Import folders with parent relationships.
        
        Folders are imported in order, ensuring parent folders exist before children.
        Uses stable IDs from the extension export.
        
        Args:
            folders: List of folder dictionaries from JSON export
            
        Returns:
            Number of folders added
        """
        if not folders:
            return 0
        
        added = 0
        
        # Sort folders by path depth to ensure parents are created first
        sorted_folders = sorted(
            folders,
            key=lambda f: len(f.get('path', [])) if isinstance(f.get('path'), list) else 0
        )
        
        for folder in sorted_folders:
            try:
                # Validate required fields
                if 'id' not in folder or 'name' not in folder:
                    self.logger.warning(f"Skipping folder with missing id or name: {folder}")
                    continue
                
                # Convert path to JSON string if it's a list
                path = folder.get('path', [])
                if isinstance(path, list):
                    path = json.dumps(path)
                
                # Use database manager's import method
                # Note: We'll use the existing import_metadata method which handles this
                
            except Exception as e:
                self.logger.error(f"Failed to import folder {folder.get('id')}: {e}")
        
        # Use the database manager's built-in import for folders
        # This is already implemented in DatabaseManager._import_folders_sync
        added = self.db._import_folders_sync(folders)
        
        return added
    
    def _import_songs(self, songs: List[dict]) -> Tuple[int, int, int]:
        """
        Import songs with metadata hash comparison for updates.
        
        For each song:
        - If song doesn't exist: insert as new
        - If song exists but hash differs: update metadata
        - If song exists with same hash: skip
        
        Args:
            songs: List of song dictionaries from JSON export
            
        Returns:
            Tuple of (added, updated, skipped) counts
        """
        if not songs:
            return 0, 0, 0
        
        # Use the database manager's built-in import for songs
        # This already implements hash-based update detection
        added, updated, skipped = self.db._import_songs_sync(songs)
        
        return added, updated, skipped
    
    def _import_tags(self, tags: List[dict]) -> int:
        """
        Import tag relationships.
        
        Tags link songs to genre/style tags. Each tag entry has:
        - song_id: Reference to song
        - tag: Tag name/value
        
        Args:
            tags: List of tag dictionaries from JSON export
            
        Returns:
            Number of tags added
        """
        if not tags:
            return 0
        
        # Use the database manager's built-in import for tags
        added = self.db._import_tags_sync(tags)
        
        return added
    
    def _should_update_song(self, existing: dict, new: dict) -> bool:
        """
        Determine if song metadata should be updated.
        
        Updates are needed when:
        - Metadata hash has changed
        - New data has fields that existing data lacks
        
        Args:
            existing: Existing song data from database
            new: New song data from JSON export
            
        Returns:
            True if song should be updated
        """
        # Primary check: hash comparison
        existing_hash = existing.get('metadata_hash')
        new_hash = new.get('metadataHash')
        
        if existing_hash != new_hash:
            return True
        
        # Secondary check: new fields available
        # This handles cases where the export format has been enhanced
        important_fields = [
            'artist', 'duration', 'createdDate', 'playCount',
            'likesCount', 'lyricsAvailable'
        ]
        
        for field in important_fields:
            # Map JSON field names to database field names
            db_field = self._map_field_name(field)
            if new.get(field) and not existing.get(db_field):
                return True
        
        return False
    
    def _map_field_name(self, json_field: str) -> str:
        """
        Map JSON field names to database field names.
        
        Args:
            json_field: Field name from JSON export (camelCase)
            
        Returns:
            Database field name (snake_case)
        """
        field_mapping = {
            'folderId': 'folder_id',
            'duration': 'duration_seconds',
            'createdDate': 'created_date',
            'isLiked': 'is_liked',
            'isDisliked': 'is_disliked',
            'playCount': 'play_count',
            'likesCount': 'likes_count',
            'lyricsAvailable': 'lyrics_available',
            'metadataHash': 'metadata_hash',
            'metadataCollectedAt': 'metadata_collected_at'
        }
        
        return field_mapping.get(json_field, json_field)
