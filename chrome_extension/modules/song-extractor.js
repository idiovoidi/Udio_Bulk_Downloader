// Song extraction logic
import { DOMUtils } from './dom-utils.js';

export class SongExtractor {
  constructor(logger) {
    this.logger = logger;
  }

  async extractSongsFromView() {
    await DOMUtils.sleep(1500);
    
    const songs = [];
    const seenUrls = new Set();
    const scrollContainer = DOMUtils.getScrollContainer();
    
    this.logger?.info('Starting scroll-based song extraction');
    
    let previousCount = 0;
    let noNewCount = 0;
    let attempts = 0;
    const maxAttempts = 50;
    
    while (attempts < maxAttempts) {
      const songRows = document.querySelectorAll('tr[class*="absolute"]');
      
      if (songRows.length === 0) {
        this._extractFromLinks(songs, seenUrls);
      } else {
        this._extractFromRows(songRows, songs, seenUrls);
      }
      
      const currentCount = songs.length;
      this.logger?.debug(`Scroll ${attempts + 1}: ${currentCount} songs (${currentCount - previousCount} new)`);
      
      if (currentCount === previousCount) {
        noNewCount++;
        if (noNewCount >= 3) break;
      } else {
        noNewCount = 0;
      }
      
      previousCount = currentCount;
      scrollContainer.scrollBy(0, 1000);
      await DOMUtils.sleep(800);
      attempts++;
    }
    
    scrollContainer.scrollTo(0, 0);
    this.logger?.success(`Extracted ${songs.length} songs`);
    
    return songs;
  }

  _extractFromLinks(songs, seenUrls) {
    const songLinks = document.querySelectorAll('a[href*="/songs/"]');
    
    songLinks.forEach(link => {
      if (!seenUrls.has(link.href)) {
        const container = link.closest('tr, div[class*="group"]');
        if (container) {
          const song = this.extractSongData(container);
          if (song?.url) {
            seenUrls.add(song.url);
            songs.push(song);
          }
        }
      }
    });
  }

  _extractFromRows(rows, songs, seenUrls) {
    rows.forEach(row => {
      const song = this.extractSongData(row);
      if (song?.url && !seenUrls.has(song.url)) {
        seenUrls.add(song.url);
        songs.push(song);
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
