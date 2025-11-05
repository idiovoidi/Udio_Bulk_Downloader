"""
Udio-specific content extractors (Playwright async version).
"""

import asyncio
import re


class UdioSongExtractor:
    """Extract songs from Udio library views using Playwright"""
    
    def __init__(self, page, logger=None):
        self.page = page
        self.logger = logger
        self.cache = {}
        self.max_attempts = 50
    
    async def extract(self, folder_path=None):
        """Extract songs from current view"""
        cache_key = '/'.join(folder_path) if folder_path else 'root'
        
        # Check cache
        if cache_key in self.cache:
            if self.logger:
                self.logger.debug(f"Using cached songs for: {cache_key}")
            else:
                print(f"  [CACHED] Songs for: {cache_key}")
            return self.cache[cache_key]
        
        await asyncio.sleep(2)  # Wait for initial load
        
        songs = []
        seen_urls = set()
        
        # Get scroll container
        scroll_container = await self.page.evaluate("""
            () => {
                return document.querySelector('[class*="overflow-y-auto"]') || 
                       document.querySelector('[class*="overflow-auto"]') ||
                       document.documentElement;
            }
        """)
        
        attempts = 0
        previous_count = 0
        no_new_count = 0
        
        while attempts < self.max_attempts:
            # Extract from current view
            current_songs = await self._extract_from_current_view()
            
            # Add new songs
            for song in current_songs:
                if song['url'] not in seen_urls:
                    seen_urls.add(song['url'])
                    songs.append(song)
            
            current_count = len(songs)
            
            # Check if we found new songs
            if current_count == previous_count:
                no_new_count += 1
            else:
                no_new_count = 0
            
            # Stop if no new songs for 5 attempts
            if no_new_count >= 5:
                break
            
            previous_count = current_count
            
            # Scroll down
            scroll_amount = 2000 if current_count > 100 else 1000
            await self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            
            wait_time = 1.2 if current_count > 500 else 1.0
            await asyncio.sleep(wait_time)
            
            attempts += 1
        
        # Scroll back to top
        await self.page.evaluate("window.scrollTo(0, 0)")
        
        if self.logger:
            self.logger.info(f"Extracted {len(songs)} songs in {attempts} scroll attempts")
        else:
            print(f"  Extracted {len(songs)} songs in {attempts} scroll attempts")
        
        # Cache results
        self.cache[cache_key] = songs
        return songs
    
    async def _extract_from_current_view(self):
        """Extract songs from current viewport"""
        # Try table rows first
        song_rows = await self.page.query_selector_all('tr[class*="absolute"]')
        
        if not song_rows:
            # Fallback to links
            return await self._extract_from_links()
        else:
            return await self._extract_from_rows(song_rows)
    
    async def _extract_from_links(self):
        """Extract songs from link elements"""
        songs = []
        song_links = await self.page.query_selector_all('a[href*="/songs/"]')
        
        for link in song_links:
            try:
                url = await link.get_attribute('href')
                text = await link.text_content()
                if url:
                    songs.append({
                        'url': url,
                        'title': text or 'Unknown',
                        'id': self._extract_id_from_url(url)
                    })
            except:
                continue
        
        return songs
    
    async def _extract_from_rows(self, rows):
        """Extract songs from table rows"""
        songs = []
        
        for row in rows:
            try:
                song_data = await self._extract_song_data(row)
                if song_data:
                    songs.append(song_data)
            except:
                continue
        
        return songs
    
    async def _extract_song_data(self, element):
        """Extract detailed song data from element"""
        try:
            # URL and ID
            link = await element.query_selector('a[href*="/songs/"]')
            if not link:
                return None
            
            url = await link.get_attribute('href')
            
            # Title
            title_elem = await element.query_selector('h4')
            title = await title_elem.text_content() if title_elem else 'Unknown'
            
            # Duration
            duration = None
            text_nodes = await element.query_selector_all('.text-muted-foreground')
            for node in text_nodes:
                text = await node.text_content()
                text = text.strip()
                if ':' in text and len(text.split(':')) == 2:
                    duration = text
                    break
            
            # Image
            image_url = None
            try:
                img = await element.query_selector('img[alt]')
                if img:
                    image_url = await img.get_attribute('src')
            except:
                pass
            
            # Tags
            tags = []
            try:
                tag_links = await element.query_selector_all('a[href*="/tags/"]')
                for tag_link in tag_links:
                    tag_text = await tag_link.text_content()
                    tags.append(tag_text.strip())
            except:
                pass
            
            return {
                'url': url,
                'id': self._extract_id_from_url(url),
                'title': title.strip() if title else 'Unknown',
                'duration': duration,
                'imageUrl': image_url,
                'tags': tags
            }
        except:
            return None
    
    def _extract_id_from_url(self, url):
        """Extract song ID from URL"""
        match = re.search(r'/songs/([^/?]+)', url)
        return match.group(1) if match else None
    
    def clear_cache(self):
        """Clear extraction cache"""
        self.cache.clear()
    
    def get_cache_size(self):
        """Get number of cached items"""
        return len(self.cache)
