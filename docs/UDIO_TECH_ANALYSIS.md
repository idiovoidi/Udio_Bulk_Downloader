# Udio Platform Technical Analysis

## Tech Stack
- **React** + **Next.js** (detected via `__NEXT_DATA__`)
- **Radix UI** / **shadcn/ui** (ARIA patterns: `role="tree"`, `role="button"`)
- **Tailwind CSS** (utility classes)
- **Lucide icons** (SVG icons)

## DOM Selectors

**Folder Tree:**
- Container: `[role="tree"]`
- Folder button: `[role="button"][aria-expanded]`
- Folder name: `button[title]` attribute
- Expand button: `button[aria-label="Expand"]`

**Song List:**
- Rows: `tr[class*="absolute"]` (virtual scrolling)
- Song ID: `a[href*="/songs/"]` → extract from href
- Title: `h4` element
- Duration: `.text-muted-foreground` (format: `MM:SS`)
- Cover: `img[alt="Song cover"]`
- Tags: `a[href*="/tags/"]`
- Play count: `.lucide-play` + adjacent `span`
- Like status: `.lucide-thumbs-up` SVG `fill` attribute

## Virtual Scrolling Behavior
- Only visible rows in DOM (`position: absolute`)
- Scroll triggers lazy load (wait 1-2s between scrolls)
- Previous content removed as you scroll
- Must scroll to bottom to see all items
- Track seen URLs with `Set()` to avoid duplicates

## Extractable Metadata
**Available:** Song ID, title, duration, cover URL, tags, play/like counts, like status, folder path
**Not available:** Download URL, creation date, audio format, lyrics (requires API/detail page)

## API & Authentication
**Endpoints (inferred):**
- `/songs/{id}` - Song page
- `/api/songs/{id}` - Metadata JSON
- `/api/songs/{id}/download` - Download URL (likely signed/temporary)

**Auth:** Cookie-based, ~24hr expiry

## Timing Requirements
- After folder click: 2500ms
- After expand/collapse: 1200ms
- Between scrolls: 1000-1200ms (adaptive based on song count)
- Scroll amount: 1000px (small libraries) → 2000px (>100 songs)

## Exit Conditions for Scrolling
- Distance from bottom < 50px
- No new songs for 5+ attempts
- Scroll position unchanged

## Download URL Discovery Methods
1. **Network inspection:** Enable CDP, monitor audio requests (.mp3, .wav, .m4a, blob)
2. **API reverse engineering:** Inspect XHR during playback for `/api/songs/{id}/stream`
3. **Page scraping:** Navigate to song page, extract `<audio>` or `<source>` src

## Analysis Script Usage
```bash
start_chrome_debug.bat
python analyze_udio.py
```

Inspect network traffic (DevTools → Network → Media/XHR) while playing songs to identify download URL pattern.
