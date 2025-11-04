// Persistent logging system for Udio Library Mapper
// Logs are saved to chrome.storage.local and can be exported

class ExtensionLogger {
  constructor(maxLogs = 1000) {
    this.maxLogs = maxLogs;
    this.sessionId = this.generateSessionId();
    this.logs = [];
    this.loadLogs();
  }
  
  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  async loadLogs() {
    try {
      const result = await chrome.storage.local.get(['extensionLogs']);
      if (result.extensionLogs) {
        this.logs = result.extensionLogs;
      }
    } catch (error) {
      console.error('Failed to load logs:', error);
    }
  }
  
  async saveLogs() {
    try {
      // Keep only the most recent logs
      if (this.logs.length > this.maxLogs) {
        this.logs = this.logs.slice(-this.maxLogs);
      }
      
      await chrome.storage.local.set({ extensionLogs: this.logs });
    } catch (error) {
      console.error('Failed to save logs:', error);
    }
  }
  
  log(level, message, data = null) {
    const entry = {
      timestamp: new Date().toISOString(),
      sessionId: this.sessionId,
      level: level,
      message: message,
      data: data,
      url: window.location?.href || 'unknown'
    };
    
    this.logs.push(entry);
    
    // Console output with color
    const colors = {
      debug: 'color: #888',
      info: 'color: #0066cc',
      success: 'color: #00aa00',
      warning: 'color: #ff8800',
      error: 'color: #cc0000'
    };
    
    console.log(
      `%c[${level.toUpperCase()}] ${message}`,
      colors[level] || '',
      data || ''
    );
    
    // Save to storage (debounced)
    this.debouncedSave();
  }
  
  debouncedSave = this.debounce(() => this.saveLogs(), 1000);
  
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
  
  debug(message, data) {
    this.log('debug', message, data);
  }
  
  info(message, data) {
    this.log('info', message, data);
  }
  
  success(message, data) {
    this.log('success', message, data);
  }
  
  warning(message, data) {
    this.log('warning', message, data);
  }
  
  error(message, data) {
    this.log('error', message, data);
  }
  
  async exportLogs() {
    const logsText = this.logs.map(entry => {
      let line = `[${entry.timestamp}] [${entry.level.toUpperCase()}] ${entry.message}`;
      if (entry.data) {
        line += `\n  Data: ${JSON.stringify(entry.data, null, 2)}`;
      }
      line += `\n  URL: ${entry.url}`;
      line += `\n  Session: ${entry.sessionId}`;
      return line;
    }).join('\n\n');
    
    return logsText;
  }
  
  async clearLogs() {
    this.logs = [];
    await chrome.storage.local.remove('extensionLogs');
    this.info('Logs cleared');
  }
  
  async getStats() {
    const stats = {
      totalLogs: this.logs.length,
      sessionId: this.sessionId,
      byLevel: {},
      oldestLog: this.logs[0]?.timestamp,
      newestLog: this.logs[this.logs.length - 1]?.timestamp
    };
    
    this.logs.forEach(log => {
      stats.byLevel[log.level] = (stats.byLevel[log.level] || 0) + 1;
    });
    
    return stats;
  }
  
  // Get logs for current session only
  getSessionLogs() {
    return this.logs.filter(log => log.sessionId === this.sessionId);
  }
  
  // Get logs by level
  getLogsByLevel(level) {
    return this.logs.filter(log => log.level === level);
  }
  
  // Get recent logs
  getRecentLogs(count = 50) {
    return this.logs.slice(-count);
  }
}

// Create global logger instance
const logger = new ExtensionLogger();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = logger;
}
