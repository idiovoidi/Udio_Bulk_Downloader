"""
Command-line interface for the Udio Downloader.
"""

import click
from pathlib import Path
from .models import DownloadConfig


@click.group()
@click.version_option(version="1.0.0")
def main():
    """Udio Downloader - Download all your songs before platform shutdown."""
    pass


@main.command()
@click.option('--output', '-o', default='./downloads', 
              help='Output directory for downloaded files')
@click.option('--concurrent', '-c', default=3, 
              help='Maximum concurrent downloads')
def map(output, concurrent):
    """Map folder structure without downloading."""
    click.echo("Mapping folder structure...")
    # Implementation will be added in later tasks


@main.command()
@click.option('--output', '-o', default='./downloads',
              help='Output directory for downloaded files')
@click.option('--concurrent', '-c', default=3,
              help='Maximum concurrent downloads')
def download(output, concurrent):
    """Download all songs and folders."""
    click.echo("Starting download process...")
    # Implementation will be added in later tasks


@main.command()
@click.option('--output', '-o', default='./downloads',
              help='Output directory for downloaded files')
def resume(output):
    """Resume interrupted download."""
    click.echo("Resuming download...")
    # Implementation will be added in later tasks


if __name__ == '__main__':
    main()