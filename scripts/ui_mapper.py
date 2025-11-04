#!/usr/bin/env python3
"""
Udio UI Mapper - Maps out the DOM structure of Udio's web interface.
Focuses on the library section where created songs are stored.
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
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class UdioUIMapper:
    """Maps the Udio user interface structure for scraping purposes."""
    
    def __init__(self, headless: bool = False):
        """
        Initialize the UI mapper.
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
        self.output_dir = Path("ui_mapping_results")
        self.output_dir.mkdir(exist_ok=True)
        
        # Udio URLs to map
        self.urls_to_map = {
            "library": "https://www.udio.com/library",
            "create": "https://www.udio.com/create",
            "my_creations": "https://www.udio.com/my-creations"
        }
    
    def setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with appropriate options."""
        options = ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        
        # Standard options for web scraping
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Anti-detection measures
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=options
        )
        
        # Additional anti-detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
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
                "text": element.text.strip() if element.text else "",
                "attributes": {},
                "location": element.location,
                "size": element.size,
                "displayed": element.is_displayed(),
                "enabled": element.is_enabled()
            }
            
            # Get all attributes
            attrs_to_check = [
                "id", "class", "data-testid", "data-cy", "data-qa", "role", 
                "aria-label", "aria-describedby", "title", "alt", "src", "href",
                "type", "name", "value", "placeholder", "onclick", "data-*"
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
                    "position": element.value_of_css_property("position"),
                    "z-index": element.value_of_css_property("z-index")
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
        
        Returns:
            List of song element information
        """
        song_elements = []
        
        # Common selectors for song/track items
        song_selectors = [
            "[data-testid*='song']",
            "[data-testid*='track']", 
            "[data-testid*='creation']",
            "[data-testid*='audio']",
            "[class*='song']",
            "[class*='track']",
            "[class*='creation']",
            "[class*='audio']",
            "[class*='card']",
            "[class*='item']",
            "article",
            ".grid > div",
            "[role='listitem']",
            "[role='button'][aria-label*='play']"
        ]
        
        for selector in song_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                logger.info(f"Found {len(elements)} elements with selector: {selector}")
                
                for element in elements[:5]:  # Limit to first 5 to avoid spam
                    info = self.extract_element_info(element)
                    info["selector_used"] = selector
                    song_elements.append(info)
                    
            except Exception as e:
                logger.warning(f"Error with selector {selector}: {e}")
        
        return song_elements
    
    def find_navigation_elements(self) -> List[Dict[str, Any]]:
        """
        Find navigation and control elements.
        
        Returns:
            List of navigation element information
        """
        nav_elements = []
        
        nav_selectors = [
            "nav",
            "[role='navigation']",
            "[data-testid*='nav']",
            "[data-testid*='menu']",
            "[class*='nav']",
            "[class*='menu']",
            "[class*='header']",
            "[class*='sidebar']",
            "button",
            "a[href]",
            "[role='button']",
            "[role='link']"
        ]
        
        for selector in nav_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                logger.info(f"Found {len(elements)} navigation elements with selector: {selector}")
                
                for element in elements[:10]:  # Limit to avoid spam
                    info = self.extract_element_info(element)
                    info["selector_used"] = selector
                    nav_elements.append(info)
                    
            except Exception as e:
                logger.warning(f"Error with navigation selector {selector}: {e}")
        
        return nav_elements
    
    def find_media_elements(self) -> List[Dict[str, Any]]:
        """
        Find audio/media player elements.
        
        Returns:
            List of media element information
        """
        media_elements = []
        
        media_selectors = [
            "audio",
            "video", 
            "[data-testid*='player']",
            "[data-testid*='audio']",
            "[class*='player']",
            "[class*='audio']",
            "[class*='media']",
            "[role='slider']",  # Volume/progress controls
            "[type='range']",   # HTML5 range inputs
            "source",
            "[src*='.mp3']",
            "[src*='.wav']",
            "[src*='.m4a']",
            "[href*='download']"
        ]
        
        for selector in media_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                logger.info(f"Found {len(elements)} media elements with selector: {selector}")
                
                for element in elements:
                    info = self.extract_element_info(element)
                    info["selector_used"] = selector
                    media_elements.append(info)
                    
            except Exception as e:
                logger.warning(f"Error with media selector {selector}: {e}")
        
        return media_elements
    
    def capture_page_structure(self, url: str, page_name: str) -> Dict[str, Any]:
        """
        Capture the complete structure of a page.
        
        Args:
            url: URL to analyze
            page_name: Name for the page (for output files)
            
        Returns:
            Dictionary with complete page analysis
        """
        logger.info(f"Analyzing page: {page_name} ({url})")
        
        try:
            # Navigate to page
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(5)
            
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
            
            # Analyze different element types
            logger.info("Finding song elements...")
            page_info["analysis"]["songs"] = self.find_song_elements()
            
            logger.info("Finding navigation elements...")
            page_info["analysis"]["navigation"] = self.find_navigation_elements()
            
            logger.info("Finding media elements...")
            page_info["analysis"]["media"] = self.find_media_elements()
            
            # Get page source for manual inspection
            page_info["page_source_sample"] = self.driver.page_source[:5000]  # First 5KB
            
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
        Map all specified Udio pages.
        
        Returns:
            Complete mapping results
        """
        logger.info("Starting Udio UI mapping...")
        
        self.driver = self.setup_driver()
        
        try:
            results = {
                "mapping_session": {
                    "timestamp": datetime.now().isoformat(),
                    "user_agent": self.driver.execute_script("return navigator.userAgent;"),
                    "window_size": self.driver.get_window_size()
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
            
            # Save complete results
            complete_file = self.output_dir / "complete_ui_mapping.json"
            with open(complete_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Complete mapping saved to {complete_file}")
            return results
            
        finally:
            if self.driver:
                self.driver.quit()
    
    def generate_summary_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary report.
        
        Args:
            results: Mapping results
            
        Returns:
            Summary report as string
        """
        report = []
        report.append("# Udio UI Mapping Summary Report")
        report.append(f"Generated: {results['mapping_session']['timestamp']}")
        report.append("")
        
        for page_name, page_data in results["pages"].items():
            if "error" in page_data:
                report.append(f"## {page_name.title()} Page - ERROR")
                report.append(f"Error: {page_data['error']}")
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
                report.append(f"Selectors that found songs: {', '.join(unique_selectors)}")
            report.append("")
            
            # Media elements summary
            media = analysis.get("media", [])
            report.append(f"### Media Elements Found: {len(media)}")
            if media:
                unique_selectors = set(elem.get("selector_used", "") for elem in media)
                report.append(f"Media selectors: {', '.join(unique_selectors)}")
            report.append("")
            
            # Navigation elements summary
            nav = analysis.get("navigation", [])
            report.append(f"### Navigation Elements Found: {len(nav)}")
            report.append("")
        
        return "\n".join(report)


def main():
    """Main function to run the UI mapping."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Map Udio UI structure")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--output-dir", default="ui_mapping_results", help="Output directory")
    
    args = parser.parse_args()
    
    # Create mapper and run analysis
    mapper = UdioUIMapper(headless=args.headless)
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
        successful_pages = sum(1 for page in results["pages"].values() if "error" not in page)
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


if __name__ == "__main__":
    main()