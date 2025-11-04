# Troubleshooting Guide

## Error: "Could not establish connection. Receiving end does not exist."

### What This Means
The extension popup is trying to communicate with the content script, but the content script isn't loaded on the page yet.

### Solutions

#### Solution 1: Refresh the Page (Most Common)
1. **Refresh the Udio page** (press F5 or Ctrl+R)
2. Wait for the page to fully load
3. Try the extension again

#### Solution 2: Reload the Extension
1. Go to `chrome://extensions/`
2. Find "Udio Library Mapper"
3. Click the refresh icon (🔄)
4. Go back to Udio and refresh that page too

#### Solution 3: Check Extension is Enabled
1. Go to `chrome://extensions/`
2. Make sure "Udio Library Mapper" is toggled ON
3. Check that it has permissions for `https://www.udio.com/*`

### How to Verify Content Script is Loaded

Open browser console (F12) and look for:
```
Udio Folder Mapper v3 loaded
Folder mapper ready. Waiting for mapping command...
```

If you see these messages, the content script is working.

If you don't see these messages:
- Refresh the page
- Check the extension is enabled
- Check you're on `https://www.udio.com/library`

---

## Error: "Folder tree panel not found"

### What This Means
The script can't find the folder tree side panel in the page.

### Solutions

#### Solution 1: Open the Folder Tree Panel
1. Look for the **folder icon** (📁) button in the top right of the library page
2. Click it to open the folder tree side panel
3. You should see a list of folders appear on the right side
4. Try the extension again

#### Solution 2: Check You're on the Library Page
1. Make sure you're on `https://www.udio.com/library`
2. Not on "My Creations" or other pages
3. The folder tree is only available on the library page

#### Solution 3: Page Structure Changed
If Udio updated their UI, the selectors might need updating:
1. Open console (F12)
2. Run: `document.querySelector('[role="tree"]')`
3. If this returns `null`, the structure changed
4. Share the HTML structure for updates

---

## Mapping Gets Stuck

### What This Means
The script is processing a folder but not progressing.

### Solutions

#### Solution 1: Wait Longer
- Large folders with many subfolders take time
- Each folder requires clicks and waits
- Check console for progress messages

#### Solution 2: Check for Errors
1. Open console (F12)
2. Look for red error messages
3. Note which folder it's stuck on
4. Share the error for troubleshooting

#### Solution 3: Refresh and Retry
1. Refresh the Udio page
2. Reload the extension
3. Try mapping again
4. If it gets stuck on the same folder, that folder may have an issue

---

## Song Count is 0 or Wrong

### What This Means
The script can't find song elements in the main view, or the selectors don't match.

### Solutions

#### Solution 1: Check Songs Load
1. Manually click a folder that should have songs
2. Wait for songs to appear in the main view
3. If songs don't appear, there may be a loading issue

#### Solution 2: Inspect Song Elements
1. Click a folder with songs
2. Right-click on a song → "Inspect"
3. Note the HTML structure and classes
4. Share this info for selector updates

#### Solution 3: Increase Wait Time
The script waits 1000ms for songs to load. If your connection is slow:
1. Edit `content_v3.js`
2. Find: `await sleep(1000); // Wait for songs to load`
3. Change to: `await sleep(2000);`
4. Reload extension and try again

---

## Children/Subfolders Not Detected

### What This Means
The script isn't finding child folders when expanding parent folders.

### Solutions

#### Solution 1: Check Padding Detection
1. Manually expand a folder with children
2. Right-click on parent folder → "Inspect"
3. Note the `padding-left` value
4. Right-click on child folder → "Inspect"
5. Note the `padding-left` value
6. The difference should be 16-24px

If the difference is larger:
1. Edit `content_v3.js`
2. Find: `if (nextPadding - currentPadding < 30)`
3. Change `30` to a larger value (e.g., `50`)
4. Reload extension and try again

#### Solution 2: Check Folder Structure
The script assumes children appear as siblings after the parent in the DOM. If Udio changed this:
1. Inspect the expanded folder structure
2. Share the HTML for updates

---

## Export Buttons Disabled

### What This Means
No mapping data is available to export.

### Solutions

1. Complete a mapping first
2. Wait for "Mapping complete!" message
3. Export buttons will enable automatically

---

## Extension Icon Grayed Out

### What This Means
The extension is not active on the current page.

### Solutions

1. Make sure you're on `https://www.udio.com/*`
2. The extension only works on Udio.com
3. Check extension permissions in `chrome://extensions/`

---

## Progress Shows 0/0 Folders

### What This Means
The script found the folder tree but it appears empty.

### Solutions

1. Make sure the folder tree panel is actually open
2. Check that you have folders in your library
3. Try closing and reopening the folder tree panel
4. Refresh the page and try again

---

## Mapping is Very Slow

### What This Means
This is normal for large libraries.

### Expected Times
- 10 folders: ~30 seconds
- 50 folders: ~3 minutes
- 100 folders: ~6 minutes
- 200+ folders: 10+ minutes

Each folder requires:
- Expanding (600ms wait)
- Finding children
- Processing recursively
- Collapsing (200ms wait)
- For leaf folders: clicking and counting songs (1500ms)

### Solutions

#### Solution 1: Be Patient
- Let it run in the background
- Don't close the popup
- Don't navigate away from the page
- Watch console for progress

#### Solution 2: Test with Subset First
1. Manually collapse most folders
2. Leave only a few expanded
3. Run the mapping
4. Verify it works correctly
5. Then do the full library

---

## Console Shows Errors

### Common Errors and Solutions

#### "Cannot read properties of undefined"
- The HTML structure doesn't match expectations
- Share the full error message
- Share the HTML structure

#### "Element is not clickable"
- Another element is covering the button
- Try closing any popups or modals
- Refresh and try again

#### "Timeout waiting for..."
- Increase wait times in the script
- Check your internet connection
- Try again when Udio is less busy

---

## Getting Help

If none of these solutions work:

1. **Gather Information:**
   - Full error message from console
   - Screenshot of the issue
   - Sample of the HTML structure (F12 → Elements)
   - Your browser version
   - Number of folders in your library

2. **Share Details:**
   - What you were trying to do
   - What you expected to happen
   - What actually happened
   - Any error messages

3. **Try Minimal Test:**
   - Create a test folder with 1-2 songs
   - Try mapping just that folder
   - Share if it works or fails

---

## Quick Diagnostic Checklist

Run these in console (F12) to diagnose issues:

```javascript
// Check content script loaded
console.log('Content script loaded:', typeof chrome.runtime !== 'undefined');

// Check folder tree exists
console.log('Folder tree:', document.querySelector('[role="tree"][aria-label="Folder structure"]'));

// Count top-level folders
const tree = document.querySelector('[role="tree"][aria-label="Folder structure"]');
console.log('Top-level folders:', tree ? tree.children.length : 'Tree not found');

// Check for expand buttons
console.log('Expand buttons:', document.querySelectorAll('button[aria-label="Expand"]').length);

// Check for folder name buttons
console.log('Folder buttons:', document.querySelectorAll('button[title]').length);
```

Share the output of these commands when asking for help.
