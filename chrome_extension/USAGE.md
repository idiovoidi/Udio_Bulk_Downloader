# Usage Guide

## Mapping Your Library

### Step 1: Prepare
- Open `udio.com/library`
- Click folder tree icon (📁) in top right
- Folder tree panel opens on right side

### Step 2: Map
- Click extension icon in toolbar
- Click "📁 Map Library Structure"
- Wait for completion (may take several minutes)
- Progress shown in popup

### Step 3: Export Checklist
- Click "📋 Export Song Checklist"
- Save the text file
- Use for systematic downloading

## Using the Checklist

### Format
```
[ ] 1. Song Title
    URL: https://www.udio.com/songs/abc123
    Duration: 3:45
    Tags: Electronic, Synthpop
```

### Workflow
1. Open checklist in text editor or print it
2. For each song:
   - Copy URL
   - Open in browser
   - Click Download → MP3
   - Mark [X] in checklist
3. Organize downloaded files by folder structure

### Tips
- Work folder by folder
- Save progress frequently (change [ ] to [X])
- Use Ctrl+F to search for specific songs
- Verify totals match summary at end

## Other Exports

### JSON Export
- Click "💾 Export as JSON"
- For programmatic processing
- Contains complete structure

### Text Export
- Click "📄 Export as Text"
- Human-readable hierarchy
- For browsing structure

## Buttons

| Button | Purpose |
|--------|---------|
| 📁 Map Library Structure | Scan all folders/songs |
| 🔍 Dump Tree Structure | Debug (check console) |
| 📋 Export Song Checklist | Download tracking list |
| ⬇️ Download All Songs | Creates download list |
| 💾 Export as JSON | Machine-readable format |
| 📄 Export as Text | Human-readable format |

## Time Estimates

| Library Size | Mapping Time |
|--------------|--------------|
| 10 folders | ~30 seconds |
| 50 folders | ~3 minutes |
| 100 folders | ~6 minutes |
| 200+ folders | 10+ minutes |

## What Gets Mapped

✓ All folders and subfolders
✓ All songs with metadata
✓ Root directory songs (not in folders)
✓ Folder hierarchy preserved
✓ Song URLs, duration, tags
✓ Play counts and likes

## Common Issues

**Mapping stuck**: Check console (F12) for errors, refresh and retry

**Missing songs**: Ensure folder tree is open before mapping

**Wrong counts**: Re-run mapping, verify all folders expanded

**No root songs**: Normal if all songs are in folders
