# Quick Start

## Setup
```bash
pip install -r requirements.txt
playwright install chromium
```

## Workflow
```bash
# 1. Export library using Chrome extension (chrome_extension/)
# 2. Import metadata
python -m udio_downloader import-metadata --json-file udio_library.json

# 3. Check status
python -m udio_downloader status

# 4. Download (browser opens for auth on first run)
python -m udio_downloader download
```

## Key Options
```bash
# Custom workers/rate limit
python -m udio_downloader download --concurrent 5 --rate-limit 2.0

# Custom output
python -m udio_downloader download --output ./my_music

# Headless mode
python -m udio_downloader download --headless
```

## Output
```
downloads/
├── metadata.db
├── Folder Name/
│   ├── Song.mp3
│   ├── Song.json
│   ├── Song.txt (lyrics)
│   └── Song.jpg (cover)
```

Session saved to `~/.udio_downloader/browser_profile`. Resume is automatic.
