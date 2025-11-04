// content_v3.js - Folder tree panel mapping (updated for actual structure)
console.log('Udio Folder Mapper v3 loaded');

let mappingInProgress = false;
let currentStructure = {
  folders: [],
  totalFolders: 0,
  mappedFolders: 0,
  totalSongs: 0
};

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
  } else if (request.action === 'downloadSong') {
    // Download a single song
    downloadSong(request.song);
    sendResponse({ status: 'downloading' });
  }
  
  return true;
});

async function startFolderTreeMapping() {
  if (mappingInProgress) {
    console.log('Mapping already in progress');
    return;
  }
  
  mappingInProgress = true;
  currentStructure = {
    folders: [],
    totalFolders: 0,
    mappedFolders: 0,
    totalSongs: 0
  };
  
  console.log('Starting folder tree mapping...');
  
  try {
    // Find the folder tree panel
    const treeContainer = document.querySelector('[role="tree"][aria-label="Folder structure"]');
    
    if (!treeContainer) {
      throw new Error('Folder tree panel not found. Please open the folder tree by clicking the folder icon in the top right.');
    }
    
    console.log('Found folder tree panel');
    console.log('Tree container HTML sample:', treeContainer.innerHTML.substring(0, 500));
    
    // Get all direct children (top-level folder items)
    const topLevelItems = Array.from(treeContainer.children);
    currentStructure.totalFolders = topLevelItems.length;
    
    console.log(`Found ${topLevelItems.length} top-level folders`);
    console.log('First item HTML:', topLevelItems[0]?.outerHTML.substring(0, 300));
    
    // Process each top-level folder
    for (let i = 0; i < topLevelItems.length; i++) {
      const item = topLevelItems[i];
      console.log(`\n=== Processing top-level folder ${i + 1}/${topLevelItems.length} ===`);
      
      const folderData = await processFolderItem(item, [], treeContainer);
      
      if (folderData) {
        console.log(`✓ Successfully processed: ${folderData.name}`);
        currentStructure.folders.push(folderData);
      } else {
        console.warn(`✗ Failed to process folder at index ${i}`);
      }
      
      currentStructure.mappedFolders = i + 1;
      
      // Send progress update
      chrome.runtime.sendMessage({
        action: 'progressUpdate',
        progress: {
          ...currentStructure,
          percentComplete: Math.round((i + 1) / topLevelItems.length * 100)
        }
      });
    }
    
    console.log('Mapping complete!', currentStructure);
    console.log('Full structure:', JSON.stringify(currentStructure, null, 2));
    
    // Send completion message
    chrome.runtime.sendMessage({
      action: 'mappingComplete',
      structure: currentStructure
    });
    
  } catch (error) {
    console.error('Mapping failed:', error);
    chrome.runtime.sendMessage({
      action: 'mappingError',
      error: error.message
    });
  } finally {
    mappingInProgress = false;
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
    await sleep(1500); // Wait for songs to load
    
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
  await sleep(800);
  
  const songs = [];
  
  // Songs are in table rows with specific structure
  // Look for rows that contain song links
  const songRows = document.querySelectorAll('tr[class*="absolute"]');
  
  console.log(`Found ${songRows.length} potential song rows`);
  
  if (songRows.length === 0) {
    // Fallback: look for any links to /songs/
    const songLinks = document.querySelectorAll('a[href*="/songs/"]');
    console.log(`Fallback: Found ${songLinks.length} song links`);
    
    songLinks.forEach((link) => {
      const container = link.closest('tr, div[class*="group"]');
      if (container && !songs.find(s => s.url === link.href)) {
        const song = extractSongFromElement(container);
        if (song) songs.push(song);
      }
    });
  } else {
    // Extract from table rows
    songRows.forEach((row) => {
      const song = extractSongFromElement(row);
      if (song) songs.push(song);
    });
  }
  
  console.log(`Extracted ${songs.length} songs with metadata`);
  return songs;
}

function extractSongFromElement(element) {
  try {
    const song = {
      title: null,
      url: null,
      id: null,
      duration: null,
      imageUrl: null,
      tags: [],
      plays: null,
      likes: null
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
