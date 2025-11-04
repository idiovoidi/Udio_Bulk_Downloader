// Background service worker for Udio Library Mapper

console.log('Udio Library Mapper: Background service worker loaded');

// Listen for extension installation
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('Udio Library Mapper installed');
    
    // Open welcome page or instructions
    chrome.tabs.create({
      url: 'https://www.udio.com/library'
    });
  }
});

// Listen for messages from content script or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Background received message:', request);
  
  // Handle any background processing here if needed
  
  return true;
});