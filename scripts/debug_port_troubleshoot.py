#!/usr/bin/env python3
"""
Debug Port Troubleshooting - Deep dive into why port 9222 isn't accessible.
"""

import os
import subprocess
import psutil
import socket
import time
from pathlib import Path


class PortTroubleshooter:
    """Troubleshoot Chrome debug port issues."""
    
    def __init__(self):
        self.debug_port = 9222
        self.chrome_path = r"C:\Program Files\Google\Chrome Dev\Application\chrome.exe"
    
    def check_port_usage(self):
        """Check what's using port 9222."""
        print(f"🔍 Checking port {self.debug_port} usage...")
        
        try:
            # Use netstat to check port
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            port_lines = [line for line in lines if f':{self.debug_port}' in line]
            
            if port_lines:
                print(f"   📡 Port {self.debug_port} activity found:")
                for line in port_lines:
                    print(f"      {line.strip()}")
            else:
                print(f"   ❌ No activity found on port {self.debug_port}")
            
            # Also check with PowerShell Get-NetTCPConnection
            try:
                ps_result = subprocess.run([
                    'powershell', '-Command', 
                    f'Get-NetTCPConnection -LocalPort {self.debug_port} -ErrorAction SilentlyContinue'
                ], capture_output=True, text=True)
                
                if ps_result.stdout.strip():
                    print(f"   📡 PowerShell shows port {self.debug_port} connections:")
                    print(f"      {ps_result.stdout.strip()}")
                else:
                    print(f"   ❌ PowerShell shows no connections on port {self.debug_port}")
                    
            except Exception as e:
                print(f"   ⚠️  PowerShell check failed: {e}")
                
        except Exception as e:
            print(f"   ❌ Error checking port usage: {e}")
    
    def check_chrome_command_lines(self):
        """Check actual command lines of running Chrome processes."""
        print("🔍 Checking Chrome process command lines...")
        
        chrome_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'chrome' in proc.info['name'].lower():
                    chrome_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not chrome_processes:
            print("   ❌ No Chrome processes found")
            return
        
        print(f"   Found {len(chrome_processes)} Chrome processes:")
        
        main_process = None
        for proc in chrome_processes:
            cmdline = ' '.join(proc['cmdline']) if proc['cmdline'] else 'No command line'
            
            # Look for main process (not renderer/utility)
            if '--type=' not in cmdline and 'chrome.exe' in cmdline:
                main_process = proc
                print(f"   🎯 MAIN PROCESS PID {proc['pid']}:")
                print(f"      {cmdline}")
                
                # Check for debug flag
                if '--remote-debugging-port' in cmdline:
                    print("      ✅ Has remote debugging flag")
                else:
                    print("      ❌ Missing remote debugging flag")
            else:
                # Child process
                process_type = "renderer" if "--type=renderer" in cmdline else "utility"
                print(f"   📄 {process_type.upper()} PID {proc['pid']}")
        
        return main_process
    
    def test_port_binding(self):
        """Test if we can bind to port 9222."""
        print(f"🧪 Testing port {self.debug_port} binding...")
        
        try:
            # Try to bind to the port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('localhost', self.debug_port))
            sock.listen(1)
            
            print(f"   ✅ Successfully bound to port {self.debug_port}")
            print("   ℹ️  This means the port is available (Chrome isn't using it)")
            
            sock.close()
            return True
            
        except OSError as e:
            if e.errno == 10048:  # Address already in use
                print(f"   ❌ Port {self.debug_port} is already in use")
                print("   ℹ️  This could mean Chrome is using it, or another process")
            else:
                print(f"   ❌ Cannot bind to port {self.debug_port}: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Error testing port binding: {e}")
            return False
    
    def check_firewall_rules(self):
        """Check Windows Firewall rules that might block the port."""
        print("🔥 Checking Windows Firewall...")
        
        try:
            # Check if Windows Firewall is blocking the port
            result = subprocess.run([
                'powershell', '-Command',
                f'Get-NetFirewallRule | Where-Object {{$_.LocalPort -eq "{self.debug_port}" -or $_.RemotePort -eq "{self.debug_port}"}}'
            ], capture_output=True, text=True)
            
            if result.stdout.strip():
                print("   🔥 Found firewall rules for port 9222:")
                print(f"      {result.stdout.strip()}")
            else:
                print("   ℹ️  No specific firewall rules found for port 9222")
                print("   ℹ️  Default Windows Firewall rules may still apply")
            
        except Exception as e:
            print(f"   ⚠️  Could not check firewall rules: {e}")
    
    def suggest_manual_chrome_start(self):
        """Suggest manual Chrome startup command."""
        print("🔧 Manual Chrome Startup Suggestion:")
        print()
        print("Try starting Chrome manually with this exact command:")
        print()
        
        cmd = [
            f'"{self.chrome_path}"',
            '--remote-debugging-port=9222',
            '--user-data-dir="C:\\Users\\user\\AppData\\Local\\Google\\Chrome Dev\\User Data"',
            '--profile-directory="Profile 2"',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--no-sandbox',
            'https://www.udio.com/library'
        ]
        
        print(' '.join(cmd))
        print()
        print("Or try this simplified version:")
        print(f'"{self.chrome_path}" --remote-debugging-port=9222')
        print()
        print("After starting, test with:")
        print("   curl http://localhost:9222/json")
        print("   or visit: http://localhost:9222")
    
    def run_comprehensive_check(self):
        """Run all troubleshooting checks."""
        print("🔧 Chrome Debug Port Troubleshooting")
        print("=" * 50)
        
        # Check port usage
        self.check_port_usage()
        print()
        
        # Check Chrome processes
        main_process = self.check_chrome_command_lines()
        print()
        
        # Test port binding
        port_available = self.test_port_binding()
        print()
        
        # Check firewall
        self.check_firewall_rules()
        print()
        
        # Analysis and recommendations
        print("📊 ANALYSIS:")
        print("=" * 20)
        
        if not main_process:
            print("❌ No Chrome main process found")
            print("   → Chrome may not be running or crashed during startup")
        else:
            cmdline = ' '.join(main_process['cmdline']) if main_process['cmdline'] else ''
            if '--remote-debugging-port' not in cmdline:
                print("❌ Chrome main process missing debug flag")
                print("   → Chrome started without --remote-debugging-port=9222")
            else:
                print("✅ Chrome main process has debug flag")
                if port_available:
                    print("❌ But port is not being used by Chrome")
                    print("   → Chrome may have failed to bind to the port")
                else:
                    print("✅ Port appears to be in use")
        
        print()
        self.suggest_manual_chrome_start()


def main():
    """Run the troubleshooting tool."""
    troubleshooter = PortTroubleshooter()
    troubleshooter.run_comprehensive_check()


if __name__ == "__main__":
    main()