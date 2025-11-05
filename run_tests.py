"""Simple test runner - no debugging required."""

import subprocess
import sys

def run_command(name, cmd):
    """Run a command and report results."""
    print(f"\n{'='*60}")
    print(f"Running: {name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {name} - SUCCESS")
            return True
        else:
            print(f"❌ {name} - FAILED (exit code {result.returncode})")
            return False
    except Exception as e:
        print(f"❌ {name} - ERROR: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("UDIO DOWNLOADER - TEST SUITE")
    print("="*60)
    
    tests = [
        ("Status Command", "python -m udio_downloader status"),
        ("Help Command", "python -m udio_downloader --help"),
        ("Version Command", "python -m udio_downloader --version"),
        ("Full Workflow Test", "python test_full_workflow.py"),
    ]
    
    results = []
    for name, cmd in tests:
        result = run_command(name, cmd)
        results.append((name, result))
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
