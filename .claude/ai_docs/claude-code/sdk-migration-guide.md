# Migrate to Claude Agent SDK

Guide for migrating the Claude Code TypeScript and Python SDKs to the Claude Agent SDK

## Overview

The Claude Code SDK has been renamed to the **Claude Agent SDK** and its documentation has been reorganized.

## What's Changed

| Aspect                   | Old                         | New                              |
| :----------------------- | :-------------------------- | :------------------------------- |
| **Package Name (TS/JS)** | `@anthropic-ai/claude-code` | `@anthropic-ai/claude-agent-sdk` |
| **Python Package**       | `claude-code-sdk`           | `claude-agent-sdk`               |
| **Documentation Location** | Claude Code docs | API Guide → Agent SDK section |

## Migration Steps

### For TypeScript/JavaScript Projects

1. Uninstall the old package:
```bash
npm uninstall @anthropic-ai/claude-code
```

2. Install the new package:
```bash
npm install @anthropic-ai/claude-agent-sdk
```

3. Update your imports:
```typescript
// Before
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-code";

// After
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
```

### For Python Projects

1. Uninstall the old package:
```bash
pip uninstall claude-code-sdk
```

2. Install the new package:
```bash
pip install claude-agent-sdk
```

3. Update your imports:
```python
# Before
from claude_code_sdk import query, ClaudeCodeOptions

# After
from claude_agent_sdk import query, ClaudeAgentOptions
```

4. Update type names:
```python
# Before
options = ClaudeCodeOptions(model="claude-sonnet-4-5")

# After
options = ClaudeAgentOptions(model="claude-sonnet-4-5")
```

## Breaking changes

### Python: ClaudeCodeOptions renamed to ClaudeAgentOptions

```python
# BEFORE (v0.0.x)
from claude_agent_sdk import query, ClaudeCodeOptions

options = ClaudeCodeOptions(
    model="claude-sonnet-4-5",
    permission_mode="acceptEdits"
)

# AFTER (v0.1.0)
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    model="claude-sonnet-4-5",
    permission_mode="acceptEdits"
)
```

### System prompt no longer default

The SDK no longer uses Claude Code's system prompt by default.

```typescript
// BEFORE (v0.0.x) - Used Claude Code's system prompt by default
const result = query({ prompt: "Hello" });

// AFTER (v0.1.0) - Uses empty system prompt by default
// To get the old behavior:
const result = query({
  prompt: "Hello",
  options: {
    systemPrompt: { type: "preset", preset: "claude_code" }
  }
});
```

```python
# BEFORE (v0.0.x)
async for message in query(prompt="Hello"):
    print(message)

# AFTER (v0.1.0)
async for message in query(
    prompt="Hello",
    options=ClaudeAgentOptions(
        system_prompt={"type": "preset", "preset": "claude_code"}
    )
):
    print(message)
```

### Settings Sources No Longer Loaded by Default

The SDK no longer reads from filesystem settings by default.

```typescript
// BEFORE (v0.0.x) - Loaded all settings automatically

// AFTER (v0.1.0) - No settings loaded by default
// To get the old behavior:
const result = query({
  prompt: "Hello",
  options: {
    settingSources: ["user", "project", "local"]
  }
});
```

```python
# BEFORE (v0.0.x) - Loaded all settings automatically

# AFTER (v0.1.0) - No settings loaded by default
async for message in query(
    prompt="Hello",
    options=ClaudeAgentOptions(
        setting_sources=["user", "project", "local"]
    )
):
    print(message)
```

**Why this changed:** Ensures SDK applications have predictable behavior independent of local filesystem configurations. Important for:
- CI/CD environments
- Deployed applications
- Testing
- Multi-tenant systems

---

> Source: https://platform.claude.com/docs/en/agent-sdk/migration-guide
