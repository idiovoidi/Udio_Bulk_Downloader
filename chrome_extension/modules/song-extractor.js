// Song extraction logic
import { DOMUtils } from './dom-utils.js';

export class SongExtractor {
  constructor(logger) {
    this.logger = logger;
    this.cache = new Map(); // Cache songs by folder path
  }

  async extractSongsFromView(folderPath = null) {
    // Check cache first
    const cacheKey = folderPath ? folderPath.join('/') : 'root';
    if (this.cache.has(cacheKey)) {
      this.logger?.info(`Using cached songs for: ${cacheKey}`);
      return this.cache.get(cacheKey);
    }

    await DOMUtils.sleep(2000); // Increased initial wait
    
    const songs = [];
    const seenUrls = new Set();
    const scrollContainer = DOMUtils.getScrollContainer();
    
    this.logger?.info('Starting scroll-based song extraction');
    
    let previousCount = 0;
    let noNewCount = 0;
    let consecutiveNoChange = 0;
    let attempts = 0;
    const maxAttempts = 200; // Increased for large libraries
    let lastScrollTop = scrollContainer.scrollTop;
    
    // More aggressive scrolling for large lists
    while (attempts < maxAttempts) {
      // Extract from current view
      const songRows = document.querySelectorAll('tr[class*="absolute"]');
      
      if (songRows.length === 0) {
        this._extractFromLinks(songs, seenUrls);
      } else {
        this._extractFromRows(songRows, songs, seenUrls);
      }
      
      const currentCount = songs.length;
      const currentScrollTop = scrollContainer.scrollTop;
      const currentScrollHeight = scrollContainer.scrollHeight;
      const clientHeight = scrollContainer.clientHeight;
      
      // Calculate if truly at bottom
      const distanceFromBottom = currentScrollHeight - (currentScrollTop + clientHeight);
      const isAtBottom = distanceFromBottom < 50;
      
      this.logger?.debug(`Scroll ${attempts + 1}: ${currentCount} songs (+${currentCount - previousCount}), bottom: ${distanceFromBottom}px`);
      
      // Track if we found new songs
      if (currentCount === previousCount) {
        noNewCount++;
        consecutiveNoChange++;
      } else {
        noNewCount = 0;
        consecutiveNoChange = 0;
      }
      
      // Only stop if we're REALLY at the bottom AND no new songs for multiple attempts
      if (isAtBottom && noNewCount >= 5) {
        this.logger?.info(`Stopping: At bottom with no new songs for ${noNewCount} attempts`);
        break;
      }
      
      // If scroll position hasn't changed for many attempts AND we're at bottom, stop
      if (currentScrollTop === lastScrollTop && consecutiveNoChange >= 5 && isAtBottom) {
        this.logger?.info('Stopping: Scroll position stuck at bottom');
        break;
      }
      
      // If we've had no new songs for a very long time, stop
      if (noNewCount >= 10) {
        this.logger?.info('Stopping: No new songs for 10 attempts');
        break;
      }
      
      previousCount = currentCount;
      lastScrollTop = currentScrollTop;
      
      // Scroll down - use larger scroll for faster traversal
      const scrollAmount = currentCount > 100 ? 2000 : 1000;
      scrollContainer.scrollBy(0, scrollAmount);
      
      // Wait for content to load - longer wait for large lists
      const waitTime = currentCount > 500 ? 1200 : 1000;
      await DOMUtils.sleep(waitTime);
      
      attempts++;
      
      // Progress indicator every 10 attempts
      if (attempts % 10 === 0) {
        this.logger?.info(`Progress: ${currentCount} songs found after ${attempts} scroll attempts`);
      }
    }
    
    if (attempts >= maxAttempts) {
      this.logger?.warning(`Reached maximum scroll attempts (${maxAttempts})`);
    }
    
    scrollContainer.scrollTo(0, 0);
    this.logger?.success(`Extracted ${songs.length} songs in ${attempts} scroll attempts`);
    
    // Cache the results
    this.cache.set(cacheKey, songs);
    
    return songs;
  }

  clearCache() {
    this.cache.clear();
    this.logger?.info('Song cache cleared');
  }

  getCacheSize() {
    return this.cache.size;
  }

  _extractFromLinks(songs, seenUrls) {
    const songLinks = document.querySelectorAll('a[href*="/songs/"]');
    
    songLinks.forEach(link => {
      try {
        if (!seenUrls.has(link.href)) {
          const container = link.closest('tr, div[class*="group"], article, [class*="card"]');
          if (container) {
            const song = this.extractSongData(container);
            if (song?.url) {
              seenUrls.add(song.url);
              songs.push(song);
            }
          }
        }
      } catch (error) {
        // Skip problematic links but continue
        this.logger?.debug('Skipped link due to error', { error: error.message });
      }
    });
  }

  _extractFromRows(rows, songs, seenUrls) {
    rows.forEach(row => {
      try {
        const song = this.extractSongData(row);
        if (song?.url && !seenUrls.has(song.url)) {
          seenUrls.add(song.url);
          songs.push(song);
        }
      } catch (error) {
        // Skip problematic rows but continue
        this.logger?.debug('Skipped row due to error', { error: error.message });
      }
    });
  }

  extractSongData(element) {
    try {
      const song = {
        title: this._extractTitle(element),
        url: this._extractUrl(element),
        id: null,
        duration: this._extractDuration(element),
        imageUrl: this._extractImage(element),
        tags: this._extractTags(element),
        plays: null,
        likes: null,
        isLiked: this._checkLiked(element),
        isDisliked: this._checkDisliked(element)
      };

      if (song.url) {
        const match = song.url.match(/\/songs\/([^/?]+)/);
        if (match) song.id = match[1];
      }

      this._extractCounts(element, song);

      return (song.title && song.url) ? song : null;
    } catch (error) {
      this.logger?.warning('Error extracting song', { error: error.message });
      return null;
    }
  }

  _extractTitle(element) {
    const titleElement = element.querySelector('h4');
    return titleElement?.textContent?.trim() || null;
  }

  _extractUrl(element) {
    const linkElement = element.querySelector('a[href*="/songs/"]');
    return linkElement?.href || null;
  }

  _extractDuration(element) {
    const textNodes = element.querySelectorAll('.text-muted-foreground');
    for (const node of textNodes) {
      const text = node.textContent.trim();
      if (/^\d+:\d+$/.test(text)) return text;
    }
    return null;
  }

  _extractImage(element) {
    const imgElement = element.querySelector('img[alt]');
    return imgElement?.src || null;
  }

  _extractTags(element) {
    const tagLinks = element.querySelectorAll('a[href*="/tags/"]');
    return Array.from(tagLinks).map(tag => tag.textContent.trim());
  }

  _extractCounts(element, song) {
    const svgIcons = element.querySelectorAll('svg.lucide-play, svg.lucide-thumbs-up');
    svgIcons.forEach(svg => {
      const nextText = svg.nextSibling;
      if (nextText?.textContent) {
        const count = parseInt(nextText.textContent.trim());
        if (!isNaN(count)) {
          if (svg.classList.contains('lucide-play')) {
            song.plays = count;
          } else if (svg.classList.contains('lucide-thumbs-up')) {
            song.likes = count;
          }
        }
      }
    });
  }

  _checkLiked(element) {
    const likeButton = element.querySelector('button:has(svg.lucide-thumbs-up)');
    if (!likeButton) return false;

    const svg = likeButton.querySelector('svg.lucide-thumbs-up');
    if (!svg) return false;

    const fill = svg.getAttribute('fill');
    const stroke = svg.getAttribute('stroke');
    const isUnlike = likeButton.getAttribute('aria-label') === 'unlike';

    return fill === 'white' || fill === 'currentColor' || stroke === 'white' || isUnlike;
  }

  _checkDisliked(element) {
    const dislikeButton = element.querySelector('button:has(svg.lucide-thumbs-down)');
    if (!dislikeButton) return false;

    const svg = dislikeButton.querySelector('svg.lucide-thumbs-down');
    if (!svg) return false;

    const fill = svg.getAttribute('fill');
    const stroke = svg.getAttribute('stroke');
    const isUndislike = dislikeButton.getAttribute('aria-label') === 'undislike';

    return fill === 'white' || fill === 'currentColor' || stroke === 'white' || isUndislike;
  }
}
