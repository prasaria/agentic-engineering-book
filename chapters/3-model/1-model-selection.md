---
title: Model Selection
description: How to choose the right model for agentic tasks
created: 2025-12-09
last_updated: 2025-12-10
tags: [models, selection, frontier, cost]
part: 1
part_title: Foundations
chapter: 3
section: 1
order: 1.3.1
---

# Model Selection

Choosing the right model is simpler than it seems: default to frontier, downgrade only with evidence.

---

## Default to Frontier

For nearly every task, reach for the SOTA class of models. Currently (December 2025) that's Anthropic's Opus 4.5 for coding tasks.

Maximizing compute is the goal—frontier models consistently outperform smaller alternatives in reasoning depth, tool use, and complex instruction-following.

The gap between different labs' SOTA models (Gemini 3 Pro vs. Opus 4.5, for instance) has shrunk significantly over the past six months.

But frontier vs. non-frontier still matters enormously.

**When in doubt, use a frontier model.** Frontier should be your default. Only downgrade when there's evidence or clear logical reasoning to do so.

---

## What Capabilities Actually Matter

**Reasoning and tool use are the most important.**

Extended thinking and step-by-step reasoning directly address multi-step planning requirements. Instruction-following is important but is more of a prompting concern than a model selection concern—it's better framed as "how can I set up instructions so that any SOTA LLM can follow them?"

---

## When to Downgrade

Use smaller, faster models for specific task types where they excel:

- **Scouting agents**: Haiku 4.5 works well for investigative tasks—reading content quickly and distilling insights. These aren't computationally intensive tasks, so the speed/cost tradeoff makes sense.
- **Simple retrieval or filtering**: When the task is more about finding than reasoning.

Reliability compounds across a system—small model failures cascade through multi-step workflows. Don't mistake cost savings for optimization.

### Small Models Are RAG

*[2025-12-09]*: Small models function as RAG systems when embedded in an orchestrator pattern.

```
USER/trigger → Orchestrator → Delegation → retrieval-agent (Haiku, natural_language_query)
```

**Context Staging** for the retrieval agent:

| Component | Token Type |
|-----------|------------|
| `base.cc/` | Agent tokens (Claude Code base config) |
| `project_prompt` | Agent tokens |
| `tool_info` | Tool input tokens |
| `tool.call (query)` | Tool input tokens |
| `tool.result` | prompt/sys.info |
| `distillation synthesis` | prompt/sys.info |

The pattern: keep the small model's context minimal (base config, project prompt, tool info, query), let it retrieve and distill, then return results to the orchestrator for synthesis.

This explains why Haiku excels at scouting—it's not doing heavy reasoning, it's doing targeted retrieval with lightweight synthesis. The orchestrator handles the complex reasoning; the small model handles the fast, focused lookup.

**See Also**:
- [Orchestrator Pattern: Capability Minimization](../6-patterns/3-orchestrator-pattern.md#capability-minimization) — How tool restriction complements model selection
- [Context: Context Loading vs. Accumulation](../4-context/_index.md#context-loading-vs-context-accumulation) — The "payload" mental model that makes small models work
- [Context Loading Demo](../../appendices/examples/context-loading-demo/README.md) — Demonstrates Haiku as retrieval agent with minimal context payloads (~800 tokens)

---

## Capability vs. Latency vs. Cost

**Capability is most important.**

You should only downgrade from frontier models if you absolutely need to—and that's usually a cost-driven decision. Frontier models are significantly more expensive, but they're expensive for a reason.

Latency matters most in multi-agent architectures: a single orchestrator running a frontier model can coordinate several subagents that gather and synthesize information across domains. The orchestrator needs to be smart; the scouts can be fast.

---

## The Decision Framework

```
┌─────────────────────────────────────────────────────────┐
│                   Model Selection                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Start with frontier model (Opus 4.5, etc.)          │
│                         │                                │
│                         ▼                                │
│  2. Is the task working reliably?                       │
│         │                    │                           │
│        YES                   NO                          │
│         │                    │                           │
│         ▼                    ▼                           │
│  3. Is cost a problem?    Debug prompt/context first    │
│         │                                                │
│        YES                                               │
│         │                                                │
│         ▼                                                │
│  4. Test with smaller model                             │
│         │                                                │
│         ▼                                                │
│  5. Does it still work reliably?                        │
│         │                    │                           │
│        YES                   NO                          │
│         │                    │                           │
│         ▼                    ▼                           │
│     Use smaller         Stay with frontier              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

The key insight: you should only consider downgrading *after* you have a working solution with a frontier model. Optimizing cost before validating capability is premature optimization.
