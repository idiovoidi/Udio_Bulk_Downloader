"""
Base classes for hierarchical structure mapping.
"""

from abc import ABC, abstractmethod


class BaseMapper(ABC):
    """Base class for mapping hierarchical structures"""
    
    def __init__(self, driver, logger=None):
        self.driver = driver
        self.logger = logger
        self.cache = {}
        self.total_items = 0
    
    @abstractmethod
    def find_container(self):
        """Find the main container element"""
        pass
    
    @abstractmethod
    def get_top_level_items(self, container):
        """Get top-level items from container"""
        pass
    
    @abstractmethod
    def process_item(self, item, parent_path=[]):
        """Process a single item (folder, category, etc.)"""
        pass
    
    def map_structure(self):
        """Map entire structure"""
        container = self.find_container()
        items = self.get_top_level_items(container)
        
        structure = {
            'items': [],
            'totalItems': len(items),
            'metadata': {}
        }
        
        for i, item in enumerate(items, 1):
            print(f"\n[{i}/{len(items)}] Processing item...")
            item_data = self.process_item(item, [])
            
            if item_data:
                structure['items'].append(item_data)
                self._print_item_summary(item_data)
        
        structure['metadata']['totalProcessed'] = self.total_items
        
        return structure
    
    def _print_item_summary(self, item_data):
        """Print summary of processed item"""
        print(f"  ✓ {item_data.get('name', 'Unknown')}")
    
    def clear_cache(self):
        """Clear mapper cache"""
        self.cache.clear()
