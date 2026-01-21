#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Pre-Compact Handler - PreCompact Hook

Backs up transcript before context compaction and logs the event.
Ensures no conversation history is lost during compaction.

Backup Location:
    .claude/logs/transcript_backups/{session_id}_pre_compact_{trigger}_{timestamp}.jsonl

Data captured enables:
- Full conversation history preservation
- Compaction frequency analysis
- Pre/post compaction comparison

Usage:
    Configure in .claude/settings.json under hooks.PreCompact
"""

import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime, timezone

# Import from relative utils
sys.path.insert(0, str(Path(__file__).parent))
from utils.log_writer import append_event, create_event


def main():
    try:
        input_data = json.load(sys.stdin)
        session_id = input_data.get("session_id", "unknown")
        transcript_path = input_data.get("transcript_path", "")
        trigger = input_data.get("trigger", "auto")

        # Ensure transcript exists
        if not transcript_path or not Path(transcript_path).exists():
            sys.exit(0)

        # Create backup directory
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
        backup_dir = Path(project_dir) / ".claude" / "logs" / "transcript_backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Create backup filename with timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        backup_filename = f"{session_id[:8]}_pre_compact_{trigger}_{timestamp}.jsonl"
        backup_path = backup_dir / backup_filename

        # Copy transcript to backup
        shutil.copy2(transcript_path, backup_path)

        # Log pre-compact event
        event = create_event(
            "pre_compact",
            session_id,
            trigger=trigger,
            backup_path=str(backup_path),
            original_path=transcript_path
        )
        append_event(event)

        # Output to stderr for visibility
        print(f"Transcript backed up: {backup_filename}", file=sys.stderr)

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception as e:
        # Non-blocking - don't fail compaction on backup errors
        print(f"Backup warning: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
