"""
Authentication handler for Udio platform login and session management.
"""

import json
import time
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import requests


logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class SessionExpiredError(Exception):
    """Raised when session has expired."""
    pass


class AuthenticationHandler:
    """
    Handles authentication with Udio platform using Selenium WebDriver.
    Manages session cookies and provides session validation/renewal.
    """
    
    def __init__(self, headless: bool = True, browser: str = "chrome"):
        """
        Initialize the authentication handler.
        
        Args:
            headless: Whether to run browser in headless mode
            browser: Browser to use ("chrome" or "firefox")
        """
        self.headless = headless
        self.browser = browser.lower()
        self.driver: Optional[webdriver.Remote] = None
        self.session_cookies: Dict[str, Any] = {}
        self.session_file = Path.home() / ".udio_downloader" / "session.json"
        self.session_file.parent.mkdir(exist_ok=True)
        
        # Udio platform URLs
        self.base_url = "https://udio.com"
        self.login_url = f"{self.base_url}/auth/login"
        self.dashboard_url = f"{self.base_url}/my-creations"
        
    def _setup_driver(self) -> webdriver.Remote:
        """Set up and configure the WebDriver."""
        try:
            if self.browser == "chrome":
                options = ChromeOptions()
                if self.headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                
                # Anti-detection measures
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                driver = webdriver.Chrome(
                    service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                    options=options
                )
                
            elif self.browser == "firefox":
                options = FirefoxOptions()
                if self.headless:
                    options.add_argument("--headless")
                
                driver = webdriver.Firefox(
                    service=webdriver.firefox.service.Service(GeckoDriverManager().install()),
                    options=options
                )
            else:
                raise ValueError(f"Unsupported browser: {self.browser}")
                
            # Set user agent to avoid detection
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            raise AuthenticationError(f"Failed to initialize browser: {e}")
    
    def login(self, username: str, password: str) -> bool:
        """
        Authenticate with Udio platform using provided credentials.
        
        Args:
            username: User's email or username
            password: User's password
            
        Returns:
            True if login successful, False otherwise
            
        Raises:
            AuthenticationError: If login fails
        """
        logger.info("Starting authentication process...")
        
        try:
            self.driver = self._setup_driver()
            
            # Navigate to login page
            logger.info("Navigating to login page...")
            self.driver.get(self.login_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Find and fill username field
            logger.info("Filling login credentials...")
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[name='username']"))
            )
            username_field.clear()
            username_field.send_keys(username)
            
            # Find and fill password field
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
            password_field.clear()
            password_field.send_keys(password)
            
            # Find and click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], button:contains('Log in'), button:contains('Sign in')")
            login_button.click()
            
            # Wait for login to complete - check for redirect or dashboard elements
            logger.info("Waiting for login completion...")
            try:
                # Wait for either dashboard or error message
                WebDriverWait(self.driver, 15).until(
                    lambda driver: (
                        self.dashboard_url in driver.current_url or
                        driver.find_elements(By.CSS_SELECTOR, "[data-testid='user-menu'], .user-avatar, .profile-menu") or
                        driver.find_elements(By.CSS_SELECTOR, ".error, .alert-error, [role='alert']")
                    )
                )
                
                # Check if we're on dashboard or have user elements (successful login)
                if (self.dashboard_url in self.driver.current_url or 
                    self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='user-menu'], .user-avatar, .profile-menu")):
                    
                    logger.info("Login successful!")
                    self._save_session_cookies()
                    return True
                else:
                    # Check for error messages
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".error, .alert-error, [role='alert']")
                    if error_elements:
                        error_text = error_elements[0].text
                        logger.error(f"Login failed: {error_text}")
                        raise AuthenticationError(f"Login failed: {error_text}")
                    else:
                        raise AuthenticationError("Login failed: Unknown error")
                        
            except TimeoutException:
                logger.error("Login timeout - page did not respond as expected")
                raise AuthenticationError("Login timeout - please check credentials and try again")
                
        except WebDriverException as e:
            logger.error(f"WebDriver error during login: {e}")
            raise AuthenticationError(f"Browser error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            raise AuthenticationError(f"Login failed: {e}")
        finally:
            # Keep driver open for session management
            pass
    
    def _save_session_cookies(self) -> None:
        """Save current session cookies to file for persistence."""
        if not self.driver:
            return
            
        try:
            cookies = self.driver.get_cookies()
            self.session_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
            
            session_data = {
                'cookies': cookies,
                'timestamp': time.time(),
                'url': self.driver.current_url
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
            logger.info(f"Session cookies saved to {self.session_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save session cookies: {e}")
    
    def load_session_cookies(self) -> bool:
        """
        Load previously saved session cookies.
        
        Returns:
            True if cookies loaded successfully, False otherwise
        """
        try:
            if not self.session_file.exists():
                logger.info("No saved session found")
                return False
                
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
                
            # Check if session is not too old (24 hours)
            if time.time() - session_data.get('timestamp', 0) > 86400:
                logger.info("Saved session is too old, will need fresh login")
                return False
                
            if not self.driver:
                self.driver = self._setup_driver()
                
            # Navigate to base URL first
            self.driver.get(self.base_url)
            
            # Add cookies to driver
            for cookie in session_data['cookies']:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    logger.warning(f"Failed to add cookie {cookie.get('name')}: {e}")
                    
            self.session_cookies = {cookie['name']: cookie['value'] for cookie in session_data['cookies']}
            logger.info("Session cookies loaded successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load session cookies: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """
        Check if current session is authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        if not self.driver:
            return False
            
        try:
            # Navigate to dashboard to check authentication
            self.driver.get(self.dashboard_url)
            
            # Wait a moment for page to load
            time.sleep(2)
            
            # Check for user-specific elements that indicate authentication
            user_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "[data-testid='user-menu'], .user-avatar, .profile-menu, .user-profile")
            
            # Also check if we're not redirected to login page
            is_on_login = "login" in self.driver.current_url.lower() or "auth" in self.driver.current_url.lower()
            
            authenticated = len(user_elements) > 0 and not is_on_login
            
            if authenticated:
                logger.info("Session is authenticated")
            else:
                logger.info("Session is not authenticated")
                
            return authenticated
            
        except Exception as e:
            logger.error(f"Error checking authentication status: {e}")
            return False
    
    def renew_session(self, username: str, password: str) -> bool:
        """
        Renew expired session by re-authenticating.
        
        Args:
            username: User's email or username
            password: User's password
            
        Returns:
            True if renewal successful, False otherwise
        """
        logger.info("Renewing session...")
        
        try:
            # Close existing driver if any
            if self.driver:
                self.driver.quit()
                self.driver = None
                
            # Clear old session data
            self.session_cookies.clear()
            
            # Perform fresh login
            return self.login(username, password)
            
        except Exception as e:
            logger.error(f"Failed to renew session: {e}")
            return False
    
    def get_session_cookies(self) -> Dict[str, Any]:
        """
        Get current session cookies.
        
        Returns:
            Dictionary of session cookies
        """
        return self.session_cookies.copy()
    
    def maintain_session(self) -> None:
        """
        Perform a lightweight operation to keep session alive.
        """
        if not self.driver:
            return
            
        try:
            # Navigate to a lightweight page to maintain session
            current_url = self.driver.current_url
            self.driver.get(self.base_url)
            
            # Wait a moment
            time.sleep(1)
            
            # Go back to where we were
            if current_url and current_url != self.base_url:
                self.driver.get(current_url)
                
            logger.debug("Session maintained")
            
        except Exception as e:
            logger.warning(f"Failed to maintain session: {e}")
    
    def close(self) -> None:
        """Clean up resources and close browser."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")
            finally:
                self.driver = None
                
        logger.info("Authentication handler closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()