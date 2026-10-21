"""
Udio-specific folder structure mapper (Playwright async version).
"""

import asyncio
from .extractors_async import UdioSongExtractor


class UdioFolderMapper:
    """Map Udio library folder structure using Playwright"""
    
    def __init__(self, page, logger=None):
        self.page = page
        self.logger = logger
        self.song_extractor = UdioSongExtractor(page, logger)
        self.cache = {}
        self.total_items = 0
    
    async def find_container(self):
        """Find the Udio folder tree container"""
        if self.logger:
            self.logger.info("Looking for folder tree...")
        else:
            print("\nLooking for folder tree...")
        
        try:
            container = await self.page.wait_for_selector(
                '[role="tree"][aria-label="Folder structure"]',
                timeout=10000
            )
            if self.logger:
                self.logger.success("Found folder tree container")
            else:
                print("✓ Found folder tree container")
            return container
        except:
            raise Exception("Folder tree not found. Please open the folder tree panel in Udio.")
    
    async def get_top_level_items(self, container):
        """Get top-level folders"""
        items = await container.query_selector_all(':scope > *')
        if self.logger:
            self.logger.success(f"Found {len(items)} top-level folders")
        else:
            print(f"✓ Found {len(items)} top-level folders")
        return items
    
    async def get_root_songs(self):
        """Extract songs at root level"""
        if self.logger:
            self.logger.info("Checking for root-level songs...")
        else:
            print("\nChecking for root-level songs...")
        
        songs = await self.song_extractor.extract(folder_path=None)
        
        if songs:
            if self.logger:
                self.logger.success(f"Found {len(songs)} root-level songs")
            else:
                print(f"✓ Found {len(songs)} root-level songs")
            self.total_items += len(songs)
        
        return songs
    
    async def process_item(self, item, parent_path=[]):
        """Process a folder item"""
        # Get folder name - try both selectors
        name_button = await item.query_selector('button[title]')
        if not name_button:
            # Try alternative selector for nested folders
            name_button = await item.query_selector('button span')
        
        if not name_button:
            return None
        
        # Get folder name from title attribute or text content
        folder_name = await name_button.get_attribute('title')
        if not folder_name:
            folder_name = await name_button.text_content()
            folder_name = folder_name.strip() if folder_name else None
        
        if not folder_name:
            return None
        
        current_path = parent_path + [folder_name]
        path_str = '/'.join(current_path)
        
        # Check cache
        if path_str in self.cache:
            if self.logger:
                self.logger.debug(f"Using cached folder: {path_str}")
            else:
                print(f"  [CACHED] {path_str}")
            return self.cache[path_str]
        
        # Check if folder has children (expand button)
        expand_button = await item.query_selector('button[aria-label="Expand"]')
        has_expand_button = expand_button is not None
        
        # Also check for nested folder divs (alternative structure)
        nested_folders = await item.query_selector_all('.group\\/folder')
        has_nested_folders = len(nested_folders) > 0
        
        has_children = has_expand_button or has_nested_folders
        is_expanded = await item.get_attribute('aria-expanded') == 'true'
        
        folder_data = {
            'name': folder_name,
            'path': current_path,
            'hasChildren': has_children,
            'isLeaf': not has_children,
            'subfolders': [],
            'songCount': 0
        }
        
        if has_children:
            if has_expand_button:
                await self._process_parent_folder(item, expand_button, is_expanded, folder_data, current_path)
            else:
                # Process nested folders directly
                await self._process_nested_folders(item, folder_data, current_path)
        else:
            await self._process_leaf_folder(name_button, folder_data, current_path)
        
        # Cache result
        self.cache[path_str] = folder_data
        return folder_data
    
    async def _process_parent_folder(self, item, expand_button, is_expanded, folder_data, current_path):
        """Process a parent folder with subfolders"""
        # Expand if needed
        if not is_expanded:
            await expand_button.click()
            await asyncio.sleep(1.2)
        
        await asyncio.sleep(0.3)
        
        # Find child folders
        nested_buttons = await item.query_selector_all('[role="button"]')
        # Filter out the parent item itself
        children = [btn for btn in nested_buttons if btn != item]
        
        # Process each child
        for child in children:
            child_data = await self.process_item(child, current_path)
            if child_data:
                folder_data['subfolders'].append(child_data)
                folder_data['songCount'] += child_data['songCount']
        
        # Collapse if it wasn't expanded
        if not is_expanded:
            await expand_button.click()
            await asyncio.sleep(0.2)
    
    async def _process_nested_folders(self, item, folder_data, current_path):
        """Process nested folders without expand button"""
        # Find all nested folder divs
        nested_folders = await item.query_selector_all('.group\\/folder')
        
        for nested_folder in nested_folders:
            # Each nested folder is a separate item to process
            child_data = await self.process_item(nested_folder, current_path)
            if child_data:
                folder_data['subfolders'].append(child_data)
                folder_data['songCount'] += child_data['songCount']
    
    async def _process_leaf_folder(self, name_button, folder_data, current_path):
        """Process a leaf folder (no subfolders)"""
        # Click to view songs
        await name_button.click()
        await asyncio.sleep(2.5)
        
        # Extract songs
        songs = await self.song_extractor.extract(folder_path=current_path)
        
        # Add to folder data
        folder_data['songs'] = songs
        folder_data['songCount'] = len(songs)
        self.total_items += len(songs)
    
    async def map_structure(self):
        """Map entire Udio folder structure"""
        print("\n" + "="*60)
        print("STARTING UDIO FOLDER TREE MAPPING")
        print("="*60)
        
        # Find container
        container = await self.find_container()
        
        # Get top-level items
        items = await self.get_top_level_items(container)
        
        # Extract root songs
        root_songs = await self.get_root_songs()
        
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
            folder_data = await self.process_item(item, [])
            
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
