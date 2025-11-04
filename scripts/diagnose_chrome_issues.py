#!/usr/bin/env python3
"""
Diagnose Chrome Dev debugging issues related to user account isolation.
"""

import os
import json
import subprocess
import requests
from pathlib import Path
import psutil
import getpass


class ChromeDebugDiagnostic:
    """Diagnose Chrome debugging setup issues."""
    
    def __init__(self):
        self.current_user = getpass.getuser()
        self.issues = []
        self.recommendations = []
    
    def check_current_user_context(self):
        """Check current Windows user context."""
        print("🔍 Checking User Context...")
        
        user_info = {
            "current_user": self.current_user,
            "user_profile": os.environ.get("USERPROFILE", "Unknown"),
            "appdata_local": os.environ.get("LOCALAPPDATA", "Unknown"),
            "appdata_roaming": os.environ.get("APPDATA", "Unknown"),
            "username_env": os.environ.get("USERNAME", "Unknown")
        }
        
        print(f"   Current User: {user_info['current_user']}")
        print(f"   User Profile: {user_info['user_profile']}")
        print(f"   Local AppData: {user_info['appdata_local']}")
        
        return user_info
    
    def check_chrome_processes(self):
        """Check running Chrome processes and their details."""
        print("\n🔍 Checking Chrome Processes...")
        
        chrome_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'username']):
            try:
                if 'chrome' in proc.info['name'].lower():
                    chrome_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else '',
                        'username': proc.info.get('username', 'Unknown')
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        print(f"   Found {len(chrome_processes)} Chrome processes")
        
        debug_enabled_processes = []
        for proc in chrome_processes:
            if '--remote-debugging-port' in proc['cmdline']:
                debug_enabled_processes.append(proc)
                print(f"   ✅ Debug-enabled: PID {proc['pid']} (User: {proc['username']})")
                print(f"      Command: {proc['cmdline'][:100]}...")
            else:
                print(f"   ❌ No debug: PID {proc['pid']} (User: {proc['username']})")
        
        if not debug_enabled_processes:
            self.issues.append("No Chrome processes found with remote debugging enabled")
            self.recommendations.append("Start Chrome with --remote-debugging-port=9222")
        
        return chrome_processes, debug_enabled_processes
    
    def check_debug_port_accessibility(self):
        """Check if debug port is accessible."""
        print("\n🔍 Checking Debug Port Accessibility...")
        
        port_status = {}
        
        # Check if port is listening
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 9222))
            sock.close()
            
            if result == 0:
                port_status['listening'] = True
                print("   ✅ Port 9222 is listening")
            else:
                port_status['listening'] = False
                print("   ❌ Port 9222 is not listening")
                self.issues.append("Debug port 9222 is not listening")
        except Exception as e:
            port_status['listening'] = False
            print(f"   ❌ Error checking port: {e}")
        
        # Try to access debug endpoint
        try:
            response = requests.get("http://localhost:9222/json", timeout=5)
            if response.status_code == 200:
                tabs = response.json()
                port_status['accessible'] = True
                port_status['tab_count'] = len(tabs)
                print(f"   ✅ Debug endpoint accessible ({len(tabs)} tabs)")
                
                # Check for Udio tabs
                udio_tabs = [tab for tab in tabs if 'udio.com' in tab.get('url', '').lower()]
                if udio_tabs:
                    print(f"   ✅ Found {len(udio_tabs)} Udio tabs")
                    for tab in udio_tabs:
                        print(f"      - {tab.get('title', 'No title')}: {tab.get('url', 'No URL')}")
                else:
                    print("   ⚠️  No Udio tabs found")
                    self.recommendations.append("Navigate to https://www.udio.com/library in Chrome")
            else:
                port_status['accessible'] = False
                print(f"   ❌ Debug endpoint returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            port_status['accessible'] = False
            print("   ❌ Cannot connect to debug endpoint")
            self.issues.append("Cannot connect to Chrome debug endpoint")
        except Exception as e:
            port_status['accessible'] = False
            print(f"   ❌ Error accessing debug endpoint: {e}")
        
        return port_status
    
    def check_profile_paths(self):
        """Check Chrome profile paths and accessibility."""
        print("\n🔍 Checking Chrome Profile Paths...")
        
        profile_info = {}
        
        # Expected profile locations
        expected_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome Dev\User Data"),
            os.path.expandvars(r"%APPDATA%\Google\Chrome Dev\User Data"),
        ]
        
        for path in expected_paths:
            path_obj = Path(path)
            if path_obj.exists():
                profile_info[path] = {
                    'exists': True,
                    'readable': os.access(path, os.R_OK),
                    'writable': os.access(path, os.W_OK),
                    'profiles': []
                }
                
                print(f"   ✅ Found: {path}")
                print(f"      Readable: {profile_info[path]['readable']}")
                print(f"      Writable: {profile_info[path]['writable']}")
                
                # List profiles
                try:
                    for item in path_obj.iterdir():
                        if item.is_dir() and (item.name.startswith("Profile") or item.name == "Default"):
                            profile_info[path]['profiles'].append({
                                'name': item.name,
                                'path': str(item),
                                'size': sum(f.stat().st_size for f in item.rglob('*') if f.is_file()) / (1024*1024)
                            })
                            print(f"      Profile: {item.name} ({profile_info[path]['profiles'][-1]['size']:.1f} MB)")
                except PermissionError:
                    print(f"      ❌ Permission denied accessing profiles")
                    self.issues.append(f"Cannot access Chrome profiles in {path}")
            else:
                profile_info[path] = {'exists': False}
                print(f"   ❌ Not found: {path}")
        
        return profile_info
    
    def check_selenium_compatibility(self):
        """Check Selenium setup and compatibility."""
        print("\n🔍 Checking Selenium Compatibility...")
        
        selenium_info = {}
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            
            selenium_info['selenium_available'] = True
            print("   ✅ Selenium is available")
            
            # Try to connect to existing Chrome session
            try:
                options = ChromeOptions()
                options.add_experimental_option("debuggerAddress", "localhost:9222")
                
                # Don't actually create driver, just test options
                selenium_info['options_valid'] = True
                print("   ✅ Chrome options configured correctly")
                
                # Try actual connection (brief test)
                try:
                    driver = webdriver.Chrome(options=options)
                    current_url = driver.current_url
                    title = driver.title
                    
                    selenium_info['connection_successful'] = True
                    selenium_info['current_url'] = current_url
                    selenium_info['title'] = title
                    
                    print(f"   ✅ Successfully connected to Chrome session")
                    print(f"      Current page: {title}")
                    print(f"      URL: {current_url}")
                    
                    # Don't quit - we're using existing session
                    
                except Exception as e:
                    selenium_info['connection_successful'] = False
                    selenium_info['connection_error'] = str(e)
                    print(f"   ❌ Failed to connect: {e}")
                    self.issues.append(f"Selenium cannot connect to Chrome: {e}")
                    
            except Exception as e:
                selenium_info['options_valid'] = False
                print(f"   ❌ Chrome options error: {e}")
                
        except ImportError as e:
            selenium_info['selenium_available'] = False
            print(f"   ❌ Selenium not available: {e}")
            self.issues.append("Selenium is not installed or not accessible")
        
        return selenium_info
    
    def generate_recommendations(self):
        """Generate specific recommendations based on findings."""
        print("\n💡 Generating Recommendations...")
        
        if self.issues:
            print("\n❌ Issues Found:")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        
        if self.recommendations:
            print("\n🔧 Recommendations:")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"   {i}. {rec}")
        
        # Additional context-specific recommendations
        print("\n🎯 Specific Solutions:")
        
        if "No Chrome processes found with remote debugging enabled" in self.issues:
            print("   → Start Chrome with debugging:")
            print("     scripts/start_chrome_profile2_debug.bat")
        
        if "Cannot connect to Chrome debug endpoint" in self.issues:
            print("   → Check if Chrome is running with correct flags:")
            print("     tasklist | findstr chrome.exe")
            print("     netstat -an | findstr :9222")
        
        if any("Cannot access Chrome profiles" in issue for issue in self.issues):
            print("   → Run as administrator or check permissions:")
            print("     Right-click Command Prompt → Run as administrator")
        
        print("\n🔄 User Account Isolation Solutions:")
        print("   1. Ensure Chrome is started from the same user account as this script")
        print("   2. Use --user-data-dir to specify exact profile path")
        print("   3. Consider running both Chrome and scripts as administrator")
        print("   4. Verify Windows DPAPI encryption compatibility")
    
    def run_full_diagnostic(self):
        """Run complete diagnostic check."""
        print("🔧 Chrome Dev Debugging Diagnostic Tool")
        print("=" * 50)
        
        results = {}
        
        # Run all checks
        results['user_context'] = self.check_current_user_context()
        results['chrome_processes'] = self.check_chrome_processes()
        results['port_status'] = self.check_debug_port_accessibility()
        results['profile_info'] = self.check_profile_paths()
        results['selenium_info'] = self.check_selenium_compatibility()
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Save results
        results_file = Path("diagnostic_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📁 Diagnostic results saved to: {results_file}")
        
        return results


def main():
    """Run the diagnostic tool."""
    diagnostic = ChromeDebugDiagnostic()
    results = diagnostic.run_full_diagnostic()
    
    # Summary
    print("\n" + "=" * 50)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if diagnostic.issues:
        print(f"❌ {len(diagnostic.issues)} issues found")
        print("🔧 Check recommendations above for solutions")
    else:
        print("✅ No major issues detected")
        print("🎉 Chrome debugging should be working!")


if __name__ == "__main__":
    main()