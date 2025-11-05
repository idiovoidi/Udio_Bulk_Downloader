"""
Core scraping framework components.
"""

from .browser import BrowserConnection
from .extractor import BaseExtractor, ScrollableExtractor
from .mapper import BaseMapper

__all__ = [
    'BrowserConnection',
    'BaseExtractor',
    'ScrollableExtractor',
    'BaseMapper',
]
