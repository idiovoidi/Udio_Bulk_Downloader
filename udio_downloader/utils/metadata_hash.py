"""
Metadata hash calculation for change detection.

This module provides a Python implementation of the same hash algorithm
used by the Chrome extension, allowing the Python code to calculate
metadata hashes independently without tight coupling to the extension.
"""

import json
from typing import Dict, Any, Optional, List


def calculate_metadata_hash(song_data: Dict[str, Any]) -> str:
    """
    Calculate metadata hash for a song.
    
    This implements the same algorithm as the Chrome extension's
    _generateMetadataHash() function to ensure consistency.
    
    The hash is based on:
    - title
    - artist
    - duration
    - isLiked/is_liked
    - isDisliked/is_disliked
    - plays/play_count
    - likes/likes_count
    - tags (sorted for consistency)
    - lyricsAvailable/lyrics_available
    
    Args:
        song_data: Dictionary containing song metadata.
                  Accepts both camelCase (from JSON) and snake_case (from DB) keys.
    
    Returns:
        Hash string in base-36 format
        
    Example:
        >>> song = {
        ...     'title': 'My Song',
        ...     'artist': 'Artist Name',
        ...     'duration': 180,
        ...     'isLiked': True,
        ...     'tags': ['rock', 'alternative']
        ... }
        >>> hash_value = calculate_metadata_hash(song)
        >>> isinstance(hash_value, str)
        True
    """
    # Normalize field names (support both camelCase and snake_case)
    hash_data = {
        'title': song_data.get('title'),
        'artist': song_data.get('artist'),
        'duration': song_data.get('duration') or song_data.get('duration_seconds'),
        'isLiked': song_data.get('isLiked') or song_data.get('is_liked', False),
        'isDisliked': song_data.get('isDisliked') or song_data.get('is_disliked', False),
        'plays': song_data.get('plays') or song_data.get('play_count', 0),
        'likes': song_data.get('likes') or song_data.get('likes_count', 0),
        'tags': _normalize_tags(song_data.get('tags')),
        'lyricsAvailable': song_data.get('lyricsAvailable') or song_data.get('lyrics_available', False)
    }
    
    # Convert to JSON string (matches JavaScript JSON.stringify behavior)
    hash_string = json.dumps(hash_data, separators=(',', ':'), sort_keys=True)
    
    # Calculate hash using same algorithm as Chrome extension
    return _simple_hash(hash_string)


def _normalize_tags(tags: Optional[Any]) -> Optional[str]:
    """
    Normalize tags to sorted comma-separated string.
    
    Args:
        tags: Tags as list, comma-separated string, or None
        
    Returns:
        Sorted comma-separated string or None
    """
    if not tags:
        return None
    
    if isinstance(tags, str):
        # Already a string, split and re-sort
        tag_list = [t.strip() for t in tags.split(',') if t.strip()]
    elif isinstance(tags, list):
        # List of tags
        tag_list = [str(t).strip() for t in tags if t]
    else:
        return None
    
    if not tag_list:
        return None
    
    # Sort for consistency (matches JavaScript .sort().join(','))
    return ','.join(sorted(tag_list))


def _simple_hash(string: str) -> str:
    """
    Simple hash function matching Chrome extension implementation.
    
    This implements the same algorithm as the JavaScript _simpleHash function:
    ```javascript
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash).toString(36);
    ```
    
    Args:
        string: String to hash
        
    Returns:
        Hash in base-36 format
    """
    hash_value = 0
    
    for char in string:
        char_code = ord(char)
        # JavaScript: ((hash << 5) - hash) + char
        hash_value = ((hash_value << 5) - hash_value) + char_code
        # Convert to 32-bit signed integer (JavaScript behavior)
        hash_value = _to_int32(hash_value)
    
    # Return absolute value in base-36
    return _to_base36(abs(hash_value))


def _to_int32(value: int) -> int:
    """
    Convert to 32-bit signed integer (matches JavaScript bitwise operations).
    
    JavaScript's bitwise operations convert numbers to 32-bit signed integers.
    This function replicates that behavior in Python.
    
    Args:
        value: Integer value
        
    Returns:
        32-bit signed integer
    """
    # Mask to 32 bits
    value = value & 0xFFFFFFFF
    
    # Convert to signed if necessary
    if value >= 0x80000000:
        value -= 0x100000000
    
    return value


def _to_base36(value: int) -> str:
    """
    Convert integer to base-36 string (matches JavaScript .toString(36)).
    
    Args:
        value: Integer value
        
    Returns:
        Base-36 string representation
    """
    if value == 0:
        return '0'
    
    digits = '0123456789abcdefghijklmnopqrstuvwxyz'
    result = []
    
    while value > 0:
        result.append(digits[value % 36])
        value //= 36
    
    return ''.join(reversed(result))


def validate_metadata_hash(song_data: Dict[str, Any], expected_hash: str) -> bool:
    """
    Validate that a song's metadata hash matches the expected value.
    
    Args:
        song_data: Song metadata dictionary
        expected_hash: Expected hash value
        
    Returns:
        True if hash matches, False otherwise
    """
    calculated_hash = calculate_metadata_hash(song_data)
    return calculated_hash == expected_hash


def recalculate_hash_if_missing(song_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recalculate metadata hash if missing from song data.
    
    This is useful when importing data that doesn't have a hash,
    or when the hash calculation algorithm has changed.
    
    Args:
        song_data: Song metadata dictionary (modified in place)
        
    Returns:
        Updated song data dictionary with metadataHash field
    """
    if not song_data.get('metadataHash') and not song_data.get('metadata_hash'):
        hash_value = calculate_metadata_hash(song_data)
        # Set both camelCase and snake_case versions for compatibility
        song_data['metadataHash'] = hash_value
        song_data['metadata_hash'] = hash_value
    
    return song_data
