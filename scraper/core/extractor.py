"""
Base classes for content extraction.
"""

from abc import ABC, abstractmethod


class BaseExtractor(ABC):
    """Base class for content extractors (async)"""
    
    def __init__(self, page, logger=None):
        self.page = page
        self.logger = logger
        self.cache = {}
    
    @abstractmethod
    async def extract(self, context=None):
        """Extract content from current page/view"""
        pass
    
    def clear_cache(self):
        """Clear extraction cache"""
        self.cache.clear()
    
    def get_cache_size(self):
        """Get number of cached items"""
        return len(self.cache)
