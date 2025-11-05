# Chrome Extension Testing

## Load Extension

1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" → Select `chrome_extension` folder
4. Check for errors on extension card

## Test on Udio

1. Navigate to `https://www.udio.com/library`
2. Click extension icon
3. Popup should open

## Debug Consoles

**Background**: `chrome://extensions/` → Click "service worker"
**Content Script**: F12 on udio.com/library page
**Popup**: Right-click popup → Inspect

## Common Issues

**"Could not establish connection"**
- Refresh the page (F5)

**Extension icon grayed out**
- Must be on udio.com domain

**Buttons don't work**
- Check popup console for errors

## Quick Test

Run in page console (F12):
```javascript
console.log('Folder tree:', document.querySelector('[data-testid="folder-tree"]'));
console.log('Songs:', document.querySelectorAll('[data-testid="song-item"]').length);
```

## Minimal Test Extension

If nothing works, test Chrome extension system:

```json
// manifest.json
{
  "manifest_version": 3,
  "name": "Test",
  "version": "1.0",
  "action": {"default_popup": "popup.html"}
}
```

```html
<!-- popup.html -->
<!DOCTYPE html>
<html><body><h1>It works!</h1></body></html>
```
