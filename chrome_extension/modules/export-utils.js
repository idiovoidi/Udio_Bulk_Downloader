// Export utilities for different formats
export class ExportUtils {
  static exportAsJson(libraryData) {
    const dataStr = JSON.stringify(libraryData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const timestamp = this._getTimestamp();
    const filename = `udio_library_${timestamp}.json`;
    
    chrome.downloads.download({ url, filename, saveAs: true });
  }

  static exportAsText(libraryData) {
    let text = this._buildTextHeader(libraryData);
    text += this._buildTextSummary(libraryData);
    text += this._buildFolderStructure(libraryData);
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const timestamp = this._getTimestamp();
    const filename = `udio_library_hierarchical_${timestamp}.txt`;
    
    chrome.downloads.download({ url, filename, saveAs: true });
  }

  static exportChecklist(libraryData) {
    let text = this._buildChecklistHeader(libraryData);
    
    const { allSongs, rootSongs } = this._collectAllSongs(libraryData);
    
    if (rootSongs.length > 0) {
      text += this._buildRootSongsSection(rootSongs);
    }
    
    text += this._buildFolderSongsSection(allSongs);
    text += this._buildChecklistSummary(rootSongs, allSongs);
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const timestamp = this._getTimestamp();
    const filename = `udio_song_checklist_${timestamp}.txt`;
    
    chrome.downloads.download({ url, filename, saveAs: true });
  }

  static _getTimestamp() {
    return new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  }

  static _buildTextHeader(data) {
    return `UDIO LIBRARY STRUCTURE (HIERARCHICAL)\n${'='.repeat(50)}\n\n` +
           `Mapped: ${new Date().toLocaleString()}\n` +
           `Page: ${data.pageUrl}\n` +
           `Type: ${data.pageType}\n\n`;
  }

  static _buildTextSummary(data) {
    const totalFolders = data.totalFolders || data.folders?.length || 0;
    const totalSongs = data.totalSongs || data.songs?.length || 0;
    
    return `SUMMARY\n${'-'.repeat(50)}\n` +
           `Total Folders: ${totalFolders}\n` +
           `Total Songs: ${totalSongs}\n\n`;
  }

  static _buildFolderStructure(data) {
    const rootFolders = data.rootFolders || data.folders || [];
    if (rootFolders.length === 0) return '';
    
    let text = `FOLDER STRUCTURE\n${'-'.repeat(50)}\n`;
    rootFolders.forEach((folder, i) => {
      text += this._formatFolderHierarchy(folder, 0, `${i + 1}.`);
    });
    return text + '\n';
  }

  static _formatFolderHierarchy(folder, depth, prefix) {
    const indent = '  '.repeat(depth);
    let text = `${indent}${prefix} ${folder.name || 'Unnamed'}`;
    
    const songCount = folder.songs?.length || folder.songCount || 0;
    const subfolderCount = folder.subfolders?.length || 0;
    
    if (songCount > 0) text += ` (${songCount} songs)`;
    if (subfolderCount > 0) text += ` (${subfolderCount} subfolders)`;
    text += '\n';
    
    if (folder.songs?.length > 0) {
      folder.songs.forEach(song => {
        text += `${indent}  • ${song.title || 'Untitled'}`;
        if (song.artist) text += ` - ${song.artist}`;
        if (song.duration) text += ` [${song.duration}]`;
        text += '\n';
      });
    }
    
    if (folder.subfolders?.length > 0) {
      folder.subfolders.forEach((subfolder, i) => {
        text += this._formatFolderHierarchy(subfolder, depth + 1, `${prefix}${i + 1}`);
      });
    }
    
    return text;
  }

  static _buildChecklistHeader(data) {
    const totalSubfolders = this._countTotalSubfolders(data.folders || []);
    
    return '═'.repeat(59) + '\n' +
           '           UDIO LIBRARY - COMPLETE SONG CHECKLIST\n' +
           '═'.repeat(59) + '\n\n' +
           `Generated: ${new Date().toLocaleString()}\n` +
           `Total Folders: ${data.totalFolders || 0}\n` +
           `Total Subfolders: ${totalSubfolders}\n` +
           `Total Songs: ${data.totalSongs || 0}\n\n`;
  }

  static _collectAllSongs(data) {
    const allSongs = [];
    const rootSongs = data.songs || [];
    
    const collectSongs = (folders, path = []) => {
      folders.forEach(folder => {
        const folderPath = [...path, folder.name];
        
        if (folder.songs?.length > 0) {
          folder.songs.forEach(song => {
            allSongs.push({
              ...song,
              folderPath,
              pathString: folderPath.join(' > ')
            });
          });
        }
        
        if (folder.subfolders?.length > 0) {
          collectSongs(folder.subfolders, folderPath);
        }
      });
    };
    
    collectSongs(data.folders || data.rootFolders || []);
    
    return { allSongs, rootSongs };
  }

  static _buildRootSongsSection(rootSongs) {
    let text = '═'.repeat(59) + '\n' +
               '                    ROOT DIRECTORY\n' +
               '                  (Songs not in folders)\n' +
               '═'.repeat(59) + '\n\n';
    
    rootSongs.forEach((song, i) => {
      text += this._formatSongChecklistItem(song, i);
    });
    
    return text + `Root Songs: ${rootSongs.length}\n\n`;
  }

  static _buildFolderSongsSection(allSongs) {
    const songsByFolder = {};
    allSongs.forEach(song => {
      const path = song.pathString;
      if (!songsByFolder[path]) songsByFolder[path] = [];
      songsByFolder[path].push(song);
    });
    
    const sortedFolders = Object.keys(songsByFolder).sort();
    let text = '';
    
    sortedFolders.forEach(folderPath => {
      const songs = songsByFolder[folderPath];
      text += '═'.repeat(59) + '\n' +
              `📁 ${folderPath}\n` +
              '═'.repeat(59) + '\n\n';
      
      songs.forEach((song, i) => {
        text += this._formatSongChecklistItem(song, i);
      });
      
      text += `Songs in this folder: ${songs.length}\n\n`;
    });
    
    return text;
  }

  static _formatSongChecklistItem(song, index) {
    const likedIcon = song.isLiked ? '👍 ' : song.isDisliked ? '👎 ' : '';
    let text = `[ ] ${index + 1}. ${likedIcon}${song.title || 'Untitled'}\n`;
    
    if (song.url) text += `    URL: ${song.url}\n`;
    if (song.duration) text += `    Duration: ${song.duration}\n`;
    if (song.isLiked) text += `    ⭐ LIKED\n`;
    if (song.isDisliked) text += `    ⛔ DISLIKED\n`;
    if (song.tags?.length > 0) text += `    Tags: ${song.tags.join(', ')}\n`;
    
    return text + '\n';
  }

  static _buildChecklistSummary(rootSongs, allSongs) {
    const allSongsArray = [...rootSongs, ...allSongs];
    const likedCount = allSongsArray.filter(s => s.isLiked).length;
    const dislikedCount = allSongsArray.filter(s => s.isDisliked).length;
    
    return '═'.repeat(59) + '\n' +
           '                         SUMMARY\n' +
           '═'.repeat(59) + '\n\n' +
           `Root Songs: ${rootSongs.length}\n` +
           `Songs in Folders: ${allSongs.length}\n` +
           `TOTAL SONGS: ${rootSongs.length + allSongs.length}\n` +
           `Liked Songs: ${likedCount} 👍\n` +
           `Disliked Songs: ${dislikedCount} 👎\n\n` +
           'INSTRUCTIONS:\n' +
           '1. Print this checklist or keep it open\n' +
           '2. Mark [ ] with [X] as you download each song\n' +
           '3. Use the URLs to navigate to each song\n' +
           '4. Click Download → MP3 for each song\n' +
           '5. Organize downloaded files into matching folder structure\n\n' +
           'TIP: You can search this file (Ctrl+F) to find specific songs!\n';
  }

  static _countTotalSubfolders(folders) {
    let count = 0;
    folders.forEach(folder => {
      if (folder.subfolders?.length > 0) {
        count += folder.subfolders.length;
        count += this._countTotalSubfolders(folder.subfolders);
      }
    });
    return count;
  }
}
