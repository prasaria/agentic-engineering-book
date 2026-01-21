#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Background Session Evaluator

Analyzes session JSONL files and extracts learning insights.
Runs as a detached background process to avoid blocking session shutdown.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict


def analyze_session(session_log_path: Path) -> dict:
    """Extract metrics and patterns from session log."""
    tool_counts = defaultdict(int)
    agent_spawned = defaultdict(int)
    orchestrator_commands = []
    total_tools = 0
    start_time = None
    last_event_time = None
    agent_depth = 0

    with open(session_log_path, "r") as f:
        for line in f:
            try:
                event = json.loads(line)
                event_type = event.get("event")

                # Track timestamp from every event for duration calculation
                timestamp = event.get("timestamp")
                if timestamp:
                    last_event_time = timestamp

                if event_type == "session_start":
                    start_time = event.get("timestamp")
                    agent_depth = event.get("agent_depth", 0)
                elif event_type == "tool_use":
                    total_tools += 1
                    tool_name = event.get("tool_name", "unknown")
                    tool_counts[tool_name] += 1

                    # Track agent spawns
                    metadata = event.get("metadata", {})
                    if metadata and "subagent_type" in metadata:
                        agent_type = metadata["subagent_type"]
                        if agent_type:
                            agent_spawned[agent_type] += 1
                elif event_type == "user_prompt":
                    # Track orchestrator command usage
                    prompt_class = event.get("prompt_classification", {})
                    if isinstance(prompt_class, dict):
                        cmd = prompt_class.get("command_name", "")
                        if cmd.startswith("/orchestrators:"):
                            orchestrator_commands.append(cmd)

            except json.JSONDecodeError:
                continue

    # Calculate duration
    duration_seconds = 0
    if start_time and last_event_time:
        try:
            start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(last_event_time.replace("Z", "+00:00"))
            duration_seconds = int((end_dt - start_dt).total_seconds())
        except Exception:
            pass

    # Extract session ID from filename
    session_id = session_log_path.stem.split("-", 3)[-1] if "-" in session_log_path.stem else "unknown"

    # Identify notable patterns
    patterns = []
    if len(agent_spawned) > 3:
        patterns.append("high_agent_spawn")
    if duration_seconds > 300:  # >5 minutes
        patterns.append("long_session")
    if tool_counts.get("Read", 0) > 10:
        patterns.append("read_heavy")
    if tool_counts.get("Write", 0) > 5 or tool_counts.get("Edit", 0) > 5:
        patterns.append("write_heavy")
    if orchestrator_commands:
        patterns.append("orchestrator_usage")
    if total_tools < 3 and duration_seconds < 30:
        patterns.append("quick_session")

    # Get top 5 tools
    top_tools = dict(sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:5])

    return {
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": duration_seconds,
        "total_tools": total_tools,
        "tool_breakdown": top_tools,
        "agents_spawned": dict(agent_spawned),
        "orchestrator_commands_used": orchestrator_commands,
        "notable_patterns": patterns,
        "agent_depth": agent_depth
    }


def append_insight(insights_path: Path, insight: dict):
    """Append insight to JSONL file."""
    insights_path.parent.mkdir(parents=True, exist_ok=True)
    with open(insights_path, "a") as f:
        f.write(json.dumps(insight) + "\n")


def main():
    """Main evaluator entry point."""
    if len(sys.argv) < 2:
        sys.exit(1)

    session_log_path = Path(sys.argv[1])
    if not session_log_path.exists():
        sys.exit(1)

    try:
        # Analyze session
        insight = analyze_session(session_log_path)

        # Write to insights file
        project_dir = session_log_path.parents[3]  # .claude/logs/sessions/file.jsonl -> project root
        insights_path = project_dir / ".claude" / "data" / "learnings" / "session-insights.jsonl"

        append_insight(insights_path, insight)

    except Exception:
        # Silently fail - this is background analysis
        pass


if __name__ == "__main__":
    main()
