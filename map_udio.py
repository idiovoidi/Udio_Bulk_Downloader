"""
Udio library folder mapper.

Usage:
Run: python map_udio.py

The script will launch Chrome with your saved profile.
If not logged in, log in to Udio and navigate to your library.
"""

import asyncio
from scraper.core import BrowserConnection
from scraper.platforms.udio.mapper_async import UdioFolderMapper
from scraper.utils import OutputFormatter, get_logger, PathManager


async def main():
    """Map Udio library structure"""
    # Setup paths and logging
    paths = PathManager(base_dir='output', platform='udio')
    logger = get_logger('udio_mapper', log_dir=str(paths.get_log_dir()))
    
    # Print directory structure
    paths.print_summary()
    
    browser = BrowserConnection()
    
    try:
        # Launch Chrome
        logger.info("Starting Udio library mapping")
        context = await browser.connect()
        
        # Get or create page
        pages = context.pages
        if pages:
            page = pages[0]
        else:
            page = await context.new_page()
        
        # Navigate to library
        logger.info("Navigating to Udio library...")
        try:
            await page.goto('https://www.udio.com/my-creations', timeout=30000)
        except:
            pass
        
        await asyncio.sleep(2)
        
        # Check if logged in
        if 'login' in page.url.lower():
            logger.warning("Not logged in. Please log in to Udio...")
            print("\n⚠️  Please log in to Udio in the browser window")
            print("Then navigate to your library and press Enter here...")
            input()
        
        logger.info("Ready to map library structure")
        print("\n📂 Make sure the folder tree is visible in the left sidebar")
        input("Press Enter when ready to start mapping...")
        
        # Create mapper
        mapper = UdioFolderMapper(page, logger=logger)
        
        # Map folder structure
        structure = await mapper.map_structure()
        
        # Print tree view
        OutputFormatter.print_tree(structure)
        
        # Print summary
        OutputFormatter.print_summary(structure)
        
        # Save to file with timestamp
        export_path = paths.get_export_path('library_structure.json', timestamped=True)
        OutputFormatter.save_json(structure, export_path)
        
        logger.success("Mapping completed successfully")
        
        # Clean old exports (keep last 5)
        paths.clean_old_exports(keep_count=5, pattern='library_structure_*.json')
        
    except Exception as e:
        logger.error(f"Mapping failed: {e}")
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await browser.close()
        logger.info("Browser closed")


if __name__ == '__main__':
    asyncio.run(main())
