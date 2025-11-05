"""
Udio-specific content extractors.
"""

import time
from selenium.webdriver.common.by import By
from scraper.core import ScrollableExtractor


class UdioSongExtractor(ScrollableExtractor):
    """Extract songs from Udio library views"""
    
    def __init__(self, driver, logger=None):
        super().__init__(driver, logger, max_attempts=50)
    
    def extract(self, folder_path=None):
        """Extract songs from current view"""
        cache_key = '/'.join(folder_path) if folder_path else 'root'
        
        # Check cache
        if cache_key in self.cache:
            if self.logger:
                self.logger.debug(f"Using cached songs for: {cache_key}")
            else:
                print(f"  [CACHED] Songs for: {cache_key}")
            return self.cache[cache_key]
        
        time.sleep(2)  # Wait for initial load
        
        songs = []
        seen_urls = set()
        scroll_container = self.get_scroll_container()
        
        def extract_current_view():
            """Extract songs from current viewport"""
            # Try table rows first
            song_rows = self.driver.find_elements(By.CSS_SELECTOR, 'tr[class*="absolute"]')
            
            if not song_rows:
                # Fallback to links
                self._extract_from_links(songs, seen_urls)
            else:
                self._extract_from_rows(song_rows, songs, seen_urls)
            
            return len(songs)
        
        # Scroll and extract
        attempts = self.scroll_to_bottom(
            scroll_container, 
            extract_current_view,
            wait_time=1.2 if len(songs) > 500 else 1.0
        )
        
        if self.logger:
            self.logger.info(f"Extracted {len(songs)} songs in {attempts} scroll attempts")
        else:
            print(f"  Extracted {len(songs)} songs in {attempts} scroll attempts")
        
        # Cache results
        self.cache[cache_key] = songs
        return songs
    
    def _extract_from_links(self, songs, seen_urls):
        """Extract songs from link elements"""
        song_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/songs/"]')
        
        for link in song_links:
            try:
                url = link.get_attribute('href')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    songs.append({
                        'url': url,
                        'title': link.text or 'Unknown',
                        'id': self._extract_id_from_url(url)
                    })
            except:
                continue
    
    def _extract_from_rows(self, rows, songs, seen_urls):
        """Extract songs from table rows"""
        for row in rows:
            try:
                song_data = self._extract_song_data(row)
                if song_data and song_data['url'] not in seen_urls:
                    seen_urls.add(song_data['url'])
                    songs.append(song_data)
            except:
                continue
    
    def _extract_song_data(self, element):
        """Extract detailed song data from element"""
        try:
            # URL and ID
            link = element.find_element(By.CSS_SELECTOR, 'a[href*="/songs/"]')
            url = link.get_attribute('href')
            
            # Title
            title_elem = element.find_element(By.CSS_SELECTOR, 'h4')
            title = title_elem.text if title_elem else 'Unknown'
            
            # Duration
            duration = None
            text_nodes = element.find_elements(By.CSS_SELECTOR, '.text-muted-foreground')
            for node in text_nodes:
                text = node.text.strip()
                if ':' in text and len(text.split(':')) == 2:
                    duration = text
                    break
            
            # Image
            image_url = None
            try:
                img = element.find_element(By.CSS_SELECTOR, 'img[alt]')
                image_url = img.get_attribute('src')
            except:
                pass
            
            # Tags
            tags = []
            try:
                tag_links = element.find_elements(By.CSS_SELECTOR, 'a[href*="/tags/"]')
                tags = [tag.text.strip() for tag in tag_links]
            except:
                pass
            
            return {
                'url': url,
                'id': self._extract_id_from_url(url),
                'title': title,
                'duration': duration,
                'imageUrl': image_url,
                'tags': tags
            }
        except:
            return None
    
    def _extract_id_from_url(self, url):
        """Extract song ID from URL"""
        import re
        match = re.search(r'/songs/([^/?]+)', url)
        return match.group(1) if match else None
