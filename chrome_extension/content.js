// Content script for Udio Library Mapper
// This runs on Udio.com pages and analyzes the library structure

console.log('Udio Library Mapper: Content script loaded');

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'mapLibrary') {
    console.log('Mapping library structure...');
    
    try {
      const libraryData = analyzeLibraryStructure();
      sendResponse({ success: true, data: libraryData });
    } catch (error) {
      console.error('Error mapping library:', error);
      sendResponse({ success: false, error: error.message });
    }
    
    return true; // Keep message channel open for async response
  }
});

// Main function to analyze library structure
function analyzeLibraryStructure() {
  const data = {
    timestamp: new Date().toISOString(),
    pageUrl: window.location.href,
    pageType: classifyPage(),
    folders: [],
    songs: [],
    navigation: [],
    metadata: {}
  };
  
  // Detect page type
  console.log('Page type:', data.pageType);
  
  // Find folders
  data.folders = findFolders();
  console.log('Found folders:', data.folders.length);
  
  // Find songs
  data.songs = findSongs();
  console.log('Found songs:', data.songs.length);
  
  // Find navigation elements
  data.navigation = findNavigation();
  console.log('Found navigation elements:', data.navigation.length);
  
  // Get page metadata
  data.metadata = getPageMetadata();
  
  return data;
}

// Classify the current page
function classifyPage() {
  const url = window.location.href.toLowerCase();
  const title = document.title.toLowerCase();
  
  if (url.includes('/library')) return 'library';
  if (url.includes('/my-creations')) return 'my-creations';
  if (url.includes('/create')) return 'create';
  if (url.includes('/login')) return 'login';
  
  return 'unknown';
}

// Find folder elements
function findFolders() {
  const folders = [];
  
  // Try multiple selectors for folders
  const folderSelectors = [
    '[data-testid*="folder"]',
    '[class*="folder"]',
    '[aria-label*="folder"]',
    '[role="treeitem"]',
    '.folder',
    '[data-folder]',
    '[data-type="folder"]'
  ];
  
  folderSelectors.forEach(selector => {
    try {
      const elements = document.querySelectorAll(selector);
      elements.forEach((element, index) => {
        const folderInfo = extractFolderInfo(element, selector, index);
        if (folderInfo) {
          folders.push(folderInfo);
        }
      });
    } catch (error) {
      console.warn(`Error with selector ${selector}:`, error);
    }
  });
  
  // Remove duplicates based on name
  const uniqueFolders = [];
  const seen = new Set();
  
  folders.forEach(folder => {
    const key = `${folder.name}-${folder.path}`;
    if (!seen.has(key)) {
      seen.add(key);
      uniqueFolders.push(folder);
    }
  });
  
  return uniqueFolders;
}

// Extract folder information from element
function extractFolderInfo(element, selector, index) {
  try {
    return {
      name: element.textContent.trim().substring(0, 200) || `Folder ${index + 1}`,
      selector: selector,
      classes: element.className,
      id: element.id,
      path: element.getAttribute('data-path') || element.getAttribute('href') || '',
      songCount: element.getAttribute('data-count') || null,
      attributes: getRelevantAttributes(element)
    };
  } catch (error) {
    console.warn('Error extracting folder info:', error);
    return null;
  }
}

// Find song/track elements
function findSongs() {
  const songs = [];
  
  // Try multiple selectors for songs
  const songSelectors = [
    '[data-testid*="song"]',
    '[data-testid*="track"]',
    '[data-testid*="audio"]',
    '[class*="song"]',
    '[class*="track"]',
    '[class*="card"]',
    'article',
    '[role="listitem"]',
    '[data-song]',
    '[data-type="song"]',
    '[data-type="track"]'
  ];
  
  songSelectors.forEach(selector => {
    try {
      const elements = document.querySelectorAll(selector);
      elements.forEach((element, index) => {
        const songInfo = extractSongInfo(element, selector, index);
        if (songInfo) {
          songs.push(songInfo);
        }
      });
    } catch (error) {
      console.warn(`Error with selector ${selector}:`, error);
    }
  });
  
  // Remove duplicates based on title
  const uniqueSongs = [];
  const seen = new Set();
  
  songs.forEach(song => {
    const key = `${song.title}-${song.url}`;
    if (!seen.has(key)) {
      seen.add(key);
      uniqueSongs.push(song);
    }
  });
  
  return uniqueSongs;
}

// Extract song information from element
function extractSongInfo(element, selector, index) {
  try {
    // Try to find title
    const titleElement = element.querySelector('[class*="title"], h1, h2, h3, h4, [data-title]');
    const title = titleElement ? titleElement.textContent.trim() : element.textContent.trim().substring(0, 100);
    
    // Try to find artist
    const artistElement = element.querySelector('[class*="artist"], [data-artist]');
    const artist = artistElement ? artistElement.textContent.trim() : null;
    
    // Try to find duration
    const durationElement = element.querySelector('[class*="duration"], [data-duration], time');
    const duration = durationElement ? durationElement.textContent.trim() : null;
    
    // Check for audio/play elements
    const hasAudio = element.querySelector('audio') !== null;
    const hasPlayButton = element.querySelector('[aria-label*="play"], [aria-label*="Play"], [class*="play"]') !== null;
    const hasDownloadButton = element.querySelector('[aria-label*="download"], [aria-label*="Download"], [class*="download"]') !== null;
    
    // Try to find URL
    const linkElement = element.querySelector('a[href]');
    const url = linkElement ? linkElement.href : '';
    
    return {
      title: title || `Song ${index + 1}`,
      artist: artist,
      duration: duration,
      selector: selector,
      classes: element.className,
      id: element.id,
      url: url,
      hasAudio: hasAudio,
      hasPlayButton: hasPlayButton,
      hasDownloadButton: hasDownloadButton,
      folder: element.getAttribute('data-folder') || null,
      attributes: getRelevantAttributes(element)
    };
  } catch (error) {
    console.warn('Error extracting song info:', error);
    return null;
  }
}

// Find navigation elements
function findNavigation() {
  const navigation = [];
  
  const navSelectors = [
    'nav',
    '[role="navigation"]',
    '[class*="nav"]',
    '[class*="menu"]',
    '[class*="sidebar"]'
  ];
  
  navSelectors.forEach(selector => {
    try {
      const elements = document.querySelectorAll(selector);
      elements.forEach(element => {
        navigation.push({
          selector: selector,
          text: element.textContent.trim().substring(0, 200),
          classes: element.className,
          id: element.id
        });
      });
    } catch (error) {
      console.warn(`Error with nav selector ${selector}:`, error);
    }
  });
  
  return navigation;
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
    hasAudioPlayer: document.querySelector('audio, video, [class*="player"]') !== null,
    mainContainers: Array.from(document.querySelectorAll('main, [role="main"], .container, .content')).length,
    gridLayouts: document.querySelectorAll('[class*="grid"]').length,
    listLayouts: document.querySelectorAll('ul, ol, [role="list"]').length
  };
}

// Auto-detect and log page structure on load
window.addEventListener('load', () => {
  console.log('Udio Library Mapper: Page loaded, ready to analyze');
  
  // Log some basic info
  const pageType = classifyPage();
  console.log('Detected page type:', pageType);
  
  if (pageType === 'library' || pageType === 'my-creations') {
    console.log('Library page detected - extension ready to map structure');
  }
});