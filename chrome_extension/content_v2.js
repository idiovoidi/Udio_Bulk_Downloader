// Enhanced Content script for Udio Library Mapper V2
// This version recursively maps folders, subfolders, and songs

console.log('Udio Library Mapper V2: Content script loaded');

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'mapLibrary') {
    console.log('Starting recursive library mapping...');
    
    // Use async function to handle the recursive mapping
    (async () => {
      try {
        const libraryData = await analyzeLibraryRecursively();
        sendResponse({ success: true, data: libraryData });
      } catch (error) {
        console.error('Error mapping library:', error);
        sendResponse({ success: false, error: error.message });
      }
    })();
    
    return true; // Keep message channel open for async response
  }
});

// Main function to recursively analyze library structure
async function analyzeLibraryRecursively() {
  const data = {
    timestamp: new Date().toISOString(),
    pageUrl: window.location.href,
    pageType: classifyPage(),
    rootFolders: [],
    totalFolders: 0,
    totalSongs: 0,
    metadata: getPageMetadata()
  };
  
  console.log('Starting recursive folder analysis...');
  
  // Get all root-level folders
  const rootFolders = findRootFolders();
  console.log(`Found ${rootFolders.length} root folders`);
  
  // Process each root folder recursively
  for (let i = 0; i < rootFolders.length; i++) {
    const folderElement = rootFolders[i];
    console.log(`Processing folder ${i + 1}/${rootFolders.length}...`);
    
    const folderData = await processFolderRecursively(folderElement, 0, `Folder ${i + 1}`);
    if (folderData) {
      data.rootFolders.push(folderData);
    }
    
    // Small delay to avoid overwhelming the page
    await sleep(100);
  }
  
  // Calculate totals
  data.totalFolders = countTotalFolders(data.rootFolders);
  data.totalSongs = countTotalSongs(data.rootFolders);
  
  console.log(`Mapping complete: ${data.totalFolders} folders, ${data.totalSongs} songs`);
  
  return data;
}

// Find root-level folders (not nested)
function findRootFolders() {
  const folders = [];
  
  // Look for folder elements with the specific class pattern
  const folderSelectors = [
    '.group\\/folder',
    '[class*="group/folder"]',
    '[data-folder]',
    '[role="treeitem"]'
  ];
  
  folderSelectors.forEach(selector => {
    try {
      const elements = document.querySelectorAll(selector);
      elements.forEach(element => {
        // Check if it's a real folder (has the right classes and text)
        const classes = element.className;
        const text = element.textContent.trim();
        
        if (classes.includes('group/folder') && text.length > 0 && text.length < 500) {
          // Avoid duplicates
          if (!folders.includes(element)) {
            folders.push(element);
          }
        }
      });
    } catch (error) {
      console.warn(`Error with selector ${selector}:`, error);
    }
  });
  
  return folders;
}

// Recursively process a folder and its contents
async function processFolderRecursively(folderElement, depth, defaultName) {
  try {
    const folderInfo = extractFolderInfo(folderElement, depth, defaultName);
    
    // Check if folder is already expanded
    const isExpanded = checkIfFolderExpanded(folderElement);
    
    if (!isExpanded) {
      // Click to expand the folder
      console.log(`  ${'  '.repeat(depth)}Expanding: ${folderInfo.name}`);
      await clickFolder(folderElement);
      
      // Wait for content to load
      await sleep(500);
    }
    
    // Find subfolders and songs within this folder
    const subfolders = findSubfoldersInFolder(folderElement);
    const songs = findSongsInFolder(folderElement);
    
    console.log(`  ${'  '.repeat(depth)}Found ${subfolders.length} subfolders, ${songs.length} songs`);
    
    folderInfo.subfolders = [];
    folderInfo.songs = songs;
    
    // Recursively process subfolders
    for (let i = 0; i < subfolders.length; i++) {
      const subfolder = await processFolderRecursively(subfolders[i], depth + 1, `Subfolder ${i + 1}`);
      if (subfolder) {
        folderInfo.subfolders.push(subfolder);
      }
    }
    
    return folderInfo;
    
  } catch (error) {
    console.error('Error processing folder:', error);
    return null;
  }
}

// Extract folder information
function extractFolderInfo(element, depth, defaultName) {
  const text = element.textContent.trim();
  
  // Parse folder name and song count from text like "My Folder123songs"
  const match = text.match(/^(.+?)(\d+)\s*songs?$/i);
  
  let name = defaultName;
  let songCount = null;
  
  if (match) {
    name = match[1].trim();
    songCount = parseInt(match[2]);
  } else if (text.length > 0 && text.length < 200) {
    name = text;
  }
  
  return {
    name: name,
    depth: depth,
    songCount: songCount,
    path: element.getAttribute('data-path') || '',
    classes: element.className,
    id: element.getAttribute('id') || '',
    subfolders: [],
    songs: [],
    attributes: getRelevantAttributes(element)
  };
}

// Check if folder is expanded
function checkIfFolderExpanded(folderElement) {
  // Look for expanded indicators
  const ariaExpanded = folderElement.getAttribute('aria-expanded');
  if (ariaExpanded === 'true') return true;
  
  // Check for expanded class
  if (folderElement.className.includes('expanded')) return true;
  
  // Check if there's visible content below
  const parent = folderElement.closest('[role="tree"], [role="group"], .folder-container');
  if (parent) {
    const nextSibling = folderElement.nextElementSibling;
    if (nextSibling && nextSibling.style.display !== 'none') {
      return true;
    }
  }
  
  return false;
}

// Click folder to expand it
async function clickFolder(folderElement) {
  try {
    // Try to find clickable element within folder
    const clickable = folderElement.querySelector('button, [role="button"], a') || folderElement;
    
    // Simulate click
    clickable.click();
    
    // Also try dispatching events
    clickable.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    
    return true;
  } catch (error) {
    console.warn('Error clicking folder:', error);
    return false;
  }
}

// Find subfolders within a folder
function findSubfoldersInFolder(parentFolder) {
  const subfolders = [];
  
  // Look for nested folder elements
  // They should be siblings or children of the parent folder
  const container = parentFolder.closest('[role="tree"], [role="group"], .folder-list') || parentFolder.parentElement;
  
  if (container) {
    const nestedFolders = container.querySelectorAll('.group\\/folder, [class*="group/folder"]');
    
    nestedFolders.forEach(folder => {
      // Make sure it's not the parent itself and is actually nested
      if (folder !== parentFolder && isDescendantOf(folder, parentFolder)) {
        subfolders.push(folder);
      }
    });
  }
  
  return subfolders;
}

// Find songs within a folder
function findSongsInFolder(parentFolder) {
  const songs = [];
  
  // Look for song elements near this folder
  const songSelectors = [
    '[data-testid*="song"]',
    '[data-testid*="track"]',
    '[class*="song-card"]',
    '[class*="track-card"]',
    'article',
    '[role="listitem"]'
  ];
  
  // Get the container that holds songs for this folder
  const container = findSongContainer(parentFolder);
  
  if (container) {
    songSelectors.forEach(selector => {
      try {
        const elements = container.querySelectorAll(selector);
        elements.forEach(element => {
          const songInfo = extractSongInfo(element);
          if (songInfo && !songs.find(s => s.title === songInfo.title)) {
            songs.push(songInfo);
          }
        });
      } catch (error) {
        console.warn(`Error with song selector ${selector}:`, error);
      }
    });
  }
  
  return songs;
}

// Find the container that holds songs for a folder
function findSongContainer(folderElement) {
  // Look for common song container patterns
  const parent = folderElement.parentElement;
  
  // Try to find next sibling that contains songs
  let sibling = folderElement.nextElementSibling;
  while (sibling) {
    if (sibling.querySelector('[data-testid*="song"], article, [class*="song"]')) {
      return sibling;
    }
    sibling = sibling.nextElementSibling;
  }
  
  // Try parent's next sibling
  if (parent) {
    sibling = parent.nextElementSibling;
    if (sibling) {
      return sibling;
    }
  }
  
  return null;
}

// Extract song information
function extractSongInfo(element) {
  try {
    const titleElement = element.querySelector('[class*="title"], h1, h2, h3, h4, [data-title]');
    const title = titleElement ? titleElement.textContent.trim() : element.textContent.trim().substring(0, 100);
    
    if (!title || title.length === 0) return null;
    
    const artistElement = element.querySelector('[class*="artist"], [data-artist]');
    const artist = artistElement ? artistElement.textContent.trim() : null;
    
    const durationElement = element.querySelector('[class*="duration"], [data-duration], time');
    const duration = durationElement ? durationElement.textContent.trim() : null;
    
    const linkElement = element.querySelector('a[href]');
    const url = linkElement ? linkElement.href : '';
    
    const downloadButton = element.querySelector('[aria-label*="download"], [aria-label*="Download"], [class*="download"]');
    const playButton = element.querySelector('[aria-label*="play"], [aria-label*="Play"], [class*="play"]');
    
    return {
      title: title,
      artist: artist,
      duration: duration,
      url: url,
      hasDownloadButton: downloadButton !== null,
      hasPlayButton: playButton !== null,
      classes: element.className,
      id: element.id || '',
      attributes: getRelevantAttributes(element)
    };
  } catch (error) {
    console.warn('Error extracting song info:', error);
    return null;
  }
}

// Helper: Check if element is descendant of another
function isDescendantOf(child, parent) {
  let node = child.parentNode;
  while (node) {
    if (node === parent) {
      return true;
    }
    node = node.parentNode;
  }
  return false;
}

// Helper: Sleep function
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Count total folders recursively
function countTotalFolders(folders) {
  let count = folders.length;
  folders.forEach(folder => {
    if (folder.subfolders && folder.subfolders.length > 0) {
      count += countTotalFolders(folder.subfolders);
    }
  });
  return count;
}

// Count total songs recursively
function countTotalSongs(folders) {
  let count = 0;
  folders.forEach(folder => {
    count += folder.songs ? folder.songs.length : 0;
    if (folder.subfolders && folder.subfolders.length > 0) {
      count += countTotalSongs(folder.subfolders);
    }
  });
  return count;
}

// Classify the current page
function classifyPage() {
  const url = window.location.href.toLowerCase();
  if (url.includes('/library')) return 'library';
  if (url.includes('/my-creations')) return 'my-creations';
  if (url.includes('/create')) return 'create';
  if (url.includes('/login')) return 'login';
  return 'unknown';
}

// Get relevant attributes from element
function getRelevantAttributes(element) {
  const attributes = {};
  const relevantAttrs = ['data-testid', 'data-id', 'data-type', 'data-path', 'data-folder', 'data-song', 'aria-label'];
  
  relevantAttrs.forEach(attr => {
    const value = element.getAttribute(attr);
    if (value) {
      attributes[attr] = value;
    }
  });
  
  return attributes;
}

// Get page metadata
function getPageMetadata() {
  return {
    title: document.title,
    url: window.location.href,
    bodyClasses: document.body.className,
    hasUserMenu: document.querySelector('[data-testid*="user"], [aria-label*="user"], .user-menu') !== null,
    hasLibraryView: document.querySelector('[data-testid*="library"], [class*="library"]') !== null,
    hasFolderTree: document.querySelector('[role="tree"], [role="treegrid"]') !== null,
    hasAudioPlayer: document.querySelector('audio, video, [class*="player"]') !== null
  };
}

// Auto-detect and log page structure on load
window.addEventListener('load', () => {
  console.log('Udio Library Mapper V2: Page loaded, ready for recursive analysis');
});