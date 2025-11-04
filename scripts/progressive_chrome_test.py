#!/usr/bin/env python3
"""
Progressive Chrome Testing - Test Chrome with gradually increasing complexity.
"""

import subprocess
import time
import requests
import psutil
from pathlib import Path


class ProgressiveChromeTest:
    """Test Chrome with progressively more complex flag combinations."""
    
    def __init__(self):
        self.chrome_path = r"C:\Program Files\Google\Chrome Dev\Application\chrome.exe"
        self.user_data_dir = r"C:\Users\Mitchell\AppData\Local\Google\Chrome Dev\User Data"
        self.debug_port = 9222
        self.current_process = None
    
    def kill_chrome(self):
        """Kill all Chrome processes."""
        for proc in psutil.process_iter(['name']):
            try:
                if 'chrome' in proc.info['name'].lower():
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        time.sleep(2)
    
    def test_chrome_config(self, config_name, flags, url=None):
        """Test a specific Chrome configuration."""
        print(f"\n🧪 Testing: {config_name}")
        print(f"   Flags: {' '.join(flags)}")
        
        self.kill_chrome()
        
        cmd = [self.chrome_path] + flags
        if url:
            cmd.append(url)
        
        try:
            # Start Chrome
            process = subprocess.Popen(cmd, 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
            self.current_process = process
            
            # Wait for startup
            time.sleep(4)
            
            # Test debug connection
            try:
                response = requests.get(f"http://localhost:{self.debug_port}/json", timeout=5)
                if response.status_code == 200:
                    tabs = response.json()
                    print(f"   ✅ SUCCESS: Debug port accessible ({len(tabs)} tabs)")
                    
                    # Check for Udio tabs if URL was provided
                    if url and 'udio.com' in url:
                        udio_tabs = [tab for tab in tabs if 'udio.com' in tab.get('url', '').lower()]
                        if udio_tabs:
                            print(f"   🎵 Found {len(udio_tabs)} Udio tabs")
                            for tab in udio_tabs:
                                title = tab.get('title', 'No title')[:40]
                                tab_url = tab.get('url', 'No URL')[:50]
                                print(f"      - {title}: {tab_url}")
                        else:
                            print("   ⚠️  No Udio tabs found yet (may still be loading)")
                    
                    return True
                else:
                    print(f"   ❌ FAILED: Debug port returned status {response.status_code}")
                    return False
                    
            except requests.exceptions.ConnectionError:
                print("   ❌ FAILED: Cannot connect to debug port")
                return False
            except Exception as e:
                print(f"   ❌ FAILED: Error testing debug connection: {e}")
                return False
                
        except Exception as e:
            print(f"   ❌ FAILED: Error starting Chrome: {e}")
            return False
    
    def run_progressive_tests(self):
        """Run progressive tests from simple to complex."""
        print("🔧 Progressive Chrome Configuration Testing")
        print("=" * 60)
        
        test_configs = [
            # Test 1: Minimal (we know this works)
            {
                'name': 'Minimal (Headless)',
                'flags': ['--remote-debugging-port=9222', '--headless'],
                'url': None
            },
            
            # Test 2: Add user data dir
            {
                'name': 'With User Data Dir',
                'flags': [
                    '--remote-debugging-port=9222',
                    f'--user-data-dir={self.user_data_dir}',
                    '--headless'
                ],
                'url': None
            },
            
            # Test 3: Add Default profile (instead of Profile 2)
            {
                'name': 'With Default Profile',
                'flags': [
                    '--remote-debugging-port=9222',
                    f'--user-data-dir={self.user_data_dir}',
                    '--profile-directory=Default',
                    '--headless'
                ],
                'url': None
            },
            
            # Test 4: Try Profile 2 (the problematic one)
            {
                'name': 'With Profile 2',
                'flags': [
                    '--remote-debugging-port=9222',
                    f'--user-data-dir={self.user_data_dir}',
                    '--profile-directory=Profile 2',
                    '--headless'
                ],
                'url': None
            },
            
            # Test 5: Remove headless (show UI)
            {
                'name': 'Profile 2 with UI',
                'flags': [
                    '--remote-debugging-port=9222',
                    f'--user-data-dir={self.user_data_dir}',
                    '--profile-directory=Profile 2'
                ],
                'url': None
            },
            
            # Test 6: Add Udio URL
            {
                'name': 'Profile 2 + Udio URL',
                'flags': [
                    '--remote-debugging-port=9222',
                    f'--user-data-dir={self.user_data_dir}',
                    '--profile-directory=Profile 2'
                ],
                'url': 'https://www.udio.com/library'
            },
            
            # Test 7: Add safe flags
            {
                'name': 'Profile 2 + Safe Flags',
                'flags': [
                    '--remote-debugging-port=9222',
                    f'--user-data-dir={self.user_data_dir}',
                    '--profile-directory=Profile 2',
                    '--no-first-run',
                    '--no-default-browser-check'
                ],
                'url': 'https://www.udio.com/library'
            },
            
            # Test 8: Add potentially problematic flags one by one
            {
                'name': 'Profile 2 + Disable Web Security',
                'flags': [
                    '--remote-debugging-port=9222',
                    f'--user-data-dir={self.user_data_dir}',
                    '--profile-directory=Profile 2',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--disable-web-security'
                ],
                'url': 'https://www.udio.com/library'
            },
            
            # Test 9: Add no-sandbox
            {
                'name': 'Profile 2 + No Sandbox',
                'flags': [
                    '--remote-debugging-port=9222',
                    f'--user-data-dir={self.user_data_dir}',
                    '--profile-directory=Profile 2',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--disable-web-security',
                    '--no-sandbox'
                ],
                'url': 'https://www.udio.com/library'
            }
        ]
        
        results = []
        successful_configs = []
        
        for config in test_configs:
            success = self.test_chrome_config(
                config['name'], 
                config['flags'], 
                config.get('url')
            )
            
            results.append({
                'name': config['name'],
                'success': success,
                'flags': config['flags']
            })
            
            if success:
                successful_configs.append(config)
            
            # Small delay between tests
            time.sleep(1)
        
        # Summary
        print("\n" + "=" * 60)
        print("PROGRESSIVE TEST RESULTS")
        print("=" * 60)
        
        successful_count = sum(1 for r in results if r['success'])
        print(f"✅ Successful configurations: {successful_count}/{len(results)}")
        
        print("\n📊 Results:")
        for result in results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"   {status}: {result['name']}")
        
        if successful_configs:
            print(f"\n🎯 RECOMMENDED CONFIGURATION:")
            # Use the most complex successful configuration
            best_config = successful_configs[-1]
            print(f"   Name: {best_config['name']}")
            print(f"   Flags: {' '.join(best_config['flags'])}")
            
            if best_config.get('url'):
                print(f"   URL: {best_config['url']}")
            
            # Generate command
            cmd_parts = [f'"{self.chrome_path}"'] + best_config['flags']
            if best_config.get('url'):
                cmd_parts.append(f'"{best_config["url"]}"')
            
            print(f"\n📋 COMMAND TO USE:")
            print(' '.join(cmd_parts))
            
        else:
            print("\n❌ No successful configurations found!")
        
        # Clean up
        self.kill_chrome()
        
        return results, successful_configs


def main():
    """Run progressive Chrome testing."""
    tester = ProgressiveChromeTest()
    
    print("This will test Chrome configurations progressively")
    print("from simple to complex to find the optimal setup.")
    print()
    
    print("Starting progressive testing...")
    
    results, successful_configs = tester.run_progressive_tests()
    
    if successful_configs:
        print(f"\n🎉 Found {len(successful_configs)} working configurations!")
        print("🎵 Ready to proceed with Udio UI mapping!")
    else:
        print("\n🔧 No working configurations found - manual troubleshooting needed")


if __name__ == "__main__":
    main()