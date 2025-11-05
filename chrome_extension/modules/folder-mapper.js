// Folder tree mapping logic (MV3 compliant - runs in content script)
import { DOMUtils } from './dom-utils.js';
import { SongExtractor } from './song-extractor.js';

export class FolderMapper {
  constructor(logger, storage) {
    this.logger = logger;
    this.storage = storage;
    this.songExtractor = new SongExtractor(logger, storage);
    this.inProgress = false;
    this.structure = this._createEmptyStructure();
    this.folderCache = new Map(); // Cache processed folders
    this.processedFolderPaths = new Set(); // Track processed paths for deduplication
  }

  _createEmptyStructure() {
    return {
      folders: [],
      rootSongs: [],
      totalFolders: 0,
      mappedFolders: 0,
      totalSongs: 0,
      scanStartTime: null,
      scanEndTime: null
    };
  }

  /**
   * Start mapping with resume capability (idempotent)
   * @param {boolean} resume - Whether to resume from saved state
   */
  async startMapping(resume = true) {
    if (this.inProgress) {
      this.logger?.warning('Mapping already in progress');
      return;
    }

    this.inProgress = true;
    
    // Try to resume from saved state
    let resumedState = null;
    if (resume) {
      resumedState = await this.storage.loadContentState();
      if (resumedState && resumedState.inProgress) {
        this.structure = resumedState.structure;
        this.logger?.info('Resuming from saved state', {
          mappedFolders: this.structure.mappedFolders,
          totalFolders: this.structure.totalFolders
        });
      }
    }

    // Initialize new scan if not resuming
    if (!resumedState) {
      this.structure = this._createEmptyStructure();
      this.structure.scanStartTime = Date.now();
    }
    
    this.logger?.info('Starting folder tree mapping');

    try {
      const treeContainer = await this._findTreeContainer();
      const topLevelItems = Array.from(treeContainer.children);
      
      // Update total if not resuming
      if (!resumedState) {
        this.structure.totalFolders = topLevelItems.length;
      }

      this.logger?.info(`Found ${topLevelItems.length} top-level folders`);

      // Extract root-level songs (skip if already done)
      if (!resumedState || this.structure.rootSongs.length === 0) {
        await this._extractRootSongs();
      }

      // Process each top-level folder (resume from where we left off)
      const startIndex = resumedState ? this.structure.mappedFolders : 0;
      
      for (let i = startIndex; i < topLevelItems.length; i++) {
        const item = topLevelItems[i];
        this.logger?.info(`Processing folder ${i + 1}/${topLevelItems.length}`);

        const folderData = await this._processFolderItem(item, [], treeContainer);
        
        if (folderData) {
          this.logger?.success(`Processed: ${folderData.name}`, {
            songs: folderData.songs?.length || 0,
            subfolders: folderData.subfolders?.length || 0
          });
          
          // Check for duplicates before adding
          const pathKey = folderData.path.join('/');
          if (!this.processedFolderPaths.has(pathKey)) {
            this.structure.folders.push(folderData);
            this.processedFolderPaths.add(pathKey);
          } else {
            this.logger?.warning(`Skipping duplicate folder: ${pathKey}`);
          }
        }

        this.structure.mappedFolders = i + 1;
        
        // Save state periodically for resume capability
        await this.storage.saveContentState({
          inProgress: this.inProgress,
          structure: this.structure
        });

        this._sendProgressUpdate();
        
        // Yield to browser to prevent blocking
        await DOMUtils.sleep(10);
      }

      this.structure.scanEndTime = Date.now();
      const duration = (this.structure.scanEndTime - this.structure.scanStartTime) / 1000;

      this.logger?.success('Mapping complete!', {
        totalFolders: this.structure.totalFolders,
        totalSongs: this.structure.totalSongs,
        durationSeconds: duration.toFixed(1)
      });

      this._sendCompletionMessage();
      return this.structure;

    } catch (error) {
      this.logger?.error('Mapping failed', { error: error.message });
      this._sendErrorMessage(error.message);
      
      // Save state even on error for resume
      await this.storage.saveContentState({
        inProgress: false,
        structure: this.structure,
        error: error.message
      });
      
      throw error;
    } finally {
      this.inProgress = false;
      await this.storage.clearContentState();
    }
  }

  async _findTreeContainer() {
    const container = document.querySelector('[role="tree"][aria-label="Folder structure"]');
    if (!container) {
      throw new Error('Folder tree panel not found. Please open the folder tree.');
    }
    return container;
  }

  async _extractRootSongs() {
    this.logger?.info('Checking for root-level songs');
    const rootSongs = await this.songExtractor.extractSongsFromView(null);
    
    if (rootSongs.length > 0) {
      this.logger?.success(`Found ${rootSongs.length} root songs`);
      this.structure.rootSongs = rootSongs;
      this.structure.totalSongs += rootSongs.length;
    }
  }

  async _processFolderItem(item, parentPath) {
    const nameButton = item.querySelector('button[title]');
    if (!nameButton) return null;

    const folderName = nameButton.getAttribute('title');
    const currentPath = [...parentPath, folderName];
    const cacheKey = currentPath.join('/');

    // Check cache first
    if (this.folderCache.has(cacheKey)) {
      this.logger?.info(`Using cached folder: ${cacheKey}`);
      return this.folderCache.get(cacheKey);
    }

    const expandButton = item.querySelector('button[aria-label="Expand"]');
    const hasChildren = expandButton !== null;
    const isExpanded = item.getAttribute('aria-expanded') === 'true';

    const folderData = {
      name: folderName,
      path: currentPath,
      hasChildren,
      isLeaf: !hasChildren,
      subfolders: [],
      songCount: 0
    };

    if (hasChildren) {
      await this._processParentFolder(item, expandButton, isExpanded, folderData, currentPath);
    } else {
      await this._processLeafFolder(nameButton, folderData, currentPath);
    }

    // Cache the result
    this.folderCache.set(cacheKey, folderData);

    return folderData;
  }

  async _processParentFolder(item, expandButton, isExpanded, folderData, currentPath) {
    if (!isExpanded) {
      expandButton.click();
      await DOMUtils.sleep(1200);
    }

    await DOMUtils.sleep(300);

    const nestedButtons = item.querySelectorAll('[role="button"]');
    const children = Array.from(nestedButtons).filter(btn => btn !== item);

    for (const child of children) {
      const childData = await this._processFolderItem(child, currentPath, item);
      if (childData) {
        folderData.subfolders.push(childData);
        folderData.songCount += childData.songCount;
      }
    }

    if (!isExpanded) {
      expandButton.click();
      await DOMUtils.sleep(200);
    }
  }

  async _processLeafFolder(nameButton, folderData, currentPath) {
    nameButton.click();
    await DOMUtils.sleep(2500);

    const songs = await this.songExtractor.extractSongsFromView(currentPath);
    songs.forEach(song => song.folderPath = currentPath);

    folderData.songs = songs;
    folderData.songCount = songs.length;
    this.structure.totalSongs += songs.length;
  }

  clearCache() {
    this.folderCache.clear();
    this.songExtractor.clearCache();
    this.logger?.info('All caches cleared');
  }

  getCacheStats() {
    return {
      folders: this.folderCache.size,
      songs: this.songExtractor.getCacheSize()
    };
  }

  _sendProgressUpdate() {
    chrome.runtime.sendMessage({
      action: 'progressUpdate',
      progress: {
        ...this.structure,
        percentComplete: Math.round((this.structure.mappedFolders / this.structure.totalFolders) * 100)
      }
    });
  }

  _sendCompletionMessage() {
    chrome.runtime.sendMessage({
      action: 'mappingComplete',
      structure: this.structure
    });
  }

  _sendErrorMessage(error) {
    chrome.runtime.sendMessage({
      action: 'mappingError',
      error
    });
  }

  getProgress() {
    return {
      inProgress: this.inProgress,
      structure: this.structure
    };
  }
}
