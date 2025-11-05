// Background service worker for Udio Library Mapper (MV3 compliant)

console.log('Udio Library Mapper: Background service worker loaded');

// Listen for extension installation
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('Udio Library Mapper installed');
    
    // Initialize storage
    chrome.storage.local.set({
      seenSongsCache: {},
      lastScanTimestamp: null
    });
    
    // Open welcome page or instructions
    chrome.tabs.create({
      url: 'https://www.udio.com/library'
    });
  }
});

// Handle chrome.alarms for periodic work (MV3 compliant)
chrome.alarms.onAlarm.addListener((alarm) => {
  console.log('Alarm triggered:', alarm.name);
  
  if (alarm.name === 'scan-library') {
    // Find Udio library tab and trigger scan
    chrome.tabs.query({ url: 'https://www.udio.com/library*' }, (tabs) => {
      if (tabs.length > 0) {
        chrome.tabs.sendMessage(tabs[0].id, { action: 'startMapping' }, (response) => {
          if (chrome.runtime.lastError) {
            console.error('Failed to start mapping:', chrome.runtime.lastError.message);
          } else {
            console.log('Mapping started via alarm:', response);
          }
        });
      } else {
        console.log('No Udio library tab found for scheduled scan');
      }
    });
  }
});

// Listen for messages from content script or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Background received message:', request);
  
  // Route messages based on action
  if (request.action === 'schedulePeriodicScan') {
    // Schedule periodic library scan using chrome.alarms
    const intervalMinutes = request.intervalMinutes || 60;
    chrome.alarms.create('scan-library', {
      delayInMinutes: intervalMinutes,
      periodInMinutes: intervalMinutes
    });
    sendResponse({ status: 'scheduled', intervalMinutes });
    
  } else if (request.action === 'cancelPeriodicScan') {
    // Cancel periodic scan
    chrome.alarms.clear('scan-library', (wasCleared) => {
      sendResponse({ status: 'cancelled', wasCleared });
    });
    return true; // Async response
    
  } else if (request.action === 'getSeenCache') {
    // Retrieve seen songs cache from storage
    chrome.storage.local.get(['seenSongsCache'], (result) => {
      sendResponse({ cache: result.seenSongsCache || {} });
    });
    return true; // Async response
    
  } else if (request.action === 'updateSeenCache') {
    // Update seen songs cache
    chrome.storage.local.set({ 
      seenSongsCache: request.cache,
      lastScanTimestamp: Date.now()
    }, () => {
      sendResponse({ status: 'updated' });
    });
    return true; // Async response
    
  } else if (request.action === 'forwardExportDownload') {
    // Forward export download request (requires user gesture context)
    // This is called from popup which has user gesture
    chrome.downloads.download({
      url: request.url,
      filename: request.filename,
      saveAs: request.saveAs !== false
    }, (downloadId) => {
      if (chrome.runtime.lastError) {
        sendResponse({ status: 'error', error: chrome.runtime.lastError.message });
      } else {
        sendResponse({ status: 'success', downloadId });
      }
    });
    return true; // Async response
    
  } else if (request.action === 'progressUpdate' || 
             request.action === 'mappingComplete' || 
             request.action === 'mappingError') {
    // Forward progress updates to popup if it's open
    chrome.runtime.sendMessage(request).catch(() => {
      // Popup might not be open, that's okay
      console.log('No popup to receive message:', request.action);
    });
    sendResponse({ status: 'forwarded' });
  }
  
  return true; // Keep message channel open for async responses
});