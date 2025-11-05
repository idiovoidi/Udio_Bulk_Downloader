"""CLI interface for Udio Library Downloader."""

import click
import logging
import asyncio
from pathlib import Path
from typing import Optional

from .services import DatabaseManager, MetadataImporter, DownloadManager, PlaywrightSessionManager
from .config import config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """Udio Library Downloader - Download and backup your Udio music library."""
    pass


@cli.command('import-metadata')
@click.option(
    '--json-file',
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help='Path to metadata JSON export from Chrome extension'
)
@click.option(
    '--db-path',
    default='./downloads/metadata.db',
    type=click.Path(path_type=Path),
    help='Path to SQLite database file (default: ./downloads/metadata.db)'
)
def import_metadata(json_file: Path, db_path: Path):
    """
    Import metadata from Chrome extension JSON export.
    
    This command imports folder structure, song metadata, and tags from a JSON
    file exported by the Chrome extension. It uses hash-based comparison to
    detect new and changed songs, updating only what's necessary.
    
    Example:
        udio-downloader import-metadata --json-file library_export.json
    """
    try:
        click.echo(f"Importing metadata from: {json_file}")
        click.echo(f"Database: {db_path}")
        click.echo()
        
        # Initialize database manager
        db_manager = DatabaseManager(str(db_path))
        
        # Initialize metadata importer
        importer = MetadataImporter(db_manager)
        
        # Import metadata
        with click.progressbar(
            length=100,
            label='Importing metadata',
            show_eta=False
        ) as bar:
            stats = importer.import_from_json(str(json_file))
            bar.update(100)
        
        # Display statistics
        click.echo()
        click.secho("Import Complete!", fg='green', bold=True)
        click.echo()
        
        # Folder statistics
        click.echo(f"Folders:")
        click.echo(f"  Added: {stats['folders_added']}")
        click.echo()
        
        # Song statistics
        click.echo(f"Songs:")
        click.echo(f"  Added: {stats['songs_added']}")
        click.echo(f"  Updated: {stats['songs_updated']}")
        click.echo(f"  Skipped (unchanged): {stats['songs_skipped']}")
        total_songs = stats['songs_added'] + stats['songs_updated'] + stats['songs_skipped']
        click.echo(f"  Total: {total_songs}")
        click.echo()
        
        # Tag statistics
        click.echo(f"Tags:")
        click.echo(f"  Added: {stats['tags_added']}")
        click.echo()
        
        # Incremental update summary
        new_or_changed = stats['songs_added'] + stats['songs_updated']
        if new_or_changed > 0:
            click.secho(
                f"Incremental Update: {new_or_changed} new or changed songs detected",
                fg='cyan'
            )
        else:
            click.secho("No new or changed songs detected", fg='yellow')
        
        # Error summary
        if stats.get('errors'):
            click.echo()
            click.secho("Errors encountered:", fg='red', bold=True)
            for error in stats['errors']:
                click.echo(f"  - {error}")
        
        # Shutdown database manager
        db_manager.shutdown()
        
    except FileNotFoundError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        raise click.Abort()
    except ValueError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        raise click.Abort()
    except Exception as e:
        click.secho(f"Unexpected error: {e}", fg='red', err=True)
        logger.exception("Import failed")
        raise click.Abort()


@cli.command('download')
@click.option(
    '--output',
    default='./downloads',
    type=click.Path(path_type=Path),
    help='Output directory for downloaded files (default: ./downloads)'
)
@click.option(
    '--concurrent',
    default=3,
    type=click.IntRange(1, 10),
    help='Number of concurrent download workers (default: 3)'
)
@click.option(
    '--resume/--no-resume',
    default=True,
    help='Resume interrupted downloads (default: enabled)'
)
@click.option(
    '--db-path',
    default='./downloads/metadata.db',
    type=click.Path(exists=True, path_type=Path),
    help='Path to SQLite database file (default: ./downloads/metadata.db)'
)
@click.option(
    '--rate-limit',
    default=1.0,
    type=float,
    help='Minimum delay between downloads in seconds (default: 1.0)'
)
@click.option(
    '--user-data-dir',
    type=click.Path(file_okay=False, path_type=Path),
    help='Chrome user data directory for authenticated Playwright session (default: ~/.udio_downloader/browser_profile)'
)
@click.option(
    '--headless/--no-headless',
    default=False,
    help='Run browser in headless mode (default: disabled)'
)
def download(
    output: Path,
    concurrent: int,
    resume: bool,
    db_path: Path,
    rate_limit: float,
    user_data_dir: Optional[Path],
    headless: bool
):
    """
    Download all songs from database using Playwright for URL resolution.
    
    This command downloads audio files, lyrics, cover art, and metadata for all
    songs in the database. It uses Playwright to resolve fresh URLs from the
    Udio platform and supports resuming interrupted downloads.
    
    The download process:
    - Queries database for pending, failed, and partial downloads
    - Uses Playwright to navigate to song pages and extract fresh URLs
    - Downloads audio files with HTTP Range resume support
    - Downloads lyrics and cover art where available
    - Saves metadata JSON files alongside audio files
    - Updates database with download status and file paths
    
    Examples:
        # Download with default settings (3 workers, resume enabled)
        udio-downloader download
        
        # Download with 5 concurrent workers
        udio-downloader download --concurrent 5
        
        # Download to custom directory
        udio-downloader download --output ./my_music
        
        # Download without resume (start fresh)
        udio-downloader download --no-resume
        
        # Use custom Chrome profile for authentication
        udio-downloader download --user-data-dir ~/.chrome-profile
    """
    try:
        # Ensure output directory exists
        output.mkdir(parents=True, exist_ok=True)
        
        # Use config defaults if not specified
        if not user_data_dir:
            user_data_dir = config.user_data_dir
        
        click.echo(f"Output directory: {output}")
        click.echo(f"Database: {db_path}")
        click.echo(f"Concurrent workers: {concurrent}")
        click.echo(f"Resume: {'enabled' if resume else 'disabled'}")
        click.echo(f"Rate limit: {rate_limit}s between downloads")
        click.echo(f"Chrome profile: {user_data_dir}")
        click.echo(f"Headless mode: {'enabled' if headless else 'disabled'}")
        click.echo()
        
        # Initialize database manager
        db_manager = DatabaseManager(str(db_path))
        
        # Get initial statistics
        initial_stats = db_manager.get_download_statistics()
        
        if initial_stats['total'] == 0:
            click.secho("No songs in database!", fg='yellow')
            click.echo("Run 'import-metadata' first to import songs.")
            db_manager.shutdown()
            return
        
        pending = initial_stats['pending'] + initial_stats['failed'] + initial_stats['partial']
        
        if pending == 0:
            click.secho("All songs already downloaded!", fg='green')
            click.echo()
            click.echo(f"Total songs: {initial_stats['total']}")
            click.echo(f"Completed: {initial_stats['completed']}")
            db_manager.shutdown()
            return
        
        click.echo(f"Songs to download: {pending}")
        click.echo(f"  Pending: {initial_stats['pending']}")
        click.echo(f"  Failed (retry): {initial_stats['failed']}")
        click.echo(f"  Partial (resume): {initial_stats['partial']}")
        click.echo()
        
        # Confirm before starting
        if not click.confirm("Start download?", default=True):
            click.echo("Download cancelled.")
            db_manager.shutdown()
            return
        
        click.echo()
        
        # Initialize Playwright session manager
        click.secho("Initializing Playwright session...", fg='cyan')
        session_manager = PlaywrightSessionManager(
            user_data_dir=str(user_data_dir),
            headless=headless
        )
        
        try:
            # Initialize session asynchronously
            asyncio.run(session_manager.initialize())
            
            # Check if authenticated
            if not session_manager.is_authenticated:
                click.secho(
                    "Warning: Not authenticated with Udio. "
                    "Please log in when the browser opens.",
                    fg='yellow'
                )
                click.echo()
                
                # Attempt to refresh session
                if click.confirm("Open browser to log in?", default=True):
                    success = asyncio.run(session_manager.refresh_session())
                    if not success:
                        click.secho("Failed to authenticate. Aborting.", fg='red')
                        asyncio.run(session_manager.cleanup())
                        db_manager.shutdown()
                        raise click.Abort()
                else:
                    click.secho("Authentication required. Aborting.", fg='red')
                    asyncio.run(session_manager.cleanup())
                    db_manager.shutdown()
                    raise click.Abort()
            
            click.secho("Session authenticated successfully!", fg='green')
            click.echo()
            
            # Initialize download manager
            download_manager = DownloadManager(
                db_manager=db_manager,
                output_dir=str(output),
                session_manager=session_manager,
                concurrent_workers=concurrent,
                rate_limit_delay=rate_limit
            )
            
            # Start downloads
            click.secho("Starting downloads...", fg='cyan', bold=True)
            click.echo()
            
            stats = download_manager.start_downloads(resume=resume)
            
        finally:
            # Cleanup Playwright session
            click.echo()
            click.secho("Cleaning up Playwright session...", fg='cyan')
            asyncio.run(session_manager.cleanup())
        
        # Display final statistics
        click.echo()
        click.secho("Download Complete!", fg='green', bold=True)
        click.echo()
        
        click.echo(f"Total songs processed: {stats['total']}")
        click.echo(f"  Completed: {stats['completed']}")
        click.echo(f"  Failed: {stats['failed']}")
        click.echo(f"  Skipped: {stats['skipped']}")
        click.echo(f"  Resumed: {stats['resumed']}")
        click.echo()
        
        click.echo(f"Duration: {stats['duration']:.1f}s")
        
        if stats['completed'] > 0:
            rate = stats['completed'] / stats['duration'] * 60
            click.echo(f"Average rate: {rate:.1f} songs/minute")
        
        # Show final database status
        click.echo()
        final_stats = db_manager.get_download_statistics()
        remaining = final_stats['pending'] + final_stats['failed'] + final_stats['partial']
        
        if remaining > 0:
            click.secho(
                f"Note: {remaining} songs still pending. Run download again to retry.",
                fg='yellow'
            )
        else:
            click.secho("All songs downloaded successfully!", fg='green')
        
        # Shutdown database manager
        db_manager.shutdown()
        
    except FileNotFoundError:
        click.secho(f"Error: Database not found at {db_path}", fg='red', err=True)
        click.echo("Run 'import-metadata' first to create the database.")
        raise click.Abort()
    except KeyboardInterrupt:
        click.echo()
        click.secho("Download interrupted by user", fg='yellow')
        click.echo("Run download again with --resume to continue.")
        raise click.Abort()
    except Exception as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        logger.exception("Download failed")
        raise click.Abort()


@cli.command('status')
@click.option(
    '--db-path',
    default='./downloads/metadata.db',
    type=click.Path(exists=True, path_type=Path),
    help='Path to SQLite database file (default: ./downloads/metadata.db)'
)
def status(db_path: Path):
    """
    Show download statistics and database status.
    
    Displays information about total songs, download progress, folder structure,
    and last run information.
    
    Examples:
        # Show status with default database
        udio-downloader status
        
        # Show status for custom database
        udio-downloader status --db-path ./my_music/metadata.db
    """
    try:
        # Initialize database manager
        db_manager = DatabaseManager(str(db_path))
        
        # Get statistics
        stats = db_manager.get_download_statistics()
        
        # Display statistics
        click.secho("Database Status", fg='cyan', bold=True)
        click.echo()
        
        click.echo(f"Database: {db_path}")
        click.echo()
        
        # Song statistics
        click.secho("Songs:", bold=True)
        click.echo(f"  Total: {stats['total']}")
        click.echo(f"  Completed: {stats['completed']}")
        click.echo(f"  Pending: {stats['pending']}")
        click.echo(f"  Failed: {stats['failed']}")
        click.echo(f"  Partial: {stats['partial']}")
        click.echo()
        
        # Calculate progress percentage
        if stats['total'] > 0:
            progress = (stats['completed'] / stats['total']) * 100
            click.echo(f"Progress: {progress:.1f}%")
            
            # Progress bar
            bar_width = 40
            filled = int(bar_width * progress / 100)
            bar = '█' * filled + '░' * (bar_width - filled)
            click.echo(f"[{bar}]")
            click.echo()
        
        # Folder structure summary
        folder_stats = db_manager.get_folder_statistics()
        if folder_stats:
            click.secho("Folder Structure:", bold=True)
            click.echo(f"  Total folders: {folder_stats['total_folders']}")
            click.echo(f"  Root songs: {folder_stats['root_songs']}")
            click.echo()
        
        # Last run information
        last_run = db_manager.get_last_metadata_run()
        if last_run:
            click.secho("Last Metadata Import:", bold=True)
            click.echo(f"  Date: {last_run['run_date']}")
            click.echo(f"  Songs processed: {last_run['songs_processed']}")
            click.echo(f"  Songs added: {last_run['songs_added']}")
            click.echo(f"  Songs updated: {last_run['songs_updated']}")
            click.echo(f"  Status: {last_run['status']}")
            click.echo()
        
        # Next steps
        pending_total = stats['pending'] + stats['failed'] + stats['partial']
        if pending_total > 0:
            click.secho("Next Steps:", fg='yellow', bold=True)
            click.echo(f"  Run 'udio-downloader download' to download {pending_total} pending songs")
        elif stats['total'] > 0 and stats['completed'] == stats['total']:
            click.secho("Status: All songs downloaded!", fg='green', bold=True)
        
        # Shutdown database manager
        db_manager.shutdown()
        
    except FileNotFoundError:
        click.secho(f"Error: Database not found at {db_path}", fg='red', err=True)
        click.echo("Run 'import-metadata' first to create the database.")
        raise click.Abort()
    except Exception as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        logger.exception("Status check failed")
        raise click.Abort()


if __name__ == '__main__':
    cli()
