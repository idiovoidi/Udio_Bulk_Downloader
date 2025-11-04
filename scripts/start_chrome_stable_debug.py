#!/usr/bin/env python3
"""
Start Chrome Stable with Debugging - Automatically setup Chrome Stable for Udio library mapping.
This is more reliable than Chrome Dev for remote debugging.
"""

import subprocess
import time
import requests
import psutil
import os
from pathlib import Path


class ChromeStableDebugger:
    """Setup Chrome Stable with debugging for Udio library mapping."""
    
    def __init__(self):
        self.chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
        ]
        self.debug_port = 9222
        self.chrome_path = None
        self.process = None
    
    def find_chrome_stable(self):
        """Find Chrome Stable installation."""
        print("🔍 Looking for Chrome Stable...")
        
        for path in self.chrome_paths:
            if Path(path).exists():
                print(f"   ✅ Found: {path}")
                
                # Verify it's actually Chrome (not Dev/Canary)
                try:
                    result = subprocess.run([path, "--version"], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        print(f"   📦 Version: {version}")
                        
                        # Check if it's stable (not Dev/Canary)
                        if "dev" not in version.lower() and "canary" not in version.lower():
                            self.chrome_path = path
                            return True
                        else:
                            print(f"   ⚠️  This is {version}, looking for Stable...")
                except Exception as e:
                    print(f"   ⚠️  Error checking version: {e}")
            else:
                print(f"   ❌ Not found: {path}")
        
        if not self.chrome_path:
            print("   ❌ Chrome Stable not found")
            print("   💡 Install from: https://www.google.com/chrome/")
            return False
        
        return True
    
    def kill_all_chrome(self):
        """Kill all Chrome processes."""
        print("🔄 Killing all Chrome processes...")
        
        killed = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'chrome' in proc.info['name'].lower():
                    proc.kill()
                    killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if killed > 0:
            print(f"   Killed {killed} Chrome processes")
            time.sleep(3)
        else:
            print("   No Chrome processes to kill")
    
    def start_chrome_with_debug(self):
        """Start Chrome Stable with debugging enabled."""
        print("🚀 Starting Chrome Stable with debugging...")
        
        # Build command with debugging flags
        cmd = [
            self.chrome_path,
            f'--remote-debugging-port={self.debug_port}',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-default-apps',
            'https://www.udio.com/library'
        ]
        
        print(f"   Command: {' '.join(cmd)}")
        
        try:
            self.process = subprocess.Popen(cmd, 
                                          stdout=subprocess.DEVNULL, 
                                          stderr=subprocess.DEVNULL)
            
            print(f"   ✅ Chrome started with PID {self.process.pid}")
            print(f"   🌐 Opening Udio library page...")
            
            # Wait for Chrome to initialize
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to start Chrome: {e}")
            return False
    
    def verify_debug_connection(self):
        """Verify debug connection is working."""
        print("🔍 Verifying debug connection...")
        
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"http://localhost:{self.debug_port}/json", timeout=5)
                if response.status_code == 200:
                    tabs = response.json()
                    print(f"   ✅ Debug connection successful! ({len(tabs)} tabs)")
                    
                    # Show tabs
                    for i, tab in enumerate(tabs, 1):
                        url = tab.get('url', 'No URL')[:60]
                        title = tab.get('title', 'No title')[:40]
                        print(f"      {i}. {title} - {url}")
                    
                    return True
                else:
                    print(f"   ❌ Debug endpoint returned status {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                if attempt < max_attempts - 1:
                    print(f"   ⏳ Attempt {attempt + 1}/{max_attempts}: Waiting for Chrome...")
                    time.sleep(2)
                else:
                    print(f"   ❌ Cannot connect after {max_attempts} attempts")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return False
    
    def check_login_status(self):
        """Check if user is on the library page (logged in)."""
        print("\n🔍 Checking login status...")
        
        try:
            response = requests.get(f"http://localhost:{self.debug_port}/json", timeout=5)
            if response.status_code == 200:
                tabs = response.json()
                
                # Look for library tab (not login page)
                for tab in tabs:
                    url = tab.get('url', '').lower()
                    title = tab.get('title', '')
                    
                    if 'udio.com/library' in url:
                        if 'login' in url:
                            print(f"   ⚠️  On login page")
                            print(f"   📄 Title: {title}")
                            return False
                        else:
                            print(f"   ✅ On library page!")
                            print(f"   📄 Title: {title}")
                            return True
                
                print("   ⚠️  Udio library page not found")
                return False
                
        except Exception as e:
            print(f"   ❌ Error checking login status: {e}")
            return False
    
    def wait_for_login(self):
        """Wait for user to complete login."""
        print("\n" + "=" * 60)
        print("👤 MANUAL LOGIN REQUIRED")
        print("=" * 60)
        print()
        print("Chrome is now open. Please:")
        print("  1. Log in to Udio with: idiovoidi@gmail.com")
        print("  2. Navigate to: https://www.udio.com/library")
        print("  3. Wait for the library page to fully load")
        print("  4. Make sure you can see your folders and songs")
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
    
    def run_setup(self):
        """Run complete setup process."""
        print("🎵 Chrome Stable Debug Setup for Udio")
        print("=" * 60)
        
        # Step 1: Find Chrome Stable
        if not self.find_chrome_stable():
            print("\n❌ Chrome Stable not found")
            print("💡 Please install Chrome Stable from: https://www.google.com/chrome/")
            return False
        
        # Step 2: Kill existing Chrome
        self.kill_all_chrome()
        
        # Step 3: Start Chrome with debugging
        if not self.start_chrome_with_debug():
            print("\n❌ Failed to start Chrome")
            return False
        
        # Step 4: Verify debug connection
        if not self.verify_debug_connection():
            print("\n❌ Debug connection failed")
            print("💡 This might be a firewall or antivirus issue")
            return False
        
        # Step 5: Check if already logged in
        if self.check_login_status():
            print("\n✅ Already logged in!")
        else:
            # Step 6: Wait for user to log in
            if not self.wait_for_login():
                print("\n❌ Login cancelled")
                return False
            
            # Step 7: Verify login
            if not self.check_login_status():
                print("\n⚠️  Login verification failed")
                print("💡 Make sure you're on https://www.udio.com/library")
                print("💡 You can still proceed, but mapping may fail")
        
        print("\n" + "=" * 60)
        print("✅ SETUP COMPLETE!")
        print("=" * 60)
        print()
        print("Chrome Stable is running with debug enabled.")
        print("You should be logged in to Udio.")
        print()
        print("🎯 Next step:")
        print("   python scripts/map_udio_library_structure.py")
        print()
        print("💡 Keep Chrome open while running the mapper!")
        print("💡 Don't close this terminal - Chrome will close if you do")
        
        return True
    
    def keep_alive(self):
        """Keep the script running to maintain Chrome process."""
        print("\n⏳ Keeping Chrome alive...")
        print("   Press Ctrl+C to stop and close Chrome")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🔄 Shutting down...")
            if self.process:
                self.process.terminate()
                time.sleep(1)
            print("✅ Chrome closed")


def main():
    """Main function."""
    debugger = ChromeStableDebugger()
    
    print("This will:")
    print("1. Find Chrome Stable installation")
    print("2. Kill existing Chrome processes")
    print("3. Start Chrome with debugging enabled")
    print("4. Open Udio library page")
    print("5. Wait for you to log in")
    print("6. Prepare for library structure mapping")
    print()
    
    success = debugger.run_setup()
    
    if success:
        print("\n🎉 Ready to map Udio library structure!")
        
        # Ask if user wants to run mapper now
        try:
            response = input("\nRun library mapper now? (y/N): ").strip().lower()
            if response in ('y', 'yes'):
                print("\n🚀 Starting library mapper...")
                import subprocess
                result = subprocess.run(['python', 'scripts/map_udio_library_structure.py'])
                
                if result.returncode == 0:
                    print("\n✅ Library mapping complete!")
                else:
                    print("\n⚠️  Library mapping had issues")
            else:
                print("\n💡 Run manually when ready:")
                print("   python scripts/map_udio_library_structure.py")
                
                # Keep Chrome alive
                debugger.keep_alive()
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    else:
        print("\n🔧 Setup failed - check output above")


if __name__ == "__main__":
    main()