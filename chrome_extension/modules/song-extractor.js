// Song extraction logic (MV3 compliant with virtualized scrolling)
import { DOMUtils } from './dom-utils.js';

export class SongExtractor {
  constructor(logger, storage) {
    this.logger = logger;
    this.storage = storage;
    this.cache = new Map(); // Cache songs by folder path
    this.seenSongIds = new Set(); // Track seen song IDs for deduplication
  }

  /**
   * Extract songs with virtualized scrolling and deduplication
   * @param {Array|null} folderPath - Current folder path
   * @returns {Promise<Array>} Array of song objects
   */
  async extractSongsFromView(folderPath = null) {
    // Check cache first
    const cacheKey = folderPath ? folderPath.join('/') : 'root';
    if (this.cache.has(cacheKey)) {
      this.logger?.info(`Using cached songs for: ${cacheKey}`);
      return this.cache.get(cacheKey);
    }

    await DOMUtils.sleep(2000); // Initial wait for content
    
    const songs = [];
    const seenUrls = new Set();
    const scrollContainer = DOMUtils.getScrollContainer();
    
    this.logger?.info('Starting virtualized scroll extraction');
    
    // Virtualized scrolling with viewport-sized increments
    const viewportHeight = scrollContainer.clientHeight;
    const scrollIncrement = Math.max(viewportHeight, 800); // At least 800px
    
    let previousCount = 0;
    let stabilizationCount = 0;
    let attempts = 0;
    const maxAttempts = 200;
    const stabilizationThreshold = 3; // Stop after 3 stable reads
    
    let lastScrollTop = scrollContainer.scrollTop;
    let lastScrollHeight = scrollContainer.scrollHeight;
    
    while (attempts < maxAttempts) {
      // Extract from current viewport
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
      
      // Calculate distance from bottom
      const distanceFromBottom = currentScrollHeight - (currentScrollTop + clientHeight);
      const isAtBottom = distanceFromBottom < 50;
      
      // Detect stabilization (no new songs found)
      if (currentCount === previousCount) {
        stabilizationCount++;
      } else {
        stabilizationCount = 0;
      }
      
      this.logger?.debug(`Scroll ${attempts + 1}: ${currentCount} songs (+${currentCount - previousCount}), stable: ${stabilizationCount}/${stabilizationThreshold}`);
      
      // Stop conditions
      if (isAtBottom && stabilizationCount >= stabilizationThreshold) {
        this.logger?.info(`Stabilized at bottom: ${currentCount} songs`);
        break;
      }
      
      // Detect if scroll is stuck
      if (currentScrollTop === lastScrollTop && 
          currentScrollHeight === lastScrollHeight && 
          stabilizationCount >= stabilizationThreshold) {
        this.logger?.info('Scroll stuck, extraction complete');
        break;
      }
      
      previousCount = currentCount;
      lastScrollTop = currentScrollTop;
      lastScrollHeight = currentScrollHeight;
      
      // Virtualized scroll by viewport increment
      scrollContainer.scrollBy(0, scrollIncrement);
      
      // Adaptive wait time based on library size
      const waitTime = currentCount > 500 ? 1200 : 
                       currentCount > 200 ? 1000 : 800;
      await DOMUtils.sleep(waitTime);
      
      attempts++;
      
      // Progress indicator
      if (attempts % 10 === 0) {
        this.logger?.info(`Progress: ${currentCount} songs, ${attempts} scrolls`);
      }
      
      // Yield to browser every 5 attempts
      if (attempts % 5 === 0) {
        await DOMUtils.sleep(10);
      }
    }
    
    if (attempts >= maxAttempts) {
      this.logger?.warning(`Max attempts reached (${maxAttempts})`);
    }
    
    // Scroll back to top
    scrollContainer.scrollTo(0, 0);
    await DOMUtils.sleep(200);
    
    this.logger?.success(`Extracted ${songs.length} songs in ${attempts} scrolls`);
    
    // Cache the results
    this.cache.set(cacheKey, songs);
    
    return songs;
  }

  clearCache() {
    this.cache.clear();
    this.seenSongIds.clear();
    this.logger?.info('Song cache cleared');
  }

  getCacheSize() {
    return this.cache.size;
  }

  /**
   * Check if song has been seen (for deduplication)
   * @param {string} songId - Song ID
   * @returns {boolean} True if already seen
   */
  hasSeen(songId) {
    return this.seenSongIds.has(songId);
  }

  /**
   * Mark song as seen
   * @param {string} songId - Song ID
   */
  markAsSeen(songId) {
    this.seenSongIds.add(songId);
  }

  /**
   * Get deduplication statistics
   * @returns {Object} Stats object
   */
  getDeduplicationStats() {
    return {
      uniqueSongsSeen: this.seenSongIds.size,
      cachedFolders: this.cache.size
    };
  }

  _extractFromLinks(songs, seenUrls) {
    const songLinks = document.querySelectorAll('a[href*="/songs/"]');
    
    songLinks.forEach(link => {
      try {
        if (!seenUrls.has(link.href)) {
          const container = link.closest('tr, div[class*="group"], article, [class*="card"]');
          if (container) {
            const song = this.extractSongData(container);
            if (song?.url && song?.id) {
              // Deduplicate by song ID
              if (!this.hasSeen(song.id)) {
                seenUrls.add(song.url);
                songs.push(song);
                this.markAsSeen(song.id);
              }
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
        if (song?.url && song?.id && !seenUrls.has(song.url)) {
          // Deduplicate by song ID
          if (!this.hasSeen(song.id)) {
            seenUrls.add(song.url);
            songs.push(song);
            this.markAsSeen(song.id);
          }
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
        // Core fields
        title: this._extractTitle(element),
        url: this._extractUrl(element),
        id: null,
        
        // Extended metadata fields
        artist: this._extractArtist(element),
        duration: this._extractDuration(element),
        createdDate: this._extractCreationDate(element),
        
        // Media fields
        imageUrl: this._extractImage(element),
        lyricsAvailable: this._checkLyricsAvailability(element),
        
        // User interaction fields
        tags: this._extractTags(element),
        plays: null,
        likes: null,
        isLiked: this._checkLiked(element),
        isDisliked: this._checkDisliked(element),
        
        // Metadata tracking
        metadataCollectedAt: new Date().toISOString(),
        metadataHash: null
      };

      if (song.url) {
        const match = song.url.match(/\/songs\/([^/?]+)/);
        if (match) song.id = match[1];
      }

      this._extractCounts(element, song);
      
      // Generate metadata hash for change detection
      song.metadataHash = this._generateMetadataHash(song);

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

  /**
   * Extract artist name from song element
   * @param {Element} element - Song container element
   * @returns {string|null} Artist name or null
   */
  _extractArtist(element) {
    // Try multiple selectors for artist
    const artistSelectors = [
      '[data-artist]',
      '.artist',
      '[class*="artist"]',
      'a[href*="/users/"]'
    ];

    for (const selector of artistSelectors) {
      const artistElement = element.querySelector(selector);
      if (artistElement) {
        const artist = artistElement.textContent?.trim();
        if (artist && artist.length > 0) {
          return artist;
        }
      }
    }

    // Fallback: look for text near title that might be artist
    const textElements = element.querySelectorAll('.text-muted-foreground, .text-sm');
    for (const el of textElements) {
      const text = el.textContent?.trim();
      // Skip if it looks like duration or count
      if (text && !/^\d+:\d+$/.test(text) && !/^\d+$/.test(text)) {
        return text;
      }
    }

    return null;
  }

  _extractDuration(element) {
    const textNodes = element.querySelectorAll('.text-muted-foreground');
    for (const node of textNodes) {
      const text = node.textContent.trim();
      if (/^\d+:\d+$/.test(text)) return text;
    }
    return null;
  }

  /**
   * Extract creation date from song element
   * @param {Element} element - Song container element
   * @returns {string|null} ISO date string or null
   */
  _extractCreationDate(element) {
    // Try to find date in various formats
    const dateSelectors = [
      '[data-created]',
      '[data-date]',
      'time[datetime]',
      '[class*="date"]'
    ];

    for (const selector of dateSelectors) {
      const dateElement = element.querySelector(selector);
      if (dateElement) {
        const datetime = dateElement.getAttribute('datetime');
        if (datetime) {
          return datetime;
        }
        
        const dateText = dateElement.textContent?.trim();
        if (dateText) {
          // Try to parse date
          const parsed = this._parseDate(dateText);
          if (parsed) return parsed;
        }
      }
    }

    // Look for relative dates like "2 days ago"
    const textElements = element.querySelectorAll('.text-muted-foreground, .text-sm, .text-xs');
    for (const el of textElements) {
      const text = el.textContent?.trim();
      if (text) {
        const parsed = this._parseRelativeDate(text);
        if (parsed) return parsed;
      }
    }

    return null;
  }

  /**
   * Parse date string to ISO format
   * @param {string} dateStr - Date string
   * @returns {string|null} ISO date string or null
   */
  _parseDate(dateStr) {
    try {
      const date = new Date(dateStr);
      if (!isNaN(date.getTime())) {
        return date.toISOString();
      }
    } catch (error) {
      // Invalid date
    }
    return null;
  }

  /**
   * Parse relative date like "2 days ago" to ISO format
   * @param {string} text - Relative date text
   * @returns {string|null} ISO date string or null
   */
  _parseRelativeDate(text) {
    const now = new Date();
    
    // Match patterns like "X days ago", "X hours ago", etc.
    const patterns = [
      { regex: /(\d+)\s*seconds?\s*ago/i, unit: 'seconds' },
      { regex: /(\d+)\s*minutes?\s*ago/i, unit: 'minutes' },
      { regex: /(\d+)\s*hours?\s*ago/i, unit: 'hours' },
      { regex: /(\d+)\s*days?\s*ago/i, unit: 'days' },
      { regex: /(\d+)\s*weeks?\s*ago/i, unit: 'weeks' },
      { regex: /(\d+)\s*months?\s*ago/i, unit: 'months' },
      { regex: /(\d+)\s*years?\s*ago/i, unit: 'years' }
    ];

    for (const pattern of patterns) {
      const match = text.match(pattern.regex);
      if (match) {
        const value = parseInt(match[1]);
        const date = new Date(now);
        
        switch (pattern.unit) {
          case 'seconds': date.setSeconds(date.getSeconds() - value); break;
          case 'minutes': date.setMinutes(date.getMinutes() - value); break;
          case 'hours': date.setHours(date.getHours() - value); break;
          case 'days': date.setDate(date.getDate() - value); break;
          case 'weeks': date.setDate(date.getDate() - (value * 7)); break;
          case 'months': date.setMonth(date.getMonth() - value); break;
          case 'years': date.setFullYear(date.getFullYear() - value); break;
        }
        
        return date.toISOString();
      }
    }

    return null;
  }

  _extractImage(element) {
    const imgElement = element.querySelector('img[alt]');
    return imgElement?.src || null;
  }

  /**
   * Check if lyrics are available for this song
   * @param {Element} element - Song container element
   * @returns {boolean} True if lyrics available
   */
  _checkLyricsAvailability(element) {
    // Look for lyrics indicator
    const lyricsIndicators = [
      '[data-lyrics="true"]',
      '[aria-label*="lyrics"]',
      '[title*="lyrics"]',
      '.lyrics-available',
      'svg.lucide-file-text' // Lyrics icon
    ];

    for (const selector of lyricsIndicators) {
      if (element.querySelector(selector)) {
        return true;
      }
    }

    // Check for lyrics badge or text
    const textElements = element.querySelectorAll('.badge, .tag, .text-xs');
    for (const el of textElements) {
      const text = el.textContent?.toLowerCase();
      if (text && text.includes('lyrics')) {
        return true;
      }
    }

    return false;
  }

  _extractTags(element) {
    const tagLinks = element.querySelectorAll('a[href*="/tags/"]');
    return Array.from(tagLinks).map(tag => tag.textContent.trim());
  }

  /**
   * Generate metadata hash for change detection
   * Excludes timestamp to detect actual content changes
   * @param {Object} song - Song object
   * @returns {string} Hash string
   */
  _generateMetadataHash(song) {
    const hashData = {
      title: song.title,
      artist: song.artist,
      duration: song.duration,
      isLiked: song.isLiked,
      isDisliked: song.isDisliked,
      plays: song.plays,
      likes: song.likes,
      tags: song.tags?.sort().join(','), // Sort for consistency
      lyricsAvailable: song.lyricsAvailable
    };

    const hashString = JSON.stringify(hashData);
    return this._simpleHash(hashString);
  }

  /**
   * Simple hash function for strings
   * @param {string} str - String to hash
   * @returns {string} Hash string
   */
  _simpleHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash).toString(36);
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
