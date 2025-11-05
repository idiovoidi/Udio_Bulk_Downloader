// Popup controller logic
import { StorageManager } from '../modules/storage.js';
import { ExportUtils } from '../modules/export-utils.js';
import { UIController } from '../modules/ui-controller.js';

export class PopupController {
  constructor(elements) {
    this.storage = new StorageManager();
    this.ui = new UIController(elements);
    this.libraryData = null;
    this.currentTabId = null;
  }

  async initialize() {
    await this.checkCurrentTab();
    await this.restoreState();
    this.setupEventListeners();
  }

  async checkCurrentTab() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab?.url?.includes('udio.com')) {
      this.ui.updateStatus('Please navigate to Udio.com', 'warning');
      this.ui.setButtonState(this.ui.elements.mapButton, true);
      return;
    }
    
    this.currentTabId = tab.id;
    
    try {
      const response = await chrome.tabs.sendMessage(tab.id, { action: 'ping' });
      if (response) {
        const state = await this.storage.loadMappingState();
        if (state?.inProgress) {
          this.ui.updateStatus(`Mapping in progress... (${state.mappedFolders}/${state.totalFolders} folders)`, 'info');
          this.ui.updateProgress(state.percent, `Mapping: ${state.mappedFolders}/${state.totalFolders} folders`);
          this.ui.setButtonState(this.ui.elements.mapButton, true);
          this.startProgressPolling(tab.id);
        } else {
          this.ui.updateStatus('Ready to map! Open folder tree panel first.', 'info');
        }
      }
    } catch (error) {
      this.ui.updateStatus('⚠️ Please REFRESH the page (F5) to load the extension', 'warning');
    }
  }

  async restoreState() {
    const state = await this.storage.loadMappingState();
    
    if (state?.inProgress && this.currentTabId) {
      this.ui.updateStatus(`Mapping in progress... (${state.mappedFolders}/${state.totalFolders} folders)`, 'info');
      this.ui.updateProgress(state.percent, `Mapping: ${state.mappedFolders}/${state.totalFolders} folders`);
      this.ui.setButtonState(this.ui.elements.mapButton, true);
      this.startProgressPolling(this.currentTabId);
    }
  }

  setupEventListeners() {
    this.ui.elements.mapButton.addEventListener('click', () => this.mapLibrary());
    this.ui.elements.dumpButton.addEventListener('click', () => this.dumpStructure());
    this.ui.elements.exportChecklist.addEventListener('click', () => this.exportChecklist());
    this.ui.elements.downloadButton.addEventListener('click', () => this.downloadAll());
    this.ui.elements.exportJson.addEventListener('click', () => this.exportJson());
    this.ui.elements.exportText.addEventListener('click', () => this.exportText());
    this.ui.elements.viewLogs.addEventListener('click', () => this.toggleLogs());
    this.ui.elements.exportLogs.addEventListener('click', () => this.exportLogs());
    this.ui.elements.clearLogs.addEventListener('click', () => this.clearLogs());
  }

  async mapLibrary() {
    try {
      this.ui.updateStatus('Starting mapping... Make sure folder tree is open!', 'info');
      this.ui.updateProgress(5, 'Connecting to page...');
      this.ui.setButtonState(this.ui.elements.mapButton, true);
      
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (!tab.url.includes('udio.com')) {
        this.ui.updateStatus('Please navigate to Udio.com first', 'error');
        this.ui.setButtonState(this.ui.elements.mapButton, false);
        this.ui.hideProgress();
        return;
      }
      
      this.ui.updateProgress(10, 'Starting folder tree mapping...');
      
      const response = await chrome.tabs.sendMessage(tab.id, { action: 'startMapping' });
      
      if (response?.status === 'started') {
        this.ui.updateStatus('Mapping in progress...', 'info');
        this.startProgressPolling(tab.id);
      } else {
        this.ui.updateStatus('Failed to start mapping', 'error');
        this.ui.hideProgress();
        this.ui.setButtonState(this.ui.elements.mapButton, false);
      }
    } catch (error) {
      if (error.message.includes('Receiving end does not exist')) {
        this.ui.updateStatus('⚠️ Please REFRESH the Udio page (F5) and try again', 'error');
      } else {
        this.ui.updateStatus(`Error: ${error.message}`, 'error');
      }
      this.ui.hideProgress();
      this.ui.setButtonState(this.ui.elements.mapButton, false);
    }
  }

  startProgressPolling(tabId) {
    this.ui.startPolling(async () => {
      chrome.tabs.sendMessage(tabId, { action: 'getProgress' }, async (response) => {
        if (chrome.runtime.lastError) {
          this.ui.stopPolling();
          this.ui.updateStatus('Connection lost', 'error');
          this.ui.hideProgress();
          this.ui.setButtonState(this.ui.elements.mapButton, false);
          await this.storage.clearMappingState();
          return;
        }
        
        if (response) {
          if (response.inProgress) {
            const structure = response.structure;
            const percent = structure.totalFolders > 0 
              ? Math.round((structure.mappedFolders / structure.totalFolders) * 100) 
              : 10;
            
            this.ui.updateProgress(percent, `Mapping: ${structure.mappedFolders}/${structure.totalFolders} folders`);
            this.ui.updateStatus(`Found ${structure.totalSongs} songs so far...`, 'info');
            
            await this.storage.saveMappingState({
              inProgress: true,
              percent,
              mappedFolders: structure.mappedFolders,
              totalFolders: structure.totalFolders,
              totalSongs: structure.totalSongs,
              tabId
            });
          } else {
            this.handleMappingComplete(response.structure);
          }
        }
      });
    });
  }

  async handleMappingComplete(structure) {
    this.ui.stopPolling();
    this.ui.updateProgress(100, 'Complete!');
    this.ui.updateStatus(`Mapping complete! ${structure.totalFolders} folders, ${structure.totalSongs} songs`, 'success');
    
    const displayData = {
      folders: structure.folders,
      rootFolders: structure.folders,
      totalFolders: structure.totalFolders,
      totalSongs: structure.totalSongs,
      pageType: 'library',
      pageUrl: 'udio.com/library',
      timestamp: new Date().toISOString()
    };
    
    this.libraryData = displayData;
    this.ui.displayResults(displayData);
    this.ui.hideProgress();
    this.ui.setButtonState(this.ui.elements.mapButton, false);
    this.ui.setButtonState(this.ui.elements.exportChecklist, false);
    this.ui.setButtonState(this.ui.elements.downloadButton, false);
    
    await this.storage.clearMappingState();
  }

  async dumpStructure() {
    try {
      this.ui.updateStatus('Dumping tree structure... Check console!', 'info');
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      await chrome.tabs.sendMessage(tab.id, { action: 'dumpStructure' });
      this.ui.updateStatus('✓ Tree structure dumped to console (F12)', 'success');
    } catch (error) {
      this.ui.updateStatus(`Error: ${error.message}`, 'error');
    }
  }

  exportJson() {
    if (!this.libraryData) return;
    ExportUtils.exportAsJson(this.libraryData);
    this.ui.updateStatus('JSON export started', 'success');
  }

  exportText() {
    if (!this.libraryData) return;
    ExportUtils.exportAsText(this.libraryData);
    this.ui.updateStatus('Text export started', 'success');
  }

  exportChecklist() {
    if (!this.libraryData) return;
    ExportUtils.exportChecklist(this.libraryData);
    this.ui.updateStatus(`✓ Checklist exported!`, 'success');
  }

  async downloadAll() {
    if (!this.libraryData?.folders) {
      this.ui.updateStatus('Please map the library first', 'error');
      return;
    }
    
    this.ui.updateStatus('Preparing download...', 'info');
    this.ui.setButtonState(this.ui.elements.downloadButton, true);
    
    // Implementation would go here
    this.ui.updateStatus('Download list feature - see documentation', 'warning');
    this.ui.setButtonState(this.ui.elements.downloadButton, false);
  }

  async toggleLogs() {
    if (this.ui.toggleLogs()) {
      const stats = await logger.getStats();
      const recentLogs = logger.getRecentLogs(100);
      this.ui.showLogs(recentLogs, stats);
    } else {
      this.ui.hideLogs();
    }
  }

  async exportLogs() {
    const logsText = await logger.exportLogs();
    const stats = await logger.getStats();
    
    const header = `UDIO LIBRARY MAPPER - DEBUG LOGS\n`;
    const separator = '='.repeat(60) + '\n';
    const statsText = `Total Logs: ${stats.totalLogs}\n` +
                     `Session ID: ${stats.sessionId}\n` +
                     `Oldest: ${stats.oldestLog}\n` +
                     `Newest: ${stats.newestLog}\n` +
                     `By Level: ${JSON.stringify(stats.byLevel, null, 2)}\n\n`;
    
    const fullText = header + separator + statsText + separator + '\n' + logsText;
    
    const blob = new Blob([fullText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const filename = `udio_mapper_logs_${timestamp}.txt`;
    
    chrome.downloads.download({ url, filename, saveAs: true });
    
    this.ui.updateStatus('Logs exported successfully', 'success');
  }

  async clearLogs() {
    if (confirm('Are you sure you want to clear all logs?')) {
      await logger.clearLogs();
      this.ui.updateStatus('Logs cleared', 'success');
      if (!this.ui.toggleLogs()) {
        this.ui.hideLogs();
      }
    }
  }
}
