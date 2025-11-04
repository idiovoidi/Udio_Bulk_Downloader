#!/usr/bin/env python3
"""
Fix Chrome Debug Issues - Properly restart Chrome with debugging enabled.
"""

import os
import time
import subprocess
import psutil
import requests
from pathlib import Path


class ChromeDebugFixer:
    """Fix Chrome debugging setup issues."""
    
    def __init__(self):
        self.chrome_path = r"C:\Program Files\Google\Chrome Dev\Application\chrome.exe"
        self.user_data_dir = r"C:\Users\Mitchell\AppData\Local\Google\Chrome Dev\User Data"
        self.profile = "Profile 2"
        self.debug_port = 9222
    
    def kill_all_chrome_processes(self):
        """Forcefully kill all Chrome processes."""
        print("🔄 Killing all Chrome processes...")
        
        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'chrome' in proc.info['name'].lower():
                    proc.kill()
                    killed_count += 1
                    print(f"   Killed PID {proc.info['pid']}: {proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        print(f"   Killed {killed_count} Chrome processes")
        
        # Wait for processes to fully terminate
        print("   Waiting for processes to terminate...")
        time.sleep(3)
        
        # Verify no Chrome processes remain
        remaining = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'chrome' in proc.info['name'].lower():
                    remaining.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if remaining:
            print(f"   ⚠️  {len(remaining)} Chrome processes still running")
            for proc in remaining:
                print(f"      PID {proc['pid']}: {proc['name']}")
        else:
            print("   ✅ All Chrome processes terminated")
        
        return len(remaining) == 0
    
    def start_chrome_with_debug(self):
        """Start Chrome with proper debugging flags."""
        print("🚀 Starting Chrome Dev with debugging...")
        
        # Build command with all necessary flags
        cmd = [
            self.chrome_path,
            f"--remote-debugging-port={self.debug_port}",
            f"--user-data-dir={self.user_data_dir}",
            f"--profile-directory={self.profile}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-default-apps",
            "--disable-popup-blocking",
            "https://www.udio.com/library"
        ]
        
        print(f"   Command: {' '.join(cmd)}")
        
        try:
            # Start Chrome process
            process = subprocess.Popen(cmd, 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
            
            print(f"   ✅ Chrome started with PID {process.pid}")
            
            # Wait for Chrome to initialize
            print("   Waiting for Chrome to initialize...")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to start Chrome: {e}")
            return False
    
    def verify_debug_connection(self):
        """Verify that debug connection is working."""
        print("🔍 Verifying debug connection...")
        
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"http://localhost:{self.debug_port}/json", timeout=5)
                if response.status_code == 200:
                    tabs = response.json()
                    print(f"   ✅ Debug connection successful!")
                    print(f"   📱 Found {len(tabs)} open tabs")
                    
                    # Look for Udio tabs
                    udio_tabs = [tab for tab in tabs if 'udio.com' in tab.get('url', '').lower()]
                    if udio_tabs:
                        print(f"   🎵 Found {len(udio_tabs)} Udio tabs:")
                        for tab in udio_tabs:
                            title = tab.get('title', 'No title')[:50]
                            url = tab.get('url', 'No URL')[:60]
                            print(f"      - {title}: {url}")
                    else:
                        print("   ⚠️  No Udio tabs found yet")
                    
                    return True
                else:
                    print(f"   ❌ Debug endpoint returned status {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                if attempt < max_attempts - 1:
                    print(f"   ⏳ Attempt {attempt + 1}/{max_attempts}: Connection refused, retrying...")
                    time.sleep(2)
                else:
                    print(f"   ❌ Cannot connect to debug endpoint after {max_attempts} attempts")
            except Exception as e:
                print(f"   ❌ Error checking debug connection: {e}")
        
        return False
    
    def test_selenium_connection(self):
        """Test Selenium connection to Chrome."""
        print("🧪 Testing Selenium connection...")
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            
            options = ChromeOptions()
            options.add_experimental_option("debuggerAddress", f"localhost:{self.debug_port}")
            
            driver = webdriver.Chrome(options=options)
            
            current_url = driver.current_url
            title = driver.title
            
            print(f"   ✅ Selenium connection successful!")
            print(f"   📄 Current page: {title}")
            print(f"   🔗 URL: {current_url}")
            
            # Check if we're on Udio
            if 'udio.com' in current_url.lower():
                print("   🎵 Successfully connected to Udio!")
                
                # Check if logged in (look for login indicators)
                if 'login' in current_url.lower():
                    print("   ⚠️  Currently on login page - authentication needed")
                else:
                    print("   ✅ Appears to be logged in!")
            else:
                print(f"   ℹ️  Not on Udio page yet: {current_url}")
            
            # Don't quit - we're using existing session
            return True
            
        except Exception as e:
            print(f"   ❌ Selenium connection failed: {e}")
            return False
    
    def fix_chrome_debug(self):
        """Complete fix process for Chrome debugging."""
        print("🔧 Chrome Debug Fix Tool")
        print("=" * 40)
        
        success_steps = 0
        total_steps = 4
        
        # Step 1: Kill existing Chrome processes
        if self.kill_all_chrome_processes():
            success_steps += 1
            print("✅ Step 1/4: Chrome processes terminated")
        else:
            print("⚠️  Step 1/4: Some Chrome processes may still be running")
        
        # Step 2: Start Chrome with debugging
        if self.start_chrome_with_debug():
            success_steps += 1
            print("✅ Step 2/4: Chrome started with debugging")
        else:
            print("❌ Step 2/4: Failed to start Chrome")
            return False
        
        # Step 3: Verify debug connection
        if self.verify_debug_connection():
            success_steps += 1
            print("✅ Step 3/4: Debug connection verified")
        else:
            print("❌ Step 3/4: Debug connection failed")
            return False
        
        # Step 4: Test Selenium
        if self.test_selenium_connection():
            success_steps += 1
            print("✅ Step 4/4: Selenium connection working")
        else:
            print("❌ Step 4/4: Selenium connection failed")
        
        print("\n" + "=" * 40)
        print(f"RESULT: {success_steps}/{total_steps} steps successful")
        
        if success_steps == total_steps:
            print("🎉 Chrome debugging is now working!")
            print("🎵 Ready to map Udio UI!")
            print("\nNext steps:")
            print("   python scripts/ui_mapper_attach.py")
            return True
        else:
            print("⚠️  Some issues remain - check output above")
            return False


def main():
    """Main function to fix Chrome debugging."""
    fixer = ChromeDebugFixer()
    
    print("This will:")
    print("1. Kill all existing Chrome processes")
    print("2. Start Chrome Dev with Profile 2 and debugging enabled")
    print("3. Open https://www.udio.com/library")
    print("4. Verify debugging connection")
    print()
    
    try:
        input("Press Enter to continue (or Ctrl+C to cancel)...")
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        return
    
    success = fixer.fix_chrome_debug()
    
    if success:
        print("\n🎯 Chrome is ready for UI mapping!")
        print("   Run: python scripts/ui_mapper_attach.py")
    else:
        print("\n🔧 Manual troubleshooting may be needed")
        print("   Check the diagnostic output above")


if __name__ == "__main__":
    main()