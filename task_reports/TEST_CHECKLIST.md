# Testing Checklist for Folder Tree Mapping

## Pre-Test Setup

- [ ] Extension is loaded in Chrome (`chrome://extensions/`)
- [ ] Developer mode is enabled
- [ ] Extension has been refreshed after code changes
- [ ] Logged into Udio.com
- [ ] On the library page (`https://www.udio.com/library`)

## Step 1: Open Folder Tree Panel

- [ ] Can see the folder icon (📁) button in top right
- [ ] Click the folder icon
- [ ] Side panel opens on the right
- [ ] Can see list of folders in the panel
- [ ] Folders have expand buttons (▶) or folder icons

## Step 2: Verify Extension Detection

Open browser console (F12) and check:

- [ ] See message: "Udio Folder Mapper v3 loaded"
- [ ] No errors in console

Run this in console to verify tree is detected:
```javascript
document.querySelector('[role="tree"][aria-label="Folder structure"]')
```

- [ ] Returns an element (not null)
- [ ] Element has children

## Step 3: Start Mapping

- [ ] Click extension icon in toolbar
- [ ] Extension popup opens
- [ ] Click "Map Library Structure" button
- [ ] Popup shows "Starting mapping..."

## Step 4: Monitor Progress

Watch the console for:

- [ ] "Starting folder tree mapping..."
- [ ] "Found folder tree panel"
- [ ] "Found X top-level folders"
- [ ] "Processing: [folder name]"
- [ ] For expandable folders: "Expanding folder: [name]"
- [ ] For expandable folders: "Found X children for [name]"
- [ ] For leaf folders: "Leaf folder: [name], clicking to view songs"
- [ ] For leaf folders: "Found X songs in [name]"

Watch the popup for:

- [ ] Progress updates: "Folders: X/Y (Z%)"
- [ ] Song count updates: "Songs found: X"
- [ ] No errors displayed

## Step 5: Verify Behavior

In the Udio page, you should see:

- [ ] Folders automatically expanding (one at a time)
- [ ] Folders collapsing after processing
- [ ] Leaf folders being clicked
- [ ] Main view showing songs when leaf folder is clicked

## Step 6: Completion

When mapping completes:

Console shows:
- [ ] "Mapping complete!" with structure object
- [ ] No errors

Popup shows:
- [ ] "Mapping complete!"
- [ ] Total folders count
- [ ] Total songs count
- [ ] Results section with folder list
- [ ] Export buttons are enabled

## Step 7: Verify Results

Check the results in popup:

- [ ] Total folders matches expected count
- [ ] Total songs seems reasonable
- [ ] Root folders list shows folder names
- [ ] Subfolder counts are shown
- [ ] Song counts are shown

## Step 8: Export

- [ ] Click "Export as JSON"
- [ ] File downloads successfully
- [ ] Open JSON file
- [ ] Verify structure looks correct
- [ ] Check folder hierarchy is preserved
- [ ] Check song counts are included

- [ ] Click "Export as Text"
- [ ] File downloads successfully
- [ ] Open text file
- [ ] Verify hierarchical format
- [ ] Check indentation shows structure
- [ ] Check song counts are included

## Common Issues

### Issue: "Folder tree panel not found"

- [ ] Folder tree panel is actually open
- [ ] Try closing and reopening the panel
- [ ] Refresh the page and try again

### Issue: Mapping gets stuck

- [ ] Check console for errors
- [ ] Note which folder it's stuck on
- [ ] Try manually expanding that folder
- [ ] Refresh page and try again

### Issue: Song count is 0

- [ ] Manually click a leaf folder
- [ ] Check if songs appear in main view
- [ ] Inspect song elements (F12)
- [ ] Note the HTML structure/classes
- [ ] May need to update selectors

### Issue: Children not detected

- [ ] Manually expand a folder
- [ ] Inspect the HTML structure
- [ ] Check padding values of parent vs children
- [ ] May need to adjust padding threshold

## Success Criteria

✅ Mapping completes without errors
✅ All folders are detected
✅ Folder hierarchy is correct
✅ Song counts are reasonable
✅ Export works for both formats
✅ Exported data is usable

## Notes

Record any observations:

- Time taken: _____ minutes
- Total folders: _____
- Total songs: _____
- Any errors: _____
- Any stuck folders: _____
- Any incorrect counts: _____

## Next Steps

If successful:
- [ ] Test with full library
- [ ] Verify all folders are included
- [ ] Check for any missing songs
- [ ] Use exported data for backup

If issues found:
- [ ] Document the specific error
- [ ] Share console logs
- [ ] Share HTML samples
- [ ] Request code adjustments
