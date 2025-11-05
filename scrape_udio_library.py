"""
Udio Library Scraper using Playwright

This script uses Playwright to scrape your Udio library structure and songs,
then exports to JSON format compatible with the udio_downloader import.
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UdioLibraryScraper:
    """Scrapes Udio library using Playwright."""
    
    def __init__(self, user_data_dir: str = None, headless: bool = False):
        """
        Initialize scraper.
        
        Args:
            user_data_dir: Path to persistent browser profile
            headless: Whether to run browser in headless mode
        """
        self.user_data_dir = user_data_dir or str(Path.home() / '.udio_downloader' / 'browser_profile')
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    async def initialize(self):
        """Initialize Playwright and browser."""
        logger.info("Initializing Playwright...")
        
        # Ensure user data directory exists
        Path(self.user_data_dir).mkdir(parents=True, exist_ok=True)
        
        self.playwright = await async_playwright().start()
        
        # Launch persistent context
        self.context = await self.playwright.chromium.launch_persistent_context(
            self.user_data_dir,
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-infobars',
                '--disable-automation',
                '--disable-browser-side-navigation',
                '--disable-gpu'
            ],
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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
        """Navigate to Udio library page."""
        logger.info("Navigating to Udio library...")
        
        try:
            await self.page.goto('https://www.udio.com/library', wait_until='domcontentloaded', timeout=30000)
        except Exception as e:
            logger.warning(f"Navigation interrupted (likely OAuth redirect): {e}")
        
        # Wait a bit for page to load
        await asyncio.sleep(3)
        
        # Check if we're logged in
        current_url = self.page.url
        if 'login' in current_url.lower() or 'google.com' in current_url.lower() or 'accounts' in current_url.lower():
            logger.warning("Not logged in! Please log in to Udio.")
            logger.info("The login process may redirect through Google OAuth.")
            logger.info("Waiting for you to complete login...")
            
            # Wait for user to log in
            print()
            print("=" * 60)
            print("LOGIN REQUIRED")
            print("=" * 60)
            print()
            print("Please complete the login process in the browser.")
            print("After you see the library page, press Enter here.")
            print()
            input("Press Enter when you're on the library page...")
            
            # Wait for navigation to complete
            try:
                await self.page.wait_for_url('**/library**', timeout=60000)
                logger.info("Successfully navigated to library page")
            except:
                logger.warning("Timeout waiting for library page, continuing anyway...")
            
            await asyncio.sleep(2)
        
        logger.info(f"Current URL: {self.page.url}")
        
    async def wait_for_content(self):
        """Wait for library content to load."""
        logger.info("Waiting for library content to load...")
        
        # Wait a bit for initial load
        await asyncio.sleep(3)
        
        # Check if songs are present
        song_count = await self.page.locator('a[href*="/songs/"]').count()
        
        if song_count == 0:
            logger.warning("No songs detected yet. Waiting for content to load...")
            print()
            print("=" * 60)
            print("WAITING FOR CONTENT")
            print("=" * 60)
            print()
            print("Please wait for the library page to fully load.")
            print("Make sure you can see your songs in the browser.")
            print()
            input("Press Enter when you can see your songs...")
            print()
            
            # Check again
            song_count = await self.page.locator('a[href*="/songs/"]').count()
            logger.info(f"Found {song_count} songs after waiting")
        else:
            logger.info(f"Found {song_count} songs")
        
        return 'a[href*="/songs/"]'
    
    async def expand_all_folders(self):
        """Expand all folders to reveal nested content."""
        logger.info("Expanding all folders...")
        
        # Try to find and click folder expand buttons
        expand_attempts = 0
        max_expand_attempts = 10
        
        while expand_attempts < max_expand_attempts:
            # Look for collapsed folders (various possible selectors)
            expand_buttons = await self.page.evaluate('''() => {
                const buttons = [];
                
                // Try different selectors for folder expand buttons
                const selectors = [
                    '[aria-expanded="false"]',
                    'button[aria-label*="expand"]',
                    'button[aria-label*="Expand"]',
                    '[role="button"][aria-expanded="false"]',
                    '.folder-toggle',
                    '[class*="expand"]',
                    '[class*="chevron"]',
                    '[class*="arrow"]'
                ];
                
                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => {
                        // Check if it's near a folder or looks like a folder control
                        const parent = el.closest('[class*="folder"], [class*="tree"], li, div');
                        if (parent) {
                            buttons.push({
                                selector: selector,
                                text: el.textContent?.trim() || '',
                                ariaLabel: el.getAttribute('aria-label') || ''
                            });
                        }
                    });
                }
                
                return buttons.length;
            }''')
            
            if expand_buttons == 0:
                logger.info("No more folders to expand")
                break
            
            logger.info(f"Found {expand_buttons} collapsed folders, expanding...")
            
            # Click all expand buttons
            await self.page.evaluate('''() => {
                const selectors = [
                    '[aria-expanded="false"]',
                    'button[aria-label*="expand"]',
                    'button[aria-label*="Expand"]',
                    '[role="button"][aria-expanded="false"]'
                ];
                
                for (const selector of selectors) {
                    document.querySelectorAll(selector).forEach(el => {
                        try {
                            el.click();
                        } catch (e) {
                            // Ignore click errors
                        }
                    });
                }
            }''')
            
            # Wait for content to load
            await asyncio.sleep(2)
            expand_attempts += 1
        
        logger.info(f"Folder expansion complete after {expand_attempts} attempts")
    
    async def scroll_to_load_all(self):
        """Scroll page to trigger lazy loading of all songs."""
        logger.info("Scrolling to load all songs...")
        
        previous_height = 0
        previous_song_count = 0
        scroll_attempts = 0
        max_attempts = 100  # Increased for larger libraries
        no_change_count = 0
        
        while scroll_attempts < max_attempts:
            # Scroll to bottom
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1.5)  # Longer wait for content to load
            
            # Get current state
            current_height = await self.page.evaluate('document.body.scrollHeight')
            current_song_count = await self.page.locator('a[href*="/songs/"]').count()
            
            # Check if anything changed
            if current_height == previous_height and current_song_count == previous_song_count:
                no_change_count += 1
                if no_change_count >= 3:
                    logger.info(f"No more content loading after {scroll_attempts} scrolls")
                    logger.info(f"Final song count: {current_song_count}")
                    break
            else:
                no_change_count = 0
                if current_song_count > previous_song_count:
                    logger.info(f"Loaded {current_song_count} songs (height: {current_height})")
                previous_height = current_height
                previous_song_count = current_song_count
            
            scroll_attempts += 1
        
        # Scroll back to top
        await self.page.evaluate('window.scrollTo(0, 0)')
        await asyncio.sleep(1)
        
        logger.info(f"Scrolling complete. Total songs visible: {previous_song_count}")
        
    async def extract_songs(self) -> List[Dict]:
        """Extract all songs from the page."""
        logger.info("Extracting songs from page...")
        
        # Try to extract songs using JavaScript
        songs = await self.page.evaluate('''() => {
            const songs = [];
            
            // Try multiple selectors
            const selectors = [
                'a[href*="/songs/"]',
                '[data-testid="song-item"]',
                '.song-item',
                '[class*="Song"]'
            ];
            
            let elements = [];
            for (const selector of selectors) {
                elements = document.querySelectorAll(selector);
                if (elements.length > 0) break;
            }
            
            console.log(`Found ${elements.length} potential song elements`);
            
            elements.forEach((el, index) => {
                try {
                    // Try to extract song URL
                    let url = null;
                    if (el.tagName === 'A') {
                        url = el.href;
                    } else {
                        const link = el.querySelector('a[href*="/songs/"]');
                        url = link ? link.href : null;
                    }
                    
                    if (!url || !url.includes('/songs/')) return;
                    
                    // Extract song ID from URL
                    const songId = url.split('/songs/')[1]?.split('?')[0]?.split('/')[0];
                    if (!songId) return;
                    
                    // Try to extract title
                    let title = null;
                    const titleSelectors = [
                        '.song-title',
                        '[class*="title"]',
                        'h3',
                        'h4',
                        '[class*="Title"]'
                    ];
                    
                    for (const sel of titleSelectors) {
                        const titleEl = el.querySelector(sel);
                        if (titleEl && titleEl.textContent.trim()) {
                            title = titleEl.textContent.trim();
                            break;
                        }
                    }
                    
                    // If no title found, use text content
                    if (!title) {
                        title = el.textContent.trim().split('\\n')[0] || `Song ${index + 1}`;
                    }
                    
                    // Try to extract duration
                    let duration = null;
                    const durationEl = el.querySelector('[class*="duration"], [class*="Duration"], time');
                    if (durationEl) {
                        duration = durationEl.textContent.trim();
                    }
                    
                    songs.push({
                        id: songId,
                        title: title,
                        url: url,
                        duration: duration,
                        index: index
                    });
                    
                } catch (err) {
                    console.error('Error extracting song:', err);
                }
            });
            
            return songs;
        }''')
        
        logger.info(f"Extracted {len(songs)} songs")
        
        # Remove duplicates based on ID
        unique_songs = {}
        for song in songs:
            if song['id'] not in unique_songs:
                unique_songs[song['id']] = song
        
        songs = list(unique_songs.values())
        logger.info(f"After deduplication: {len(songs)} unique songs")
        
        return songs
    
    async def extract_folders(self) -> List[Dict]:
        """Extract folder structure with hierarchy."""
        logger.info("Attempting to extract folder structure...")
        
        folders = await self.page.evaluate('''() => {
            const folders = [];
            const seenNames = new Set();
            
            // Try to find folder elements in tree structure
            const folderSelectors = [
                '[role="treeitem"]',
                '[data-testid="folder"]',
                'li[class*="folder"]',
                'div[class*="folder"]',
                '.folder',
                '[class*="Folder"]'
            ];
            
            let folderElements = [];
            for (const selector of folderSelectors) {
                folderElements = document.querySelectorAll(selector);
                if (folderElements.length > 0) {
                    console.log(`Found ${folderElements.length} folders with selector: ${selector}`);
                    break;
                }
            }
            
            folderElements.forEach((el, index) => {
                try {
                    // Try to get folder name from various elements
                    let name = null;
                    
                    // Try text content of specific child elements
                    const nameSelectors = [
                        'span',
                        'div',
                        'button',
                        '[class*="name"]',
                        '[class*="title"]'
                    ];
                    
                    for (const sel of nameSelectors) {
                        const nameEl = el.querySelector(sel);
                        if (nameEl) {
                            const text = nameEl.textContent.trim();
                            if (text && text.length > 0 && text.length < 100) {
                                name = text;
                                break;
                            }
                        }
                    }
                    
                    // Fallback to element text
                    if (!name) {
                        name = el.textContent.trim().split('\\n')[0];
                    }
                    
                    // Clean up name
                    if (name) {
                        name = name.replace(/[\\n\\r\\t]+/g, ' ').trim();
                        
                        // Skip if too short or duplicate
                        if (name.length < 1 || name.length > 200 || seenNames.has(name)) {
                            return;
                        }
                        
                        seenNames.add(name);
                        
                        // Try to determine hierarchy level
                        let level = 0;
                        let parent = el.parentElement;
                        while (parent && level < 10) {
                            if (parent.matches('[role="treeitem"], li, [class*="folder"]')) {
                                level++;
                            }
                            parent = parent.parentElement;
                        }
                        
                        folders.push({
                            id: `folder_${index}`,
                            name: name,
                            path: `/${name}`,
                            level: level
                        });
                    }
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
        logger.info("Creating export data structure...")
        
        # Convert songs to expected format
        formatted_songs = []
        for song in songs:
            formatted_song = {
                'id': song['id'],
                'title': song['title'],
                'url': song['url'],
                'folderId': None,  # We don't have folder mapping yet
                'folderPath': '/',
                'createdAt': datetime.now().isoformat(),
                'duration': self._parse_duration(song.get('duration')),
                'tags': [],
                'isPublic': False
            }
            formatted_songs.append(formatted_song)
        
        # Create export structure
        export_data = {
            'exportDate': datetime.now().isoformat(),
            'totalSongs': len(formatted_songs),
            'folders': folders,
            'songs': formatted_songs
        }
        
        return export_data
    
    def _parse_duration(self, duration_str: Optional[str]) -> int:
        """Parse duration string to seconds."""
        if not duration_str:
            return 0
        
        try:
            # Try to parse MM:SS format
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
    
    async def save_export(self, export_data: Dict, output_file: str):
        """Save export data to JSON file."""
        logger.info(f"Saving export to {output_file}...")
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Export saved successfully!")
        logger.info(f"Total songs: {export_data['totalSongs']}")
        logger.info(f"Total folders: {len(export_data['folders'])}")
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up...")
        
        if self.context:
            await self.context.close()
        
        if self.playwright:
            await self.playwright.stop()
        
        logger.info("Cleanup complete")


async def main():
    """Main scraping workflow."""
    print("=" * 60)
    print("UDIO LIBRARY SCRAPER")
    print("=" * 60)
    print()
    
    # Configuration
    output_file = "udio_library_export.json"
    headless = False  # Set to True to hide browser
    
    scraper = UdioLibraryScraper(headless=headless)
    
    try:
        # Initialize
        await scraper.initialize()
        
        # Navigate to library
        await scraper.navigate_to_library()
        
        # Wait for content
        await scraper.wait_for_content()
        
        # Expand all folders first
        await scraper.expand_all_folders()
        
        # Scroll to load all songs
        await scraper.scroll_to_load_all()
        
        # Extract data
        songs = await scraper.extract_songs()
        folders = await scraper.extract_folders()
        
        if not songs:
            logger.error("No songs found! Check if you're logged in and on the library page.")
            print()
            print("Troubleshooting:")
            print("1. Make sure you're logged into Udio")
            print("2. Navigate to https://www.udio.com/library")
            print("3. Make sure songs are visible on the page")
            print("4. Try running the script again")
            return
        
        # Create export
        export_data = scraper.create_export(songs, folders)
        
        # Save export
        await scraper.save_export(export_data, output_file)
        
        print()
        print("=" * 60)
        print("SCRAPING COMPLETE!")
        print("=" * 60)
        print()
        print(f"✅ Exported {len(songs)} songs")
        print(f"✅ Exported {len(folders)} folders")
        print(f"✅ Saved to: {output_file}")
        print()
        print("Next steps:")
        print(f"1. Import: python -m udio_downloader import-metadata --json-file {output_file}")
        print(f"2. Status: python -m udio_downloader status")
        print(f"3. Download: python -m udio_downloader download")
        
    except KeyboardInterrupt:
        print()
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await scraper.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
