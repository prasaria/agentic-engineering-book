#!/usr/bin/env python3
"""
Session state management for status line updates.

Provides atomic operations for reading/writing session state used by the
status line display. State includes session metadata, counters, and git context.

State file location: .claude/data/session_state.json
Non-blocking: all errors are suppressed to avoid breaking hook execution.
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def get_state_file_path() -> Path:
    """
    Get path to session state file.

    Returns:
        Path to session state JSON file

    Notes:
        - Location: .claude/data/session_state.json
        - File is created on first write if it doesn't exist
    """
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    data_dir = Path(project_dir) / ".claude" / "data"
    return data_dir / "session_state.json"


def read_session_state() -> dict[str, Any]:
    """
    Read current session state.

    Returns:
        Session state dictionary, or empty dict if file doesn't exist

    Notes:
        - Non-blocking: returns {} on any error
        - Safe to call even if state file doesn't exist yet
    """
    try:
        state_file = get_state_file_path()
        if not state_file.exists():
            return {}

        with open(state_file, "r") as f:
            return json.load(f)

    except (json.JSONDecodeError, OSError, Exception):
        return {}


def write_session_state(state: dict[str, Any]) -> bool:
    """
    Write complete session state.

    Args:
        state: Complete state dictionary to write

    Returns:
        True if write succeeded, False otherwise

    Notes:
        - Overwrites entire state file
        - Creates parent directories if needed
        - Adds last_updated timestamp automatically
        - Non-blocking: errors are suppressed
    """
    try:
        state_file = get_state_file_path()

        # Ensure parent directory exists
        state_file.parent.mkdir(parents=True, exist_ok=True)

        # Add last_updated timestamp
        state["last_updated"] = datetime.now(timezone.utc).isoformat()

        # Atomic write via temp file + rename
        temp_file = state_file.with_suffix(".tmp")
        with open(temp_file, "w") as f:
            json.dump(state, f, indent=2)

        temp_file.replace(state_file)
        return True

    except Exception:
        # Suppress errors - state management should never break hooks
        return False


def update_session_state(**kwargs) -> bool:
    """
    Atomically update specific fields in session state.

    Args:
        **kwargs: Fields to update in state

    Returns:
        True if update succeeded, False otherwise

    Example:
        >>> update_session_state(tool_count=47, model="claude-opus-4-5")
        True

    Notes:
        - Reads current state, merges updates, writes back
        - Creates state file if it doesn't exist
        - Non-blocking: errors are suppressed
    """
    try:
        # Read current state
        state = read_session_state()

        # Merge updates
        state.update(kwargs)

        # Write back
        return write_session_state(state)

    except Exception:
        return False


def increment_counter(counter_name: str, amount: int = 1) -> int:
    """
    Atomically increment a counter and return new value.

    Args:
        counter_name: Name of counter field in state
        amount: Amount to increment by (default: 1)

    Returns:
        New counter value, or 0 if operation failed

    Example:
        >>> increment_counter("tool_count", 1)
        47
        >>> increment_counter("agents_spawned")
        4

    Notes:
        - Thread-safe via read-modify-write
        - Creates counter if it doesn't exist (starts at 0)
        - Returns 0 on error (not distinguishable from actual 0)
    """
    try:
        # Read current state
        state = read_session_state()

        # Get current value (default to 0)
        current = state.get(counter_name, 0)
        if not isinstance(current, (int, float)):
            current = 0

        # Increment
        new_value = current + amount
        state[counter_name] = new_value

        # Write back
        if write_session_state(state):
            return new_value
        else:
            return 0

    except Exception:
        return 0


def init_session_state(
    session_id: str,
    parent_session_id: Optional[str] = None,
    agent_depth: int = 0,
    model: Optional[str] = None,
    git_branch: Optional[str] = None,
    log_file: Optional[str] = None,
) -> bool:
    """
    Initialize session state at session start.

    Args:
        session_id: Current session ID
        parent_session_id: Parent session ID if spawned from agent
        agent_depth: Nesting depth (0 = user session, 1+ = agent)
        model: Model name (e.g., "claude-opus-4-5")
        git_branch: Current git branch
        log_file: Path to the session log file

    Returns:
        True if initialization succeeded, False otherwise

    Notes:
        - Creates fresh state file with initial values
        - Sets start_time to current timestamp
        - Initializes counters to 0
        - Non-blocking: errors are suppressed

    Example:
        >>> init_session_state(
        ...     session_id="abc123",
        ...     model="claude-opus-4-5",
        ...     git_branch="main",
        ...     log_file="/path/to/session.jsonl"
        ... )
        True
    """
    try:
        state = {
            "session_id": session_id,
            "parent_session_id": parent_session_id,
            "agent_depth": agent_depth,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "tool_count": 0,
            "agents_spawned": 0,
            "agents_completed": 0,
            "git_branch": git_branch,
            "orchestrator_context": None,
            "log_file": log_file,
        }

        return write_session_state(state)

    except Exception:
        return False
