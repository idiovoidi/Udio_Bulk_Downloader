#!/usr/bin/env python3
"""
Comprehensive Debug Check - Investigate all potential issues before changing ports.
"""

import os
import subprocess
import psutil
import socket
import time
import winreg
import json
from pathlib import Path
import requests


class ComprehensiveDebugChecker:
    """Comprehensive checker for Chrome debugging issues."""
    
    def __init__(self):
        self.debug_port = 9222
        self.chrome_path = r"C:\Program Files\Google\Chrome Dev\Application\chrome.exe"
        self.user_data_dir = r"C:\Users\Mitchell\AppData\Local\Google\Chrome Dev\User Data"
        self.profile = "Profile 2"
        self.issues = []
        self.warnings = []
        self.info = []
    
    def check_chrome_version_compatibility(self):
        """Check Chrome version and known debugging issues."""
        print("🔍 Checking Chrome Version and Compatibility...")
        
        try:
            # Get Chrome version
            result = subprocess.run([self.chrome_path, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"   ✅ Chrome Version: {version}")
                
                # Check for known problematic versions
                if "dev" in version.lower():
                    self.warnings.append("Using Chrome Dev - debugging may be unstable")
                    print("   ⚠️  Chrome Dev versions can have debugging instabilities")
                
                # Extract version number for specific checks
                import re
                version_match = re.search(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', version)
                if version_match:
                    major = int(version_match.group(1))
                    if major >= 120:
                        print(f"   ✅ Chrome {major} should support remote debugging")
                    else:
                        self.warnings.append(f"Chrome {major} may have debugging limitations")
                
            else:
                self.issues.append("Cannot determine Chrome version")
                print("   ❌ Cannot determine Chrome version")
                
        except Exception as e:
            self.issues.append(f"Error checking Chrome version: {e}")
            print(f"   ❌ Error checking Chrome version: {e}")
    
    def check_system_resources(self):
        """Check system resources that might affect Chrome."""
        print("\n🔍 Checking System Resources...")
        
        # Check available memory
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        memory_available_gb = memory.available / (1024**3)
        
        print(f"   💾 Total Memory: {memory_gb:.1f} GB")
        print(f"   💾 Available Memory: {memory_available_gb:.1f} GB")
        print(f"   💾 Memory Usage: {memory.percent}%")
        
        if memory.percent > 90:
            self.warnings.append("High memory usage may affect Chrome performance")
        
        # Check disk space
        disk = psutil.disk_usage('C:')
        disk_free_gb = disk.free / (1024**3)
        
        print(f"   💽 Free Disk Space: {disk_free_gb:.1f} GB")
        
        if disk_free_gb < 1:
            self.issues.append("Very low disk space may prevent Chrome from starting")
        elif disk_free_gb < 5:
            self.warnings.append("Low disk space may affect Chrome performance")
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"   🖥️  CPU Usage: {cpu_percent}%")
        
        if cpu_percent > 90:
            self.warnings.append("High CPU usage may affect Chrome startup")
    
    def check_antivirus_interference(self):
        """Check for potential antivirus interference."""
        print("\n🔍 Checking for Antivirus Interference...")
        
        # Check Windows Defender status
        try:
            result = subprocess.run([
                'powershell', '-Command',
                'Get-MpPreference | Select-Object -Property DisableRealtimeMonitoring'
            ], capture_output=True, text=True)
            
            if "False" in result.stdout:
                print("   🛡️  Windows Defender Real-time Protection: Enabled")
                self.warnings.append("Windows Defender may interfere with Chrome debugging")
            else:
                print("   🛡️  Windows Defender Real-time Protection: Disabled")
                
        except Exception as e:
            print(f"   ⚠️  Could not check Windows Defender status: {e}")
        
        # Check for common antivirus processes
        antivirus_processes = [
            'avp.exe', 'avgnt.exe', 'avguard.exe', 'bdagent.exe', 'mbam.exe',
            'mcshield.exe', 'nortonsecurity.exe', 'avastui.exe', 'avgui.exe'
        ]
        
        running_av = []
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() in [av.lower() for av in antivirus_processes]:
                    running_av.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if running_av:
            print(f"   🛡️  Detected antivirus processes: {', '.join(running_av)}")
            self.warnings.append(f"Antivirus software may block Chrome debugging: {', '.join(running_av)}")
        else:
            print("   ✅ No common antivirus processes detected")
    
    def check_network_configuration(self):
        """Check network configuration that might affect localhost access."""
        print("\n🔍 Checking Network Configuration...")
        
        # Test localhost resolution
        try:
            import socket
            localhost_ip = socket.gethostbyname('localhost')
            print(f"   🌐 localhost resolves to: {localhost_ip}")
            
            if localhost_ip != '127.0.0.1':
                self.warnings.append(f"localhost resolves to {localhost_ip} instead of 127.0.0.1")
        except Exception as e:
            self.issues.append(f"Cannot resolve localhost: {e}")
        
        # Check if 127.0.0.1 is accessible
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 80))  # Test with port 80
            sock.close()
            
            if result == 0:
                print("   ✅ 127.0.0.1 is accessible")
            else:
                print("   ⚠️  127.0.0.1 connection test failed (normal if nothing on port 80)")
        except Exception as e:
            print(f"   ⚠️  Error testing 127.0.0.1 connectivity: {e}")
        
        # Check proxy settings
        try:
            result = subprocess.run([
                'powershell', '-Command',
                'Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" | Select-Object ProxyEnable, ProxyServer'
            ], capture_output=True, text=True)
            
            if "ProxyEnable" in result.stdout:
                if "1" in result.stdout:
                    print("   🌐 System proxy is enabled")
                    self.warnings.append("System proxy may interfere with localhost connections")
                else:
                    print("   ✅ No system proxy detected")
            
        except Exception as e:
            print(f"   ⚠️  Could not check proxy settings: {e}")
    
    def check_chrome_profile_integrity(self):
        """Check Chrome profile integrity and permissions."""
        print("\n🔍 Checking Chrome Profile Integrity...")
        
        profile_path = Path(self.user_data_dir) / self.profile
        
        if not profile_path.exists():
            self.issues.append(f"Profile '{self.profile}' does not exist")
            print(f"   ❌ Profile path does not exist: {profile_path}")
            return
        
        print(f"   ✅ Profile path exists: {profile_path}")
        
        # Check permissions
        try:
            # Test read access
            test_read = os.access(profile_path, os.R_OK)
            test_write = os.access(profile_path, os.W_OK)
            
            print(f"   📁 Read access: {'✅' if test_read else '❌'}")
            print(f"   📁 Write access: {'✅' if test_write else '❌'}")
            
            if not test_read or not test_write:
                self.issues.append("Insufficient permissions for Chrome profile")
        except Exception as e:
            self.issues.append(f"Error checking profile permissions: {e}")
        
        # Check for lock files
        lock_files = ['lockfile', 'SingletonLock', 'SingletonSocket']
        for lock_file in lock_files:
            lock_path = profile_path / lock_file
            if lock_path.exists():
                print(f"   🔒 Found lock file: {lock_file}")
                self.warnings.append(f"Profile lock file exists: {lock_file}")
        
        # Check profile size and key files
        try:
            profile_size = sum(f.stat().st_size for f in profile_path.rglob('*') if f.is_file())
            profile_size_mb = profile_size / (1024 * 1024)
            print(f"   📊 Profile size: {profile_size_mb:.1f} MB")
            
            # Check for important files
            important_files = ['Preferences', 'Local State', 'Cookies']
            for file_name in important_files:
                file_path = profile_path / file_name
                if file_path.exists():
                    print(f"   ✅ Found: {file_name}")
                else:
                    print(f"   ⚠️  Missing: {file_name}")
                    
        except Exception as e:
            print(f"   ⚠️  Error analyzing profile: {e}")
    
    def check_chrome_flags_compatibility(self):
        """Check if Chrome flags are compatible and not conflicting."""
        print("\n🔍 Checking Chrome Flags Compatibility...")
        
        flags_to_test = [
            '--remote-debugging-port=9222',
            '--user-data-dir',
            '--profile-directory',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--no-sandbox'
        ]
        
        print("   🏁 Flags to be used:")
        for flag in flags_to_test:
            print(f"      {flag}")
        
        # Check for potentially conflicting flags
        conflicting_combinations = [
            (['--no-sandbox', '--disable-web-security'], 'May cause security warnings'),
            (['--disable-features=VizDisplayCompositor'], 'May affect rendering performance')
        ]
        
        for flags, warning in conflicting_combinations:
            print(f"   ⚠️  {warning}: {', '.join(flags)}")
            self.warnings.append(f"Flag combination warning: {warning}")
    
    def check_port_alternatives(self):
        """Check alternative ports if 9222 has issues."""
        print("\n🔍 Checking Alternative Debug Ports...")
        
        alternative_ports = [9223, 9224, 9225, 9221]
        available_ports = []
        
        for port in alternative_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('localhost', port))
                sock.close()
                available_ports.append(port)
                print(f"   ✅ Port {port}: Available")
            except OSError:
                print(f"   ❌ Port {port}: In use")
        
        if available_ports:
            self.info.append(f"Alternative ports available: {available_ports}")
        else:
            self.warnings.append("No alternative debug ports available")
    
    def test_minimal_chrome_startup(self):
        """Test Chrome startup with minimal flags."""
        print("\n🧪 Testing Minimal Chrome Startup...")
        
        # Kill any existing Chrome processes
        for proc in psutil.process_iter(['name']):
            try:
                if 'chrome' in proc.info['name'].lower():
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        time.sleep(2)
        
        # Try minimal startup
        minimal_cmd = [
            self.chrome_path,
            '--remote-debugging-port=9222',
            '--headless'  # Use headless to avoid UI issues
        ]
        
        print(f"   🚀 Testing minimal command: {' '.join(minimal_cmd)}")
        
        try:
            process = subprocess.Popen(minimal_cmd, 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.PIPE)
            
            # Wait a moment for startup
            time.sleep(3)
            
            # Check if debug port is accessible
            try:
                response = requests.get("http://localhost:9222/json", timeout=5)
                if response.status_code == 200:
                    print("   ✅ Minimal Chrome startup successful!")
                    print("   ✅ Debug port accessible with minimal flags")
                    self.info.append("Minimal Chrome startup works - issue may be with additional flags")
                else:
                    print(f"   ❌ Debug port returned status {response.status_code}")
            except requests.exceptions.ConnectionError:
                print("   ❌ Debug port not accessible even with minimal flags")
                self.issues.append("Chrome debug port not working even with minimal configuration")
            
            # Clean up
            process.terminate()
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Error testing minimal startup: {e}")
            self.issues.append(f"Cannot start Chrome with minimal flags: {e}")
    
    def run_comprehensive_check(self):
        """Run all checks and provide summary."""
        print("🔧 Comprehensive Chrome Debug Check")
        print("=" * 50)
        
        # Run all checks
        self.check_chrome_version_compatibility()
        self.check_system_resources()
        self.check_antivirus_interference()
        self.check_network_configuration()
        self.check_chrome_profile_integrity()
        self.check_chrome_flags_compatibility()
        self.check_port_alternatives()
        self.test_minimal_chrome_startup()
        
        # Summary
        print("\n" + "=" * 50)
        print("COMPREHENSIVE CHECK SUMMARY")
        print("=" * 50)
        
        if self.issues:
            print(f"❌ CRITICAL ISSUES ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        if self.info:
            print(f"\nℹ️  INFORMATION ({len(self.info)}):")
            for i, info in enumerate(self.info, 1):
                print(f"   {i}. {info}")
        
        # Recommendations
        print("\n🎯 RECOMMENDATIONS:")
        if not self.issues and not self.warnings:
            print("   ✅ No major issues found - Chrome debugging should work")
        else:
            if self.issues:
                print("   🔧 Address critical issues first")
            if "Minimal Chrome startup works" in str(self.info):
                print("   🔧 Try using minimal flags first, then add features gradually")
            if any("alternative ports" in str(info) for info in self.info):
                print("   🔧 Consider using an alternative debug port")
            if any("antivirus" in warning.lower() for warning in self.warnings):
                print("   🔧 Consider temporarily disabling antivirus for testing")
        
        return {
            'issues': self.issues,
            'warnings': self.warnings,
            'info': self.info
        }


def main():
    """Run comprehensive debug check."""
    checker = ComprehensiveDebugChecker()
    results = checker.run_comprehensive_check()
    
    # Save results
    with open('comprehensive_debug_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to: comprehensive_debug_results.json")


if __name__ == "__main__":
    main()