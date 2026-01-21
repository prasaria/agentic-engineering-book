#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Pre-Tool Use Logger - PreToolUse Hook

Logs tool invocations BEFORE execution and applies security guards.
Blocks dangerous commands with exit code 2, otherwise exits 0.

Enhanced with hierarchical logging:
- Correlation IDs for tracking related events
- Sequence numbers for ordering
- Agent spawn detection for Task tool
- Session state updates

Security Guards:
- Dangerous rm -rf commands
- .env file access (optional, commented out by default)

Additional Context Injection:
- Write tool: Guidance for chapter .md files (frontmatter, style guide)
- Edit tool: Guidance for preserving frontmatter when editing chapters

Data captured enables:
- Tool usage pattern analysis
- Security incident tracking
- Pre-execution audit trail
- Agent hierarchy tracking

Usage:
    Configure in .claude/settings.json under hooks.PreToolUse
"""

import json
import os
import sys
from pathlib import Path

# Import from relative utils
sys.path.insert(0, str(Path(__file__).parent))
from utils.log_writer import append_event, create_event
from utils.security_guards import is_dangerous_rm_command, is_env_file_access
from utils.status_state_manager import read_session_state, increment_counter
from utils.correlation_tracker import generate_correlation_id, get_sequence_number


def store_correlation_for_post_hook(session_id: str, correlation_id: str):
    """Store correlation ID in temp file for PostToolUse hook to read."""
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
        temp_dir = Path(project_dir) / ".claude" / "data" / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        temp_file = temp_dir / f"{session_id}-correlation.txt"
        with open(temp_file, "w") as f:
            f.write(correlation_id)
    except Exception:
        pass  # Non-blocking


def main():
    try:
        input_data = json.load(sys.stdin)
        session_id = input_data.get("session_id", "unknown")
        tool_name = input_data.get("tool_name", "unknown")
        tool_input = input_data.get("tool_input", {})

        # Get session state for hierarchical context
        state = read_session_state()
        parent_session_id = state.get("parent_session_id")
        agent_depth = state.get("agent_depth", 0)

        # Generate correlation ID and sequence number
        correlation_id = generate_correlation_id()
        sequence_number = get_sequence_number()

        # Store correlation ID for PostToolUse hook
        store_correlation_for_post_hook(session_id, correlation_id)

        # Security guard: Check for dangerous rm commands
        if tool_name == "Bash":
            command = tool_input.get("command", "")
            if is_dangerous_rm_command(command):
                # Log blocked event with hierarchical context
                event = create_event(
                    "tool_blocked",
                    session_id,
                    parent_session_id=parent_session_id,
                    agent_depth=agent_depth,
                    correlation_id=correlation_id,
                    sequence_number=sequence_number,
                    tool_name=tool_name,
                    reason="Dangerous rm command detected and prevented"
                )
                append_event(event)

                # Block the tool call
                print(
                    "BLOCKED: Dangerous rm command detected and prevented",
                    file=sys.stderr,
                )
                sys.exit(2)

        # Security guard: Check for .env file access (commented out by default)
        # if is_env_file_access(tool_name, tool_input):
        #     event = create_event(
        #         "tool_blocked",
        #         session_id,
        #         parent_session_id=parent_session_id,
        #         agent_depth=agent_depth,
        #         correlation_id=correlation_id,
        #         sequence_number=sequence_number,
        #         tool_name=tool_name,
        #         reason="Access to .env files containing sensitive data is prohibited"
        #     )
        #     append_event(event)
        #
        #     print("BLOCKED: Access to .env files containing sensitive data is prohibited", file=sys.stderr)
        #     print("Use .env.sample for template files instead", file=sys.stderr)
        #     sys.exit(2)

        # Detect Task tool for agent spawn tracking
        if tool_name == "Task":
            agent_type = tool_input.get("subagent_type", "unknown")
            description = tool_input.get("description", "")
            prompt = tool_input.get("prompt", "")

            # Log agent spawn event
            spawn_event = create_event(
                "agent_spawn",
                session_id,
                parent_session_id=parent_session_id,
                agent_depth=agent_depth,
                correlation_id=correlation_id,
                agent_type=agent_type,
                spawn_reason=description,
                task_description=prompt[:200] if prompt else description[:200]
            )
            append_event(spawn_event)

            # Update session state: increment agents_spawned counter
            increment_counter("agents_spawned")

            # Store timing marker for Task tool (enables latency calculation in PostToolUse)
            try:
                from datetime import datetime, timezone
                project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
                temp_dir = Path(project_dir) / ".claude" / "data" / "temp"
                temp_dir.mkdir(parents=True, exist_ok=True)

                timing_file = temp_dir / f"{session_id}-task-timing.txt"
                with open(timing_file, "w") as f:
                    f.write(datetime.now(timezone.utc).isoformat())
            except Exception:
                pass  # Non-blocking

        # Log pre-tool event with hierarchical context
        event = create_event(
            "tool_pre",
            session_id,
            parent_session_id=parent_session_id,
            agent_depth=agent_depth,
            correlation_id=correlation_id,
            sequence_number=sequence_number,
            tool_name=tool_name,
            tool_input=tool_input
        )
        append_event(event)

        # Return additionalContext for content-modifying tools
        additional_context = {}
        file_path = tool_input.get("file_path", "")

        if tool_name == "Write":
            if file_path.endswith(".md") and "chapters/" in file_path:
                additional_context = {
                    "guidance": "Remember to update last_updated in frontmatter when modifying chapter content",
                    "conventions": "Follow STYLE_GUIDE.md voice and structure requirements"
                }
        elif tool_name == "Edit":
            if file_path.endswith(".md") and "chapters/" in file_path:
                additional_context = {
                    "guidance": "Preserve existing frontmatter fields; update last_updated date"
                }

        # Output additionalContext for Claude Code to inject (if any)
        if additional_context:
            result = {"additionalContext": additional_context}
            print(json.dumps(result))

        # Allow the tool
        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
