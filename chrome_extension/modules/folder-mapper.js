// Folder tree mapping logic
import { DOMUtils } from './dom-utils.js';
import { SongExtractor } from './song-extractor.js';

export class FolderMapper {
  constructor(logger, storage) {
    this.logger = logger;
    this.storage = storage;
    this.songExtractor = new SongExtractor(logger);
    this.inProgress = false;
    this.structure = this._createEmptyStructure();
  }

  _createEmptyStructure() {
    return {
      folders: [],
      rootSongs: [],
      totalFolders: 0,
      mappedFolders: 0,
      totalSongs: 0
    };
  }

  async startMapping() {
    if (this.inProgress) {
      this.logger?.warning('Mapping already in progress');
      return;
    }

    this.inProgress = true;
    this.structure = this._createEmptyStructure();
    
    this.logger?.info('Starting folder tree mapping');

    try {
      const treeContainer = await this._findTreeContainer();
      const topLevelItems = Array.from(treeContainer.children);
      this.structure.totalFolders = topLevelItems.length;

      this.logger?.info(`Found ${topLevelItems.length} top-level folders`);

      // Extract root-level songs
      await this._extractRootSongs();

      // Process each top-level folder
      for (let i = 0; i < topLevelItems.length; i++) {
        const item = topLevelItems[i];
        this.logger?.info(`Processing folder ${i + 1}/${topLevelItems.length}`);

        const folderData = await this._processFolderItem(item, [], treeContainer);
        
        if (folderData) {
          this.logger?.success(`Processed: ${folderData.name}`, {
            songs: folderData.songs?.length || 0,
            subfolders: folderData.subfolders?.length || 0
          });
          this.structure.folders.push(folderData);
        }

        this.structure.mappedFolders = i + 1;
        await this.storage.saveContentState({
          inProgress: this.inProgress,
          structure: this.structure
        });

        this._sendProgressUpdate();
      }

      this.logger?.success('Mapping complete!', {
        totalFolders: this.structure.totalFolders,
        totalSongs: this.structure.totalSongs
      });

      this._sendCompletionMessage();
      return this.structure;

    } catch (error) {
      this.logger?.error('Mapping failed', { error: error.message });
      this._sendErrorMessage(error.message);
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
    const rootSongs = await this.songExtractor.extractSongsFromView();
    
    if (rootSongs.length > 0) {
      this.logger?.success(`Found ${rootSongs.length} root songs`);
      this.structure.rootSongs = rootSongs;
      this.structure.totalSongs += rootSongs.length;
    }
  }

  async _processFolderItem(item, parentPath, treeContainer) {
    const nameButton = item.querySelector('button[title]');
    if (!nameButton) return null;

    const folderName = nameButton.getAttribute('title');
    const currentPath = [...parentPath, folderName];

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

    const songs = await this.songExtractor.extractSongsFromView();
    songs.forEach(song => song.folderPath = currentPath);

    folderData.songs = songs;
    folderData.songCount = songs.length;
    this.structure.totalSongs += songs.length;
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
