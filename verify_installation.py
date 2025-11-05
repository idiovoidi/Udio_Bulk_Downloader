"""Verify Udio Downloader installation and readiness."""

import sys
from pathlib import Path

def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.10+)")
        return False

def check_dependencies():
    """Check required dependencies."""
    print("\nChecking dependencies...")
    
    dependencies = [
        ("click", "Click"),
        ("playwright", "Playwright"),
        ("requests", "Requests"),
        ("pydantic", "Pydantic"),
        ("tqdm", "TQDM"),
        ("dateutil", "python-dateutil"),
    ]
    
    all_ok = True
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} (not installed)")
            all_ok = False
    
    return all_ok

def check_playwright_browsers():
    """Check Playwright browsers."""
    print("\nChecking Playwright browsers...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Try to get browser
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
                print("✅ Chromium browser installed")
                return True
            except Exception as e:
                print(f"❌ Chromium browser not installed")
                print(f"   Run: playwright install chromium")
                return False
                
    except Exception as e:
        print(f"❌ Error checking browsers: {e}")
        return False

def check_cli_commands():
    """Check CLI commands."""
    print("\nChecking CLI commands...")
    
    import subprocess
    
    try:
        result = subprocess.run(
            ["python", "-m", "udio_downloader", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ CLI working ({version})")
            return True
        else:
            print("❌ CLI not working")
            return False
            
    except Exception as e:
        print(f"❌ Error checking CLI: {e}")
        return False

def check_directories():
    """Check required directories."""
    print("\nChecking directories...")
    
    dirs = [
        ("downloads", "Output directory"),
        ("chrome_extension", "Chrome extension"),
    ]
    
    all_ok = True
    for dir_name, description in dirs:
        path = Path(dir_name)
        if path.exists():
            print(f"✅ {description} ({dir_name})")
        else:
            print(f"⚠️  {description} ({dir_name}) - will be created on first use")
    
    return True

def check_documentation():
    """Check documentation files."""
    print("\nChecking documentation...")
    
    docs = [
        ("README.md", "Main README"),
        ("QUICK_START.md", "Quick Start Guide"),
        ("TEST_RESULTS.md", "Test Results"),
        ("requirements.txt", "Requirements"),
    ]
    
    all_ok = True
    for file_name, description in docs:
        path = Path(file_name)
        if path.exists():
            print(f"✅ {description}")
        else:
            print(f"❌ {description} (missing)")
            all_ok = False
    
    return all_ok

def main():
    """Run all checks."""
    print("=" * 60)
    print("UDIO DOWNLOADER - INSTALLATION VERIFICATION")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Playwright Browsers", check_playwright_browsers),
        ("CLI Commands", check_cli_commands),
        ("Directories", check_directories),
        ("Documentation", check_documentation),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            results.append((name, False))
    
    print()
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print()
    
    all_passed = all(result for _, result in results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    
    if all_passed:
        print("=" * 60)
        print("✅ ALL CHECKS PASSED - READY TO USE!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Export your Udio library using the Chrome extension")
        print("2. Run: python -m udio_downloader import-metadata --json-file <export.json>")
        print("3. Run: python -m udio_downloader download")
        print()
        print("For detailed instructions, see QUICK_START.md")
        return 0
    else:
        print("=" * 60)
        print("❌ SOME CHECKS FAILED")
        print("=" * 60)
        print()
        print("Please fix the issues above before using the downloader.")
        print()
        print("Common fixes:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Install Playwright browsers: playwright install chromium")
        print("- Check Python version: python --version (requires 3.10+)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
