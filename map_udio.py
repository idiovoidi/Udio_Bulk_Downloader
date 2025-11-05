"""
Udio library folder mapper.

Usage:
1. Start Chrome with: chrome.exe --remote-debugging-port=9222 --user-data-dir="C:/path/to/profile"
2. Navigate to Udio library page and open the folder tree panel
3. Run: python map_udio.py
"""

from scraper.core import BrowserConnection
from scraper.platforms.udio import UdioFolderMapper
from scraper.utils import OutputFormatter, get_logger, PathManager


def main():
    """Map Udio library structure"""
    # Setup paths and logging
    paths = PathManager(base_dir='output', platform='udio')
    logger = get_logger('udio_mapper', log_dir=str(paths.get_log_dir()))
    
    # Print directory structure
    paths.print_summary()
    
    browser = BrowserConnection(debug_port=9222)
    
    try:
        # Connect to Chrome
        logger.info("Starting Udio library mapping")
        driver = browser.connect()
        
        # Create mapper
        mapper = UdioFolderMapper(driver, logger=logger)
        
        # Map folder structure
        structure = mapper.map_structure()
        
        # Print tree view
        OutputFormatter.print_tree(structure)
        
        # Print summary
        OutputFormatter.print_summary(structure)
        
        # Save to file with timestamp
        export_path = paths.get_export_path('library_structure.json', timestamped=True)
        OutputFormatter.save_json(structure, export_path)
        
        logger.success(f"Mapping completed successfully")
        
        # Clean old exports (keep last 5)
        paths.clean_old_exports(keep_count=5, pattern='library_structure_*.json')
        
    except Exception as e:
        logger.error(f"Mapping failed: {e}")
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()
        logger.info("Browser connection closed")


if __name__ == '__main__':
    main()
