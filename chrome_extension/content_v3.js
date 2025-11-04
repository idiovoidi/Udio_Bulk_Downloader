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
  } else if (request.action === 'startMapping') {
    startFolderTreeMapping();
    sendResponse({ status: 'started' });
  } else if (request.action === 'getProgress') {
    sendResponse({
      inProgress: mappingInProgress,
      structure: currentStructure
    });
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
    
    // Get all direct children (top-level folder items)
    const topLevelItems = Array.from(treeContainer.children);
    currentStructure.totalFolders = topLevelItems.length;
    
    console.log(`Found ${topLevelItems.length} top-level folders`);
    
    // Process each top-level folder
    for (let i = 0; i < topLevelItems.length; i++) {
      const item = topLevelItems[i];
      const folderData = await processFolderItem(item, [], treeContainer);
      
      if (folderData) {
        currentStructure.folders.push(folderData);
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
      await sleep(600); // Wait for expansion
    }
    
    // After expanding, find child items
    // Children appear as siblings immediately after this item in the DOM
    const allItems = Array.from(treeContainer.children);
    const currentIndex = allItems.indexOf(item);
    
    // Get the padding of current item to compare with children
    const currentGroup = item.querySelector('.group');
    const currentPadding = currentGroup ? parseInt(window.getComputedStyle(currentGroup).paddingLeft) : 0;
    
    console.log(`Current padding: ${currentPadding}px`);
    
    // Find children (they will have more padding)
    const children = [];
    for (let i = currentIndex + 1; i < allItems.length; i++) {
      const nextItem = allItems[i];
      const nextGroup = nextItem.querySelector('.group');
      
      if (!nextGroup) continue;
      
      const nextPadding = parseInt(window.getComputedStyle(nextGroup).paddingLeft);
      
      // If padding is greater, it's a child
      if (nextPadding > currentPadding) {
        // Only add direct children (padding is exactly one level deeper)
        // Typically each level adds 16-24px
        if (nextPadding - currentPadding < 30) {
          children.push(nextItem);
        }
      } else {
        // No longer a child, stop looking
        break;
      }
    }
    
    console.log(`Found ${children.length} direct children for ${folderName}`);
    
    // Process each child recursively
    for (const child of children) {
      const childData = await processFolderItem(child, currentPath, treeContainer);
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
    await sleep(1000); // Wait for songs to load
    
    // Try to count songs in the main view
    const songCount = await countSongsInView();
    folderData.songCount = songCount;
    currentStructure.totalSongs += songCount;
    
    console.log(`Found ${songCount} songs in ${folderName}`);
  }
  
  return folderData;
}

async function countSongsInView() {
  // Wait a bit for content to load
  await sleep(500);
  
  // Try multiple selectors to find song elements
  const songSelectors = [
    '[data-testid*="song"]',
    '[data-song-id]',
    '[role="article"]',
    '.song-item',
    '[class*="song-card"]',
    '[class*="track-item"]'
  ];
  
  for (const selector of songSelectors) {
    const elements = document.querySelectorAll(selector);
    if (elements.length > 0) {
      console.log(`Found ${elements.length} songs using selector: ${selector}`);
      return elements.length;
    }
  }
  
  // Fallback: look for any repeated elements that might be songs
  const mainContent = document.querySelector('main, [role="main"], .content');
  if (mainContent) {
    // Look for repeated elements with similar structure
    const allElements = mainContent.querySelectorAll('div[class], article[class]');
    const classCount = {};
    
    allElements.forEach(el => {
      const className = el.className;
      if (className && className.length > 10 && className.length < 200) {
        classCount[className] = (classCount[className] || 0) + 1;
      }
    });
    
    // Find the most common class (likely songs)
    let maxCount = 0;
    for (const count of Object.values(classCount)) {
      if (count > maxCount) {
        maxCount = count;
      }
    }
    
    if (maxCount > 2) {
      console.log(`Estimated ${maxCount} songs based on repeated elements`);
      return maxCount;
    }
  }
  
  console.log('Could not determine song count');
  return 0;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Log when script loads
console.log('Folder mapper ready. Waiting for mapping command...');
