// content.js - Folder tree panel mapping (updated for actual structure)
console.log('Udio Folder Mapper loaded');

// Initialize logger
logger.info('Content script loaded', { url: window.location.href });

let mappingInProgress = false;
let currentStructure = {
  folders: [],
  rootSongs: [],
  totalFolders: 0,
  mappedFolders: 0,
  totalSongs: 0
};

// Load state from storage on page load
async function loadMappingState() {
  try {
    const result = await chrome.storage.local.get(['contentMappingState']);
    if (result.contentMappingState) {
      mappingInProgress = result.contentMappingState.inProgress || false;
      currentStructure = result.contentMappingState.structure || currentStructure;
      logger.info('Restored mapping state from storage', { 
        inProgress: mappingInProgress,
        mappedFolders: currentStructure.mappedFolders,
        totalFolders: currentStructure.totalFolders
      });
    }
  } catch (error) {
    logger.error('Failed to load mapping state', { error: error.message });
  }
}

// Save state to storage
async function saveMappingState() {
  try {
    await chrome.storage.local.set({
      contentMappingState: {
        inProgress: mappingInProgress,
        structure: currentStructure,
        timestamp: Date.now()
      }
    });
  } catch (error) {
    logger.error('Failed to save mapping state', { error: error.message });
  }
}

// Clear state from storage
async function clearMappingState() {
  try {
    await chrome.storage.local.remove('contentMappingState');
  } catch (error) {
    logger.error('Failed to clear mapping state', { error: error.message });
  }
}

// Load state on initialization
loadMappingState();

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Message received:', request.action);
  
  if (request.action === 'ping') {
    // Simple ping to check if content script is loaded
    sendResponse({ status: 'ready' });
  } else if (request.action === 'dumpStructure') {
    // Diagnostic: dump the tree structure
    dumpTreeStructure();
    sendResponse({ status: 'dumped' });
  } else if (request.action === 'startMapping') {
    startFolderTreeMapping();
    sendResponse({ status: 'started' });
  } else if (request.action === 'getProgress') {
    sendResponse({
      inProgress: mappingInProgress,
      structure: currentStructure
    });
  } else if (request.action === 'exportMetadata') {
    // Export metadata with incremental update support
    exportMetadataWithIncrementalSupport(request.structure).then(result => {
      sendResponse(result);
    });
    return true; // Async response
  } else if (request.action === 'downloadSong') {
    // Download a single song
    downloadSong(request.song);
    sendResponse({ status: 'downloading' });
  }
  
  return true;
});

async function startFolderTreeMapping() {
  if (mappingInProgress) {
    logger.warning('Mapping already in progress');
    console.log('Mapping already in progress');
    return;
  }
  
  mappingInProgress = true;
  currentStructure = {
    folders: [],
    rootSongs: [],
    totalFolders: 0,
    mappedFolders: 0,
    totalSongs: 0
  };
  
  logger.info('Starting folder tree mapping');
  console.log('Starting folder tree mapping...');
  
  try {
    // Find the folder tree panel
    const treeContainer = document.querySelector('[role="tree"][aria-label="Folder structure"]');
    
    if (!treeContainer) {
      const error = 'Folder tree panel not found. Please open the folder tree by clicking the folder icon in the top right.';
      logger.error(error);
      throw new Error(error);
    }
    
    logger.success('Found folder tree panel');
    console.log('Found folder tree panel');
    console.log('Tree container HTML sample:', treeContainer.innerHTML.substring(0, 500));
    
    // Get all direct children (top-level folder items)
    const topLevelItems = Array.from(treeContainer.children);
    currentStructure.totalFolders = topLevelItems.length;
    
    logger.info(`Found ${topLevelItems.length} top-level folders`);
    console.log(`Found ${topLevelItems.length} top-level folders`);
    console.log('First item HTML:', topLevelItems[0]?.outerHTML.substring(0, 300));
    
    // First, check for root-level songs (songs not in any folder)
    logger.info('Checking for root-level songs');
    console.log('\n=== Checking for root-level songs ===');
    
    // Click on "My Songs" or root view to see if there are songs not in folders
    const rootSongs = await extractSongsFromView();
    if (rootSongs.length > 0) {
      logger.success(`Found ${rootSongs.length} songs in root directory`, { count: rootSongs.length });
      console.log(`Found ${rootSongs.length} songs in root directory`);
      currentStructure.rootSongs = rootSongs;
      currentStructure.totalSongs += rootSongs.length;
    }
    
    // Process each top-level folder
    for (let i = 0; i < topLevelItems.length; i++) {
      const item = topLevelItems[i];
      logger.info(`Processing top-level folder ${i + 1}/${topLevelItems.length}`);
      console.log(`\n=== Processing top-level folder ${i + 1}/${topLevelItems.length} ===`);
      
      const folderData = await processFolderItem(item, [], treeContainer);
      
      if (folderData) {
        logger.success(`Successfully processed: ${folderData.name}`, { 
          name: folderData.name, 
          songs: folderData.songs?.length || 0,
          subfolders: folderData.subfolders?.length || 0
        });
        console.log(`✓ Successfully processed: ${folderData.name}`);
        currentStructure.folders.push(folderData);
      } else {
        logger.error(`Failed to process folder at index ${i}`);
        console.warn(`✗ Failed to process folder at index ${i}`);
      }
      
      currentStructure.mappedFolders = i + 1;
      
      // Save state after each folder
      await saveMappingState();
      
      // Send progress update
      chrome.runtime.sendMessage({
        action: 'progressUpdate',
        progress: {
          ...currentStructure,
          percentComplete: Math.round((i + 1) / topLevelItems.length * 100)
        }
      });
    }
    
    logger.success('Mapping complete!', {
      totalFolders: currentStructure.totalFolders,
      totalSongs: currentStructure.totalSongs,
      rootSongs: currentStructure.rootSongs.length
    });
    console.log('Mapping complete!', currentStructure);
    console.log('Full structure:', JSON.stringify(currentStructure, null, 2));
    
    // Send completion message
    chrome.runtime.sendMessage({
      action: 'mappingComplete',
      structure: currentStructure
    });
    
  } catch (error) {
    logger.error('Mapping failed', { error: error.message, stack: error.stack });
    console.error('Mapping failed:', error);
    
    // Save state even on error so we don't lose progress
    await saveMappingState();
    
    chrome.runtime.sendMessage({
      action: 'mappingError',
      error: error.message
    });
  } finally {
    mappingInProgress = false;
    // Clear state when done (success or failure)
    await clearMappingState();
  }
}

async function processFolderItem(item, parentPath, treeContainer) {
  // Get folder name from the button with title attribute
  const nameButton = item.querySelector('button[title]');
  if (!nameButton) {
    console.log('No name button found, skipping item');
    return null;
  }
  
  const folderName = nameButton.getAttribute('title');
  const currentPath = [...parentPath, folderName];
  
  console.log(`Processing: ${currentPath.join(' > ')}`);
  
  // Check if this folder has children (has expand button with chevron)
  const expandButton = item.querySelector('button[aria-label="Expand"]');
  const hasExpandButton = expandButton !== null;
  const isExpanded = item.getAttribute('aria-expanded') === 'true';
  
  console.log(`Folder: ${folderName}, hasExpandButton: ${hasExpandButton}, isExpanded: ${isExpanded}`);
  
  const folderData = {
    name: folderName,
    path: currentPath,
    hasChildren: hasExpandButton,
    isLeaf: !hasExpandButton,
    subfolders: [],
    songCount: 0
  };
  
  // If it has an expand button, it has children
  if (hasExpandButton) {
    // Expand if not already expanded
    if (!isExpanded) {
      console.log(`Expanding folder: ${folderName}`);
      expandButton.click();
      
      // Wait for expansion animation and DOM update
      await sleep(1200);
      
      // Verify it actually expanded
      const expandedCheck = item.getAttribute('aria-expanded');
      console.log(`After click, aria-expanded: ${expandedCheck}`);
      
      if (expandedCheck !== 'true') {
        console.warn(`Folder didn't expand properly, waiting longer...`);
        await sleep(800);
      }
    }
    
    // Extra wait to ensure children are rendered
    await sleep(300);
    
    // Children are NESTED inside the parent item, not as siblings!
    // Look for all [role="button"] elements inside this item
    const nestedButtons = item.querySelectorAll('[role="button"]');
    
    console.log(`Found ${nestedButtons.length} nested buttons (including parent)`);
    
    // Filter out the parent itself - children are the rest
    const children = Array.from(nestedButtons).filter(btn => btn !== item);
    
    console.log(`Found ${children.length} direct children for ${folderName}`);
    
    // Process each child recursively
    for (const child of children) {
      const childData = await processFolderItem(child, currentPath, item);
      if (childData) {
        folderData.subfolders.push(childData);
        folderData.songCount += childData.songCount;
      }
    }
    
    // Collapse the folder after processing to keep UI clean
    if (!isExpanded) {
      console.log(`Collapsing folder: ${folderName}`);
      expandButton.click();
      await sleep(200);
    }
  } else {
    // Leaf folder - click to view songs
    console.log(`Leaf folder: ${folderName}, clicking to view songs`);
    nameButton.click();
    await sleep(2500); // Wait for songs to load (increased delay)
    
    // Extract song information
    const songs = await extractSongsFromView();
    folderData.songs = songs;
    folderData.songCount = songs.length;
    currentStructure.totalSongs += songs.length;
    
    console.log(`Found ${songs.length} songs in ${folderName}`);
    
    // Add folder path to each song for later download
    songs.forEach(song => {
      song.folderPath = currentPath;
    });
  }
  
  return folderData;
}

async function extractSongsFromView() {
  // Wait for content to load
  await sleep(1500); // Increased delay to ensure songs are fully loaded
  
  const songs = [];
  const seenUrls = new Set(); // Track unique songs
  
  // Find the scrollable container (usually the main content area)
  const scrollContainer = document.querySelector('main') || 
                         document.querySelector('[role="main"]') || 
                         document.querySelector('.overflow-auto') ||
                         document.documentElement;
  
  console.log('Starting scroll-based song extraction...');
  
  let previousSongCount = 0;
  let noNewSongsCount = 0;
  const maxScrollAttempts = 50; // Prevent infinite loops
  let scrollAttempts = 0;
  
  // Scroll and extract songs until no more new songs are found
  while (scrollAttempts < maxScrollAttempts) {
    // Extract currently visible songs
    const songRows = document.querySelectorAll('tr[class*="absolute"]');
    
    if (songRows.length === 0) {
      // Fallback: look for any links to /songs/
      const songLinks = document.querySelectorAll('a[href*="/songs/"]');
      
      songLinks.forEach((link) => {
        if (!seenUrls.has(link.href)) {
          const container = link.closest('tr, div[class*="group"]');
          if (container) {
            const song = extractSongFromElement(container);
            if (song && song.url) {
              seenUrls.add(song.url);
              songs.push(song);
            }
          }
        }
      });
    } else {
      // Extract from table rows
      songRows.forEach((row) => {
        const song = extractSongFromElement(row);
        if (song && song.url && !seenUrls.has(song.url)) {
          seenUrls.add(song.url);
          songs.push(song);
        }
      });
    }
    
    const currentSongCount = songs.length;
    console.log(`Scroll attempt ${scrollAttempts + 1}: Found ${currentSongCount} songs (${currentSongCount - previousSongCount} new)`);
    
    // Check if we found new songs
    if (currentSongCount === previousSongCount) {
      noNewSongsCount++;
      // If no new songs found after 3 scroll attempts, we're done
      if (noNewSongsCount >= 3) {
        console.log('No new songs found after 3 scroll attempts, extraction complete');
        break;
      }
    } else {
      noNewSongsCount = 0; // Reset counter if we found new songs
    }
    
    previousSongCount = currentSongCount;
    
    // Scroll down to load more content
    scrollContainer.scrollBy(0, 1000);
    
    // Wait for new content to load
    await sleep(800);
    
    scrollAttempts++;
  }
  
  if (scrollAttempts >= maxScrollAttempts) {
    console.warn('Reached maximum scroll attempts, some songs may be missing');
  }
  
  // Scroll back to top
  scrollContainer.scrollTo(0, 0);
  
  console.log(`Extracted ${songs.length} total songs with metadata`);
  return songs;
}

function extractSongFromElement(element) {
  try {
    const song = {
      title: null,
      url: null,
      id: null,
      artist: null,
      duration: null,
      createdDate: null,
      imageUrl: null,
      lyricsAvailable: false,
      tags: [],
      plays: null,
      likes: null,
      isLiked: false,
      isDisliked: false,
      metadataCollectedAt: new Date().toISOString(),
      metadataHash: null
    };
    
    // Find title (in h4 tag)
    const titleElement = element.querySelector('h4');
    if (titleElement) {
      song.title = titleElement.textContent.trim();
    }
    
    // Find song URL and ID
    const linkElement = element.querySelector('a[href*="/songs/"]');
    if (linkElement) {
      song.url = linkElement.href;
      const match = song.url.match(/\/songs\/([^/?]+)/);
      if (match) {
        song.id = match[1];
      }
    }
    
    // Find image
    const imgElement = element.querySelector('img[alt]');
    if (imgElement) {
      song.imageUrl = imgElement.src;
    }
    
    // Find duration (looks like "2:10")
    const textNodes = element.querySelectorAll('.text-muted-foreground');
    textNodes.forEach(node => {
      const text = node.textContent.trim();
      if (/^\d+:\d+$/.test(text)) {
        song.duration = text;
      }
    });
    
    // Find tags
    const tagLinks = element.querySelectorAll('a[href*="/tags/"]');
    tagLinks.forEach(tag => {
      song.tags.push(tag.textContent.trim());
    });
    
    // Find artist (look for user links or artist text)
    const artistLink = element.querySelector('a[href*="/users/"]');
    if (artistLink) {
      song.artist = artistLink.textContent.trim();
    }
    
    // Check for lyrics availability
    const lyricsIcon = element.querySelector('svg.lucide-file-text');
    song.lyricsAvailable = lyricsIcon !== null;
    
    // Find play count and likes
    const svgIcons = element.querySelectorAll('svg.lucide-play, svg.lucide-thumbs-up');
    svgIcons.forEach(svg => {
      const nextText = svg.nextSibling;
      if (nextText && nextText.textContent) {
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
    
    // Generate metadata hash
    song.metadataHash = generateMetadataHash(song);
    
    // Check if song is liked (thumbs-up button is filled/active)
    // Look for the thumbs-up button and check if it's in a liked state
    const likeButton = element.querySelector('button:has(svg.lucide-thumbs-up)');
    if (likeButton) {
      // Check for filled state - liked songs have fill="white" or fill="currentColor"
      const thumbsUpSvg = likeButton.querySelector('svg.lucide-thumbs-up');
      if (thumbsUpSvg) {
        const fillAttr = thumbsUpSvg.getAttribute('fill');
        const strokeAttr = thumbsUpSvg.getAttribute('stroke');
        
        // Liked state: fill="white" or stroke="white", or aria-label="unlike"
        const hasFill = fillAttr === 'white' || fillAttr === 'currentColor' || strokeAttr === 'white';
        const isUnlikeButton = likeButton.getAttribute('aria-label') === 'unlike' || 
                               likeButton.getAttribute('title')?.toLowerCase().includes('remove like');
        
        song.isLiked = hasFill || isUnlikeButton;
      }
    }
    
    // Check if song is disliked (thumbs-down button is filled/active)
    const dislikeButton = element.querySelector('button:has(svg.lucide-thumbs-down)');
    if (dislikeButton) {
      const thumbsDownSvg = dislikeButton.querySelector('svg.lucide-thumbs-down');
      if (thumbsDownSvg) {
        const fillAttr = thumbsDownSvg.getAttribute('fill');
        const strokeAttr = thumbsDownSvg.getAttribute('stroke');
        
        // Disliked state: fill="white" or stroke="white", or aria-label="undislike"
        const hasFill = fillAttr === 'white' || fillAttr === 'currentColor' || strokeAttr === 'white';
        const isUndislikeButton = dislikeButton.getAttribute('aria-label') === 'undislike' || 
                                  dislikeButton.getAttribute('title')?.toLowerCase().includes('remove dislike');
        
        song.isDisliked = hasFill || isUndislikeButton;
      }
    }
    
    // Only return if we have at least title and URL
    if (song.title && song.url) {
      return song;
    }
    
    return null;
  } catch (error) {
    console.warn('Error extracting song:', error);
    return null;
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Diagnostic function to dump tree structure
async function dumpTreeStructure() {
  console.log('\n========== TREE STRUCTURE DIAGNOSTIC ==========\n');
  
  const treeContainer = document.querySelector('[role="tree"][aria-label="Folder structure"]');
  
  if (!treeContainer) {
    console.error('❌ Folder tree panel not found!');
    return;
  }
  
  console.log('✓ Found folder tree panel');
  console.log(`Total direct children: ${treeContainer.children.length}\n`);
  
  // Find first folder with expand button
  const expandableFolder = Array.from(treeContainer.children).find(item => {
    return item.querySelector('button[aria-label="Expand"]') !== null;
  });
  
  if (!expandableFolder) {
    console.log('No expandable folders found');
    return;
  }
  
  const folderName = expandableFolder.querySelector('button[title]')?.getAttribute('title');
  console.log(`Found expandable folder: "${folderName}"`);
  console.log(`Current aria-expanded: ${expandableFolder.getAttribute('aria-expanded')}`);
  
  const itemsBefore = treeContainer.children.length;
  console.log(`Items before expansion: ${itemsBefore}`);
  
  // Expand it
  const expandButton = expandableFolder.querySelector('button[aria-label="Expand"]');
  console.log('\nClicking expand button...');
  expandButton.click();
  
  await sleep(1500);
  
  const itemsAfter = treeContainer.children.length;
  console.log(`Items after expansion: ${itemsAfter}`);
  console.log(`Items added: ${itemsAfter - itemsBefore}`);
  console.log(`New aria-expanded: ${expandableFolder.getAttribute('aria-expanded')}`);
  
  // Check if children are nested inside the item
  console.log('\n--- Checking for nested children ---');
  const nestedChildren = expandableFolder.querySelectorAll('[role="button"]');
  console.log(`Found ${nestedChildren.length} nested button elements (including parent)`);
  
  if (nestedChildren.length > 1) {
    console.log('✓ Children are NESTED inside the parent item!');
    console.log('First few nested children:');
    Array.from(nestedChildren).slice(1, 4).forEach((child, i) => {
      const name = child.querySelector('button[title]')?.getAttribute('title') || 'unnamed';
      console.log(`  ${i + 1}. ${name}`);
    });
  }
  
  // Dump all items with their padding
  console.log('\n--- All items in tree (with padding) ---');
  const allItems = Array.from(treeContainer.children);
  
  allItems.forEach((item, index) => {
    const name = item.querySelector('button[title]')?.getAttribute('title') || 'unnamed';
    const group = item.querySelector('.group');
    const padding = group ? parseInt(window.getComputedStyle(group).paddingLeft) : 0;
    const hasExpand = item.querySelector('button[aria-label="Expand"]') !== null;
    const isExpanded = item.getAttribute('aria-expanded') === 'true';
    
    console.log(`${index}: "${name}" | padding=${padding}px | expand=${hasExpand} | expanded=${isExpanded}`);
  });
  
  console.log('\n--- First 3 items HTML ---');
  allItems.slice(0, 3).forEach((item, index) => {
    const name = item.querySelector('button[title]')?.getAttribute('title') || 'unnamed';
    console.log(`\nItem ${index} (${name}):`);
    console.log(item.outerHTML.substring(0, 400) + '...');
  });
  
  console.log('\n========== END DIAGNOSTIC ==========\n');
}

// Download a single song
async function downloadSong(song) {
  console.log(`Downloading: ${song.title} from ${song.folderPath.join('/')}`);
  
  try {
    // Navigate to song page
    window.location.href = song.url;
    
    // Wait for page to load
    await sleep(2000);
    
    // Find download button (button with lucide-download icon)
    const downloadButton = document.querySelector('button:has(svg.lucide-download)');
    
    if (!downloadButton) {
      console.error('Download button not found');
      return;
    }
    
    console.log('Clicking download button...');
    downloadButton.click();
    
    // Wait for menu to appear
    await sleep(500);
    
    // Look for MP3 option in the menu
    // The menu items might be in a dropdown/menu element
    const menuItems = document.querySelectorAll('[role="menuitem"], [role="option"], button');
    
    for (const item of menuItems) {
      const text = item.textContent.toLowerCase();
      if (text.includes('mp3')) {
        console.log('Clicking MP3 option...');
        item.click();
        await sleep(500);
        break;
      }
    }
    
    console.log('Download initiated for:', song.title);
    
  } catch (error) {
    console.error('Error downloading song:', error);
  }
}

// Log when script loads
console.log('Folder mapper ready. Waiting for mapping command...');


// ============================================================================
// METADATA EXPORT WITH INCREMENTAL UPDATE SUPPORT
// ============================================================================

/**
 * Export metadata with incremental update detection
 */
async function exportMetadataWithIncrementalSupport(structure) {
  try {
    logger.info('Preparing metadata export with incremental support');
    
    // Load seen songs cache
    const result = await chrome.storage.local.get(['seenSongsCache']);
    const seenCache = result.seenSongsCache || {};
    
    // Flatten folder tree
    const folders = flattenFolders(structure.folders || structure.rootFolders || []);
    
    // Extract all songs with incremental detection
    const songs = extractAllSongsWithIncrementalInfo(structure, seenCache);
    
    // Extract tag relationships
    const tags = extractAllTags(songs);
    
    // Update seen cache
    const newCache = {};
    songs.forEach(song => {
      newCache[song.id] = {
        hash: song.metadataHash,
        lastSeen: song.metadataCollectedAt
      };
    });
    await chrome.storage.local.set({ 
      seenSongsCache: newCache,
      lastScanTimestamp: Date.now()
    });
    
    // Calculate statistics
    const stats = {
      totalFolders: folders.length,
      totalSongs: songs.length,
      newSongs: songs.filter(s => s.isNew).length,
      changedSongs: songs.filter(s => s.isChanged).length,
      unchangedSongs: songs.filter(s => !s.isNew && !s.isChanged).length
    };
    
    logger.success('Export prepared', stats);
    
    // Prepare export data
    const exportData = {
      exportVersion: '2.0',
      exportDate: new Date().toISOString(),
      statistics: stats,
      folders: folders,
      songs: songs.map(s => sanitizeSongForExport(s)),
      tags: tags
    };
    
    // Trigger download
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
      type: 'application/json' 
    });
    const url = URL.createObjectURL(blob);
    
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `udio_metadata_${timestamp}.json`;
    
    chrome.downloads.download({
      url: url,
      filename: filename,
      saveAs: true
    }, (downloadId) => {
      if (chrome.runtime.lastError) {
        logger.error('Export download failed', { 
          error: chrome.runtime.lastError.message 
        });
      } else {
        logger.success('Export download started', { downloadId, filename });
      }
      
      // Clean up blob URL
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
    
    return {
      status: 'success',
      stats: stats
    };
    
  } catch (error) {
    logger.error('Export failed', { error: error.message });
    return {
      status: 'error',
      error: error.message
    };
  }
}

/**
 * Flatten folder tree into array with stable IDs
 */
function flattenFolders(folders, parentId = null, parentPath = []) {
  const flattened = [];
  
  folders.forEach(folder => {
    const currentPath = [...parentPath, folder.name];
    const folderId = generateFolderId(currentPath);
    
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
      const subfolders = flattenFolders(
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
 */
function generateFolderId(path) {
  const pathString = path.join('/');
  return simpleHash(pathString);
}

/**
 * Extract all songs with incremental detection
 */
function extractAllSongsWithIncrementalInfo(structure, seenCache) {
  const songs = [];
  
  // Extract root songs
  if (structure.rootSongs && structure.rootSongs.length > 0) {
    structure.rootSongs.forEach(song => {
      const enrichedSong = enrichSongWithIncrementalInfo(song, null, seenCache);
      songs.push(enrichedSong);
    });
  }
  
  // Extract songs from folders recursively
  const extractFromFolders = (folders, parentPath = []) => {
    folders.forEach(folder => {
      const currentPath = [...parentPath, folder.name];
      const folderId = generateFolderId(currentPath);
      
      if (folder.songs && folder.songs.length > 0) {
        folder.songs.forEach(song => {
          const enrichedSong = enrichSongWithIncrementalInfo(song, folderId, seenCache);
          songs.push(enrichedSong);
        });
      }
      
      if (folder.subfolders && folder.subfolders.length > 0) {
        extractFromFolders(folder.subfolders, currentPath);
      }
    });
  };
  
  const rootFolders = structure.folders || structure.rootFolders || [];
  if (rootFolders.length > 0) {
    extractFromFolders(rootFolders);
  }
  
  return songs;
}

/**
 * Enrich song with incremental update information
 */
function enrichSongWithIncrementalInfo(song, folderId, seenCache) {
  const cached = seenCache[song.id];
  
  // Generate metadata hash if not present
  if (!song.metadataHash) {
    song.metadataHash = generateMetadataHash(song);
  }
  
  // Add metadata collection timestamp if not present
  if (!song.metadataCollectedAt) {
    song.metadataCollectedAt = new Date().toISOString();
  }
  
  return {
    ...song,
    folderId: folderId,
    isNew: !cached,
    isChanged: cached && cached.hash !== song.metadataHash
  };
}

/**
 * Generate metadata hash for change detection
 */
function generateMetadataHash(song) {
  const hashData = {
    title: song.title,
    artist: song.artist,
    duration: song.duration,
    isLiked: song.isLiked,
    isDisliked: song.isDisliked,
    plays: song.plays,
    likes: song.likes,
    tags: song.tags?.sort().join(','),
    lyricsAvailable: song.lyricsAvailable
  };
  
  const hashString = JSON.stringify(hashData);
  return simpleHash(hashString);
}

/**
 * Sanitize song for export (stable IDs only, no transient URLs)
 */
function sanitizeSongForExport(song) {
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
  };
}

/**
 * Extract all tag relationships
 */
function extractAllTags(songs) {
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
 * Simple hash function for generating stable IDs
 */
function simpleHash(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(36);
}
