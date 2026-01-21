# Agent SDK reference - TypeScript

Complete API reference for the TypeScript Agent SDK, including all functions, types, and interfaces.

## Installation

```bash
npm install @anthropic-ai/claude-agent-sdk
```

## Functions

### `query()`

The primary function for interacting with Claude Code. Creates an async generator that streams messages.

```typescript
function query({
  prompt,
  options
}: {
  prompt: string | AsyncIterable<SDKUserMessage>;
  options?: Options;
}): Query
```

Returns a `Query` object that extends `AsyncGenerator<SDKMessage, void>` with additional methods.

### `tool()`

Creates a type-safe MCP tool definition.

```typescript
function tool<Schema extends ZodRawShape>(
  name: string,
  description: string,
  inputSchema: Schema,
  handler: (args: z.infer<ZodObject<Schema>>, extra: unknown) => Promise<CallToolResult>
): SdkMcpToolDefinition<Schema>
```

### `createSdkMcpServer()`

Creates an MCP server instance that runs in the same process.

```typescript
function createSdkMcpServer(options: {
  name: string;
  version?: string;
  tools?: Array<SdkMcpToolDefinition<any>>;
}): McpSdkServerConfigWithInstance
```

## Types

### `Options`

Configuration object for the `query()` function.

| Property | Type | Default | Description |
| :------- | :--- | :------ | :---------- |
| `abortController` | `AbortController` | `new AbortController()` | Controller for cancelling operations |
| `allowedTools` | `string[]` | All tools | List of allowed tool names |
| `agents` | `Record<string, AgentDefinition>` | `undefined` | Programmatically define subagents |
| `canUseTool` | `CanUseTool` | `undefined` | Custom permission function |
| `continue` | `boolean` | `false` | Continue the most recent conversation |
| `cwd` | `string` | `process.cwd()` | Current working directory |
| `hooks` | `Partial<Record<HookEvent, HookCallbackMatcher[]>>` | `{}` | Hook callbacks for events |
| `mcpServers` | `Record<string, McpServerConfig>` | `{}` | MCP server configurations |
| `model` | `string` | Default from CLI | Claude model to use |
| `permissionMode` | `PermissionMode` | `'default'` | Permission mode for the session |
| `resume` | `string` | `undefined` | Session ID to resume |
| `settingSources` | `SettingSource[]` | `[]` | Control which filesystem settings to load |
| `systemPrompt` | `string \| { type: 'preset'; preset: 'claude_code'; append?: string }` | `undefined` | System prompt configuration |

### `Query`

Interface returned by the `query()` function.

```typescript
interface Query extends AsyncGenerator<SDKMessage, void> {
  interrupt(): Promise<void>;
  rewindFiles(userMessageUuid: string): Promise<void>;
  setPermissionMode(mode: PermissionMode): Promise<void>;
  setModel(model?: string): Promise<void>;
  supportedCommands(): Promise<SlashCommand[]>;
  supportedModels(): Promise<ModelInfo[]>;
  mcpServerStatus(): Promise<McpServerStatus[]>;
  accountInfo(): Promise<AccountInfo>;
}
```

### `AgentDefinition`

```typescript
type AgentDefinition = {
  description: string;
  tools?: string[];
  prompt: string;
  model?: 'sonnet' | 'opus' | 'haiku' | 'inherit';
}
```

### `SettingSource`

```typescript
type SettingSource = 'user' | 'project' | 'local';
```

### `PermissionMode`

```typescript
type PermissionMode =
  | 'default'
  | 'acceptEdits'
  | 'bypassPermissions'
  | 'plan'
```

### `CanUseTool`

```typescript
type CanUseTool = (
  toolName: string,
  input: ToolInput,
  options: { signal: AbortSignal; suggestions?: PermissionUpdate[] }
) => Promise<PermissionResult>;
```

### `PermissionResult`

```typescript
type PermissionResult =
  | { behavior: 'allow'; updatedInput: ToolInput; updatedPermissions?: PermissionUpdate[] }
  | { behavior: 'deny'; message: string; interrupt?: boolean }
```

## Message Types

### `SDKMessage`

```typescript
type SDKMessage =
  | SDKAssistantMessage
  | SDKUserMessage
  | SDKUserMessageReplay
  | SDKResultMessage
  | SDKSystemMessage
  | SDKPartialAssistantMessage
  | SDKCompactBoundaryMessage;
```

### `SDKResultMessage`

```typescript
type SDKResultMessage =
  | {
      type: 'result';
      subtype: 'success';
      session_id: string;
      duration_ms: number;
      is_error: boolean;
      num_turns: number;
      result: string;
      total_cost_usd: number;
      usage: NonNullableUsage;
    }
  | {
      type: 'result';
      subtype: 'error_max_turns' | 'error_during_execution' | 'error_max_budget_usd';
      session_id: string;
      is_error: boolean;
      errors: string[];
    }
```

## Hook Types

### `HookEvent`

```typescript
type HookEvent =
  | 'PreToolUse'
  | 'PostToolUse'
  | 'PostToolUseFailure'
  | 'Notification'
  | 'UserPromptSubmit'
  | 'SessionStart'
  | 'SessionEnd'
  | 'Stop'
  | 'SubagentStart'
  | 'SubagentStop'
  | 'PreCompact'
  | 'PermissionRequest';
```

### `HookCallback`

```typescript
type HookCallback = (
  input: HookInput,
  toolUseID: string | undefined,
  options: { signal: AbortSignal }
) => Promise<HookJSONOutput>;
```

## Tool Input Types

### Bash

```typescript
interface BashInput {
  command: string;
  timeout?: number;
  description?: string;
  run_in_background?: boolean;
}
```

### Edit

```typescript
interface FileEditInput {
  file_path: string;
  old_string: string;
  new_string: string;
  replace_all?: boolean;
}
```

### Read

```typescript
interface FileReadInput {
  file_path: string;
  offset?: number;
  limit?: number;
}
```

### Write

```typescript
interface FileWriteInput {
  file_path: string;
  content: string;
}
```

### Glob

```typescript
interface GlobInput {
  pattern: string;
  path?: string;
}
```

### Grep

```typescript
interface GrepInput {
  pattern: string;
  path?: string;
  glob?: string;
  type?: string;
  output_mode?: 'content' | 'files_with_matches' | 'count';
  '-i'?: boolean;
  '-n'?: boolean;
  '-B'?: number;
  '-A'?: number;
  '-C'?: number;
  head_limit?: number;
  multiline?: boolean;
}
```

### Task

```typescript
interface AgentInput {
  description: string;
  prompt: string;
  subagent_type: string;
}
```

## Sandbox Configuration

```typescript
type SandboxSettings = {
  enabled?: boolean;
  autoAllowBashIfSandboxed?: boolean;
  excludedCommands?: string[];
  allowUnsandboxedCommands?: boolean;
  network?: NetworkSandboxSettings;
  ignoreViolations?: SandboxIgnoreViolations;
}
```

### Example

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const result = await query({
  prompt: "Build and test my project",
  options: {
    sandbox: {
      enabled: true,
      autoAllowBashIfSandboxed: true,
      excludedCommands: ["docker"],
      network: {
        allowLocalBinding: true,
        allowUnixSockets: ["/var/run/docker.sock"]
      }
    }
  }
});
```

---

> Source: https://platform.claude.com/docs/en/agent-sdk/typescript
> Updated: 2025-12-25
