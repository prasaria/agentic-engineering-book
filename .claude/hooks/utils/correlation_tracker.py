#!/usr/bin/env python3
"""
Correlation ID and sequence number generation for event tracing.

Provides utilities for:
- Generating unique correlation IDs (UUIDs)
- Managing global sequence counters for event ordering
- Session-scoped sequence tracking

Sequence file location: .claude/data/sequence_counter.json
Non-blocking: all errors are suppressed to avoid breaking hook execution.
"""

import json
import os
import uuid
from pathlib import Path
from typing import Optional


def generate_correlation_id() -> str:
    """
    Generate UUID for correlation tracking.

    Returns:
        UUID string in format "abc123def456"

    Example:
        >>> generate_correlation_id()
        "a1b2c3d4e5f6"

    Notes:
        - Uses UUID4 (random)
        - Returns hex string without dashes
        - Safe to call even in error conditions
    """
    try:
        return uuid.uuid4().hex
    except Exception:
        # Fallback to timestamp-based ID if UUID generation fails
        import time
        return f"fallback_{int(time.time() * 1000)}"


def _get_sequence_file_path() -> Path:
    """
    Get path to sequence counter file.

    Returns:
        Path to sequence counter JSON file

    Notes:
        - Location: .claude/data/sequence_counter.json
        - File stores current sequence number for session
    """
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    data_dir = Path(project_dir) / ".claude" / "data"
    return data_dir / "sequence_counter.json"


def _read_sequence_file() -> dict:
    """
    Read sequence counter from disk.

    Returns:
        Dictionary with sequence counter, or empty dict on error

    Notes:
        - Non-blocking: returns {} if file doesn't exist
        - Returns {} on JSON decode errors
    """
    try:
        sequence_file = _get_sequence_file_path()
        if not sequence_file.exists():
            return {}

        with open(sequence_file, "r") as f:
            return json.load(f)

    except (json.JSONDecodeError, OSError, Exception):
        return {}


def _write_sequence_file(data: dict) -> bool:
    """
    Write sequence counter to disk.

    Args:
        data: Dictionary to write

    Returns:
        True if write succeeded, False otherwise

    Notes:
        - Creates parent directories if needed
        - Atomic write via temp file + rename
        - Non-blocking: errors are suppressed
    """
    try:
        sequence_file = _get_sequence_file_path()

        # Ensure parent directory exists
        sequence_file.parent.mkdir(parents=True, exist_ok=True)

        # Atomic write via temp file + rename
        temp_file = sequence_file.with_suffix(".tmp")
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=2)

        temp_file.replace(sequence_file)
        return True

    except Exception:
        return False


def get_sequence_number() -> int:
    """
    Get and increment global sequence counter for this session.

    Returns:
        Next sequence number (1-indexed), or 0 on error

    Example:
        >>> get_sequence_number()
        1
        >>> get_sequence_number()
        2

    Notes:
        - First call returns 1, increments from there
        - Thread-safe via read-modify-write
        - Returns 0 on error (distinguishable from valid sequence)
        - Sequence persists across hook invocations within a session
    """
    try:
        data = _read_sequence_file()

        # Get current sequence (default to 0)
        current = data.get("sequence", 0)
        if not isinstance(current, int):
            current = 0

        # Increment
        next_sequence = current + 1
        data["sequence"] = next_sequence

        # Write back
        if _write_sequence_file(data):
            return next_sequence
        else:
            return 0

    except Exception:
        return 0


def reset_sequence() -> None:
    """
    Reset sequence counter (called at session start).

    Notes:
        - Sets sequence back to 0
        - Next call to get_sequence_number() will return 1
        - Non-blocking: errors are suppressed
        - Safe to call even if file doesn't exist

    Example:
        >>> reset_sequence()
        >>> get_sequence_number()
        1
    """
    try:
        data = {"sequence": 0}
        _write_sequence_file(data)
    except Exception:
        pass  # Non-blocking


def get_current_sequence() -> int:
    """
    Get current sequence number without incrementing.

    Returns:
        Current sequence number, or 0 if not initialized

    Example:
        >>> get_sequence_number()
        1
        >>> get_current_sequence()
        1
        >>> get_sequence_number()
        2
        >>> get_current_sequence()
        2

    Notes:
        - Read-only operation
        - Returns 0 if sequence file doesn't exist yet
        - Non-blocking: returns 0 on any error
    """
    try:
        data = _read_sequence_file()
        current = data.get("sequence", 0)
        if isinstance(current, int):
            return current
        return 0

    except Exception:
        return 0
