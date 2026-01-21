---
title: Twelve Leverage Points of Agentic Coding
description: A hierarchy of intervention points for improving agentic systems, from low to high leverage
created: 2025-12-08
last_updated: 2025-12-10
tags: [foundations, leverage-points, framework, agenticengineer]
source: https://agenticengineer.com
part: 1
part_title: Foundations
chapter: 1
section: 1
order: 1.1.1
---

# Twelve Leverage Points of Agentic Coding

A framework for understanding where to intervene in agentic systems. The hierarchy follows Donella Meadows' "Places to Intervene in a System" pattern—lower numbers indicate higher leverage points that affect the entire system. Changes at the top (#1-#4) cascade throughout the system; changes at the bottom (#9-#12) produce local fixes.

> **Guiding philosophy:** "One agent, one purpose, one prompt."

---

## The Hierarchy

AI Developer Workflows (ADWs) define how work flows between agents in multi-agent systems—the highest leverage intervention point in the framework.

| # | Leverage Point | Core Question |
|---|----------------|---------------|
| 12 | [Context](#12-context) | What does the agent actually know? |
| 11 | [Model](#11-model) | What tradeoffs exist: cost, speed, intelligence? |
| 10 | [Prompt](#10-prompt) | Are instructions concrete and followable? |
| 9 | [Tools](#9-tools) | What actions can agents take, and in what form? |
| 8 | [Standard Out](#8-standard-out) | Can agents and operators see what's happening? |
| 7 | [Types](#7-types) | Is typing consistent and enforced? |
| 6 | [Documentation](#6-documentation) | Can agents navigate and trust the documentation? |
| 5 | [Tests](#5-tests) | Are tests helping agents or just theatre? |
| 4 | [Architecture](#4-architecture) | Is the codebase agentically intuitive? |
| 3 | [Plans](#3-plans) | Can agents complete tasks without further input? |
| 2 | [Templates](#2-templates) | Do agents know what good output looks like? |
| 1 | [ADWs](#1-adws-ai-developer-workflows) | How does work flow between agents? |

---

## Low Leverage (Local Fixes)

### 12. Context

What does the agent actually know? What's in the context window? Is it all necessary? Will the current context increase the likelihood of outputting the next token correctly?

**Key considerations:**
- How to audit what's actually in an agent's context at decision time
- The cost of irrelevant context and methods to measure it
- How to distinguish "necessary" context from "nice to have" information
- Processes for pruning context that isn't contributing to outcomes

**Example: Good vs. Poor Context Management**

Poor: Loading entire documentation suite into context for every task (500k+ tokens, most irrelevant).

Good: Loading only the relevant module documentation based on task requirements (15k tokens, high signal-to-noise ratio).

---

### 11. Model

What model is the system using? How capable is it? What tradeoffs exist? Cost vs speed vs intelligence.

**Key considerations:**
- How to map tasks to the right model tier
- Identifying cases where over-indexing on capability wastes resources
- Staying current on model capabilities without constant churn

**Example: Good vs. Poor Model Selection**

Poor: Using GPT-4o for simple text extraction tasks that GPT-3.5-turbo handles perfectly (10x cost overhead).

Good: Using Claude 3.5 Sonnet for complex code generation, GPT-3.5-turbo for text classification (matched capability to task requirements).

---

### 10. Prompt

What instructions does the agent have? Are they concrete? Can they be followed properly?

**Key considerations:**
- What makes a prompt "concrete" vs. "vague"
- How to test whether a prompt can actually be followed
- Setting quality bars for prompts before looking elsewhere for the problem

**Example: Good vs. Poor Prompting**

Poor: "Make this code better" (vague, no success criteria).

Good: "Refactor the authentication module to use dependency injection. Extract the token validation logic into a separate class. Maintain existing test coverage." (concrete, testable, clear success criteria).

---

### 9. Tools

What actions can agents take? What form are these tools available in? Internal tooling vs MCP vs CLI vs something else.

**Key considerations:**
- How to decide between internal tools, MCP servers, and CLI wrappers
- The tradeoff between tool flexibility and tool reliability
- When tool limitations become the bottleneck

---

## Medium Leverage (System Properties)

### 8. Standard Out

Can agents (and operators) actually SEE what the code is doing? Is it being output centrally? Is it self-documenting? Do logs have clear sources and descriptions?

**Key considerations:**
- How observable agent systems are
- What information is missing from current visibility
- How to balance verbose logging with signal-to-noise ratio
- What "self-documenting" output looks like in practice

---

### 7. Types

Is the codebase typing consistent? Are agents aware of it? To what extent is it being policed and are the agents informed if/when they make infractions?

**Key considerations:**
- How strong typing helps agents write correct code
- How to surface type errors to agents in actionable ways
- The relationship between type coverage and agent success rate

---

### 6. Documentation

Where is the documentation? What's in there? Can agents easily navigate? Is it out of date? Is it being updated constantly? Is it "self-improving"?

**Key considerations:**
- What makes documentation "agent-navigable"
- How to keep docs in sync with code when agents are making changes
- What "self-improving" documentation looks like in practice
- Where agents look for documentation, and whether that's where it lives

---

### 5. Tests

What are the tests doing and how do they help agents? Are agents conducting "testing theatre"? Is testing using mock implementations or running against actual code?

**Key considerations:**
- The difference between tests that help agents and tests that don't
- How to detect "testing theatre" (tests that pass but don't verify anything real)
- When mocks help and when they hide problems
- How test failures guide agent behavior

---

## High Leverage (Structural Changes)

### 4. Architecture

What patterns does the codebase follow? How is it structured? Is it "agentically-intuitive"—following historically-popular structures with higher likelihood of existing in training data?

**Key considerations:**
- What makes an architecture "agentically intuitive"
- How to balance "what's in training data" with "what's right for the problem"
- What architectural patterns agents handle well vs. poorly
- How much codebase structure affects agent success

---

### 3. Plans

Plans are MASSIVE prompts passed to an agent with the expectation that no more user interaction must happen in that session for the agent to finish its task.

**Key considerations:**
- What makes a plan "complete enough" to run without human intervention
- How to scope a plan—what's too big, what's too small
- How to handle plans that fail partway through
- The relationship between plan quality and task success
- How to write plans that are robust to unexpected situations

---

### 2. Templates

Do agents know what docs, code, prompts, etc. should look like? Are prompts/plans reusable? Are templates structured consistently? Are all elements necessary?

**Key considerations:**
- What templates get used most frequently
- How to decide what goes in a template vs. what's generated fresh
- How to prevent templates from becoming bloated over time
- The relationship between template quality and output consistency

---

### 1. ADWs (AI Developer Workflows)

How does work carry between agents? How are multiple agents working together to accomplish a shared goal? To what extent are ADWs deterministic (based in code) vs. stochastic/agentic (using orchestrator agent, agents can invoke other agents, etc.)?

**Key considerations:**
- What ADWs have been built or used, and what worked
- How to decide between deterministic workflows and agentic orchestration
- The handoff problem between agents and how to solve it
- When multi-agent coordination helps vs. adds unnecessary complexity
- How to debug workflows that span multiple agents

---

## Connections

- **To [Core Four](_index.md):** The twelve leverage points expand on the four pillars. Context (#12), Model (#11), Prompt (#10), and Tools (#9) map directly to the core four. The higher leverage points (Plans, Templates, ADWs) represent system-level patterns built on top of the pillars.

- **To [Evaluation](../7-practices/2-evaluation.md):** Each leverage point requires different evaluation approaches. Low leverage points (context, model, prompt) can be evaluated per-task. High leverage points (architecture, templates, ADWs) require system-level metrics across multiple tasks.

- **To [Patterns](../6-patterns/_index.md):** ADWs (#1) and Plans (#3) directly correspond to the orchestrator and plan-build-review patterns. Templates (#2) enable self-improving expert patterns.

---

## Notes on the Source

This framework comes from [agenticengineer.com](https://agenticengineer.com). The hierarchy draws from Donella Meadows' "Leverage Points: Places to Intervene in a System" (1999), applying systems thinking to agentic engineering.


