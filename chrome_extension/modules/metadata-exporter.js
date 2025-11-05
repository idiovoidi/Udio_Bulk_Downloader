// Metadata exporter with incremental update support
export class MetadataExporter {
  constructor(logger, storage) {
    this.logger = logger;
    this.storage = storage;
  }

  /**
   * Prepare folder structure for export with stable IDs only
   * @param {Object} structure - Folder structure from FolderMapper
   * @returns {Promise<Object>} Export data with incremental update info
   */
  async prepareForExport(structure) {
    this.logger?.info('Preparing metadata for export');

    // Load seen cache for incremental detection
    const seenCache = await this.storage.getSeenCache();
    
    // Flatten folder tree
    const folders = this._flattenFolders(structure.folders);
    
    // Extract all songs with incremental detection
    const songs = this._extractAllSongs(structure, seenCache);
    
    // Extract tag relationships
    const tags = this._extractAllTags(songs);
    
    // Update seen cache with current state
    const newCache = {};
    songs.forEach(song => {
      newCache[song.id] = {
        hash: song.metadataHash,
        lastSeen: song.metadataCollectedAt
      };
    });
    await this.storage.updateSeenCache(newCache);
    
    // Calculate statistics
    const stats = {
      totalFolders: folders.length,
      totalSongs: songs.length,
      newSongs: songs.filter(s => s.isNew).length,
      changedSongs: songs.filter(s => s.isChanged).length,
      unchangedSongs: songs.filter(s => !s.isNew && !s.isChanged).length
    };

    this.logger?.success('Export prepared', stats);

    return {
      exportVersion: '2.0',
      exportDate: new Date().toISOString(),
      statistics: stats,
      folders,
      songs: songs.map(s => this._sanitizeSongForExport(s)),
      tags
    };
  }

  /**
   * Flatten folder tree into array with stable IDs
   * @param {Array} folders - Nested folder array
   * @param {string|null} parentId - Parent folder ID
   * @param {Array} parentPath - Parent path array
   * @returns {Array} Flattened folder array
   */
  _flattenFolders(folders, parentId = null, parentPath = []) {
    const flattened = [];

    folders.forEach(folder => {
      const currentPath = [...parentPath, folder.name];
      const folderId = this._generateFolderId(currentPath);

      const flatFolder = {
        id: folderId,
        name: folder.name,
        parentId: parentId,
        path: currentPath,
        songCount: folder.songCount || 0,
        hasChildren: (folder.subfolders && folder.subfolders.length > 0)
      };

      flattened.push(flatFolder);

      // Recursively flatten subfolders
      if (folder.subfolders && folder.subfolders.length > 0) {
        const subfolders = this._flattenFolders(
          folder.subfolders,
          folderId,
          currentPath
        );
        flattened.push(...subfolders);
      }
    });

    return flattened;
  }

  /**
   * Generate stable folder ID from path
   * @param {Array} path - Folder path array
   * @returns {string} Stable folder ID
   */
  _generateFolderId(path) {
    const pathString = path.join('/');
    return this._simpleHash(pathString);
  }

  /**
   * Extract all songs from structure with incremental detection
   * @param {Object} structure - Folder structure
   * @param {Object} seenCache - Previously seen songs cache
   * @returns {Array} Array of songs with incremental flags
   */
  _extractAllSongs(structure, seenCache) {
    const songs = [];

    // Extract root songs
    if (structure.rootSongs && structure.rootSongs.length > 0) {
      structure.rootSongs.forEach(song => {
        const enrichedSong = this._enrichSongWithIncrementalInfo(
          song,
          null,
          seenCache
        );
        songs.push(enrichedSong);
      });
    }

    // Extract songs from folders recursively
    const extractFromFolders = (folders, parentPath = []) => {
      folders.forEach(folder => {
        const currentPath = [...parentPath, folder.name];
        const folderId = this._generateFolderId(currentPath);

        if (folder.songs && folder.songs.length > 0) {
          folder.songs.forEach(song => {
            const enrichedSong = this._enrichSongWithIncrementalInfo(
              song,
              folderId,
              seenCache
            );
            songs.push(enrichedSong);
          });
        }

        if (folder.subfolders && folder.subfolders.length > 0) {
          extractFromFolders(folder.subfolders, currentPath);
        }
      });
    };

    if (structure.folders && structure.folders.length > 0) {
      extractFromFolders(structure.folders);
    }

    return songs;
  }

  /**
   * Enrich song with incremental update information
   * @param {Object} song - Song object
   * @param {string|null} folderId - Folder ID
   * @param {Object} seenCache - Seen songs cache
   * @returns {Object} Enriched song object
   */
  _enrichSongWithIncrementalInfo(song, folderId, seenCache) {
    const cached = seenCache[song.id];
    
    return {
      ...song,
      folderId: folderId,
      isNew: !cached,
      isChanged: cached && cached.hash !== song.metadataHash
    };
  }

  /**
   * Sanitize song for export (remove transient data, keep stable IDs only)
   * @param {Object} song - Song object
   * @returns {Object} Sanitized song object
   */
  _sanitizeSongForExport(song) {
    return {
      // Stable ID (primary key)
      id: song.id,
      
      // Core metadata
      title: song.title,
      artist: song.artist,
      duration: song.duration,
      createdDate: song.createdDate,
      
      // Folder reference
      folderId: song.folderId,
      
      // User interaction data
      isLiked: song.isLiked,
      isDisliked: song.isDisliked,
      playCount: song.plays,
      likesCount: song.likes,
      
      // Content flags
      lyricsAvailable: song.lyricsAvailable,
      
      // Metadata tracking
      metadataHash: song.metadataHash,
      metadataCollectedAt: song.metadataCollectedAt,
      
      // Incremental update flags
      isNew: song.isNew,
      isChanged: song.isChanged
      
      // NOTE: Transient URLs (song URL, image URL) are NOT exported
      // They will be resolved at download time via Playwright
    };
  }

  /**
   * Extract all tag relationships
   * @param {Array} songs - Array of songs
   * @returns {Array} Array of tag relationships
   */
  _extractAllTags(songs) {
    const tags = [];

    songs.forEach(song => {
      if (song.tags && song.tags.length > 0) {
        song.tags.forEach(tag => {
          tags.push({
            songId: song.id,
            tag: tag
          });
        });
      }
    });

    return tags;
  }

  /**
   * Export to JSON file via chrome.downloads API
   * Requires user gesture context
   * @param {Object} data - Export data
   * @returns {Promise<void>}
   */
  async exportToFile(data) {
    try {
      const blob = new Blob([JSON.stringify(data, null, 2)], { 
        type: 'application/json' 
      });
      const url = URL.createObjectURL(blob);
      
      const timestamp = new Date().toISOString().split('T')[0];
      const filename = `udio_metadata_${timestamp}.json`;

      this.logger?.info('Starting export download', { filename });

      // Use chrome.downloads API (requires user gesture)
      chrome.downloads.download({
        url: url,
        filename: filename,
        saveAs: true
      }, (downloadId) => {
        if (chrome.runtime.lastError) {
          this.logger?.error('Export failed', { 
            error: chrome.runtime.lastError.message 
          });
        } else {
          this.logger?.success('Export started', { 
            downloadId, 
            filename 
          });
        }
        
        // Clean up blob URL after download starts
        setTimeout(() => URL.revokeObjectURL(url), 1000);
      });

    } catch (error) {
      this.logger?.error('Export error', { error: error.message });
      throw error;
    }
  }

  /**
   * Simple hash function for generating stable IDs
   * @param {string} str - String to hash
   * @returns {string} Hash string
   */
  _simpleHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return Math.abs(hash).toString(36);
  }
}
