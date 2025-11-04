// Popup script for Udio Library Mapper extension

let libraryData = null;

// DOM elements
const statusDiv = document.getElementById('status');
const mapButton = document.getElementById('mapLibrary');
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
  const totalSongs = data.totalSongs || data.songs?.length || 0;
  
  let html = '<ul>';
  html += `<li><strong>Total Folders:</strong> ${totalFolders}</li>`;
  html += `<li><strong>Total Songs:</strong> ${totalSongs}</li>`;
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
    updateStatus('Mapping library...', 'info');
    updateProgress(10, 'Connecting to page...');
    mapButton.disabled = true;
    
    // Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab.url.includes('udio.com')) {
      updateStatus('Please navigate to Udio.com first', 'error');
      mapButton.disabled = false;
      hideProgress();
      return;
    }
    
    updateProgress(30, 'Analyzing page structure...');
    
    // Send message to content script to analyze the page
    const response = await chrome.tabs.sendMessage(tab.id, { action: 'mapLibrary' });
    
    if (response.success) {
      updateProgress(100, 'Complete!');
      updateStatus(`Found ${response.data.folders.length} folders and ${response.data.songs.length} songs`, 'success');
      displayResults(response.data);
      hideProgress();
    } else {
      updateStatus(response.error || 'Failed to map library', 'error');
      hideProgress();
    }
    
  } catch (error) {
    console.error('Error mapping library:', error);
    updateStatus(`Error: ${error.message}`, 'error');
    hideProgress();
  } finally {
    mapButton.disabled = false;
  }
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

// Event listeners
mapButton.addEventListener('click', mapLibrary);
exportJsonButton.addEventListener('click', exportAsJson);
exportTextButton.addEventListener('click', exportAsText);

// Check if we're on Udio.com
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  if (tabs[0] && !tabs[0].url.includes('udio.com')) {
    updateStatus('Please navigate to Udio.com', 'warning');
    mapButton.disabled = true;
  }
});