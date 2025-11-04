// Popup script for Udio Library Mapper extension

let libraryData = null;

// DOM elements
const statusDiv = document.getElementById('status');
const mapButton = document.getElementById('mapLibrary');
const exportChecklistButton = document.getElementById('exportChecklist');
const downloadButton = document.getElementById('downloadAll');
const exportJsonButton = document.getElementById('exportJson');
const exportTextButton = document.getElementById('exportText');
const progressDiv = document.getElementById('progress');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const resultsDiv = document.getElementById('results');
const resultsContent = document.getElementById('resultsContent');

// Update status message
function updateStatus(message, type = 'info') {
  statusDiv.textContent = message;
  statusDiv.className = `status ${type}`;
}

// Update progress
function updateProgress(percent, text) {
  progressDiv.classList.add('active');
  progressFill.style.width = `${percent}%`;
  progressText.textContent = text;
}

// Hide progress
function hideProgress() {
  progressDiv.classList.remove('active');
}

// Display results
function displayResults(data) {
  libraryData = data;
  
  const totalFolders = data.totalFolders || data.folders?.length || data.rootFolders?.length || 0;
  const rootSongCount = data.rootSongs?.length || 0;
  const totalSongs = data.totalSongs || data.songs?.length || 0;
  
  let html = '<ul>';
  html += `<li><strong>Total Folders:</strong> ${totalFolders}</li>`;
  html += `<li><strong>Total Songs:</strong> ${totalSongs}</li>`;
  if (rootSongCount > 0) {
    html += `<li><strong>Root Songs:</strong> ${rootSongCount} (not in folders)</li>`;
  }
  html += `<li><strong>Page Type:</strong> ${data.pageType}</li>`;
  html += '</ul>';
  
  // Show root folders
  const rootFolders = data.rootFolders || data.folders || [];
  if (rootFolders.length > 0) {
    html += '<h4>Root Folders:</h4><ul>';
    rootFolders.slice(0, 5).forEach(folder => {
      const subfolderCount = folder.subfolders ? folder.subfolders.length : 0;
      const songCount = folder.songs ? folder.songs.length : folder.songCount || 0;
      html += `<li>${folder.name || 'Unnamed'}`;
      if (subfolderCount > 0) html += ` (${subfolderCount} subfolders)`;
      if (songCount > 0) html += ` (${songCount} songs)`;
      html += `</li>`;
    });
    if (rootFolders.length > 5) {
      html += `<li><em>...and ${rootFolders.length - 5} more</em></li>`;
    }
    html += '</ul>';
  }
  
  resultsContent.innerHTML = html;
  resultsDiv.style.display = 'block';
  
  // Enable export buttons
  exportJsonButton.disabled = false;
  exportTextButton.disabled = false;
}

// Map library structure
async function mapLibrary() {
  try {
    updateStatus('Starting mapping... Make sure folder tree is open!', 'info');
    updateProgress(5, 'Connecting to page...');
    mapButton.disabled = true;
    
    // Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab.url.includes('udio.com')) {
      updateStatus('Please navigate to Udio.com first', 'error');
      mapButton.disabled = false;
      hideProgress();
      return;
    }
    
    updateProgress(10, 'Starting folder tree mapping...');
    
    // Send message to content script to start mapping
    try {
      const response = await chrome.tabs.sendMessage(tab.id, { action: 'startMapping' });
      
      if (response && response.status === 'started') {
        updateStatus('Mapping in progress...', 'info');
        // Start polling for progress
        startProgressPolling(tab.id);
      } else {
        updateStatus('Failed to start mapping', 'error');
        hideProgress();
        mapButton.disabled = false;
      }
    } catch (msgError) {
      // Content script not loaded
      if (msgError.message.includes('Receiving end does not exist')) {
        updateStatus('⚠️ Please REFRESH the Udio page (F5) and try again', 'error');
        console.log('Content script not loaded. User needs to refresh the page.');
      } else {
        updateStatus(`Error: ${msgError.message}`, 'error');
      }
      hideProgress();
      mapButton.disabled = false;
    }
    
  } catch (error) {
    console.error('Error mapping library:', error);
    updateStatus(`Error: ${error.message}`, 'error');
    hideProgress();
    mapButton.disabled = false;
  }
}

// Poll for progress updates
function startProgressPolling(tabId) {
  const pollInterval = setInterval(() => {
    chrome.tabs.sendMessage(tabId, { action: 'getProgress' }, (response) => {
      if (chrome.runtime.lastError) {
        clearInterval(pollInterval);
        updateStatus('Connection lost', 'error');
        hideProgress();
        mapButton.disabled = false;
        return;
      }
      
      if (response) {
        if (response.inProgress) {
          const structure = response.structure;
          const percent = structure.totalFolders > 0 
            ? Math.round((structure.mappedFolders / structure.totalFolders) * 100) 
            : 10;
          
          updateProgress(percent, `Mapping: ${structure.mappedFolders}/${structure.totalFolders} folders`);
          updateStatus(`Found ${structure.totalSongs} songs so far...`, 'info');
        } else {
          // Mapping complete
          clearInterval(pollInterval);
          const structure = response.structure;
          updateProgress(100, 'Complete!');
          updateStatus(`Mapping complete! ${structure.totalFolders} folders, ${structure.totalSongs} songs`, 'success');
          
          // Format data for display
          const displayData = {
            folders: structure.folders,
            rootFolders: structure.folders,
            totalFolders: structure.totalFolders,
            totalSongs: structure.totalSongs,
            pageType: 'library',
            pageUrl: 'udio.com/library',
            timestamp: new Date().toISOString()
          };
          
          displayResults(displayData);
          hideProgress();
          mapButton.disabled = false;
          exportChecklistButton.disabled = false; // Enable checklist button
          downloadButton.disabled = false; // Enable download button
        }
      }
    });
  }, 500);
}

// Export as JSON
function exportAsJson() {
  if (!libraryData) return;
  
  const dataStr = JSON.stringify(libraryData, null, 2);
  const blob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  const filename = `udio_library_${timestamp}.json`;
  
  chrome.downloads.download({
    url: url,
    filename: filename,
    saveAs: true
  });
  
  updateStatus('JSON export started', 'success');
}

// Export as text
function exportAsText() {
  if (!libraryData) return;
  
  let text = 'UDIO LIBRARY STRUCTURE (HIERARCHICAL)\n';
  text += '='.repeat(50) + '\n\n';
  text += `Mapped: ${new Date().toLocaleString()}\n`;
  text += `Page: ${libraryData.pageUrl}\n`;
  text += `Type: ${libraryData.pageType}\n\n`;
  
  const totalFolders = libraryData.totalFolders || libraryData.folders?.length || 0;
  const totalSongs = libraryData.totalSongs || libraryData.songs?.length || 0;
  
  text += `SUMMARY\n`;
  text += '-'.repeat(50) + '\n';
  text += `Total Folders: ${totalFolders}\n`;
  text += `Total Songs: ${totalSongs}\n\n`;
  
  // Export hierarchical folder structure
  const rootFolders = libraryData.rootFolders || libraryData.folders || [];
  if (rootFolders.length > 0) {
    text += `FOLDER STRUCTURE\n`;
    text += '-'.repeat(50) + '\n';
    rootFolders.forEach((folder, i) => {
      text += formatFolderHierarchy(folder, 0, `${i + 1}.`);
    });
    text += '\n';
  }
  
  const blob = new Blob([text], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  const filename = `udio_library_hierarchical_${timestamp}.txt`;
  
  chrome.downloads.download({
    url: url,
    filename: filename,
    saveAs: true
  });
  
  updateStatus('Text export started', 'success');
}

// Helper function to format folder hierarchy
function formatFolderHierarchy(folder, depth, prefix) {
  const indent = '  '.repeat(depth);
  let text = `${indent}${prefix} ${folder.name || 'Unnamed'}`;
  
  const songCount = folder.songs ? folder.songs.length : folder.songCount || 0;
  const subfolderCount = folder.subfolders ? folder.subfolders.length : 0;
  
  if (songCount > 0) text += ` (${songCount} songs)`;
  if (subfolderCount > 0) text += ` (${subfolderCount} subfolders)`;
  text += '\n';
  
  // Add songs in this folder
  if (folder.songs && folder.songs.length > 0) {
    folder.songs.forEach((song, i) => {
      text += `${indent}  • ${song.title || 'Untitled'}`;
      if (song.artist) text += ` - ${song.artist}`;
      if (song.duration) text += ` [${song.duration}]`;
      text += '\n';
    });
  }
  
  // Recursively add subfolders
  if (folder.subfolders && folder.subfolders.length > 0) {
    folder.subfolders.forEach((subfolder, i) => {
      text += formatFolderHierarchy(subfolder, depth + 1, `${prefix}${i + 1}`);
    });
  }
  
  return text;
}

// Download all songs
async function downloadAllSongs() {
  if (!libraryData || !libraryData.folders) {
    updateStatus('Please map the library first', 'error');
    return;
  }
  
  updateStatus('Preparing download...', 'info');
  downloadButton.disabled = true;
  
  try {
    // Collect all songs from all folders
    const allSongs = [];
    
    function collectSongs(folders, path = []) {
      folders.forEach(folder => {
        const folderPath = [...path, folder.name];
        
        if (folder.songs && folder.songs.length > 0) {
          folder.songs.forEach(song => {
            allSongs.push({
              ...song,
              folderPath: folderPath
            });
          });
        }
        
        if (folder.subfolders && folder.subfolders.length > 0) {
          collectSongs(folder.subfolders, folderPath);
        }
      });
    }
    
    collectSongs(libraryData.folders);
    
    console.log(`Collected ${allSongs.length} songs to download`);
    
    if (allSongs.length === 0) {
      updateStatus('No songs found to download', 'warning');
      downloadButton.disabled = false;
      return;
    }
    
    // Create download list file
    const downloadList = allSongs.map((song, i) => {
      const folderPath = song.folderPath.join('/');
      return `${i + 1}. ${song.title}\n   Folder: ${folderPath}\n   URL: ${song.url}\n`;
    }).join('\n');
    
    // Export download list
    const blob = new Blob([downloadList], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    await chrome.downloads.download({
      url: url,
      filename: 'Udio_Download_List.txt',
      saveAs: false
    });
    
    updateStatus(
      `Found ${allSongs.length} songs. Download list saved. ` +
      `Now you need to manually download each song and organize them. ` +
      `See DOWNLOAD_INSTRUCTIONS.md for details.`,
      'warning'
    );
    
    // Note: Automatic downloading requires navigating to each song page
    // and clicking download buttons, which is complex and may violate ToS
    // For now, we provide the list and user can download manually
    
  } catch (error) {
    console.error('Download error:', error);
    updateStatus(`Error: ${error.message}`, 'error');
  } finally {
    downloadButton.disabled = false;
  }
}

// Export comprehensive song checklist
function exportSongChecklist() {
  if (!libraryData) return;
  
  let text = '═══════════════════════════════════════════════════════════\n';
  text += '           UDIO LIBRARY - COMPLETE SONG CHECKLIST\n';
  text += '═══════════════════════════════════════════════════════════\n\n';
  text += `Generated: ${new Date().toLocaleString()}\n`;
  text += `Total Folders: ${libraryData.totalFolders || 0}\n`;
  text += `Total Songs: ${libraryData.totalSongs || 0}\n\n`;
  
  // Collect all songs with their paths
  const allSongs = [];
  let rootSongs = [];
  
  function collectSongs(folders, path = []) {
    folders.forEach(folder => {
      const folderPath = [...path, folder.name];
      
      if (folder.songs && folder.songs.length > 0) {
        folder.songs.forEach(song => {
          allSongs.push({
            ...song,
            folderPath: folderPath,
            pathString: folderPath.join(' > ')
          });
        });
      }
      
      if (folder.subfolders && folder.subfolders.length > 0) {
        collectSongs(folder.subfolders, folderPath);
      }
    });
  }
  
  // Check for root-level songs (songs not in any folder)
  if (libraryData.songs && libraryData.songs.length > 0) {
    rootSongs = libraryData.songs;
  }
  
  collectSongs(libraryData.folders || libraryData.rootFolders || []);
  
  // Add root songs section if any exist
  if (rootSongs.length > 0) {
    text += '═══════════════════════════════════════════════════════════\n';
    text += '                    ROOT DIRECTORY\n';
    text += '                  (Songs not in folders)\n';
    text += '═══════════════════════════════════════════════════════════\n\n';
    
    rootSongs.forEach((song, i) => {
      text += `[ ] ${i + 1}. ${song.title || 'Untitled'}\n`;
      if (song.url) text += `    URL: ${song.url}\n`;
      if (song.duration) text += `    Duration: ${song.duration}\n`;
      if (song.tags && song.tags.length > 0) text += `    Tags: ${song.tags.join(', ')}\n`;
      text += '\n';
    });
    
    text += `Root Songs: ${rootSongs.length}\n\n`;
  }
  
  // Group songs by folder
  const songsByFolder = {};
  allSongs.forEach(song => {
    const path = song.pathString;
    if (!songsByFolder[path]) {
      songsByFolder[path] = [];
    }
    songsByFolder[path].push(song);
  });
  
  // Sort folders alphabetically
  const sortedFolders = Object.keys(songsByFolder).sort();
  
  // Output each folder with its songs
  sortedFolders.forEach(folderPath => {
    const songs = songsByFolder[folderPath];
    
    text += '═══════════════════════════════════════════════════════════\n';
    text += `📁 ${folderPath}\n`;
    text += '═══════════════════════════════════════════════════════════\n\n';
    
    songs.forEach((song, i) => {
      text += `[ ] ${i + 1}. ${song.title || 'Untitled'}\n`;
      if (song.url) text += `    URL: ${song.url}\n`;
      if (song.duration) text += `    Duration: ${song.duration}\n`;
      if (song.tags && song.tags.length > 0) text += `    Tags: ${song.tags.join(', ')}\n`;
      text += '\n';
    });
    
    text += `Songs in this folder: ${songs.length}\n\n`;
  });
  
  // Summary at the end
  text += '═══════════════════════════════════════════════════════════\n';
  text += '                         SUMMARY\n';
  text += '═══════════════════════════════════════════════════════════\n\n';
  text += `Total Folders: ${sortedFolders.length}\n`;
  text += `Root Songs: ${rootSongs.length}\n`;
  text += `Songs in Folders: ${allSongs.length}\n`;
  text += `TOTAL SONGS: ${rootSongs.length + allSongs.length}\n\n`;
  
  text += 'INSTRUCTIONS:\n';
  text += '1. Print this checklist or keep it open\n';
  text += '2. Mark [ ] with [X] as you download each song\n';
  text += '3. Use the URLs to navigate to each song\n';
  text += '4. Click Download → MP3 for each song\n';
  text += '5. Organize downloaded files into matching folder structure\n\n';
  
  text += 'TIP: You can search this file (Ctrl+F) to find specific songs!\n';
  
  // Download the checklist
  const blob = new Blob([text], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  const filename = `udio_song_checklist_${timestamp}.txt`;
  
  chrome.downloads.download({
    url: url,
    filename: filename,
    saveAs: true
  });
  
  updateStatus(`✓ Checklist exported! ${rootSongs.length + allSongs.length} songs total`, 'success');
}

// Sanitize filename for downloads
function sanitizeFilename(filename) {
  return filename
    .replace(/[<>:"/\\|?*]/g, '_')
    .replace(/\s+/g, ' ')
    .trim()
    .substring(0, 200);
}

// Dump tree structure for debugging
async function dumpTreeStructure() {
  try {
    updateStatus('Dumping tree structure... Check console!', 'info');
    
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    await chrome.tabs.sendMessage(tab.id, { action: 'dumpStructure' });
    
    updateStatus('✓ Tree structure dumped to console (F12)', 'success');
  } catch (error) {
    updateStatus(`Error: ${error.message}`, 'error');
  }
}

// Event listeners
const dumpButton = document.getElementById('dumpStructure');
mapButton.addEventListener('click', mapLibrary);
dumpButton.addEventListener('click', dumpTreeStructure);
exportChecklistButton.addEventListener('click', exportSongChecklist);
downloadButton.addEventListener('click', downloadAllSongs);
exportJsonButton.addEventListener('click', exportAsJson);
exportTextButton.addEventListener('click', exportAsText);

// Listen for messages from background/content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'mappingComplete') {
    console.log('Mapping complete!', message.structure);
  } else if (message.action === 'mappingError') {
    updateStatus(`Error: ${message.error}`, 'error');
    hideProgress();
    mapButton.disabled = false;
  } else if (message.action === 'progressUpdate') {
    console.log('Progress update:', message.progress);
  }
});

// Check if we're on Udio.com and if content script is loaded
chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
  if (tabs[0] && !tabs[0].url.includes('udio.com')) {
    updateStatus('Please navigate to Udio.com', 'warning');
    mapButton.disabled = true;
    return;
  }
  
  // Check if content script is loaded
  if (tabs[0]) {
    try {
      const response = await chrome.tabs.sendMessage(tabs[0].id, { action: 'ping' });
      if (response) {
        updateStatus('Ready to map! Open folder tree panel first.', 'info');
      }
    } catch (error) {
      updateStatus('⚠️ Please REFRESH the page (F5) to load the extension', 'warning');
      console.log('Content script not detected. Page needs refresh.');
    }
  }
});