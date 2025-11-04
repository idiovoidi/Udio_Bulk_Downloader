#!/usr/bin/env python3
"""
Udio UI Mapper - Attaches to existing Chrome browser session.
Maps out the DOM structure of Udio's web interface using an existing authenticated session.
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class UdioUIMapperAttach:
    """Maps the Udio user interface structure by attaching to existing Chrome session."""
    
    def __init__(self, debug_port: int = 9222):
        """
        Initialize the UI mapper to attach to existing Chrome.
        
        Args:
            debug_port: Chrome remote debugging port (default 9222)
        """
        self.debug_port = debug_port
        self.driver: Optional[webdriver.Chrome] = None
        self.output_dir = Path("ui_mapping_authenticated")
        self.output_dir.mkdir(exist_ok=True)
        
        # Udio URLs to map (focusing on authenticated pages)
        self.urls_to_map = {
            "library": "https://www.udio.com/library",
            "my_creations": "https://www.udio.com/my-creations",
            "create": "https://www.udio.com/create"
        }
    
    def setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver to attach to existing session."""
        options = ChromeOptions()
        
        # Connect to existing Chrome instance
        options.add_experimental_option("debuggerAddress", f"localhost:{self.debug_port}")
        
        # Don't add other options that might conflict with existing session
        driver = webdriver.Chrome(options=options)
        
        logger.info(f"Connected to existing Chrome session on port {self.debug_port}")
        return driver
    
    def extract_element_info(self, element) -> Dict[str, Any]:
        """
        Extract comprehensive information about a DOM element.
        
        Args:
            element: Selenium WebElement
            
        Returns:
            Dictionary with element information
        """
        try:
            info = {
                "tag": element.tag_name,
                "text": element.text.strip()[:200] if element.text else "",  # Limit text length
                "attributes": {},
                "location": element.location,
                "size": element.size,
                "displayed": element.is_displayed(),
                "enabled": element.is_enabled()
            }
            
            # Get important attributes
            attrs_to_check = [
                "id", "class", "data-testid", "data-cy", "data-qa", "role", 
                "aria-label", "aria-describedby", "title", "alt", "src", "href",
                "type", "name", "value", "placeholder", "onclick"
            ]
            
            for attr in attrs_to_check:
                try:
                    value = element.get_attribute(attr)
                    if value:
                        info["attributes"][attr] = value
                except:
                    pass
            
            # Get computed CSS properties for important styling
            try:
                info["css"] = {
                    "display": element.value_of_css_property("display"),
                    "visibility": element.value_of_css_property("visibility"),
                    "position": element.value_of_css_property("position")
                }
            except:
                info["css"] = {}
                
            return info
            
        except Exception as e:
            logger.warning(f"Error extracting element info: {e}")
            return {"error": str(e)}
    
    def find_song_elements(self) -> List[Dict[str, Any]]:
        """
        Find and analyze elements that likely represent songs in the library.
        Enhanced selectors for authenticated Udio pages.
        
        Returns:
            List of song element information
        """
        song_elements = []
        
        # Enhanced selectors based on common music app patterns
        song_selectors = [
            # Udio-specific patterns (guessed)
            "[data-testid*='song']",
            "[data-testid*='track']", 
            "[data-testid*='creation']",
            "[data-testid*='audio']",
            "[data-testid*='music']",
            "[data-testid*='clip']",
            
            # Class-based patterns
            "[class*='song']",
            "[class*='track']",
            "[class*='creation']",
            "[class*='audio']",
            "[class*='music']",
            "[class*='clip']",
            "[class*='card']",
            "[class*='item']",
            "[class*='tile']",
            "[class*='grid-item']",
            
            # Structural patterns
            "article",
            ".grid > div",
            ".list > div",
            "[role='listitem']",
            "[role='gridcell']",
            
            # Interactive elements
            "[role='button'][aria-label*='play']",
            "[role='button'][aria-label*='pause']",
            "button[aria-label*='play']",
            "button[aria-label*='pause']",
            
            # Media-related
            "audio",
            "video",
            "[controls]",
            
            # Download/action buttons
            "[aria-label*='download']",
            "[title*='download']",
            "a[href*='download']",
            "button[data-action*='download']"
        ]
        
        for selector in song_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"Found {len(elements)} elements with selector: {selector}")
                    
                    for i, element in enumerate(elements[:10]):  # Limit to first 10
                        info = self.extract_element_info(element)
                        info["selector_used"] = selector
                        info["element_index"] = i
                        song_elements.append(info)
                        
            except Exception as e:
                logger.warning(f"Error with selector {selector}: {e}")
        
        return song_elements
    
    def find_navigation_elements(self) -> List[Dict[str, Any]]:
        """Find navigation and control elements."""
        nav_elements = []
        
        nav_selectors = [
            "nav",
            "[role='navigation']",
            "[data-testid*='nav']",
            "[data-testid*='menu']",
            "[data-testid*='header']",
            "[data-testid*='sidebar']",
            "[class*='nav']",
            "[class*='menu']",
            "[class*='header']",
            "[class*='sidebar']",
            "[class*='toolbar']",
            "button",
            "a[href]",
            "[role='button']",
            "[role='link']",
            "[role='tab']",
            "[role='tablist']"
        ]
        
        for selector in nav_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"Found {len(elements)} navigation elements with selector: {selector}")
                    
                    for i, element in enumerate(elements[:5]):  # Limit to avoid spam
                        info = self.extract_element_info(element)
                        info["selector_used"] = selector
                        info["element_index"] = i
                        nav_elements.append(info)
                        
            except Exception as e:
                logger.warning(f"Error with navigation selector {selector}: {e}")
        
        return nav_elements
    
    def find_media_elements(self) -> List[Dict[str, Any]]:
        """Find audio/media player elements."""
        media_elements = []
        
        media_selectors = [
            "audio",
            "video", 
            "[data-testid*='player']",
            "[data-testid*='audio']",
            "[data-testid*='media']",
            "[class*='player']",
            "[class*='audio']",
            "[class*='media']",
            "[class*='waveform']",
            "[role='slider']",  # Volume/progress controls
            "[type='range']",   # HTML5 range inputs
            "source",
            "[src*='.mp3']",
            "[src*='.wav']",
            "[src*='.m4a']",
            "[src*='.ogg']",
            "[href*='download']",
            "[data-src]",  # Lazy-loaded audio
            "canvas"  # Waveform visualizations
        ]
        
        for selector in media_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"Found {len(elements)} media elements with selector: {selector}")
                    
                    for element in elements:
                        info = self.extract_element_info(element)
                        info["selector_used"] = selector
                        media_elements.append(info)
                        
            except Exception as e:
                logger.warning(f"Error with media selector {selector}: {e}")
        
        return media_elements
    
    def analyze_page_structure(self) -> Dict[str, Any]:
        """Analyze the overall page structure and layout."""
        try:
            structure = {
                "body_classes": self.driver.find_element(By.TAG_NAME, "body").get_attribute("class"),
                "main_containers": [],
                "grid_layouts": [],
                "list_layouts": []
            }
            
            # Find main containers
            container_selectors = ["main", "[role='main']", ".container", ".wrapper", ".content"]
            for selector in container_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    info = self.extract_element_info(element)
                    info["selector"] = selector
                    structure["main_containers"].append(info)
            
            # Find grid layouts
            grid_selectors = [".grid", "[style*='grid']", "[class*='grid']"]
            for selector in grid_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    info = self.extract_element_info(element)
                    info["selector"] = selector
                    info["child_count"] = len(element.find_elements(By.XPATH, "./*"))
                    structure["grid_layouts"].append(info)
            
            # Find list layouts
            list_selectors = ["ul", "ol", "[role='list']", "[class*='list']"]
            for selector in list_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    info = self.extract_element_info(element)
                    info["selector"] = selector
                    info["child_count"] = len(element.find_elements(By.XPATH, "./*"))
                    structure["list_layouts"].append(info)
            
            return structure
            
        except Exception as e:
            logger.error(f"Error analyzing page structure: {e}")
            return {"error": str(e)}
    
    def capture_page_structure(self, url: str, page_name: str) -> Dict[str, Any]:
        """
        Capture the complete structure of a page.
        
        Args:
            url: URL to analyze
            page_name: Name for the page (for output files)
            
        Returns:
            Dictionary with complete page analysis
        """
        logger.info(f"Analyzing authenticated page: {page_name} ({url})")
        
        try:
            # Navigate to page
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Capture page info
            page_info = {
                "url": url,
                "title": self.driver.title,
                "current_url": self.driver.current_url,
                "timestamp": datetime.now().isoformat(),
                "page_source_length": len(self.driver.page_source),
                "window_size": self.driver.get_window_size(),
                "analysis": {}
            }
            
            # Check if we're actually on the intended page (not redirected to login)
            if "login" in self.driver.current_url.lower():
                logger.warning(f"Redirected to login page for {page_name}")
                page_info["redirected_to_login"] = True
                return page_info
            
            # Analyze different element types
            logger.info("Analyzing page structure...")
            page_info["analysis"]["structure"] = self.analyze_page_structure()
            
            logger.info("Finding song elements...")
            page_info["analysis"]["songs"] = self.find_song_elements()
            
            logger.info("Finding navigation elements...")
            page_info["analysis"]["navigation"] = self.find_navigation_elements()
            
            logger.info("Finding media elements...")
            page_info["analysis"]["media"] = self.find_media_elements()
            
            # Get page source sample for manual inspection
            page_info["page_source_sample"] = self.driver.page_source[:10000]  # First 10KB
            
            # Take screenshot
            screenshot_path = self.output_dir / f"{page_name}_screenshot.png"
            self.driver.save_screenshot(str(screenshot_path))
            page_info["screenshot_path"] = str(screenshot_path)
            
            logger.info(f"Analysis complete for {page_name}")
            return page_info
            
        except Exception as e:
            logger.error(f"Error analyzing {page_name}: {e}")
            return {
                "url": url,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def map_all_pages(self) -> Dict[str, Any]:
        """
        Map all specified Udio pages using existing Chrome session.
        
        Returns:
            Complete mapping results
        """
        logger.info("Starting Udio UI mapping with existing Chrome session...")
        
        try:
            self.driver = self.setup_driver()
            
            # Get current session info
            current_url = self.driver.current_url
            logger.info(f"Connected to Chrome. Current URL: {current_url}")
            
            results = {
                "mapping_session": {
                    "timestamp": datetime.now().isoformat(),
                    "user_agent": self.driver.execute_script("return navigator.userAgent;"),
                    "window_size": self.driver.get_window_size(),
                    "initial_url": current_url,
                    "debug_port": self.debug_port
                },
                "pages": {}
            }
            
            # Map each page
            for page_name, url in self.urls_to_map.items():
                results["pages"][page_name] = self.capture_page_structure(url, page_name)
                
                # Save individual page results
                page_file = self.output_dir / f"{page_name}_analysis.json"
                with open(page_file, 'w', encoding='utf-8') as f:
                    json.dump(results["pages"][page_name], f, indent=2, ensure_ascii=False)
                
                logger.info(f"Saved {page_name} analysis to {page_file}")
                
                # Small delay between pages
                time.sleep(2)
            
            # Save complete results
            complete_file = self.output_dir / "complete_ui_mapping.json"
            with open(complete_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Complete mapping saved to {complete_file}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to connect to Chrome session: {e}")
            logger.info("Make sure Chrome is running with --remote-debugging-port=9222")
            raise
        finally:
            # Don't quit the driver since we're using an existing session
            pass
    
    def generate_summary_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable summary report."""
        report = []
        report.append("# Udio UI Mapping Summary Report (Authenticated Session)")
        report.append(f"Generated: {results['mapping_session']['timestamp']}")
        report.append(f"Debug Port: {results['mapping_session']['debug_port']}")
        report.append("")
        
        for page_name, page_data in results["pages"].items():
            if "error" in page_data:
                report.append(f"## {page_name.title()} Page - ERROR")
                report.append(f"Error: {page_data['error']}")
                continue
                
            if page_data.get("redirected_to_login"):
                report.append(f"## {page_name.title()} Page - REDIRECTED TO LOGIN")
                report.append("Session may have expired or page requires additional authentication")
                continue
                
            report.append(f"## {page_name.title()} Page")
            report.append(f"URL: {page_data['url']}")
            report.append(f"Title: {page_data['title']}")
            report.append("")
            
            analysis = page_data.get("analysis", {})
            
            # Song elements summary
            songs = analysis.get("songs", [])
            report.append(f"### Song Elements Found: {len(songs)}")
            if songs:
                unique_selectors = set(song.get("selector_used", "") for song in songs)
                report.append(f"Selectors that found songs: {', '.join(sorted(unique_selectors))}")
                
                # Show some example elements
                for i, song in enumerate(songs[:3]):
                    if song.get("text"):
                        report.append(f"  - Example {i+1}: {song['text'][:100]}...")
            report.append("")
            
            # Media elements summary
            media = analysis.get("media", [])
            report.append(f"### Media Elements Found: {len(media)}")
            if media:
                unique_selectors = set(elem.get("selector_used", "") for elem in media)
                report.append(f"Media selectors: {', '.join(sorted(unique_selectors))}")
            report.append("")
            
            # Structure summary
            structure = analysis.get("structure", {})
            if structure:
                report.append(f"### Page Structure:")
                report.append(f"  - Main containers: {len(structure.get('main_containers', []))}")
                report.append(f"  - Grid layouts: {len(structure.get('grid_layouts', []))}")
                report.append(f"  - List layouts: {len(structure.get('list_layouts', []))}")
            report.append("")
        
        return "\n".join(report)


def main():
    """Main function to run the UI mapping with existing Chrome session."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Map Udio UI structure using existing Chrome session")
    parser.add_argument("--debug-port", type=int, default=9222, help="Chrome remote debugging port")
    parser.add_argument("--output-dir", default="ui_mapping_authenticated", help="Output directory")
    
    args = parser.parse_args()
    
    print("🔗 Connecting to existing Chrome session...")
    print(f"   Debug port: {args.debug_port}")
    print("   Make sure Chrome is running with --remote-debugging-port=9222")
    print("")
    
    # Create mapper and run analysis
    mapper = UdioUIMapperAttach(debug_port=args.debug_port)
    mapper.output_dir = Path(args.output_dir)
    mapper.output_dir.mkdir(exist_ok=True)
    
    try:
        results = mapper.map_all_pages()
        
        # Generate and save summary report
        summary = mapper.generate_summary_report(results)
        summary_file = mapper.output_dir / "summary_report.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"\n✅ UI mapping complete!")
        print(f"📁 Results saved to: {mapper.output_dir}")
        print(f"📊 Summary report: {summary_file}")
        print(f"🖼️  Screenshots saved for each page")
        
        # Print quick summary
        total_pages = len(results["pages"])
        successful_pages = sum(1 for page in results["pages"].values() 
                             if "error" not in page and not page.get("redirected_to_login"))
        print(f"\n📈 Quick Summary:")
        print(f"   Pages analyzed: {successful_pages}/{total_pages}")
        
        for page_name, page_data in results["pages"].items():
            if "analysis" in page_data:
                analysis = page_data["analysis"]
                song_count = len(analysis.get("songs", []))
                media_count = len(analysis.get("media", []))
                print(f"   {page_name}: {song_count} song elements, {media_count} media elements")
        
    except KeyboardInterrupt:
        print("\n❌ Mapping interrupted by user")
    except Exception as e:
        logger.error(f"Mapping failed: {e}")
        print(f"❌ Mapping failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure Chrome is running")
        print("   2. Start Chrome with: chrome --remote-debugging-port=9222")
        print("   3. Or restart Chrome and try again")


if __name__ == "__main__":
    main()