# DownloadManager Usage Guide

## Basic Usage

```python
from udio_downloader.services import DatabaseManager, DownloadManager

# Initialize database
db = DatabaseManager(db_path='./downloads/metadata.db')

# Initialize download manager
dm = DownloadManager(
    db_manager=db,
    output_dir='./downloads',
    user_data_dir='./chrome-profile',  # Path to authenticated Chrome profile
    concurrent_workers=3,
    rate_limit_delay=1.0
)

# Start downloads
stats = dm.start_downloads(resume=True)

print(f"Downloaded {stats['completed']} songs")
print(f"Failed: {stats['failed']}, Skipped: {stats['skipped']}")
print(f"Resumed: {stats['resumed']}")
print(f"Duration: {stats['duration']:.1f}s")

# Cleanup
db.shutdown()
```

## Configuration Options

### concurrent_workers
- **Type:** int
- **Default:** 3
- **Description:** Number of parallel download workers
- **Recommendation:** 3-5 for optimal performance without overwhelming the server

### rate_limit_delay
- **Type:** float
- **Default:** 1.0
- **Description:** Minimum delay between downloads in seconds
- **Recommendation:** Keep at 1.0 to avoid rate limiting

### user_data_dir
- **Type:** str
- **Required:** Yes
- **Description:** Path to Chrome user data directory with authenticated session
- **Setup:** 
  1. Login to Udio in Chrome
  2. Close Chrome
  3. Point to the profile directory (e.g., `C:\Users\YourName\AppData\Local\Google\Chrome\User Data\Default`)

## Output Structure

```
downloads/
├── metadata.db
├── Folder1/
│   ├── Song1_abc123.mp3
│   ├── Song1_abc123_lyrics.txt
│   ├── Song1_abc123_cover.jpg
│   └── Song1_abc123_metadata.json
└── Folder2/
    ├── Song2_def456.mp3
    ├── Song2_def456_lyrics.txt
    ├── Song2_def456_cover.png
    └── Song2_def456_metadata.json
```

## Metadata JSON Format

```json
{
  "id": "abc123",
  "title": "My Song",
  "artist": "Artist Name",
  "duration_seconds": 180,
  "created_date": "2024-01-15",
  "is_liked": true,
  "is_disliked": false,
  "play_count": 42,
  "likes_count": 10,
  "lyrics_available": true,
  "tags": ["rock", "energetic"],
  "metadata_collected_at": "2024-01-20T10:30:00",
  "downloaded_at": "2024-01-20T11:00:00"
}
```

## Resume Capability

The DownloadManager automatically resumes interrupted downloads:

1. **Partial Audio Files:** Uses HTTP Range requests to continue from last byte
2. **ETag Validation:** Ensures file hasn't changed on server
3. **Size Validation:** Verifies partial file integrity
4. **Status Tracking:** Database tracks pending/failed/partial/completed states

To resume after interruption:
```python
# Just run start_downloads again - it automatically detects and resumes
stats = dm.start_downloads(resume=True)
```

## Error Handling

### Network Errors
- Automatic retry with exponential backoff (handled in future task 5)
- Failed downloads marked in database for manual retry
- Detailed error logging

### Missing Content
- Missing lyrics: Download continues without lyrics
- Missing cover art: Download continues without cover
- Missing audio: Download fails, marked for retry

### Rate Limiting
- 429 responses trigger worker pause (future task 5)
- Configurable rate limit delay prevents most rate limiting

## Advanced Usage

### Custom URL Resolution
```python
# Resolve URLs for a specific song
urls = await dm.resolve_song_urls('song_id_123')
print(f"Audio: {urls['audio_url']}")
print(f"Lyrics: {urls['lyrics_url']}")
print(f"Cover: {urls['cover_url']}")
```

### Manual Download
```python
# Download audio with resume
path, etag, size = dm.download_audio_with_resume(
    url='https://example.com/audio.mp3',
    output_path=Path('./song.mp3'),
    existing_size=1024000,  # Resume from 1MB
    existing_etag='abc123'
)

# Download lyrics
lyrics_path = await dm.download_lyrics(
    song_id='song_123',
    lyrics_url='https://example.com/lyrics',
    output_path=Path('./lyrics.txt')
)

# Download cover art
cover_path = dm.download_cover_art(
    cover_url='https://example.com/cover.jpg',
    output_path=Path('./cover')  # Extension auto-detected
)
```

## Troubleshooting

### "Playwright browser context not initialized"
- Ensure `start_downloads()` is called (it initializes Playwright)
- Don't call `resolve_song_urls()` before `start_downloads()`

### "Could not resolve audio URL"
- Check that user_data_dir points to authenticated Chrome profile
- Verify you're logged into Udio in that profile
- Check network connectivity

### Slow Downloads
- Increase `concurrent_workers` (but not too high)
- Check network speed
- Verify rate_limit_delay isn't too high

### Resume Not Working
- Ensure server supports Range requests (Accept-Ranges: bytes)
- Check that ETag matches (file may have changed on server)
- Verify partial file isn't corrupted

## Performance Tips

1. **Optimal Concurrency:** 3-5 workers balances speed and server load
2. **Rate Limiting:** Keep at 1.0s to avoid 429 errors
3. **Disk I/O:** Use SSD for better performance with many small files
4. **Network:** Stable connection important for resume capability
5. **Memory:** Each worker uses ~50MB, plan accordingly

## Logging

Enable debug logging to see detailed progress:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Log levels:
- **INFO:** Progress updates, completed downloads
- **DEBUG:** URL resolution, file operations
- **WARNING:** Resume failures, missing content
- **ERROR:** Download failures, network errors
