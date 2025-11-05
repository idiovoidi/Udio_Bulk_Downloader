// Storage manager for chrome.storage.local operations
export class StorageManager {
  constructor(logger) {
    this.logger = logger;
  }

  /**
   * Get seen songs cache for incremental updates
   * @returns {Promise<Object>} Cache object with song IDs as keys
   */
  async getSeenCache() {
    try {
      const result = await chrome.storage.local.get(['seenSongsCache']);
      return result.seenSongsCache || {};
    } catch (error) {
      this.logger?.error('Failed to get seen cache', { error: error.message });
      return {};
    }
  }

  /**
   * Update seen songs cache
   * @param {Object} cache - New cache object
   */
  async updateSeenCache(cache) {
    try {
      await chrome.storage.local.set({
        seenSongsCache: cache,
        lastScanTimestamp: Date.now()
      });
      this.logger?.info('Seen cache updated', { songCount: Object.keys(cache).length });
    } catch (error) {
      this.logger?.error('Failed to update seen cache', { error: error.message });
      throw error;
    }
  }

  /**
   * Save content script state for resume capability
   * @param {Object} state - Current mapping state
   */
  async saveContentState(state) {
    try {
      await chrome.storage.local.set({
        contentMappingState: {
          ...state,
          timestamp: Date.now()
        }
      });
    } catch (error) {
      this.logger?.error('Failed to save content state', { error: error.message });
    }
  }

  /**
   * Load content script state
   * @returns {Promise<Object|null>} Saved state or null
   */
  async loadContentState() {
    try {
      const result = await chrome.storage.local.get(['contentMappingState']);
      return result.contentMappingState || null;
    } catch (error) {
      this.logger?.error('Failed to load content state', { error: error.message });
      return null;
    }
  }

  /**
   * Clear content script state
   */
  async clearContentState() {
    try {
      await chrome.storage.local.remove('contentMappingState');
    } catch (error) {
      this.logger?.error('Failed to clear content state', { error: error.message });
    }
  }

  /**
   * Get last scan timestamp
   * @returns {Promise<number|null>} Timestamp or null
   */
  async getLastScanTimestamp() {
    try {
      const result = await chrome.storage.local.get(['lastScanTimestamp']);
      return result.lastScanTimestamp || null;
    } catch (error) {
      this.logger?.error('Failed to get last scan timestamp', { error: error.message });
      return null;
    }
  }

  /**
   * Clear all extension data
   */
  async clearAll() {
    try {
      await chrome.storage.local.clear();
      this.logger?.info('All storage cleared');
    } catch (error) {
      this.logger?.error('Failed to clear storage', { error: error.message });
      throw error;
    }
  }

  /**
   * Get storage usage statistics
   * @returns {Promise<Object>} Storage stats
   */
  async getStorageStats() {
    try {
      const data = await chrome.storage.local.get(null);
      const keys = Object.keys(data);
      const sizes = {};
      
      keys.forEach(key => {
        const size = JSON.stringify(data[key]).length;
        sizes[key] = size;
      });

      const totalSize = Object.values(sizes).reduce((a, b) => a + b, 0);

      return {
        keys: keys.length,
        totalBytes: totalSize,
        byKey: sizes
      };
    } catch (error) {
      this.logger?.error('Failed to get storage stats', { error: error.message });
      return { keys: 0, totalBytes: 0, byKey: {} };
    }
  }
}
