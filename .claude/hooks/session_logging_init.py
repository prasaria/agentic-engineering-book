#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Session Logging Initialization - SessionStart Hook

Sets up logging infrastructure at session start:
- Create .claude/logs/ directory structure
- Initialize per-session JSONL file
- Write initial context record
- Initialize session state for hierarchical tracking
- Reset sequence counter
"""

import json
import os
import platform
import sys
from pathlib import Path
from datetime import datetime, timezone

# Import utilities
sys.path.insert(0, str(Path(__file__).parent / "utils"))
from status_state_manager import init_session_state
from correlation_tracker import reset_sequence, generate_correlation_id
from model_extractor import get_model_from_transcript


def get_git_info(project_dir: str) -> dict:
    """Capture git branch and uncommitted changes count."""
    import subprocess

    git_info = {}
    try:
        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            git_info["branch"] = result.stdout.strip()

        # Get uncommitted changes count
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            uncommitted = len([line for line in result.stdout.strip().split("\n") if line])
            git_info["uncommitted_files"] = uncommitted
    except Exception:
        # Git commands failed, return partial info
        pass

    return git_info


def get_model_info(input_data: dict) -> dict:
    """Extract model information from input or transcript."""
    model_info = {"id": "unknown", "display_name": "Unknown Model"}

    try:
        # Try to get from transcript first
        session_id = input_data.get("session_id", "")
        transcript_path = input_data.get("transcript_path", "")

        if session_id and transcript_path:
            model_id = get_model_from_transcript(session_id, transcript_path)
            if model_id:
                # Parse display name from model ID
                # E.g., "claude-opus-4-5-20251101" -> "Opus 4.5"
                if "opus" in model_id.lower():
                    model_info = {"id": model_id, "display_name": "Opus 4.5"}
                elif "sonnet" in model_id.lower():
                    model_info = {"id": model_id, "display_name": "Sonnet 4.5"}
                else:
                    model_info = {"id": model_id, "display_name": model_id}

        # Fall back to environment variable if available
        if model_info["id"] == "unknown":
            model_env = os.environ.get("CLAUDE_MODEL")
            if model_env:
                model_info["id"] = model_env
                # Parse display name
                if "opus" in model_env.lower():
                    model_info["display_name"] = "Opus 4.5"
                elif "sonnet" in model_env.lower():
                    model_info["display_name"] = "Sonnet 4.5"
                else:
                    model_info["display_name"] = model_env

    except Exception:
        pass

    return model_info


def get_environment_info() -> dict:
    """Capture environment context."""
    try:
        return {
            "platform": platform.system().lower(),
            "python_version": platform.python_version()
        }
    except Exception:
        return {"platform": "unknown", "python_version": "unknown"}


def detect_source(input_data: dict) -> str:
    """Detect session source: startup, resume, or clear."""
    # This is a heuristic - adjust based on actual Claude Code behavior
    # For now, default to "startup"
    return "startup"


def init_logging():
    """Initialize logging infrastructure."""
    try:
        input_data = json.load(sys.stdin)
        session_id = input_data.get("session_id", "unknown")

        # Get project directory from environment or input
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")

        # Create log directories
        log_base = Path(project_dir) / ".claude" / "logs"
        log_base.mkdir(parents=True, exist_ok=True)
        (log_base / "sessions").mkdir(exist_ok=True)
        (log_base / "aggregated").mkdir(exist_ok=True)

        # Create data/sessions directory for metadata
        data_sessions = Path(project_dir) / ".claude" / "data" / "sessions"
        data_sessions.mkdir(parents=True, exist_ok=True)

        # Initialize per-session log with timestamp prefix for sorting
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        session_log = log_base / "sessions" / f"{timestamp}-{session_id[:8]}.jsonl"

        # Detect if in orchestrator context
        orchestrator_context = os.environ.get("CLAUDE_ORCHESTRATOR_CONTEXT", "")

        # Get hierarchical context
        parent_session_id = os.environ.get("CLAUDE_PARENT_SESSION_ID")
        agent_depth = int(os.environ.get("CLAUDE_AGENT_DEPTH", "0"))

        # If we have a parent, we're a subagent - increment depth
        if parent_session_id and agent_depth == 0:
            agent_depth = 1

        # Capture context first
        git_info = get_git_info(project_dir)
        model_info = get_model_info(input_data)

        # Initialize session state (including log file path for other hooks to find)
        init_session_state(
            session_id=session_id,
            parent_session_id=parent_session_id,
            agent_depth=agent_depth,
            model=model_info.get("id"),
            git_branch=git_info.get("branch") if git_info else None,
            log_file=str(session_log)
        )

        # Reset sequence counter for this session
        reset_sequence()

        # Capture remaining context
        env_info = get_environment_info()
        source = detect_source(input_data)
        correlation_id = generate_correlation_id()

        # Write enhanced session start event
        start_event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "session_start",
            "session_id": session_id,
            "parent_session_id": parent_session_id,
            "agent_depth": agent_depth,
            "correlation_id": correlation_id,
            "source": source,
            "model": model_info,
            "git": git_info if git_info else None,
            "project_dir": str(project_dir),
            "environment": env_info
        }

        with open(session_log, "a") as f:
            f.write(json.dumps(start_event) + "\n")

        # Initialize session metadata file
        metadata_file = data_sessions / f"{timestamp}-{session_id[:8]}.json"
        metadata = {
            "session_id": session_id,
            "parent_session_id": parent_session_id,
            "agent_depth": agent_depth,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "log_file": str(session_log),
            "model": model_info,
            "git": git_info if git_info else None
        }
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        # Store session log path and session ID in environment for other hooks
        env_file = os.environ.get("CLAUDE_ENV_FILE")
        if env_file:
            with open(env_file, "a") as f:
                f.write(f'export CLAUDE_SESSION_LOG="{session_log}"\n')
                f.write(f'export CLAUDE_SESSION_ID="{session_id}"\n')
                if parent_session_id:
                    f.write(f'export CLAUDE_PARENT_SESSION_ID="{parent_session_id}"\n')
                f.write(f'export CLAUDE_AGENT_DEPTH="{agent_depth}"\n')

        # Output goes to verbose logs
        print(f"Session logging initialized: {session_log.name}", file=sys.stderr)
        if parent_session_id:
            print(f"Subagent session (depth={agent_depth}, parent={parent_session_id[:8]})", file=sys.stderr)
        print(f"Model: {model_info['display_name']}", file=sys.stderr)
        if git_info:
            print(f"Git context: {git_info}", file=sys.stderr)
        sys.exit(0)

    except Exception as e:
        # Don't block session on logging errors
        print(f"Logging init warning: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    init_logging()
