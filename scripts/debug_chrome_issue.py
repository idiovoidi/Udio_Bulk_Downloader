#!/usr/bin/env python3
"""
Systematic Chrome debugging issue analysis.
"""

import subprocess
import requests
import time
import psutil
from pathlib import Path

def check_chrome_processes():
    """Check all running Chrome processes and their command lines."""
    print("🔍 Analyzing Chrome processes...")
    
    chrome_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                chrome_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if not chrome_processes:
        print("❌ No Chrome processes found")
        return False
    
    print(f"📊 Found {len(chrome_processes)} Chrome processes")
    
    debugging_enabled = False
    for proc in chrome_processes:
        cmdline = ' '.join(proc['cmdline']) if proc['cmdline'] else 'N/A'
        if '--remote-debugging-port' in cmdline:
            print(f"✅ Process {proc['pid']}: Debugging enabled")
            print(f"   Command: {cmdline}")
            debugging_enabled = True
        else:
            print(f"⚪ Process {proc['pid']}: No debugging flag")
    
    return debugging_enabled

def check_port_accessibility():
    """Check if port 9222 is accessible."""
    print("\n🌐 Checking port 9222 accessibility...")
    
    try:
        response = requests.get("http://localhost:9222/json", timeout=5)
        print(f"✅ Port 9222 is accessible (Status: {response.status_code})")
        
        if response.status_code == 200:
            tabs = response.json()
            print(f"📱 Found {len(tabs)} browser tabs/windows")
            return True
        else:
            print(f"⚠️  Port accessible but returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Port 9222 is not accessible (Connection refused)")
        return False
    except Exception as e:
        print(f"❌ Error checking port: {e}")
        return False

def check_firewall_and_network():
    """Check if Windows firewall or network settings might block the port."""
    print("\n🛡️  Checking network/firewall status...")
    
    try:
        # Check if port is listening
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        if ':9222' in result.stdout:
            print("✅ Port 9222 is listening")
            return True
        else:
            print("❌ Port 9222 is not listening")
            return False
    except Exception as e:
        print(f"⚠️  Could not check network status: {e}")
        return False

def test_chrome_startup_methods():
    """Test different methods of starting Chrome with debugging."""
    print("\n🧪 Testing Chrome startup methods...")
    
    chrome_path = r"C:\Program Files\Google\Chrome Dev\Application\chrome.exe"
    user_data_dir = r"C:\Users\Mitchell\AppData\Local\Google\Chrome Dev\User Data"
    
    methods = [
        {
            "name": "Method 1: Basic debugging flag",
            "command": [chrome_path, "--remote-debugging-port=9222"]
        },
        {
            "name": "Method 2: With user data dir",
            "command": [chrome_path, "--remote-debugging-port=9222", f"--user-data-dir={user_data_dir}"]
        },
        {
            "name": "Method 3: With specific profile",
            "command": [chrome_path, "--remote-debugging-port=9222", f"--user-data-dir={user_data_dir}", "--profile-directory=Profile 2"]
        },
        {
            "name": "Method 4: With new user data dir",
            "command": [chrome_path, "--remote-debugging-port=9222", "--user-data-dir=C:\\temp\\chrome-debug-test"]
        }
    ]
    
    for method in methods:
        print(f"\n🔧 {method['name']}")
        print(f"   Command: {' '.join(method['command'])}")
        
        # Don't actually run these - just show what we would test
        print("   (Test command prepared - not executed)")

def analyze_chrome_dev_differences():
    """Analyze potential differences between Chrome Dev and regular Chrome."""
    print("\n🔬 Analyzing Chrome Dev specifics...")
    
    chrome_path = Path(r"C:\Program Files\Google\Chrome Dev\Application\chrome.exe")
    
    if chrome_path.exists():
        print(f"✅ Chrome Dev executable found: {chrome_path}")
        
        # Check file properties
        try:
            stat = chrome_path.stat()
            print(f"   File size: {stat.st_size:,} bytes")
            print(f"   Modified: {time.ctime(stat.st_mtime)}")
        except Exception as e:
            print(f"   Could not get file stats: {e}")
    else:
        print(f"❌ Chrome Dev executable not found: {chrome_path}")
    
    print("\n💡 Chrome Dev considerations:")
    print("   - Chrome Dev may have different flag handling")
    print("   - May require different debugging setup")
    print("   - Could have additional security restrictions")
    print("   - Might need --disable-web-security for debugging")

def provide_recommendations():
    """Provide step-by-step recommendations."""
    print("\n📋 Systematic Troubleshooting Steps:")
    print("\n1. **Complete Chrome Shutdown**")
    print("   - Close ALL Chrome windows and tabs")
    print("   - Check Task Manager for remaining chrome.exe processes")
    print("   - Kill any remaining Chrome processes")
    
    print("\n2. **Test with Minimal Command**")
    print('   - Run: "C:\\Program Files\\Google\\Chrome Dev\\Application\\chrome.exe" --remote-debugging-port=9222')
    print("   - Wait 5 seconds")
    print("   - Test: curl http://localhost:9222/json")
    
    print("\n3. **Test with New Profile**")
    print("   - Use --user-data-dir=C:\\temp\\chrome-debug-test")
    print("   - This eliminates profile conflicts")
    
    print("\n4. **Check Chrome Dev Specific Issues**")
    print("   - Try regular Chrome instead of Chrome Dev")
    print("   - Chrome Dev might have different debugging behavior")
    
    print("\n5. **Network/Security Check**")
    print("   - Disable Windows Firewall temporarily")
    print("   - Check antivirus software")
    print("   - Try different port (--remote-debugging-port=9223)")

def main():
    print("🔧 Chrome Remote Debugging Issue Analysis")
    print("=" * 50)
    
    # Step 1: Check current Chrome processes
    has_debugging = check_chrome_processes()
    
    # Step 2: Check port accessibility
    port_accessible = check_port_accessibility()
    
    # Step 3: Check network/firewall
    port_listening = check_firewall_and_network()
    
    # Step 4: Analyze Chrome Dev specifics
    analyze_chrome_dev_differences()
    
    # Step 5: Test methods (preparation only)
    test_chrome_startup_methods()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 ANALYSIS SUMMARY")
    print(f"   Chrome processes with debugging: {'Yes' if has_debugging else 'No'}")
    print(f"   Port 9222 accessible: {'Yes' if port_accessible else 'No'}")
    print(f"   Port 9222 listening: {'Yes' if port_listening else 'No'}")
    
    if not any([has_debugging, port_accessible, port_listening]):
        print("\n❌ ISSUE IDENTIFIED: Chrome is not starting with debugging enabled")
        print("   Root cause: The --remote-debugging-port flag is not taking effect")
    
    # Provide recommendations
    provide_recommendations()

if __name__ == "__main__":
    main()