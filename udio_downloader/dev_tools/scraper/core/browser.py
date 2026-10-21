"""
Core browser connection and management.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, BrowserContext, Playwright


class BrowserConnection:
    """Manages Playwright browser connection with persistent context"""
    
    def __init__(self, user_data_dir=None, headless=False):
        # Shares the profile used by the downloader (udio_downloader.config)
        self.user_data_dir = Path(user_data_dir) if user_data_dir else Path.home() / '.udio_downloader' / 'browser_profile'
        self.headless = headless
        self.playwright = None
        self.context = None
        
    async def connect(self):
        """Connect to Chrome with persistent context"""
        print(f"Launching Chrome with profile: {self.user_data_dir}")
        
        # Ensure directory exists
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Start Playwright
        self.playwright = await async_playwright().start()
        
        # Launch persistent context
        self.context = await self.playwright.chromium.launch_persistent_context(
            str(self.user_data_dir),
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-infobars',
                '--disable-automation',
                '--disable-browser-side-navigation',
                '--disable-gpu',
            ],
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            ignore_default_args=['--enable-automation'],
        )
        
        # Add stealth script
        await self.context.add_init_script("""
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
        
        print(f"✓ Connected! Browser ready")
        return self.context
    
    async def close(self):
        """Close browser connection"""
        if self.context:
            await self.context.close()
            self.context = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
    
    async def __aenter__(self):
        return await self.connect()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
