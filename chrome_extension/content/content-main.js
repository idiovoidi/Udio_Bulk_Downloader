// Main content script entry point
import { FolderMapper } from '../modules/folder-mapper.js';
import { StorageManager } from '../modules/storage.js';
import { MessageHandler } from './message-handler.js';
import { Diagnostics } from './diagnostics.js';

console.log('Udio Folder Mapper v4 (modular) loaded');

// Initialize logger (global from logger.js)
if (typeof logger !== 'undefined') {
  logger.info('Content script v4 loaded', { url: window.location.href });
}

// Initialize modules
const storage = new StorageManager();
const folderMapper = new FolderMapper(typeof logger !== 'undefined' ? logger : null, storage);
const diagnostics = new Diagnostics(typeof logger !== 'undefined' ? logger : null);
const messageHandler = new MessageHandler(folderMapper, diagnostics);

// Load state on initialization
(async () => {
  const state = await storage.loadContentState();
  if (state?.inProgress) {
    folderMapper.inProgress = state.inProgress;
    folderMapper.structure = state.structure;
    if (typeof logger !== 'undefined') {
      logger.info('Restored mapping state', {
        mappedFolders: state.structure.mappedFolders,
        totalFolders: state.structure.totalFolders
      });
    }
  }
})();

// Log when page loads
window.addEventListener('load', () => {
  console.log('Udio Library Mapper: Page loaded, ready to analyze');
  
  const pageType = window.location.href.includes('/library') ? 'library' : 'other';
  console.log('Detected page type:', pageType);
  
  if (pageType === 'library') {
    console.log('Library page detected - extension ready to map structure');
  }
});

console.log('Folder mapper ready. Waiting for mapping command...');
