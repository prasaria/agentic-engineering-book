# Slash commands

> Control Claude's behavior during an interactive session with slash commands.

## Built-in slash commands

| Command                   | Purpose                                                                                                                     |
| :------------------------ | :-------------------------------------------------------------------------------------------------------------------------- |
| `/add-dir`                | Add additional working directories                                                                                          |
| `/agents`                 | Manage custom AI subagents for specialized tasks                                                                            |
| `/bashes`                 | List and manage background tasks                                                                                            |
| `/bug`                    | Report bugs (sends conversation to Anthropic)                                                                               |
| `/clear`                  | Clear conversation history                                                                                                  |
| `/compact [instructions]` | Compact conversation with optional focus instructions                                                                       |
| `/config`                 | Open the Settings interface (Config tab)                                                                                    |
| `/context`                | Visualize current context usage as a colored grid                                                                           |
| `/cost`                   | Show token usage statistics                                                                                                 |
| `/doctor`                 | Checks the health of your Claude Code installation                                                                          |
| `/exit`                   | Exit the REPL                                                                                                               |
| `/export [filename]`      | Export the current conversation to a file or clipboard                                                                      |
| `/help`                   | Get usage help                                                                                                              |
| `/hooks`                  | Manage hook configurations for tool events                                                                                  |
| `/ide`                    | Manage IDE integrations and show status                                                                                     |
| `/init`                   | Initialize project with `CLAUDE.md` guide                                                                                   |
| `/install-github-app`     | Set up Claude GitHub Actions for a repository                                                                               |
| `/login`                  | Switch Anthropic accounts                                                                                                   |
| `/logout`                 | Sign out from your Anthropic account                                                                                        |
| `/mcp`                    | Manage MCP server connections and OAuth authentication                                                                      |
| `/memory`                 | Edit `CLAUDE.md` memory files                                                                                               |
| `/model`                  | Select or change the AI model                                                                                               |
| `/output-style [style]`   | Set the output style directly or from a selection menu                                                                      |
| `/permissions`            | View or update permissions                                                                                                  |
| `/plugin`                 | Manage Claude Code plugins                                                                                                  |
| `/pr-comments`            | View pull request comments                                                                                                  |
| `/privacy-settings`       | View and update your privacy settings                                                                                       |
| `/release-notes`          | View release notes                                                                                                          |
| `/rename <name>`          | Rename the current session for easier identification                                                                        |
| `/resume [session]`       | Resume a conversation by ID or name, or open the session picker                                                             |
| `/review`                 | Request code review                                                                                                         |
| `/rewind`                 | Rewind the conversation and/or code                                                                                         |
| `/sandbox`                | Enable sandboxed bash tool with filesystem and network isolation                                                            |
| `/security-review`        | Complete a security review of pending changes on the current branch                                                         |
| `/stats`                  | Visualize daily usage, session history, streaks, and model preferences                                                      |
| `/status`                 | Open the Settings interface (Status tab)                                                                                    |
| `/statusline`             | Set up Claude Code's status line UI                                                                                         |
| `/terminal-setup`         | Install Shift+Enter key binding for newlines (iTerm2 and VSCode only)                                                       |
| `/todos`                  | List current TODO items                                                                                                     |
| `/usage`                  | For subscription plans only: show plan usage limits and rate limit status                                                   |
| `/vim`                    | Enter vim mode for alternating insert and command modes                                                                     |

## Custom slash commands

Custom slash commands allow you to define frequently used prompts as Markdown files that Claude Code can execute.

### Syntax

```
/<command-name> [arguments]
```

### Command types

#### Project commands

Commands stored in your repository and shared with your team.

**Location**: `.claude/commands/`

```bash
# Create a project command
mkdir -p .claude/commands
echo "Analyze this code for performance issues and suggest optimizations:" > .claude/commands/optimize.md
```

#### Personal commands

Commands available across all your projects.

**Location**: `~/.claude/commands/`

```bash
# Create a personal command
mkdir -p ~/.claude/commands
echo "Review this code for security vulnerabilities:" > ~/.claude/commands/security-review.md
```

### Features

#### Namespacing

Use subdirectories to group related commands.

* `.claude/commands/frontend/component.md` creates `/component` with description "(project:frontend)"
* `~/.claude/commands/component.md` creates `/component` with description "(user)"

#### Arguments

Pass dynamic values to commands using argument placeholders:

##### All arguments with `$ARGUMENTS`

```bash
# Command definition
echo 'Fix issue #$ARGUMENTS following our coding standards' > .claude/commands/fix-issue.md

# Usage
> /fix-issue 123 high-priority
# $ARGUMENTS becomes: "123 high-priority"
```

##### Individual arguments with `$1`, `$2`, etc.

```bash
# Command definition
echo 'Review PR #$1 with priority $2 and assign to $3' > .claude/commands/review-pr.md

# Usage
> /review-pr 456 high alice
# $1 becomes "456", $2 becomes "high", $3 becomes "alice"
```

#### Bash command execution

Execute bash commands before the slash command runs using the `!` prefix:

```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
description: Create a git commit
---

## Context

- Current git status: !`git status`
- Current git diff (staged and unstaged changes): !`git diff HEAD`
- Current branch: !`git branch --show-current`

## Your task

Based on the above changes, create a single git commit.
```

#### File references

Include file contents in commands using the `@` prefix to reference files.

```markdown
# Reference a specific file
Review the implementation in @src/utils/helpers.js

# Reference multiple files
Compare @src/old-version.js with @src/new-version.js
```

### Frontmatter

Command files support frontmatter for specifying metadata:

| Frontmatter                | Purpose                                                        | Default                             |
| :------------------------- | :------------------------------------------------------------- | :---------------------------------- |
| `allowed-tools`            | List of tools the command can use                              | Inherits from the conversation      |
| `argument-hint`            | The arguments expected for the slash command                   | None                                |
| `description`              | Brief description of the command                               | Uses the first line from the prompt |
| `model`                    | Specific model string                                          | Inherits from the conversation      |
| `disable-model-invocation` | Whether to prevent `SlashCommand` tool from calling this command | false                             |

Example:

```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
argument-hint: [message]
description: Create a git commit
model: claude-3-5-haiku-20241022
---

Create a git commit with message: $ARGUMENTS
```

## Plugin commands

Plugins can provide custom slash commands that integrate seamlessly with Claude Code.

* **Namespaced**: Commands can use the format `/plugin-name:command-name`
* **Automatically available**: Once a plugin is enabled, its commands appear in `/help`
* **Fully integrated**: Support all command features (arguments, frontmatter, bash execution, file references)

## MCP slash commands

MCP servers can expose prompts as slash commands that become available in Claude Code.

### Command format

```
/mcp__<server-name>__<prompt-name> [arguments]
```

### Features

* Dynamic discovery from connected MCP servers
* Arguments defined by the server
* Server and prompt names are normalized (spaces become underscores)

## `SlashCommand` tool

The `SlashCommand` tool allows Claude to execute custom slash commands programmatically during a conversation.

To encourage Claude to use the `SlashCommand` tool, reference the command by name in your prompts or `CLAUDE.md` file:

```
> Run /write-unit-test when you are about to start writing tests.
```

### Disable `SlashCommand` tool

```bash
/permissions
# Add to deny rules: SlashCommand
```

### Disable specific commands only

Add `disable-model-invocation: true` to the slash command's frontmatter.

## Skills vs slash commands

**Slash commands** are for quick, frequently used prompts. **Agent Skills** are for comprehensive capabilities with structure.

### Key differences

| Aspect         | Slash Commands                   | Agent Skills                        |
| -------------- | -------------------------------- | ----------------------------------- |
| **Complexity** | Simple prompts                   | Complex capabilities                |
| **Structure**  | Single .md file                  | Directory with SKILL.md + resources |
| **Discovery**  | Explicit invocation (`/command`) | Automatic (based on context)        |
| **Files**      | One file only                    | Multiple files, scripts, templates  |

---

> Source: https://code.claude.com/docs/en/slash-commands
> Updated: 2025-12-25
