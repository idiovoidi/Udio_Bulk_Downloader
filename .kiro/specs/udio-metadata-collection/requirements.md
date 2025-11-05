# Requirements Document

## Introduction

This feature enables comprehensive metadata collection and download management for Udio music libraries. The system will extend the existing Chrome extension to collect detailed song metadata, store it in a SQLite database, and provide a Python-based download manager to systematically download audio files and lyrics while preserving folder structure. The system must support incremental updates and resume capability to handle interruptions and website delays.

## Glossary

- **Metadata_Collector**: The enhanced Chrome extension component that extracts song information from the Udio web interface
- **Database_Manager**: The Python component that manages the SQLite database for storing folder and song metadata
- **Download_Manager**: The Python service that orchestrates downloading audio files and lyrics based on database records
- **Udio_Platform**: The web-based music platform being backed up
- **Library_Structure**: The hierarchical organization of folders and songs in a user's Udio account
- **Incremental_Update**: The process of updating only new or changed songs without re-processing the entire library
- **Resume_Capability**: The ability to continue interrupted downloads from where they stopped

## Requirements

### Requirement 1

**User Story:** As a Udio user, I want to collect comprehensive metadata for all songs in my library, so that I have a complete catalog before the platform shuts down

#### Acceptance Criteria

1. WHEN the Metadata_Collector processes a song, THE Metadata_Collector SHALL extract song ID, title, artist, folder location, duration, creation date, like/dislike status, play count, cover art URL, genre tags, and lyrics availability
2. THE Database_Manager SHALL store all extracted metadata in a SQLite database with tables for folders, songs, tags, and lyrics
3. WHEN a song has already been cataloged, THE Metadata_Collector SHALL skip processing that song during subsequent runs
4. WHEN new songs are added to the Udio_Platform since the last run, THE Metadata_Collector SHALL detect and catalog only the new songs
5. THE Metadata_Collector SHALL record a timestamp for when each song's metadata was collected

### Requirement 2

**User Story:** As a Udio user, I want the system to handle website delays and errors gracefully, so that I can successfully collect all my songs despite platform instability

#### Acceptance Criteria

1. WHEN the Udio_Platform responds slowly, THE Metadata_Collector SHALL wait up to 30 seconds before timing out on a single song
2. IF a song fails to load after 3 retry attempts, THEN THE Metadata_Collector SHALL log the failure and continue processing remaining songs
3. THE Database_Manager SHALL track which songs failed to process with error details
4. WHEN the user reruns the collection process, THE Metadata_Collector SHALL retry previously failed songs
5. THE Metadata_Collector SHALL provide progress indicators showing songs processed, skipped, and failed

### Requirement 3

**User Story:** As a Udio user, I want to download all audio files and lyrics while preserving my folder structure, so that I have a complete local backup

#### Acceptance Criteria

1. THE Download_Manager SHALL read song records from the SQLite database where download status equals 'pending'
2. WHEN downloading a song, THE Download_Manager SHALL save the audio file as MP3 format in the corresponding folder path
3. WHERE lyrics are available for a song, THE Download_Manager SHALL download and save lyrics as a separate TXT file with the same base filename as the audio file
4. THE Download_Manager SHALL update the download status in the database to 'completed' with a timestamp after successful download
5. THE Download_Manager SHALL create the local folder structure matching the Library_Structure from the database

### Requirement 4

**User Story:** As a Udio user, I want to resume interrupted downloads, so that I don't have to restart the entire download process if something goes wrong

#### Acceptance Criteria

1. WHEN the Download_Manager starts, THE Download_Manager SHALL query the database for songs with download status not equal to 'completed'
2. THE Download_Manager SHALL skip downloading files that already exist locally with matching file size greater than 0 bytes
3. IF a download fails, THEN THE Download_Manager SHALL update the download status to 'failed' with error details
4. WHEN the user restarts the Download_Manager, THE Download_Manager SHALL automatically resume from incomplete and failed downloads
5. THE Download_Manager SHALL provide a summary showing total songs, completed downloads, pending downloads, and failed downloads

### Requirement 5

**User Story:** As a Udio user, I want concurrent downloads with rate limiting, so that downloads complete quickly without overwhelming the platform or my connection

#### Acceptance Criteria

1. THE Download_Manager SHALL support configurable concurrent download workers with a default of 3 workers
2. THE Download_Manager SHALL enforce a minimum delay of 1 second between starting new downloads
3. WHEN a download worker encounters a rate limit error, THE Download_Manager SHALL pause that worker for 60 seconds before retrying
4. THE Download_Manager SHALL display real-time progress showing active downloads, download speed, and estimated time remaining
5. THE Download_Manager SHALL allow the user to adjust concurrency level via command-line parameter

### Requirement 6

**User Story:** As a Udio user, I want to preserve additional metadata alongside downloaded files, so that I can reference song details offline

#### Acceptance Criteria

1. WHERE a song is downloaded, THE Download_Manager SHALL create a JSON metadata file with the same base filename as the audio file
2. THE metadata JSON file SHALL contain song ID, title, artist, duration, creation date, like/dislike status, play count, genre tags, and cover art URL
3. THE Download_Manager SHALL download cover art images and save them with the same base filename as the audio file with appropriate image extension
4. THE Database_Manager SHALL maintain referential integrity between folders and songs tables using foreign key constraints
5. THE Database_Manager SHALL support exporting the complete database to a portable JSON format for backup purposes
