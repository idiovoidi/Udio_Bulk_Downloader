# Refactoring Plan

## Architecture

### Phase 1: Folder Mapping ✓
Chrome extension maps folder hierarchy to JSON.

### Phase 2: Metadata Collection ✓
Extension collects: song ID, title, artist, folder path, likes/dislikes, duration, cover art, play count, creation date, lyrics availability.

**Database Schema:**
```sql
CREATE TABLE folders (id TEXT PRIMARY KEY, name TEXT, parent_id TEXT, path TEXT);
CREATE TABLE songs (id TEXT PRIMARY KEY, title TEXT, folder_id TEXT, url TEXT, duration TEXT, 
    is_liked BOOLEAN, cover_art_url TEXT, download_status TEXT DEFAULT 'pending');
CREATE TABLE tags (song_id TEXT, tag TEXT);
CREATE TABLE lyrics (song_id TEXT PRIMARY KEY, lyrics_text TEXT);
```

### Phase 3: Download Manager
Python service: reads SQLite DB, downloads MP3s + lyrics, preserves folder structure, tracks status, supports resume.

**File Structure:**
```
downloads/
├── metadata.db
└── [folders]/
    ├── song.mp3
    └── song_lyrics.txt
```

### Phase 4: Local UI (Future)
Flask/FastAPI backend + minimal frontend for browsing, search, playback.

## Data Flow
```
Chrome Extension → JSON → Python Importer → SQLite → Download Manager → Local Files → UI
```

## Status
- Phase 1-2: ✅ Complete
- Phase 3: In progress (download manager)
- Phase 4: Future
