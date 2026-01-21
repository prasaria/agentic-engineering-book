---
title: Claude Code
description: Anthropic's CLI coding agent with subagents, Skills, and hooks
created: 2025-12-08
last_updated: 2026-01-17
tags: [tools, claude-code, coding-agent, anthropic, slash-commands, expert-pattern, skills, orchestration, tool-restriction, hooks, sandbox, security]
part: 3
part_title: Perspectives
chapter: 9
section: 1
order: 3.9.1
---

# Claude Code

Anthropic's official coding agent. A primary tool for agentic software development, offering subagent orchestration, progressive disclosure via Skills, and extensive customization through hooks.

---

## Mental Model for Claude Code

**Claude Code is a programmable orchestrator, not just a chatbot that writes code.** The value comes from configuring it as a multi-agent system where specialized subagents handle specific concerns. Hooks provide observability into agent behavior, Skills provide just-in-time expertise, and tool restrictions create forcing functions for better delegation.

The shift from "assistant" to "system" thinking changes how you use it—instead of asking Claude to do everything, design the environment where Claude coordinates specialists.


---

## Connections

- **To [Prompt](../2-prompt/_index.md):** Skills and slash commands demonstrate model-invoked vs user-invoked prompt patterns. See [Model-Invoked vs. User-Invoked Prompts](../2-prompt/_index.md#model-invoked-vs-user-invoked-prompts) for design trade-offs.
- **To [Context](../4-context/_index.md):** Skills implement the [Progressive Disclosure pattern](../4-context/_index.md#progressive-disclosure-pattern) for context management
- **To [Cost and Latency](../7-practices/3-cost-and-latency.md):** Token cost models for different feature types—understanding the economics of tools, Skills, subagents, and MCP
- **ReAct Loop:** How does Claude Code implement the ReAct pattern?
- **Human-in-the-Loop:** How do you stay in the loop while using Claude Code?

---

## Tips & Tricks

*Specific techniques that work well:*

*[2025-12-08]*: **The Three-Command Expert Pattern (Plan-Build-Improve)** - This pattern creates a learning triangle where production experience feeds back into prompts through mutable Expertise sections. Each expert has three slash commands: Plan (creates specifications), Build (implements the spec), and Improve (analyzes recent work and updates the Expertise sections in Plan and Build commands). The Improve command closes the loop by extracting learnings from actual production usage and updating the expert's knowledge base, making each iteration smarter than the last. This creates a self-improving system where the prompts themselves evolve based on real-world experience.

*[2026-01-11]*: **Real-Time Message Steering** - Claude Code 2.1.0 introduced the ability to send messages while Claude works, fundamentally changing the interaction model from "fire and wait" to "fire and steer."

**How it works:** Type and send messages during active execution. Claude receives the input and can adjust its approach mid-task—correcting misunderstandings, refining direction, or pivoting focus without waiting for completion.

**Use cases:**
- **Mid-task corrections:** "Actually, focus on the authentication module first"
- **Scope refinement:** "Skip the tests for now, just get the implementation working"
- **Context injection:** "The config file moved to /etc/app.conf last week"
- **Priority shifts:** "This is blocking, handle error cases before edge cases"

**Pattern: Progressive Refinement**

Rather than crafting a perfect initial prompt, start with a direction and refine as Claude works:

1. Issue broad instruction: "Refactor the payment module for testability"
2. Observe initial approach in real-time
3. Steer as needed: "Good direction, but preserve the async interface"
4. Continue steering: "Focus on the PaymentProcessor class specifically"

This pattern reduces upfront prompt engineering effort and enables adaptation based on what Claude actually does, not what was anticipated.

**Contrast with backgrounding:** Real-time steering requires the task to remain in foreground. Backgrounded tasks (Ctrl+B) run without steering capability—use backgrounding for well-defined tasks that need no mid-flight adjustment.

**Sources:** [Claude Code Changelog 2.1.0](https://code.claude.com/docs/en/changelog)

*[2026-01-11]*: **Clickable File Paths (OSC 8)** - Claude Code 2.1.2 added OSC 8 hyperlink support, making file paths in tool output clickable in supported terminals (iTerm2, WezTerm, Ghostty, Kitty, and others).

**What this means:** When Claude references files in output, paths render as clickable links that open directly in the default editor or file browser.

**Requirements for clickable paths:**
1. Terminal must support OSC 8 escape sequences
2. File paths must be absolute (relative paths don't resolve reliably)
3. Files must exist at the referenced location

**Practical implication:** Agents and skills that emit file paths should prefer absolute paths to enable clicking:

```markdown
# Less useful (not clickable)
See the config in ./config/app.yaml

# More useful (clickable in OSC 8 terminals)
See the config in /Users/dev/project/config/app.yaml
```

**Configuration tip:** Agents designed for navigation-heavy workflows benefit from instructions to emit absolute paths:

```markdown
When referencing files, always use absolute paths to enable terminal linking.
```

**Supported terminals:** iTerm2, WezTerm, Ghostty, Kitty, Windows Terminal, and others implementing the OSC 8 standard. Verify support in terminal documentation.

**Sources:** [Claude Code Changelog 2.1.2](https://code.claude.com/docs/en/changelog)

---

## Keyboard Customization

*[2026-01-17]*: Claude Code 2.1.7 added customizable keybindings for power-user workflows.

### Default Bindings

| Key | Action |
|-----|--------|
| `Ctrl+K` | New conversation |
| `Ctrl+Shift+L` | Clear context |
| `Ctrl+B` | Background task |
| `Ctrl+/` | Command palette |
| `Escape` | Cancel current operation |

### Custom Bindings

Configure in `~/.claude/keybindings.json`:

```json
{
  "bindings": [
    {
      "key": "ctrl+shift+b",
      "command": "background-task",
      "description": "Run current task in background"
    },
    {
      "key": "ctrl+shift+r",
      "command": "/review:clarity",
      "description": "Quick clarity review"
    }
  ]
}
```

### Power-User Patterns

- **Bind frequently-used slash commands** to muscle memory shortcuts
- **Create keyboard macros** for multi-step workflows
- **Organize by frequency**: most-used on easiest keys
- **Consider domain-specific bindings** for specialized work

The ability to bind slash commands directly to key combinations eliminates the friction of typing command names, enabling faster workflow execution for repeated patterns.

**Sources:** [Claude Code Changelog 2.1.7](https://code.claude.com/docs/en/changelog)

---

## Subagent System

*[2025-12-09]*: Claude Code's subagent system (part of the Claude Agent SDK, renamed from "Claude Code SDK" in late 2025) is the primary mechanism for multi-agent coordination. Understanding it is essential for building effective multi-agent workflows.

### Core Concepts

**Context Isolation**: Each subagent maintains a separate context window from the orchestrator. They return only synthesized, relevant information—not their full context. This prevents context pollution and enables parallel information processing without bloating the orchestrator's context.

**Parallelization**: Subagents can run truly concurrently when invoked via multiple Task tool calls in a single message. This is the foundation of parallel multi-agent workflows.

### Nesting Constraint and Workarounds

*[2025-12-11]*: Claude Code's Task tool is unavailable to subagents—they cannot spawn nested subagents. This is a hard architectural constraint as of December 2024, though the limitation will likely evolve as the tooling matures.

**Why the constraint exists**:
- Prevents infinite recursion scenarios where agents spawn agents indefinitely
- Avoids token budget runaway in deeply nested delegation chains
- Simplifies the execution model and debugging surface
- Keeps coordination patterns explicit rather than emergent

This creates a flat orchestration model: one HEAD agent coordinates multiple subagents, but subagents are leaf nodes that cannot delegate further.

**Workaround 1: Subprocess spawning via `claude -p`**

Subagents can invoke `claude -p <prompt>` through the Bash tool to spawn independent Claude Code processes:

```python
# In a subagent that needs to spawn another agent
result = bash("""
claude -p "agent-name" <<EOF
Perform specific task with inputs
EOF
""")
```

**Trade-offs**:
- **Gain**: Enables multi-level delegation when architecturally necessary
- **Cost**: Loses visibility—subprocess agents run in separate sessions
- **Cost**: No access to parent session state or shared context
- **Cost**: Adds 10+ second subprocess startup overhead per spawn
- **Cost**: Subprocess billing is separate (may complicate cost tracking)

**Workaround 2: MCP-based agent spawning**

Create an MCP server that exposes agent spawning as a tool. This maintains observability within the Claude Code session while enabling nested delegation:

```yaml
# MCP server definition exposing spawn_agent tool
tools:
  - name: spawn_agent
    description: Spawn a specialized subagent for delegation
    parameters:
      agent_name: string
      task: string
      context: object
```

Subagents invoke the MCP tool, which handles spawning and returns results within the session's execution context.

**Trade-offs**:
- **Gain**: Maintains session visibility and cost tracking
- **Gain**: Reusable across projects via MCP protocol
- **Cost**: Requires implementing and running an MCP server
- **Cost**: Additional architectural complexity
- **Cost**: MCP server itself must manage agent lifecycles

**Workaround 3: Document-driven coordination**

Instead of nested spawning, use shared document state for multi-level coordination:

1. Subagent writes task specification to a file (e.g., `tasks/pending/task-123.md`)
2. Subagent reports completion to orchestrator
3. Orchestrator reads pending tasks and spawns appropriate specialists
4. Specialists write results back to shared state

**Trade-offs**:
- **Gain**: Fully decoupled—no nesting required
- **Gain**: Natural audit trail via filesystem artifacts
- **Gain**: Enables asynchronous multi-agent workflows
- **Cost**: Requires explicit coordination protocol
- **Cost**: Orchestrator must poll or be notified of pending work
- **Cost**: Higher latency—tasks complete in subsequent orchestrator turns

**Future direction**: Nested spawning is a natural evolution as agent systems mature. The current constraint reflects Claude Code's focus on preventing runaway behaviors in early adoption. Expect capabilities to expand, possibly with:
- Depth limits on nesting (e.g., max 2-3 levels)
- Token budget controls across nested chains
- Enhanced observability for nested execution trees

For now, design architectures that work within the flat model. The workarounds exist for edge cases but should not be the default pattern.

**See Also**:
- [Orchestrator Pattern](../6-patterns/3-orchestrator-pattern.md) — Design patterns for flat orchestration
- [Multi-Agent Context](../4-context/4-multi-agent-context.md) — Managing context across agent boundaries

### Defining Subagents

Two approaches:

**Filesystem Definition** (`.claude/agents/*.md`):
```yaml
---
name: code-reviewer
description: Security-focused code review specialist
tools: [Read, Grep, Glob]
model: sonnet
---

You are a security-focused code reviewer. Analyze code for vulnerabilities,
code smells, and deviation from best practices.
```

Project-level agents go in `.claude/agents/`, user-level in `~/.claude/agents/`.

**Programmatic Definition** (SDK):
```typescript
const result = query({
  prompt: "Review the authentication module",
  options: {
    agents: {
      'code-reviewer': {
        description: 'Security-focused code review specialist',
        prompt: 'You are a security-focused code reviewer...',
        tools: ['Read', 'Grep', 'Glob'],
        model: 'sonnet'
      }
    }
  }
});
```

Programmatic definitions take precedence when names conflict.

### Tool Restrictions as Security Boundaries

Configure tool access per subagent to follow least-privilege principles:

| Subagent Role | Appropriate Tools | Rationale |
|---------------|-------------------|-----------|
| Reviewer/Analyzer | Read, Grep, Glob | Read-only, can't modify files |
| Test Runner | Bash, Read, Grep | Execute tests, read results |
| Builder/Implementer | Read, Edit, Write, Grep, Glob | Full modification access |
| Orchestrator | Task, Read, Glob | Routes work, minimal direct access |

This is production IAM thinking applied to agents: deny-all by default, allowlist only what's necessary.

For MCP (Model Context Protocol) tools, the same pattern applies with extended naming: `mcp__<server>__<tool>`. See [Tool Use: MCP Tool Declarations](../5-tool-use/_index.md#mcp-tool-declarations-in-frontmatter) for the full pattern.

### Proactive Spawning

To encourage proactive subagent use, include phrases like "use PROACTIVELY" or "MUST BE USED" in the subagent description field. Native spawning eliminates subprocess overhead—agent creation is near-instantaneous rather than 10+ seconds.

**Sources**: [Subagents in the SDK - Claude Docs](https://platform.claude.com/docs/en/agent-sdk/subagents), [Building agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk), [Best practices for Claude Code subagents](https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/)

---

## Skills System

*[2025-12-09]*: Claude Code's Skills system enables progressive disclosure of procedural knowledge—teaching agents specialized reasoning patterns without upfront context cost.

### What Skills Are

Skills are procedural knowledge modules stored as `SKILLS.md` files in `.claude/skills/` directories. Unlike subagents (which delegate work) or slash commands (which require explicit invocation), Skills activate autonomously when Claude's reasoning determines relevance.

Each skill consists of:
- **YAML frontmatter**: Name, description (~50-200 chars), optional tool restrictions
- **Markdown instructions**: Detailed guidance (500-5,000 words)
- **Optional resources**: Supporting files in `scripts/`, `references/`, `assets/`

Skills use three-tier loading for context efficiency (see [Progressive Disclosure pattern](../4-context/_index.md#progressive-disclosure-pattern)):
1. **Metadata** loads into every prompt (descriptions only)
2. **Full instructions** load when the model determines relevance
3. **Supporting resources** load on-demand when referenced

### Model-Invoked Design

Skills represent a fundamental shift in how agents access specialized knowledge. The model decides when to activate a skill based on the task at hand—no explicit command required.

**Comparison**:
- **Tools** (function calling): *What* the agent can do—read files, run commands, call APIs
- **Skills**: *How* the agent should reason about specialized domains—temporary behavioral specialization
- **Subagents**: *Who* does the work—delegate to isolated agents with separate contexts
- **Slash commands**: *When* the user says—explicit invocation via `/command`

Skills solve the context efficiency problem differently than subagents. Subagents isolate work in separate contexts; Skills temporarily specialize the main agent's behavior within its existing context.

### Skills vs Other Features

**Skills vs Subagents**: Skills temporarily add expertise to the current agent. Subagents delegate work to separate agents with isolated contexts. Use Skills when you want the agent to *learn temporarily*; use subagents when you want to *divide work*.

**Skills vs Slash Commands**: Slash commands require users to know when specialized behavior is needed. Skills activate autonomously based on the agent's reasoning about the task. Use slash commands for user-driven workflows; use Skills for context-appropriate specialization.

*[2026-01-11]*: **Unified Mental Model (2.1.3):** Slash commands and Skills are now presented as a unified concept in Claude Code. The underlying behavior remains unchanged—slash commands still require explicit `/` invocation while Skills activate autonomously—but the UI and documentation treat them as variations of the same capability rather than separate features.

**What changed:**
- Single configuration surface for both
- Shared discovery mechanisms
- Unified documentation and help

**What stayed the same:**
- Invocation semantics (explicit vs. autonomous)
- Tool restriction patterns
- Progressive disclosure loading

**Practical implication:** When designing extensibility for Claude Code projects, think of slash commands and Skills as two invocation patterns for the same underlying primitive:

| Aspect | Slash Commands | Skills |
|--------|----------------|--------|
| Invocation | User types `/command` | Model determines relevance |
| Discovery | User knows command exists | Model finds during reasoning |
| Control | User-driven workflow | Context-appropriate activation |
| Definition | `.claude/commands/*.md` | `.claude/skills/SKILLS.md` |

The merge simplifies the mental model without changing when to use each pattern. Prefer slash commands when the user should explicitly trigger behavior; prefer Skills when behavior should activate based on task context.

**Sources:** [Claude Code Changelog 2.1.3](https://code.claude.com/docs/en/changelog)

**Skills vs MCP**: MCP connects agents to external data sources and services. Skills teach agents how to reason about and use that data. MCP says "here's a database"; Skills say "here's how to query databases effectively for this domain."

### Tool Restrictions in Skills

The `allowed-tools` field in SKILLS.md frontmatter enables temporary privilege escalation within defined scopes:

```yaml
---
name: database-migration
description: Safe database schema changes with rollback planning
allowed-tools: [Read, Write, Bash, mcp__supabase__execute_sql]
---
```

This implements "safe by default, permissive by context"—the skill grants additional capabilities only while active. Once the task completes, those permissions revert. This is more granular than subagent tool restrictions, which apply for the entire subagent lifecycle.

**Use case**: A general-purpose agent might not have database write access by default, but activating the `database-migration` skill temporarily grants those capabilities with appropriate guardrails baked into the skill's instructions.

### When to Use Skills

**Good fits**:
- Domain-specific reasoning patterns (security review, accessibility auditing, API design)
- Specialized workflows that recur but don't warrant dedicated agents
- Context-heavy procedures where progressive disclosure saves tokens
- Teaching agents about project-specific conventions or standards

**Poor fits**:
- Simple operations better handled by tools
- Work requiring full context isolation (use subagents)
- User-driven workflows with explicit triggers (use slash commands)
- Knowledge that should always be available (put in CLAUDE.md)

### Practical Example

A skill for API design might include:
- **Description**: "REST API design patterns and consistency checking"
- **Instructions**: Detailed guidance on endpoint naming, versioning, error handling, idempotency
- **Resources**: `references/api-standards.md`, `scripts/check-openapi-spec.py`
- **Allowed tools**: `Read, Grep, mcp__openapi__validate`

When the agent encounters a task involving API endpoints, it autonomously loads the skill, temporarily gaining specialized API design reasoning—without that knowledge consuming context tokens for unrelated tasks.

### Connections

- **To [Context](../4-context/_index.md):** Skills implement the [Progressive Disclosure pattern](../4-context/_index.md#progressive-disclosure-pattern)—specialized knowledge loads only when needed, preserving context capacity for other work
- **To [Tool Use](../5-tool-use/_index.md):** Skills teach meta-patterns for tool usage; tools provide capabilities, Skills teach when and how to use them effectively
- **To [Prompt](../2-prompt/_index.md):** Skills are model-invoked rather than user-invoked—the agent determines relevance through reasoning, not explicit commands

**Sources**: [Skills - Claude Code Docs](https://code.claude.com/docs/en/skills), [Equipping Agents for the Real World with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), [Claude Skills: progressive disclosure for agent workflows](https://simonwillison.net/2025/Oct/16/claude-skills/), [Claude Skills Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)

### Skill Development Workflow

*[2026-01-11]*: Claude Code 2.1.0 introduced automatic skill hot-reload. Skills in `~/.claude/skills` or `.claude/skills` become immediately available without restarting Claude Code. This enables an iterative development workflow where skill definitions evolve in real-time.

**The Workflow:**

1. **Create or edit** a skill file in `.claude/skills/`
2. **Save** the file
3. **Use** the skill immediately—no restart, no reload command

**Development Pattern: Iterative Refinement**

```
# Terminal 1: Claude Code session
> [Working on task, notice skill needs adjustment]

# Terminal 2 (or editor): Edit skill
$ vim .claude/skills/my-skill/SKILLS.md
# Save changes

# Terminal 1: Skill changes take effect immediately
> [Continue task with updated skill behavior]
```

**Testing Skills in Isolation:**

Combine hot-reload with sub-agent forking (`context: fork`) to test skill behavior without polluting the main conversation context:

```yaml
---
name: test-skill
description: Test skill in isolated context
context: fork
---

Test the target skill behavior with this specific scenario...
```

The forked context prevents test interactions from affecting the main session while hot-reload ensures the latest skill definition is used.

**Practical Benefits:**
- No context loss from restarts during skill development
- Immediate feedback loop on skill changes
- Reduced friction for experimental skill designs
- Enables "edit-save-test" cycles measured in seconds

**Sources:** [Claude Code Changelog 2.1.0](https://code.claude.com/docs/en/changelog)

---

## Configuration

### Tool Restriction as Forcing Function for Delegation

*[2025-12-09]*: The default Claude Code HEAD agent inherits all tools. This means it *can* delegate via Task, but nothing *forces* it to. The agent might do everything itself—creating bloated context, no parallelization, monolithic reasoning that's hard to debug.

**The insight**: If the orchestrator literally *cannot* read files, write code, or execute bash, it has no choice but to spawn subagents.

Two configuration layers shape orchestrator behavior:

**1. Claude Code Settings (`.claude/settings.json`)**

```json
{
  "permissions": {
    "allow": ["Task", "AskUserQuestion", "Read", "Glob", "TodoWrite"],
    "deny": ["Write", "Edit", "Bash*"]
  }
}
```

Restricts tools uniformly across HEAD and all subagents. The HEAD agent can explore (Read, Glob) and delegate (Task), but cannot implement. *Note: This also restricts subagents unless they explicitly declare tools in frontmatter.*

**2. Slash Commands as Workflow Boundaries**

Orchestrator commands (like `/orchestrators:knowledge`) embody this pattern structurally. The orchestrator has one job: spawn and coordinate specialists. The slash command defines the workflow, not the implementation.

**Why this matters**:

| Benefit | Mechanism |
|---------|-----------|
| Context isolation | Subagents return summaries, not raw tool output |
| Natural parallelization | Multiple Task calls = concurrent execution |
| Debugging clarity | Know which specialist failed, not "somewhere in 500 tool calls" |
| Cost optimization | Smaller specialists can use cheaper models |

**Minimum orchestrator tool set**:
- `Task` — spawn subagents
- `Read` — read specs, understand context
- `Glob` — file discovery for routing decisions
- `AskUserQuestion` — clarification when needed
- `TodoWrite` — track workflow progress

**The meta-principle**: Constraints enable architecture. The same way type systems prevent bugs by making invalid states unrepresentable, tool restrictions prevent bad orchestration by making direct implementation unavailable.

### Current Limitations

*[2025-12-09]*: Claude Code's permission system applies uniformly to HEAD and subagents—there is no built-in mechanism to restrict the HEAD agent while allowing subagents broader tool access.

**What this means:**
- Restrictions in `settings.json` affect all agents equally
- Subagents must explicitly declare tools to exceed HEAD restrictions
- The "HEAD can only delegate" pattern requires per-agent tool declarations

### Explicit Tool Declaration Pattern

To achieve orchestrator forcing functions today:

**1. Restrict settings.json to orchestration tools:**
```json
{
  "permissions": {
    "allow": ["Task", "Read", "Glob", "AskUserQuestion", "TodoWrite"]
  }
}
```

**2. Every subagent declares its tools:**
```yaml
---
name: build-agent
tools: Read, Write, Edit, Glob, Grep, Bash
---
```

**3. HEAD cannot implement (no Write/Edit/Bash)**

**4. Subagents opt-in to capabilities they need**

**Trade-offs:**
- Achieves forcing function for orchestration
- Makes capabilities explicit (good for documentation)
- Requires verbose tool declarations across all subagents
- Easy to forget when creating new agents

This is the recommended pattern until Claude Code adds HEAD/subagent permission distinction.

**Open questions**:
- ~~How do hooks determine HEAD vs. subagent context?~~
  *[2025-12-09]*: Hooks receive event data but no explicit HEAD/subagent flag. Detection would require heuristics based on session metadata. Not currently documented or confirmed reliable.
- What happens when subagents need to sub-delegate? (Currently not supported)
- How do you handle exploration that naturally leads to implementation?
- **What would native HEAD/subagent permission distinction look like?**
  Potential design: `permissionMode` extension or new `scope` field in permissions:
  ```json
  {
    "permissions": {
      "head": {
        "allow": ["Task", "Read", "Glob"]
      },
      "subagents": {
        "inherit": ["Write", "Edit", "Bash"]
      }
    }
  }
  ```
  Feature request candidate for Anthropic.

**See Also**:
- [Orchestrator Pattern: Capability Minimization](../6-patterns/3-orchestrator-pattern.md#capability-minimization) — The subagent side of this pattern
- [Tool Use: Tool Restrictions as Security Boundaries](../5-tool-use/_index.md#tool-restrictions-as-security-boundaries) — Security framing

### Output Styles Deprecation

*[2026-01-11]*: Output styles are deprecated as of Claude Code 2.1.0. The feature continues to work but will be removed in a future version. Projects using output styles should migrate to one of the following approaches:

**Migration Options** (in order of preference):

| Approach | Scope | Use Case |
|----------|-------|----------|
| `CLAUDE.md` | Project | Style guidance checked into codebase, visible to all collaborators |
| `--system-prompt-file <path>` | Session | Load style instructions from file at startup |
| `--append-system-prompt <text>` | Session | Add to default system prompt without replacing it |
| `--system-prompt <text>` | Session | Replace default system prompt entirely |
| Plugins | Session | Most flexible; programmatic control over prompts |

**Recommended Migration Path:**

For agent definitions using `output-style` frontmatter, embed style requirements directly in the agent prompt body:

```yaml
---
name: research-agent
tools: Read, Grep, Glob, WebFetch
model: sonnet
# REMOVED: output-style: concise-reference
---

## Response Format
- Use bullet points for findings
- Include source citations
- Limit summaries to 3-5 sentences

[Rest of agent prompt...]
```

For project-wide style consistency, add guidance to `CLAUDE.md`:

```markdown
## Response Style

- Prefer bullet points over prose
- Include evidence for claims
- Use tables for comparisons
```

**Rationale:** `CLAUDE.md` already serves as the canonical source of project instructions. Embedding style guidance there (or directly in agent prompts) eliminates a separate abstraction layer and keeps all behavioral configuration visible in version control.

**Sources:** [Claude Code Changelog 2.1.0](https://code.claude.com/docs/en/changelog)

### Sandbox Mode vs. Permissions: Independent Security Layers

*[2025-12-09]*: A critical distinction that's easy to miss—Claude Code has two separate security mechanisms that operate independently:

**Sandbox Mode** (OS-level isolation):
- Uses bubblewrap (Linux) or Seatbelt (macOS) for container-like restrictions
- Restricts filesystem access to current working directory by default
- Routes network traffic through a proxy, allowing only approved domains
- Enforced at the OS level—even if Claude wants to escape, it physically cannot

**Permission System** (`--dangerously-skip-permissions`):
- Controls whether Claude asks before doing things
- Bypasses permission prompts (for CI, trusted environments, etc.)
- Does NOT disable sandbox boundaries

**The key insight**: Using `--dangerously-skip-permissions` does NOT disable sandboxing. You can run Claude Code unattended with the flag, and sandbox restrictions still apply at the OS level. Commands trying to write outside the working directory or reach non-whitelisted domains are blocked regardless of permission settings.

This is defense-in-depth: even if a prompt injection attack manipulates Claude into trying something malicious, the sandbox prevents actual damage. The permission flag just means "don't ask me," not "remove all restrictions."

**The escape hatch**: There's a `dangerouslyDisableSandbox` parameter on the Bash tool for commands that legitimately need to run outside sandbox (like Docker). Even this goes through normal permission flow—it's not automatic. Can be disabled entirely with `"allowUnsandboxedCommands": false` in settings.

| Layer | Controls | `--dangerously-skip-permissions` Effect |
|-------|----------|----------------------------------------|
| Sandbox | OS-level filesystem/network boundaries | None—still enforced |
| Permissions | Ask-before-doing prompts | Bypassed |
| Escape Hatch | Per-command sandbox override | Still requires permission |

This independence matters for security architecture: you can safely automate Claude Code in trusted environments without losing the OS-level protection against runaway behavior.

### Hook Context Injection

*[2026-01-17]*: Claude Code 2.1.9 enables PreToolUse hooks to inject context back to the model via `additionalContext`.

**The Problem**: Previously, hooks could only allow or block tool execution. This binary choice forced conservative blocking policies—hooks couldn't provide nuance.

**The Solution**: Hooks can now return context that influences the model's decision-making without hard-blocking:

```python
def pre_tool_use(event):
    tool = event.get("tool")
    params = event.get("parameters", {})

    if tool == "Write" and "/etc" in params.get("path", ""):
        return {
            "additionalContext": {
                "warning": "/etc is a system directory",
                "alternatives": ["/tmp", "~/.config"],
                "guidance": "Consider user-space paths for configuration"
            },
            "action": "allow"  # Let model decide with context
        }

    return {"action": "allow"}
```

### Use Cases

| Pattern | additionalContext Value |
|---------|------------------------|
| Cost warnings | Estimated API cost before expensive calls |
| Safety guardrails | Alternative approaches for risky operations |
| Style guidance | Project conventions before file writes |
| Dynamic permissions | Context-dependent allow/deny decisions |

### Comparison: Block vs. Context Injection

| Approach | When to Use |
|----------|-------------|
| Block (exit 2) | Hard security boundaries—never allow |
| additionalContext | Soft boundaries—model decides with information |

**The mental model**: Context injection enables *safer autonomy*. Models make better decisions when hooks provide visibility rather than just blocking. The hook becomes an advisor, not a gatekeeper.

**Security consideration**: `additionalContext` does not replace blocking for true security boundaries. System directories, credential files, and destructive operations should still use hard blocks. Context injection is for "you probably don't want to do this" cases, not "you must never do this" cases.

**Sources:** [Claude Code Changelog 2.1.9](https://code.claude.com/docs/en/changelog)

---

*Your CLAUDE.md, settings, or setup notes:*


