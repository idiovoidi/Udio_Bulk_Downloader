"""
Centralized logging configuration.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


class ScraperLogger:
    """Centralized logger for scraping operations"""
    
    def __init__(self, name, log_dir='logs', console_level=logging.INFO, file_level=logging.DEBUG):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.log_dir / f'{name}_{timestamp}.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(file_level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        self.logger.info(f"Logging initialized. Log file: {log_file}")
    
    def debug(self, message, **kwargs):
        """Log debug message"""
        self._log_with_context(logging.DEBUG, message, kwargs)
    
    def info(self, message, **kwargs):
        """Log info message"""
        self._log_with_context(logging.INFO, message, kwargs)
    
    def warning(self, message, **kwargs):
        """Log warning message"""
        self._log_with_context(logging.WARNING, message, kwargs)
    
    def error(self, message, **kwargs):
        """Log error message"""
        self._log_with_context(logging.ERROR, message, kwargs)
    
    def success(self, message, **kwargs):
        """Log success message (info level with ✓ prefix)"""
        self._log_with_context(logging.INFO, f"✓ {message}", kwargs)
    
    def _log_with_context(self, level, message, context):
        """Log message with optional context"""
        if context:
            context_str = ', '.join(f'{k}={v}' for k, v in context.items())
            message = f"{message} [{context_str}]"
        self.logger.log(level, message)
    
    def get_logger(self):
        """Get underlying logger instance"""
        return self.logger


def get_logger(name, log_dir='logs'):
    """Get or create a logger"""
    return ScraperLogger(name, log_dir=log_dir)
