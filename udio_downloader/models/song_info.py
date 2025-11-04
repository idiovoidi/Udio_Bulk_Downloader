"""
Song information data model.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class SongInfo:
    """
    Represents information about a song from Udio platform.
    
    Attributes:
        id: Unique identifier for the song
        title: Display title of the song
        filename: Filename for local storage
        download_url: URL to download the song file
        folder_path: Path to the folder containing this song
        file_size: Size of the song file in bytes (if available)
        created_date: Date when the song was created (if available)
        metadata: Additional metadata about the song
    """
    id: str
    title: str
    filename: str
    download_url: str
    folder_path: str
    file_size: Optional[int] = None
    created_date: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize metadata as empty dict if None."""
        if self.metadata is None:
            self.metadata = {}