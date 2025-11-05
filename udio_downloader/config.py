"""Configuration management for Udio Downloader."""

import os
from pathlib import Path
from typing import Optional


class Config:
    """
    Configuration settings for Udio Downloader.
    
    This class manages configuration values with support for:
    - Environment variables
    - Default values
    - User-specific paths
    """
    
    # Default paths
    DEFAULT_OUTPUT_DIR = Path('./downloads')
    DEFAULT_DB_NAME = 'metadata.db'
    DEFAULT_USER_DATA_DIR = Path.home() / '.udio_downloader' / 'browser_profile'
    
    # Download settings
    DEFAULT_CONCURRENT_WORKERS = 3
    DEFAULT_RATE_LIMIT_DELAY = 1.0  # seconds
    DEFAULT_MAX_RETRIES = 3
    
    # Playwright settings
    DEFAULT_HEADLESS = False
    DEFAULT_TIMEOUT = 30000  # milliseconds
    
    def __init__(self):
        """Initialize configuration with defaults and environment overrides."""
        # Paths
        self.output_dir = Path(
            os.getenv('UDIO_OUTPUT_DIR', self.DEFAULT_OUTPUT_DIR)
        )
        self.db_path = self.output_dir / self.DEFAULT_DB_NAME
        self.user_data_dir = Path(
            os.getenv('UDIO_USER_DATA_DIR', self.DEFAULT_USER_DATA_DIR)
        )
        
        # Download settings
        self.concurrent_workers = int(
            os.getenv('UDIO_CONCURRENT_WORKERS', self.DEFAULT_CONCURRENT_WORKERS)
        )
        self.rate_limit_delay = float(
            os.getenv('UDIO_RATE_LIMIT_DELAY', self.DEFAULT_RATE_LIMIT_DELAY)
        )
        self.max_retries = int(
            os.getenv('UDIO_MAX_RETRIES', self.DEFAULT_MAX_RETRIES)
        )
        
        # Playwright settings
        self.headless = os.getenv('UDIO_HEADLESS', str(self.DEFAULT_HEADLESS)).lower() == 'true'
        self.timeout = int(
            os.getenv('UDIO_TIMEOUT', self.DEFAULT_TIMEOUT)
        )
        
        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
    
    def get_db_path(self, custom_path: Optional[str] = None) -> Path:
        """
        Get database path with optional custom override.
        
        Args:
            custom_path: Optional custom database path
            
        Returns:
            Path to database file
        """
        if custom_path:
            return Path(custom_path)
        return self.db_path
    
    def get_user_data_dir(self, custom_path: Optional[str] = None) -> Path:
        """
        Get user data directory with optional custom override.
        
        Args:
            custom_path: Optional custom user data directory
            
        Returns:
            Path to user data directory
        """
        if custom_path:
            return Path(custom_path)
        return self.user_data_dir
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return (
            f"Config(\n"
            f"  output_dir={self.output_dir},\n"
            f"  db_path={self.db_path},\n"
            f"  user_data_dir={self.user_data_dir},\n"
            f"  concurrent_workers={self.concurrent_workers},\n"
            f"  rate_limit_delay={self.rate_limit_delay},\n"
            f"  max_retries={self.max_retries},\n"
            f"  headless={self.headless},\n"
            f"  timeout={self.timeout}\n"
            f")"
        )


# Global configuration instance
config = Config()
