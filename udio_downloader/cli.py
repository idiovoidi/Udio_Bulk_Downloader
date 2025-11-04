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
    click.echo("⚠️  This command is not yet implemented.")
    click.echo("\n💡 Use the standalone script instead:")
    click.echo("   python scripts/map_udio_library_structure.py")
    click.echo("\nPrerequisites:")
    click.echo("  1. Chrome running with --remote-debugging-port=9222")
    click.echo("  2. Logged into Udio at https://www.udio.com/library")


@main.command()
@click.option('--output', '-o', default='./downloads',
              help='Output directory for downloaded files')
@click.option('--concurrent', '-c', default=3,
              help='Maximum concurrent downloads')
def download(output, concurrent):
    """Download all songs and folders."""
    click.echo("⚠️  This command is not yet implemented.")
    click.echo("\n💡 Next steps:")
    click.echo("  1. First run: python scripts/map_udio_library_structure.py")
    click.echo("  2. Review the analysis to identify download URLs")
    click.echo("  3. Implement the download logic based on the analysis")
    click.echo("\n📋 The download feature requires:")
    click.echo("  • Song URL extraction from library")
    click.echo("  • Concurrent download handling")
    click.echo("  • Progress tracking and resume capability")


@main.command()
@click.option('--output', '-o', default='./downloads',
              help='Output directory for downloaded files')
def resume(output):
    """Resume interrupted download."""
    click.echo("⚠️  This command is not yet implemented.")
    click.echo("\n💡 The resume feature will:")
    click.echo("  • Check for partially downloaded files")
    click.echo("  • Skip already completed downloads")
    click.echo("  • Continue from where it left off")
    click.echo("\n📋 First implement the download command before resume")


if __name__ == '__main__':
    main()