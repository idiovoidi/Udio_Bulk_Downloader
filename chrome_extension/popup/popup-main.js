// Main popup entry point
import { PopupController } from './popup-controller.js';

// DOM elements
const elements = {
  status: document.getElementById('status'),
  mapButton: document.getElementById('mapLibrary'),
  exportChecklist: document.getElementById('exportChecklist'),
  downloadButton: document.getElementById('downloadAll'),
  exportJson: document.getElementById('exportJson'),
  exportText: document.getElementById('exportText'),
  progress: document.getElementById('progress'),
  progressFill: document.getElementById('progressFill'),
  progressText: document.getElementById('progressText'),
  results: document.getElementById('results'),
  resultsContent: document.getElementById('resultsContent'),
  dumpButton: document.getElementById('dumpStructure'),
  viewLogs: document.getElementById('viewLogs'),
  exportLogs: document.getElementById('exportLogs'),
  clearLogs: document.getElementById('clearLogs'),
  logsView: document.getElementById('logsView'),
  logsContent: document.getElementById('logsContent'),
  logStats: document.getElementById('logStats')
};

// Initialize controller
const controller = new PopupController(elements);
controller.initialize();

// Listen for messages from background/content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'mappingComplete') {
    console.log('Mapping complete!', message.structure);
  } else if (message.action === 'mappingError') {
    controller.ui.updateStatus(`Error: ${message.error}`, 'error');
    controller.ui.hideProgress();
    controller.ui.setButtonState(elements.mapButton, false);
  } else if (message.action === 'progressUpdate') {
    console.log('Progress update:', message.progress);
  }
});
