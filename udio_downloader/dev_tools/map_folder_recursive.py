"""
Map a single Udio folder recursively (including subfolders).

Usage:
Run: python -m udio_downloader.dev_tools.map_folder_recursive
"""

import asyncio
from udio_downloader.dev_tools.scraper.core import BrowserConnection
from udio_downloader.dev_tools.scraper.platforms.udio.mapper_async import UdioFolderMapper
from udio_downloader.dev_tools.scraper.utils import OutputFormatter, get_logger, PathManager


async def main():
    """Map a single folder recursively"""
    # Setup paths and logging
    paths = PathManager(base_dir='output', platform='udio')
    logger = get_logger('udio_folder_recursive', log_dir=str(paths.get_log_dir()))
    
    browser = BrowserConnection()
    
    try:
        # Launch Chrome
        logger.info("Starting recursive folder mapping")
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
        print("RECURSIVE FOLDER MAPPER")
        print("="*60)
        print("\n📂 Instructions:")
        print("1. Make sure the folder tree is visible in the left sidebar")
        print("2. DO NOT click on any folder - just make sure you can see the tree")
        print("3. Press Enter here to start")
        print()
        input("Press Enter when ready...")
        
        # Create mapper
        mapper = UdioFolderMapper(page, logger=logger)
        
        # Find the folder tree
        logger.info("Finding folder tree...")
        container = await mapper.find_container()
        
        # Get all top-level folders
        items = await container.query_selector_all(':scope > *')
        
        # Find "Instrumental Songs" folder
        target_folder = None
        target_item = None
        
        for item in items:
            name_button = await item.query_selector('button[title]')
            if name_button:
                folder_name = await name_button.get_attribute('title')
                if folder_name == 'Instrumental Songs':
                    target_folder = folder_name
                    target_item = item
                    break
        
        if not target_item:
            print("\n❌ Could not find 'Instrumental Songs' folder")
            print("Available folders:")
            for item in items:
                name_button = await item.query_selector('button[title]')
                if name_button:
                    folder_name = await name_button.get_attribute('title')
                    print(f"  - {folder_name}")
            return
        
        logger.info(f"Found folder: {target_folder}")
        print(f"\n✓ Found folder: {target_folder}")
        print("Processing folder and all subfolders...")
        
        # Process the folder recursively
        folder_data = await mapper.process_item(target_item, [])
        
        # Print results
        print("\n" + "="*60)
        print("EXTRACTION COMPLETE")
        print("="*60)
        print(f"\nFolder: {folder_data['name']}")
        print(f"Total songs (including subfolders): {folder_data['songCount']}")
        print(f"Subfolders: {len(folder_data['subfolders'])}")
        
        # Print folder tree
        def print_folder_tree(folder, indent=0):
            prefix = "  " * indent
            icon = "📂" if folder['hasChildren'] else "📁"
            direct_songs = len(folder.get('songs', []))
            print(f"{prefix}{icon} {folder['name']} ({direct_songs} songs directly, {folder['songCount']} total)")
            for subfolder in folder.get('subfolders', []):
                print_folder_tree(subfolder, indent + 1)
        
        print("\nFolder structure:")
        print_folder_tree(folder_data)
        
        # Show sample songs
        all_songs = []
        def collect_songs(folder):
            all_songs.extend(folder.get('songs', []))
            for subfolder in folder.get('subfolders', []):
                collect_songs(subfolder)
        
        collect_songs(folder_data)
        
        if all_songs:
            print(f"\nFirst 5 songs (from {len(all_songs)} total):")
            for i, song in enumerate(all_songs[:5], 1):
                print(f"\n{i}. {song['title']}")
                print(f"   ID: {song['id']}")
                print(f"   Duration: {song.get('duration', 'N/A')}")
                print(f"   Liked: {song.get('isLiked', False)}")
                print(f"   Disliked: {song.get('isDisliked', False)}")
                print(f"   Tags: {', '.join(song.get('tags', []))}")
        
        # Save to file
        export_path = paths.get_export_path('instrumental_songs_recursive.json', timestamped=True)
        OutputFormatter.save_json(folder_data, export_path)
        
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
