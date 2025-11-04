# Debug Logging System

The Udio Library Mapper extension now includes a comprehensive logging system to help with debugging and preserving findings even if the mapping process fails.

## Features

### Persistent Logs
- All logs are automatically saved to Chrome's local storage
- Logs persist across browser sessions
- Maximum of 1000 most recent logs kept (configurable)

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **SUCCESS**: Successful operations
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages with stack traces

### What Gets Logged

The extension automatically logs:
- Extension initialization
- Page navigation and detection
- Folder tree discovery
- Each folder being processed
- Songs found in each folder
- Progress updates
- Completion status
- Any errors with full details

## Using the Logs

### View Logs in Extension
1. Click the extension icon
2. Click "📋 View Debug Logs"
3. See the most recent 100 log entries
4. Click again to hide

### Export Logs
1. Click "💾 Export Logs" button
2. Saves a timestamped text file with:
   - Complete log history
   - Statistics (total logs, by level)
   - Session information
   - Timestamps and URLs

### Clear Logs
1. Click "🗑️ Clear Logs" button
2. Confirms before clearing
3. Removes all stored logs

## Log File Format

Exported logs include:
```
[2024-11-05 14:30:15] [INFO] Starting folder tree mapping
  URL: https://www.udio.com/library
  Session: session_1730826615_abc123

[2024-11-05 14:30:16] [SUCCESS] Found folder tree panel
  URL: https://www.udio.com/library
  Session: session_1730826615_abc123

[2024-11-05 14:30:17] [INFO] Found 5 top-level folders
  URL: https://www.udio.com/library
  Session: session_1730826615_abc123
```

## Benefits

### Debugging
- See exactly what happened during mapping
- Identify where failures occurred
- Track progress through complex operations

### Preservation
- Even if mapping fails, logs are saved
- Can review what was found before failure
- Export logs to share with developers

### Analysis
- Review mapping patterns
- Identify performance issues
- Track success rates

## Console Output

Logs are also output to the browser console with color coding:
- Debug: Gray
- Info: Blue
- Success: Green
- Warning: Orange
- Error: Red

Open DevTools (F12) to see real-time console output while mapping.

## Storage

Logs are stored in:
- `chrome.storage.local` under key `extensionLogs`
- Automatically managed (old logs removed when limit reached)
- Survives browser restarts
- Cleared only when you explicitly clear them

## Tips

1. **Before mapping**: Clear old logs for a clean session
2. **During mapping**: Watch console for real-time feedback
3. **After mapping**: Export logs for your records
4. **If it fails**: Export logs immediately to preserve findings
5. **Troubleshooting**: Share exported logs when reporting issues

## Privacy

- Logs are stored locally only (never sent anywhere)
- Contains URLs and song/folder names from your library
- Export files may contain personal data
- Clear logs if sharing device with others
