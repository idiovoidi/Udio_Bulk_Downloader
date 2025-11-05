# CLI Usage Guide

## Installation

Install the package in development mode:

```bash
pip install -e .
```

This will install the `udio-downloader` command globally.

## Commands

### import-metadata

Import metadata from Chrome extension JSON export into the SQLite database.

**Usage:**

```bash
# Using the installed command
udio-downloader import-metadata --json-file library_export.json

# Or using python -m
python -m udio_downloader import-metadata --json-file library_export.json

# Specify custom database path
udio-downloader import-metadata --json-file library_export.json --db-path ./custom/path/metadata.db
```

**Options:**

- `--json-file FILE` (required): Path to metadata JSON export from Chrome extension
- `--db-path PATH` (optional): Path to SQLite database file (default: `./downloads/metadata.db`)

**Features:**

- **Hash-based incremental updates**: Only new or changed songs are processed
- **Automatic folder creation**: Folder hierarchy is preserved
- **Tag relationships**: Genre and style tags are imported
- **Statistics display**: Shows added, updated, and skipped counts

**Example Output:**

```
Importing metadata from: library_export.json
Database: ./downloads/metadata.db

Import Complete!

Folders:
  Added: 5

Songs:
  Added: 15
  Updated: 3
  Skipped (unchanged): 82
  Total: 100

Tags:
  Added: 45

Incremental Update: 18 new or changed songs detected
```

### status

Show download statistics and database status.

**Usage:**

```bash
# Using the installed command
udio-downloader status

# Or using python -m
python -m udio_downloader status

# Specify custom database path
udio-downloader status --db-path ./custom/path/metadata.db
```

**Options:**

- `--db-path PATH` (optional): Path to SQLite database file (default: `./downloads/metadata.db`)

**Example Output:**

```
Database Status

Total songs: 100
  Completed: 75
  Pending: 20
  Failed: 3
  Partial: 2

Progress: 75.0%
[██████████████████████████████░░░░░░░░░░]
```

## Workflow

### Step 1: Export metadata from Chrome extension

1. Open your Udio library page
2. Click the extension icon
3. Click "Map Library" to scan your library
4. Click "Export" to download the JSON file

### Step 2: Import metadata into database

```bash
udio-downloader import-metadata --json-file udio_metadata_2025-11-05.json
```

### Step 3: Check status

```bash
udio-downloader status
```

### Step 4: Download songs (coming soon)

```bash
udio-downloader download --output ./downloads --concurrent 3
```

## Incremental Updates

The import command supports incremental updates:

1. **First import**: All songs are added as new
2. **Subsequent imports**: 
   - Songs with unchanged metadata hash are skipped
   - Songs with changed metadata hash are updated
   - New songs are added

This allows you to:
- Re-run imports without duplicating data
- Update metadata for songs that have changed (likes, plays, etc.)
- Add newly created songs to your library

## Database Schema

The SQLite database contains the following tables:

- `folders`: Folder hierarchy with stable IDs
- `songs`: Song metadata with download status tracking
- `tags`: Genre and style tags linked to songs
- `lyrics`: Lyrics content (populated during download)
- `metadata_runs`: Import run history

## Troubleshooting

### "Database not found" error

Run `import-metadata` first to create the database:

```bash
udio-downloader import-metadata --json-file your_export.json
```

### "Invalid JSON file" error

Ensure the JSON file is a valid export from the Chrome extension (version 2.0+).

### Permission errors

Ensure you have write permissions to the database directory:

```bash
mkdir -p ./downloads
chmod 755 ./downloads
```

## Advanced Usage

### Custom database location

Store the database in a custom location:

```bash
udio-downloader import-metadata \
  --json-file library_export.json \
  --db-path ~/backups/udio/metadata.db
```

### Multiple libraries

Manage multiple Udio accounts with separate databases:

```bash
# Account 1
udio-downloader import-metadata \
  --json-file account1_export.json \
  --db-path ./account1/metadata.db

# Account 2
udio-downloader import-metadata \
  --json-file account2_export.json \
  --db-path ./account2/metadata.db
```

## Next Steps

After importing metadata, you can:

1. Use the `download` command to download audio files (coming in task 4)
2. Query the SQLite database directly for custom analysis
3. Export the database to JSON for backup (coming in task 9)
