# Agent SDK reference - Python

Complete API reference for the Python Agent SDK, including all functions, types, and classes.

## Installation

```bash
pip install claude-agent-sdk
```

## Choosing Between `query()` and `ClaudeSDKClient`

| Feature             | `query()`                     | `ClaudeSDKClient`                  |
| :------------------ | :---------------------------- | :--------------------------------- |
| **Session**         | Creates new session each time | Reuses same session                |
| **Conversation**    | Single exchange               | Multiple exchanges in same context |
| **Streaming Input** | Supported                     | Supported                          |
| **Interrupts**      | Not supported                 | Supported                          |
| **Hooks**           | Not supported                 | Supported                          |
| **Custom Tools**    | Not supported                 | Supported                          |
| **Use Case**        | One-off tasks                 | Continuous conversations           |

## Functions

### `query()`

Creates a new session for each interaction with Claude Code. Returns an async iterator that yields messages.

```python
async def query(
    *,
    prompt: str | AsyncIterable[dict[str, Any]],
    options: ClaudeAgentOptions | None = None
) -> AsyncIterator[Message]
```

#### Example

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    options = ClaudeAgentOptions(
        system_prompt="You are an expert Python developer",
        permission_mode='acceptEdits',
        cwd="/home/user/project"
    )

    async for message in query(
        prompt="Create a Python web server",
        options=options
    ):
        print(message)

asyncio.run(main())
```

### `tool()`

Decorator for defining MCP tools with type safety.

```python
from claude_agent_sdk import tool
from typing import Any

@tool("greet", "Greet a user", {"name": str})
async def greet(args: dict[str, Any]) -> dict[str, Any]:
    return {
        "content": [{
            "type": "text",
            "text": f"Hello, {args['name']}!"
        }]
    }
```

### `create_sdk_mcp_server()`

Create an in-process MCP server.

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("add", "Add two numbers", {"a": float, "b": float})
async def add(args):
    return {
        "content": [{
            "type": "text",
            "text": f"Sum: {args['a'] + args['b']}"
        }]
    }

calculator = create_sdk_mcp_server(
    name="calculator",
    version="2.0.0",
    tools=[add]
)

options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator},
    allowed_tools=["mcp__calc__add"]
)
```

## Classes

### `ClaudeSDKClient`

Maintains a conversation session across multiple exchanges.

```python
class ClaudeSDKClient:
    def __init__(self, options: ClaudeAgentOptions | None = None)
    async def connect(self, prompt: str | AsyncIterable[dict] | None = None) -> None
    async def query(self, prompt: str | AsyncIterable[dict], session_id: str = "default") -> None
    async def receive_messages(self) -> AsyncIterator[Message]
    async def receive_response(self) -> AsyncIterator[Message]
    async def interrupt(self) -> None
    async def rewind_files(self, user_message_uuid: str) -> None
    async def disconnect(self) -> None
```

#### Example - Continuing a conversation

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock

async def main():
    async with ClaudeSDKClient() as client:
        await client.query("What's the capital of France?")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # Follow-up - Claude remembers context
        await client.query("What's the population of that city?")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

asyncio.run(main())
```

## Types

### `ClaudeAgentOptions`

Configuration dataclass for Claude Code queries.

| Property                      | Type                                         | Default              | Description                                                    |
| :---------------------------- | :------------------------------------------- | :------------------- | :------------------------------------------------------------- |
| `allowed_tools`               | `list[str]`                                  | `[]`                 | List of allowed tool names                                     |
| `system_prompt`               | `str \| SystemPromptPreset \| None`          | `None`               | System prompt configuration                                    |
| `mcp_servers`                 | `dict[str, McpServerConfig] \| str \| Path`  | `{}`                 | MCP server configurations                                      |
| `permission_mode`             | `PermissionMode \| None`                     | `None`               | Permission mode for tool usage                                 |
| `continue_conversation`       | `bool`                                       | `False`              | Continue the most recent conversation                          |
| `resume`                      | `str \| None`                                | `None`               | Session ID to resume                                           |
| `max_turns`                   | `int \| None`                                | `None`               | Maximum conversation turns                                     |
| `model`                       | `str \| None`                                | `None`               | Claude model to use                                            |
| `cwd`                         | `str \| Path \| None`                        | `None`               | Current working directory                                      |
| `hooks`                       | `dict[HookEvent, list[HookMatcher]] \| None` | `None`               | Hook configurations                                            |
| `agents`                      | `dict[str, AgentDefinition] \| None`         | `None`               | Programmatically defined subagents                             |
| `setting_sources`             | `list[SettingSource] \| None`                | `None`               | Control which filesystem settings to load                      |

### `PermissionMode`

```python
PermissionMode = Literal[
    "default",           # Standard permission behavior
    "acceptEdits",       # Auto-accept file edits
    "plan",              # Planning mode - no execution
    "bypassPermissions"  # Bypass all permission checks
]
```

### `SettingSource`

```python
SettingSource = Literal["user", "project", "local"]
```

| Value       | Description                    | Location                      |
| :---------- | :----------------------------- | :---------------------------- |
| `"user"`    | Global user settings           | `~/.claude/settings.json`     |
| `"project"` | Shared project settings        | `.claude/settings.json`       |
| `"local"`   | Local project settings         | `.claude/settings.local.json` |

### `AgentDefinition`

```python
@dataclass
class AgentDefinition:
    description: str
    prompt: str
    tools: list[str] | None = None
    model: Literal["sonnet", "opus", "haiku", "inherit"] | None = None
```

## Message Types

### `Message`

```python
Message = UserMessage | AssistantMessage | SystemMessage | ResultMessage
```

### `ResultMessage`

```python
@dataclass
class ResultMessage:
    subtype: str
    duration_ms: int
    duration_api_ms: int
    is_error: bool
    num_turns: int
    session_id: str
    total_cost_usd: float | None = None
    usage: dict[str, Any] | None = None
    result: str | None = None
```

## Content Block Types

```python
ContentBlock = TextBlock | ThinkingBlock | ToolUseBlock | ToolResultBlock
```

## Error Types

```python
class ClaudeSDKError(Exception): ...
class CLINotFoundError(CLIConnectionError): ...
class CLIConnectionError(ClaudeSDKError): ...
class ProcessError(ClaudeSDKError): ...
class CLIJSONDecodeError(ClaudeSDKError): ...
```

## Hook Types

```python
HookEvent = Literal[
    "PreToolUse",
    "PostToolUse",
    "UserPromptSubmit",
    "Stop",
    "SubagentStop",
    "PreCompact"
]

HookCallback = Callable[
    [dict[str, Any], str | None, HookContext],
    Awaitable[dict[str, Any]]
]
```

### Hook Usage Example

```python
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher, HookContext
from typing import Any

async def validate_bash_command(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    if input_data['tool_name'] == 'Bash':
        command = input_data['tool_input'].get('command', '')
        if 'rm -rf /' in command:
            return {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': 'Dangerous command blocked'
                }
            }
    return {}

options = ClaudeAgentOptions(
    hooks={
        'PreToolUse': [
            HookMatcher(matcher='Bash', hooks=[validate_bash_command])
        ]
    }
)
```

## Sandbox Configuration

```python
sandbox_settings: SandboxSettings = {
    "enabled": True,
    "autoAllowBashIfSandboxed": True,
    "excludedCommands": ["docker"],
    "network": {
        "allowLocalBinding": True,
        "allowUnixSockets": ["/var/run/docker.sock"]
    }
}

async for message in query(
    prompt="Build and test my project",
    options=ClaudeAgentOptions(sandbox=sandbox_settings)
):
    print(message)
```

---

> Source: https://platform.claude.com/docs/en/agent-sdk/python
> Updated: 2025-12-25
