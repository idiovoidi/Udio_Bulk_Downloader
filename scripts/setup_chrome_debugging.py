#!/usr/bin/env python3
"""
Setup Chrome with debugging enabled - step by step process.
"""

import subprocess
import time
import requests

def kill_chrome_processes():
    """Kill all Chrome processes."""
    print("🔄 Closing all Chrome processes...")
    
    try:
        result = subprocess.run(['taskkill', '/f', '/im', 'chrome.exe'], 
                              capture_output=True, text=True)
        
        if "SUCCESS" in result.stdout:
            print("✅ Chrome processes terminated")
        elif "not found" in result.stderr.lower():
            print("ℹ️  No Chrome processes were running")
        else:
            print(f"⚠️  Result: {result.stdout.strip()}")
            
        # Wait for processes to fully terminate
        time.sleep(3)
        return True
        
    except Exception as e:
        print(f"❌ Error killing Chrome processes: {e}")
        return False

def start_chrome_with_debugging():
    """Start Chrome with debugging enabled."""
    print("\n🚀 Starting Chrome with debugging...")
    
    chrome_path = r"C:\Program Files\Google\Chrome Dev\Application\chrome.exe"
    
    # Try with fresh profile first (most likely to work)
    command = [
        chrome_path,
        "--remote-debugging-port=9222",
        "--user-data-dir=C:\\temp\\chrome-debug-udio",
        "https://www.udio.com/login"
    ]
    
    print(f"📝 Command: {' '.join(command)}")
    
    try:
        # Start Chrome process
        subprocess.Popen(command)
        print("✅ Chrome started with debugging enabled")
        print("⏳ Waiting 5 seconds for Chrome to initialize...")
        time.sleep(5)
        return True
        
    except Exception as e:
        print(f"❌ Error starting Chrome: {e}")
        return False

def verify_debugging():
    """Verify that debugging is working."""
    print("\n🔍 Verifying debugging connection...")
    
    try:
        response = requests.get("http://localhost:9222/json", timeout=10)
        
        if response.status_code == 200:
            tabs = response.json()
            print(f"✅ Debugging connection successful!")
            print(f"📱 Found {len(tabs)} browser tabs/windows")
            
            # Show current tabs
            for i, tab in enumerate(tabs[:3]):
                title = tab.get('title', 'No title')[:40]
                url = tab.get('url', 'No URL')[:50]
                print(f"   Tab {i+1}: {title} - {url}")
            
            return True
        else:
            print(f"❌ Debugging endpoint returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to debugging endpoint")
        print("   Chrome may not have started with debugging enabled")
        return False
    except Exception as e:
        print(f"❌ Error verifying debugging: {e}")
        return False

def provide_next_steps():
    """Provide next steps for the user."""
    print("\n📋 Next Steps:")
    print("1. 🌐 Chrome should now be open with a fresh profile")
    print("2. 🔐 Navigate to https://www.udio.com/login")
    print("3. 📧 Login with: user@example.com")
    print("4. 📚 Go to: https://www.udio.com/library")
    print("5. 🤖 Run: python scripts/ui_mapper_attach.py")
    print("\n💡 Note: You're using a fresh Chrome profile, so you'll need to login again")

def main():
    print("🔧 Chrome Debugging Setup")
    print("=" * 40)
    
    # Step 1: Kill existing Chrome processes
    if not kill_chrome_processes():
        print("❌ Failed to close Chrome processes. Please close Chrome manually.")
        return
    
    # Step 2: Start Chrome with debugging
    if not start_chrome_with_debugging():
        print("❌ Failed to start Chrome with debugging")
        return
    
    # Step 3: Verify debugging is working
    if verify_debugging():
        print("\n🎉 SUCCESS! Chrome debugging is now enabled")
        provide_next_steps()
    else:
        print("\n❌ FAILED: Chrome debugging is not working")
        print("\n🔧 Troubleshooting:")
        print("1. Try running this script as Administrator")
        print("2. Check Windows Firewall settings")
        print("3. Try with regular Chrome instead of Chrome Dev")
        print("4. Manually run: chrome --remote-debugging-port=9222")

if __name__ == "__main__":
    main()