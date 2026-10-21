"""
Centralized path management for outputs and logs.
"""

from pathlib import Path
from datetime import datetime


class PathManager:
    """Manage output directories and file paths"""
    
    def __init__(self, base_dir='output', platform=None):
        self.base_dir = Path(base_dir)
        self.platform = platform
        
        # Create directory structure
        self.logs_dir = Path('logs')
        self.exports_dir = self.base_dir / 'exports'
        self.downloads_dir = self.base_dir / 'downloads'
        self.metadata_dir = self.base_dir / 'metadata'
        
        # Platform-specific subdirectories
        if platform:
            self.exports_dir = self.exports_dir / platform
            self.downloads_dir = self.downloads_dir / platform
            self.metadata_dir = self.metadata_dir / platform
        
        # Create all directories
        self._create_directories()
    
    def _create_directories(self):
        """Create all necessary directories"""
        for directory in [self.logs_dir, self.exports_dir, self.downloads_dir, self.metadata_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_export_path(self, filename, timestamped=False):
        """Get path for export file"""
        if timestamped:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = f"{name}_{timestamp}.{ext}" if ext else f"{name}_{timestamp}"
        
        return self.exports_dir / filename
    
    def get_download_path(self, *parts):
        """Get path for downloaded file"""
        return self.downloads_dir.joinpath(*parts)
    
    def get_metadata_path(self, filename):
        """Get path for metadata file"""
        return self.metadata_dir / filename
    
    def get_log_dir(self):
        """Get logs directory"""
        return self.logs_dir
    
    def list_exports(self, pattern='*'):
        """List all export files"""
        return list(self.exports_dir.glob(pattern))
    
    def list_downloads(self, pattern='*'):
        """List all downloaded files"""
        return list(self.downloads_dir.glob(pattern))
    
    def get_latest_export(self, pattern='*.json'):
        """Get most recent export file"""
        exports = self.list_exports(pattern)
        if not exports:
            return None
        return max(exports, key=lambda p: p.stat().st_mtime)
    
    def clean_old_exports(self, keep_count=5, pattern='*.json'):
        """Keep only the N most recent export files"""
        exports = sorted(
            self.list_exports(pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        for old_export in exports[keep_count:]:
            old_export.unlink()
            print(f"Deleted old export: {old_export.name}")
    
    def get_summary(self):
        """Get summary of all directories"""
        return {
            'base_dir': str(self.base_dir),
            'platform': self.platform,
            'logs': str(self.logs_dir),
            'exports': str(self.exports_dir),
            'downloads': str(self.downloads_dir),
            'metadata': str(self.metadata_dir),
            'export_count': len(self.list_exports()),
            'download_count': len(self.list_downloads())
        }
    
    def print_summary(self):
        """Print directory structure summary"""
        summary = self.get_summary()
        print("\n" + "="*60)
        print("OUTPUT DIRECTORY STRUCTURE")
        print("="*60)
        print(f"Platform: {summary['platform'] or 'Generic'}")
        print(f"Logs: {summary['logs']}")
        print(f"Exports: {summary['exports']} ({summary['export_count']} files)")
        print(f"Downloads: {summary['downloads']} ({summary['download_count']} files)")
        print(f"Metadata: {summary['metadata']}")
        print("="*60)
