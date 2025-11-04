"""
Download configuration data model.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class DownloadConfig:
    """
    Configuration settings for the download process.
    
    Attributes:
        output_directory: Directory where downloaded files will be stored
        max_concurrent_downloads: Maximum number of simultaneous downloads
        retry_attempts: Number of retry attempts for failed downloads
        timeout_seconds: Timeout for download requests in seconds
        preserve_metadata: Whether to preserve song metadata
        create_folder_structure: Whether to recreate folder structure locally
    """
    output_directory: str
    max_concurrent_downloads: int = 3
    retry_attempts: int = 3
    timeout_seconds: int = 30
    preserve_metadata: bool = True
    create_folder_structure: bool = True
    
    def __post_init__(self):
        """Validate configuration values."""
        if self.max_concurrent_downloads < 1:
            raise ValueError("max_concurrent_downloads must be at least 1")
        
        if self.retry_attempts < 0:
            raise ValueError("retry_attempts must be non-negative")
        
        if self.timeout_seconds < 1:
            raise ValueError("timeout_seconds must be at least 1")
        
        # Ensure output directory path is absolute
        self.output_directory = str(Path(self.output_directory).resolve())
    
    @property
    def output_path(self) -> Path:
        """Get output directory as Path object."""
        return Path(self.output_directory)