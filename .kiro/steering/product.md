---
inclusion: always
---

# Product Overview

Udio Downloader is a Python CLI tool for backing up complete music libraries from the Udio platform. It preserves folder hierarchy, song metadata, and supports resumable downloads.

## Core Workflows

### 1. Map Library Structure
Extract folder hierarchy and song metadata from user's Udio library without downloading files. Output: JSON structure mapping folders and songs.

### 2. Download Content
Bulk download all songs with concurrent processing (default: 3 workers). Preserves folder organization and metadata. Supports resume on interruption.

### 3. Authentication Flow
- Secure credential storage via keyring
- Session persistence (~/.udio_downloader/session.json, 24hr expiry)
- Automatic session renewal
- Chrome remote debugging integration (port 9222)

## Product Constraints

- Platform shutdown imminent - reliability and data preservation are critical
- Must handle large libraries (100+ songs) efficiently
- Network interruptions are common - resume capability is essential
- Session management required - Udio uses authentication cookies

## User Expectations

- Simple CLI commands (map, download, resume)
- Clear progress indicators during operations
- Preserved folder structure matches Udio's organization
- Metadata includes: title, artist, duration, creation date, folder path
- Downloads continue from last successful point on resume

## Output Structure

```
downloads/
├── metadata.db          # SQLite database with song metadata
├── Folder Name/
│   ├── song1.mp3
│   └── song2.mp3
└── Another Folder/
    └── song3.mp3
```

## Chrome Extension Component

Browser extension provides direct library access for mapping. Runs in user's authenticated Chrome session, bypassing API limitations.
