# Hook System Installation Summary

## What Was Built

Nine hook scripts for the logging/observability system plus utility modules:

### Hook Scripts

1. **session_logging_init.py** (SessionStart hook)
   - Initializes session logging infrastructure
   - Creates session log and metadata files
   - Sets up `.claude/logs/sessions/` and `.claude/data/sessions/`

2. **user_prompt_submit.py** (UserPromptSubmit hook)
   - Logs user prompts to session JSONL
   - Updates session metadata at `.claude/data/sessions/{session_id}.json`
   - Captures prompt length and preview for analysis

3. **outcome_capture.py** (UserPromptSubmit hook)
   - Captures session outcome data for analysis
   - Works alongside user_prompt_submit.py

4. **pre_tool_use_logger.py** (PreToolUse hook)
   - Logs tool invocations BEFORE execution
   - Applies security guards (dangerous rm commands)
   - Exits with code 2 to block dangerous operations

5. **tool_usage_logger.py** (PostToolUse hook)
   - Logs tool usage AFTER execution completes
   - Captures tool results and metadata

6. **subagent_stop_logger.py** (SubagentStop hook)
   - Tracks subagent lifecycle by logging completion events
   - Captures transcript path and stop hook status

7. **pre_compact_handler.py** (PreCompact hook)
   - Backs up transcript before context compaction
   - Saves to `.claude/logs/transcript_backups/`
   - Ensures no conversation history is lost

8. **session_logging_finalize.py** (Stop hook)
   - Finalizes session logging
   - Writes session summary statistics

9. **session_evaluator.py** (Stop hook)
   - Evaluates session quality/outcomes
   - Runs after session_logging_finalize.py

### Utility Modules

1. **utils/log_writer.py**
   - `get_session_log_path()` - Get session log from environment
   - `append_to_session_log()` - Atomic JSONL append
   - `create_event()` - Create timestamped events
   - `append_event()` - Convenient event appending
   - `get_session_metadata_path()` - Get metadata file path
   - `read_session_metadata()` - Read session metadata
   - `write_session_metadata()` - Write session metadata

2. **utils/security_guards.py**
   - `is_dangerous_rm_command()` - Detect destructive rm patterns
   - `is_env_file_access()` - Detect sensitive file access
   - `get_blocked_reason()` - Get blocking reason string

3. **utils/model_extractor.py**
   - `get_model_from_transcript()` - Extract model with TTL caching
   - Cache location: `.claude/data/model-cache/{session_id}.json`

4. **utils/correlation_tracker.py**
   - Tracks correlation between events

5. **utils/prompt_classifier.py**
   - Classifies prompt types for analysis

6. **utils/status_state_manager.py**
   - Manages session status state

7. **utils/background_evaluator.py**
   - Background evaluation utilities

## Directory Structure

```
.claude/
├── hooks/
│   ├── README.md                      # Comprehensive documentation
│   ├── INSTALLATION.md                # This file
│   ├── session_logging_init.py        # SessionStart hook
│   ├── session_logging_finalize.py    # Stop hook
│   ├── session_evaluator.py           # Stop hook - session evaluation
│   ├── user_prompt_submit.py          # UserPromptSubmit hook - logs prompts
│   ├── outcome_capture.py             # UserPromptSubmit hook - captures outcomes
│   ├── pre_tool_use_logger.py         # PreToolUse hook - logs + security
│   ├── tool_usage_logger.py           # PostToolUse hook
│   ├── subagent_stop_logger.py        # SubagentStop hook
│   ├── pre_compact_handler.py         # PreCompact hook - backs up transcripts
│   └── utils/
│       ├── __init__.py
│       ├── log_writer.py              # Shared logging utilities
│       ├── security_guards.py         # Security pattern detection
│       ├── model_extractor.py         # Model extraction with caching
│       ├── correlation_tracker.py     # Event correlation tracking
│       ├── prompt_classifier.py       # Prompt type classification
│       ├── status_state_manager.py    # Session status state management
│       └── background_evaluator.py    # Background evaluation utilities
├── logs/
│   ├── sessions/                      # Per-session JSONL logs
│   ├── aggregated/                    # Aggregated analytics
│   └── transcript_backups/            # Pre-compact transcript backups
├── data/
│   ├── sessions/                      # Session metadata JSON files
│   └── model-cache/                   # Model extraction cache
└── settings.json                      # Hook configuration
```

## Configuration

The hooks are registered in `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      { "type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/session_logging_init.py", "timeout": 5000 }
    ],
    "UserPromptSubmit": [
      { "type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/user_prompt_submit.py", "timeout": 5000 },
      { "type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/outcome_capture.py", "timeout": 5000 }
    ],
    "PreToolUse": [
      { "type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/pre_tool_use_logger.py", "timeout": 3000 }
    ],
    "PostToolUse": [
      { "type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/tool_usage_logger.py", "timeout": 3000 }
    ],
    "SubagentStop": [
      { "type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/subagent_stop_logger.py", "timeout": 3000 }
    ],
    "PreCompact": [
      { "type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/pre_compact_handler.py", "timeout": 5000 }
    ],
    "Stop": [
      { "type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/session_logging_finalize.py", "timeout": 5000 },
      { "type": "command", "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/session_evaluator.py", "timeout": 2000 }
    ]
  }
}
```

## Testing

The hooks can be tested by running them manually with appropriate environment variables. Each hook expects JSON input via stdin and uses environment variables for session context.

## Event Schema

### Session Log Events (`.claude/logs/sessions/{timestamp}-{session_id}.jsonl`)

```jsonl
{"timestamp": "2025-12-10T09:10:00Z", "event": "session_start", "session_id": "abc123"}
{"timestamp": "2025-12-10T09:10:05Z", "event": "user_prompt", "session_id": "abc123", "prompt_length": 42, "prompt_preview": "Create..."}
{"timestamp": "2025-12-10T09:10:10Z", "event": "tool_pre", "session_id": "abc123", "tool_name": "Read", "tool_input": {...}}
{"timestamp": "2025-12-10T09:10:10Z", "event": "tool_blocked", "session_id": "abc123", "tool_name": "Bash", "reason": "Dangerous rm command"}
{"timestamp": "2025-12-10T09:10:11Z", "event": "tool_use", "session_id": "abc123", "tool_name": "Read", "metadata": {...}}
{"timestamp": "2025-12-10T09:10:15Z", "event": "subagent_stop", "session_id": "abc123", "transcript_path": "/path"}
{"timestamp": "2025-12-10T09:15:00Z", "event": "pre_compact", "session_id": "abc123", "trigger": "auto", "backup_path": "/path"}
{"timestamp": "2025-12-10T09:20:00Z", "event": "session_end", "session_id": "abc123", "summary": {...}}
```

### Session Metadata (`.claude/data/sessions/{session_id}.json`)

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

## Code Statistics

- **Hook Scripts**: 9 files
- **Utility Modules**: 7 files (including `__init__.py`)
- **Documentation**: README.md + INSTALLATION.md (this file)

## Features

### Logging & Observability
- ✓ Session lifecycle tracking
- ✓ User prompt logging with metadata
- ✓ Pre-tool execution logging
- ✓ Post-tool execution logging
- ✓ Subagent lifecycle tracking
- ✓ Transcript backup before compaction
- ✓ Session summary statistics

### Security
- ✓ Dangerous rm command detection and blocking
- ✓ .env file access detection (optional, commented out)
- ✓ Security event audit trail
- ✓ Exit code 2 for blocking operations

### Data Management
- ✓ JSONL event streaming for easy parsing
- ✓ Per-session metadata files
- ✓ Model extraction with TTL caching
- ✓ Automatic directory creation
- ✓ Non-blocking error handling

## Usage

The hooks are automatically invoked by Claude Code during normal operation. No manual intervention required.

### Viewing Session Logs

```bash
# View latest session log
ls -lt .claude/logs/sessions/ | head -1

# View session events
cat .claude/logs/sessions/{timestamp}-{session_id}.jsonl | jq .

# Count tool usage
cat .claude/logs/sessions/*.jsonl | grep '"event": "tool_use"' | jq -r .tool_name | sort | uniq -c
```

### Checking Session Metadata

```bash
# View session metadata
cat .claude/data/sessions/{session_id}.json | jq .

# List all sessions
ls -lt .claude/data/sessions/
```

### Viewing Transcript Backups

```bash
# List backups
ls -lt .claude/logs/transcript_backups/

# View a backup
cat .claude/logs/transcript_backups/{session_id}_pre_compact_*.jsonl | jq .
```

## Next Steps

The hook system is fully operational and ready for production use. Future enhancements could include:

1. **Analytics Dashboard** - Visualize tool usage patterns, session metrics
2. **Alerting** - Notify on excessive tool usage, security events
3. **Log Aggregation** - Combine session logs for cross-session analysis
4. **Performance Metrics** - Track tool execution times, latency
5. **Cost Tracking** - Estimate API costs based on model usage

## References

- Hook Documentation: `.claude/hooks/README.md`
- Test Suite: `.claude/hooks/test_hooks.sh`
- Settings: `.claude/settings.json`
- Project Root: `/Users/jayminwest/Projects/agentic-engineering-knowledge-base`
