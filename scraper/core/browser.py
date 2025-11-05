"""
Core browser connection and management.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class BrowserConnection:
    """Manages connection to Chrome via DevTools Protocol"""
    
    def __init__(self, debug_port=9222):
        self.debug_port = debug_port
        self.driver = None
        
    def connect(self):
        """Connect to existing Chrome instance"""
        print(f"Connecting to Chrome on port {self.debug_port}...")
        options = Options()
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.debug_port}")
        
        self.driver = webdriver.Chrome(options=options)
        print(f"✓ Connected! Current URL: {self.driver.current_url}")
        return self.driver
    
    def close(self):
        """Close connection (doesn't close Chrome)"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
