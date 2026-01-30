---
title: "KotaDB Case Study: Patterns in Production"
description: Analysis of how the KotaDB project implements patterns from Part 2 Craft
created: 2026-01-30
last_updated: 2026-01-30
tags: [case-study, kotadb, patterns, production]
part: 4
part_title: Appendices
chapter: 10
section: 1
order: 4.10.1
---

# KotaDB Case Study: Patterns in Production

A comprehensive analysis of how the KotaDB project implements patterns from Part 2: Craft of the Agentic Engineering Knowledge Base.

---

## Project Overview

**KotaDB** is an HTTP API service for code indexing built with Bun, TypeScript, and Supabase. The project's `.claude/` directory represents a mature implementation of agentic engineering patterns, with 90+ slash commands, 4 specialized agents, and a 7-domain expert system.

**Scale:**
- 4 core agents (scout, build, review, orchestrator)
- 7 domain experts with plan/review/improve commands each
- 90+ slash commands organized across 12 subdirectories
- Machine-readable agent registry with capability/model indexes

---

## Patterns Implemented

### 1. Orchestrator Pattern (Ch. 6.3)

**Implementation:** `orchestrator-agent.md` + `orchestrator.md` command

The KotaDB orchestrator demonstrates the core orchestrator pattern with a five-phase workflow:

| Phase | Agent | Purpose | Model | Output |
|-------|-------|---------|-------|--------|
| Scout | scout-agent | Read-only exploration | haiku | In-memory findings |
| Plan | planning-council | Multi-expert analysis | sonnet | `docs/specs/<name>.md` |
| Build | build-agent (1-N) | Implementation | sonnet | Code changes |
| Review | review-panel | Multi-expert review | sonnet | `docs/reviews/<name>-review.md` |
| Validate | Bash | Tests, lint, typecheck | n/a | Console output |

**Key Mechanisms Demonstrated:**

**Single-Message Parallelism** (from `orchestrator.md` lines 91-103):
```markdown
For **parallel builds** (independent files):
  Use Task tool (multiple calls in SINGLE message):
    subagent_type: "build-agent"
    prompt: "{file_1_implementation_prompt}"

    subagent_type: "build-agent"
    prompt: "{file_2_implementation_prompt}"
```

This directly implements the book's critical insight: "All parallel agents must be invoked in one message for true concurrency."

**Spec File as Shared Context** (from `orchestrator.md` lines 62-67):
- Scout outputs exploration findings
- Plan creates `docs/specs/<name>.md`
- Build agents read spec file
- Review agents reference spec for compliance

**Phase Gating** (from `orchestrator.md` lines 108-121):
```markdown
**Prerequisite Check:**
Before executing build, verify spec file exists:
  test -f {spec_file_path} || echo "ERROR: Spec file missing"
```

**Connection to Book:** Ch. 6.3 states "If a prerequisite fails, halt and provide remediation instructions." KotaDB implements this with structured error messages and resume commands.

---

### 2. Self-Improving Expert Commands (Ch. 6.2)

**Implementation:** `experts/` directory with 7 domain experts

Each expert follows the three-command pattern documented in Ch. 6.2:

```
.claude/commands/experts/
├── architecture-expert/
│   ├── architecture_expert_plan.md    # Has ## Expertise section
│   ├── architecture_expert_review.md  # Has ## Expertise section
│   └── architecture_expert_improve.md # Updates Expertise sections
├── testing-expert/
├── security-expert/
├── integration-expert/
├── ux-expert/
├── cc_hook_expert/
└── claude-config/
```

**Expertise Section Evolution:**

The architecture expert's plan command (lines 25-145) contains evolved expertise including:

```markdown
**Anti-Patterns Discovered:**
- Relative imports instead of path aliases (causes refactoring brittleness)
- Direct `console.*` usage (violates logging standards) — Use `@logging/logger`
- Unbounded database queries without pagination (discovered in #473)
- Missing error telemetry in try-catch blocks (discovered in ed4c4f9)
```

Each anti-pattern includes:
- What the anti-pattern is
- Why it's problematic
- Better alternative
- Evidence from git history (PR/commit references)

**The Improve Command** (`architecture_expert_improve.md`):

```markdown
### 1. Analyze Recent Changes
git log --oneline -30 --all -- "app/src/**"

### 3. Update Expertise Sections
**Rules for Updates:**
- **PRESERVE** existing patterns unless confirmed obsolete
- **APPEND** new learnings with evidence from commit history
- **DATE** new entries with commit reference (e.g., "Added after #123")
- **REMOVE** only patterns contradicted by multiple recent implementations
```

This directly mirrors Ch. 6.2's conservative update rules:
- PRESERVE patterns still relevant
- APPEND new learnings with timestamps
- DATE entries with `*[YYYY-MM-DD]*:`
- REMOVE only with clear evidence

**Connection to Book:** Ch. 6.2 emphasizes "Git History as Learning Signal." KotaDB demonstrates this through PR references in expertise sections and the improve command's git analysis workflow.

---

### 3. Plan-Build-Review Pattern (Ch. 6.1)

**Implementation:** Workflow commands in `workflows/` directory

The `/plan` command (lines 5-120) creates specification artifacts:

```markdown
## Plan Document Structure

# Implementation Plan: {task_title}

**ADW ID**: {adw_id}
**Created**: {ISO timestamp}

## Current State
Description of the current codebase state...

## Proposed Changes
### 1. {Component/File Name}
- **Action**: create/modify/delete
- **Location**: src/path/to/file.ts
- **Rationale**: Why this change is needed

## Validation Requirements
- Level 1: lint, typecheck
- Level 2: Level 1 + integration tests
- Level 3: Level 2 + all tests + build
```

**Spec File Quality Requirements** match Ch. 6.1's guidance on "Research as Artifact Generation":
- Concrete file paths and line numbers
- Explicit constraints and dependencies
- Validation commands specified upfront

**Connection to Book:** Ch. 6.1 states "The output of research isn't just understanding—it's concise summary documents." KotaDB's plan command generates these artifacts with the exact structure recommended.

---

### 4. Capability Minimization (Ch. 6.3)

**Implementation:** Agent definitions with restricted tool sets

The agent-registry.json provides a clear tool matrix:

| Agent | Tools | Read-Only |
|-------|-------|-----------|
| scout-agent | Glob, Grep, Read, MCP search | Yes |
| build-agent | Glob, Grep, Read, Edit, Write, Bash, MCP | No |
| review-agent | Glob, Grep, Read, MCP, WebFetch | Yes |
| orchestrator-agent | Task, SlashCommand, Read, Glob, Grep | Yes |

**Key Observation:** The orchestrator has NO write access (Edit, Write, Bash are excluded). This implements the book's principle: "Default to 'message' instead of 'broadcast'... Orchestrators shouldn't do the heavy lifting."

**From scout-agent.md:**
```markdown
constraints:
  - No file modifications allowed
  - No shell command execution
  - Report findings without making changes
```

**From orchestrator-agent.md:**
```markdown
constraints:
  - No direct file modifications (delegate to build-agent)
  - Coordinate agents without duplicating their work
```

**Connection to Book:** Ch. 6.3 states "Tool restriction isn't just about limiting what agents can do—it's about enabling coordination patterns through deliberate capability differentiation."

---

### 5. Context Isolation via Sub-Agents (Ch. 6.3)

**Implementation:** Model tier assignment for context management

From agent-registry.json's modelIndex:
```json
"modelIndex": {
  "haiku": ["scout-agent", "review-agent"],
  "sonnet": ["build-agent"],
  "opus": ["orchestrator-agent"]
}
```

**Design Rationale:**
- **Scout/Review (haiku)**: Fast, cheap, read-only exploration. Fresh context windows for each search/analysis task.
- **Build (sonnet)**: Balanced capability for implementation. Context contains spec + target file patterns.
- **Orchestrator (opus)**: Complex coordination decisions. Clean context for synthesis.

This implements Ch. 6.3's insight: "Sub-agents are expensive, disposable context buffers. They absorb the noise so the orchestrator can think clearly."

---

### 6. Parallel Expert Councils (Ch. 6.3)

**Implementation:** `planning_council.md` and `review_panel.md`

**Planning Council Workflow:**
```markdown
### Phase 1: Expert Invocation
Invoke all domain experts in parallel:
  /experts:architecture-expert:architecture_expert_plan <CONTEXT>
  /experts:testing-expert:testing_expert_plan <CONTEXT>
  /experts:security-expert:security_expert_plan <CONTEXT>
  /experts:integration-expert:integration_expert_plan <CONTEXT>
  /experts:ux-expert:ux_expert_plan <CONTEXT>
  /experts:cc_hook_expert:cc_hook_expert_plan <CONTEXT>
  /experts:claude-config:claude_config_plan <CONTEXT>
```

**Critical Implementation Detail** (from `planning_council.md`):
```markdown
**Expert Invocation Strategy (added after #490):**
- Invoke ALL 7 experts in a single message for true parallelism
- Use Task tool with model: haiku for cost efficiency
- Handle partial failures gracefully
```

**Review Panel Aggregation Rules:**
```markdown
**Aggregate Decision Rules:**
| Condition | Panel Status |
|-----------|--------------|
| Any expert returns CHANGES_REQUESTED | CHANGES_REQUESTED |
| All experts return APPROVE | APPROVE |
| Mix of APPROVE and COMMENT | COMMENT |
```

**Connection to Book:** Ch. 6.3 describes "Expert Synthesis" where the orchestrator collects structured outputs, identifies cross-cutting concerns, and synthesizes unified recommendations. KotaDB's councils demonstrate this exact pattern.

---

## Anti-Patterns Avoided

KotaDB's implementation explicitly addresses anti-patterns documented in the book:

### From Ch. 6.3 (Orchestrator Pattern):

**Anti-Pattern:** "Missing spec path validation"
**KotaDB Solution:** `test -f {spec_file_path}` before build phase with structured error messages

**Anti-Pattern:** "Implicit environment assumptions"
**KotaDB Solution:** Environment detection in validate phase:
```bash
if [ -f .parity-status.json ] && pnpm parity:status ...; then
  VALIDATION_CMD="pnpm parity:validate"
else
  VALIDATION_CMD="pnpm validate:full"
fi
```

### From Ch. 6.2 (Self-Improving Experts):

**Anti-Pattern:** "Updating Workflow Sections"
**KotaDB Solution:** Improve commands explicitly target only Expertise sections

**Anti-Pattern:** "Not Dating New Expertise Entries"
**KotaDB Solution:** All expertise updates include `(added after #PR)` or `(discovered in commit)` references

---

## Template Categories and Output Discipline

KotaDB implements a classification system for command outputs:

| Category | Description | Output Format | Sentinel |
|----------|-------------|---------------|----------|
| Message-Only | Single text response | Single line | `0` |
| Path Resolution | Returns file path | Absolute path | `0` |
| Action | Performs operations | Structured report | Exit code |
| Structured Data | Machine-parseable | JSON | Empty object |

**Meta-Commentary Forbidden Patterns:**
```markdown
- "Based on the changes..."
- "The commit should..."
- "Here is the..."
- "I can see that..."
```

This discipline ensures agents produce parseable, actionable outputs rather than conversational responses.

**Connection to Book:** While not explicitly documented as a pattern, this approach implements the principle of **explicit contracts between agents**—each agent knows exactly what format to expect from others.

---

## Machine-Readable Coordination

**Implementation:** `agent-registry.json`

The registry provides three indexes for programmatic agent discovery:

```json
{
  "capabilityIndex": {
    "explore": ["scout-agent"],
    "implement": ["build-agent"],
    "review": ["review-agent"],
    "orchestrate": ["orchestrator-agent"]
  },
  "modelIndex": {
    "haiku": ["scout-agent", "review-agent"],
    "sonnet": ["build-agent"],
    "opus": ["orchestrator-agent"]
  },
  "toolMatrix": {
    "Edit": ["build-agent"],
    "Write": ["build-agent"],
    "Task": ["scout-agent", "build-agent", "review-agent", "orchestrator-agent"]
  }
}
```

**Use Cases:**
- **Capability routing**: "Find an agent that can 'implement'" → build-agent
- **Cost optimization**: "Use cheapest agent for read-only task" → haiku tier → scout-agent
- **Tool audit**: "Which agents have write access?" → toolMatrix["Edit"] → build-agent

This enables **dynamic agent selection** rather than hardcoded routing—a pattern that scales as agent inventories grow.

---

## Connections to Book Chapters

| KotaDB Component | Primary Pattern | Book Reference |
|------------------|-----------------|----------------|
| orchestrator-agent.md | Orchestrator Pattern | Ch. 6.3 |
| orchestrator.md (command) | Phase-gated workflows | Ch. 6.3 |
| planning_council.md | Parallel expert synthesis | Ch. 6.3 |
| review_panel.md | Aggregated review decisions | Ch. 6.3 |
| *_improve.md commands | Self-improving experts | Ch. 6.2 |
| Expertise sections | Mutable vs stable separation | Ch. 6.2 |
| plan.md → implement.md | Plan-Build-Review | Ch. 6.1 |
| docs/specs/*.md | Spec file as artifact | Ch. 6.1 |
| Agent tool restrictions | Capability minimization | Ch. 6.3 |
| Model tier assignment | Context isolation | Ch. 6.3, Ch. 4 |
| agent-registry.json | Machine-readable coordination | Ch. 6.3 |

---

## Key Takeaways

1. **Orchestration is coordination, not execution.** KotaDB's orchestrator has no write access—it spawns, sequences, and synthesizes.

2. **Spec files are contracts.** The `docs/specs/` artifacts flow through all phases, enabling phase gating and agent handoffs.

3. **Self-improvement requires discipline.** The improve commands follow strict PRESERVE/APPEND/DATE/REMOVE rules to prevent expertise drift.

4. **Parallel invocation is a message-level concern.** All 7 experts invoke in a single message for true parallelism.

5. **Tool restrictions force patterns.** Read-only scouts must report findings; write-capable builders must implement.

6. **Model tiers match cognitive load.** Haiku for exploration, Sonnet for implementation, Opus for orchestration.

7. **Machine-readable registries scale.** The capability/model/tool indexes enable dynamic routing as the agent inventory grows.

---

## References

**Book Patterns:**
- [Ch. 6.1: Plan-Build-Review](../../../chapters/6-patterns/1-plan-build-review.md)
- [Ch. 6.2: Self-Improving Experts](../../../chapters/6-patterns/2-self-improving-experts.md)
- [Ch. 6.3: Orchestrator Pattern](../../../chapters/6-patterns/3-orchestrator-pattern.md)

**KotaDB Implementation:**
- [Agent Registry](./kotadb/.claude/agents/agent-registry.json)
- [Orchestrator Agent](./kotadb/.claude/agents/orchestrator-agent.md)
- [Orchestrator Command](./kotadb/.claude/commands/experts/orchestrators/orchestrator.md)
- [Architecture Expert Plan](./kotadb/.claude/commands/experts/architecture-expert/architecture_expert_plan.md)
