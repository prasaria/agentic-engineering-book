# Claude Code Hooks

This directory contains hook scripts that integrate with Claude Code's lifecycle events to provide logging, observability, and security features.

## Hook Scripts

### Session Lifecycle

#### `session_logging_init.py` (SessionStart)
- Initializes logging infrastructure at session start
- Creates `.claude/logs/sessions/` directory structure
- Initializes per-session JSONL file with timestamp prefix
- Writes initial session context record
- Sets `CLAUDE_SESSION_LOG` environment variable

#### `session_logging_finalize.py` (Stop)
- Processes session logs and writes summary statistics
- Computes tool usage frequency, agent spawning patterns
- Appends session end event with summary metadata
- Runs when the main agent stops (not subagents)

#### `session_evaluator.py` (Stop)
- Ensures sessions without explicit outcome get defaulted to "null"
- Checks if outcome already recorded via /success, /failure, or /null commands
- Records outcome="null" with reason="unrated" for sessions without feedback
- Spawns background evaluator for session analysis (non-blocking)
- Background evaluator extracts insights to session-insights.jsonl

#### `outcome_capture.py` (UserPromptSubmit)
- Captures user-provided session outcomes (/success, /failure, /null)
- Analyzes session logs for metrics (duration, tool count, agents spawned)
- Stores full session data to learnings/sessions/{session_id}.json
- Appends outcome summary to learnings/outcomes.jsonl
- Extracts transcript summary from ~/.claude/projects/{hash}/{session_id}.jsonl

### User Interaction

#### `user_prompt_submit.py` (UserPromptSubmit)
- Logs user prompts to session JSONL
- Updates session metadata file at `.claude/data/sessions/{session_id}.json`
- Captures prompt length and preview for analysis
- Enables conversation flow tracking and prompt complexity analysis

### Tool Execution

#### `pre_tool_use_logger.py` (PreToolUse)
- Logs tool invocations BEFORE execution
- Applies security guards (dangerous rm commands, .env file access)
- Exits with code 2 to block dangerous commands
- Logs blocked events for security audit trail

#### `tool_usage_logger.py` (PostToolUse)
- Logs tool invocations AFTER successful execution
- Redacts sensitive parameters (content, new_string, command)
- Extracts metadata for analysis (file paths, patterns, URLs)
- Enables tool usage frequency and performance profiling

### Agent Lifecycle

#### `subagent_stop_logger.py` (SubagentStop)
- Tracks subagent lifecycle by logging completion events
- Captures transcript path and stop hook status
- Enables agent spawning frequency and delegation pattern analysis

### Context Management

#### `pre_compact_handler.py` (PreCompact)
- Backs up transcript before context compaction
- Saves to `.claude/logs/transcript_backups/{session_id}_pre_compact_{trigger}_{timestamp}.jsonl`
- Logs compaction events with backup path
- Ensures no conversation history is lost during compaction

## Utility Modules

### `utils/log_writer.py`
Shared logging utilities for JSONL append operations:
- `get_session_log()` - Get session log path from environment
- `append_event(event)` - Append event to session log
- `create_event(type, session_id, **kwargs)` - Create timestamped event
- `get_session_metadata_path(session_id)` - Get metadata file path
- `read_session_metadata(session_id)` - Read session metadata
- `write_session_metadata(session_id, metadata)` - Write session metadata

### `utils/security_guards.py`
Security guard functions for dangerous operation detection:
- `is_dangerous_rm_command(command)` - Detect destructive rm patterns
- `is_env_file_access(tool_name, tool_input)` - Detect sensitive file access
- `get_blocked_reason(tool_name, tool_input)` - Get blocking reason string

### `utils/model_extractor.py`
Model name extraction from transcripts with TTL caching:
- `get_model_from_transcript(session_id, transcript_path, ttl)` - Extract model with caching

### `utils/background_evaluator.py`
Background session analysis (runs detached from main session):
- `analyze_session(session_log_path)` - Extract metrics and patterns from session
- `append_insight(insights_path, insight)` - Append insight to session-insights.jsonl
- Identifies notable patterns: high_agent_spawn, long_session, read_heavy, write_heavy, orchestrator_usage, quick_session
- Runs asynchronously to avoid blocking session shutdown

## Log Output Structure

### Session Logs (`.claude/logs/sessions/{timestamp}-{session_id}.jsonl`)
Newline-delimited JSON with these event types:

```jsonl
{"timestamp": "2025-12-10T09:10:00Z", "event": "session_start", "session_id": "abc123", "project_dir": "/path/to/project"}
{"timestamp": "2025-12-10T09:10:05Z", "event": "user_prompt", "session_id": "abc123", "prompt_length": 42, "prompt_preview": "Create a new feature..."}
{"timestamp": "2025-12-10T09:10:10Z", "event": "tool_pre", "session_id": "abc123", "tool_name": "Read", "tool_input": {...}}
{"timestamp": "2025-12-10T09:10:11Z", "event": "tool_use", "session_id": "abc123", "tool_name": "Read", "metadata": {...}, "status": "invoked"}
{"timestamp": "2025-12-10T09:10:15Z", "event": "subagent_stop", "session_id": "abc123", "transcript_path": "/path/to/transcript.jsonl"}
{"timestamp": "2025-12-10T09:15:00Z", "event": "pre_compact", "session_id": "abc123", "trigger": "auto", "backup_path": "/path/to/backup.jsonl"}
{"timestamp": "2025-12-10T09:20:00Z", "event": "session_end", "session_id": "abc123", "summary": {...}}
```

### Session Metadata (`.claude/data/sessions/{session_id}.json`)
Per-session metadata for quick access:

```json
{
  "session_id": "abc123",
  "started_at": "2025-12-10T09:10:00Z",
  "prompts": [
    {
      "timestamp": "2025-12-10T09:10:05Z",
      "preview": "Create a new feature...",
      "length": 42
    }
  ]
}
```

## Configuration

Hooks are configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {"type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/session_logging_init.py", "timeout": 5000}
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {"type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/user_prompt_submit.py", "timeout": 5000}
        ]
      },
      {
        "hooks": [
          {"type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/outcome_capture.py", "timeout": 5000}
        ]
      }
    ],
    "PreToolUse": [
      {
        "hooks": [
          {"type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/pre_tool_use_logger.py", "timeout": 3000}
        ]
      }
    ],
    "PostToolUse": [
      {
        "hooks": [
          {"type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/tool_usage_logger.py", "timeout": 3000}
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [
          {"type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/subagent_stop_logger.py", "timeout": 3000}
        ]
      }
    ],
    "PreCompact": [
      {
        "hooks": [
          {"type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/pre_compact_handler.py", "timeout": 5000}
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {"type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/session_logging_finalize.py", "timeout": 5000}
        ]
      },
      {
        "hooks": [
          {"type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/session_evaluator.py", "timeout": 2000}
        ]
      }
    ]
  }
}
```

## Hook Execution Pattern

All hooks follow this pattern:

1. **Shebang**: `#!/usr/bin/env -S uv run --script`
2. **Script metadata**: `# /// script` with Python version requirement
3. **JSON input**: Read from stdin with `json.load(sys.stdin)`
4. **Session log**: Get from `os.environ.get("CLAUDE_SESSION_LOG")`
5. **Exit codes**:
   - `0` - Success, allow operation (default)
   - `2` - Block operation (security guard)
6. **Non-blocking**: Always exit 0 except for security blocks
7. **Error handling**: Catch all exceptions to prevent hook failures

## Security Features

### Dangerous Command Detection
- Recursive file deletion patterns (`rm -rf`)
- Root directory targeting
- Home directory references
- Wildcard expansion in dangerous contexts

### Sensitive File Protection (Optional)
- `.env` file access detection
- Credentials file patterns
- Secret/token content scanning

## Analysis Use Cases

The logging system enables:

1. **Tool usage patterns** - Which tools are most frequently used
2. **Performance profiling** - Identify slow operations
3. **Agent delegation analysis** - Track subagent spawning patterns
4. **Security auditing** - Review blocked operations
5. **Conversation flow** - Understand user interaction patterns
6. **Compaction frequency** - Monitor context management
7. **Session metrics** - Duration, tool count, agent count

## Development

When adding new hooks:

1. Follow the uv run script pattern from existing hooks
2. Be non-blocking (exit 0) except for security blocks (exit 2)
3. Import utils from relative path: `from utils.log_writer import ...`
4. Add comprehensive docstrings explaining purpose and data captured
5. Update this README with the new hook documentation
6. Update `.claude/settings.json` to register the hook
