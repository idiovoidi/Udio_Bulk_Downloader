"""
Udio Library Scraper - Main Window Approach

Scrapes directly from the main library view without dealing with folder tree.
Much simpler and more reliable!
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


class UdioMainScraper:
    """Scrapes Udio library from main window."""
    
    def __init__(self, user_data_dir: str = None, headless: bool = False):
        self.user_data_dir = user_data_dir or str(Path.home() / '.udio_downloader' / 'browser_profile')
        self.headless = headless
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
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
    
    async def wait_for_songs(self):
        """Wait for songs to be visible."""
        logger.info("Waiting for songs to load...")
        
        await asyncio.sleep(2)
        
        song_count = await self.page.locator('a[href*="/songs/"]').count()
        
        if song_count == 0:
            print()
            print("=" * 60)
            print("WAITING FOR SONGS")
            print("=" * 60)
            print()
            print("Please make sure songs are visible in the main window.")
            print("If you see folders, click on 'All Songs' or a specific folder.")
            print()
            input("Press Enter when you can see songs...")
            
            song_count = await self.page.locator('a[href*="/songs/"]').count()
            logger.info(f"Found {song_count} songs after waiting")
        else:
            logger.info(f"Found {song_count} songs")
    
    async def scroll_to_load_all(self):
        """Scroll to load all songs via lazy loading."""
        logger.info("Scrolling to load all songs...")
        
        print()
        print("Scrolling to load all content...")
        print("This may take a few minutes for large libraries.")
        print()
        
        previous_count = 0
        no_change_count = 0
        scroll_count = 0
        max_scrolls = 200  # Increased for very large libraries
        
        while scroll_count < max_scrolls:
            # Scroll to bottom
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1.5)
            
            # Get current song count
            current_count = await self.page.locator('a[href*="/songs/"]').count()
            
            # Check if new songs loaded
            if current_count > previous_count:
                logger.info(f"Loaded {current_count} songs...")
                previous_count = current_count
                no_change_count = 0
            else:
                no_change_count += 1
                if no_change_count >= 3:
                    logger.info(f"No more songs loading. Final count: {current_count}")
                    break
            
            scroll_count += 1
        
        # Scroll back to top
        await self.page.evaluate('window.scrollTo(0, 0)')
        await asyncio.sleep(1)
        
        return previous_count
    
    async def extract_all_songs(self) -> List[Dict]:
        """Extract all songs from the page."""
        logger.info("Extracting all songs...")
        
        songs = await self.page.evaluate('''() => {
            const songs = [];
            const songLinks = document.querySelectorAll('a[href*="/songs/"]');
            
            console.log(`Extracting from ${songLinks.length} song links`);
            
            songLinks.forEach((link, index) => {
                try {
                    const url = link.href;
                    if (!url || !url.includes('/songs/')) return;
                    
                    // Extract song ID
                    const songId = url.split('/songs/')[1]?.split('?')[0]?.split('/')[0];
                    if (!songId) return;
                    
                    // Get title - try multiple strategies
                    let title = null;
                    
                    // Strategy 1: Link text
                    if (link.textContent?.trim()) {
                        title = link.textContent.trim();
                    }
                    
                    // Strategy 2: Look in parent container
                    if (!title || title.length < 2) {
                        const parent = link.closest('div, li, article');
                        if (parent) {
                            // Try to find title element
                            const titleEl = parent.querySelector('[class*="title"], h1, h2, h3, h4, span');
                            if (titleEl && titleEl.textContent?.trim()) {
                                title = titleEl.textContent.trim();
                            }
                        }
                    }
                    
                    // Fallback
                    if (!title || title.length < 2) {
                        title = `Song ${index + 1}`;
                    }
                    
                    // Clean up title
                    title = title.replace(/[\\n\\r\\t]+/g, ' ').trim();
                    
                    // Try to get duration
                    let duration = null;
                    const parent = link.closest('div, li, article');
                    if (parent) {
                        const durationEl = parent.querySelector('[class*="duration"], time');
                        if (durationEl) {
                            duration = durationEl.textContent?.trim();
                        }
                    }
                    
                    songs.push({
                        id: songId,
                        title: title,
                        url: url,
                        duration: duration
                    });
                    
                } catch (err) {
                    console.error('Error extracting song:', err);
                }
            });
            
            return songs;
        }''')
        
        logger.info(f"Extracted {len(songs)} songs")
        
        # Remove duplicates
        unique_songs = {}
        for song in songs:
            if song['id'] not in unique_songs:
                unique_songs[song['id']] = song
        
        songs = list(unique_songs.values())
        logger.info(f"After deduplication: {len(songs)} unique songs")
        
        return songs
    
    async def extract_folders(self) -> List[Dict]:
        """Try to extract folder information."""
        logger.info("Attempting to extract folder information...")
        
        # Try to find folder elements
        folders = await self.page.evaluate('''() => {
            const folders = [];
            
            // Look for elements with folder icon
            const folderElements = document.querySelectorAll('[class*="folder"]');
            
            folderElements.forEach((el, index) => {
                try {
                    // Check if it has a folder icon
                    const icon = el.querySelector('svg.lucide-folder');
                    if (!icon) return;
                    
                    // Get folder name
                    const nameEl = el.querySelector('span');
                    if (!nameEl) return;
                    
                    const name = nameEl.textContent?.trim();
                    if (!name || name.length < 1) return;
                    
                    // Try to get song count
                    let songCount = 0;
                    const countText = el.textContent;
                    const match = countText.match(/(\\d+)\\s*songs?/i);
                    if (match) {
                        songCount = parseInt(match[1]);
                    }
                    
                    folders.push({
                        id: `folder_${index}`,
                        name: name,
                        path: `/${name}`,
                        songCount: songCount
                    });
                } catch (err) {
                    console.error('Error extracting folder:', err);
                }
            });
            
            return folders;
        }''')
        
        logger.info(f"Extracted {len(folders)} folders")
        return folders
    
    def create_export(self, songs: List[Dict], folders: List[Dict]) -> Dict:
        """Create export data structure."""
        
        # Format songs for downloader
        formatted_songs = []
        for song in songs:
            formatted_songs.append({
                'id': song['id'],
                'title': song['title'],
                'url': song['url'],
                'folderId': None,
                'folderPath': '/',
                'createdAt': datetime.now().isoformat(),
                'duration': self._parse_duration(song.get('duration')),
                'tags': [],
                'isPublic': False
            })
        
        return {
            'exportDate': datetime.now().isoformat(),
            'totalSongs': len(formatted_songs),
            'folders': folders,
            'songs': formatted_songs
        }
    
    def _parse_duration(self, duration_str: Optional[str]) -> int:
        """Parse duration string to seconds."""
        if not duration_str:
            return 0
        
        try:
            if ':' in duration_str:
                parts = duration_str.split(':')
                if len(parts) == 2:
                    minutes, seconds = parts
                    return int(minutes) * 60 + int(seconds)
                elif len(parts) == 3:
                    hours, minutes, seconds = parts
                    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        except:
            pass
        
        return 0
    
    async def save_export(self, export_data: Dict, filename: str = "udio_library_export.json"):
        """Save export to file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved export to {filename}")
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()


async def main():
    print("=" * 60)
    print("UDIO LIBRARY SCRAPER - MAIN WINDOW")
    print("=" * 60)
    print()
    print("This scraper extracts songs from the main library view.")
    print("Much simpler than navigating folder trees!")
    print()
    
    scraper = UdioMainScraper(headless=False)
    
    try:
        # Initialize
        await scraper.initialize()
        
        # Navigate to library
        await scraper.navigate_to_library()
        
        # Wait for songs
        await scraper.wait_for_songs()
        
        # Scroll to load all
        total_songs = await scraper.scroll_to_load_all()
        
        # Extract songs
        songs = await scraper.extract_all_songs()
        
        # Extract folders
        folders = await scraper.extract_folders()
        
        if not songs:
            logger.error("No songs found!")
            print()
            print("Troubleshooting:")
            print("1. Make sure you're on the library page")
            print("2. Make sure songs are visible")
            print("3. Try clicking 'All Songs' if you see folders")
            return
        
        # Create export
        export_data = scraper.create_export(songs, folders)
        
        # Save
        await scraper.save_export(export_data)
        
        # Summary
        print()
        print("=" * 60)
        print("SCRAPING COMPLETE!")
        print("=" * 60)
        print()
        print(f"✅ Exported {len(songs)} songs")
        print(f"✅ Exported {len(folders)} folders")
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
