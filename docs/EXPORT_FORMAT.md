# Export format (extension → Python)

The only interface between `chrome_extension/` and `udio_downloader/`. Written by `exportMetadataWithIncrementalSupport` in `chrome_extension/content.js`, read by `udio_downloader/services/metadata_importer.py`.

```jsonc
{
  "exportVersion": "2.0",          // importer warns if it doesn't start with "2."
  "exportDate": "ISO-8601",
  "statistics": { "totalFolders": 0, "totalSongs": 0, "newSongs": 0, "changedSongs": 0, "unchangedSongs": 0 },
  "folders": [ { "id": "...", "path": ["Parent", "Child"] } ],
  "songs": [
    {
      "id": "...",                  // stable primary key
      "title": "", "artist": "", "duration": "", "createdDate": "",
      "folderId": "...",            // references folders[].id
      "isLiked": false, "isDisliked": false,
      "playCount": 0, "likesCount": 0,
      "lyricsAvailable": false,
      "metadataHash": "...",        // change detection, see below
      "metadataCollectedAt": "ISO-8601",
      "isNew": false, "isChanged": false
    }
  ],
  "tags": []                        // song <-> tag relationships
}
```

Transient URLs (song page, image) are deliberately not exported; the downloader gets fresh URLs from the song page at download time.

## Change detection

`metadataHash` is computed in the extension (`generateMetadataHash` in `content.js`). On import, a song is skipped when its hash equals the stored `metadata_hash`, and updated otherwise. If the hash is missing, Python computes one via `udio_downloader/utils/metadata_hash.py`. The two implementations should stay equivalent: if you change the fields that go into the hash on one side, change the other.

## Versioning

Bump `exportVersion` when the shape changes incompatibly, and update the importer in the same change.
