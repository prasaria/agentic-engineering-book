# Hooks reference

> Reference documentation for implementing hooks in Claude Code.

## Configuration

Claude Code hooks are configured in your settings files:

* `~/.claude/settings.json` - User settings
* `.claude/settings.json` - Project settings
* `.claude/settings.local.json` - Local project settings (not committed)
* Enterprise managed policy settings

### Structure

Hooks are organized by matchers, where each matcher can have multiple hooks:

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",
        "hooks": [
          {
            "type": "command",
            "command": "your-command-here"
          }
        ]
      }
    ]
  }
}
```

* **matcher**: Pattern to match tool names, case-sensitive (only for `PreToolUse`, `PermissionRequest`, and `PostToolUse`)
  * Simple strings match exactly: `Write` matches only the Write tool
  * Supports regex: `Edit|Write` or `Notebook.*`
  * Use `*` to match all tools
* **hooks**: Array of hooks to execute
  * `type`: `"command"` for bash commands or `"prompt"` for LLM-based evaluation
  * `command`: The bash command to execute
  * `prompt`: The prompt to send to the LLM
  * `timeout`: Optional timeout in seconds

### Project-Specific Hook Scripts

Use `CLAUDE_PROJECT_DIR` to reference scripts in your project:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/check-style.sh"
          }
        ]
      }
    ]
  }
}
```

## Prompt-Based Hooks

Prompt-based hooks (`type: "prompt"`) use an LLM to evaluate whether to allow or block an action. Currently only supported for `Stop` and `SubagentStop` hooks.

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Evaluate if Claude should stop: $ARGUMENTS. Check if all tasks are complete."
          }
        ]
      }
    ]
  }
}
```

### Response schema

```json
{
  "decision": "approve" | "block",
  "reason": "Explanation for the decision",
  "continue": false,
  "stopReason": "Message shown to user",
  "systemMessage": "Warning or context"
}
```

## Hook Events

### PreToolUse

Runs after Claude creates tool parameters and before processing the tool call.

**Common matchers**: `Task`, `Bash`, `Glob`, `Grep`, `Read`, `Edit`, `Write`, `WebFetch`, `WebSearch`

### PermissionRequest

Runs when the user is shown a permission dialog.

### PostToolUse

Runs immediately after a tool completes successfully.

### Notification

Runs when Claude Code sends notifications.

**Common matchers**: `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog`

### UserPromptSubmit

Runs when the user submits a prompt, before Claude processes it.

### Stop

Runs when the main Claude Code agent has finished responding.

### SubagentStop

Runs when a Claude Code subagent (Task tool call) has finished responding.

### PreCompact

Runs before Claude Code is about to run a compact operation.

**Matchers**: `manual`, `auto`

### SessionStart

Runs when Claude Code starts a new session or resumes an existing session.

**Matchers**: `startup`, `resume`, `clear`, `compact`

#### Persisting environment variables

SessionStart hooks have access to `CLAUDE_ENV_FILE` for persisting environment variables:

```bash
#!/bin/bash
if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=production' >> "$CLAUDE_ENV_FILE"
fi
exit 0
```

### SessionEnd

Runs when a Claude Code session ends.

The `reason` field will be: `clear`, `logout`, `prompt_input_exit`, or `other`

## Hook Input

Hooks receive JSON data via stdin:

```typescript
{
  session_id: string
  transcript_path: string
  cwd: string
  permission_mode: string
  hook_event_name: string
  // Event-specific fields...
}
```

## Hook Output

### Simple: Exit Code

* **Exit code 0**: Success
* **Exit code 2**: Blocking error
* **Other exit codes**: Non-blocking error

### Advanced: JSON Output

Hooks can return structured JSON for more control:

```json
{
  "continue": true,
  "stopReason": "string",
  "suppressOutput": true,
  "systemMessage": "string"
}
```

#### PreToolUse Decision Control

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow" | "deny" | "ask",
    "permissionDecisionReason": "My reason here",
    "updatedInput": {
      "field_to_modify": "new value"
    }
  }
}
```

#### PostToolUse Decision Control

```json
{
  "decision": "block",
  "reason": "Explanation for decision",
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "Additional information for Claude"
  }
}
```

#### Stop/SubagentStop Decision Control

```json
{
  "decision": "block",
  "reason": "Must be provided when Claude is blocked from stopping"
}
```

## Hook Execution Details

* **Timeout**: 60-second execution limit by default, configurable per command
* **Parallelization**: All matching hooks run in parallel
* **Deduplication**: Multiple identical hook commands are deduplicated
* **Environment**: Runs in current directory with Claude Code's environment
  * `CLAUDE_PROJECT_DIR`: Absolute path to the project root
  * `CLAUDE_CODE_REMOTE`: Indicates remote vs local environment

## Security Considerations

**USE AT YOUR OWN RISK**: Claude Code hooks execute arbitrary shell commands on your system.

### Security Best Practices

1. Validate and sanitize inputs
2. Always quote shell variables (`"$VAR"` not `$VAR`)
3. Block path traversal (check for `..` in file paths)
4. Use absolute paths
5. Skip sensitive files (`.env`, `.git/`, keys)

### Configuration Safety

Direct edits to hooks in settings files don't take effect immediately. Claude Code:
1. Captures a snapshot of hooks at startup
2. Uses this snapshot throughout the session
3. Warns if hooks are modified externally
4. Requires review in `/hooks` menu for changes to apply

## Debugging

### Basic Troubleshooting

1. Check configuration with `/hooks`
2. Verify JSON syntax
3. Test commands manually
4. Check script permissions
5. Review logs with `claude --debug`

Common issues:
* Quotes not escaped
* Wrong matcher (case-sensitive)
* Command not found (use full paths)

---

> Source: https://code.claude.com/docs/en/hooks
> Updated: 2025-12-25
