#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Outcome Capture Hook - Captures user-provided session outcomes

Triggered when user runs /success, /failure, or /null commands.
Stores session transcript summary and outcome to learnings directory.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict


def detect_outcome_command(prompt: str) -> tuple[str, str]:
    """Detect if this is an outcome command. Returns (outcome_type, reason)."""
    prompt = prompt.strip()
    if prompt == "/success":
        return ("success", "")
    elif prompt.startswith("/failure"):
        return ("failure", prompt[8:].strip())
    elif prompt == "/null":
        return ("null", "")
    return (None, "")


def get_session_log_path(session_id: str, project_dir: Path) -> Path:
    """Find the session log file for this session ID."""
    session_log_dir = project_dir / ".claude" / "logs" / "sessions"
    if not session_log_dir.exists():
        return None
    matching_files = list(session_log_dir.glob(f"*{session_id[:8]}*.jsonl"))
    return max(matching_files, key=lambda p: p.stat().st_mtime) if matching_files else None


def get_transcript_path(session_id: str) -> Path:
    """Find transcript file in ~/.claude/projects/{hash}/{session_id}.jsonl."""
    claude_dir = Path.home() / ".claude" / "projects"
    if not claude_dir.exists():
        return None
    for project_dir in claude_dir.iterdir():
        if project_dir.is_dir():
            transcript = project_dir / f"{session_id}.jsonl"
            if transcript.exists():
                return transcript
    return None


def extract_transcript_summary(transcript_path: Path, max_chars: int = 500) -> str:
    """Extract first N chars of user prompts from transcript."""
    user_prompts = []
    try:
        with open(transcript_path, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("type") == "user":
                        msg = entry.get("message", {})
                        content = msg.get("content", "")

                        if isinstance(content, str):
                            text = content.strip()
                            if text and not text.startswith("<command-"):
                                user_prompts.append(text)
                        elif isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and item.get("type") == "text":
                                    text = item.get("text", "").strip()
                                    if text:
                                        user_prompts.append(text)
                except json.JSONDecodeError:
                    continue
    except Exception:
        return ""

    full_text = " | ".join(user_prompts)
    return full_text[:max_chars] + "..." if len(full_text) > max_chars else full_text


def analyze_session(session_log_path: Path) -> dict:
    """Extract metrics from session log."""
    tool_counts = defaultdict(int)
    agent_spawned = defaultdict(int)
    total_tools = 0
    start_time = end_time = None

    with open(session_log_path, "r") as f:
        for line in f:
            try:
                event = json.loads(line)
                event_type = event.get("event")
                if event_type == "session_start":
                    start_time = event.get("timestamp")
                elif event_type == "session_end":
                    end_time = event.get("timestamp")
                elif event_type == "tool_use":
                    total_tools += 1
                    tool_counts[event.get("tool_name", "unknown")] += 1
                    if metadata := event.get("metadata", {}):
                        if agent_type := metadata.get("subagent_type"):
                            agent_spawned[agent_type] += 1
            except json.JSONDecodeError:
                continue

    duration_seconds = 0
    if start_time and end_time:
        try:
            start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            duration_seconds = int((end_dt - start_dt).total_seconds())
        except Exception:
            pass

    return {
        "duration_seconds": duration_seconds,
        "tool_count": total_tools,
        "agents_spawned": dict(agent_spawned)
    }


def main():
    """Main hook entry point."""
    try:
        input_data = json.load(sys.stdin)
        outcome_type, outcome_reason = detect_outcome_command(input_data.get("prompt", ""))
        if not outcome_type:
            sys.exit(0)

        session_id = input_data.get("session_id", "unknown")
        project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))

        # Find session log
        session_log_path = get_session_log_path(session_id, project_dir)
        if not session_log_path or not session_log_path.exists():
            sys.exit(0)

        # Find and summarize transcript
        transcript_summary = ""
        full_transcript_path = ""
        if transcript_path := get_transcript_path(session_id):
            if transcript_path.exists():
                transcript_summary = extract_transcript_summary(transcript_path)
                full_transcript_path = str(transcript_path)

        # Analyze session
        metrics = analyze_session(session_log_path)
        timestamp = datetime.now(timezone.utc).isoformat()

        # Build and write full session data
        learnings_dir = project_dir / ".claude" / "data" / "learnings"
        sessions_dir = learnings_dir / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)

        session_data = {
            "session_id": session_id,
            "outcome": outcome_type,
            "outcome_reason": outcome_reason,
            "timestamp": timestamp,
            "duration_seconds": metrics["duration_seconds"],
            "transcript_summary": transcript_summary,
            "full_transcript_path": full_transcript_path,
            "tool_count": metrics["tool_count"],
            "agents_spawned": metrics["agents_spawned"],
            "notable_patterns": []
        }

        with open(sessions_dir / f"{session_id}.json", "w") as f:
            json.dump(session_data, f, indent=2)

        # Append to outcomes JSONL
        outcome_summary = {
            "session_id": session_id,
            "outcome": outcome_type,
            "outcome_reason": outcome_reason,
            "timestamp": timestamp,
            "duration_seconds": metrics["duration_seconds"]
        }

        with open(learnings_dir / "outcomes.jsonl", "a") as f:
            f.write(json.dumps(outcome_summary) + "\n")

        sys.exit(0)

    except Exception as e:
        print(f"Outcome capture warning: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
