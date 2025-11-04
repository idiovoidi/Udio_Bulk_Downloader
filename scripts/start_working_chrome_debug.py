#!/usr/bin/env python3
"""
Start Working Chrome Debug - Use the configuration we know works.
"""

import subprocess
import time
import requests
import psutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions


class WorkingChromeDebug:
    """Start Chrome with the working debug configuration."""
    
    def __init__(self):
        self.chrome_path = r"C:\Program Files\Google\Chrome Dev\Application\chrome.exe"
        self.debug_port = 9222
        self.process = None
    
    def kill_chrome(self):
        """Kill all Chrome processes."""
        print("🔄 Killing existing Chrome processes...")
        killed = 0
        for proc in psutil.process_iter(['name']):
            try:
                if 'chrome' in proc.info['name'].lower():
                    proc.kill()
                    killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if killed > 0:
            print(f"   Killed {killed} Chrome processes")
            time.sleep(2)
        else:
            print("   No Chrome processes to kill")
    
    def start_chrome_debug(self):
        """Start Chrome with working debug configuration."""
        print("🚀 Starting Chrome with working debug configuration...")
        
        # Use the configuration we know works
        cmd = [
            self.chrome_path,
            '--remote-debugging-port=9222',
            '--new-window',  # Open in new window
            '--disable-default-apps',
            '--no-first-run'
        ]
        
        print(f"   Command: {' '.join(cmd)}")
        
        try:
            self.process = subprocess.Popen(cmd, 
                                          stdout=subprocess.DEVNULL, 
                                          stderr=subprocess.DEVNULL)
            
            print(f"   ✅ Chrome started with PID {self.process.pid}")
            
            # Wait for Chrome to initialize
            print("   ⏳ Waiting for Chrome to initialize...")
            time.sleep(4)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to start Chrome: {e}")
            return False
    
    def verify_debug_connection(self):
        """Verify debug connection is working."""
        print("🔍 Verifying debug connection...")
        
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"http://localhost:{self.debug_port}/json", timeout=5)
                if response.status_code == 200:
                    tabs = response.json()
                    print(f"   ✅ Debug connection successful! ({len(tabs)} tabs)")
                    return True
                else:
                    print(f"   ❌ Debug endpoint returned status {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                if attempt < max_attempts - 1:
                    print(f"   ⏳ Attempt {attempt + 1}/{max_attempts}: Retrying...")
                    time.sleep(2)
                else:
                    print(f"   ❌ Cannot connect after {max_attempts} attempts")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return False
    
    def navigate_to_udio(self):
        """Use Selenium to navigate to Udio."""
        print("🎵 Navigating to Udio...")
        
        try:
            options = ChromeOptions()
            options.add_experimental_option("debuggerAddress", f"localhost:{self.debug_port}")
            
            driver = webdriver.Chrome(options=options)
            
            print("   🌐 Opening Udio library page...")
            driver.get("https://www.udio.com/library")
            
            # Wait for page to load
            time.sleep(3)
            
            current_url = driver.current_url
            title = driver.title
            
            print(f"   📄 Current page: {title}")
            print(f"   🔗 URL: {current_url}")
            
            # Check if we need to login
            if 'login' in current_url.lower():
                print("   ⚠️  Currently on login page")
                print("   👤 Please log in manually with: user@example.com")
                print("   ⏳ Waiting for you to complete login...")
                
                # Wait for user to login (check URL changes)
                login_timeout = 300  # 5 minutes
                start_time = time.time()
                
                while 'login' in driver.current_url.lower():
                    if time.time() - start_time > login_timeout:
                        print("   ⏰ Login timeout - please complete login and try again")
                        return False
                    
                    time.sleep(2)
                
                print("   ✅ Login detected! Proceeding...")
                current_url = driver.current_url
                title = driver.title
                print(f"   📄 New page: {title}")
                print(f"   🔗 New URL: {current_url}")
            
            if 'udio.com' in current_url.lower() and 'login' not in current_url.lower():
                print("   ✅ Successfully on Udio platform!")
                return True
            else:
                print(f"   ⚠️  Unexpected page: {current_url}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error navigating to Udio: {e}")
            return False
    
    def run_setup(self):
        """Run complete setup process."""
        print("🔧 Chrome Debug Setup (Working Configuration)")
        print("=" * 50)
        
        # Step 1: Kill existing Chrome
        self.kill_chrome()
        
        # Step 2: Start Chrome with debug
        if not self.start_chrome_debug():
            print("❌ Failed to start Chrome")
            return False
        
        # Step 3: Verify debug connection
        if not self.verify_debug_connection():
            print("❌ Debug connection failed")
            return False
        
        # Step 4: Navigate to Udio
        if not self.navigate_to_udio():
            print("❌ Failed to navigate to Udio")
            return False
        
        print("\n" + "=" * 50)
        print("✅ SETUP COMPLETE!")
        print("🎵 Chrome is running with debug enabled and Udio is loaded")
        print("🎯 Ready to run UI mapping!")
        print("\nNext step:")
        print("   python scripts/ui_mapper_attach.py")
        
        return True


def main():
    """Main function."""
    setup = WorkingChromeDebug()
    
    print("This will:")
    print("1. Kill existing Chrome processes")
    print("2. Start Chrome with working debug configuration")
    print("3. Navigate to Udio (you may need to login)")
    print("4. Prepare for UI mapping")
    print()
    
    success = setup.run_setup()
    
    if success:
        print("\n🎉 Ready for UI mapping!")
        print("   Keep this Chrome window open")
        print("   Run: python scripts/ui_mapper_attach.py")
    else:
        print("\n🔧 Setup failed - check output above")


if __name__ == "__main__":
    main()