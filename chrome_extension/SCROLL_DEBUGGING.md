# Scroll Debugging Guide

## Issue: Not All Songs Detected

If the extension reports fewer songs than expected (e.g., 187 instead of 2000), use this guide to debug.

## Quick Fixes

### 1. Increase Scroll Attempts
The extension now uses up to 200 scroll attempts (increased from 50) to handle large libraries.

### 2. Clear Cache and Re-run
```
1. Click "🗑️ Clear Cache"
2. Refresh the Udio page (F5)
3. Re-run mapping
```

### 3. Check Scroll Container
Open DevTools (F12) and run:
```javascript
// Check scroll container
const container = document.querySelector('main') || 
                 document.querySelector('[role="main"]') || 
                 document.querySelector('.overflow-auto') ||
                 document.documentElement;

console.log('Container:', container);
console.log('Scroll height:', container.scrollHeight);
console.log('Client height:', container.clientHeight);
console.log('Scroll top:', container.scrollTop);
```

## Debugging Steps

### Step 1: Check Visible Songs
```javascript
// In DevTools console on udio.com
const rows = document.querySelectorAll('tr[class*="absolute"]');
console.log('Visible rows:', rows.length);

const links = document.querySelectorAll('a[href*="/songs/"]');
console.log('Song links:', links.length);
```

### Step 2: Monitor Scrolling
Watch the extension logs:
```
1. Click "📋 View Debug Logs"
2. Look for scroll progress:
   - "Scroll 1: 10 songs (+10), bottom: 5000px"
   - "Scroll 2: 25 songs (+15), bottom: 4000px"
   - "Progress: 100 songs found after 10 scroll attempts"
```

### Step 3: Check Stop Conditions
The extension stops when:
1. At bottom AND no new songs for 5 attempts
2. Scroll position stuck AND at bottom for 5 attempts
3. No new songs for 10 attempts (anywhere)
4. Maximum 200 scroll attempts reached

### Step 4: Manual Scroll Test
1. Open folder with many songs
2. Manually scroll to bottom
3. Count how many songs you see
4. Compare with extension count

## Common Issues

### Issue 1: Virtual Scrolling
**Symptom:** Only ~200 songs detected in folder with 2000

**Cause:** Udio uses virtual scrolling - only renders visible songs

**Solution:** Extension now scrolls more aggressively:
- Larger scroll amounts (2000px for large lists)
- Longer wait times (1200ms for >500 songs)
- More attempts (200 max)

### Issue 2: Slow Loading
**Symptom:** Extension stops before all songs load

**Cause:** Songs take time to render after scroll

**Solution:** Increased wait times:
- Initial wait: 2000ms (was 1500ms)
- Per-scroll wait: 1000-1200ms (was 800ms)
- More patience before stopping (5-10 attempts)

### Issue 3: Wrong Container
**Symptom:** No scrolling happens

**Cause:** Wrong scroll container detected

**Solution:** Check container detection:
```javascript
// Should find the scrollable element
const container = DOMUtils.getScrollContainer();
console.log('Container:', container.tagName, container.className);
```

### Issue 4: Duplicate Detection
**Symptom:** Same songs counted multiple times

**Cause:** URL deduplication not working

**Solution:** Extension uses Set to track seen URLs:
```javascript
const seenUrls = new Set();
if (!seenUrls.has(song.url)) {
  seenUrls.add(song.url);
  songs.push(song);
}
```

## Advanced Debugging

### Enable Verbose Logging
In `song-extractor.js`, the logger already logs:
- Each scroll attempt with song count
- Distance from bottom
- Progress every 10 attempts
- Stop reason

### Manual Extraction Test
Run in DevTools console:
```javascript
// Test extraction on current view
const rows = document.querySelectorAll('tr[class*="absolute"]');
const songs = [];

rows.forEach(row => {
  const link = row.querySelector('a[href*="/songs/"]');
  const title = row.querySelector('h4');
  
  if (link && title) {
    songs.push({
      url: link.href,
      title: title.textContent.trim()
    });
  }
});

console.log('Extracted:', songs.length, 'songs');
console.log('Sample:', songs.slice(0, 5));
```

### Check Scroll Behavior
```javascript
// Test scrolling
const container = document.querySelector('main');
const before = container.scrollTop;

container.scrollBy(0, 1000);

setTimeout(() => {
  const after = container.scrollTop;
  console.log('Scrolled:', after - before, 'px');
  console.log('At bottom:', 
    (container.scrollTop + container.clientHeight) >= 
    (container.scrollHeight - 50)
  );
}, 1000);
```

## Configuration Tweaks

### For Very Large Libraries (>1000 songs)
Edit `song-extractor.js`:

```javascript
// Increase max attempts
const maxAttempts = 300; // was 200

// Increase scroll amount
const scrollAmount = 3000; // was 2000

// Increase wait time
const waitTime = 1500; // was 1200
```

### For Slow Connections
```javascript
// Increase wait times
await DOMUtils.sleep(2000); // initial wait
const waitTime = 2000; // per-scroll wait
```

### For Fast Connections
```javascript
// Decrease wait times
await DOMUtils.sleep(1000); // initial wait
const waitTime = 800; // per-scroll wait
```

## Verification

### After Changes
1. Clear cache
2. Refresh page
3. Re-run mapping
4. Check logs for:
   - Total scroll attempts
   - Final song count
   - Stop reason

### Expected Behavior
For 2000 songs:
- Scroll attempts: 50-150
- Time: 2-5 minutes
- Stop reason: "At bottom with no new songs"

## Reporting Issues

If still not working, provide:
1. Expected song count
2. Actual song count
3. Number of folders
4. Scroll attempts (from logs)
5. Stop reason (from logs)
6. Browser console errors

## Quick Reference

### Key Parameters
```javascript
maxAttempts: 200        // Maximum scroll attempts
scrollAmount: 1000-2000 // Pixels per scroll
waitTime: 1000-1200     // Milliseconds between scrolls
stopThreshold: 5-10     // Attempts with no new songs
```

### Stop Conditions
```javascript
// Condition 1: At bottom, no new songs
isAtBottom && noNewCount >= 5

// Condition 2: Scroll stuck at bottom
scrollTop === lastScrollTop && consecutiveNoChange >= 5 && isAtBottom

// Condition 3: Long time no new songs
noNewCount >= 10

// Condition 4: Max attempts
attempts >= maxAttempts
```

## Success Indicators

✅ Good signs:
- "Progress: X songs found after Y scroll attempts" every 10 attempts
- Song count increasing steadily
- Stops with "At bottom with no new songs"
- Final count matches expected

❌ Bad signs:
- Stops after only 3-5 attempts
- "No new songs after 3 attempts" (too early)
- Song count much lower than expected
- "Scroll position stuck" (wrong container)

---

**Last Updated:** 2024-11-05
**Version:** 2.1.1 (Scroll Fix)
