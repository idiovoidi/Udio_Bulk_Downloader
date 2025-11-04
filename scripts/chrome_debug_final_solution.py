#!/usr/bin/env python3
"""
Chrome Debug Final Solution - Try multiple approaches to get debugging working.
"""

import subprocess
import time
import requests
import psutil
import os
from pathlib import Path


class ChromeDebugFinalSolution:
    """Final comprehensive solution for Chrome debugging."""
    
    def __init__(self):
        self.chrome_paths = [
            r"C:\Program Files\Google\Chrome Dev\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome Dev\Application\chrome.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        self.debug_ports = [9222, 9223, 9224, 9225]
        self.working_config = None
    
    def find_chrome_executable(self):
        """Find working Chrome executable."""
        print("🔍 Finding Chrome executable...")
        
        for chrome_path in self.chrome_paths:
            if Path(chrome_path).exists():
                print(f"   ✅ Found: {chrome_path}")
                try:
                    # Test if it can run
                    result = subprocess.run([chrome_path, "--version"], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        print(f"      Version: {version}")
                        return chrome_path
                    else:
                        print(f"      ❌ Cannot run: {chrome_path}")
                except Exception as e:
                    print(f"      ❌ Error testing: {e}")
            else:
                print(f"   ❌ Not found: {chrome_path}")
        
        return None
    
    def kill_all_chrome(self):
        """Kill all Chrome processes completely."""
        print("🔄 Killing all Chrome processes...")
        
        # First try graceful termination
        killed = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'chrome' in proc.info['name'].lower():
                    proc.terminate()
                    killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if killed > 0:
            print(f"   Terminated {killed} Chrome processes")
            time.sleep(3)
        
        # Then force kill any remaining
        remaining = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'chrome' in proc.info['name'].lower():
                    proc.kill()
                    remaining += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if remaining > 0:
            print(f"   Force killed {remaining} remaining processes")
            time.sleep(2)
        
        print("   ✅ All Chrome processes terminated")
    
    def test_chrome_debug_config(self, chrome_path, port, additional_flags=None):
        """Test a specific Chrome debug configuration."""
        base_flags = [
            f'--remote-debugging-port={port}',
            '--no-first-run',
            '--disable-default-apps'
        ]
        
        if additional_flags:
            base_flags.extend(additional_flags)
        
        cmd = [chrome_path] + base_flags
        
        print(f"   🧪 Testing port {port} with flags: {' '.join(base_flags)}")
        
        try:
            # Start Chrome
            process = subprocess.Popen(cmd, 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
            
            # Wait for startup
            time.sleep(5)
            
            # Test connection
            try:
                response = requests.get(f"http://localhost:{port}/json", timeout=3)
                if response.status_code == 200:
                    tabs = response.json()
                    print(f"      ✅ SUCCESS on port {port} ({len(tabs)} tabs)")
                    
                    # Kill this test instance
                    process.terminate()
                    time.sleep(1)
                    
                    return {
                        'chrome_path': chrome_path,
                        'port': port,
                        'flags': base_flags,
                        'success': True
                    }
                else:
                    print(f"      ❌ Port {port} returned status {response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"      ❌ Cannot connect to port {port}")
            except Exception as e:
                print(f"      ❌ Error testing port {port}: {e}")
            
            # Clean up failed attempt
            process.terminate()
            time.sleep(1)
            
        except Exception as e:
            print(f"      ❌ Error starting Chrome: {e}")
        
        return None
    
    def find_working_configuration(self):
        """Find a working Chrome debug configuration."""
        print("🔧 Finding working Chrome debug configuration...")
        
        chrome_path = self.find_chrome_executable()
        if not chrome_path:
            print("❌ No working Chrome executable found")
            return None
        
        print(f"   Using Chrome: {chrome_path}")
        
        # Test different configurations
        configurations = [
            # Basic configurations
            {'flags': None},
            {'flags': ['--headless']},
            {'flags': ['--disable-web-security']},
            {'flags': ['--no-sandbox']},
            {'flags': ['--disable-features=VizDisplayCompositor']},
            
            # Combined configurations
            {'flags': ['--headless', '--disable-web-security']},
            {'flags': ['--no-sandbox', '--disable-web-security']},
        ]
        
        for port in self.debug_ports:
            print(f"\n🔍 Testing port {port}:")
            
            # Kill any existing Chrome processes
            self.kill_all_chrome()
            
            for config in configurations:
                result = self.test_chrome_debug_config(chrome_path, port, config['flags'])
                if result:
                    print(f"   🎉 Found working configuration!")
                    return result
        
        return None
    
    def start_final_chrome_session(self, config):
        """Start Chrome with the working configuration for actual use."""
        print("🚀 Starting final Chrome session...")
        
        # Kill existing processes
        self.kill_all_chrome()
        
        # Start Chrome with working config
        cmd = [config['chrome_path']] + config['flags'] + ['https://www.udio.com/library']
        
        print(f"   Command: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(cmd, 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
            
            print(f"   ✅ Chrome started with PID {process.pid}")
            
            # Wait for startup
            time.sleep(5)
            
            # Verify it's working
            try:
                response = requests.get(f"http://localhost:{config['port']}/json", timeout=5)
                if response.status_code == 200:
                    tabs = response.json()
                    print(f"   ✅ Debug connection verified ({len(tabs)} tabs)")
                    
                    # Look for Udio tabs
                    udio_tabs = [tab for tab in tabs if 'udio.com' in tab.get('url', '').lower()]
                    if udio_tabs:
                        print(f"   🎵 Found {len(udio_tabs)} Udio tabs:")
                        for tab in udio_tabs:
                            title = tab.get('title', 'No title')[:40]
                            url = tab.get('url', 'No URL')[:50]
                            print(f"      - {title}: {url}")
                    else:
                        print("   ⏳ Udio page may still be loading...")
                    
                    return True
                else:
                    print(f"   ❌ Debug connection failed: status {response.status_code}")
                    return False
            except Exception as e:
                print(f"   ❌ Debug connection failed: {e}")
                return False
                
        except Exception as e:
            print(f"   ❌ Failed to start Chrome: {e}")
            return False
    
    def run_final_solution(self):
        """Run the complete final solution."""
        print("🔧 Chrome Debug Final Solution")
        print("=" * 50)
        
        # Step 1: Find working configuration
        config = self.find_working_configuration()
        
        if not config:
            print("\n❌ FAILED: No working Chrome debug configuration found")
            print("\n🔧 Manual troubleshooting suggestions:")
            print("   1. Try running Chrome manually:")
            print("      chrome --remote-debugging-port=9222")
            print("   2. Check Windows Defender/Firewall settings")
            print("   3. Try running as administrator")
            print("   4. Try different Chrome version (stable instead of dev)")
            return False
        
        print(f"\n✅ FOUND WORKING CONFIGURATION:")
        print(f"   Chrome: {config['chrome_path']}")
        print(f"   Port: {config['port']}")
        print(f"   Flags: {' '.join(config['flags'])}")
        
        # Step 2: Start final session
        if self.start_final_chrome_session(config):
            print(f"\n🎉 SUCCESS!")
            print(f"   Chrome is running with debug on port {config['port']}")
            print(f"   Udio should be loading...")
            print(f"\n🎯 Next steps:")
            print(f"   1. Wait for Udio to load completely")
            print(f"   2. Log in with: idiovoidi@gmail.com")
            print(f"   3. Run UI mapper: python scripts/ui_mapper_attach.py --debug-port {config['port']}")
            
            # Save working config for future use
            self.working_config = config
            return True
        else:
            print(f"\n❌ Failed to start final Chrome session")
            return False


def main():
    """Run the final solution."""
    solution = ChromeDebugFinalSolution()
    
    print("This is the final comprehensive solution to get Chrome debugging working.")
    print("It will test multiple Chrome versions, ports, and flag combinations.")
    print()
    
    success = solution.run_final_solution()
    
    if success:
        print("\n🎉 Chrome debugging is now working!")
        print("🎵 Ready to map Udio UI!")
    else:
        print("\n🔧 All attempts failed - manual intervention needed")


if __name__ == "__main__":
    main()