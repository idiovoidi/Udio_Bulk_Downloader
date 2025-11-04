#!/usr/bin/env python3
"""
Check if Chrome remote debugging is available and test connection.
"""

import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

def check_debug_port(port=9222):
    """Check if Chrome debugging is available on the specified port."""
    try:
        response = requests.get(f"http://localhost:{port}/json", timeout=5)
        if response.status_code == 200:
            tabs = response.json()
            print(f"✅ Chrome debugging is available on port {port}")
            print(f"📱 Found {len(tabs)} open tabs/windows:")
            
            for i, tab in enumerate(tabs[:5]):  # Show first 5 tabs
                title = tab.get('title', 'No title')[:50]
                url = tab.get('url', 'No URL')[:60]
                print(f"   {i+1}. {title} - {url}")
            
            if len(tabs) > 5:
                print(f"   ... and {len(tabs) - 5} more tabs")
            
            return True
        else:
            print(f"❌ Chrome debugging port {port} responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Chrome debugging port {port}")
        print("   Chrome is not running with --remote-debugging-port=9222")
        return False
    except Exception as e:
        print(f"❌ Error checking debug port: {e}")
        return False

def test_selenium_connection(port=9222):
    """Test if we can connect with Selenium."""
    try:
        options = ChromeOptions()
        options.add_experimental_option("debuggerAddress", f"localhost:{port}")
        
        driver = webdriver.Chrome(options=options)
        current_url = driver.current_url
        title = driver.title
        
        print(f"✅ Selenium connection successful!")
        print(f"   Current page: {title}")
        print(f"   URL: {current_url}")
        
        # Don't quit - we're using existing session
        return True
        
    except Exception as e:
        print(f"❌ Selenium connection failed: {e}")
        return False

def main():
    print("🔍 Checking Chrome Remote Debugging Status...")
    print()
    
    # Check if debugging port is available
    if check_debug_port():
        print()
        print("🧪 Testing Selenium connection...")
        if test_selenium_connection():
            print()
            print("🎉 Everything looks good! You can run the UI mapper now:")
            print("   python scripts/ui_mapper_attach.py")
        else:
            print()
            print("⚠️  Debugging port is available but Selenium can't connect")
            print("   Try restarting Chrome with debugging enabled")
    else:
        print()
        print("💡 To enable Chrome debugging:")
        print("   1. Close Chrome completely")
        print("   2. Run: chrome --remote-debugging-port=9222")
        print("   3. Or use: scripts/start_chrome_dev_debug.bat")

if __name__ == "__main__":
    main()