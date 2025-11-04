#!/usr/bin/env python3
"""
Update ChromeDriver to match Chrome Dev version.
"""

import subprocess
import os
import shutil
from webdriver_manager.chrome import ChromeDriverManager


def update_chromedriver():
    """Update ChromeDriver to latest version."""
    print("🔄 Updating ChromeDriver...")
    
    try:
        # Clear cache to force fresh download
        print("   Clearing ChromeDriver cache...")
        cache_dir = os.path.expanduser("~/.wdm")
        if os.path.exists(cache_dir):
            import shutil
            shutil.rmtree(cache_dir)
            print("   ✅ Cache cleared")
        
        # Download latest ChromeDriver
        print("   Downloading latest ChromeDriver...")
        driver_path = ChromeDriverManager().install()
        print(f"   ✅ ChromeDriver installed at: {driver_path}")
        
        # Test the driver
        print("   Testing ChromeDriver...")
        result = subprocess.run([driver_path, "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   ✅ ChromeDriver version: {version}")
        else:
            print("   ⚠️  Could not get ChromeDriver version")
        
        return driver_path
        
    except Exception as e:
        print(f"   ❌ Error updating ChromeDriver: {e}")
        return None


def get_chrome_version():
    """Get current Chrome version."""
    chrome_path = r"C:\Program Files\Google\Chrome Dev\Application\chrome.exe"
    
    try:
        result = subprocess.run([chrome_path, "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"Error getting Chrome version: {e}")
    
    return "Unknown"


def main():
    """Main function."""
    print("🔧 ChromeDriver Update Tool")
    print("=" * 30)
    
    # Show current Chrome version
    chrome_version = get_chrome_version()
    print(f"Chrome Version: {chrome_version}")
    
    # Update ChromeDriver
    driver_path = update_chromedriver()
    
    if driver_path:
        print("\n✅ ChromeDriver update complete!")
        print("🎯 Now try running the UI mapper again:")
        print("   python scripts/ui_mapper_attach.py")
    else:
        print("\n❌ ChromeDriver update failed")


if __name__ == "__main__":
    main()