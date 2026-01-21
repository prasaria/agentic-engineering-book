#!/usr/bin/env python3
"""
Model name extraction from transcript with TTL caching.

Scans Claude Code transcripts to find the most recent assistant message
containing a model field. Implements file-based caching with TTL to avoid
repeated transcript scanning.

Cache location: .claude/data/model-cache/{session_id}.json
Cache schema: {"model": "claude-opus-4-5", "timestamp": 1234567890, "ttl": 60}
"""

import json
import os
import time
from pathlib import Path
from typing import Optional


def get_model_from_transcript(
    session_id: str,
    transcript_path: str,
    ttl: int = 60
) -> Optional[str]:
    """
    Extract model name from transcript with TTL caching.

    Args:
        session_id: Current session identifier
        transcript_path: Path to transcript JSONL file
        ttl: Cache time-to-live in seconds (default: 60)

    Returns:
        Model name string (e.g., "claude-opus-4-5"), or None if not found

    Process:
        1. Check cache for unexpired entry
        2. If cache miss/expired, scan transcript for model field
        3. Update cache with new result
        4. Return model name

    Notes:
        - Non-blocking: errors return None
        - Cache stored per session_id
        - Scans transcript in reverse for most recent model
    """
    try:
        # Determine cache path from project directory
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
        cache_dir = Path(project_dir) / ".claude" / "data" / "model-cache"
        cache_file = cache_dir / f"{session_id}.json"

        current_time = int(time.time())

        # Try to read from cache
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    cache_data = json.load(f)

                cached_time = cache_data.get("timestamp", 0)
                cached_ttl = cache_data.get("ttl", ttl)

                # Check if cache is still valid
                if current_time - cached_time < cached_ttl:
                    return cache_data.get("model")
            except (json.JSONDecodeError, OSError):
                pass  # Cache corrupted, fall through to scan

        # Cache miss or expired - scan transcript
        model = _scan_transcript_for_model(transcript_path)

        if model:
            # Update cache
            _write_cache(cache_file, model, current_time, ttl)

        return model

    except Exception:
        # Non-blocking - return None on any error
        return None


def _scan_transcript_for_model(transcript_path: str) -> Optional[str]:
    """
    Scan transcript JSONL for most recent assistant message with model field.

    Args:
        transcript_path: Path to transcript JSONL file

    Returns:
        Model name string, or None if not found
    """
    try:
        transcript_file = Path(transcript_path)
        if not transcript_file.exists():
            return None

        # Read all lines (could optimize with reverse scan for large files)
        model = None
        with open(transcript_file, "r") as f:
            for line in f:
                try:
                    event = json.loads(line)

                    # Look for assistant messages with model field
                    if event.get("role") == "assistant":
                        event_model = event.get("model")
                        if event_model:
                            model = event_model  # Keep updating to get most recent

                except json.JSONDecodeError:
                    continue

        return model

    except Exception:
        return None


def _write_cache(cache_file: Path, model: str, timestamp: int, ttl: int) -> None:
    """
    Write model cache entry.

    Args:
        cache_file: Path to cache file
        model: Model name to cache
        timestamp: Current unix timestamp
        ttl: Cache TTL in seconds
    """
    try:
        # Ensure cache directory exists
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        cache_data = {
            "model": model,
            "timestamp": timestamp,
            "ttl": ttl
        }

        with open(cache_file, "w") as f:
            json.dump(cache_data, f, indent=2)

    except Exception:
        pass  # Non-blocking
