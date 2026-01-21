#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Session Evaluator - Background Evaluation Hook

Spawns a lightweight background process to analyze completed sessions
and extract learning insights without blocking session shutdown.

Also ensures sessions without explicit outcome get defaulted to "null".
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone


def has_outcome_recorded(session_id: str, project_dir: Path) -> bool:
    """Check if this session already has an outcome recorded."""
    # Check if session JSON exists in learnings/sessions/
    session_file = project_dir / ".claude" / "data" / "learnings" / "sessions" / f"{session_id}.json"
    if session_file.exists():
        return True

    # Check if session appears in outcomes.jsonl
    outcomes_file = project_dir / ".claude" / "data" / "learnings" / "outcomes.jsonl"
    if outcomes_file.exists():
        try:
            with open(outcomes_file, "r") as f:
                for line in f:
                    try:
                        outcome = json.loads(line)
                        if outcome.get("session_id") == session_id:
                            return True
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass

    return False


def record_null_outcome(session_id: str, project_dir: Path):
    """Record a null outcome for sessions without explicit feedback."""
    try:
        learnings_dir = project_dir / ".claude" / "data" / "learnings"
        sessions_dir = learnings_dir / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).isoformat()

        # Create minimal session data with null outcome
        session_data = {
            "session_id": session_id,
            "outcome": "null",
            "outcome_reason": "unrated - session ended without explicit feedback",
            "timestamp": timestamp,
            "duration_seconds": 0,
            "transcript_summary": "",
            "full_transcript_path": "",
            "tool_count": 0,
            "agents_spawned": {},
            "notable_patterns": []
        }

        with open(sessions_dir / f"{session_id}.json", "w") as f:
            json.dump(session_data, f, indent=2)

        # Append to outcomes JSONL
        outcome_summary = {
            "session_id": session_id,
            "outcome": "null",
            "outcome_reason": "unrated - session ended without explicit feedback",
            "timestamp": timestamp,
            "duration_seconds": 0
        }

        with open(learnings_dir / "outcomes.jsonl", "a") as f:
            f.write(json.dumps(outcome_summary) + "\n")

    except Exception as e:
        # Non-critical, don't block session end
        print(f"Warning: Failed to record null outcome: {e}", file=sys.stderr)


def spawn_evaluator():
    """Spawn background evaluator process and exit immediately."""
    try:
        input_data = json.load(sys.stdin)
        session_id = input_data.get("session_id", "unknown")

        # Get session log path from env or discover it
        project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
        session_log_dir = project_dir / ".claude" / "logs" / "sessions"

        # Find the most recent session log file matching this session_id
        session_log_path = None
        if session_log_dir.exists():
            matching_files = list(session_log_dir.glob(f"*{session_id[:8]}*.jsonl"))
            if matching_files:
                session_log_path = max(matching_files, key=lambda p: p.stat().st_mtime)

        if not session_log_path or not session_log_path.exists():
            sys.exit(0)

        # Check if outcome already recorded, if not, default to null
        if not has_outcome_recorded(session_id, project_dir):
            record_null_outcome(session_id, project_dir)

        # Spawn background evaluator with nohup-like behavior
        evaluator_script = Path(__file__).parent / "utils" / "background_evaluator.py"

        subprocess.Popen(
            ["uv", "run", "--script", str(evaluator_script), str(session_log_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True  # Detach from parent process
        )

        sys.exit(0)

    except Exception as e:
        # Silently fail - evaluation is non-critical
        print(f"Session evaluator spawn warning: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    spawn_evaluator()
