"""
Main entry point for the Udio Downloader application.
"""

import sys
from pathlib import Path

# Add the parent directory to the Python path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from udio_downloader.cli import main

if __name__ == "__main__":
    main()