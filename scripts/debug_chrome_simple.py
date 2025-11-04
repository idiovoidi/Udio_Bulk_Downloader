#!/usr/bin/env python3
"""
Simple Chrome debugging issue analysis without external dependencies.
"""

import subprocess
import requests
import time
import json

def check_chrome_processes():
    """Check Chrome processes using Windows tasklist."""
    print("🔍 Analyzing Chrome processes...")
    
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq chrome.exe', '/FO', 'CSV'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # Header + at least one process
                chrome_count = len(lines) - 1
                print(f"📊 Found {chrome_count} Chrome processes")
                return True
            else:
                print("❌ No Chrome processes found")
                return False
        else:
            print("⚠️  Could not check Chrome processes")
            return False
            
    except Exception as e:
        print(f"❌ Error checking processes: {e}")
        return False

def check_port_accessibility():
    """Check if port 9222 is accessible."""
    print("\n🌐 Checking port 9222 accessibility...")
    
    try:
        response = requests.get("http://localhost:9222/json", timeout=5)
        print(f"✅ Port 9222 is accessible (Status: {response.status_code})")
        
        if response.status_code == 200:
            tabs = response.json()
            print(f"📱 Found {len(tabs)} browser tabs/windows")
            
            # Show some tab info
            for i, tab in enumerate(tabs[:3]):
                title = tab.get('title', 'No title')[:50]
                url = tab.get('url', 'No URL')[:60]
                print(f"   Tab {i+1}: {title} - {url}")
            
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

def check_port_listening():
    """Check if port 9222 is listening using netstat."""
    print("\n🔌 Checking if port 9222 is listening...")
    
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        if ':9222' in result.stdout:
            print("✅ Port 9222 is listening")
            
            # Find the specific line
            for line in result.stdout.split('\n'):
                if ':9222' in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print("❌ Port 9222 is not listening")
            return False
    except Exception as e:
        print(f"⚠️  Could not check port status: {e}")
        return False

def test_basic_chrome_command():
    """Test the most basic Chrome debugging command."""
    print("\n🧪 Testing basic Chrome debugging command...")
    
    chrome_path = r"C:\Program Files\Google\Chrome Dev\Application\chrome.exe"
    
    print("📝 Recommended test steps:")
    print("1. Close ALL Chrome windows completely")
    print("2. Open Command Prompt as Administrator")
    print("3. Run this exact command:")
    print(f'   "{chrome_path}" --remote-debugging-port=9222')
    print("4. Wait 5 seconds")
    print("5. Test with: curl http://localhost:9222/json")
    print("   Or visit: http://localhost:9222 in another browser")

def analyze_potential_issues():
    """Analyze potential issues preventing debugging."""
    print("\n🔬 Potential Issues Analysis:")
    
    issues = [
        {
            "issue": "Chrome Dev vs Regular Chrome",
            "description": "Chrome Dev might handle debugging flags differently",
            "solution": "Try with regular Chrome: chrome --remote-debugging-port=9222"
        },
        {
            "issue": "Existing Chrome Processes",
            "description": "Other Chrome processes might prevent debugging mode",
            "solution": "Kill ALL chrome.exe processes before starting with debugging"
        },
        {
            "issue": "Windows Security/Firewall",
            "description": "Windows might block the debugging port",
            "solution": "Temporarily disable Windows Firewall or add exception"
        },
        {
            "issue": "User Data Directory Conflicts",
            "description": "Profile conflicts might prevent debugging",
            "solution": "Use fresh profile: --user-data-dir=C:\\temp\\chrome-debug"
        },
        {
            "issue": "Administrative Privileges",
            "description": "Chrome might need admin rights for debugging",
            "solution": "Run Command Prompt as Administrator"
        }
    ]
    
    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. **{issue['issue']}**")
        print(f"   Problem: {issue['description']}")
        print(f"   Solution: {issue['solution']}")

def create_test_commands():
    """Create test commands for systematic testing."""
    print("\n📋 Systematic Test Commands:")
    
    chrome_path = r"C:\Program Files\Google\Chrome Dev\Application\chrome.exe"
    
    commands = [
        {
            "name": "Test 1: Minimal command",
            "command": f'"{chrome_path}" --remote-debugging-port=9222',
            "notes": "Most basic test - close all Chrome first"
        },
        {
            "name": "Test 2: With fresh profile",
            "command": f'"{chrome_path}" --remote-debugging-port=9222 --user-data-dir=C:\\temp\\chrome-debug',
            "notes": "Eliminates profile conflicts"
        },
        {
            "name": "Test 3: Different port",
            "command": f'"{chrome_path}" --remote-debugging-port=9223',
            "notes": "Test if port 9222 is blocked"
        },
        {
            "name": "Test 4: Regular Chrome",
            "command": 'chrome --remote-debugging-port=9222',
            "notes": "Test with regular Chrome instead of Dev"
        }
    ]
    
    for cmd in commands:
        print(f"\n🔧 {cmd['name']}")
        print(f"   Command: {cmd['command']}")
        print(f"   Notes: {cmd['notes']}")
        print(f"   Test: curl http://localhost:9222/json (after 5 seconds)")

def main():
    print("🔧 Chrome Remote Debugging Issue Analysis")
    print("=" * 60)
    
    # Current state analysis
    has_chrome = check_chrome_processes()
    port_accessible = check_port_accessibility()
    port_listening = check_port_listening()
    
    # Analysis
    analyze_potential_issues()
    
    # Test commands
    create_test_commands()
    
    # Summary and next steps
    print("\n" + "=" * 60)
    print("📊 CURRENT STATE SUMMARY")
    print(f"   Chrome processes running: {'Yes' if has_chrome else 'No'}")
    print(f"   Port 9222 accessible: {'Yes' if port_accessible else 'No'}")
    print(f"   Port 9222 listening: {'Yes' if port_listening else 'No'}")
    
    if not port_accessible and not port_listening:
        print("\n❌ DIAGNOSIS: Chrome debugging is not enabled")
        print("   The --remote-debugging-port flag is not taking effect")
        print("\n🎯 NEXT STEPS:")
        print("   1. Close ALL Chrome windows and processes")
        print("   2. Try Test 1 (minimal command) first")
        print("   3. If that fails, try Test 2 (fresh profile)")
        print("   4. Check Windows Firewall if still failing")
    
    print("\n💡 TIP: Run commands in Administrator Command Prompt for best results")

if __name__ == "__main__":
    main()