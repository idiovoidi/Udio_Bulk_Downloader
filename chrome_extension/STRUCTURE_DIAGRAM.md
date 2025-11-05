# Visual Structure Diagrams

## Extension Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CHROME EXTENSION                              │
│                  Udio Library Mapper v2.0                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐     ┌──────────────┐
│   POPUP UI   │      │  BACKGROUND  │     │   CONTENT    │
│              │      │   WORKER     │     │   SCRIPT     │
│ popup.html   │      │              │     │              │
│ popup-main.js│◄────►│background.js │◄───►│content-main  │
└──────┬───────┘      └──────────────┘     └──────┬───────┘
       │                                           │
       │                                           │
       ▼                                           ▼
┌──────────────┐                          ┌──────────────┐
│    POPUP     │                          │   MESSAGE    │
│  CONTROLLER  │                          │   HANDLER    │
└──────┬───────┘                          └──────┬───────┘
       │                                           │
       │                                           │
       ├───────────────────┬───────────────────────┤
       │                   │                       │
       ▼                   ▼                       ▼
┌──────────────┐    ┌──────────────┐      ┌──────────────┐
│      UI      │    │   EXPORT     │      │    FOLDER    │
│  CONTROLLER  │    │   UTILS      │      │    MAPPER    │
└──────────────┘    └──────────────┘      └──────┬───────┘
                                                  │
                    ┌─────────────────────────────┤
                    │                             │
                    ▼                             ▼
            ┌──────────────┐            ┌──────────────┐
            │     SONG     │            │  DIAGNOSTICS │
            │  EXTRACTOR   │            └──────────────┘
            └──────┬───────┘
                   │
                   ▼
            ┌──────────────┐
            │  DOM UTILS   │
            └──────────────┘
                   │
                   ▼
            ┌──────────────┐
            │   STORAGE    │
            └──────────────┘
```

## Module Dependency Graph

```
                    ┌─────────────┐
                    │   logger.js │
                    │  (Global)   │
                    └──────┬──────┘
                           │
                           │ Used by all modules
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   storage.js │   │ dom-utils.js │   │ui-controller │
│              │   │              │   │     .js      │
└──────┬───────┘   └──────┬───────┘   └──────────────┘
       │                  │
       │                  │
       │                  ▼
       │          ┌──────────────┐
       │          │song-extractor│
       │          │     .js      │
       │          └──────┬───────┘
       │                 │
       │                 │
       ▼                 ▼
┌──────────────────────────────┐
│     folder-mapper.js         │
│  (Uses storage + extractor)  │
└──────────────┬───────────────┘
               │
               │
               ▼
┌──────────────────────────────┐
│    message-handler.js        │
│  (Routes to folder-mapper)   │
└──────────────┬───────────────┘
               │
               │
               ▼
┌──────────────────────────────┐
│      content-main.js         │
│     (Entry Point)            │
└──────────────────────────────┘


┌──────────────┐
│export-utils  │
│    .js       │
└──────┬───────┘
       │
       │
       ▼
┌──────────────────────────────┐
│   popup-controller.js        │
│ (Uses UI + Export + Storage) │
└──────────────┬───────────────┘
               │
               │
               ▼
┌──────────────────────────────┐
│      popup-main.js           │
│     (Entry Point)            │
└──────────────────────────────┘
```

## Data Flow: Mapping Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  USER CLICKS "MAP LIBRARY" BUTTON                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  popup-controller.js                                         │
│  • Validates tab is on udio.com                             │
│  • Updates UI status                                         │
│  • Shows progress bar                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ chrome.tabs.sendMessage
                         │ { action: 'startMapping' }
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  message-handler.js (Content Script)                        │
│  • Receives message                                          │
│  • Routes to folder-mapper                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  folder-mapper.js                                            │
│  • Finds folder tree container                              │
│  • Counts top-level folders                                  │
│  • Extracts root songs                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ For each folder...
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  folder-mapper.js → _processFolderItem()                    │
│  • Clicks folder to expand                                   │
│  • Waits for DOM update                                      │
│  • Processes subfolders recursively                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ For leaf folders...
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  song-extractor.js → extractSongsFromView()                 │
│  • Scrolls page to load all songs                           │
│  • Extracts song data from DOM                              │
│  • Parses metadata (title, duration, tags, likes)          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ After each folder...
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  storage.js → saveContentState()                            │
│  • Saves progress to chrome.storage.local                   │
│  • Enables resume on page refresh                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ chrome.runtime.sendMessage
                         │ { action: 'progressUpdate' }
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  popup-controller.js                                         │
│  • Receives progress update                                  │
│  • Updates progress bar                                      │
│  • Updates status message                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Repeat until all folders mapped...
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  folder-mapper.js                                            │
│  • Sends completion message                                  │
│  • Returns final structure                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ chrome.runtime.sendMessage
                         │ { action: 'mappingComplete' }
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  popup-controller.js                                         │
│  • Receives completion message                              │
│  • Stores library data                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  ui-controller.js → displayResults()                        │
│  • Formats results HTML                                      │
│  • Shows folder/song counts                                  │
│  • Enables export buttons                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  USER SEES RESULTS                                           │
│  • Total folders: X                                          │
│  • Total songs: Y                                            │
│  • Export buttons enabled                                    │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow: Export Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  USER CLICKS "EXPORT CHECKLIST" BUTTON                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  popup-controller.js → exportChecklist()                    │
│  • Validates library data exists                            │
│  • Calls export utility                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  export-utils.js → exportChecklist()                        │
│  • Builds checklist header                                   │
│  • Collects all songs from folders                          │
│  • Groups songs by folder path                              │
│  • Formats as printable checklist                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  export-utils.js                                             │
│  • Creates Blob from text                                    │
│  • Generates filename with timestamp                         │
│  • Triggers chrome.downloads.download                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  FILE DOWNLOADED TO USER'S COMPUTER                          │
│  udio_song_checklist_2024-11-05.txt                         │
└─────────────────────────────────────────────────────────────┘
```

## Module Interaction Matrix

```
                    │ storage │ dom-utils │ song-ext │ folder-map │ export │ ui-ctrl │
────────────────────┼─────────┼───────────┼──────────┼────────────┼────────┼─────────┤
folder-mapper.js    │    ✓    │     ✓     │    ✓     │     -      │   -    │    -    │
song-extractor.js   │    -    │     ✓     │    -     │     -      │   -    │    -    │
export-utils.js     │    -    │     -     │    -     │     -      │   -    │    -    │
ui-controller.js    │    -    │     -     │    -     │     -      │   -    │    -    │
popup-controller.js │    ✓    │     -     │    -     │     -      │   ✓    │    ✓    │
message-handler.js  │    -    │     -     │    -     │     ✓      │   -    │    -    │
content-main.js     │    ✓    │     -     │    -     │     ✓      │   -    │    -    │
diagnostics.js      │    -    │     ✓     │    -     │     -      │   -    │    -    │

Legend:
✓ = Direct dependency
- = No dependency
```

## File Size Breakdown

```
Modules (710 lines)
├── folder-mapper.js    ████████████████ 150 lines (21%)
├── export-utils.js     ██████████████   200 lines (28%)
├── song-extractor.js   █████████        120 lines (17%)
├── ui-controller.js    ███████          100 lines (14%)
├── storage.js          ██████            80 lines (11%)
└── dom-utils.js        ████              60 lines (8%)

Content (210 lines)
├── diagnostics.js      ███████████      100 lines (48%)
├── message-handler.js  ████████          70 lines (33%)
└── content-main.js     ████              40 lines (19%)

Popup (230 lines)
├── popup-controller.js ████████████████ 200 lines (87%)
└── popup-main.js       ███               30 lines (13%)

Total: 1,150 lines across 11 modules
Average: 105 lines per module
```

## Complexity Comparison

```
Before (Monolithic)
┌────────────────────────────────────────┐
│  popup.js                              │
│  ████████████████████████████████████  │
│  700 lines - HIGH COMPLEXITY           │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  content_v3.js                         │
│  ██████████████████████████████████    │
│  600 lines - HIGH COMPLEXITY           │
└────────────────────────────────────────┘

After (Modular)
┌──────────────────┐ ┌──────────────────┐
│ popup-controller │ │ export-utils     │
│ ████████████     │ │ ██████████████   │
│ 200 lines - MED  │ │ 200 lines - MED  │
└──────────────────┘ └──────────────────┘

┌──────────────────┐ ┌──────────────────┐
│ folder-mapper    │ │ song-extractor   │
│ ████████████     │ │ ██████████       │
│ 150 lines - MED  │ │ 120 lines - LOW  │
└──────────────────┘ └──────────────────┘

┌──────────────────┐ ┌──────────────────┐
│ ui-controller    │ │ diagnostics      │
│ ████████         │ │ ████████         │
│ 100 lines - LOW  │ │ 100 lines - LOW  │
└──────────────────┘ └──────────────────┘

+ 5 more small modules (30-80 lines each)
```

## Communication Patterns

```
┌─────────────┐                    ┌─────────────┐
│   POPUP     │                    │   CONTENT   │
│             │                    │             │
│  ┌────────┐ │                    │ ┌────────┐  │
│  │ Main   │ │                    │ │ Main   │  │
│  └───┬────┘ │                    │ └───┬────┘  │
│      │      │                    │     │       │
│      ▼      │                    │     ▼       │
│  ┌────────┐ │  sendMessage()     │ ┌────────┐  │
│  │Control │ ├───────────────────►│ │Handler │  │
│  │  ler   │ │                    │ │        │  │
│  └───┬────┘ │                    │ └───┬────┘  │
│      │      │                    │     │       │
│      │      │  sendMessage()     │     ▼       │
│      │      │◄───────────────────┤ ┌────────┐  │
│      │      │  (progress)        │ │ Mapper │  │
│      │      │                    │ └────────┘  │
│      ▼      │                    │             │
│  ┌────────┐ │                    │             │
│  │   UI   │ │                    │             │
│  └────────┘ │                    │             │
└─────────────┘                    └─────────────┘

Message Types:
→ startMapping, getProgress, dumpStructure
← progressUpdate, mappingComplete, mappingError
```

## State Management

```
┌─────────────────────────────────────────────────────────┐
│              chrome.storage.local                        │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
             ▼                            ▼
┌────────────────────────┐   ┌────────────────────────┐
│   mappingState         │   │  contentMappingState   │
│   (Popup)              │   │  (Content Script)      │
│                        │   │                        │
│  • inProgress          │   │  • inProgress          │
│  • percent             │   │  • structure           │
│  • mappedFolders       │   │    - folders[]         │
│  • totalFolders        │   │    - totalSongs        │
│  • totalSongs          │   │    - mappedFolders     │
│  • tabId               │   │  • timestamp           │
└────────────────────────┘   └────────────────────────┘
             │                            │
             │                            │
             ▼                            ▼
┌────────────────────────┐   ┌────────────────────────┐
│  popup-controller.js   │   │  folder-mapper.js      │
│  Restores on open      │   │  Restores on reload    │
└────────────────────────┘   └────────────────────────┘
```

---

**Legend:**
- ✓ = Has dependency
- → = Sends message
- ← = Receives message
- ▼ = Calls/Uses
- ◄ = Returns to
