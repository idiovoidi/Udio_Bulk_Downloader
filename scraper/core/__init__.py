"""
Core scraping framework components.
"""

from .browser import BrowserConnection
from .extractor import BaseExtractor
from .mapper import BaseMapper

__all__ = [
    'BrowserConnection',
    'BaseExtractor',
    'BaseMapper',
]
