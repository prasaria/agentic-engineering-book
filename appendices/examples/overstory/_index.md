---
title: "Overstory: Session-as-Orchestrator Multi-Agent System"
description: "Case study of project-agnostic swarm orchestration using TypeScript/Bun with session-based coordination"
created: 2026-02-13
last_updated: 2026-02-13
tags: [case-study, multi-agent, orchestration, overstory, production, typescript, bun, session-based]
part: 4
part_title: Appendices
chapter: 10
section: 4
order: 4.10.4
---

# Overstory: Session-as-Orchestrator Multi-Agent System

Overstory is a production-grade multi-agent orchestration system built in TypeScript/Bun (~31K LOC, 912 tests) that turns a single Claude Code session into a multi-agent team. Created as a project-agnostic alternative to daemon-based coordination, Overstory demonstrates that your active Claude Code session can serve as the orchestrator—no separate mayor process required. Workers spawn in isolated git worktrees via tmux, coordinate through a custom SQLite mail system (~1-5ms query latency), and merge their work back through a four-tier conflict resolution queue.

As of early 2026, Overstory represents one of the most comprehensive explorations of session-as-orchestrator architecture, validating patterns also seen in Gas Town (daemon-based Go implementation) through a fundamentally different technology stack and coordination model.

---

## Core Questions

### Architecture and Design
- How does session-as-orchestrator differ from daemon-based coordination?
- What does "your Claude Code session IS the orchestrator" mean in practice?
- How does two-layer agent definition (base + overlay) enable dynamic capability assignment?

### Novel Mechanisms
- How does SQLite WAL mail achieve ~1-5ms messaging at scale?
- What role does hook-based enforcement play in mechanical safeguards?
- How does 4-tier merge resolution differ from traditional conflict handling?

### Production Realities
- What are the cost implications of subscription vs API token models?
- How does zero-dependency architecture affect deployment and portability?
- What quality gates exist in the merge queue?

### Broader Implications
- Which Overstory patterns transfer to smaller-scale agent systems?
- Where does TypeScript/Bun ecosystem integration help versus hinder?
- What does Overstory reveal about session-based coordination at scale?

---

## Your Mental Model

**Overstory treats your Claude Code session as the factory floor manager, not a worker.** Where most frameworks spawn an external orchestrator daemon, Overstory recognizes that the practitioner already has a conversational interface with context and tools—the active Claude Code session. The `overstory` CLI provides stateful operations (spawn workers, manage queues, merge branches), and hooks provide integration points (SessionStart for priming, UserPromptSubmit for mail injection, PreToolUse for mechanical enforcement). The session coordinates; workers execute in their own tmux-isolated contexts.

**The two-layer definition pattern separates HOW from WHAT.** Base agent definitions (.md files in the `agents/` directory) document HOW agents work (capabilities, workflow, constraints). Per-task overlays (dynamic CLAUDE.md written to each worktree) specify WHAT this specific agent should do (task ID, file scope, expertise domains). This separation enables dynamic capability assignment—the same base "builder" definition supports auth builders, API builders, and test builders through different overlays. A team lead agent crafts overlays for its subordinates, implementing hierarchical delegation without re-explaining core workflows.

---

## Philosophy

Overstory encodes several design principles that distinguish it from conventional multi-agent frameworks. As of early 2026, these principles guide architectural decisions across the 31K LOC implementation.

### Session-as-Orchestrator Principle

The orchestrator need not be a separate process. The practitioner's active Claude Code session already possesses:
- Conversational interface for task decomposition
- Full tool access (Bash, Read, Write, Edit, Grep, Glob)
- Context window for tracking active work
- Hook integration points for system events

External daemons (like Gas Town's Mayor) provide process independence—if the orchestrator crashes, workers continue. Session-as-orchestrator trades this independence for infrastructure simplicity: one fewer process to monitor, no inter-process communication overhead, no daemon lifecycle management. When the orchestrator session terminates, workers retain their state in worktrees; a new orchestrator session resumes coordination through persistent filesystem state (`.overstory/` directory structure).

### Propulsion Principle

Agents execute immediately without permission-seeking. This mirrors Gas Town's GUPP (Gas Town Universal Propulsion Principle) but implements it through different mechanics. Overstory agents receive task specifications in their overlay CLAUDE.md; the presence of a task specification is implicit authorization to proceed. No "wait for approval" steps exist in agent workflows. Forward motion is the default state.

**Rationale:** Permission-seeking creates coordination bottlenecks. At 10-15 concurrent agents, requiring human approval for each step serializes work that should execute in parallel. The propulsion principle shifts human effort from approving actions to reviewing outcomes—quality gates operate on completed work, not proposed actions.

### Zero-Dependency Architecture

Overstory's runtime dependencies consist entirely of Bun built-ins: `bun:sqlite`, `child_process` (for spawning tmux/git), and filesystem APIs. No external npm packages at runtime. Development dependencies (Biome for linting, TypeScript for type checking) do not ship with the binary.

**Implications:**
- **Portability:** Single binary deployment—no npm install, no version conflicts
- **Startup speed:** Bun's fast cold start (~50-100ms for CLI commands)
- **Debugging:** No dependency maze to trace through when things fail
- **Security surface:** Fewer transitive dependencies to audit

### Design Axioms

As of early 2026, Overstory's implementation reflects these architectural axioms:

| Axiom | Statement | Implementation |
|-------|-----------|----------------|
| 1. Worktree Isolation | Every agent operates in a dedicated git worktree | `.overstory/worktrees/{agent-name}/` per agent |
| 2. Typed Messaging | Agent communication uses structured message types | SQLite schema with 8 message types + 4 semantic types |
| 3. Mechanical Enforcement | Tool restrictions enforced via hooks, not prompts | PreToolUse hook blocks disallowed operations |
| 4. Depth-Limited Hierarchy | Agents delegate, but runaway spawning is prevented | Configurable depth limit (default: 2 levels) |
| 5. Clean Exits Only | No lingering resources after agent work completes | Worktree cleanup removes branch + tmux + logs |

---

## Architecture

### Agent Hierarchy

Overstory implements hierarchical delegation with explicit depth limits to prevent runaway spawning:

```
Coordinator (depth 0, orchestrator session)
  │
  ├─→ Supervisor (depth 1, per-project team lead)
  │     │
  │     ├─→ Scout (depth 2, read-only exploration)
  │     ├─→ Builder (depth 2, implementation)
  │     ├─→ Reviewer (depth 2, validation)
  │     └─→ Merger (depth 2, branch integration)
  │
  └─→ Lead (depth 1, can spawn sub-workers)
        │
        └─→ Builder (depth 2, specialist implementation)
```

**Coordinator** is the orchestrator session itself—the practitioner's active Claude Code session. It decomposes high-level objectives, dispatches work to supervisors or directly to workers, and tracks task group progress.

**Supervisor** (depth 1) serves as a per-project team lead. One supervisor agent manages the lifecycle of all workers for a specific project or work stream. Supervisors handle nudging stalled workers, escalating blockers, and coordinating handoffs.

**Workers** (depth 2) execute specific capabilities:
- **Scout** — Read-only exploration and research
- **Builder** — Implementation and code changes
- **Reviewer** — Validation and code review
- **Merger** — Branch merge specialist

**Lead** (depth 1) coordinates teams of specialists. A lead can spawn subordinate builders, scouts, or reviewers for parallel work decomposition. Leads receive tasks that require coordination across multiple files or domains.

**Depth enforcement:** The `overstory sling` command accepts `--depth` parameter. Default max depth is 2 (orchestrator → lead/supervisor → worker). Attempting to spawn beyond max depth returns an error. This prevents infinite delegation chains.

### Two-Layer Agent Definition

Agent definitions separate the HOW (reusable base workflow) from the WHAT (task-specific overlay):

```
┌────────────────────────────────────────────┐
│         Base Definition (agents/*.md)      │
│  "HOW do I work as a builder?"             │
│  - Capabilities list                       │
│  - Standard workflow steps                 │
│  - Constraints and restrictions            │
│  - Communication protocols                 │
└────────────────────────────────────────────┘
                    +
┌────────────────────────────────────────────┐
│    Overlay (worktree/.claude/CLAUDE.md)    │
│  "WHAT is MY specific assignment?"         │
│  - Task ID (bead reference)                │
│  - File scope (exclusive ownership)        │
│  - Spec path (.overstory/specs/...)        │
│  - Parent agent (who spawned me)           │
│  - Expertise domains (mulch priming)       │
└────────────────────────────────────────────┘
                    ↓
    Agent session reads both layers at startup
```

**Example base definition** (`agents/builder.md`):
```markdown
You are a builder agent. Your job is to implement changes according to a spec.

## Capabilities
- Read, Write, Edit files within your assigned file scope
- Run bash commands (git, tests, lint)
- Send mail via `overstory mail send`

## Workflow
1. Read your task spec at the path provided in CLAUDE.md
2. Read relevant expertise via `mulch prime`
3. Implement the changes
4. Run quality gates: tests, linting, type checking
5. Report completion: `bd close <task-id> --reason "summary"`

## Constraints
- Only modify files listed in your FILE_SCOPE
- Never push directly to the canonical branch
- Commit to your worktree branch only
- Never spawn additional agents (you are depth 2)
```

**Example overlay** (generated by `overstory sling`, written to worktree):
```markdown
# .claude/CLAUDE.md
# Auto-generated by overstory. Do not edit.

## Your Assignment
- **Task ID:** bd-abc123
- **Agent Name:** auth-login
- **Spec:** .overstory/specs/bd-abc123.md
- **Branch:** overstory/auth-login/bd-abc123

## File Scope (exclusive ownership)
- src/auth/login.ts
- src/auth/login.test.ts
- src/auth/types.ts

## Expertise
Run: `mulch prime auth api --format json`

## Communication
- Send mail: `overstory mail send --to orchestrator --subject "done" --body "..."`
- Check mail: `overstory mail check`
- Your address: agent-auth-login

## Parent
Spawned by: supervisor-auth
```

The base definition content is injected into the overlay automatically, creating a complete system prompt. This pattern emerged from kotadb issue #200 analysis—team leads only need to specify task parameters (the overlay), not re-explain the agent's core workflow.

### SQLite WAL Mail Protocol

Overstory implements a custom messaging system using SQLite with WAL (Write-Ahead Logging) mode, achieving ~1-5ms query latency suitable for high-frequency polling.

**Why custom mail instead of beads?**
- **Frequency mismatch:** Mail queries occur on every prompt submission (UserPromptSubmit hook). The `bd` CLI spawns at ~50-200ms per invocation—acceptable for task management, too slow for 10+ agents polling every prompt.
- **Abstraction mismatch:** Beads model issues with status/priority/assignee. Messages need from/to/subject/body/thread semantics.
- **Separation of concerns:** Beads = task lifecycle. Mail = agent communication. Independent failure domains.

**Schema:**
```sql
-- .overstory/mail.db
CREATE TABLE IF NOT EXISTS messages (
  id TEXT PRIMARY KEY,              -- "msg-" + nanoid(12)
  from_agent TEXT NOT NULL,         -- sender agent name
  to_agent TEXT NOT NULL,           -- recipient agent name or "orchestrator"
  subject TEXT NOT NULL,
  body TEXT NOT NULL,
  type TEXT NOT NULL DEFAULT 'status',    -- 8 protocol types
  priority TEXT NOT NULL DEFAULT 'normal', -- low | normal | high | urgent
  thread_id TEXT,                   -- optional: group related messages
  read INTEGER NOT NULL DEFAULT 0,  -- 0 = unread, 1 = read
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_inbox ON messages(to_agent, read);
CREATE INDEX IF NOT EXISTS idx_thread ON messages(thread_id);
```

**Message types:**
1. `status` — Progress updates, state changes
2. `question` — Requesting clarification or guidance
3. `result` — Work completion with summary
4. `error` — Failure reporting
5. `dispatch` — Task assignment (orchestrator → worker)
6. `escalation` — Blocked, needs human intervention
7. `worker_done` — Agent completed task, ready for merge
8. `merge_ready` — Branch merged successfully

**Priority levels:**
- `low` — Informational, no urgency
- `normal` — Standard updates
- `high` — Attention recommended soon
- `urgent` — Immediate attention required; auto-nudges recipient

**Hook integration:**
```json
// .claude/settings.local.json (deployed to each worktree)
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "overstory mail check --inject --agent $OVERSTORY_AGENT_NAME"
      }]
    }]
  }
}
```

On every prompt submission, the hook queries:
```sql
SELECT * FROM messages
WHERE to_agent = $OVERSTORY_AGENT_NAME AND read = 0
ORDER BY created_at ASC;
```

The `--inject` flag formats results for context injection:
```
You have 2 unread messages:

[msg-x1y2z3] From: auth-signup | Subject: Build complete
Body: Implemented signup flow. Tests passing. Ready for merge.

[msg-a4b5c6] From: orchestrator | Subject: Clarification needed
Body: Does the signup flow handle email verification?
```

Query latency with proper indexing: ~1-5ms even with thousands of messages. WAL mode allows concurrent readers + single writer—multiple agent worktrees can all query mail.db simultaneously.

### Worktree Isolation

Each agent operates in a dedicated git worktree, providing:
- **Filesystem isolation:** No file conflicts between concurrent agents
- **Branch isolation:** Each worktree checks out its own branch (`overstory/{agent-name}/{task-id}`)
- **State isolation:** Agent workspace cleanup doesn't affect other agents
- **Context isolation:** Each agent session runs in its own tmux session

```
.overstory/worktrees/
├── auth-login/            # Builder agent #1
│   ├── .git → main repo
│   ├── .claude/
│   │   ├── CLAUDE.md      # Overlay with task specifics
│   │   └── settings.local.json  # Hooks config
│   └── src/auth/...       # Code being modified
├── auth-signup/           # Builder agent #2
│   └── ...
└── auth-reviewer/         # Reviewer agent
    └── ...
```

**Worktree lifecycle:**
1. `overstory sling --task bd-abc --capability builder --name auth-login`
   - Creates worktree at `.overstory/worktrees/auth-login/`
   - Checks out branch `overstory/auth-login/bd-abc`
   - Writes overlay CLAUDE.md
   - Deploys hooks to `.claude/settings.local.json`
   - Sets env var `OVERSTORY_AGENT_NAME=auth-login`
   - Starts tmux session `overstory-auth-login`
   - Launches `claude` inside tmux

2. Agent works in isolation, commits to its branch

3. `bd close bd-abc --reason "implemented login flow"`
   - Pushes branch to remote
   - Sends mail: type=`worker_done`, to=`orchestrator`

4. `overstory merge --branch overstory/auth-login/bd-abc`
   - Merges via 4-tier resolution
   - On success, marks branch merged

5. `overstory worktree clean auth-login`
   - Removes worktree directory
   - Deletes branch reference (if merged)
   - Kills tmux session
   - Logs are preserved (never auto-deleted)

### The Merge Queue (4-Tier Resolution)

Workers never push directly to the canonical branch (main/develop). Every code change flows through the merge queue with automated conflict escalation:

```
Agent completes work → bd close → worker_done mail
                                         ↓
                              overstory merge --branch X
                                         ↓
                            ┌────────────────────────┐
                            │  Tier 1: Clean Merge   │  git merge succeeds (seconds)
                            └─────────┬──────────────┘
                                      │ Conflicts?
                                      ↓
                            ┌────────────────────────┐
                            │ Tier 2: Auto-Resolve   │  Standard conflict regions (seconds)
                            └─────────┬──────────────┘
                                      │ Still conflicts?
                                      ↓
                            ┌────────────────────────┐
                            │  Tier 3: AI Resolve    │  AI reads both versions, merges (minutes)
                            └─────────┬──────────────┘
                                      │ Irreconcilable?
                                      ↓
                            ┌────────────────────────┐
                            │  Tier 4: Re-Imagine    │  AI re-implements change vs current main
                            └────────────────────────┘  (minutes to hours)
```

**Tier 1: Clean Merge**
Standard `git merge` succeeds. Most common case when agents work on disjoint file sets with proper file scope assignment. Completes in seconds.

**Tier 2: Auto-Resolve**
Git detects conflicts but conflict markers follow standard patterns (separate regions, no interdependencies). Automated resolution merges sections by choosing "ours" for structural changes, "theirs" for additions. Completes in seconds.

**Tier 3: AI Resolve**
Spawn ephemeral Claude session to read both versions, understand intent, produce merged result. This tier handles overlapping changes where both versions contain valid logic that must coexist. Completes in minutes (depends on code complexity).

**Tier 4: Re-Imagine**
When merge drift is severe (agent branch diverged significantly from main), reimplementation becomes cheaper than conflict archaeology. Spawn Claude session to re-implement the agent's original intent against current main. Preserves the goal; discards the specific implementation path. Completes in minutes to hours.

**Configuration:**
```yaml
# .overstory/config.yaml
merge:
  aiResolveEnabled: true     # Enable Tier 3
  reimagineEnabled: true     # Enable Tier 4
```

Tiers 3-4 can be disabled for projects where human review is preferred for conflicts.

### Tiered Health Monitoring

Overstory implements supervision through three tiers, inspired by Gas Town's watchdog architecture but adapted for session-based coordination:

```
Tier 0: Mechanical Daemon (no AI, fastest)
  │     Process monitoring via tmux and PID checks
  │     Resource limits (CPU, memory thresholds)
  │     Runs: Every 5-30 seconds
  │
Tier 1: AI Triage (ephemeral, fast reasoning)
  │     "What kind of failure is this?"
  │     Spawned when Tier 0 detects anomaly
  │     Runs: On-demand
  │
Tier 2: Monitor Agent (persistent, slow patrol)
  │     Continuous fleet health assessment
  │     Strategic intervention planning
  │     Runs: Continuously in background tmux session
  │
Tier 3: Supervisor (per-project oversight)
        Manages worker lifecycle for a project
        Handles escalations and handoffs
        Runs: Active session, responds to events
```

**Tier 0: Mechanical Daemon** (`overstory watch`)
Go-style daemon (TypeScript via Bun) performing mechanical checks:
- Is tmux session alive for each active agent?
- Is Claude Code process responsive?
- Has agent exceeded resource limits?
- Time since last activity (stale threshold)?

No AI reasoning—pure system monitoring. Logs health check results to `.overstory/logs/watchdog/`.

**Tier 1: AI Triage** (ephemeral)
When Tier 0 detects an anomaly (process died, agent stale), spawn ephemeral triage agent to classify:
- Process crash (restart agent)
- Context exhaustion (spawn fresh session with seancing)
- Genuine stuck state (escalate to Tier 2)
- Resource limit hit (notify orchestrator)

Triage agent examines logs, recent tool use, mail history. Completes in <1 minute.

**Tier 2: Monitor Agent** (`overstory monitor start`)
Persistent agent running in dedicated tmux session, continuously patrolling:
- Overall system progress (are tasks advancing?)
- Cross-agent patterns (multiple scouts stalling suggests unclear specs)
- Queue depths (merge queue backing up?)
- Resource trends (average agent lifetime, merge success rate)

Sends periodic status reports to orchestrator. Escalates strategic concerns.

**Tier 3: Supervisor** (per-project)
Human-readable oversight agent managing a specific project's workers:
- Receives escalations from Tier 2
- Nudges stalled agents with context-specific guidance
- Coordinates handoffs when agents block on each other
- Reports project-level progress to orchestrator

Runs as active session (not background daemon). Supervisors are depth-1 agents.

---

## Novel Contributions

Overstory introduces several mechanisms not commonly found in existing agent frameworks. These contributions represent architectural explorations that generalize beyond the specific TypeScript/Bun implementation.

### Session-as-Orchestrator vs Daemon-Based

| Dimension | Session-as-Orchestrator (Overstory) | Daemon-Based (Gas Town) |
|-----------|-------------------------------------|------------------------|
| **Infrastructure** | No separate process—orchestrator IS your active session | External Mayor process coordinates |
| **Crash resilience** | Orchestrator crash stops coordination; workers retain state | Mayor survives independent of human session |
| **Startup complexity** | Open Claude Code in project → immediately orchestrator | Spawn Mayor, configure, connect |
| **Human interface** | Natural conversation with orchestrator | CLI commands to daemon |
| **Resource overhead** | One fewer process (no Mayor) | Mayor + Deacon + monitoring daemons |
| **State handoff** | Resume from filesystem state after session restart | Continuous state in Mayor memory |

**Trade-off analysis:**
Session-as-orchestrator sacrifices orchestrator crash independence for infrastructure simplicity. When the orchestrator session terminates (intentional or crash), coordination pauses. Workers preserve their state in worktrees; a fresh orchestrator session resumes coordination by reading filesystem state (`.overstory/` directory structure, mail.db, agent manifests).

Daemon-based orchestration (Gas Town's Mayor) continues coordination even if the human terminates their session. The Mayor process is independent. This resilience costs infrastructure complexity: the Mayor must be spawned, monitored, and communicated with via IPC or CLI.

**When session-as-orchestrator works:**
- Projects where human oversight is continuous (practitioner stays engaged)
- Development workflows (not long-running production deployments)
- Environments where orchestrator restart is acceptable (minutes of downtime)

**When daemon-based works:**
- Overnight agent runs (human disconnects, agents continue)
- Production deployments (orchestrator must survive human session crashes)
- Multi-user environments (orchestrator serves multiple human sessions)

### Hook-Based Mechanical Enforcement

Overstory's PreToolUse hook provides mechanical restrictions beyond prompt-based guidance:

```json
// .claude/settings.local.json (read-only scout)
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "command": "overstory log tool-blocked --agent $OVERSTORY_AGENT_NAME --tool $TOOL_NAME && exit 1"
      }]
    }]
  }
}
```

**Before Claude Code invokes Write or Edit**, the hook runs. The `exit 1` prevents tool execution. The scout agent receives error message: "Tool use blocked by hook."

**Contrast with prompt-based restrictions:**
```markdown
## Constraints
- You are a read-only agent. Never use Write or Edit tools.
```

Prompt-based restrictions rely on model compliance. Models occasionally ignore constraints ("I know you said read-only, but I'll just make a small fix..."). Hook-based enforcement is mechanical—the tool simply won't execute.

**Implementation pattern:**
```typescript
// src/agents/hooks-deployer.ts
function deployHooks(capability: string, worktreePath: string) {
  const restrictions = TOOL_RESTRICTIONS[capability];
  const hooks = {
    PreToolUse: restrictions.blockedTools.map(tool => ({
      matcher: tool,
      hooks: [{
        type: "command",
        command: `overstory log tool-blocked --agent ${agentName} --tool ${tool} && exit 1`
      }]
    }))
  };
  writeFileSync(`${worktreePath}/.claude/settings.local.json`, JSON.stringify(hooks));
}
```

**Tool restriction matrix:**

| Capability | Allowed Tools | Blocked Tools | Enforcement |
|------------|---------------|---------------|-------------|
| Scout | Read, Grep, Glob, Bash (read-only) | Write, Edit | PreToolUse hook |
| Builder | Read, Write, Edit, Grep, Glob, Bash | (none) | File scope enforced via prompt |
| Reviewer | Read, Grep, Glob, Bash (read-only) | Write, Edit | PreToolUse hook |
| Merger | Read, Write (git only), Bash | Edit (app code) | PreToolUse hook + git path filter |

### SQLite Performance Characteristics

Overstory's mail system demonstrates that SQLite is viable for high-frequency agent coordination:

**Benchmark data (as of early 2026):**
- Query latency: ~1-5ms (SELECT with indexed WHERE clause)
- Insert latency: ~2-8ms (single message)
- Concurrent readers: 10+ agents polling simultaneously (WAL mode)
- Database size: ~1MB per 10,000 messages (negligible for most projects)

**Configuration for performance:**
```typescript
// src/mail/store.ts
db.exec("PRAGMA journal_mode=WAL");       // Write-Ahead Logging
db.exec("PRAGMA synchronous=NORMAL");     // Balance durability/speed
db.exec("PRAGMA busy_timeout=5000");      // 5s wait on lock contention
db.exec("PRAGMA cache_size=-64000");      // 64MB cache
```

WAL mode is critical: it allows multiple concurrent readers while one writer operates. Without WAL, SQLite serializes all database access—unacceptable for 10+ agents polling.

**Comparison with other messaging approaches:**

| Approach | Latency | Concurrency | Persistence | Complexity |
|----------|---------|-------------|-------------|------------|
| SQLite (WAL) | ~1-5ms | Readers parallel, 1 writer | Durable | Low (stdlib) |
| File-based mail | ~10-50ms (stat + read) | Requires file locking | Durable | Low (stdlib) |
| Redis | ~1-3ms (network RTT) | High | Optional | Medium (external service) |
| Message queue | ~5-20ms | High | Durable | High (Kafka, RabbitMQ, etc.) |

SQLite provides the sweet spot for agent swarm messaging: low latency, durable persistence, zero external dependencies. The file-based database lives in `.overstory/mail.db`; backups and version control are straightforward.

### TypeScript/Bun Ecosystem Integration

Overstory's technology choices demonstrate both benefits and constraints of the TypeScript/Bun ecosystem:

**Benefits:**
- **Fast startup:** Bun cold starts in ~50-100ms; CLI commands feel instant
- **Native APIs:** `bun:sqlite` provides C-level performance without native modules
- **Type safety:** Strict TypeScript catches errors at development time
- **Single binary:** `bun build --compile` produces standalone executable
- **Zero runtime deps:** No `node_modules` to ship or version-match

**Constraints:**
- **Ecosystem maturity:** Bun is young (v1.x as of early 2026); edge cases exist
- **Platform support:** Linux/macOS mature; Windows support improving
- **Debugging tools:** Less mature than Node.js ecosystem
- **Community size:** Smaller than Node.js; fewer resources when troubleshooting

**Language lock-in comparison:**

| Dimension | Overstory (TypeScript/Bun) | Gas Town (Go) |
|-----------|----------------------------|---------------|
| Ecosystem size | Large (npm) | Medium (Go modules) |
| Startup speed | Fast (~50-100ms) | Fast (~10-50ms) |
| Memory footprint | Medium (V8 engine) | Small (Go runtime) |
| Concurrency model | Event loop (async/await) | Goroutines |
| Cross-platform | Good (via Bun) | Excellent (Go native) |
| Binary size | ~40-50MB (bundled Bun) | ~10-20MB (Go static) |

Neither approach is universally superior. TypeScript/Bun benefits from npm ecosystem breadth; Go benefits from mature concurrency and smaller binaries. The convergence of patterns across both implementations suggests architectural patterns are language-agnostic.

---

## The Overstory CLI

The `overstory` binary serves as the complete interface. Every operation—spawning agents, checking mail, merging branches, monitoring health—goes through CLI commands.

### Core Workflow Commands

```bash
# Initialize .overstory/ in project root
overstory init

# Spawn a worker agent
overstory sling bd-abc123 --capability builder --name auth-login \
  --spec .overstory/specs/bd-abc123.md \
  --files src/auth/login.ts,src/auth/types.ts

# Load context for orchestrator
overstory prime

# Load context for specific agent (during compaction or restart)
overstory prime --agent auth-login --compact

# Show system state (all active agents, worktrees, task progress)
overstory status

# Live TUI dashboard for monitoring
overstory dashboard
```

### Communication Commands

```bash
# Send a message
overstory mail send --to orchestrator --subject "Build complete" \
  --body "Implemented login flow. Tests passing." --type result

# Check inbox (human-readable)
overstory mail check

# Check inbox for specific agent (JSON output)
overstory mail check --agent auth-login --json

# Check inbox and format for hook injection
overstory mail check --inject

# List all mail with filters
overstory mail list --from auth-login --unread

# Mark message as read
overstory mail read msg-x1y2z3

# Reply to message (preserves thread)
overstory mail reply msg-x1y2z3 --body "Acknowledged, proceeding."

# Nudge a stalled agent (sends text message via mail)
overstory nudge auth-login "Check if the test data is properly seeded."
```

### Integration Commands

```bash
# Install hooks to .claude/settings.local.json
overstory hooks install

# Uninstall hooks
overstory hooks uninstall

# Check hook installation status
overstory hooks status

# Merge a single branch through 4-tier resolution
overstory merge --branch overstory/auth-login/bd-abc123

# Merge all completed agent branches
overstory merge --all

# Dry-run to check for conflicts
overstory merge --branch overstory/auth-login/bd-abc123 --dry-run

# List worktrees with status
overstory worktree list

# Clean completed worktrees
overstory worktree clean --completed

# Clean specific worktree
overstory worktree clean auth-login
```

### Monitoring Commands

```bash
# Start watchdog daemon (Tier 0 mechanical monitoring)
overstory watch --background

# Start Tier 2 monitor agent (persistent fleet patrol)
overstory monitor start

# Stop monitor agent
overstory monitor stop

# Show session metrics
overstory metrics --last 10

# Show metrics as JSON
overstory metrics --json

# Log a hook event (called by hooks, not directly by humans)
overstory log session-start --agent auth-login
```

### Coordination Commands

```bash
# Start persistent coordinator agent (orchestrator)
overstory coordinator start

# Stop coordinator
overstory coordinator stop

# Check coordinator status
overstory coordinator status

# Start per-project supervisor
overstory supervisor start

# Stop supervisor
overstory supervisor stop

# Create a task group for batch coordination
overstory group create auth-module

# Add issues to group
overstory group add auth-module bd-abc123 bd-def456 bd-ghi789

# Show group progress
overstory group status auth-module

# List all groups
overstory group list
```

---

## Production Realities

### Cost and Economics

Overstory's subscription-based cost model contrasts with API-token-based systems:

| Dimension | Overstory (Subscription) | Gas Town (API Tokens) |
|-----------|--------------------------|----------------------|
| **Base cost** | Claude Code Pro subscription (~$20/month, 2026 pricing) | $0 base, pay-per-token |
| **Agent cost** | Included in subscription (up to tier limits) | ~$3-5 per agent-hour (Claude Opus) |
| **20-agent swarm** | Fixed monthly cost | ~$60-100/hour runtime cost |
| **Economic incentive** | Maximize utilization within subscription | Minimize token usage per task |
| **Bottleneck** | Subscription tier limits, human design time | Token budget, cost approval |

**Implications:**
- **Fixed-cost model:** Practitioners optimize for throughput (how much work can agents complete per month?) rather than per-token efficiency.
- **Subscription tiers:** Claude Code Pro supports limited concurrent agents; Enterprise tiers may raise limits.
- **Cost predictability:** Monthly cost is predictable; no surprise bills from runaway agent usage.
- **Design pressure:** The bottleneck shifts to human design capacity—how quickly can the practitioner decompose work and write specs?

**When subscription model works:**
- Steady agent workload (agents utilized most days)
- Budget predictability valued (fixed monthly cost)
- Per-token accounting overhead unwanted

**When API token model works:**
- Bursty agent usage (heavy use for a week, then idle)
- Pay-per-use preferred (align cost with value delivered)
- Cost attribution required (charge agent usage to specific projects)

### Zero-Dependency Deployment

Overstory's architecture demonstrates the benefits and trade-offs of zero runtime dependencies:

**Deployment:**
```bash
# Build standalone binary
cd overstory
bun build --compile src/index.ts --outfile overstory

# Copy to target system (no npm install required)
scp overstory user@target-system:/usr/local/bin/

# Run immediately (Bun runtime bundled in binary)
overstory init
```

**Benefits:**
- **No version conflicts:** No `node_modules` to manage
- **Fast installation:** Copy single binary
- **Reproducibility:** Same binary works across machines
- **Security surface:** Fewer dependencies to audit

**Trade-offs:**
- **Binary size:** ~40-50MB (includes Bun runtime)
- **Update friction:** Must rebuild and redistribute binary for updates
- **Platform-specific builds:** Separate binaries for Linux/macOS/Windows

**Contrast with node_modules approach:**
```bash
# Traditional Node.js deployment
npm install overstory-cli -g

# Now managing:
# - Node version compatibility
# - 100+ transitive dependencies
# - Potential version conflicts with other global packages
```

Overstory's zero-dependency stance reflects a design philosophy: infrastructure simplicity over ecosystem convenience. The cost is binary size and platform-specific builds; the benefit is deployment predictability.

### Quality Trade-offs

Overstory's 4-tier merge resolution makes explicit quality trade-offs:

**Accepted:**
- Tier 3-4 merges may not preserve original agent implementation details (intent preserved, specifics discarded)
- AI-resolved conflicts may introduce subtle bugs not caught by automated tests
- Re-imagination (Tier 4) can diverge from agent's original approach

**Mitigated:**
- Test suites run after every merge (validation gate)
- Human review remains available for complex merges
- Merge tier escalation is visible in logs (audit trail)
- Worktree branches preserved until explicitly cleaned (rollback possible)

**Unresolved (as of early 2026):**
- No automated verification that Tier 3-4 merges preserve semantic intent
- Complex conflicts may require human review despite AI resolution attempts
- Merge queue can become bottleneck with 15+ concurrent agents producing rapid changes

---

## Criticisms and Limitations

### Early Maturity

As of early 2026, Overstory is production-capable but not production-proven across diverse organizations:

**Maturity indicators:**
- **Implementation completeness:** Full Phase 1-3 feature set (912 tests, 31K LOC)
- **Operational validation:** Limited to creator's projects; not yet battle-tested at scale
- **Edge case coverage:** Known unknowns exist around multi-project coordination, long-running tasks (days/weeks)
- **Documentation depth:** Comprehensive technical docs; limited practitioner guides

**Comparison with Gas Town maturity:**
Gas Town (as of early 2026) has operational validation with 20-30 concurrent agents on production projects. Overstory demonstrates architectural completeness without equivalent operational history.

**Risk mitigation:**
- Start with 3-5 agents to learn operational patterns
- Establish monitoring and alerting before scaling beyond 10 agents
- Maintain manual override paths for merge queue and agent spawning
- Expect edge cases requiring human intervention

### TypeScript/Bun Ecosystem Lock-in

Overstory's Bun dependency creates technology stack lock-in:

**Portability considerations:**
- **Runtime requirement:** Target systems must support Bun (or run compiled binary)
- **Platform support:** Linux/macOS mature; Windows improving but less tested
- **Upgrade path:** Bun major version changes may require code updates
- **Ecosystem evolution:** Bun is young (v1.x); breaking changes possible

**Migration path complexity:**
Porting Overstory to Node.js would require:
- Replacing `bun:sqlite` with `better-sqlite3` or similar
- Replacing Bun-specific APIs (spawn, filesystem)
- Managing npm dependencies (losing zero-dependency property)
- Re-tuning performance characteristics

**Mitigation:**
- Core patterns (session-as-orchestrator, two-layer definitions, SQLite mail) are implementation-agnostic
- Architectural documentation enables reimplementation in other languages/runtimes
- Bun's maturity trajectory suggests ecosystem lock-in risk decreases over time

### Cognitive Load

Managing 10-15 concurrent agents via session-based coordination creates distinct cognitive demands:

**Orchestrator session mental model:**
- Track which agents are active (dashboard/status commands)
- Review incoming mail from workers (check inbox regularly)
- Make design decisions when agents escalate blockers
- Coordinate merge order when conflicts arise
- Monitor overall system progress (are tasks advancing?)

**Comparison with daemon-based orchestration:**
Daemon-based systems (Gas Town's Mayor) externalize coordination state. The human issues commands to the daemon; the daemon tracks agent state. Session-as-orchestrator internalizes coordination state—the human's session IS the coordinator.

**Cognitive load mitigation strategies:**
- **Dashboard TUI:** `overstory dashboard` provides live fleet visualization
- **Automated mail injection:** Hooks surface agent messages without polling
- **Task groups:** Batch tracking reduces individual task attention
- **Supervisor agents:** Offload per-project coordination to depth-1 supervisors

**Scale ceiling:**
Session-based coordination likely hits cognitive limits at 15-20 agents. Beyond that, external orchestrator daemons (Gas Town's Mayor) may provide better human-machine interface. The practitioner's attention becomes the bottleneck.

---

## Lessons for Practitioners

Overstory's architecture encodes several principles applicable to multi-agent systems at any scale, regardless of technology stack.

### 1. Session-as-Orchestrator Viability

The orchestrator need not be a separate process. For projects with continuous human oversight, the practitioner's active session serves as a natural coordination point. Benefits:
- No daemon lifecycle management (one fewer process to monitor)
- Natural conversational interface (human talks to orchestrator directly)
- Infrastructure simplicity (no IPC, no daemon configuration)

**Transfer pattern:**
Any multi-agent system with a primary human operator can adopt session-as-orchestrator. Implement:
- Persistent state on filesystem (survive session restarts)
- Hook integration for event notifications (SessionStart, UserPromptSubmit)
- CLI or conversation interface for agent management

### 2. Two-Layer Agent Definitions

Separating HOW (base workflow) from WHAT (task specifics) enables dynamic capability assignment. The base definition is reusable; the overlay specifies the assignment.

**Transfer pattern:**
When spawning agents in any framework:
- Write reusable base definitions (capabilities, workflow, constraints)
- Generate per-task overlays (task ID, file scope, parent agent, expertise domains)
- Inject base content into overlay (single complete system prompt)

Hierarchical delegation becomes simpler: parent agents craft overlays, not full system prompts.

### 3. SQLite for High-Frequency Messaging

File-based SQL databases (SQLite with WAL mode) provide sufficient performance for agent coordination:
- ~1-5ms query latency (indexed queries)
- Concurrent readers + single writer (WAL mode)
- Zero external dependencies (bundled with most languages)
- Durable persistence (survives crashes)

**Transfer pattern:**
For any system requiring agent-to-agent messaging or event logging:
- Use SQLite with WAL mode for high-frequency operations
- Create indexes on frequent query patterns (e.g., `inbox WHERE to_agent = X AND read = 0`)
- Set `busy_timeout` for lock contention handling
- Reserve external message queues (Redis, Kafka) for systems requiring distributed coordination across machines

### 4. Hook-Based Mechanical Enforcement

Tool restrictions enforced via PreToolUse hooks provide mechanical guarantees beyond prompt-based guidance. Models occasionally ignore prompt constraints; hooks mechanically block disallowed operations.

**Transfer pattern:**
For any agent system with capability restrictions (read-only agents, file scope limits):
- Implement PreToolUse hooks that check tool names and parameters
- Return non-zero exit code to block disallowed operations
- Log blocked attempts (observability for debugging)
- Combine with prompt-based guidance (defense in depth)

### 5. 4-Tier Merge Resolution

Automated conflict escalation handles the spectrum from clean merges (seconds) to complex reimplementation (hours):
1. Try clean merge (fast, most common)
2. Auto-resolve standard conflicts (fast, handles many cases)
3. AI-assisted merge (slower, handles overlapping logic)
4. Reimplementation (slowest, handles severe drift)

**Transfer pattern:**
Any multi-agent system producing concurrent code changes benefits from tiered resolution:
- Implement Tier 1-2 with standard git tooling
- Reserve Tier 3-4 for projects where human merge overhead exceeds AI merge risk
- Make each tier configurable (enable/disable based on project tolerance)

### 6. Zero-Dependency Architecture Benefits

Minimizing runtime dependencies improves deployment predictability:
- Single binary or minimal dependency set
- No transitive dependency version conflicts
- Faster installation (no dependency resolution)
- Smaller security surface (fewer packages to audit)

**Transfer pattern:**
When building agent infrastructure:
- Prefer language standard libraries over external packages
- Bundle dependencies when possible (single executable)
- Document the trade-off: ecosystem convenience vs deployment simplicity
- Accept that zero-dependency is not always achievable or desirable (choose consciously)

---

## Comparison with Other Approaches

| Dimension | Overstory | Gas Town | Claude Code Agent Teams |
|-----------|-----------|----------|------------------------|
| **Orchestrator** | Session-as-orchestrator (your active Claude session) | External daemon (Mayor) | Implicit (Claude Code manages) |
| **Agent identity** | Persistent (CVs, work history via identity.yaml) | Persistent (Beads-backed CVs) | Ephemeral (per-session) |
| **Coordination** | SQLite mail (~1-5ms) | Typed mail protocol | Peer-to-peer messaging |
| **Work tracking** | Beads (bd CLI) for tasks, SQLite for messages | Beads (MEOW: Formula/Protomolecule/Molecule) | Shared task list |
| **Quality gates** | 4-tier merge resolution | Refinery with AI reimagination | Human review |
| **Scale target** | 10-15 agents (session cognitive limits) | 20-30 agents | 2-10 agents |
| **Persistence** | Filesystem (.overstory/ directory) | Git-backed Beads (JSONL + SQLite) | None (session-scoped) |
| **Runtime** | TypeScript/Bun (~40-50MB binary) | Go (~10-20MB binary) | Built into Claude Code |
| **Cost model** | Subscription (fixed monthly) | API tokens (~$100/hr for 20-30 agents) | Subscription (included) |
| **Failure handling** | Tiered watchdog + supervisor agents | NDI (Nondeterministic Idempotence) | Manual retry |
| **Agent definition** | Two-layer (base .md + overlay CLAUDE.md) | Similar pattern | Implicit (prompts) |
| **Merge strategy** | 4-tier automated escalation | Refinery (dedicated AI agent) | Manual or CI/CD |
| **Hierarchy** | Depth-limited (default 2 levels) | Town/Rig structure (explicit depth) | Flat (teammates) |

**Architectural convergence:**
Both Overstory and Gas Town converge on:
- Persistent identity, ephemeral sessions
- Worktree isolation for concurrent agents
- Typed message protocols (mail systems)
- Tiered health monitoring (watchdog chains)
- Merge queue infrastructure (quality gates)
- Git-backed persistence (filesystem state)

The convergence across different technology stacks (TypeScript/Bun vs Go) and coordination models (session vs daemon) suggests these patterns are fundamental to swarm coordination, not artifacts of specific implementations.

---

## Technical Implementation Details

### Directory Structure

**In target project (after `overstory init`):**
```
target-project/
├── .overstory/
│   ├── config.yaml                   # Project configuration
│   ├── agent-manifest.json           # Agent registry
│   ├── hooks.json                    # Central hooks config
│   ├── agents/                       # Agent state
│   │   └── {name}/
│   │       ├── identity.yaml         # Persistent identity
│   │       └── work-history.md       # Append-only log
│   ├── worktrees/                    # Git worktrees (gitignored)
│   │   └── {agent-name}/
│   ├── specs/                        # Task specifications
│   │   └── {bead-id}.md
│   ├── logs/                         # Agent logs (gitignored)
│   │   └── {agent-name}/{timestamp}/
│   │       ├── session.log           # Human-readable
│   │       ├── events.ndjson         # Machine-parseable
│   │       ├── tools.ndjson          # Tool use log
│   │       └── errors.log            # Stack traces
│   ├── mail.db                       # SQLite mail (gitignored, WAL)
│   └── metrics.db                    # SQLite metrics (gitignored)
├── .gitignore                        # Updated with .overstory/worktrees, logs
└── .claude/
    └── CLAUDE.md                     # Updated with overstory awareness
```

**The `overstory` repository itself:**
```
overstory/
├── src/
│   ├── index.ts                      # CLI entry point (command router)
│   ├── types.ts                      # Shared types and interfaces
│   ├── config.ts                     # Config loader + validation
│   ├── errors.ts                     # Custom error types
│   ├── commands/                     # One file per CLI subcommand (17 commands)
│   │   ├── coordinator.ts            # Persistent orchestrator lifecycle
│   │   ├── supervisor.ts             # Team lead management
│   │   ├── dashboard.ts              # Live TUI dashboard
│   │   ├── hooks.ts                  # Orchestrator hooks management
│   │   ├── sling.ts                  # Agent spawning
│   │   ├── group.ts                  # Task group batch tracking
│   │   ├── nudge.ts                  # Agent nudging
│   │   ├── mail.ts                   # Inter-agent messaging
│   │   ├── monitor.ts                # Tier 2 monitor management
│   │   ├── merge.ts                  # Branch merging
│   │   ├── status.ts                 # Fleet status overview
│   │   ├── prime.ts                  # Context priming
│   │   ├── init.ts                   # Project initialization
│   │   ├── worktree.ts               # Worktree management
│   │   ├── watch.ts                  # Watchdog daemon
│   │   ├── log.ts                    # Hook event logging
│   │   └── metrics.ts                # Session metrics
│   ├── agents/                       # Agent lifecycle management
│   │   ├── manifest.ts               # Agent registry (load + query)
│   │   ├── overlay.ts                # Dynamic CLAUDE.md overlay generator
│   │   ├── identity.ts               # Persistent agent identity (CVs)
│   │   ├── checkpoint.ts             # Session checkpoint save/restore
│   │   ├── lifecycle.ts              # Handoff orchestration
│   │   └── hooks-deployer.ts         # Deploy hooks + tool enforcement
│   ├── worktree/                     # Git worktree + tmux management
│   │   ├── manager.ts
│   │   └── tmux.ts
│   ├── mail/                         # SQLite mail system (typed protocol)
│   │   ├── store.ts
│   │   └── client.ts
│   ├── merge/                        # FIFO queue + conflict resolution
│   │   ├── queue.ts
│   │   └── resolver.ts
│   ├── watchdog/                     # Tiered health monitoring
│   │   ├── daemon.ts                 # Tier 0 mechanical
│   │   ├── triage.ts                 # Tier 1 AI classification
│   │   └── health.ts                 # Health check definitions
│   ├── logging/                      # Multi-format logger + sanitizer + reporter
│   │   ├── logger.ts
│   │   ├── sanitizer.ts
│   │   └── reporter.ts
│   ├── metrics/                      # SQLite metrics + transcript parsing
│   │   ├── store.ts
│   │   └── summary.ts
│   ├── beads/                        # bd CLI wrapper + molecules
│   │   ├── client.ts
│   │   └── molecules.ts
│   └── mulch/                        # mulch CLI wrapper
│       └── client.ts
├── agents/                           # Base agent definitions (8 roles)
│   ├── coordinator.md
│   ├── supervisor.md
│   ├── scout.md
│   ├── builder.md
│   ├── reviewer.md
│   ├── lead.md
│   ├── merger.md
│   └── monitor.md
├── templates/                        # Templates for overlays and hooks
│   ├── CLAUDE.md.tmpl
│   ├── overlay.md.tmpl
│   └── hooks.json.tmpl
├── package.json
├── tsconfig.json
├── biome.json
└── README.md
```

### The `overstory` Binary

The CLI is the entire interface. All commands route through `src/index.ts`:

```typescript
// src/index.ts (simplified)
#!/usr/bin/env bun

const command = process.argv[2];

switch (command) {
  case "init": await initCommand(); break;
  case "sling": await slingCommand(); break;
  case "prime": await primeCommand(); break;
  case "status": await statusCommand(); break;
  case "dashboard": await dashboardCommand(); break;
  case "mail": await mailCommand(); break;
  case "merge": await mergeCommand(); break;
  case "worktree": await worktreeCommand(); break;
  case "hooks": await hooksCommand(); break;
  case "coordinator": await coordinatorCommand(); break;
  case "supervisor": await supervisorCommand(); break;
  case "group": await groupCommand(); break;
  case "nudge": await nudgeCommand(); break;
  case "monitor": await monitorCommand(); break;
  case "watch": await watchCommand(); break;
  case "log": await logCommand(); break;
  case "metrics": await metricsCommand(); break;
  default:
    console.error(`Unknown command: ${command}`);
    process.exit(1);
}
```

Commands are self-contained modules in `src/commands/`. Each exports a default async function handling the command logic.

### Hook Integration

Hooks provide integration points between Claude Code sessions and Overstory infrastructure:

```json
// .overstory/hooks.json (central config)
{
  "SessionStart": [{
    "type": "command",
    "command": "overstory prime --agent $OVERSTORY_AGENT_NAME"
  }],
  "UserPromptSubmit": [{
    "matcher": "",
    "hooks": [{
      "type": "command",
      "command": "overstory mail check --inject --agent $OVERSTORY_AGENT_NAME"
    }]
  }],
  "PreToolUse": [{
    "matcher": "Write|Edit",
    "hooks": [{
      "type": "command",
      "command": "overstory log tool-attempt --agent $OVERSTORY_AGENT_NAME --tool $TOOL_NAME"
    }]
  }],
  "PostToolUse": [{
    "matcher": "",
    "hooks": [{
      "type": "command",
      "command": "overstory log tool-complete --agent $OVERSTORY_AGENT_NAME --tool $TOOL_NAME"
    }]
  }],
  "Stop": [{
    "type": "command",
    "command": "overstory log session-end --agent $OVERSTORY_AGENT_NAME"
  }],
  "PreCompact": [{
    "type": "command",
    "command": "overstory prime --agent $OVERSTORY_AGENT_NAME --compact"
  }]
}
```

The `overstory hooks install` command deploys this config to `.claude/settings.local.json` in each worktree, customized per agent capability (e.g., read-only agents get PreToolUse blocks on Write/Edit).

---

## Open Questions

- **Session cognitive limits:** At what agent count does session-as-orchestrator become untenable? 15? 20? Is the ceiling fixed or practitioner-dependent?
- **Merge queue throughput:** Can 4-tier resolution handle 20+ concurrent agents producing rapid changes? What's the merge queue bottleneck?
- **SQLite WAL concurrency:** How many concurrent agents can safely poll `.overstory/mail.db` before lock contention degrades performance?
- **Orchestrator session crash recovery:** What's the maximum acceptable resume time after orchestrator session terminates unexpectedly?
- **Two-layer definition evolution:** As agent capabilities expand, do base definitions grow unwieldy? When should base definitions split into specialized variants?
- **Hook enforcement limits:** What operations require enforcement beyond PreToolUse blocks (e.g., Bash command filtering)?
- **Cross-project coordination:** How does Overstory scale to multi-repository work (convoy-style tracking)?
- **Supervisor agent effectiveness:** Do depth-1 supervisors meaningfully reduce orchestrator cognitive load, or do they just add indirection?
- **Zero-dependency sustainability:** As Overstory matures, will feature pressure force adoption of external dependencies (breaking the zero-dependency stance)?

---

## Sources

### Primary Sources
- **Overstory Repository** — github.com/jayminwest/overstory (MIT licensed, TypeScript/Bun, 31K LOC, 912 tests)
- **Overstory Implementation Blueprint** — blueprints/overstory-implementation-plan.md (1,201 lines of architectural documentation)
- **Overstory README** — /Users/jayminwest/Projects/overstory/README.md (comprehensive CLI reference)

### Analysis and Commentary
- **Gas Town Case Study** — appendices/examples/gastown/_index.md (comparative analysis of daemon-based orchestration)
- **Production Multi-Agent Systems** — chapters/6-patterns/11-production-multi-agent-systems.md (patterns validated by both Overstory and Gas Town)

---

## Connections

- **To [Orchestrator Pattern](../../../chapters/6-patterns/3-orchestrator-pattern.md):** Session-as-orchestrator demonstrates that the coordinator need not be a separate process. Leveraging an existing conversational interface (the practitioner's Claude Code session) reduces infrastructure overhead while introducing different failure modes (orchestrator crash stops coordination).

- **To [Production Multi-Agent Systems](../../../chapters/6-patterns/11-production-multi-agent-systems.md):** Overstory validates the same six production patterns (persistent identity, watchdog chains, mail coordination, self-cleaning workers, convoy tracking, merge queue) through session-based coordination and TypeScript/Bun implementation. The architectural convergence with Gas Town (daemon-based Go) suggests these patterns are language-agnostic and coordination-model-agnostic.

- **To [Operating Agent Swarms](../../../chapters/7-practices/7-operating-agent-swarms.md):** Session-based coordination changes the practitioner's daily rhythm. The orchestrator is the active session—coordination state lives in the practitioner's context window, not an external daemon's memory. This creates different cognitive load patterns and different failure modes.

- **To [Execution Topologies](../../../chapters/8-mental-models/5-execution-topologies.md):** Overstory's hierarchical delegation (coordinator → supervisor/lead → workers) maps to nested topology with explicit depth limits (default 2 levels). The depth parameter prevents runaway spawning—a practical constraint on nested topology that other implementations often leave unbounded.

- **To [Multi-Agent Workspace Managers](../../../chapters/9-practitioner-toolkit/5-multi-agent-workspace-managers.md):** Overstory represents the TypeScript/Bun alternative to Gas Town's Go implementation. The convergence of patterns (worktree isolation, typed messaging, tiered supervision, merge queues) across different technology stacks validates that workspace management patterns transcend language ecosystems.

- **To [Multi-Agent Landscape](../../../chapters/6-patterns/10-multi-agent-landscape.md):** Overstory's session-as-orchestrator model represents a distinct coordination architecture compared to daemon-based (Gas Town), SDK-orchestrated (LangGraph), and model-native (Claude Code Agent Teams) approaches. The model provides evidence that orchestration infrastructure choices offer meaningful trade-offs rather than strict superiority hierarchies.
