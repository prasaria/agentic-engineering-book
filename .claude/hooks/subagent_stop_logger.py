#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Subagent Stop Logger - SubagentStop Hook

Tracks subagent lifecycle by logging when subagents complete.
Enables analysis of agent delegation patterns and hierarchy.

Enhanced with hierarchical logging:
- Parent session and agent depth
- Duration calculation from spawn time
- Outcome tracking (success/error/interrupted)
- Tool call count for the subagent session

Data captured enables:
- Agent spawning frequency analysis
- Delegation pattern tracking
- Multi-agent workflow understanding
- Performance metrics per agent

Usage:
    Configure in .claude/settings.json under hooks.SubagentStop
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import from relative utils
sys.path.insert(0, str(Path(__file__).parent))
from utils.log_writer import append_event, create_event
from utils.status_state_manager import read_session_state, increment_counter


def calculate_duration(state: dict) -> float:
    """Calculate session duration in seconds."""
    try:
        start_time_str = state.get("start_time")
        if not start_time_str:
            return 0.0

        start_time = datetime.fromisoformat(start_time_str)
        now = datetime.now(timezone.utc)
        duration = (now - start_time).total_seconds()
        return round(duration, 2)

    except Exception:
        return 0.0


def detect_outcome(input_data: dict, state: dict) -> str:
    """
    Detect subagent outcome: success, error, or interrupted.

    Heuristics:
    - If stop_hook_active is False, likely interrupted
    - Otherwise, assume success (error detection would require error tracking)
    """
    try:
        stop_hook_active = input_data.get("stop_hook_active", False)

        # If stop hook wasn't actively triggered, likely interrupted
        if not stop_hook_active:
            return "interrupted"

        # Default to success
        # TODO: Could enhance with error detection from transcript
        return "success"

    except Exception:
        return "success"


def main():
    try:
        input_data = json.load(sys.stdin)
        session_id = input_data.get("session_id", "unknown")
        stop_hook_active = input_data.get("stop_hook_active", False)
        transcript_path = input_data.get("transcript_path", "")

        # Get session state for hierarchical context and metrics
        state = read_session_state()
        parent_session_id = state.get("parent_session_id")
        agent_depth = state.get("agent_depth", 0)

        # Calculate duration from session start
        duration_seconds = calculate_duration(state)

        # Detect outcome
        outcome = detect_outcome(input_data, state)

        # Get tool call count for this session
        tool_calls = state.get("tool_count", 0)

        # Log enhanced subagent stop event
        event = create_event(
            "subagent_stop",
            session_id,
            parent_session_id=parent_session_id,
            agent_depth=agent_depth,
            duration_seconds=duration_seconds,
            outcome=outcome,
            tool_calls=tool_calls,
            stop_hook_active=stop_hook_active,
            transcript_path=transcript_path
        )
        append_event(event)

        # Update parent session's agents_completed counter if we have a parent
        # Note: This updates the CURRENT session's state, which may be the parent
        # if this hook is called in the parent's context after subagent finishes
        if parent_session_id:
            increment_counter("agents_completed")

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
