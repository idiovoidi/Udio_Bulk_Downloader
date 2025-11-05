"""
Udio-specific folder structure mapper.
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper.core import BaseMapper
from .extractors import UdioSongExtractor


class UdioFolderMapper(BaseMapper):
    """Map Udio library folder structure"""
    
    def __init__(self, driver, logger=None):
        super().__init__(driver, logger)
        self.song_extractor = UdioSongExtractor(driver, logger)
    
    def find_container(self):
        """Find the Udio folder tree container"""
        if self.logger:
            self.logger.info("Looking for folder tree...")
        else:
            print("\nLooking for folder tree...")
        
        try:
            container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '[role="tree"][aria-label="Folder structure"]')
                )
            )
            if self.logger:
                self.logger.success("Found folder tree container")
            else:
                print("✓ Found folder tree container")
            return container
        except:
            raise Exception("Folder tree not found. Please open the folder tree panel in Udio.")
    
    def get_top_level_items(self, container):
        """Get top-level folders"""
        items = container.find_elements(By.XPATH, './child::*')
        if self.logger:
            self.logger.success(f"Found {len(items)} top-level folders")
        else:
            print(f"✓ Found {len(items)} top-level folders")
        return items
    
    def get_root_songs(self):
        """Extract songs at root level"""
        if self.logger:
            self.logger.info("Checking for root-level songs...")
        else:
            print("\nChecking for root-level songs...")
        
        songs = self.song_extractor.extract(folder_path=None)
        
        if songs:
            if self.logger:
                self.logger.success(f"Found {len(songs)} root-level songs")
            else:
                print(f"✓ Found {len(songs)} root-level songs")
            self.total_items += len(songs)
        
        return songs
    
    def process_item(self, item, parent_path=[]):
        """Process a folder item"""
        # Get folder name
        name_button = item.find_element(By.CSS_SELECTOR, 'button[title]')
        folder_name = name_button.get_attribute('title')
        current_path = parent_path + [folder_name]
        path_str = '/'.join(current_path)
        
        # Check cache
        if path_str in self.cache:
            if self.logger:
                self.logger.debug(f"Using cached folder: {path_str}")
            else:
                print(f"  [CACHED] {path_str}")
            return self.cache[path_str]
        
        # Check if folder has children
        try:
            expand_button = item.find_element(By.CSS_SELECTOR, 'button[aria-label="Expand"]')
            has_children = True
        except:
            has_children = False
            expand_button = None
        
        is_expanded = item.get_attribute('aria-expanded') == 'true'
        
        folder_data = {
            'name': folder_name,
            'path': current_path,
            'hasChildren': has_children,
            'isLeaf': not has_children,
            'subfolders': [],
            'songCount': 0
        }
        
        if has_children:
            self._process_parent_folder(item, expand_button, is_expanded, folder_data, current_path)
        else:
            self._process_leaf_folder(name_button, folder_data, current_path)
        
        # Cache result
        self.cache[path_str] = folder_data
        return folder_data
    
    def _process_parent_folder(self, item, expand_button, is_expanded, folder_data, current_path):
        """Process a parent folder with subfolders"""
        # Expand if needed
        if not is_expanded:
            expand_button.click()
            time.sleep(1.2)
        
        time.sleep(0.3)
        
        # Find child folders
        nested_buttons = item.find_elements(By.CSS_SELECTOR, '[role="button"]')
        children = [btn for btn in nested_buttons if btn != item]
        
        # Process each child
        for child in children:
            child_data = self.process_item(child, current_path)
            if child_data:
                folder_data['subfolders'].append(child_data)
                folder_data['songCount'] += child_data['songCount']
        
        # Collapse if it wasn't expanded
        if not is_expanded:
            expand_button.click()
            time.sleep(0.2)
    
    def _process_leaf_folder(self, name_button, folder_data, current_path):
        """Process a leaf folder (no subfolders)"""
        # Click to view songs
        name_button.click()
        time.sleep(2.5)
        
        # Extract songs
        songs = self.song_extractor.extract(folder_path=current_path)
        
        # Add to folder data
        folder_data['songs'] = songs
        folder_data['songCount'] = len(songs)
        self.total_items += len(songs)
    
    def map_structure(self):
        """Map entire Udio folder structure"""
        print("\n" + "="*60)
        print("STARTING UDIO FOLDER TREE MAPPING")
        print("="*60)
        
        # Find container
        container = self.find_container()
        
        # Get top-level items
        items = self.get_top_level_items(container)
        
        # Extract root songs
        root_songs = self.get_root_songs()
        
        # Build structure
        structure = {
            'folders': [],
            'rootSongs': root_songs,
            'totalFolders': len(items),
            'totalSongs': self.total_items
        }
        
        # Process each folder
        for i, item in enumerate(items, 1):
            print(f"\n[{i}/{len(items)}] Processing folder...")
            folder_data = self.process_item(item, [])
            
            if folder_data:
                structure['folders'].append(folder_data)
                print(f"  ✓ {folder_data['name']}")
                print(f"    Songs: {folder_data['songCount']}")
                print(f"    Subfolders: {len(folder_data['subfolders'])}")
        
        print("\n" + "="*60)
        print("MAPPING COMPLETE!")
        print("="*60)
        print(f"Total folders: {len(items)}")
        print(f"Total songs: {self.total_items}")
        print(f"Root songs: {len(root_songs)}")
        
        return structure
    
    def _print_item_summary(self, item_data):
        """Print folder summary"""
        print(f"  ✓ {item_data['name']} ({item_data['songCount']} songs)")
