// Message routing for content script
export class MessageHandler {
  constructor(folderMapper, diagnostics) {
    this.folderMapper = folderMapper;
    this.diagnostics = diagnostics;
    this.setupListener();
  }

  setupListener() {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      this.handleMessage(request, sender, sendResponse);
      return true; // Keep channel open for async responses
    });
  }

  async handleMessage(request, sender, sendResponse) {
    const { action } = request;

    try {
      switch (action) {
        case 'ping':
          sendResponse({ status: 'ready' });
          break;

        case 'dumpStructure':
          await this.diagnostics.dumpTreeStructure();
          sendResponse({ status: 'dumped' });
          break;

        case 'startMapping':
          this.folderMapper.startMapping();
          sendResponse({ status: 'started' });
          break;

        case 'getProgress':
          sendResponse(this.folderMapper.getProgress());
          break;

        case 'downloadSong':
          await this.downloadSong(request.song);
          sendResponse({ status: 'downloading' });
          break;

        default:
          sendResponse({ status: 'unknown_action' });
      }
    } catch (error) {
      sendResponse({ status: 'error', error: error.message });
    }
  }

  async downloadSong(song) {
    console.log(`Downloading: ${song.title} from ${song.folderPath.join('/')}`);
    
    window.location.href = song.url;
    await this._sleep(2000);
    
    const downloadButton = document.querySelector('button:has(svg.lucide-download)');
    if (!downloadButton) {
      throw new Error('Download button not found');
    }
    
    downloadButton.click();
    await this._sleep(500);
    
    const menuItems = document.querySelectorAll('[role="menuitem"], [role="option"], button');
    for (const item of menuItems) {
      if (item.textContent.toLowerCase().includes('mp3')) {
        item.click();
        await this._sleep(500);
        break;
      }
    }
  }

  _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
