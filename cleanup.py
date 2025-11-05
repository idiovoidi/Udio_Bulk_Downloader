"""
Workspace Cleanup Script

Removes old/obsolete files and organizes the workspace.
"""

import os
import shutil
from pathlib import Path

# Files to keep
KEEP_FILES = {
    # Core application
    'requirements.txt',
    'setup.py',
    '.gitignore',
    
    # Working scrapers
    'scrape_udio_final.py',
    'simple_logger.py',
    
    # Data files
    'action_log.json',
    'udio_library_export.json',
    
    # This cleanup script
    'cleanup.py',
    'README.md',  # Will create
}

# Directories to keep
KEEP_DIRS = {
    '.git',
    '.venv',
    '.vscode',
    '.kiro',
    'udio_downloader',
    'chrome_extension',
    'downloads',
}

# Files to remove
REMOVE_FILES = [
    'action_logger.py',  # Replaced by simple_logger.py
    'scrape_udio_complete.py',  # Old version
    'scrape_udio_library.py',  # Old version
    'scrape_udio_main.py',  # Old version
    'scrape_udio_simple.py',  # Old version
    'scrape_udio_tree.py',  # Old version
    'inspect_udio_page.js',  # Not needed
    'login_helper.py',  # Not needed
    'run_tests.py',  # Old tests
    'test_full_workflow.py',  # Old tests
    'test_metadata.json',  # Test data
    'test_playwright.py',  # Old tests
    'verify_installation.py',  # Not needed
    'view_action_log.py',  # Not needed
    'SUMMARY.md',  # Old doc
    'TEST_README.md',  # Old doc
    'TEST.txt',  # Test file
    'udio_page_dump.html',  # Debug file
]

# Directories to remove
REMOVE_DIRS = [
    '.docs',
    'docs',
    'ui_analysis',
    '.chrome-debug-profile',
]


def cleanup():
    """Perform cleanup."""
    print("=" * 60)
    print("WORKSPACE CLEANUP")
    print("=" * 60)
    print()
    
    removed_files = []
    removed_dirs = []
    errors = []
    
    # Remove files
    print("Removing obsolete files...")
    for filename in REMOVE_FILES:
        filepath = Path(filename)
        if filepath.exists():
            try:
                filepath.unlink()
                removed_files.append(filename)
                print(f"  ✓ Removed: {filename}")
            except Exception as e:
                errors.append(f"Could not remove {filename}: {e}")
                print(f"  ✗ Error: {filename}")
    
    print()
    
    # Remove directories
    print("Removing obsolete directories...")
    for dirname in REMOVE_DIRS:
        dirpath = Path(dirname)
        if dirpath.exists():
            try:
                shutil.rmtree(dirpath)
                removed_dirs.append(dirname)
                print(f"  ✓ Removed: {dirname}/")
            except Exception as e:
                errors.append(f"Could not remove {dirname}: {e}")
                print(f"  ✗ Error: {dirname}/")
    
    print()
    print("=" * 60)
    print("CLEANUP SUMMARY")
    print("=" * 60)
    print()
    print(f"Files removed: {len(removed_files)}")
    print(f"Directories removed: {len(removed_dirs)}")
    
    if errors:
        print()
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
    
    print()
    print("✅ Cleanup complete!")
    print()
    print("Remaining structure:")
    print("  scrape_udio_final.py  - Main scraper")
    print("  simple_logger.py      - Action logger")
    print("  udio_downloader/      - Download manager")
    print("  chrome_extension/     - Browser extension")
    print("  downloads/            - Downloaded songs")
    print()


if __name__ == "__main__":
    response = input("This will remove old files. Continue? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        cleanup()
    else:
        print("Cleanup cancelled.")
