# Download Implementation Guide

## Current Status

✅ Folder structure mapping works
✅ Song metadata extraction (partial)
❌ Download URLs need to be found

## What We Need

To download songs, we need to find the actual MP3/audio file URLs. Here's how to find them:

### Method 1: Check for Download Buttons

1. Click on a song in Udio
2. Look for a download button
3. Right-click → Inspect the download button
4. Check what happens when you click it (does it trigger a download?)
5. Share the button's HTML and any network requests

### Method 2: Inspect Network Requests

1. Open DevTools (F12) → Network tab
2. Filter by "Media" or "XHR"
3. Play a song or click download
4. Look for requests that return audio files (.mp3, .wav, etc.)
5. Check the URL pattern
6. Share the URL format

### Method 3: Check Audio Elements

Run this in console while viewing songs:

```javascript
// Find all audio elements
const audioElements = document.querySelectorAll('audio');
console.log('Audio elements:', audioElements.length);

audioElements.forEach((audio, i) => {
  console.log(`Audio ${i}:`);
  console.log('  src:', audio.src);
  console.log('  currentSrc:', audio.currentSrc);
  
  const sources = audio.querySelectorAll('source');
  sources.forEach((source, j) => {
    console.log(`  source ${j}:`, source.src);
  });
});
```

### Method 4: Check for API Endpoints

Run this in console:

```javascript
// Intercept fetch requests
const originalFetch = window.fetch;
window.fetch = function(...args) {
  console.log('Fetch:', args[0]);
  return originalFetch.apply(this, args);
};

// Now play a song or click download and watch console
```

## Implementation Options

### Option A: Direct Download URLs

If we can find direct MP3 URLs:
- Extract URLs during mapping
- Use `chrome.downloads.download()` API
- Preserve folder structure in filenames

### Option B: Click Download Buttons

If songs have download buttons:
- Find download button for each song
- Click it programmatically
- Let browser handle the download
- May need to rename files after download

### Option C: Capture Audio Streams

If songs are streamed:
- Intercept network requests
- Capture audio data
- Save as files
- More complex but works for streaming

### Option D: Use Udio API

If Udio has an API:
- Find API endpoints
- Get authentication token
- Request song data directly
- Download via API

## Next Steps

1. **Investigate download mechanism**
   - How do you normally download songs from Udio?
   - Is there a download button?
   - Does it download directly or open a new tab?

2. **Find audio URLs**
   - Run the diagnostic scripts above
   - Share the results
   - We'll implement the appropriate method

3. **Test with one song**
   - Get it working for a single song first
   - Then scale to full library

## Current Code

The extension currently:
- Maps folder structure ✅
- Extracts song metadata (title, artist, URL) ✅
- Has download button UI ✅
- Needs: actual download URLs ❌

## Questions to Answer

1. Does Udio have a download button for songs?
2. What format are the songs (MP3, WAV, etc.)?
3. Are songs streamed or directly downloadable?
4. Do you need to be logged in to download?
5. Is there a rate limit or download limit?

Once we know the answers, we can implement the appropriate download method!
