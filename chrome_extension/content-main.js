// Main content script - integrates all modules (MV3 compliant)
import { FolderMapper } from './modules/folder-mapper.js';
import { SongExtractor } from './modules/song-extractor.js';
import { MetadataExporter } from './modules/metadata-exporter.js';
import { StorageManager } from './modules/storage-manager.js';

console.log('Udio Library Mapper: Main content script loaded');

// Initialize modules
const storage = new StorageManager(logger);
const folderMapper = new FolderMapper(logger, storage);
const metadataExporter = new MetadataExporter(logger, storage);

// Listen for messages from popup and service worker
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Content script received message:', request.action);
  
  if (request.action === 'ping') {
    // Health check
    sendResponse({ status: 'ready' });
    
  } else if (request.action === 'startMapping') {
    // Start folder mapping
    handleStartMapping(sendResponse);
    return true; // Async response
    
  } else if (request.action === 'getProgress') {
    // Get current mapping progress
    const progress = folderMapper.getProgress();
    sendResponse(progress);
    
  } else if (request.action === 'exportMetadata') {
    // Export metadata with incremental update support
    handleExportMetadata(request.structure, sendResponse);
    return true; // Async response
    
  } else if (request.action === 'dumpStructure') {
    // Debug: dump tree structure
    dumpTreeStructure();
    sendResponse({ status: 'dumped' });
  }
  
  return false;
});

/**
 * Handle start mapping request
 */
async function handleStartMapping(sendResponse) {
  try {
    logger.info('Starting mapping from content script');
    
    // Start mapping (with resume capability)
    const structure = await folderMapper.startMapping(true);
    
    sendResponse({ 
      status: 'completed',
      structure: structure
    });
    
  } catch (error) {
    logger.error('Mapping failed', { error: error.message });
    sendResponse({ 
      status: 'error',
      error: error.message
    });
  }
}

/**
 * Handle export metadata request
 */
async function handleExportMetadata(structure, sendResponse) {
  try {
    logger.info('Exporting metadata');
    
    // Prepare export data with incremental update detection
    const exportData = await metadataExporter.prepareForExport(structure);
    
    // Trigger download (requires user gesture from popup)
    await metadataExporter.exportToFile(exportData);
    
    sendResponse({
      status: 'success',
      stats: exportData.statistics
    });
    
  } catch (error) {
    logger.error('Export failed', { error: error.message });
    sendResponse({
      status: 'error',
      error: error.message
    });
  }
}

/**
 * Debug function to dump tree structure
 */
async function dumpTreeStructure() {
  console.log('\n========== TREE STRUCTURE DIAGNOSTIC ==========\n');
  
  const treeContainer = document.querySelector('[role="tree"][aria-label="Folder structure"]');
  
  if (!treeContainer) {
    console.error('❌ Folder tree panel not found!');
    logger.error('Folder tree panel not found');
    return;
  }
  
  console.log('✓ Found folder tree panel');
  console.log(`Total direct children: ${treeContainer.children.length}\n`);
  
  logger.info('Tree structure dumped to console', {
    children: treeContainer.children.length
  });
  
  // Log first few items
  Array.from(treeContainer.children).slice(0, 3).forEach((item, index) => {
    const nameButton = item.querySelector('button[title]');
    const name = nameButton?.getAttribute('title') || 'unnamed';
    console.log(`${index + 1}. ${name}`);
  });
  
  console.log('\n========== END DIAGNOSTIC ==========\n');
}

// Log when script loads
logger.info('Content script initialized', { 
  url: window.location.href,
  modules: ['FolderMapper', 'MetadataExporter', 'StorageManager']
});

console.log('Udio Library Mapper ready. Modules loaded:', {
  folderMapper: !!folderMapper,
  metadataExporter: !!metadataExporter,
  storage: !!storage
});
