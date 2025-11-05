"""Playwright session manager for authenticated browser contexts."""

import asyncio
import logging
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Playwright


logger = logging.getLogger(__name__)


class PlaywrightSessionManager:
    """
    Manages Playwright browser sessions with persistent authentication.
    
    This class handles:
    - Launching persistent browser contexts with userDataDir
    - Session validation via auth cookies
    - Session refresh for expired sessions
    - Resource cleanup
    """
    
    def __init__(
        self,
        user_data_dir: str,
        headless: bool = False,
        timeout: int = 30000
    ):
        """
        Initialize Playwright session manager.
        
        Args:
            user_data_dir: Path to persistent browser profile directory
            headless: Whether to run browser in headless mode
            timeout: Default timeout for page operations in milliseconds
        """
        self.user_data_dir = Path(user_data_dir)
        self.headless = headless
        self.timeout = timeout
        
        # Playwright instances
        self.playwright: Optional[Playwright] = None
        self.browser_context: Optional[BrowserContext] = None
        
        # Session state
        self.is_initialized = False
        self.is_authenticated = False
        
        logger.info(f"PlaywrightSessionManager initialized with user_data_dir: {self.user_data_dir}")
    
    async def initialize(self):
        """
        Initialize Playwright and launch persistent browser context.
        
        This creates a persistent browser context that reuses the same
        profile directory, preserving cookies and authentication state.
        """
        if self.is_initialized:
            logger.warning("Playwright already initialized")
            return
        
        logger.info("Initializing Playwright browser context...")
        
        # Ensure user data directory exists
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Start Playwright
        self.playwright = await async_playwright().start()
        
        # Launch persistent context with user data directory
        # This reuses the authenticated session from the browser
        self.browser_context = await self.playwright.chromium.launch_persistent_context(
            str(self.user_data_dir),
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-infobars',
                '--disable-automation',
                '--disable-browser-side-navigation',
                '--disable-gpu'
            ],
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            ignore_default_args=['--enable-automation']
        )
        
        # Set default timeout
        self.browser_context.set_default_timeout(self.timeout)
        
        # Add stealth script to hide automation
        await self.browser_context.add_init_script("""
            // Hide webdriver flag
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Hide automation flags
            window.navigator.chrome = {
                runtime: {}
            };
            
            // Overwrite the plugins array
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Overwrite the languages array
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        self.is_initialized = True
        logger.info("Playwright browser context initialized successfully")
        
        # Validate session
        await self.validate_session()
    
    async def validate_session(self) -> bool:
        """
        Validate that the session is authenticated by checking for auth cookies.
        
        Returns:
            True if session is authenticated, False otherwise
        """
        if not self.browser_context:
            logger.error("Cannot validate session: browser context not initialized")
            return False
        
        logger.info("Validating Udio session...")
        
        try:
            # Get all cookies for Udio domain
            cookies = await self.browser_context.cookies('https://www.udio.com')
            
            # Check for authentication cookies
            # Common auth cookie names: session, auth_token, access_token, etc.
            auth_cookie_names = ['session', 'auth_token', 'access_token', 'token', '__session']
            
            has_auth_cookie = any(
                cookie['name'] in auth_cookie_names or 'auth' in cookie['name'].lower()
                for cookie in cookies
            )
            
            if has_auth_cookie:
                logger.info(f"Session validated: found {len(cookies)} cookies including auth cookies")
                self.is_authenticated = True
                return True
            else:
                logger.warning(
                    f"Session validation failed: no auth cookies found "
                    f"(found {len(cookies)} cookies total)"
                )
                self.is_authenticated = False
                return False
                
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            self.is_authenticated = False
            return False
    
    async def refresh_session(self) -> bool:
        """
        Refresh expired session by navigating to login page.
        
        This method opens the Udio login page and waits for user to authenticate.
        It's intended for interactive use when the session has expired.
        
        Returns:
            True if session was refreshed successfully, False otherwise
        """
        if not self.browser_context:
            logger.error("Cannot refresh session: browser context not initialized")
            return False
        
        logger.info("Refreshing Udio session...")
        
        try:
            # Create a new page
            page = await self.browser_context.new_page()
            
            # Navigate to Udio login page
            await page.goto('https://www.udio.com/login', wait_until='domcontentloaded')
            
            logger.info(
                "Please log in to Udio in the browser window. "
                "Waiting for authentication..."
            )
            
            # Wait for navigation to main page (indicates successful login)
            # This will timeout if user doesn't log in
            try:
                await page.wait_for_url(
                    'https://www.udio.com/**',
                    timeout=300000  # 5 minutes for user to log in
                )
                
                logger.info("Login detected, validating session...")
                
                # Close the login page
                await page.close()
                
                # Validate the new session
                is_valid = await self.validate_session()
                
                if is_valid:
                    logger.info("Session refreshed successfully")
                    return True
                else:
                    logger.error("Session refresh failed: validation failed after login")
                    return False
                    
            except Exception as e:
                logger.error(f"Timeout waiting for login: {e}")
                await page.close()
                return False
                
        except Exception as e:
            logger.error(f"Error refreshing session: {e}")
            return False
    
    async def get_context(self) -> Optional[BrowserContext]:
        """
        Get the browser context, initializing if necessary.
        
        Returns:
            BrowserContext instance or None if initialization failed
        """
        if not self.is_initialized:
            await self.initialize()
        
        return self.browser_context
    
    async def cleanup(self):
        """
        Cleanup Playwright resources.
        
        This should be called when done with the session manager to
        properly close the browser and release resources.
        """
        logger.info("Cleaning up Playwright resources...")
        
        if self.browser_context:
            try:
                await self.browser_context.close()
                logger.info("Browser context closed")
            except Exception as e:
                logger.error(f"Error closing browser context: {e}")
            finally:
                self.browser_context = None
        
        if self.playwright:
            try:
                await self.playwright.stop()
                logger.info("Playwright stopped")
            except Exception as e:
                logger.error(f"Error stopping Playwright: {e}")
            finally:
                self.playwright = None
        
        self.is_initialized = False
        self.is_authenticated = False
        
        logger.info("Playwright resources cleaned up")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
