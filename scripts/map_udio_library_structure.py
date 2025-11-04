#!/usr/bin/env python3
"""
Map Udio Library Structure - Analyze folder/song structure while logged in.
Uses Chrome DevTools Protocol to inspect the authenticated library page.
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
import websocket
import threading


class UdioLibraryMapper:
    """Map the folder and song structure of Udio library."""
    
    def __init__(self, debug_port=9222):
        self.debug_port = debug_port
        self.base_url = f"http://localhost:{debug_port}"
        self.output_dir = Path("udio_library_structure")
        self.output_dir.mkdir(exist_ok=True)
        self.ws = None
        self.message_id = 0
        self.responses = {}
    
    def get_tabs(self):
        """Get all open tabs."""
        try:
            response = requests.get(f"{self.base_url}/json", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Error getting tabs: {e}")
            return None
    
    def find_library_tab(self, tabs):
        """Find the Udio library tab."""
        for tab in tabs:
            url = tab.get('url', '').lower()
            if 'udio.com/library' in url and 'login' not in url:
                return tab
        return None
    
    def send_cdp_command(self, ws_url, method, params=None):
        """Send a Chrome DevTools Protocol command via WebSocket."""
        try:
            import websocket
            
            ws = websocket.create_connection(ws_url, timeout=10)
            
            self.message_id += 1
            message = {
                "id": self.message_id,
                "method": method,
                "params": params or {}
            }
            
            ws.send(json.dumps(message))
            
            # Wait for response
            response = ws.recv()
            result = json.loads(response)
            
            ws.close()
            
            return result
            
        except Exception as e:
            print(f"❌ Error sending CDP command: {e}")
            return None
    
    def get_page_dom(self, ws_url):
        """Get the DOM structure of the page."""
        print("🔍 Getting page DOM structure...")
        
        try:
            # Enable DOM domain
            self.send_cdp_command(ws_url, "DOM.enable")
            
            # Get document
            result = self.send_cdp_command(ws_url, "DOM.getDocument", {"depth": -1})
            
            if result and 'result' in result:
                print("   ✅ DOM structure retrieved")
                return result['result']
            else:
                print("   ❌ Failed to get DOM structure")
                return None
                
        except Exception as e:
            print(f"   ❌ Error getting DOM: {e}")
            return None
    
    def execute_javascript(self, ws_url, script):
        """Execute JavaScript on the page."""
        try:
            result = self.send_cdp_command(ws_url, "Runtime.evaluate", {
                "expression": script,
                "returnByValue": True
            })
            
            if result and 'result' in result and 'result' in result['result']:
                return result['result']['result'].get('value')
            return None
            
        except Exception as e:
            print(f"❌ Error executing JavaScript: {e}")
            return None
    
    def analyze_library_structure(self, tab):
        """Analyze the library page structure."""
        print(f"🎵 Analyzing Udio Library Structure")
        print(f"   URL: {tab.get('url')}")
        print(f"   Title: {tab.get('title')}")
        
        ws_url = tab.get('webSocketDebuggerUrl')
        if not ws_url:
            print("   ❌ No WebSocket URL available")
            return None
        
        analysis = {
            'tab_info': {
                'url': tab.get('url'),
                'title': tab.get('title'),
                'id': tab.get('id')
            },
            'timestamp': datetime.now().isoformat(),
            'structure': {}
        }
        
        # JavaScript to analyze the page structure
        analysis_script = """
        (function() {
            const result = {
                folders: [],
                songs: [],
                navigation: [],
                controls: [],
                page_structure: {}
            };
            
            // Look for folder elements
            const folderSelectors = [
                '[data-testid*="folder"]',
                '[class*="folder"]',
                '[aria-label*="folder"]',
                '.folder',
                '[role="treeitem"]'
            ];
            
            folderSelectors.forEach(selector => {
                try {
                    const elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        result.folders.push({
                            selector: selector,
                            count: elements.length,
                            sample: Array.from(elements).slice(0, 3).map(el => ({
                                text: el.textContent.trim().substring(0, 100),
                                classes: el.className,
                                id: el.id,
                                attributes: Array.from(el.attributes).map(attr => ({
                                    name: attr.name,
                                    value: attr.value.substring(0, 50)
                                }))
                            }))
                        });
                    }
                } catch(e) {}
            });
            
            // Look for song/track elements
            const songSelectors = [
                '[data-testid*="song"]',
                '[data-testid*="track"]',
                '[data-testid*="audio"]',
                '[class*="song"]',
                '[class*="track"]',
                '[class*="card"]',
                'article',
                '[role="listitem"]'
            ];
            
            songSelectors.forEach(selector => {
                try {
                    const elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        result.songs.push({
                            selector: selector,
                            count: elements.length,
                            sample: Array.from(elements).slice(0, 3).map(el => ({
                                text: el.textContent.trim().substring(0, 100),
                                classes: el.className,
                                id: el.id,
                                hasAudio: el.querySelector('audio') !== null,
                                hasPlayButton: el.querySelector('[aria-label*="play"], [aria-label*="Play"]') !== null,
                                hasDownloadButton: el.querySelector('[aria-label*="download"], [aria-label*="Download"]') !== null
                            }))
                        });
                    }
                } catch(e) {}
            });
            
            // Look for navigation elements
            const navSelectors = [
                'nav',
                '[role="navigation"]',
                '[class*="nav"]',
                '[class*="menu"]',
                '[class*="sidebar"]'
            ];
            
            navSelectors.forEach(selector => {
                try {
                    const elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        result.navigation.push({
                            selector: selector,
                            count: elements.length,
                            sample: Array.from(elements).slice(0, 2).map(el => ({
                                text: el.textContent.trim().substring(0, 200),
                                classes: el.className
                            }))
                        });
                    }
                } catch(e) {}
            });
            
            // Look for control elements
            const controlSelectors = [
                'button',
                '[role="button"]',
                'a[href]',
                'input',
                'select'
            ];
            
            controlSelectors.forEach(selector => {
                try {
                    const elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        result.controls.push({
                            selector: selector,
                            count: elements.length
                        });
                    }
                } catch(e) {}
            });
            
            // Get page structure overview
            result.page_structure = {
                title: document.title,
                url: window.location.href,
                bodyClasses: document.body.className,
                mainContainers: Array.from(document.querySelectorAll('main, [role="main"], .container, .content')).map(el => ({
                    tag: el.tagName,
                    classes: el.className,
                    id: el.id
                })),
                gridLayouts: document.querySelectorAll('[class*="grid"]').length,
                listLayouts: document.querySelectorAll('ul, ol, [role="list"]').length
            };
            
            // Look for specific Udio elements
            result.udio_specific = {
                hasUserMenu: document.querySelector('[data-testid*="user"], [aria-label*="user"], .user-menu') !== null,
                hasLibraryView: document.querySelector('[data-testid*="library"], [class*="library"]') !== null,
                hasFolderTree: document.querySelector('[role="tree"], [role="treegrid"]') !== null,
                hasAudioPlayer: document.querySelector('audio, video, [class*="player"]') !== null
            };
            
            return result;
        })();
        """
        
        print("   🔍 Executing page analysis...")
        structure_data = self.execute_javascript(ws_url, analysis_script)
        
        if structure_data:
            analysis['structure'] = structure_data
            print("   ✅ Page structure analyzed")
            
            # Print summary
            if structure_data.get('folders'):
                print(f"\n   📁 Folder Elements Found:")
                for folder_info in structure_data['folders']:
                    print(f"      Selector: {folder_info['selector']}")
                    print(f"      Count: {folder_info['count']}")
                    if folder_info.get('sample'):
                        print(f"      Sample: {folder_info['sample'][0].get('text', 'N/A')[:50]}...")
            
            if structure_data.get('songs'):
                print(f"\n   🎵 Song/Track Elements Found:")
                for song_info in structure_data['songs']:
                    print(f"      Selector: {song_info['selector']}")
                    print(f"      Count: {song_info['count']}")
                    if song_info.get('sample'):
                        sample = song_info['sample'][0]
                        print(f"      Has Audio: {sample.get('hasAudio', False)}")
                        print(f"      Has Play Button: {sample.get('hasPlayButton', False)}")
                        print(f"      Has Download: {sample.get('hasDownloadButton', False)}")
            
            if structure_data.get('udio_specific'):
                print(f"\n   🎯 Udio-Specific Features:")
                udio_features = structure_data['udio_specific']
                print(f"      User Menu: {'✅' if udio_features.get('hasUserMenu') else '❌'}")
                print(f"      Library View: {'✅' if udio_features.get('hasLibraryView') else '❌'}")
                print(f"      Folder Tree: {'✅' if udio_features.get('hasFolderTree') else '❌'}")
                print(f"      Audio Player: {'✅' if udio_features.get('hasAudioPlayer') else '❌'}")
        else:
            print("   ❌ Failed to analyze page structure")
        
        return analysis
    
    def save_analysis(self, analysis, filename):
        """Save analysis to file."""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Analysis saved to: {filepath}")
    
    def map_library(self):
        """Map the Udio library structure."""
        print("🎵 Udio Library Structure Mapper")
        print("=" * 50)
        
        # Get tabs
        print("🔍 Looking for Udio library tab...")
        tabs = self.get_tabs()
        
        if not tabs:
            print("❌ Could not get Chrome tabs")
            print("💡 Make sure Chrome is running with --remote-debugging-port=9222")
            return False
        
        # Find library tab
        library_tab = self.find_library_tab(tabs)
        
        if not library_tab:
            print("❌ Udio library tab not found")
            print("💡 Make sure you have https://www.udio.com/library open")
            print("💡 And that you're logged in (not on login page)")
            
            # Show available tabs
            print(f"\n📋 Available tabs ({len(tabs)}):")
            for i, tab in enumerate(tabs, 1):
                url = tab.get('url', 'No URL')[:60]
                title = tab.get('title', 'No title')[:40]
                print(f"   {i}. {title} - {url}")
            
            return False
        
        print(f"✅ Found library tab: {library_tab.get('title')}")
        
        # Analyze the library structure
        analysis = self.analyze_library_structure(library_tab)
        
        if analysis:
            # Save analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"udio_library_structure_{timestamp}.json"
            self.save_analysis(analysis, filename)
            
            # Generate summary report
            self.generate_summary_report(analysis)
            
            return True
        else:
            print("❌ Failed to analyze library structure")
            return False
    
    def generate_summary_report(self, analysis):
        """Generate a human-readable summary report."""
        print("\n" + "=" * 50)
        print("UDIO LIBRARY STRUCTURE SUMMARY")
        print("=" * 50)
        
        structure = analysis.get('structure', {})
        
        # Folders
        folders = structure.get('folders', [])
        if folders:
            print(f"\n📁 FOLDERS ({len(folders)} selector types found):")
            for folder_info in folders:
                print(f"   • {folder_info['selector']}: {folder_info['count']} elements")
        else:
            print(f"\n📁 FOLDERS: None found")
        
        # Songs
        songs = structure.get('songs', [])
        if songs:
            print(f"\n🎵 SONGS/TRACKS ({len(songs)} selector types found):")
            for song_info in songs:
                print(f"   • {song_info['selector']}: {song_info['count']} elements")
        else:
            print(f"\n🎵 SONGS/TRACKS: None found")
        
        # Navigation
        navigation = structure.get('navigation', [])
        if navigation:
            print(f"\n🧭 NAVIGATION ({len(navigation)} elements found):")
            for nav_info in navigation:
                print(f"   • {nav_info['selector']}: {nav_info['count']} elements")
        
        # Controls
        controls = structure.get('controls', [])
        if controls:
            print(f"\n🎛️  CONTROLS:")
            for control_info in controls:
                print(f"   • {control_info['selector']}: {control_info['count']} elements")
        
        # Page structure
        page_structure = structure.get('page_structure', {})
        if page_structure:
            print(f"\n📄 PAGE STRUCTURE:")
            print(f"   • Main containers: {len(page_structure.get('mainContainers', []))}")
            print(f"   • Grid layouts: {page_structure.get('gridLayouts', 0)}")
            print(f"   • List layouts: {page_structure.get('listLayouts', 0)}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if folders:
            print(f"   ✅ Folder structure detected - use these selectors for navigation")
        if songs:
            print(f"   ✅ Song elements detected - use these selectors for scraping")
        if not folders and not songs:
            print(f"   ⚠️  No folder or song elements found")
            print(f"   💡 You may need to:")
            print(f"      1. Ensure you're logged in")
            print(f"      2. Wait for page to fully load")
            print(f"      3. Check if library has content")


def main():
    """Main function."""
    # Check if websocket-client is installed
    try:
        import websocket
    except ImportError:
        print("❌ websocket-client library not found")
        print("📦 Installing websocket-client...")
        import subprocess
        subprocess.run(["pip", "install", "websocket-client"], check=True)
        print("✅ websocket-client installed")
    
    mapper = UdioLibraryMapper()
    
    print("🎵 Udio Library Structure Mapper")
    print("This tool analyzes the folder and song structure")
    print("of your Udio library while you're logged in.")
    print()
    print("Prerequisites:")
    print("  1. Chrome running with --remote-debugging-port=9222")
    print("  2. Logged into Udio")
    print("  3. Library page open: https://www.udio.com/library")
    print()
    
    success = mapper.map_library()
    
    if success:
        print("\n✅ Library structure mapping complete!")
        print(f"📁 Results saved to: {mapper.output_dir}")
        print("\n" + "=" * 50)
        print("NEXT STEPS")
        print("=" * 50)
        print("\n1. Review the analysis files in the output directory")
        print("2. Use the identified selectors to build the download script")
        print("3. Run the download command to fetch all songs:")
        print("   python -m udio_downloader download --output ./downloads")
        print("\n💡 TIP: Check the JSON file for detailed selector information")
        print("💡 TIP: Use the Chrome extension for direct library access")
    else:
        print("\n❌ Library structure mapping failed")
        print("\n" + "=" * 50)
        print("TROUBLESHOOTING")
        print("=" * 50)
        print("\n1. Ensure Chrome is running with debugging enabled:")
        print("   chrome.exe --remote-debugging-port=9222")
        print("\n2. Make sure you're logged into Udio")
        print("\n3. Navigate to: https://www.udio.com/library")
        print("\n4. Wait for the page to fully load before running this script")


if __name__ == "__main__":
    main()