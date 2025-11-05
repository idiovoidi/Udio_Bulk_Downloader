"""
Udio Library Scraper - Final Version

Based on actual user interaction patterns from action logs.
Uses the exact selectors and workflow that work in practice.
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


class UdioFinalScraper:
    """Final scraper based on real user interaction patterns."""
    
    def __init__(self, user_data_dir: str = None, headless: bool = False):
        self.user_data_dir = user_data_dir or str(Path.home() / '.udio_downloader' / 'browser_profile')
        self.headless = headless
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Storage
        self.all_songs: List[Dict] = []
        self.all_folders: List[Dict] = []
        self.song_ids: set = set()
        
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
    
    async def get_folders(self) -> List[Dict]:
        """Get all folders using the exact pattern from action log."""
        logger.info("Finding folders...")
        
        folders = await self.page.evaluate('''() => {
            const folders = [];
            
            // Find all folder buttons - they have the group/label class pattern
            const buttons = document.querySelectorAll('button.group\\\\/label');
            
            buttons.forEach((button, index) => {
                try {
                    // Get folder name from span inside button
                    const nameSpan = button.querySelector('span');
                    if (!nameSpan) return;
                    
                    const name = nameSpan.textContent?.trim();
                    if (!name || name.length < 1) return;
                    
                    // Get parent container to find song count
                    const container = button.closest('.flex.h-8.grow.items-center');
                    if (!container) return;
                    
                    // Try to find song count in the container's parent
                    const parentDiv = container.parentElement;
                    let songCount = 0;
                    
                    if (parentDiv) {
                        const countText = parentDiv.textContent;
                        const match = countText.match(/(\\d+)\\s*songs?/i);
                        if (match) {
                            songCount = parseInt(match[1]);
                        }
                    }
                    
                    folders.push({
                        name: name,
                        songCount: songCount,
                        index: index
                    });
                } catch (err) {
                    console.error('Error extracting folder:', err);
                }
            });
            
            return folders;
        }''')
        
        logger.info(f"Found {len(folders)} folders")
        return folders
    
    async def click_folder(self, folder_name: str) -> bool:
        """Click a folder using the exact selector pattern."""
        logger.info(f"Clicking folder: {folder_name}")
        
        try:
            # Find and click the folder button by name
            clicked = await self.page.evaluate('''(folderName) => {
                const buttons = document.querySelectorAll('button.group\\\\/label');
                
                for (const button of buttons) {
                    const span = button.querySelector('span');
                    if (span && span.textContent?.trim() === folderName) {
                        button.click();
                        return true;
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
    
    async def scroll_to_load_songs(self):
        """Scroll to load all songs in current view."""
        previous_count = 0
        no_change = 0
        
        for _ in range(50):
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1)
            
            # Count song elements (they have play count indicators)
            current_count = await self.page.evaluate('''() => {
                return document.querySelectorAll('.lucide-play').length;
            }''')
            
            if current_count > previous_count:
                previous_count = current_count
                no_change = 0
            else:
                no_change += 1
                if no_change >= 3:
                    break
        
        return previous_count
    
    async def extract_songs_from_current_view(self, folder_path: str) -> List[Dict]:
        """Extract songs from current view using patterns from action log."""
        logger.info("Extracting songs...")
        
        songs = await self.page.evaluate('''(folderPath) => {
            const songs = [];
            
            // Find all song containers - they have play icons and duration info
            const playIcons = document.querySelectorAll('.lucide-play');
            
            playIcons.forEach((icon, index) => {
                try {
                    // Get the parent container that has song info
                    const container = icon.closest('div[class*="flex"]');
                    if (!container) return;
                    
                    // Find the song title - usually in a nearby element
                    let title = null;
                    let songUrl = null;
                    
                    // Look for links to songs
                    const songLink = container.closest('a[href*="/songs/"]') || 
                                    container.querySelector('a[href*="/songs/"]') ||
                                    container.parentElement?.querySelector('a[href*="/songs/"]');
                    
                    if (songLink) {
                        songUrl = songLink.href;
                        const songId = songUrl.split('/songs/')[1]?.split('?')[0];
                        
                        // Try to get title from link or nearby text
                        title = songLink.textContent?.trim() || 
                               songLink.getAttribute('aria-label') ||
                               container.textContent?.split('\\n')[0]?.trim();
                        
                        if (songId && title) {
                            songs.push({
                                id: songId,
                                title: title,
                                url: songUrl,
                                folderPath: folderPath
                            });
                        }
                    }
                } catch (err) {
                    console.error('Error extracting song:', err);
                }
            });
            
            return songs;
        }''', folder_path)
        
        logger.info(f"Extracted {len(songs)} songs")
        return songs
    
    async def scrape_all_folders(self):
        """Scrape all folders and their songs."""
        
        print()
        print("=" * 60)
        print("UDIO LIBRARY SCRAPER")
        print("=" * 60)
        print()
        
        # Get all folders
        folders = await self.get_folders()
        
        if not folders:
            logger.error("No folders found!")
            print()
            print("Troubleshooting:")
            print("1. Make sure you're on the library page")
            print("2. Make sure folders are visible")
            print("3. Try scrolling to see folders")
            return
        
        print(f"Found {len(folders)} folders:")
        for i, folder in enumerate(folders):
            print(f"  {i+1}. {folder['name']:40} ({folder['songCount']} songs)")
        print()
        
        input("Press Enter to start scraping...")
        print()
        
        # Scrape each folder
        for i, folder in enumerate(folders):
            print()
            print(f"Processing folder {i+1}/{len(folders)}: {folder['name']}")
            print("-" * 60)
            
            # Click folder
            clicked = await self.click_folder(folder['name'])
            if not clicked:
                logger.warning(f"Could not click folder: {folder['name']}")
                continue
            
            # Scroll to load all songs
            song_count = await self.scroll_to_load_songs()
            logger.info(f"Found {song_count} song elements")
            
            # Extract songs
            songs = await self.extract_songs_from_current_view(f"/{folder['name']}")
            
            # Add new songs
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
                'songCount': new_songs
            })
            
            # Navigate back to library
            await self.page.goto('https://www.udio.com/library')
            await asyncio.sleep(2)
        
        logger.info("Scraping complete!")
    
    def create_export(self) -> Dict:
        """Create export data structure."""
        
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
        
        filepath = Path(filename).absolute()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved to {filepath}")
        
        return export_data
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()


async def main():
    print("=" * 60)
    print("UDIO LIBRARY SCRAPER - FINAL VERSION")
    print("=" * 60)
    print()
    print("Based on real user interaction patterns")
    print()
    
    scraper = UdioFinalScraper(headless=False)
    
    try:
        await scraper.initialize()
        await scraper.navigate_to_library()
        await scraper.scrape_all_folders()
        
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
            print(f"  {folder['name']}: {folder['songCount']} songs")
        
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
