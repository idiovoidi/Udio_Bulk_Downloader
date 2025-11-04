#!/usr/bin/env python3
"""
Open Udio for Login - Start Chrome with debugging in non-headless mode for manual login.
"""

import subprocess
import time
import requests
import psutil
from pathlib import Path


class UdioLoginHelper:
    """Helper to open Udio in Chrome for manual login."""
    
    def __init__(self):
        self.chrome_path = r"C:\Program Files\Google\Chrome Dev\Application\chrome.exe"
        self.debug_port = 9222
    
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
    
    def start_chrome_for_login(self):
        """Start Chrome in non-headless mode for manual login."""
        print("🚀 Starting Chrome for manual login...")
        
        # Use non-headless mode so you can see and interact with the browser
        cmd = [
            self.chrome_path,
            f'--remote-debugging-port={self.debug_port}',
            '--no-first-run',
            '--disable-default-apps',
            'https://www.udio.com/library'
        ]
        
        print(f"   Command: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(cmd, 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
            
            print(f"   ✅ Chrome started with PID {process.pid}")
            print(f"   🌐 Opening Udio library page...")
            
            # Wait for Chrome to start
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
                    
            except requests.exceptions.ConnectionError:
                if attempt < max_attempts - 1:
                    print(f"   ⏳ Attempt {attempt + 1}/{max_attempts}: Retrying...")
                    time.sleep(2)
                else:
                    print(f"   ❌ Cannot connect after {max_attempts} attempts")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return False
    
    def wait_for_login(self):
        """Wait for user to complete login."""
        print("\n" + "=" * 50)
        print("👤 MANUAL LOGIN REQUIRED")
        print("=" * 50)
        print()
        print("Chrome is now open. Please:")
        print("  1. Log in to Udio with: idiovoidi@gmail.com")
        print("  2. Navigate to: https://www.udio.com/library")
        print("  3. Wait for the library page to fully load")
        print()
        print("Once you're logged in and on the library page,")
        print("press Enter to continue...")
        print()
        
        try:
            input("Press Enter when ready...")
            return True
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user")
            return False
    
    def check_login_status(self):
        """Check if user is logged in."""
        print("\n🔍 Checking login status...")
        
        try:
            response = requests.get(f"http://localhost:{self.debug_port}/json", timeout=5)
            if response.status_code == 200:
                tabs = response.json()
                
                # Look for library tab (not login page)
                for tab in tabs:
                    url = tab.get('url', '').lower()
                    if 'udio.com/library' in url and 'login' not in url:
                        print(f"   ✅ Logged in! Library page detected")
                        print(f"   📄 Title: {tab.get('title')}")
                        print(f"   🔗 URL: {tab.get('url')}")
                        return True
                
                print("   ⚠️  Still on login page or library not loaded")
                print("   💡 Make sure you're logged in and on the library page")
                return False
                
        except Exception as e:
            print(f"   ❌ Error checking login status: {e}")
            return False
    
    def run_setup(self):
        """Run complete setup process."""
        print("🎵 Udio Login Helper")
        print("=" * 50)
        
        # Step 1: Kill existing Chrome
        self.kill_chrome()
        
        # Step 2: Start Chrome for login
        if not self.start_chrome_for_login():
            print("❌ Failed to start Chrome")
            return False
        
        # Step 3: Verify debug connection
        if not self.verify_debug_connection():
            print("❌ Debug connection failed")
            return False
        
        # Step 4: Wait for user to log in
        if not self.wait_for_login():
            print("❌ Login cancelled")
            return False
        
        # Step 5: Check login status
        if not self.check_login_status():
            print("⚠️  Login verification failed")
            print("💡 You can still proceed, but make sure you're logged in")
        
        print("\n" + "=" * 50)
        print("✅ SETUP COMPLETE!")
        print("=" * 50)
        print()
        print("Chrome is running with debug enabled and you should be logged in.")
        print()
        print("🎯 Next step:")
        print("   python scripts/map_udio_library_structure.py")
        print()
        print("💡 Keep Chrome open while running the mapper!")
        
        return True


def main():
    """Main function."""
    helper = UdioLoginHelper()
    
    print("This will:")
    print("1. Kill existing Chrome processes")
    print("2. Start Chrome with debugging enabled (visible window)")
    print("3. Open Udio library page")
    print("4. Wait for you to log in manually")
    print("5. Prepare for library structure mapping")
    print()
    
    success = helper.run_setup()
    
    if success:
        print("🎉 Ready to map Udio library structure!")
    else:
        print("🔧 Setup failed - check output above")


if __name__ == "__main__":
    main()