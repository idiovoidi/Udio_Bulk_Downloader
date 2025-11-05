"""
Udio Complete Library Scraper

Recursively navigates through all folders and subfolders,
extracting songs from each one to build a complete library map.
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Set
from playwright.async_api import async_playwright, Page, BrowserContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UdioCompleteScraper:
    """Complete recursive folder and song scraper."""
    
    def __init__(self, user_data_dir: str = None, headless: bool = False):
        self.user_data_dir = user_data_dir or str(Path.home() / '.udio_downloader' / 'browser_profile')
        self.headless = headless
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Storage for scraped data
        self.all_songs: List[Dict] = []
        self.all_folders: List[Dict] = []
        self.processed_folders: Set[str] = set()
        self.song_ids: Set[str] = set()
        
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
        
        # Hide webdriver
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
            print("Please log in to Udio.")
            input("Press Enter when you're on the library page...")
            
            try:
                await self.page.wait_for_url('**/library**', timeout=60000)
            except:
                pass
            
            await asyncio.sleep(2)
        
        logger.info(f"Current URL: {self.page.url}")
    
    async def get_visible_folders(self) -> List[Dict]:
        """Get all currently visible folders."""
        
        folders = await self.page.evaluate('''() => {
            const folders = [];
            
            // Find all elements that look like folders
            // They have a folder icon and a name
            const allElements = document.querySelectorAll('div, button, a');
            
            for (const el of allElements) {
                // Check if it has a folder icon
                const folderIcon = el.querySelector('svg.lucide-folder, svg[class*="folder"]');
                if (!folderIcon) continue;
                
                // Get the folder name
                const spans = el.querySelectorAll('span');
                let folderName = null;
                
                for (const span of spans) {
                    const text = span.textContent?.trim();
                    if (text && text.length > 0 && text.length < 100 && !text.includes('songs')) {
                        folderName = text;
                        break;
                    }
                }
                
                if (!folderName) continue;
                
                // Try to get song count
                let songCount = 0;
                const fullText = el.textContent;
                const match = fullText.match(/(\\d+)\\s*songs?/i);
                if (match) {
                    songCount = parseInt(match[1]);
                }
                
                // Get position for clicking
                const rect = el.getBoundingClientRect();
                
                folders.push({
                    name: folderName,
                    songCount: songCount,
                    x: rect.x + rect.width / 2,
                    y: rect.y + rect.height / 2,
                    visible: rect.top >= 0 && rect.bottom <= window.innerHeight
                });
            }
            
            // Remove duplicates by name
            const unique = {};
            folders.forEach(f => {
                if (!unique[f.name]) {
                    unique[f.name] = f;
                }
            });
            
            return Object.values(unique);
        }''')
        
        return folders
    
    async def click_folder(self, folder_name: str) -> bool:
        """Click on a folder to open it."""
        logger.info(f"Clicking folder: {folder_name}")
        
        try:
            # Find and click the folder
            clicked = await self.page.evaluate('''(folderName) => {
                // Find all elements
                const allElements = document.querySelectorAll('div, button, a');
                
                for (const el of allElements) {
                    // Check if it has a folder icon
                    const folderIcon = el.querySelector('svg.lucide-folder, svg[class*="folder"]');
                    if (!folderIcon) continue;
                    
                    // Check if name matches
                    const spans = el.querySelectorAll('span');
                    for (const span of spans) {
                        if (span.textContent?.trim() === folderName) {
                            // Found it! Click it
                            el.click();
                            return true;
                        }
                    }
                }
                
                return false;
            }''', folder_name)
            
            if clicked:
                await asyncio.sleep(2)  # Wait for folder to load
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error clicking folder: {e}")
            return False
    
    async def scroll_and_load_songs(self):
        """Scroll current view to load all songs."""
        previous_count = 0
        no_change = 0
        
        for _ in range(50):  # Max 50 scrolls per folder
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1)
            
            current_count = await self.page.locator('a[href*="/songs/"]').count()
            
            if current_count > previous_count:
                previous_count = current_count
                no_change = 0
            else:
                no_change += 1
                if no_change >= 3:
                    break
        
        return previous_count
    
    async def extract_songs_from_current_view(self, folder_path: str) -> List[Dict]:
        """Extract all songs from current view."""
        
        songs = await self.page.evaluate('''(folderPath) => {
            const songs = [];
            const songLinks = document.querySelectorAll('a[href*="/songs/"]');
            
            songLinks.forEach((link, index) => {
                try {
                    const url = link.href;
                    const songId = url.split('/songs/')[1]?.split('?')[0]?.split('/')[0];
                    
                    if (!songId) return;
                    
                    // Get title
                    let title = link.textContent?.trim();
                    
                    if (!title || title.length < 2) {
                        const parent = link.closest('div, li, article');
                        if (parent) {
                            const titleEl = parent.querySelector('[class*="title"], span, h1, h2, h3, h4');
                            if (titleEl) {
                                title = titleEl.textContent?.trim();
                            }
                        }
                    }
                    
                    if (!title || title.length < 2) {
                        title = `Song ${index + 1}`;
                    }
                    
                    title = title.replace(/[\\n\\r\\t]+/g, ' ').trim();
                    
                    songs.push({
                        id: songId,
                        title: title,
                        url: url,
                        folderPath: folderPath
                    });
                    
                } catch (err) {
                    console.error('Error extracting song:', err);
                }
            });
            
            return songs;
        }''', folder_path)
        
        return songs
    
    async def scrape_folder_recursive(self, folder_name: str, folder_path: str, depth: int = 0):
        """Recursively scrape a folder and all its subfolders."""
        
        if depth > 5:  # Reduced max depth to prevent issues
            logger.warning(f"Max depth reached for {folder_path}")
            return
        
        # Check if already processed
        if folder_path in self.processed_folders:
            logger.info(f"Already processed: {folder_path}")
            return
        
        indent = "  " * depth
        logger.info(f"{indent}📁 Scraping: {folder_path}")
        
        # Click the folder (if not root)
        if depth > 0:
            clicked = await self.click_folder(folder_name)
            if not clicked:
                logger.warning(f"{indent}Could not click folder: {folder_name}")
                return
        
        # Mark as processed BEFORE looking for subfolders
        self.processed_folders.add(folder_path)
        
        # Scroll to load all songs in this folder
        song_count = await self.scroll_and_load_songs()
        logger.info(f"{indent}Found {song_count} songs in view")
        
        # Extract songs
        songs = await self.extract_songs_from_current_view(folder_path)
        
        # Add new songs (avoid duplicates)
        new_songs = 0
        for song in songs:
            if song['id'] not in self.song_ids:
                self.all_songs.append(song)
                self.song_ids.add(song['id'])
                new_songs += 1
        
        logger.info(f"{indent}Added {new_songs} new songs from {folder_path}")
        
        # Record folder
        self.all_folders.append({
            'id': f'folder_{len(self.all_folders)}',
            'name': folder_name,
            'path': folder_path,
            'songCount': new_songs,
            'depth': depth
        })
        
        # Look for subfolders (but filter out parent folders)
        all_folders = await self.get_visible_folders()
        
        # Filter to only NEW subfolders (not already processed)
        subfolders = []
        for folder in all_folders:
            potential_path = f"{folder_path}/{folder['name']}"
            # Only add if not processed and not the current folder
            if potential_path not in self.processed_folders and folder['name'] != folder_name:
                subfolders.append(folder)
        
        if subfolders:
            logger.info(f"{indent}Found {len(subfolders)} NEW subfolders to process")
            
            for subfolder in subfolders:
                subfolder_name = subfolder['name']
                subfolder_path = f"{folder_path}/{subfolder_name}"
                
                # Double-check not processed
                if subfolder_path in self.processed_folders:
                    logger.info(f"{indent}Skipping already processed: {subfolder_path}")
                    continue
                
                # Recursively scrape subfolder
                await self.scrape_folder_recursive(
                    subfolder_name,
                    subfolder_path,
                    depth + 1
                )
                
                # Navigate back to parent folder
                if depth > 0:
                    await self.click_folder(folder_name)
                    await asyncio.sleep(1)
        else:
            logger.info(f"{indent}No new subfolders to process")
    
    async def scrape_all(self):
        """Main scraping workflow."""
        
        print()
        print("=" * 60)
        print("COMPLETE LIBRARY SCRAPING")
        print("=" * 60)
        print()
        print("Choose scraping mode:")
        print()
        print("1. Simple mode - Click each folder once, extract songs")
        print("   (Recommended - faster, more reliable)")
        print()
        print("2. Recursive mode - Navigate into subfolders automatically")
        print("   (Advanced - may get stuck on complex structures)")
        print()
        choice = input("Choose mode (1 or 2): ").strip()
        
        if choice == "1":
            await self.scrape_simple()
        else:
            await self.scrape_recursive()
    
    async def scrape_simple(self):
        """Simple non-recursive scraping."""
        print()
        print("Simple mode: Processing each folder once")
        print()
        
        # Get root folders
        logger.info("Finding root folders...")
        root_folders = await self.get_visible_folders()
        
        if not root_folders:
            logger.error("No folders found!")
            print()
            print("Troubleshooting:")
            print("1. Make sure you're on the library page")
            print("2. Make sure folders are visible")
            print("3. Try scrolling down to see folders")
            return
        
        logger.info(f"Found {len(root_folders)} root folders")
        print()
        print("Root folders:")
        for i, folder in enumerate(root_folders):
            print(f"  {i+1}. {folder['name']:40} ({folder['songCount']} songs)")
        print()
        
        # Scrape each root folder (simple mode)
        for i, folder in enumerate(root_folders):
            print()
            print(f"Processing folder {i+1}/{len(root_folders)}: {folder['name']}")
            print("-" * 60)
            
            # Click folder
            clicked = await self.click_folder(folder['name'])
            if not clicked:
                logger.warning(f"Could not click folder: {folder['name']}")
                continue
            
            # Scroll and extract
            song_count = await self.scroll_and_load_songs()
            logger.info(f"Found {song_count} songs in view")
            
            songs = await self.extract_songs_from_current_view(f"/{folder['name']}")
            
            # Add songs
            new_songs = 0
            for song in songs:
                if song['id'] not in self.song_ids:
                    self.all_songs.append(song)
                    self.song_ids.add(song['id'])
                    new_songs += 1
            
            logger.info(f"Added {new_songs} new songs from {folder['name']}")
            
            # Record folder
            self.all_folders.append({
                'id': f'folder_{len(self.all_folders)}',
                'name': folder['name'],
                'path': f"/{folder['name']}",
                'songCount': new_songs,
                'depth': 1
            })
            
            # Navigate back to root
            await self.page.goto('https://www.udio.com/library')
            await asyncio.sleep(2)
        
        logger.info("Scraping complete!")
    
    async def scrape_recursive(self):
        """Recursive scraping with subfolder navigation."""
        print()
        print("Recursive mode: Processing folders and subfolders")
        print()
        
        # Get root folders
        logger.info("Finding root folders...")
        root_folders = await self.get_visible_folders()
        
        if not root_folders:
            logger.error("No folders found!")
            return
        
        logger.info(f"Found {len(root_folders)} root folders")
        print()
        print("Root folders:")
        for i, folder in enumerate(root_folders):
            print(f"  {i+1}. {folder['name']:40} ({folder['songCount']} songs)")
        print()
        
        # Scrape each root folder recursively
        for i, folder in enumerate(root_folders):
            print()
            print(f"Processing folder {i+1}/{len(root_folders)}: {folder['name']}")
            print("-" * 60)
            
            await self.scrape_folder_recursive(
                folder['name'],
                f"/{folder['name']}",
                depth=1
            )
            
            # Navigate back to root
            await self.page.goto('https://www.udio.com/library')
            await asyncio.sleep(2)
        
        logger.info("Scraping complete!")
    
    def create_export(self) -> Dict:
        """Create export data structure."""
        
        # Format songs
        formatted_songs = []
        for song in self.all_songs:
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
        
        logger.info(f"Saved to {filename}")
        
        return export_data
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()


async def main():
    print("=" * 60)
    print("UDIO COMPLETE LIBRARY SCRAPER")
    print("=" * 60)
    print()
    print("This scraper will:")
    print("- Navigate through ALL folders and subfolders")
    print("- Scroll to load ALL songs in each folder")
    print("- Build a complete hierarchical map")
    print("- Extract every single song")
    print()
    
    scraper = UdioCompleteScraper(headless=False)
    
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
        print(f"✅ Total songs: {len(scraper.all_songs)}")
        print(f"✅ Total folders: {len(scraper.all_folders)}")
        print(f"✅ Unique songs: {len(scraper.song_ids)}")
        print(f"✅ Saved to: udio_library_export.json")
        print()
        
        # Show folder breakdown
        print("Folder breakdown:")
        for folder in scraper.all_folders:
            indent = "  " * folder['depth']
            print(f"{indent}{folder['name']}: {folder['songCount']} songs")
        
        print()
        print("Next steps:")
        print("1. Import: python -m udio_downloader import-metadata --json-file udio_library_export.json")
        print("2. Status: python -m udio_downloader status")
        print("3. Download: python -m udio_downloader download")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        print(f"Partial results: {len(scraper.all_songs)} songs, {len(scraper.all_folders)} folders")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await scraper.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
