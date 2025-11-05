"""
Udio Library Tree Scraper

This version navigates through the folder tree structure,
clicking into each folder to extract songs.
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, BrowserContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UdioTreeScraper:
    """Scrapes Udio library by navigating folder tree."""
    
    def __init__(self, user_data_dir: str = None, headless: bool = False):
        self.user_data_dir = user_data_dir or str(Path.home() / '.udio_downloader' / 'browser_profile')
        self.headless = headless
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.all_songs = []
        self.all_folders = []
        
    async def initialize(self):
        """Initialize Playwright and browser."""
        logger.info("Initializing Playwright...")
        
        Path(self.user_data_dir).mkdir(parents=True, exist_ok=True)
        
        self.playwright = await async_playwright().start()
        
        self.context = await self.playwright.chromium.launch_persistent_context(
            self.user_data_dir,
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--disable-automation'
            ],
            viewport={'width': 1920, 'height': 1080},
            ignore_default_args=['--enable-automation']
        )
        
        self.page = await self.context.new_page()
        
        # Hide webdriver flag
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        logger.info("Browser initialized")
        
    async def navigate_to_library(self):
        """Navigate to Udio library."""
        logger.info("Navigating to Udio library...")
        
        try:
            await self.page.goto('https://www.udio.com/library', timeout=30000)
        except:
            pass
        
        await asyncio.sleep(3)
        
        if 'login' in self.page.url.lower() or 'google.com' in self.page.url.lower():
            print()
            print("=" * 60)
            print("LOGIN REQUIRED")
            print("=" * 60)
            print("Please log in to Udio in the browser.")
            input("Press Enter when you're on the library page...")
            
            try:
                await self.page.wait_for_url('**/library**', timeout=60000)
            except:
                pass
            
            await asyncio.sleep(2)
        
        logger.info(f"Current URL: {self.page.url}")
    
    async def get_folder_tree(self) -> List[Dict]:
        """Extract the folder tree structure."""
        logger.info("Extracting folder tree...")
        
        print()
        print("=" * 60)
        print("FOLDER TREE EXTRACTION")
        print("=" * 60)
        print()
        print("Please make sure the folder tree is visible on the left side.")
        print("If you don't see it, click the folder icon in the top-left.")
        print()
        input("Press Enter when folder tree is visible...")
        
        # Extract folder tree
        folders = await self.page.evaluate('''() => {
            const folders = [];
            
            // Look for folder containers with the specific structure
            // Folders have: class="group/folder" and contain a folder SVG icon
            const folderContainers = document.querySelectorAll('.group\\/folder');
            
            console.log(`Found ${folderContainers.length} folder containers`);
            
            folderContainers.forEach((container, index) => {
                try {
                    // Check if it has a folder icon (lucide-folder SVG)
                    const folderIcon = container.querySelector('.lucide-folder');
                    if (!folderIcon) return;
                    
                    // Get folder name from the span inside the button
                    const nameSpan = container.querySelector('button span');
                    if (!nameSpan) return;
                    
                    const name = nameSpan.textContent?.trim();
                    if (!name || name.length < 1) return;
                    
                    // Get song count
                    let songCount = 0;
                    const countSpans = container.querySelectorAll('.text-muted-foreground span');
                    if (countSpans.length >= 2) {
                        songCount = parseInt(countSpans[0].textContent) || 0;
                    }
                    
                    // Get the clickable button
                    const button = container.querySelector('button');
                    
                    folders.push({
                        name: name,
                        songCount: songCount,
                        index: index,
                        hasButton: !!button,
                        element: container.outerHTML.substring(0, 300)
                    });
                } catch (err) {
                    console.error('Error extracting folder:', err);
                }
            });
            
            return folders;
        }''')
        
        logger.info(f"Found {len(folders)} potential folder items")
        
        # Show folders to user
        print()
        print("Found folders:")
        total_songs = 0
        for i, folder in enumerate(folders):
            song_count = folder.get('songCount', 0)
            total_songs += song_count
            print(f"  {i+1}. {folder['name'][:40]:40} ({song_count} songs)")
        
        print()
        print(f"Total: {len(folders)} folders, {total_songs} songs")
        print()
        
        return folders
    
    async def click_folder(self, folder_name: str) -> bool:
        """Click on a folder to open it."""
        logger.info(f"Clicking folder: {folder_name}")
        
        try:
            # Find and click the folder button
            clicked = await self.page.evaluate('''(folderName) => {
                // Find all folder containers
                const folders = document.querySelectorAll('.group\\/folder');
                
                for (const folder of folders) {
                    // Check if this folder has the matching name
                    const nameSpan = folder.querySelector('button span');
                    if (nameSpan && nameSpan.textContent.trim() === folderName) {
                        // Click the button
                        const button = folder.querySelector('button');
                        if (button) {
                            button.click();
                            return true;
                        }
                    }
                }
                
                return false;
            }''', folder_name)
            
            if clicked:
                await asyncio.sleep(1.5)  # Wait for folder to load
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error clicking folder: {e}")
            return False
    
    async def extract_songs_from_current_view(self, folder_path: str = "/") -> List[Dict]:
        """Extract songs visible in current view."""
        
        # Scroll to load all songs in this view
        await self.scroll_current_view()
        
        songs = await self.page.evaluate(f'''(folderPath) => {{
            const songs = [];
            const songLinks = document.querySelectorAll('a[href*="/songs/"]');
            
            songLinks.forEach((link, index) => {{
                try {{
                    const url = link.href;
                    const songId = url.split('/songs/')[1]?.split('?')[0]?.split('/')[0];
                    
                    if (!songId) return;
                    
                    // Get title
                    let title = link.textContent?.trim() || `Song ${{index + 1}}`;
                    title = title.replace(/[\\n\\r\\t]+/g, ' ').trim();
                    
                    songs.push({{
                        id: songId,
                        title: title,
                        url: url,
                        folderPath: folderPath
                    }});
                }} catch (err) {{
                    console.error('Error extracting song:', err);
                }}
            }});
            
            return songs;
        }}''', folder_path)
        
        return songs
    
    async def scroll_current_view(self):
        """Scroll the current view to load all songs."""
        previous_count = 0
        no_change = 0
        
        for _ in range(20):
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(0.5)
            
            current_count = await self.page.locator('a[href*="/songs/"]').count()
            
            if current_count == previous_count:
                no_change += 1
                if no_change >= 2:
                    break
            else:
                no_change = 0
                previous_count = current_count
    
    async def scrape_folder_recursive(self, folder_name: str, folder_path: str, depth: int = 0):
        """Recursively scrape a folder and its subfolders."""
        
        if depth > 10:  # Prevent infinite recursion
            return
        
        indent = "  " * depth
        logger.info(f"{indent}Scraping folder: {folder_path}")
        
        # Click the folder
        if depth > 0:  # Don't click root
            clicked = await self.click_folder(folder_name)
            if not clicked:
                logger.warning(f"{indent}Could not click folder: {folder_name}")
                return
        
        # Extract songs from this folder
        songs = await self.extract_songs_from_current_view(folder_path)
        logger.info(f"{indent}Found {len(songs)} songs in {folder_path}")
        
        self.all_songs.extend(songs)
        
        # Record folder
        self.all_folders.append({
            'id': f'folder_{len(self.all_folders)}',
            'name': folder_name,
            'path': folder_path,
            'songCount': len(songs)
        })
        
        # TODO: Find and scrape subfolders
        # This would require identifying subfolder elements and recursing
    
    async def scrape_all(self):
        """Main scraping workflow."""
        
        # Get root folders
        folders = await self.get_folder_tree()
        
        if not folders:
            logger.error("No folders found!")
            return
        
        print()
        print("=" * 60)
        print("SCRAPING STRATEGY")
        print("=" * 60)
        print()
        print("Option 1: Scrape all visible songs (current view)")
        print("Option 2: Navigate through each folder (manual)")
        print()
        choice = input("Choose option (1 or 2): ").strip()
        
        if choice == "1":
            # Simple approach: just get all visible songs
            logger.info("Scraping all visible songs...")
            
            # Scroll to load everything
            logger.info("Scrolling to load all content...")
            previous_count = 0
            no_change = 0
            
            for i in range(100):
                await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1.5)
                
                current_count = await self.page.locator('a[href*="/songs/"]').count()
                
                if current_count > previous_count:
                    logger.info(f"Loaded {current_count} songs...")
                    previous_count = current_count
                    no_change = 0
                else:
                    no_change += 1
                    if no_change >= 3:
                        break
            
            logger.info(f"Final count: {current_count} songs")
            
            # Extract all songs
            self.all_songs = await self.extract_songs_from_current_view("/")
            
            # Extract folders
            self.all_folders = folders[:50]  # Limit to reasonable number
            
        else:
            # Manual navigation approach
            logger.info("Manual navigation mode")
            print()
            print("For each folder:")
            print("1. Manually click the folder in the browser")
            print("2. Wait for songs to load")
            print("3. Press Enter here")
            print("4. Script will extract songs")
            print("5. Repeat for next folder")
            print()
            
            for folder in folders[:10]:  # Limit for manual mode
                print(f"\nFolder: {folder['name']}")
                input("Click this folder in browser, then press Enter...")
                
                songs = await self.extract_songs_from_current_view(f"/{folder['name']}")
                logger.info(f"Extracted {len(songs)} songs")
                self.all_songs.extend(songs)
                
                self.all_folders.append({
                    'id': f'folder_{len(self.all_folders)}',
                    'name': folder['name'],
                    'path': f"/{folder['name']}",
                    'songCount': len(songs)
                })
    
    def create_export(self) -> Dict:
        """Create export data structure."""
        
        # Remove duplicates
        unique_songs = {}
        for song in self.all_songs:
            if song['id'] not in unique_songs:
                unique_songs[song['id']] = song
        
        songs = list(unique_songs.values())
        
        # Format for downloader
        formatted_songs = []
        for song in songs:
            formatted_songs.append({
                'id': song['id'],
                'title': song['title'],
                'url': song['url'],
                'folderId': None,
                'folderPath': song.get('folderPath', '/'),
                'createdAt': datetime.now().isoformat(),
                'duration': 0,
                'tags': [],
                'isPublic': False
            })
        
        return {
            'exportDate': datetime.now().isoformat(),
            'totalSongs': len(formatted_songs),
            'folders': self.all_folders,
            'songs': formatted_songs
        }
    
    async def save_export(self, filename: str = "udio_library_export.json"):
        """Save export to file."""
        export_data = self.create_export()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved export to {filename}")
        logger.info(f"Total songs: {export_data['totalSongs']}")
        logger.info(f"Total folders: {len(export_data['folders'])}")
        
        return export_data
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()


async def main():
    print("=" * 60)
    print("UDIO TREE SCRAPER")
    print("=" * 60)
    print()
    
    scraper = UdioTreeScraper(headless=False)
    
    try:
        await scraper.initialize()
        await scraper.navigate_to_library()
        await scraper.scrape_all()
        
        export_data = await scraper.save_export()
        
        print()
        print("=" * 60)
        print("SCRAPING COMPLETE!")
        print("=" * 60)
        print()
        print(f"✅ Exported {export_data['totalSongs']} songs")
        print(f"✅ Exported {len(export_data['folders'])} folders")
        print(f"✅ Saved to: udio_library_export.json")
        print()
        print("Next steps:")
        print("1. Import: python -m udio_downloader import-metadata --json-file udio_library_export.json")
        print("2. Status: python -m udio_downloader status")
        print("3. Download: python -m udio_downloader download")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await scraper.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
