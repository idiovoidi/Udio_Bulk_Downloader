"""
Base classes for content extraction.
"""

from abc import ABC, abstractmethod


class BaseExtractor(ABC):
    """Base class for content extractors"""
    
    def __init__(self, driver, logger=None):
        self.driver = driver
        self.logger = logger
        self.cache = {}
    
    @abstractmethod
    def extract(self, context=None):
        """Extract content from current page/view"""
        pass
    
    def clear_cache(self):
        """Clear extraction cache"""
        self.cache.clear()
    
    def get_cache_size(self):
        """Get number of cached items"""
        return len(self.cache)


class ScrollableExtractor(BaseExtractor):
    """Base class for extractors that need scrolling"""
    
    def __init__(self, driver, logger=None, max_attempts=50, scroll_amount=1000):
        super().__init__(driver, logger)
        self.max_attempts = max_attempts
        self.scroll_amount = scroll_amount
    
    def get_scroll_container(self):
        """Find the scrollable container"""
        return self.driver.execute_script("""
            return document.querySelector('[class*="overflow-y-auto"]') || 
                   document.querySelector('[class*="overflow-auto"]') ||
                   document.documentElement;
        """)
    
    def scroll_to_bottom(self, container, callback, wait_time=1.0):
        """
        Scroll container to bottom, calling callback after each scroll.
        Returns when no new content is found.
        """
        attempts = 0
        previous_result = None
        no_change_count = 0
        
        while attempts < self.max_attempts:
            # Get current state via callback
            current_result = callback()
            
            # Check if anything changed
            if current_result == previous_result:
                no_change_count += 1
            else:
                no_change_count = 0
            
            # Stop if no changes for 5 attempts
            if no_change_count >= 5:
                break
            
            previous_result = current_result
            
            # Scroll down
            self.driver.execute_script(
                f"arguments[0].scrollBy(0, {self.scroll_amount});", 
                container
            )
            
            # Wait for content to load
            import time
            time.sleep(wait_time)
            
            attempts += 1
        
        # Scroll back to top
        self.driver.execute_script("arguments[0].scrollTo(0, 0);", container)
        
        return attempts
