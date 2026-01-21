#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
User Prompt Submit Logger - UserPromptSubmit Hook

Logs user prompts to session JSONL and updates session metadata.
Captures prompt length and preview for analysis.

Enhanced with hierarchical logging:
- Parent session and agent depth
- Correlation IDs and sequence numbers
- Prompt classification (type, subtype, command, topics)

Data captured enables:
- Session conversation flow analysis
- Prompt complexity tracking
- User interaction patterns
- Command usage analysis
- Topic trend detection

Usage:
    Configure in .claude/settings.json under hooks.UserPromptSubmit
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import from relative utils
sys.path.insert(0, str(Path(__file__).parent))
from utils.log_writer import append_event, create_event, read_session_metadata, write_session_metadata
from utils.status_state_manager import read_session_state
from utils.correlation_tracker import generate_correlation_id, get_sequence_number
from utils.prompt_classifier import classify_prompt


def main():
    try:
        input_data = json.load(sys.stdin)
        session_id = input_data.get("session_id", "unknown")
        prompt = input_data.get("prompt", "")

        # Get session state for hierarchical context
        state = read_session_state()
        parent_session_id = state.get("parent_session_id")
        agent_depth = state.get("agent_depth", 0)

        # Generate correlation ID and sequence number
        correlation_id = generate_correlation_id()
        sequence_number = get_sequence_number()

        # Create prompt event with preview
        prompt_length = len(prompt)
        prompt_preview = prompt[:100] + "..." if len(prompt) > 100 else prompt

        # Classify the prompt
        prompt_classification = classify_prompt(prompt)

        # Create enhanced event
        event = create_event(
            "user_prompt",
            session_id,
            parent_session_id=parent_session_id,
            agent_depth=agent_depth,
            correlation_id=correlation_id,
            sequence_number=sequence_number,
            prompt_length=prompt_length,
            prompt_preview=prompt_preview,
            prompt_classification=prompt_classification
        )

        # Append to session log
        append_event(event)

        # Update session metadata
        metadata = read_session_metadata(session_id)

        # Initialize metadata if new session
        if not metadata:
            metadata = {
                "session_id": session_id,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "prompts": []
            }

        # Append prompt metadata
        metadata["prompts"].append({
            "timestamp": event["timestamp"],
            "preview": prompt_preview,
            "length": prompt_length,
            "classification": prompt_classification
        })

        # Write updated metadata
        write_session_metadata(session_id, metadata)

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
