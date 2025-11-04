#!/usr/bin/env python3
"""
Find Chrome profiles and identify which one belongs to idiovoidi@gmail.com
"""

import os
import json
import sqlite3
from pathlib import Path

def find_chrome_profiles():
    """Find all Chrome profiles and their associated accounts."""
    
    # Chrome Dev user data directory
    chrome_user_data = Path(os.environ['LOCALAPPDATA']) / "Google" / "Chrome Dev" / "User Data"
    
    if not chrome_user_data.exists():
        print(f"❌ Chrome Dev user data directory not found: {chrome_user_data}")
        return []
    
    print(f"📁 Chrome Dev user data: {chrome_user_data}")
    print()
    
    profiles = []
    
    # Look for profile directories
    for item in chrome_user_data.iterdir():
        if item.is_dir() and (item.name == "Default" or item.name.startswith("Profile ")):
            profile_info = analyze_profile(item)
            if profile_info:
                profiles.append(profile_info)
    
    return profiles

def analyze_profile(profile_path):
    """Analyze a Chrome profile to extract account information."""
    
    profile_info = {
        "path": str(profile_path),
        "name": profile_path.name,
        "accounts": [],
        "preferences": {}
    }
    
    # Check Preferences file for account info
    prefs_file = profile_path / "Preferences"
    if prefs_file.exists():
        try:
            with open(prefs_file, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
            
            # Extract account information
            if 'account_info' in prefs:
                for account in prefs['account_info']:
                    if 'email' in account:
                        profile_info['accounts'].append(account['email'])
            
            # Extract profile name
            if 'profile' in prefs and 'name' in prefs['profile']:
                profile_info['profile_name'] = prefs['profile']['name']
            
            # Extract signin info
            if 'signin' in prefs:
                signin = prefs['signin']
                if 'allowed_username' in signin:
                    profile_info['accounts'].append(signin['allowed_username'])
                
        except Exception as e:
            print(f"⚠️  Could not read preferences for {profile_path.name}: {e}")
    
    # Check Local State for additional account info
    local_state_file = profile_path.parent / "Local State"
    if local_state_file.exists():
        try:
            with open(local_state_file, 'r', encoding='utf-8') as f:
                local_state = json.load(f)
            
            if 'profile' in local_state and 'info_cache' in local_state['profile']:
                info_cache = local_state['profile']['info_cache']
                for profile_key, profile_data in info_cache.items():
                    if profile_key == profile_path.name:
                        if 'user_name' in profile_data:
                            profile_info['accounts'].append(profile_data['user_name'])
                        if 'gaia_name' in profile_data:
                            profile_info['profile_display_name'] = profile_data['gaia_name']
                            
        except Exception as e:
            print(f"⚠️  Could not read local state: {e}")
    
    # Remove duplicates from accounts
    profile_info['accounts'] = list(set(profile_info['accounts']))
    
    return profile_info

def main():
    print("🔍 Searching for Chrome Dev profiles...")
    print()
    
    profiles = find_chrome_profiles()
    
    if not profiles:
        print("❌ No Chrome profiles found")
        return
    
    target_email = "idiovoidi@gmail.com"
    target_profile = None
    
    print(f"📋 Found {len(profiles)} Chrome profiles:")
    print()
    
    for i, profile in enumerate(profiles, 1):
        print(f"Profile {i}: {profile['name']}")
        print(f"  Path: {profile['path']}")
        
        if profile['accounts']:
            print(f"  Accounts: {', '.join(profile['accounts'])}")
            
            # Check if target email is in this profile
            if target_email in profile['accounts']:
                target_profile = profile
                print(f"  ✅ MATCHES TARGET EMAIL: {target_email}")
        else:
            print(f"  Accounts: None found")
        
        if 'profile_display_name' in profile:
            print(f"  Display Name: {profile['profile_display_name']}")
        
        print()
    
    if target_profile:
        print(f"🎯 Target profile found!")
        print(f"   Profile: {target_profile['name']}")
        print(f"   Path: {target_profile['path']}")
        print()
        print(f"💡 To start Chrome with this profile and debugging:")
        
        profile_dir = f"--profile-directory={target_profile['name']}"
        user_data_dir = str(Path(target_profile['path']).parent)
        
        print(f'   "C:\\Program Files\\Google\\Chrome Dev\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir="{user_data_dir}" {profile_dir} --new-window "https://www.udio.com/library"')
        
        # Save the command to a batch file
        batch_content = f'"C:\\Program Files\\Google\\Chrome Dev\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir="{user_data_dir}" {profile_dir} --new-window "https://www.udio.com/library"'
        
        with open("start_chrome_with_profile.bat", "w") as f:
            f.write(batch_content)
        
        print()
        print("📝 Command saved to: start_chrome_with_profile.bat")
        
    else:
        print(f"❌ Profile with {target_email} not found")
        print("   Make sure you're logged into Chrome Dev with this account")

if __name__ == "__main__":
    main()