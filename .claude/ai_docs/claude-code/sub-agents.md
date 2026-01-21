# Subagents

> Create and use specialized AI subagents in Claude Code for task-specific workflows and improved context management.

Custom subagents in Claude Code are specialized AI assistants that can be invoked to handle specific types of tasks. They enable more efficient problem-solving by providing task-specific configurations with customized system prompts, tools and a separate context window.

## What are subagents?

Subagents are pre-configured AI personalities that Claude Code can delegate tasks to. Each subagent:

* Has a specific purpose and expertise area
* Uses its own context window separate from the main conversation
* Can be configured with specific tools it's allowed to use
* Includes a custom system prompt that guides its behavior

## Key benefits

* **Context preservation**: Each subagent operates in its own context, preventing pollution of the main conversation
* **Specialized expertise**: Subagents can be fine-tuned with detailed instructions for specific domains
* **Reusability**: Once created, you can use subagents across different projects
* **Flexible permissions**: Each subagent can have different tool access levels

## Quick start

1. Open the subagents interface: `/agents`
2. Select 'Create New Agent'
3. Define the subagent (recommended: generate with Claude first, then customize)
4. Save and use

Your subagent is now available. Claude uses it automatically when appropriate, or you can invoke it explicitly:

```
> Use the code-reviewer subagent to check my recent changes
```

## Subagent configuration

### File locations

Subagents are stored as Markdown files with YAML frontmatter:

| Type                  | Location            | Scope                         | Priority |
| :-------------------- | :------------------ | :---------------------------- | :------- |
| **Project subagents** | `.claude/agents/`   | Available in current project  | Highest  |
| **User subagents**    | `~/.claude/agents/` | Available across all projects | Lower    |

When subagent names conflict, project-level subagents take precedence.

### CLI-based configuration

You can also define subagents dynamically using the `--agents` CLI flag:

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

### File format

```markdown
---
name: your-sub-agent-name
description: Description of when this subagent should be invoked
tools: tool1, tool2, tool3  # Optional - inherits all tools if omitted
model: sonnet  # Optional - specify model alias or 'inherit'
permissionMode: default  # Optional - permission mode for the subagent
skills: skill1, skill2  # Optional - skills to auto-load
---

Your subagent's system prompt goes here. This can be multiple paragraphs
and should clearly define the subagent's role, capabilities, and approach
to solving problems.
```

#### Configuration fields

| Field            | Required | Description                                                                                                                                                                                                     |
| :--------------- | :------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`           | Yes      | Unique identifier using lowercase letters and hyphens                                                                                                                                                           |
| `description`    | Yes      | Natural language description of the subagent's purpose                                                                                                                                                          |
| `tools`          | No       | Comma-separated list of specific tools. If omitted, inherits all tools                                                                                                                                          |
| `model`          | No       | Model to use: `sonnet`, `opus`, `haiku`, or `'inherit'`                                                                                                                                                         |
| `permissionMode` | No       | Permission mode: `default`, `acceptEdits`, `bypassPermissions`, `plan`, `ignore`                                                                                                                                |
| `skills`         | No       | Comma-separated list of skill names to auto-load                                                                                                                                                                |

## Built-in subagents

### General-purpose subagent

A capable agent for complex, multi-step tasks that require both exploration and action.

* **Model**: Uses Sonnet
* **Tools**: Has access to all tools
* **Mode**: Can read and write files, execute commands, make changes

### Plan subagent

Specialized for use during plan mode. Conducts research and gathers information about your codebase before presenting a plan.

* **Model**: Uses Sonnet
* **Tools**: Read, Glob, Grep, and Bash tools for codebase exploration

### Explore subagent

A fast, lightweight agent optimized for searching and analyzing codebases. Operates in strict read-only mode.

* **Model**: Uses Haiku for fast, low-latency searches
* **Mode**: Strictly read-only
* **Tools**: Glob, Grep, Read, Bash (read-only commands only)

**Thoroughness levels**:
* **Quick** - Fast searches with minimal exploration
* **Medium** - Moderate exploration
* **Very thorough** - Comprehensive analysis across multiple locations

## Example subagents

### Code reviewer

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)
```

### Debugger

```markdown
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works

For each issue, provide:
- Root cause explanation
- Evidence supporting the diagnosis
- Specific code fix
- Testing approach
- Prevention recommendations
```

## Best practices

* **Start with Claude-generated agents**: Generate your initial subagent with Claude and then iterate
* **Design focused subagents**: Create subagents with single, clear responsibilities
* **Write detailed prompts**: Include specific instructions, examples, and constraints
* **Limit tool access**: Only grant tools that are necessary for the subagent's purpose
* **Version control**: Check project subagents into version control

## Advanced usage

### Chaining subagents

```
> First use the code-analyzer subagent to find performance issues, then use the optimizer subagent to fix them
```

### Resumable subagents

Subagents can be resumed to continue previous conversations:

* Each subagent execution is assigned a unique `agentId`
* The agent's conversation is stored in a separate transcript file
* Resume by providing the `agentId` via the `resume` parameter

---

> Source: https://code.claude.com/docs/en/sub-agents
> Updated: 2025-12-25
