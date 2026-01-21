#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Orchestration Trace Logger - PostToolUse Hook

Captures lightweight execution traces when Task tool is used.
Enables self-improving orchestration analysis.

Part of Emergent Learning Architecture (ELA) Component 2.

Data captured:
- Agent name, type, file path
- Phase (plan/build/improve/question)
- Domain (knowledge, claude-config, etc.)
- Latency, success/failure
- Context and token counts
- Spec path if referenced

Output: .claude/.cache/orchestration-traces.jsonl

Usage:
    Configure in .claude/settings.json under hooks.PostToolUse
    with matcher for Task tool only.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import utilities
sys.path.insert(0, str(Path(__file__).parent / "utils"))
from status_state_manager import read_session_state
from correlation_tracker import get_current_sequence


def extract_phase(agent_name: str) -> str:
    """Extract phase from agent name (plan/build/improve/question)."""
    if '-plan-agent' in agent_name:
        return 'plan'
    elif '-build-agent' in agent_name:
        return 'build'
    elif '-improve-agent' in agent_name:
        return 'improve'
    elif '-question-agent' in agent_name:
        return 'question'
    return None


def extract_domain(agent_name: str, agent_file: str) -> str:
    """Extract expert domain from agent name or file path."""
    # Try agent name first
    if '-' in agent_name:
        parts = agent_name.split('-')
        # Remove 'agent' suffix
        if parts[-1] == 'agent':
            parts = parts[:-1]
        # Remove phase suffix
        if parts[-1] in ['plan', 'build', 'improve', 'question']:
            parts = parts[:-1]
        if parts:
            return '-'.join(parts)

    # Fallback: extract from file path
    if '/experts/' in agent_file:
        try:
            return agent_file.split('/experts/')[1].split('/')[0]
        except (IndexError, AttributeError):
            pass

    return 'unknown'


def detect_workflow_type(agent_file: str, agent_name: str) -> str:
    """Classify agent into workflow categories."""
    if '/experts/' in agent_file:
        return 'expert'
    elif 'orchestrator' in agent_name.lower():
        return 'orchestrator'
    elif agent_name in ['scout-agent', 'docs-scraper', 'meta-agent', 'github-versioning-agent']:
        return 'utility'
    return 'unknown'


def extract_spec_path(prompt: str) -> str:
    """Extract specification file path from Task prompt."""
    if not prompt:
        return None

    patterns = [
        r'PATH_TO_SPEC:\s*([^\s]+\.md)',
        r'Specification:\s*([^\s]+\.md)',
        r'(\.claude/\.cache/specs/[^\s]+\.md)',
    ]

    for pattern in patterns:
        match = re.search(pattern, prompt)
        if match:
            return match.group(1)

    return None


def infer_spawned_by(agent_depth: int) -> str:
    """Infer which command/agent spawned this Task."""
    if agent_depth == 0:
        return "HEAD"
    elif agent_depth == 1:
        return "/do"  # Most common case
    else:
        return "agent"


def read_correlation_id_for_trace(session_id: str) -> str:
    """Read correlation ID from temp file (similar to tool_usage_logger)."""
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
        temp_dir = Path(project_dir) / ".claude" / "data" / "temp"
        temp_file = temp_dir / f"{session_id}-correlation.txt"

        if temp_file.exists():
            with open(temp_file, "r") as f:
                return f.read().strip() or "unknown"

        return "unknown"

    except Exception:
        return "unknown"


def calculate_latency(session_id: str) -> int:
    """
    Calculate latency from PreToolUse timestamp.

    Note: This is approximate. Reads temp file written by pre_tool_use_logger.
    Returns 0 if timing data unavailable.
    """
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
        temp_dir = Path(project_dir) / ".claude" / "data" / "temp"
        timing_file = temp_dir / f"{session_id}-task-timing.txt"

        if timing_file.exists():
            with open(timing_file, "r") as f:
                start_time_str = f.read().strip()

            # Clean up temp file
            try:
                timing_file.unlink()
            except Exception:
                pass

            start_time = datetime.fromisoformat(start_time_str)
            now = datetime.now(timezone.utc)
            latency_ms = int((now - start_time).total_seconds() * 1000)
            return latency_ms

        return 0

    except Exception:
        return 0


def main():
    """Log orchestration trace for Task tool invocations."""
    try:
        input_data = json.load(sys.stdin)

        # Only process Task tool
        tool_name = input_data.get("tool_name", "")
        if tool_name != "Task":
            sys.exit(0)

        # Extract basic fields
        session_id = input_data.get("session_id", "unknown")
        tool_input = input_data.get("tool_input", {})

        # Get session state for hierarchical context
        state = read_session_state()
        parent_session_id = state.get("parent_session_id")
        agent_depth = state.get("agent_depth", 0)

        # Get correlation and sequence
        correlation_id = read_correlation_id_for_trace(session_id)
        sequence_number = get_current_sequence()

        # Extract Task-specific fields
        agent_name = tool_input.get("subagent_type", "unknown")
        agent_type = "file" if "subagent_type" in tool_input else "inline"
        agent_file = tool_input.get("subagent_type", "") if agent_type == "file" else None
        description = tool_input.get("description", "")
        prompt = tool_input.get("prompt", "")
        run_in_background = tool_input.get("run_in_background", False)

        # Derive metadata
        phase = extract_phase(agent_name)
        domain = extract_domain(agent_name, agent_file or "")
        workflow_type = detect_workflow_type(agent_file or "", agent_name)
        spec_path = extract_spec_path(prompt)
        spawned_by = infer_spawned_by(agent_depth)

        # Calculate latency (requires PreToolUse cooperation)
        latency_ms = calculate_latency(session_id)

        # Extract token counts (if available in PostToolUse)
        # Note: Claude Code may not provide these in hook input
        # Defaulting to 0 if unavailable
        context_tokens = input_data.get("context_tokens", 0)
        output_tokens = input_data.get("output_tokens", 0)
        total_tokens = context_tokens + output_tokens

        # Success determination
        # PostToolUse means tool executed; check for error field
        success = not bool(input_data.get("error"))
        error_type = input_data.get("error_type") if not success else None

        # Build trace record
        trace = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "parent_session_id": parent_session_id,
            "agent_depth": agent_depth,
            "correlation_id": correlation_id,
            "sequence_number": sequence_number,

            "agent_name": agent_name,
            "agent_type": agent_type,
            "agent_file": agent_file,

            "phase": phase,
            "domain": domain,
            "workflow_type": workflow_type,

            "spec_path": spec_path,
            "description": description[:200] if description else None,  # Truncate long descriptions

            "latency_ms": latency_ms,
            "success": success,
            "error_type": error_type,

            "context_tokens": context_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,

            "spawned_by": spawned_by,
            "run_in_background": run_in_background,
        }

        # Write to orchestration traces file
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
        traces_dir = Path(project_dir) / ".claude" / ".cache"
        traces_dir.mkdir(parents=True, exist_ok=True)

        traces_file = traces_dir / "orchestration-traces.jsonl"

        with open(traces_file, "a") as f:
            f.write(json.dumps(trace) + "\n")

        sys.exit(0)

    except Exception as e:
        # Non-blocking - don't fail the tool call
        print(f"Orchestration trace logging warning: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
