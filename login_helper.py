"""Helper script to authenticate with Udio and save session."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from udio_downloader.services.playwright_session_manager import PlaywrightSessionManager
from udio_downloader.config import config


async def authenticate():
    """Interactive authentication with Udio."""
    print("=" * 60)
    print("UDIO AUTHENTICATION HELPER")
    print("=" * 60)
    print()
    print(f"Browser profile: {config.user_data_dir}")
    print()
    
    # Initialize session manager
    session_manager = PlaywrightSessionManager(
        user_data_dir=str(config.user_data_dir),
        headless=False  # Show browser so you can log in
    )
    
    try:
        print("Initializing browser...")
        await session_manager.initialize()
        print()
        
        # Check if already authenticated
        if session_manager.is_authenticated:
            print("✅ Already authenticated!")
            print()
            print("Your session is saved and ready to use.")
            print("You can now run: python -m udio_downloader download")
            return
        
        print("⚠️  Not authenticated yet")
        print()
        print("A browser window will open. Please:")
        print("1. Log in to Udio")
        print("2. Wait for the library page to load")
        print("3. Come back here")
        print()
        
        input("Press ENTER to open browser...")
        print()
        
        # Attempt to refresh session (opens login page)
        print("Opening Udio login page...")
        success = await session_manager.refresh_session()
        
        if success:
            print()
            print("=" * 60)
            print("✅ AUTHENTICATION SUCCESSFUL!")
            print("=" * 60)
            print()
            print("Your session has been saved to:")
            print(f"  {config.user_data_dir}")
            print()
            print("You can now run:")
            print("  python -m udio_downloader download")
            print()
        else:
            print()
            print("=" * 60)
            print("❌ AUTHENTICATION FAILED")
            print("=" * 60)
            print()
            print("Please try again or check your credentials.")
            print()
        
    except KeyboardInterrupt:
        print()
        print("Authentication cancelled by user.")
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print()
        print("Closing browser...")
        await session_manager.cleanup()
        print("Done!")


if __name__ == "__main__":
    asyncio.run(authenticate())
