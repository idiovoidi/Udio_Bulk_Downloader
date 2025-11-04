"""
Folder node data model for representing hierarchical folder structure.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from .song_info import SongInfo


@dataclass
class FolderNode:
    """
    Represents a folder node in the hierarchical folder structure.
    
    Attributes:
        id: Unique identifier for the folder
        name: Display name of the folder
        path: Full path to the folder
        parent_id: ID of the parent folder (None for root)
        children: List of child folder nodes
        songs: List of songs contained in this folder
        song_count: Total number of songs in this folder and subfolders
    """
    id: str
    name: str
    path: str
    parent_id: Optional[str] = None
    children: List['FolderNode'] = field(default_factory=list)
    songs: List[SongInfo] = field(default_factory=list)
    song_count: int = 0
    
    def add_child(self, child: 'FolderNode') -> None:
        """Add a child folder node."""
        child.parent_id = self.id
        self.children.append(child)
    
    def add_song(self, song: SongInfo) -> None:
        """Add a song to this folder."""
        self.songs.append(song)
        self.song_count += 1
    
    def get_total_song_count(self) -> int:
        """Get total song count including all subfolders."""
        total = len(self.songs)
        for child in self.children:
            total += child.get_total_song_count()
        return total