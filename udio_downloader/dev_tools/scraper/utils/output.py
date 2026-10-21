"""
Output formatting and file saving utilities.
"""

import json
from pathlib import Path


class OutputFormatter:
    """Format and save scraping results"""
    
    @staticmethod
    def save_json(data, filepath, indent=2):
        """Save data to JSON file"""
        # Ensure filepath is a Path object
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        print(f"\n✓ Saved to {filepath}")
        return filepath
    
    @staticmethod
    def print_tree(structure, root_label="ROOT"):
        """Print hierarchical tree structure"""
        print("\n" + "="*60)
        print("FOLDER TREE")
        print("="*60)
        
        # Print root items if present
        if 'rootSongs' in structure and structure['rootSongs']:
            print(f"\n📁 {root_label} ({len(structure['rootSongs'])} songs)")
        
        # Print folders
        for folder in structure.get('folders', []):
            OutputFormatter._print_folder(folder, indent=0)
    
    @staticmethod
    def _print_folder(folder, indent=0):
        """Recursively print folder structure"""
        prefix = "  " * indent
        icon = "📂" if folder.get('hasChildren') else "📁"
        song_count = folder.get('songCount', 0)
        
        print(f"{prefix}{icon} {folder['name']} ({song_count} songs)")
        
        # Print subfolders
        for subfolder in folder.get('subfolders', []):
            OutputFormatter._print_folder(subfolder, indent + 1)
    
    @staticmethod
    def print_summary(structure):
        """Print summary statistics"""
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        total_folders = structure.get('totalFolders', 0)
        total_songs = structure.get('totalSongs', 0)
        root_songs = len(structure.get('rootSongs', []))
        
        print(f"Total folders: {total_folders}")
        print(f"Total songs: {total_songs}")
        print(f"Root songs: {root_songs}")
