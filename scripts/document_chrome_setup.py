#!/usr/bin/env python3
"""
Document Chrome Dev Setup - Automatically detect and document Chrome Dev installation.
Creates a system-specific configuration file for future reference.
"""

import os
import json
import platform
from pathlib import Path
from datetime import datetime
import subprocess
import winreg


class ChromeDevDocumenter:
    """Automatically detect and document Chrome Dev installation details."""
    
    def __init__(self):
        self.system_info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.architecture()[0],
            "user": os.getenv("USERNAME", "unknown"),
            "timestamp": datetime.now().isoformat()
        }
        
        self.chrome_info = {}
        self.config_file = Path("config/chrome_dev_config.json")
        self.config_file.parent.mkdir(exist_ok=True)
    
    def find_chrome_dev_paths(self):
        """Find Chrome Dev installation paths."""
        possible_paths = []
        
        if platform.system() == "Windows":
            # Common Windows paths
            base_paths = [
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome Dev\Application"),
                os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome Dev\Application"),
                os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome Dev\Application"),
            ]
            
            for base_path in base_paths:
                chrome_exe = Path(base_path) / "chrome.exe"
                if chrome_exe.exists():
                    possible_paths.append({
                        "path": str(chrome_exe),
                        "type": "Chrome Dev",
                        "exists": True,
                        "size": chrome_exe.stat().st_size if chrome_exe.exists() else 0
                    })
        
        return possible_paths
    
    def find_chrome_profiles(self):
        """Find Chrome Dev profile directories."""
        profiles = []
        
        if platform.system() == "Windows":
            user_data_paths = [
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome Dev\User Data"),
                os.path.expandvars(r"%APPDATA%\Google\Chrome Dev\User Data"),
            ]
            
            for user_data_path in user_data_paths:
                user_data_dir = Path(user_data_path)
                if user_data_dir.exists():
                    # Find profile directories
                    for item in user_data_dir.iterdir():
                        if item.is_dir() and (item.name.startswith("Profile") or item.name == "Default"):
                            profiles.append({
                                "name": item.name,
                                "path": str(item),
                                "exists": True,
                                "size": sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                            })
        
        return profiles
    
    def get_chrome_version(self, chrome_path):
        """Get Chrome version information."""
        try:
            result = subprocess.run([chrome_path, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            return f"Error getting version: {e}"
        return "Unknown"
    
    def check_registry_info(self):
        """Check Windows registry for Chrome Dev information."""
        registry_info = {}
        
        if platform.system() == "Windows":
            try:
                # Check Chrome Dev registry entries
                reg_paths = [
                    r"SOFTWARE\Google\Chrome Dev",
                    r"SOFTWARE\WOW6432Node\Google\Chrome Dev",
                ]
                
                for reg_path in reg_paths:
                    try:
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                            try:
                                version = winreg.QueryValueEx(key, "Version")[0]
                                registry_info["version"] = version
                            except FileNotFoundError:
                                pass
                            
                            try:
                                install_path = winreg.QueryValueEx(key, "InstallLocation")[0]
                                registry_info["install_location"] = install_path
                            except FileNotFoundError:
                                pass
                    except FileNotFoundError:
                        continue
                        
            except Exception as e:
                registry_info["error"] = str(e)
        
        return registry_info
    
    def test_debugging_capability(self):
        """Test if debugging can be enabled."""
        debug_info = {
            "port_9222_available": self.is_port_available(9222),
            "selenium_available": self.check_selenium_available(),
            "webdriver_manager_available": self.check_webdriver_manager()
        }
        return debug_info
    
    def is_port_available(self, port):
        """Check if a port is available."""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def check_selenium_available(self):
        """Check if Selenium is available."""
        try:
            import selenium
            return {"available": True, "version": selenium.__version__}
        except ImportError:
            return {"available": False, "error": "Selenium not installed"}
    
    def check_webdriver_manager(self):
        """Check if WebDriver Manager is available."""
        try:
            import webdriver_manager
            return {"available": True, "version": getattr(webdriver_manager, '__version__', 'unknown')}
        except ImportError:
            return {"available": False, "error": "WebDriver Manager not installed"}
    
    def generate_config(self):
        """Generate complete Chrome Dev configuration."""
        print("🔍 Detecting Chrome Dev installation...")
        
        # Find Chrome installations
        chrome_paths = self.find_chrome_dev_paths()
        print(f"   Found {len(chrome_paths)} Chrome Dev installations")
        
        # Find profiles
        profiles = self.find_chrome_profiles()
        print(f"   Found {len(profiles)} Chrome profiles")
        
        # Get version info for each Chrome installation
        for chrome_info in chrome_paths:
            if chrome_info["exists"]:
                chrome_info["version"] = self.get_chrome_version(chrome_info["path"])
        
        # Check registry
        registry_info = self.check_registry_info()
        print(f"   Registry info: {'found' if registry_info else 'not found'}")
        
        # Test debugging capabilities
        debug_info = self.test_debugging_capability()
        print(f"   Debugging capabilities: {debug_info}")
        
        # Compile configuration
        config = {
            "system": self.system_info,
            "chrome_installations": chrome_paths,
            "chrome_profiles": profiles,
            "registry_info": registry_info,
            "debugging_capabilities": debug_info,
            "recommended_setup": self.generate_recommendations(chrome_paths, profiles),
            "udio_config": {
                "test_account": "idiovoidi@gmail.com",
                "target_urls": [
                    "https://www.udio.com/library",
                    "https://www.udio.com/my-creations",
                    "https://www.udio.com/create"
                ],
                "debug_port": 9222
            }
        }
        
        return config
    
    def generate_recommendations(self, chrome_paths, profiles):
        """Generate setup recommendations based on detected configuration."""
        recommendations = {
            "preferred_chrome_path": None,
            "preferred_profile": None,
            "startup_command": None,
            "notes": []
        }
        
        # Choose preferred Chrome path
        if chrome_paths:
            # Prefer user installation over system installation
            user_installs = [p for p in chrome_paths if "AppData\\Local" in p["path"]]
            if user_installs:
                recommendations["preferred_chrome_path"] = user_installs[0]["path"]
            else:
                recommendations["preferred_chrome_path"] = chrome_paths[0]["path"]
        
        # Choose preferred profile
        if profiles:
            # Prefer Default profile, then Profile 1, etc.
            default_profiles = [p for p in profiles if p["name"] == "Default"]
            if default_profiles:
                recommendations["preferred_profile"] = default_profiles[0]["path"]
            else:
                recommendations["preferred_profile"] = profiles[0]["path"]
        
        # Generate startup command
        if recommendations["preferred_chrome_path"]:
            cmd_parts = [
                f'"{recommendations["preferred_chrome_path"]}"',
                "--remote-debugging-port=9222",
                "--restore-last-session"
            ]
            
            if recommendations["preferred_profile"]:
                profile_parent = str(Path(recommendations["preferred_profile"]).parent)
                cmd_parts.append(f'--user-data-dir="{profile_parent}"')
            
            recommendations["startup_command"] = " ".join(cmd_parts)
        
        # Add notes
        if not chrome_paths:
            recommendations["notes"].append("Chrome Dev not found - install from https://www.google.com/chrome/dev/")
        
        if not profiles:
            recommendations["notes"].append("No Chrome profiles found - run Chrome Dev once to create profile")
        
        return recommendations
    
    def save_config(self, config):
        """Save configuration to file."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Configuration saved to: {self.config_file}")
    
    def generate_batch_file(self, config):
        """Generate a custom batch file for this system."""
        recommendations = config.get("recommended_setup", {})
        startup_command = recommendations.get("startup_command")
        
        if not startup_command:
            print("⚠️  Cannot generate batch file - no Chrome installation found")
            return
        
        batch_content = f"""@echo off
echo Starting Chrome Dev with Remote Debugging
echo System: {self.system_info['platform']} {self.system_info['platform_version']}
echo User: {self.system_info['user']}
echo Generated: {self.system_info['timestamp']}
echo.

REM Close existing Chrome instances
echo Closing existing Chrome instances...
taskkill /f /im chrome.exe 2>nul

REM Wait for processes to close
timeout /t 2 /nobreak >nul

REM Start Chrome Dev with debugging
echo Starting Chrome Dev with debugging enabled...
{startup_command} "https://www.udio.com/library"

echo.
echo Chrome Dev started with remote debugging on port 9222
echo Navigate to Udio and log in with: idiovoidi@gmail.com
echo Then run: python scripts/ui_mapper_attach.py
echo.
pause"""
        
        batch_file = Path("scripts/start_chrome_dev_custom.bat")
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        print(f"📝 Custom batch file created: {batch_file}")
    
    def print_summary(self, config):
        """Print a summary of the configuration."""
        print("\n" + "="*60)
        print("CHROME DEV CONFIGURATION SUMMARY")
        print("="*60)
        
        print(f"System: {config['system']['platform']} ({config['system']['architecture']})")
        print(f"User: {config['system']['user']}")
        print()
        
        chrome_installs = config['chrome_installations']
        print(f"Chrome Dev Installations: {len(chrome_installs)}")
        for i, install in enumerate(chrome_installs, 1):
            print(f"  {i}. {install['path']}")
            print(f"     Version: {install.get('version', 'Unknown')}")
        print()
        
        profiles = config['chrome_profiles']
        print(f"Chrome Profiles: {len(profiles)}")
        for i, profile in enumerate(profiles, 1):
            size_mb = profile['size'] / (1024*1024) if profile['size'] > 0 else 0
            print(f"  {i}. {profile['name']} ({size_mb:.1f} MB)")
            print(f"     Path: {profile['path']}")
        print()
        
        recommendations = config['recommended_setup']
        print("RECOMMENDED SETUP:")
        if recommendations['startup_command']:
            print(f"Startup Command:")
            print(f"  {recommendations['startup_command']}")
        else:
            print("  No recommendations available - Chrome Dev not found")
        print()
        
        print("UDIO CONFIGURATION:")
        print(f"  Test Account: {config['udio_config']['test_account']}")
        print(f"  Debug Port: {config['udio_config']['debug_port']}")
        print(f"  Target URLs: {len(config['udio_config']['target_urls'])}")
        for url in config['udio_config']['target_urls']:
            print(f"    - {url}")


def main():
    """Main function to document Chrome Dev setup."""
    print("🔧 Chrome Dev Setup Documentation Tool")
    print("="*50)
    
    documenter = ChromeDevDocumenter()
    
    try:
        # Generate configuration
        config = documenter.generate_config()
        
        # Save configuration
        documenter.save_config(config)
        
        # Generate custom batch file
        documenter.generate_batch_file(config)
        
        # Print summary
        documenter.print_summary(config)
        
        print("\n✅ Documentation complete!")
        print(f"📁 Config file: {documenter.config_file}")
        print("📝 Custom batch file: scripts/start_chrome_dev_custom.bat")
        print("📖 Full documentation: docs/chrome_dev_setup.md")
        
    except Exception as e:
        print(f"❌ Error documenting setup: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()