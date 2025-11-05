"""Quick test script to verify Playwright session manager works."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from udio_downloader.services.playwright_session_manager import PlaywrightSessionManager
from udio_downloader.config import config


async def test_playwright():
    """Test Playwright session initialization."""
    print("Testing Playwright Session Manager...")
    print(f"User data dir: {config.user_data_dir}")
    print()
    
    # Initialize session manager
    session_manager = PlaywrightSessionManager(
        user_data_dir=str(config.user_data_dir),
        headless=False
    )
    
    try:
        print("Initializing Playwright...")
        await session_manager.initialize()
        print("✓ Playwright initialized successfully")
        print()
        
        print(f"Authenticated: {session_manager.is_authenticated}")
        print(f"Browser context: {session_manager.browser_context is not None}")
        print()
        
        if session_manager.browser_context:
            print("Creating new page...")
            page = await session_manager.browser_context.new_page()
            
            print("Navigating to Udio homepage...")
            await page.goto("https://www.udio.com", wait_until="domcontentloaded")
            print(f"Current URL: {page.url}")
            print()
            
            # Wait a bit to see the page
            print("Waiting 3 seconds...")
            await asyncio.sleep(3)
            
            await page.close()
        
        print("✓ Test completed successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print()
        print("Cleaning up...")
        await session_manager.cleanup()
        print("✓ Cleanup complete")


if __name__ == "__main__":
    asyncio.run(test_playwright())
