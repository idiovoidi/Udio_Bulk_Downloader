"""
Secure credential management for Udio Downloader.
Handles secure input, storage, and retrieval of user credentials.
"""

import getpass
import logging
from typing import Optional, Tuple
from pathlib import Path

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    logging.warning("keyring library not available - credentials will not be stored securely")


logger = logging.getLogger(__name__)


class CredentialManager:
    """
    Manages secure credential input, storage, and retrieval.
    Uses keyring for secure storage when available, falls back to session-only storage.
    """
    
    SERVICE_NAME = "udio-downloader"
    
    def __init__(self):
        """Initialize the credential manager."""
        self._session_username: Optional[str] = None
        self._session_password: Optional[str] = None
        
    def get_credentials(self, username: Optional[str] = None, prompt_if_missing: bool = True) -> Tuple[str, str]:
        """
        Get user credentials, prompting securely if needed.
        
        Args:
            username: Optional username to use (will prompt if not provided)
            prompt_if_missing: Whether to prompt for missing credentials
            
        Returns:
            Tuple of (username, password)
            
        Raises:
            ValueError: If credentials cannot be obtained
        """
        # Try to use provided username or session username
        if not username:
            username = self._session_username
            
        # Try to get stored password if we have a username
        password = None
        if username and KEYRING_AVAILABLE:
            try:
                password = keyring.get_password(self.SERVICE_NAME, username)
                if password:
                    logger.info(f"Retrieved stored credentials for {username}")
            except Exception as e:
                logger.warning(f"Failed to retrieve stored password: {e}")
        
        # Use session password if available
        if not password and username == self._session_username:
            password = self._session_password
            
        # Prompt for missing credentials if allowed
        if prompt_if_missing:
            if not username:
                username = self._prompt_username()
                
            if not password:
                password = self._prompt_password(username)
                
        # Validate we have both credentials
        if not username or not password:
            raise ValueError("Username and password are required")
            
        # Store in session for this run
        self._session_username = username
        self._session_password = password
        
        return username, password
    
    def _prompt_username(self) -> str:
        """
        Prompt user for username/email.
        
        Returns:
            Username entered by user
        """
        while True:
            username = input("Udio username/email: ").strip()
            if username:
                return username
            print("Username cannot be empty. Please try again.")
    
    def _prompt_password(self, username: str) -> str:
        """
        Securely prompt user for password.
        
        Args:
            username: Username for context in prompt
            
        Returns:
            Password entered by user
        """
        while True:
            password = getpass.getpass(f"Password for {username}: ")
            if password:
                return password
            print("Password cannot be empty. Please try again.")
    
    def store_credentials(self, username: str, password: str, persistent: bool = True) -> bool:
        """
        Store credentials securely.
        
        Args:
            username: Username to store
            password: Password to store
            persistent: Whether to store persistently (requires keyring)
            
        Returns:
            True if stored successfully, False otherwise
        """
        # Always store in session
        self._session_username = username
        self._session_password = password
        
        # Store persistently if requested and keyring is available
        if persistent and KEYRING_AVAILABLE:
            try:
                keyring.set_password(self.SERVICE_NAME, username, password)
                logger.info(f"Credentials stored securely for {username}")
                return True
            except Exception as e:
                logger.warning(f"Failed to store credentials securely: {e}")
                return False
        elif persistent and not KEYRING_AVAILABLE:
            logger.warning("Persistent storage requested but keyring not available")
            return False
            
        return True
    
    def remove_stored_credentials(self, username: str) -> bool:
        """
        Remove stored credentials for a user.
        
        Args:
            username: Username whose credentials to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        if not KEYRING_AVAILABLE:
            logger.info("No persistent storage available to remove from")
            return True
            
        try:
            keyring.delete_password(self.SERVICE_NAME, username)
            logger.info(f"Stored credentials removed for {username}")
            return True
        except keyring.errors.PasswordDeleteError:
            logger.info(f"No stored credentials found for {username}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove stored credentials: {e}")
            return False
    
    def clear_session_credentials(self) -> None:
        """Clear credentials from current session."""
        self._session_username = None
        self._session_password = None
        logger.info("Session credentials cleared")
    
    def has_stored_credentials(self, username: str) -> bool:
        """
        Check if credentials are stored for a user.
        
        Args:
            username: Username to check
            
        Returns:
            True if credentials are stored, False otherwise
        """
        if not KEYRING_AVAILABLE:
            return False
            
        try:
            password = keyring.get_password(self.SERVICE_NAME, username)
            return password is not None
        except Exception as e:
            logger.warning(f"Error checking stored credentials: {e}")
            return False
    
    def list_stored_users(self) -> list:
        """
        List users with stored credentials.
        
        Returns:
            List of usernames with stored credentials
        """
        # Note: keyring doesn't provide a standard way to list all stored credentials
        # This is a limitation of the keyring library for security reasons
        logger.info("Cannot list stored users - keyring limitation for security")
        return []
    
    def prompt_save_credentials(self, username: str, password: str) -> bool:
        """
        Ask user if they want to save credentials and do so if confirmed.
        
        Args:
            username: Username to potentially save
            password: Password to potentially save
            
        Returns:
            True if credentials were saved (or user declined), False if error
        """
        if not KEYRING_AVAILABLE:
            print("Note: Secure credential storage not available (keyring library missing)")
            return True
            
        try:
            response = input(f"Save credentials for {username} securely? (y/N): ").strip().lower()
            if response in ('y', 'yes'):
                return self.store_credentials(username, password, persistent=True)
            else:
                logger.info("User declined to save credentials")
                return True
        except KeyboardInterrupt:
            print("\nOperation cancelled")
            return False
        except Exception as e:
            logger.error(f"Error prompting for credential save: {e}")
            return False


class SecureAuthenticationHandler:
    """
    Enhanced authentication handler with secure credential management.
    Combines AuthenticationHandler with CredentialManager for complete auth solution.
    """
    
    def __init__(self, headless: bool = True, browser: str = "chrome"):
        """
        Initialize secure authentication handler.
        
        Args:
            headless: Whether to run browser in headless mode
            browser: Browser to use ("chrome" or "firefox")
        """
        from .authentication import AuthenticationHandler
        
        self.auth_handler = AuthenticationHandler(headless=headless, browser=browser)
        self.credential_manager = CredentialManager()
        self._current_username: Optional[str] = None
    
    def authenticate(self, username: Optional[str] = None, password: Optional[str] = None, 
                    save_credentials: Optional[bool] = None) -> bool:
        """
        Authenticate with automatic credential management.
        
        Args:
            username: Optional username (will prompt if not provided)
            password: Optional password (will prompt if not provided)
            save_credentials: Whether to save credentials (will prompt if None)
            
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Get credentials (will prompt if needed)
            if not username or not password:
                username, password = self.credential_manager.get_credentials(
                    username=username, prompt_if_missing=True
                )
            
            # Attempt authentication
            success = self.auth_handler.login(username, password)
            
            if success:
                self._current_username = username
                
                # Store credentials in session
                self.credential_manager.store_credentials(username, password, persistent=False)
                
                # Ask about persistent storage if not specified
                if save_credentials is None:
                    self.credential_manager.prompt_save_credentials(username, password)
                elif save_credentials:
                    self.credential_manager.store_credentials(username, password, persistent=True)
                    
            return success
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def authenticate_with_retry(self, max_attempts: int = 3, username: Optional[str] = None) -> bool:
        """
        Authenticate with retry logic for failed attempts.
        
        Args:
            max_attempts: Maximum number of authentication attempts
            username: Optional username to use
            
        Returns:
            True if authentication successful, False otherwise
        """
        for attempt in range(max_attempts):
            try:
                print(f"\nAuthentication attempt {attempt + 1} of {max_attempts}")
                
                if self.authenticate(username=username):
                    return True
                    
                if attempt < max_attempts - 1:
                    print("Authentication failed. Please check your credentials and try again.")
                    # Clear session credentials to force re-prompt
                    self.credential_manager.clear_session_credentials()
                    
            except KeyboardInterrupt:
                print("\nAuthentication cancelled by user")
                return False
            except Exception as e:
                logger.error(f"Authentication attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    print(f"Error: {e}")
                    
        print("Maximum authentication attempts reached")
        return False
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        return self.auth_handler.is_authenticated()
    
    def renew_session_if_needed(self) -> bool:
        """
        Check authentication status and renew if needed.
        
        Returns:
            True if session is valid or successfully renewed, False otherwise
        """
        if self.is_authenticated():
            return True
            
        logger.info("Session expired, attempting renewal...")
        
        if not self._current_username:
            logger.error("Cannot renew session - no current username")
            return False
            
        try:
            username, password = self.credential_manager.get_credentials(
                username=self._current_username, prompt_if_missing=False
            )
            return self.auth_handler.renew_session(username, password)
        except ValueError:
            logger.error("Cannot renew session - credentials not available")
            return False
    
    def get_session_cookies(self):
        """Get current session cookies."""
        return self.auth_handler.get_session_cookies()
    
    def maintain_session(self):
        """Maintain current session."""
        self.auth_handler.maintain_session()
    
    def close(self):
        """Clean up resources."""
        self.auth_handler.close()
        self.credential_manager.clear_session_credentials()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()