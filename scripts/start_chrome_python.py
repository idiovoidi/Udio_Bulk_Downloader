#!/usr/bin/env python3
"""
Start Chrome Dev with debugging using Python subprocess.
This provides better control and error handling than batch files.
"""

import subprocess
import time
import requests
import psutil
import os
from pathlib import Path


def kill_chrome_processes():
    """Kill all Chrome processes."""
    print("🔄 Terminating existing Chrome processes...")
    killed_count = 0
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'chrome.exe' in proc.info['name'].lower():
                proc.kill()
                killed_count += 1
                print(f"   Killed Chrome process PID {proc.info['pid']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if killed_count > 0:
        print(f"   Terminated {killed_count} Chrome processes")
        time.sleep(3)  # Wait for processes to fully terminate
    else:
        print("   No Chrome processes found")
    
    return killed_count


def check_debugging_port(port=9222, timeout=5):
    """Check if Chrome debugging port is responding."""
    try:
        response = requests.get(f"http://localhost:{port}/json", timeout=timeout)
        if response.status_code == 200:
            tabs = response.json()
            return True, len(tabs)
    except requests.exceptions.RequestException:
        pass
    return False, 0


def start_chrome_with_debugging():
    """Start Chrome Dev with debugging enabled."""
    chrome_path = r"C:\Program Files\Google\Chrome Dev\Application\chrome.exe"
    user_data_dir = r"C:\Users\Mitchell\AppData\Local\Google\Chrome Dev\User Data"
    profile_dir = "Profile 2"
    debug_port = 9222
    target_url = "https://www.udio.com/library"
    
    # Verify Chrome executable exists
    if not Path(chrome_path).exists():
        print(f"❌ Chrome Dev not found at: {chrome_path}")
        return False
    
    # Verify user data directory exists
    if not Path(user_data_dir).exists():
        print(f"❌ User data directory not found: {user_data_dir}")
        return False
    
    # Kill existing Chrome processes
    kill_chrome_processes()
    
    # Build command
    cmd = [
        chrome_path,
        f"--remote-debugging-port={debug_port}",
        f"--user-data-dir={user_data_dir}",
        f"--profile-directory={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        target_url
    ]
    
    print("🚀 Starting Chrome Dev with debugging...")
    print(f"   Path: {chrome_path}")
    print(f"   Profile: {profile_dir}")
    print(f"   Debug Port: {debug_port}")
    print(f"   Target URL: {target_url}")
    
    try:
        # Start Chrome process
        process = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        
        print(f"   Chrome process started with PID: {process.pid}")
        
        # Wait for Chrome to initialize
        print("⏳ Waiting for Chrome to initialize...")
        for i in range(10):  # Wait up to 10 seconds
            time.sleep(1)
            is_ready, tab_count = check_debugging_port(debug_port)
            if is_ready:
                print(f"✅ Chrome debugging ready! Found {tab_count} tabs")
                return True
            print(f"   Attempt {i+1}/10: Waiting for debugging port...")
        
        print("❌ Chrome debugging port did not become available")
        return False
        
    except Exception as e:
        print(f"❌ Failed to start Chrome: {e}")
        return False


def main():
    """Main function."""
    print("🔧 Chrome Dev Debug Starter (Python Version)")
    print("=" * 50)
    
    # Check if debugging is already active
    print("🔍 Checking current debugging status...")
    is_active, tab_count = check_debugging_port()
    if is_active:
        print(f"✅ Chrome debugging already active with {tab_count} tabs")
        print("   You can proceed with UI mapping")
        return True
    
    # Start Chrome with debugging
    success = start_chrome_with_debugging()
    
    if success:
        print("\n🎉 Chrome Dev started successfully!")
        print("📋 Next steps:")
        print("   1. Verify you're logged into Udio (idiovoidi@gmail.com)")
        print("   2. Run: python scripts/check_chrome_debug.py")
        print("   3. Run: python scripts/ui_mapper_attach.py")
        
        # Show current tabs
        is_active, tab_count = check_debugging_port()
        if is_active:
            try:
                response = requests.get("http://localhost:9222/json", timeout=5)
                tabs = response.json()
                print(f"\n📱 Current tabs ({len(tabs)}):")
                for i, tab in enumerate(tabs[:3], 1):
                    title = tab.get('title', 'No title')[:50]
                    url = tab.get('url', 'No URL')[:60]
                    print(f"   {i}. {title} - {url}")
                if len(tabs) > 3:
                    print(f"   ... and {len(tabs) - 3} more tabs")
            except:
                pass
    else:
        print("\n❌ Failed to start Chrome with debugging")
        print("💡 Troubleshooting:")
        print("   1. Try running as administrator")
        print("   2. Check if antivirus is blocking Chrome")
        print("   3. Verify Chrome Dev is properly installed")
        print("   4. Try the batch file: scripts/start_chrome_debug_robust.bat")
    
    return success


if __name__ == "__main__":
    main()