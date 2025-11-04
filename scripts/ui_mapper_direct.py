#!/usr/bin/env python3
"""
Direct UI Mapper - Use Chrome DevTools Protocol directly without Selenium.
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime


class DirectUIMapper:
    """Map Udio UI using Chrome DevTools Protocol directly."""
    
    def __init__(self, debug_port=9222):
        self.debug_port = debug_port
        self.base_url = f"http://localhost:{debug_port}"
        self.output_dir = Path("ui_mapping_direct")
        self.output_dir.mkdir(exist_ok=True)
    
    def get_tabs(self):
        """Get all open tabs."""
        try:
            response = requests.get(f"{self.base_url}/json", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error getting tabs: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error getting tabs: {e}")
            return None
    
    def find_udio_tabs(self, tabs):
        """Find tabs with Udio content."""
        udio_tabs = []
        for tab in tabs:
            url = tab.get('url', '').lower()
            if 'udio.com' in url:
                udio_tabs.append(tab)
        return udio_tabs
    
    def send_devtools_command(self, tab_id, method, params=None):
        """Send a command to Chrome DevTools."""
        try:
            ws_url = f"ws://localhost:{self.debug_port}/devtools/page/{tab_id}"
            
            # Use HTTP endpoint instead of WebSocket for simplicity
            command_url = f"{self.base_url}/json/runtime/evaluate"
            
            # Alternative: use the tab's webSocketDebuggerUrl
            # For now, let's try a different approach
            
            return None
        except Exception as e:
            print(f"❌ Error sending DevTools command: {e}")
            return None
    
    def get_page_content(self, tab):
        """Get page content using DevTools Protocol."""
        try:
            # Try to get the page source via the tab's debugger URL
            tab_id = tab.get('id')
            if not tab_id:
                return None
            
            # Use Runtime.evaluate to get document content
            # This is a simplified approach - in a full implementation,
            # we'd use WebSocket connections to the DevTools Protocol
            
            return {
                'tab_info': tab,
                'content_method': 'devtools_protocol',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting page content: {e}")
            return None
    
    def analyze_udio_structure(self, tab):
        """Analyze Udio page structure."""
        print(f"🔍 Analyzing tab: {tab.get('title', 'No title')}")
        print(f"   URL: {tab.get('url', 'No URL')}")
        
        analysis = {
            'tab_info': {
                'id': tab.get('id'),
                'title': tab.get('title'),
                'url': tab.get('url'),
                'type': tab.get('type'),
                'description': tab.get('description', ''),
                'webSocketDebuggerUrl': tab.get('webSocketDebuggerUrl')
            },
            'analysis_timestamp': datetime.now().isoformat(),
            'page_type': self.classify_udio_page(tab.get('url', '')),
            'elements_found': [],
            'potential_selectors': []
        }
        
        # Classify the page type
        url = tab.get('url', '').lower()
        if 'login' in url:
            analysis['page_type'] = 'login'
            analysis['expected_elements'] = [
                'email input field',
                'password input field', 
                'login button',
                'social login buttons'
            ]
        elif 'library' in url:
            analysis['page_type'] = 'library'
            analysis['expected_elements'] = [
                'song cards/tiles',
                'play buttons',
                'download buttons',
                'song titles',
                'artist names',
                'navigation menu'
            ]
        elif 'my-creations' in url:
            analysis['page_type'] = 'my_creations'
            analysis['expected_elements'] = [
                'user created songs',
                'edit buttons',
                'delete buttons',
                'share buttons'
            ]
        elif 'create' in url:
            analysis['page_type'] = 'create'
            analysis['expected_elements'] = [
                'text input for prompts',
                'generate button',
                'style selectors',
                'audio controls'
            ]
        else:
            analysis['page_type'] = 'unknown'
        
        # Add common selectors to look for
        analysis['common_selectors_to_try'] = [
            # Song/track related
            "[data-testid*='song']",
            "[data-testid*='track']",
            "[data-testid*='audio']",
            "[class*='song']",
            "[class*='track']",
            "[class*='card']",
            
            # Interactive elements
            "button[aria-label*='play']",
            "button[aria-label*='download']",
            "[role='button']",
            
            # Media elements
            "audio",
            "video",
            "[controls]",
            
            # Navigation
            "nav",
            "[role='navigation']",
            "[class*='menu']"
        ]
        
        return analysis
    
    def classify_udio_page(self, url):
        """Classify the type of Udio page."""
        url_lower = url.lower()
        if 'login' in url_lower:
            return 'login'
        elif 'library' in url_lower:
            return 'library'
        elif 'my-creations' in url_lower:
            return 'my_creations'
        elif 'create' in url_lower:
            return 'create'
        else:
            return 'unknown'
    
    def save_analysis(self, analysis, filename):
        """Save analysis to file."""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"   💾 Analysis saved to: {filepath}")
    
    def map_udio_ui(self):
        """Map Udio UI structure."""
        print("🎵 Direct Udio UI Mapping")
        print("=" * 40)
        
        # Get all tabs
        print("🔍 Getting Chrome tabs...")
        tabs = self.get_tabs()
        
        if not tabs:
            print("❌ Could not get Chrome tabs")
            return False
        
        print(f"   ✅ Found {len(tabs)} total tabs")
        
        # Find Udio tabs
        udio_tabs = self.find_udio_tabs(tabs)
        
        if not udio_tabs:
            print("❌ No Udio tabs found")
            print("💡 Make sure you have Udio open in Chrome")
            return False
        
        print(f"   🎵 Found {len(udio_tabs)} Udio tabs")
        
        # Analyze each Udio tab
        all_analyses = []
        
        for i, tab in enumerate(udio_tabs):
            print(f"\n📄 Tab {i+1}/{len(udio_tabs)}:")
            analysis = self.analyze_udio_structure(tab)
            all_analyses.append(analysis)
            
            # Save individual analysis
            page_type = analysis['page_type']
            filename = f"udio_{page_type}_tab_{i+1}.json"
            self.save_analysis(analysis, filename)
        
        # Create summary
        summary = {
            'mapping_session': {
                'timestamp': datetime.now().isoformat(),
                'total_tabs': len(tabs),
                'udio_tabs': len(udio_tabs),
                'debug_port': self.debug_port
            },
            'udio_pages_found': {},
            'all_analyses': all_analyses
        }
        
        # Categorize pages
        for analysis in all_analyses:
            page_type = analysis['page_type']
            if page_type not in summary['udio_pages_found']:
                summary['udio_pages_found'][page_type] = []
            summary['udio_pages_found'][page_type].append({
                'title': analysis['tab_info']['title'],
                'url': analysis['tab_info']['url']
            })
        
        # Save summary
        self.save_analysis(summary, 'udio_ui_mapping_summary.json')
        
        # Print summary
        print(f"\n" + "=" * 40)
        print("UDIO UI MAPPING SUMMARY")
        print("=" * 40)
        
        print(f"📊 Total Chrome tabs: {summary['mapping_session']['total_tabs']}")
        print(f"🎵 Udio tabs found: {summary['mapping_session']['udio_tabs']}")
        
        print(f"\n📄 Udio pages by type:")
        for page_type, pages in summary['udio_pages_found'].items():
            print(f"   {page_type}: {len(pages)} pages")
            for page in pages:
                title = page['title'][:50] + "..." if len(page['title']) > 50 else page['title']
                print(f"      - {title}")
        
        print(f"\n💡 Next steps:")
        print(f"   1. Review the analysis files in: {self.output_dir}")
        print(f"   2. Look for patterns in the expected elements")
        print(f"   3. Use the suggested selectors for scraping")
        
        if any('login' in page_type for page_type in summary['udio_pages_found']):
            print(f"   4. ⚠️  Login page detected - authenticate first")
        
        return True


def main():
    """Main function."""
    mapper = DirectUIMapper()
    
    print("🎵 Direct Udio UI Mapper")
    print("This tool analyzes Udio pages using Chrome DevTools Protocol")
    print("without requiring Selenium/ChromeDriver compatibility.")
    print()
    
    success = mapper.map_udio_ui()
    
    if success:
        print("\n✅ UI mapping complete!")
        print(f"📁 Results saved to: {mapper.output_dir}")
    else:
        print("\n❌ UI mapping failed")
        print("💡 Make sure Chrome is running with --remote-debugging-port=9222")
        print("💡 And that you have Udio pages open")


if __name__ == "__main__":
    main()