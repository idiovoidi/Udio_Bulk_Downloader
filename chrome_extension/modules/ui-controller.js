// UI state management for popup
export class UIController {
  constructor(elements) {
    this.elements = elements;
    this.pollingInterval = null;
  }

  updateStatus(message, type = 'info') {
    this.elements.status.textContent = message;
    this.elements.status.className = `status ${type}`;
  }

  updateProgress(percent, text) {
    this.elements.progress.classList.add('active');
    this.elements.progressFill.style.width = `${percent}%`;
    this.elements.progressText.textContent = text;
  }

  hideProgress() {
    this.elements.progress.classList.remove('active');
  }

  displayResults(data) {
    const totalFolders = data.totalFolders || data.folders?.length || 0;
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
    
    const rootFolders = data.rootFolders || data.folders || [];
    if (rootFolders.length > 0) {
      html += '<h4>Root Folders:</h4><ul>';
      rootFolders.slice(0, 5).forEach(folder => {
        const subfolderCount = folder.subfolders?.length || 0;
        const songCount = folder.songs?.length || folder.songCount || 0;
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
    
    this.elements.resultsContent.innerHTML = html;
    this.elements.results.style.display = 'block';
    
    this.enableExportButtons();
  }

  enableExportButtons() {
    this.elements.exportJson.disabled = false;
    this.elements.exportText.disabled = false;
  }

  setButtonState(button, disabled) {
    button.disabled = disabled;
  }

  startPolling(callback, interval = 500) {
    this.stopPolling();
    this.pollingInterval = setInterval(callback, interval);
  }

  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }

  showLogs(logs, stats) {
    this.elements.logStats.textContent = `(${stats.totalLogs} total, showing last 100)`;
    this.elements.logsContent.textContent = logs.map(log => {
      const time = new Date(log.timestamp).toLocaleTimeString();
      return `[${time}] [${log.level.toUpperCase()}] ${log.message}${log.data ? '\n  ' + JSON.stringify(log.data) : ''}`;
    }).join('\n\n');
    
    this.elements.logsView.style.display = 'block';
    this.elements.viewLogs.textContent = '❌ Hide Logs';
  }

  hideLogs() {
    this.elements.logsView.style.display = 'none';
    this.elements.viewLogs.textContent = '📋 View Debug Logs';
  }

  toggleLogs() {
    return this.elements.logsView.style.display === 'none';
  }
}
