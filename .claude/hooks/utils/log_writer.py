#!/usr/bin/env python3
"""
Shared JSONL logging utilities.

Provides atomic append operations to session logs with proper error handling.
Non-blocking - errors are suppressed to avoid breaking hook execution.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any


def get_session_log_path() -> Optional[str]:
    """
    Get the current session log path from environment or discover from state.

    Returns:
        Path to session log file, or None if not found

    Notes:
        - First checks CLAUDE_SESSION_LOG environment variable
        - Falls back to discovering from session_state.json
        - Falls back to finding most recent session log file
    """
    # Try environment variable first
    env_path = os.environ.get("CLAUDE_SESSION_LOG")
    if env_path and Path(env_path).exists():
        return env_path

    # Fallback: try to get from session state
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")

    # Check session_state.json for log file path hint
    state_file = Path(project_dir) / ".claude" / "data" / "session_state.json"
    if state_file.exists():
        try:
            with open(state_file, "r") as f:
                state = json.load(f)

                # Primary: check for explicit log_file path
                log_file = state.get("log_file")
                if log_file:
                    log_path = Path(log_file)
                    if log_path.exists():
                        return str(log_path)

                # Secondary: try to find matching log file by session ID
                session_id = state.get("session_id", "")
                if session_id:
                    logs_dir = Path(project_dir) / ".claude" / "logs" / "sessions"
                    if logs_dir.exists():
                        # Look for log file containing this session ID prefix
                        for log_file in logs_dir.glob(f"*-{session_id[:8]}.jsonl"):
                            return str(log_file)
        except Exception:
            pass

    # Final fallback: find most recent session log
    logs_dir = Path(project_dir) / ".claude" / "logs" / "sessions"
    if logs_dir.exists():
        try:
            log_files = sorted(logs_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
            if log_files:
                return str(log_files[0])
        except Exception:
            pass

    return None


def append_to_session_log(session_log_path: str, event: dict) -> bool:
    """
    Atomically append a JSON event to the session log.

    Args:
        session_log_path: Path to the JSONL session log file
        event: Dictionary to write as a JSON line

    Returns:
        True if write succeeded, False otherwise

    Notes:
        - Non-blocking: errors are caught and suppressed
        - Creates parent directories if needed
        - Appends newline-delimited JSON
    """
    try:
        log_path = Path(session_log_path)

        # Ensure parent directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Atomic append (mode 'a' with single write call)
        with open(log_path, "a") as f:
            f.write(json.dumps(event) + "\n")

        return True

    except Exception:
        # Suppress errors - logging should never break hooks
        return False


def create_event(event_type: str, session_id: str, **kwargs) -> dict[str, Any]:
    """
    Create a timestamped event dictionary.

    Args:
        event_type: The event type identifier
        session_id: The session ID
        **kwargs: Additional event fields

    Returns:
        Event dictionary with timestamp
    """
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        "session_id": session_id,
    }
    event.update(kwargs)
    return event


def append_event(event: dict) -> bool:
    """
    Append an event to the session log from environment.

    Args:
        event: Event dictionary to append

    Returns:
        True if successful, False otherwise
    """
    session_log_path = get_session_log_path()
    if not session_log_path:
        return False
    return append_to_session_log(session_log_path, event)


def get_session_metadata_path(session_id: str) -> Path:
    """
    Get the path to the session metadata file.

    Args:
        session_id: The session ID

    Returns:
        Path to the session metadata JSON file
    """
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    data_dir = Path(project_dir) / ".claude" / "data" / "sessions"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / f"{session_id}.json"


def read_session_metadata(session_id: str) -> dict[str, Any]:
    """
    Read session metadata from disk.

    Args:
        session_id: The session ID

    Returns:
        Session metadata dictionary
    """
    metadata_path = get_session_metadata_path(session_id)
    if not metadata_path.exists():
        return {}

    try:
        with open(metadata_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return {}


def write_session_metadata(session_id: str, metadata: dict[str, Any]) -> bool:
    """
    Write session metadata to disk.

    Args:
        session_id: The session ID
        metadata: Metadata dictionary to write

    Returns:
        True if successful, False otherwise
    """
    metadata_path = get_session_metadata_path(session_id)

    try:
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        return True
    except Exception:
        return False
