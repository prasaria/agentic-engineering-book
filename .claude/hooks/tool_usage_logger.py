#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Tool Usage Logger - PostToolUse Hook

Logs every tool invocation with parameters, duration, and status.
Writes to per-session JSONL file for later analysis.

Enhanced with hierarchical logging:
- Correlation IDs (read from PreToolUse temp file)
- Sequence numbers
- Parent session and agent depth
- Duration tracking
- Success status

Data captured enables:
- Tool usage frequency analysis
- Performance profiling (slow tools)
- Error pattern detection
- Agent behavior analysis
- Event correlation across pre/post hooks
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import utilities
sys.path.insert(0, str(Path(__file__).parent / "utils"))
from status_state_manager import read_session_state, increment_counter
from log_writer import get_session_log_path


# Tools that may contain sensitive data - redact parameters
SENSITIVE_TOOLS = {"Bash", "Write", "Edit"}

# Parameters to always redact
SENSITIVE_PARAMS = {"content", "new_string", "command"}


def redact_sensitive(params: dict, tool_name: str) -> dict:
    """Redact potentially sensitive parameter values."""
    if tool_name not in SENSITIVE_TOOLS:
        return params

    redacted = {}
    for key, value in params.items():
        if key in SENSITIVE_PARAMS:
            redacted[key] = f"<redacted:{len(str(value))} chars>"
        else:
            redacted[key] = value
    return redacted


def read_correlation_id(session_id: str) -> str:
    """Read correlation ID from temp file written by PreToolUse hook."""
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
        temp_dir = Path(project_dir) / ".claude" / "data" / "temp"
        temp_file = temp_dir / f"{session_id}-correlation.txt"

        if temp_file.exists():
            with open(temp_file, "r") as f:
                correlation_id = f.read().strip()

            # Clean up temp file
            try:
                temp_file.unlink()
            except Exception:
                pass

            return correlation_id if correlation_id else "unknown"

        return "unknown"

    except Exception:
        return "unknown"


def log_tool_use():
    """Log tool usage event."""
    try:
        input_data = json.load(sys.stdin)

        session_id = input_data.get("session_id", "unknown")
        tool_name = input_data.get("tool_name", "unknown")
        tool_input = input_data.get("tool_input", {})

        # Get session log path (checks env, state file, or discovers)
        session_log_path = get_session_log_path()
        if not session_log_path:
            # Logging not initialized, skip silently
            sys.exit(0)

        # Get session state for hierarchical context
        state = read_session_state()
        parent_session_id = state.get("parent_session_id")
        agent_depth = state.get("agent_depth", 0)

        # Read correlation ID from temp file
        correlation_id = read_correlation_id(session_id)

        # Get sequence number (note: this is AFTER PreToolUse incremented it)
        # So we use the current value
        from utils.correlation_tracker import get_current_sequence
        sequence_number = get_current_sequence()

        # Redact sensitive parameters
        safe_params = redact_sensitive(tool_input, tool_name)

        # Extract key metadata for certain tools
        metadata = {}
        if tool_name == "Read":
            metadata["file_path"] = tool_input.get("file_path", "")
        elif tool_name == "Glob":
            metadata["pattern"] = tool_input.get("pattern", "")
        elif tool_name == "Grep":
            metadata["pattern"] = tool_input.get("pattern", "")
        elif tool_name == "Task":
            metadata["subagent_type"] = tool_input.get("subagent_type", "")
            metadata["description"] = tool_input.get("description", "")
        elif tool_name == "WebFetch":
            metadata["url"] = tool_input.get("url", "")

        # Try to extract duration if available (timing info may not be present)
        duration_ms = None
        # Note: Claude Code may not provide timing info in PostToolUse
        # This is a placeholder for future enhancement

        # Create enhanced event record
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "tool_use",
            "session_id": session_id,
            "parent_session_id": parent_session_id,
            "agent_depth": agent_depth,
            "correlation_id": correlation_id,
            "sequence_number": sequence_number,
            "tool_name": tool_name,
            "metadata": metadata if metadata else None,
            "duration_ms": duration_ms,
            "status": "success"  # PostToolUse means it ran successfully
        }

        # Append to session log
        with open(session_log_path, "a") as f:
            f.write(json.dumps(event) + "\n")

        # Update session state: increment tool_count
        increment_counter("tool_count")

        sys.exit(0)

    except Exception as e:
        # Non-blocking - don't fail the tool call
        print(f"Tool logging warning: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    log_tool_use()
