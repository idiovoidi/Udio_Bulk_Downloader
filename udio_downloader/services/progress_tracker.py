"""Progress tracking and reporting for download operations."""

import time
import logging
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from tqdm import tqdm


logger = logging.getLogger(__name__)


@dataclass
class WorkerStatus:
    """Status information for a single worker."""
    worker_id: int
    current_song: Optional[str] = None
    current_song_id: Optional[str] = None
    status: str = 'idle'  # idle, downloading, paused
    songs_completed: int = 0
    songs_failed: int = 0
    last_update: float = field(default_factory=time.time)


@dataclass
class DownloadStats:
    """Statistics for download operations."""
    total: int = 0
    completed: int = 0
    failed: int = 0
    skipped: int = 0
    resumed: int = 0
    pending: int = 0
    
    def get_progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total == 0:
            return 0.0
        processed = self.completed + self.failed + self.skipped
        return (processed / self.total) * 100


class ProgressTracker:
    """Track and display download progress with tqdm integration."""
    
    def __init__(
        self,
        total_songs: int,
        concurrent_workers: int = 3,
        show_worker_status: bool = True
    ):
        """
        Initialize progress tracker.
        
        Args:
            total_songs: Total number of songs to download
            concurrent_workers: Number of concurrent workers
            show_worker_status: Whether to show per-worker status
        """
        self.stats = DownloadStats(total=total_songs, pending=total_songs)
        self.concurrent_workers = concurrent_workers
        self.show_worker_status = show_worker_status
        
        # Worker tracking
        self.workers: Dict[int, WorkerStatus] = {
            i: WorkerStatus(worker_id=i) for i in range(concurrent_workers)
        }
        
        # Timing
        self.start_time = time.time()
        self.last_update_time = self.start_time
        
        # Progress bar
        self.pbar: Optional[tqdm] = None
        self._initialize_progress_bar()
        
        logger.info(f"ProgressTracker initialized for {total_songs} songs with {concurrent_workers} workers")
    
    def _initialize_progress_bar(self):
        """Initialize tqdm progress bar."""
        self.pbar = tqdm(
            total=self.stats.total,
            desc="Downloading",
            unit="song",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]',
            dynamic_ncols=True
        )
    
    def update(self, result: Dict[str, any]):
        """
        Update progress based on download result.
        
        Args:
            result: Download result dictionary with keys:
                - song_id: str
                - status: str (completed, failed, skipped)
                - error: Optional[str]
                - resumed: bool
                - worker_id: Optional[int]
        """
        status = result.get('status', 'unknown')
        
        # Update statistics
        if status == 'completed':
            self.stats.completed += 1
        elif status == 'failed':
            self.stats.failed += 1
        elif status == 'skipped':
            self.stats.skipped += 1
        
        if result.get('resumed', False):
            self.stats.resumed += 1
        
        self.stats.pending = self.stats.total - (
            self.stats.completed + self.stats.failed + self.stats.skipped
        )
        
        # Update worker status
        worker_id = result.get('worker_id')
        if worker_id is not None and worker_id in self.workers:
            worker = self.workers[worker_id]
            
            if status == 'completed':
                worker.songs_completed += 1
            elif status == 'failed':
                worker.songs_failed += 1
            
            worker.current_song = None
            worker.current_song_id = None
            worker.status = 'idle'
            worker.last_update = time.time()
        
        # Update progress bar
        self.pbar.update(1)
        
        # Update postfix with current stats
        self._update_progress_display()
        
        self.last_update_time = time.time()
    
    def update_worker_status(
        self,
        worker_id: int,
        song_title: Optional[str] = None,
        song_id: Optional[str] = None,
        status: str = 'downloading'
    ):
        """
        Update status for a specific worker.
        
        Args:
            worker_id: Worker identifier
            song_title: Current song title
            song_id: Current song ID
            status: Worker status (idle, downloading, paused)
        """
        if worker_id in self.workers:
            worker = self.workers[worker_id]
            worker.current_song = song_title
            worker.current_song_id = song_id
            worker.status = status
            worker.last_update = time.time()
            
            self._update_progress_display()
    
    def _update_progress_display(self):
        """Update progress bar postfix with current statistics."""
        elapsed = time.time() - self.start_time
        rate = self._calculate_rate()
        
        postfix = {
            'completed': self.stats.completed,
            'failed': self.stats.failed,
            'resumed': self.stats.resumed,
            'rate': f"{rate:.1f}/min"
        }
        
        if self.show_worker_status:
            active_workers = sum(1 for w in self.workers.values() if w.status == 'downloading')
            postfix['active'] = active_workers
        
        self.pbar.set_postfix(postfix)
    
    def _calculate_rate(self) -> float:
        """
        Calculate download rate in songs per minute.
        
        Returns:
            Songs per minute
        """
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            processed = self.stats.completed + self.stats.failed + self.stats.skipped
            return (processed / elapsed) * 60
        return 0.0
    
    def _calculate_eta(self) -> Optional[timedelta]:
        """
        Calculate estimated time remaining.
        
        Returns:
            Estimated time remaining as timedelta, or None if cannot calculate
        """
        rate = self._calculate_rate()
        if rate > 0 and self.stats.pending > 0:
            minutes_remaining = self.stats.pending / rate
            return timedelta(minutes=minutes_remaining)
        return None
    
    def get_summary(self) -> Dict[str, any]:
        """
        Get summary of download progress.
        
        Returns:
            Dictionary with summary statistics
        """
        elapsed = time.time() - self.start_time
        rate = self._calculate_rate()
        eta = self._calculate_eta()
        
        return {
            'total': self.stats.total,
            'completed': self.stats.completed,
            'failed': self.stats.failed,
            'skipped': self.stats.skipped,
            'resumed': self.stats.resumed,
            'pending': self.stats.pending,
            'progress_percentage': self.stats.get_progress_percentage(),
            'elapsed_seconds': elapsed,
            'rate_per_minute': rate,
            'eta_seconds': eta.total_seconds() if eta else None,
            'active_workers': sum(1 for w in self.workers.values() if w.status == 'downloading')
        }
    
    def print_worker_status(self):
        """Print detailed status for each worker."""
        if not self.show_worker_status:
            return
        
        print("\n" + "=" * 80)
        print("Worker Status:")
        print("-" * 80)
        
        for worker in self.workers.values():
            status_icon = "🔄" if worker.status == 'downloading' else "⏸️" if worker.status == 'paused' else "💤"
            
            current = worker.current_song or "Idle"
            if len(current) > 50:
                current = current[:47] + "..."
            
            print(
                f"{status_icon} Worker {worker.worker_id}: {current} "
                f"(✓{worker.songs_completed} ✗{worker.songs_failed})"
            )
        
        print("=" * 80 + "\n")
    
    def print_summary(self):
        """Print final summary report."""
        summary = self.get_summary()
        elapsed = timedelta(seconds=summary['elapsed_seconds'])
        
        print("\n" + "=" * 80)
        print("Download Summary")
        print("=" * 80)
        print(f"Total Songs:      {summary['total']}")
        print(f"Completed:        {summary['completed']} ({summary['completed']/summary['total']*100:.1f}%)")
        print(f"Failed:           {summary['failed']}")
        print(f"Skipped:          {summary['skipped']}")
        print(f"Resumed:          {summary['resumed']}")
        print("-" * 80)
        print(f"Duration:         {elapsed}")
        print(f"Average Rate:     {summary['rate_per_minute']:.1f} songs/min")
        
        if summary['failed'] > 0:
            print(f"\n⚠️  {summary['failed']} downloads failed. Check logs for details.")
            print("   Run the download command again to retry failed downloads.")
        
        if summary['resumed'] > 0:
            print(f"\n✓ {summary['resumed']} downloads were resumed from partial files.")
        
        print("=" * 80 + "\n")
    
    def close(self):
        """Close progress bar and cleanup."""
        if self.pbar:
            self.pbar.close()
        
        logger.info("ProgressTracker closed")
