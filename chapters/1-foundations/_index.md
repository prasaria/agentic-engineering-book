---
title: Foundations
description: The core four pillars of agentic systems - prompt, model, context, and tooling
created: 2025-12-08
last_updated: 2025-12-10
tags: [foundations, core-concepts]
part: 1
part_title: Foundations
chapter: 1
section: 0
order: 1.1.0
---

# Foundations

Everything in agentic engineering flows from four interconnected pillars:

| Pillar | Core Question |
|--------|---------------|
| [Prompt](../2-prompt/_index.md) | How to instruct the agent? |
| [Model](../3-model/_index.md) | What capabilities does the system provide? |
| [Context](../4-context/_index.md) | What information does the agent access? |
| [Tool Use](../5-tool-use/_index.md) | What actions can the agent take? |

This framing is adopted from [agenticengineer.com](https://agenticengineer.com)'s "core four." For a more granular hierarchy of intervention points, see the [Twelve Leverage Points](1-twelve-leverage-points.md)—a framework that expands beyond the core four into architecture, workflows, and system-level concerns.

---

## The Pillars in Plain Language

Explaining agentic engineering in 60 seconds:

- **Model**: The "brain" of the operation. Different models have varying levels of capability and intelligence.
- **Context**: The "active memory"—what the agent has seen and can access during a session.
- **Tools**: How agents take action. Reading and writing files, conducting web research, spawning subagents.
- **Prompt**: The trigger that initiates model action. The interface between user (or system) and agent.

---

## How the Pillars Interact

The pillars are deeply interdependent:

```
┌─────────────────────────────────────────┐
│                                         │
│   ┌─────────┐         ┌─────────┐       │
│   │ Prompt  │◄───────►│ Context │       │
│   └────┬────┘         └────┬────┘       │
│        │                   │            │
│        ▼                   ▼            │
│   ┌─────────┐         ┌─────────┐       │
│   │  Model  │◄───────►│ Tooling │       │
│   └─────────┘         └─────────┘       │
│                                         │
└─────────────────────────────────────────┘
```

- **Context fills as tools grow**—tool outputs consume context window space
- **Context is treated differently by different models**—each model has its own strengths and quirks
- **Certain models are better at tool calling**—capability varies significantly
- **Prompting impacts how models react to their context and tools**—a prompt can intentionally disregard sections of context or available tools

When one pillar changes, it ripples to the others:
- **Downgrade the model** → massive performance impacts across the board
- **Add more tools** → risk flooding the context window if not handled properly
- **Alter context** → changes model behavior for that entire session, including tool usage
- **Change the prompt** → can steer or override how the model interprets context and uses tools

---

## Is There a Hierarchy?

*[2025-12-10]*: Until mid-2025, **model** sat at the top. The gap between state-of-the-art (SOTA) and other models was so large that model choice dominated outcomes.

*[2025-12-10]*: The frontier narrowed through 2024. Claude 3.5 Sonnet (June 2024), Gemini 1.5 Pro, and GPT-4o compressed capability gaps. Differences between frontier models became less deterministic of outcomes. The other pillars now carry more weight:

- **Tool use** is essential to any workflow that needs to take action. A model without tools produces analysis but cannot execute workflows.
- **Context** alters the entire behavior of a model during a session.
- **Prompting** determines the direction of the context window and model behavior.

*[2025-12-10]*: Practical observation from production deployments: SOTA models provide superior outcomes across most tasks. The cost premium pays for itself through reduced iteration cycles and higher first-attempt success rates.

---

## How the Framework Has Evolved

*[2025-12-10]*: Early LLMs (pre-2023) lacked tool use capabilities. GPT-3.5's function calling (June 2023) marked the transition to agentic systems. Claude 3 Opus demonstrated extended context windows (March 2024, 200k tokens). Each capability expansion required reevaluation of what agents could accomplish.

*[2025-12-10]*: Current SOTA models (Claude 3.5 Sonnet, GPT-4o, Gemini 1.5 Pro) demonstrate capability across most coding tasks. Observable limitations center on context window constraints and tool availability rather than model intelligence.

---

## Common Mistakes

*[2025-12-10]*: Observed patterns from new practitioners in agentic engineering:

1. **Organization of information**—poor structure kills agent effectiveness. Unstructured context causes models to miss critical information.
2. **Excessive trust in model outputs**—skipping verification leads to compounding errors in multi-step workflows.
3. **Flooding context with unrelated tools**—unfocused agents waste tokens evaluating irrelevant options.
4. **Using ad-hoc prompts with passive language**—vague instructions produce vague results.
5. **Neglecting structure** in prompts, context, and tool responses—models perform better with consistent formatting.
6. **Allowing too much freedom**—agents need constraints to succeed. Unbounded option spaces lead to analysis paralysis.
7. **Insufficient instruction detail**—relying too heavily on agent discovery increases failure rates.
8. **Failing to adhere to the [pit of success](../8-mental-models/1-pit-of-success.md) mindset**—making correct actions harder than incorrect ones.

*[2025-12-10]*: Counter-intuitive finding: "more" does not equal better capability. More tools, more context, and more steering prompts degrade performance. **A focused agent is a productive agent.**

---

## Limits of the Framework

What this framework doesn't capture well:

- **"Prompting" is too general.** It could mean sending ad-hoc "build me a website" prompts, or 2,500-line spec files that do cutting-edge engineering work. This distinction can be murky.

When the four-pillar lens has led astray:

- The misconception that "more is better"—more tools, more context, more steering prompts. This floods agents and degrades performance.

---

## Connections

- **To [Prompt](../2-prompt/_index.md):** Prompts serve as the primary interface for instructing agents. Prompt design determines how effectively agents can parse instructions and structure their outputs. Poor prompt structure undermines gains from better models or tools.

- **To [Model](../3-model/_index.md):** Model selection defines the ceiling of agent capability. Different models excel at different tasks—tool calling, reasoning, code generation. Understanding model characteristics allows matching capability to task requirements.

- **To [Context](../4-context/_index.md):** Context management determines what information agents can access during execution. Context window constraints force tradeoffs between comprehensiveness and focus. Effective context strategies prevent information loss while avoiding token waste.

- **To [Tool Use](../5-tool-use/_index.md):** Tools translate agent intelligence into action. Well-designed tools provide clear interfaces and reliable outputs. Tool selection and restriction patterns shape what agents can accomplish and how efficiently they work.
