---
title: Debugging Agents
description: Finding and fixing what went wrong in agentic systems
created: 2025-12-08
last_updated: 2025-12-10
tags: [practices, debugging, troubleshooting]
part: 2
part_title: Craft
chapter: 7
section: 1
order: 2.7.1
---

# Debugging Agents

Agents fail in ways that traditional software doesn't. The debugging skills are different too.

---

## Anti-Patterns

### Debugging Without Logs
**What it looks like**: Agent fails. The engineer stares at the prompt and tries to guess what went wrong. Changes are made based on intuition rather than data.

**Why it fails**:
- Debugging the theory of what happened, not what actually happened
- Intermittent failures are impossible to diagnose
- Can't distinguish "agent didn't try" from "agent tried and failed"
- Waste time fixing problems that don't exist

**Better alternative**: Instrument before debugging. Add logging at decision points, tool calls, and validation gates. Use event logs to trace execution. Read agent outputs and intermediate states. Debug the data, not the mental model.

### Changing Multiple Things at Once
**What it looks like**: Agent isn't working right. The engineer simultaneously changes the prompt structure, swaps the model, adjusts the context window, and modifies the tool permissions. One of those fixes it—but which one?

**Why it fails**:
- Can't identify root cause
- Might have fixed one thing but broken another
- No reproducible solution to apply elsewhere
- Regression hunting becomes impossible

**Better alternative**: Change one variable at a time. Make a hypothesis, change only what tests that hypothesis, verify the impact. If that didn't work, revert and try the next hypothesis. Keep notes on what was tried.

### Not Reproducing Before Fixing
**What it looks like**: Agent failed once. The engineer makes a change without verifying the original failure can be reproduced or that the fix prevents it.

**Why it fails**:
- "Fix" might do nothing, failure was intermittent
- Can't tell if future failures are regressions or new issues
- No confidence the problem is actually solved
- Accumulate superstitious fixes that don't address real problems

**Better alternative**: First, reproduce the failure reliably (even if just 2-3 times in a row). Document the repro steps. Then make the fix. Then verify the fix prevents the failure in 5+ consecutive runs. Without reproduction, there's no verification.

### Assuming It's the Model
**What it looks like**: Agent produces wrong output. Model capability gets blamed immediately: "Haiku isn't smart enough for this" or "Opus hallucinates here." Switch to bigger/newer model without investigating further.

**Why it fails**:
- Most agent failures are prompt, context, or tool issues, not model capability
- Bigger models are slower and more expensive
- Doesn't fix the actual problem—new model often fails the same way
- Misses learning opportunity about prompt design

**Better alternative**: Check the other "core four" first. Is the instruction clear? Does the agent have the right context? Are tools working correctly? Is the output format well-specified? Model capability is usually the last resort, not the first suspect.

### Debugging in Production
**What it looks like**: Agent fails in production. The engineer modifies the production prompt to add debugging output or try different approaches. Iteration happens on the live system.

**Why it fails**:
- Every iteration affects real users or systems
- Can't experiment freely without consequences
- Pressure leads to quick hacks instead of root cause fixes
- Lost changes if rollback is needed

**Better alternative**: Reproduce the failure locally or in a dev environment. Use production logs to understand the failure mode, but fix and test in isolation. Only deploy to production after verifying the fix in a safe environment.

### Ignoring Partial Successes
**What it looks like**: Agent works 70% of the time, fails 30%. Focus goes only to the failures, trying to fix what went wrong. Successes are never analyzed for what makes them different.

**Why it fails**:
- Successes often show what conditions enable correct behavior
- Failure analysis alone doesn't reveal missing prerequisites
- Can't identify environmental or input patterns that matter
- Miss the insight that "it works when X is true"

**Better alternative**: Compare successes to failures. What's different about the inputs, context, or environment when it works? Often the pattern is "succeeds when context includes Y" or "fails when input is ambiguous." This points directly to the fix.

### The Infinite Retry Loop
**What it looks like**: Add retry logic to handle intermittent failures. Agent fails, retries, fails, retries... infinitely, never surfacing the underlying issue.

**Why it fails**:
- Masks systemic problems with tactical patches
- Wastes tokens and time on doomed attempts
- No signal to humans that something is fundamentally broken
- Logs fill with noise, hiding real issues

**Better alternative**: Limit retries (2-3 max). On persistent failure, escalate to human or halt with detailed error. Log each retry with context. If retries are frequently triggered, that's a signal to fix the root cause, not increase the retry limit.

---

## Connections

- **To [Evaluation](2-evaluation.md):** How does systematic eval help with debugging?
- **To [Prompt](../2-prompt/_index.md):** When is the prompt the bug?
- **To [Context](../4-context/_index.md):** When is missing or wrong context the bug?

---

## Debugging War Stories

*Document specific debugging sessions—what happened, how you figured it out:*

### Multi-Agent Debugging Strategies

*[2025-12-09]*: Multi-agent systems have distinct failure modes that require different debugging approaches than single-agent systems.

**Check Single-Message Parallelism First**

When parallel agents run slower than expected or produce suspiciously sequential results, check whether they were invoked in a single message. This is the most common multi-agent debugging issue—developers expect parallelism but the framework serializes execution because Task calls were spread across multiple messages. Look at your orchestrator's outputs: are all parallel Task calls in one response?

**Graceful Degradation Patterns**

Multi-agent systems should degrade gracefully when individual agents fail:
- If one expert fails, note the failure and continue with available analyses
- Recommend manual review for failed expert domains
- Include recovery instructions in output
- Don't let one failing subagent tank the entire workflow

Implement this by checking subagent return status before synthesis. The orchestrator should be resilient to partial failures.

**Partial Success Handling**

Unlike single-agent (which either works or doesn't), multi-agent systems have complex success states:
- Commit successful changes before reporting failures
- Allow selective retry via phase parameters
- Never leave the workflow in an inconsistent state
- Track which subagents succeeded vs. failed

**Use Hooks to Trace Agent Transitions**

SubagentStop hooks record what each subagent produced. ErrorEscalation surfaces failures to the orchestrator. These create an audit trail for debugging:
- Which subagent ran when?
- What did it return?
- Where did it fail?

Without these hooks, multi-agent failures are nearly impossible to diagnose.

**Domain Isolation Debugging**

Each agent stays focused on its domain and doesn't need to know about other agents. If you see cross-domain confusion, something is leaking context incorrectly. The orchestrator is responsible for synthesis—individual experts should be testable in isolation.

**Coordination vs. Agent Failures**

Two distinct failure modes:
1. **Agent failure**: Individual subagent does wrong thing (debug like single-agent)
2. **Coordination failure**: Orchestrator routes incorrectly, synthesizes badly, or mismanages state

For coordination failures, the problem is usually in the orchestrator prompt or the spec file, not in the subagents themselves. Test subagents in isolation to rule out agent-level issues before debugging coordination.

**Sources**: [Orchestrator Pattern](../6-patterns/3-orchestrator-pattern.md), [Building agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)

---

## Testing and Debugging Hooks

Hooks are automation that runs at specific events in your workflow. When they break, they're invisible—the system just doesn't behave as expected. Here's how to diagnose and fix hook issues.

### Manual Hook Testing

Test hooks outside of Claude Code before deploying them. This isolates hook logic from the rest of the system.

**Basic Testing Pattern:**

```bash
# Pipe JSON to stdin
echo '{"prompt": "/orchestrators:test"}' | python .claude/hooks/orchestrator_context.py

# Check exit code
echo $?

# Test with project environment variables
cd /path/to/project
CLAUDE_PROJECT_DIR=$(pwd) echo '{"tool_name": "Write"}' | python .claude/hooks/orchestrator_guard.py
```

**Testing with Realistic Input:**

Create test JSON files that mirror what Claude Code actually sends:

```bash
# test-pretool-input.json
{
  "sessionId": "test-123",
  "projectDir": "/Users/jayminwest/Projects/agentic-engineering-knowledge-base",
  "tool_name": "Write",
  "parameters": {
    "file_path": "/path/to/file.md",
    "content": "test content"
  }
}

# Test the hook
cat test-pretool-input.json | python .claude/hooks/orchestrator_guard.py
```

**Verifying Exit Codes:**

Exit codes control hook behavior:
- **Exit 0**: Success, allow operation
- **Exit 2**: Block operation, show stderr to Claude
- **Other**: Non-blocking error, visible in debug mode only

```bash
# Test blocking behavior
cat test-input.json | python hook.py
if [ $? -eq 2 ]; then
  echo "Hook correctly blocked the operation"
fi
```

**Testing Environment File Interaction:**

For hooks that read/write `CLAUDE_ENV_FILE`, test with a temporary file:

```bash
# Create temp environment file
export CLAUDE_ENV_FILE=$(mktemp)

# Run hook that writes to env file
echo '{"prompt": "/orchestrators:knowledge test"}' | python .claude/hooks/orchestrator_context.py

# Verify what was written
cat "$CLAUDE_ENV_FILE"

# Clean up
rm "$CLAUDE_ENV_FILE"
```

### Debugging Hook Issues

**Use Debug Mode:**

Run Claude Code with the `--debug` flag to see detailed hook execution:

```bash
claude --debug
```

This shows:
- Which hooks are triggered
- stdin/stdout/stderr content
- Exit codes
- Execution timing
- Decision results

**Use `/hooks` Command:**

Inside Claude Code, run `/hooks` to see all registered hooks and their configuration. This confirms:
- Hook is properly registered
- Matcher patterns are correct
- Hook file paths are valid
- Multiple hooks aren't conflicting

**Common Hook Issues:**

**1. Hook Not Running:**

Check matcher patterns. If you have:

```json
{
  "matcher": "Write",
  "type": "command",
  "command": "python hook.py"
}
```

This only matches the exact tool name "Write". It won't match "Edit" or "MultiEdit". Use wildcards for broader matching:

```json
{
  "matchers": ["Write", "Edit", "MultiEdit"]
}
```

**2. Timeout Errors:**

Default timeouts may be too short for complex hooks. Increase the timeout:

```json
{
  "type": "command",
  "command": "python slow-hook.py",
  "timeout": 30000
}
```

If timeouts persist, optimize the hook script. Hooks should complete in seconds, not minutes.

**3. JSON Parse Errors:**

Hooks must handle malformed JSON gracefully:

```python
try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError:
    # Don't crash - allow operation to continue
    sys.exit(0)
```

Crashing on bad JSON breaks Claude Code's workflow. Exit 0 to allow operations when you can't parse input.

**4. Permission Denied:**

Hook scripts must be executable:

```bash
chmod +x .claude/hooks/orchestrator_context.py
```

If using `#!/usr/bin/env -S uv run --script`, ensure `uv` is installed and in PATH.

### Verifying Orchestrator Enforcement

The orchestrator pattern uses two hooks working together:
1. `orchestrator_context.py` (UserPromptSubmit) - Sets context when orchestrator commands run
2. `orchestrator_guard.py` (PreToolUse) - Blocks Write/Edit tools in orchestrator context

**Verify Context is Set:**

When you run `/orchestrators:knowledge` or `/questions:orchestrator`, check that the context is set:

```bash
# During a Claude Code session, in another terminal:
cat "$HOME/.claude/env/session-<id>.env"

# Should contain:
# export CLAUDE_ORCHESTRATOR_CONTEXT="knowledge"
```

The session ID can be found via `/hooks` output or by listing `~/.claude/env/` files sorted by modification time.

**Verify Tools are Blocked:**

When orchestrator context is active, attempting to use Write or Edit should fail with a clear error message:

```
BLOCKED: Orchestrator 'knowledge' cannot use Write directly.
Delegate to a build agent using the Task tool instead.
Example: Task(subagent_type='knowledge-build-agent', prompt='...')
```

If you're not seeing this error when you should, check:
1. Is `CLAUDE_ORCHESTRATOR_CONTEXT` actually set in the env file?
2. Is the PreToolUse hook registered? (use `/hooks` to verify)
3. Is the hook script executable and working? (test manually)

**What to Look For in Error Messages:**

Good hook errors should:
- Identify the problem clearly: "BLOCKED: Orchestrator 'X' cannot use Y"
- Explain why: "Delegate to a build agent"
- Show how to fix it: "Example: Task(...)"

If errors are vague or missing, add better error messages to your hooks. Write to stderr for blocking errors:

```python
print(
    f"BLOCKED: Orchestrator '{orchestrator}' cannot use {tool_name} directly.\n"
    f"Delegate to a build agent using the Task tool instead.\n"
    f"Example: Task(subagent_type='knowledge-build-agent', prompt='...')",
    file=sys.stderr
)
sys.exit(2)
```

### Hook Logging Pattern

Hooks are hard to debug because they're invisible during normal operation. Add logging to understand what's happening.

**Logging to File:**

Don't use stdout (it becomes context for Claude). Write to a log file instead:

```python
import json
import sys
from pathlib import Path
from datetime import datetime

LOG_FILE = Path.home() / ".claude" / "logs" / "orchestrator_guard.log"

def log_hook_execution(message: str, data: dict = None):
    """Log hook execution for debugging."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] {message}"

    if data:
        log_entry += f"\n{json.dumps(data, indent=2)}"

    with LOG_FILE.open("a") as f:
        f.write(log_entry + "\n\n")

def main():
    try:
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")

        log_hook_execution("PreToolUse triggered", {
            "tool": tool_name,
            "orchestrator": get_orchestrator_context()
        })

        # ... rest of hook logic

    except Exception as e:
        log_hook_execution(f"Hook error: {e}")
        sys.exit(0)
```

**What to Log:**

Log decision points, not every line:
- Hook triggered (with input summary)
- Context detected (orchestrator name, environment state)
- Decisions made (allow/block, why)
- Errors encountered

**Reviewing Logs:**

Tail the log during a Claude Code session:

```bash
tail -f ~/.claude/logs/orchestrator_guard.log
```

This shows hook execution in real-time, helping you understand:
- Which hooks are actually running
- What input they're receiving
- What decisions they're making
- Where errors occur

**Log Rotation:**

Hook logs can grow large. Implement basic rotation:

```python
def rotate_log_if_needed():
    """Keep log file under 1MB."""
    if LOG_FILE.exists() and LOG_FILE.stat().st_size > 1_000_000:
        # Move old log to backup
        backup = LOG_FILE.with_suffix(".log.old")
        LOG_FILE.rename(backup)
```

**Conditional Logging:**

Enable detailed logging only when debugging:

```python
DEBUG = os.environ.get("CLAUDE_HOOK_DEBUG", "false") == "true"

def log_hook_execution(message: str, data: dict = None):
    if not DEBUG:
        return
    # ... logging code
```

Then enable when needed:

```bash
export CLAUDE_HOOK_DEBUG=true
claude --debug
```

This keeps logs clean during normal operation while providing detail when troubleshooting.

---


