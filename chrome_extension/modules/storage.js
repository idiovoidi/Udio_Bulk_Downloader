// Storage management module for persistent state
export class StorageManager {
  constructor() {
    this.keys = {
      MAPPING_STATE: 'mappingState',
      CONTENT_STATE: 'contentMappingState',
      LOGS: 'extensionLogs'
    };
  }

  async saveMappingState(state) {
    await chrome.storage.local.set({ [this.keys.MAPPING_STATE]: state });
  }

  async loadMappingState() {
    const result = await chrome.storage.local.get([this.keys.MAPPING_STATE]);
    return result[this.keys.MAPPING_STATE] || null;
  }

  async clearMappingState() {
    await chrome.storage.local.remove(this.keys.MAPPING_STATE);
  }

  async saveContentState(state) {
    await chrome.storage.local.set({
      [this.keys.CONTENT_STATE]: {
        ...state,
        timestamp: Date.now()
      }
    });
  }

  async loadContentState() {
    const result = await chrome.storage.local.get([this.keys.CONTENT_STATE]);
    return result[this.keys.CONTENT_STATE] || null;
  }

  async clearContentState() {
    await chrome.storage.local.remove(this.keys.CONTENT_STATE);
  }

  async saveLogs(logs) {
    await chrome.storage.local.set({ [this.keys.LOGS]: logs });
  }

  async loadLogs() {
    const result = await chrome.storage.local.get([this.keys.LOGS]);
    return result[this.keys.LOGS] || [];
  }

  async clearLogs() {
    await chrome.storage.local.remove(this.keys.LOGS);
  }
}
