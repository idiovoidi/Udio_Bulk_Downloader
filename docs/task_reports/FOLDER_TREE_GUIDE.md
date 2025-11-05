# Folder Tree Mapping Guide

## Overview

Version 3 of the content script uses the **folder tree side panel** to map your library structure. This is more reliable than trying to parse the main library view.

## How It Works

### 1. Finding the Folder Tree Panel

The script looks for:
```javascript
document.querySelector('[role="tree"][aria-label="Folder structure"]')
```

This is the side panel that appears when you click the folder icon.

### 2. Identifying Folder Types

**Folders with children** (expandable):
- Have an expand button: `button[aria-label="Expand"]`
- Have `aria-expanded` attribute (true/false)
- Contain a chevron icon (▶)

**Leaf folders** (no children):
- No expand button
- Just have a folder icon
- Clicking them shows songs in the main view

### 3. Mapping Process

For each folder:

1. **Extract name** from `button[title]` attribute
2. **Check if expandable** by looking for expand button
3. **If expandable:**
   - Click expand button
   - Wait for children to appear
   - Find children by comparing padding levels
   - Recursively process each child
   - Collapse folder when done
4. **If leaf folder:**
   - Click folder name to view songs
   - Count songs in main view
   - Record song count

### 4. Finding Children

Children are identified by:
- Appearing as siblings after the parent in the DOM
- Having greater `paddingLeft` than the parent
- Typically 16-24px more padding per level

## HTML Structure

### Expandable Folder
```html
<div role="button" aria-expanded="false">
  <div class="group">
    <button aria-label="Expand">
      <svg><!-- chevron icon --></svg>
    </button>
    <button title="Folder Name">Folder Name</button>
  </div>
</div>
```

### Leaf Folder
```html
<div role="button" aria-selected="false">
  <div class="group">
    <div class="ml-2 size-4">
      <svg><!-- folder icon --></svg>
    </div>
    <button title="Folder Name">Folder Name</button>
  </div>
</div>
```

## Key Selectors

| Element | Selector |
|---------|----------|
| Tree container | `[role="tree"][aria-label="Folder structure"]` |
| Folder item | Direct children of tree container |
| Folder name | `button[title]` |
| Expand button | `button[aria-label="Expand"]` |
| Expanded state | `[aria-expanded="true"]` |

## Timing

- **Expand animation:** 600ms wait
- **Collapse animation:** 200ms wait
- **Song loading:** 1000ms wait
- **Song count check:** 500ms additional wait

These delays ensure the DOM has updated before we try to read it.

## Error Handling

### Folder tree not found
```
Error: Folder tree panel not found. Please open the folder tree by clicking the folder icon.
```

**Solution:** Click the folder icon (📁) in the top right of the library page.

### Cannot read properties of undefined
This usually means:
- The folder tree structure changed
- The page hasn't fully loaded
- The selectors need updating

## Progress Tracking

The script tracks:
- `totalFolders`: Count of top-level folders
- `mappedFolders`: Number processed so far
- `totalSongs`: Running total of songs found
- `folders`: Array of folder data with hierarchy

Progress updates are sent every time a folder is processed.

## Output Structure

```javascript
{
  name: "Folder Name",
  path: ["Parent", "Child", "Folder Name"],
  hasChildren: true,
  isLeaf: false,
  subfolders: [
    // Recursive subfolder objects
  ],
  songCount: 0  // Only for leaf folders
}
```

## Debugging

### Enable verbose logging

Open browser console (F12) and look for:
- "Udio Folder Mapper v3 loaded"
- "Found folder tree panel"
- "Processing: Folder > Path > Here"
- "Expanding folder: Name"
- "Found X children for Name"
- "Leaf folder: Name, clicking to view songs"
- "Found X songs in Name"

### Check folder tree is open

Run in console:
```javascript
document.querySelector('[role="tree"][aria-label="Folder structure"]')
```

Should return an element, not null.

### Check folder structure

Run in console:
```javascript
const tree = document.querySelector('[role="tree"][aria-label="Folder structure"]');
console.log('Top-level folders:', tree.children.length);
```

## Limitations

1. **Must have folder tree open** - The script cannot open it automatically
2. **Slow for large libraries** - Each folder requires clicks and waits
3. **Song counting is approximate** - Relies on finding song elements in main view
4. **No song metadata** - Only counts songs, doesn't extract titles/artists

## Future Improvements

- Auto-open folder tree panel
- Better song element detection
- Extract song metadata (title, artist, duration)
- Parallel processing of folders
- Resume capability for interrupted mapping
