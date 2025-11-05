"""
Map a single Udio folder for testing.

Usage:
Run: python map_single_folder.py
"""

import asyncio
from scraper.core import BrowserConnection
from scraper.platforms.udio.extractors_async import UdioSongExtractor
from scraper.utils import OutputFormatter, get_logger, PathManager


async def main():
    """Map a single folder"""
    # Setup paths and logging
    paths = PathManager(base_dir='output', platform='udio')
    logger = get_logger('udio_single_folder', log_dir=str(paths.get_log_dir()))
    
    browser = BrowserConnection()
    
    try:
        # Launch Chrome
        logger.info("Starting single folder mapping")
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
            await page.goto('https://www.udio.com/library', timeout=30000)
        except:
            pass
        
        await asyncio.sleep(2)
        
        # Check if logged in
        if 'login' in page.url.lower():
            logger.warning("Not logged in. Please log in to Udio...")
            print("\n⚠️  Please log in to Udio in the browser window")
            print("Then navigate to your library and press Enter here...")
            input()
        
        print("\n" + "="*60)
        print("SINGLE FOLDER MAPPER")
        print("="*60)
        print("\n📂 Instructions:")
        print("1. Make sure the folder tree is visible in the left sidebar")
        print("2. Click on the folder you want to map: 'Instrumental Songs'")
        print("3. Wait for the songs to load")
        print("4. Press Enter here to start extraction")
        print()
        input("Press Enter when ready...")
        
        # Create extractor
        extractor = UdioSongExtractor(page, logger=logger)
        
        # Extract songs from current view
        logger.info("Extracting songs from 'Instrumental Songs' folder...")
        songs = await extractor.extract(folder_path=['Instrumental Songs'])
        
        # Build structure
        structure = {
            'folder': 'Instrumental Songs',
            'songCount': len(songs),
            'songs': songs
        }
        
        # Print results
        print("\n" + "="*60)
        print("EXTRACTION COMPLETE")
        print("="*60)
        print(f"\nFolder: Instrumental Songs")
        print(f"Songs found: {len(songs)}")
        
        if songs:
            print("\nFirst 5 songs:")
            for i, song in enumerate(songs[:5], 1):
                print(f"\n{i}. {song['title']}")
                print(f"   ID: {song['id']}")
                print(f"   Duration: {song.get('duration', 'N/A')}")
                print(f"   Liked: {song.get('isLiked', False)}")
                print(f"   Disliked: {song.get('isDisliked', False)}")
                print(f"   Tags: {', '.join(song.get('tags', []))}")
        
        # Save to file
        export_path = paths.get_export_path('instrumental_songs_test.json', timestamped=True)
        OutputFormatter.save_json(structure, export_path)
        
        logger.success("Extraction completed successfully")
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await browser.close()
        logger.info("Browser closed")


if __name__ == '__main__':
    asyncio.run(main())
