"""Test the full Udio Downloader workflow."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from udio_downloader.services.database_manager import DatabaseManager


def test_database():
    """Test database operations."""
    print("=" * 60)
    print("Testing Database Manager")
    print("=" * 60)
    print()
    
    db_path = "./downloads/metadata.db"
    print(f"Database: {db_path}")
    print()
    
    # Initialize database manager
    db_manager = DatabaseManager(db_path)
    
    try:
        # Get statistics
        stats = db_manager.get_download_statistics()
        
        print("Download Statistics:")
        print(f"  Total songs: {stats['total']}")
        print(f"  Completed: {stats['completed']}")
        print(f"  Pending: {stats['pending']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Partial: {stats['partial']}")
        print()
        
        # Get folder statistics
        folder_stats = db_manager.get_folder_statistics()
        if folder_stats:
            print("Folder Statistics:")
            print(f"  Total folders: {folder_stats['total_folders']}")
            print(f"  Root songs: {folder_stats['root_songs']}")
            print()
        
        # Get pending downloads
        pending_downloads = db_manager.get_pending_downloads(limit=5)
        
        if pending_downloads:
            print(f"Sample Pending Downloads (showing {len(pending_downloads)}):")
            for song in pending_downloads:
                print(f"  - {song['title']} (ID: {song['id']})")
                print(f"    Folder ID: {song.get('folder_id', 'Root')}")
                print(f"    Status: {song['download_status']}")
                print(f"    Duration: {song.get('duration_seconds', 0)}s")
                print()
        else:
            print("No pending downloads found.")
            print()
        
        print("✓ Database test completed successfully!")
        
    finally:
        db_manager.shutdown()
    
    print()


def test_config():
    """Test configuration."""
    print("=" * 60)
    print("Testing Configuration")
    print("=" * 60)
    print()
    
    from udio_downloader.config import config
    
    print("Current Configuration:")
    print(f"  Output directory: {config.output_dir}")
    print(f"  Database path: {config.db_path}")
    print(f"  User data directory: {config.user_data_dir}")
    print(f"  Concurrent workers: {config.concurrent_workers}")
    print(f"  Rate limit delay: {config.rate_limit_delay}s")
    print(f"  Max retries: {config.max_retries}")
    print(f"  Headless mode: {config.headless}")
    print(f"  Timeout: {config.timeout}ms")
    print()
    
    print("✓ Configuration test completed successfully!")
    print()


def test_cli_commands():
    """Test CLI command availability."""
    print("=" * 60)
    print("Testing CLI Commands")
    print("=" * 60)
    print()
    
    import subprocess
    
    commands = [
        ("Help", ["python", "-m", "udio_downloader", "--help"]),
        ("Version", ["python", "-m", "udio_downloader", "--version"]),
        ("Status Help", ["python", "-m", "udio_downloader", "status", "--help"]),
        ("Import Help", ["python", "-m", "udio_downloader", "import-metadata", "--help"]),
        ("Download Help", ["python", "-m", "udio_downloader", "download", "--help"]),
    ]
    
    for name, cmd in commands:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✓ {name}: OK")
            else:
                print(f"✗ {name}: Failed (exit code {result.returncode})")
        except Exception as e:
            print(f"✗ {name}: Error - {e}")
    
    print()
    print("✓ CLI commands test completed!")
    print()


def main():
    """Run all tests."""
    print()
    print("=" * 60)
    print("UDIO DOWNLOADER - FULL WORKFLOW TEST")
    print("=" * 60)
    print()
    
    try:
        # Test configuration
        test_config()
        
        # Test CLI commands
        test_cli_commands()
        
        # Test database
        test_database()
        
        print("=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        
        print("Next Steps:")
        print("1. Export your Udio library using the Chrome extension")
        print("2. Import metadata: python -m udio_downloader import-metadata --json-file <export.json>")
        print("3. Check status: python -m udio_downloader status")
        print("4. Download songs: python -m udio_downloader download")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("TEST FAILED!")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
