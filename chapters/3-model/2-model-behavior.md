---
title: Model Behavior
description: How models behave in agentic contexts—variance, consistency, temperature effects, and behavioral patterns that affect agent design
created: 2025-12-10
last_updated: 2025-12-10
tags: [model, behavior, temperature, consistency, agentic]
part: 1
part_title: Foundations
chapter: 3
section: 2
order: 1.3.2
---

# Model Behavior

Models are probabilistic systems, not deterministic functions. Understanding their behavioral patterns—variance, consistency, temperature effects, and learned tendencies—shapes how agents should be architected.

---

## Core Questions

### Behavioral Consistency
- Same prompt, different runs—how much variance appears in production?
- How does temperature affect reliability in multi-step workflows?
- What behavioral patterns remain consistent across model families?

### Model Characteristics
- What are "model behaviors" beyond raw capability metrics?
- How do learned patterns (verbosity, refusal, instruction-following) affect agent design?
- When do model-specific quirks matter for production systems?

### Extended Reasoning
- When should extended thinking modes be enabled?
- What trade-offs exist between reasoning depth and latency?
- How do thinking budgets affect output quality?

---

## Variance and Consistency

Models produce different outputs for identical inputs. This isn't a bug—it's inherent to sampling-based generation.

At temperature 0, most models approach near-deterministic behavior. "Near" matters: subtle variance remains even at zero temperature. For tasks requiring strict reproducibility (compliance logs, audit trails, contract generation), architectural solutions (templates, validators, post-processing) provide stronger guarantees than model settings alone.

### Temperature Effects on Reliability

*[2025-12-10]*: **Temperature compounds in multi-step workflows.** A single task at temperature 1.0 might succeed 95% of the time. Ten sequential tasks at the same temperature? Reliability degrades to approximately 60%.

The math: 0.95^10 ≈ 0.60. Small per-step error rates multiply across steps.

**Practical implications:**

| Temperature | Single-Step Success | 10-Step Success |
|-------------|---------------------|-----------------|
| 0.0 (near-deterministic) | ~99% | ~90% |
| 0.5 (moderate creativity) | ~97% | ~74% |
| 1.0 (high creativity) | ~95% | ~60% |

These numbers reflect observed patterns, not guaranteed bounds. The specific degradation depends on task complexity, prompt quality, and model capability.

**Design guidance:** For multi-agent orchestration or long workflows, default to temperature 0 unless creative variation provides measurable value. When higher temperature is required (brainstorming, creative writing), isolate those steps from reliability-critical paths.

### When Variance Helps

Not all variance is unwanted. For certain task types, probabilistic sampling creates value:

- **Brainstorming and ideation**: Higher temperature generates diverse options
- **Creative writing**: Natural variation in phrasing and structure
- **Exploration tasks**: Discovering multiple solution paths

The pattern: use variance when discovering possibilities, eliminate it when executing known workflows.

---

## Model Personality Patterns

Models exhibit learned behavioral tendencies. These aren't "personalities" in an anthropomorphic sense—they're statistical patterns in how models respond to inputs.

### Verbosity Defaults

Different models have different verbosity baselines. Claude tends toward longer, more explanatory responses. GPT skews terser. Gemini varies by version.

This affects prompt design. Instructions like "be concise" or "provide detailed explanations" have different effects depending on the model's natural baseline.

**Architectural pattern:** When switching models, audit output lengths. Adjust prompts to maintain consistent behavior, or accept the model's defaults if they fit task requirements.

### Refusal Patterns

Safety training creates refusal behaviors. Models decline requests that pattern-match against their safety training, even when the request is legitimate.

*[2025-12-10]*: **Refusal patterns vary by provider.** Claude tends to refuse cautiously (higher false-positive rate). GPT-4 is more permissive but still refuses edge cases. Gemini has evolved through versions, with different thresholds.

**Production impact:** Build fallback paths for expected refusals. If generating SQL for database administration tools, include explicit permissions in the prompt ("You are authorized to generate DDL statements for schema management"). If refusals persist, route to a different model or escalate to human review.

### Instruction-Following Reliability

Frontier models (Opus 4.5, GPT-4o, Gemini 2.0 Pro) follow complex instructions reliably. Mid-tier models (Sonnet, GPT-4 Turbo) handle structured instructions well but may skip subtle requirements. Smaller models (Haiku, GPT-3.5) work for simple, well-constrained instructions.

The gap: multi-constraint instructions ("Format as JSON, include only non-null fields, sort by timestamp descending") succeed consistently on frontier models but degrade on smaller ones.

**When downgrading matters:** Instruction-following reliability is more important than raw capability for many agent tasks. A smaller model that reliably follows output format requirements beats a larger model that occasionally ignores them.

---

## Extended Thinking Modes

Modern frontier models offer extended thinking capabilities—additional reasoning before generating final output.

### Claude Extended Thinking

*[2025-12-10]*: Claude's extended thinking uses a configurable token budget for internal reasoning. Key constraints:

- **Minimum budget**: 1,024 tokens
- **Temperature incompatibility**: Extended thinking requires temperature 0 (deterministic reasoning)
- **Latency trade-off**: Additional thinking time before output generation

Extended thinking helps most on tasks requiring multi-step reasoning, mathematical computation, or logical deduction. For simple retrieval or formatting tasks, it adds latency without meaningful benefit.

**Example use cases:**
- Complex planning tasks requiring dependency analysis
- Mathematical problem-solving
- Multi-constraint optimization
- Debugging complex errors with multiple potential causes

**Poor fit:**
- Simple CRUD operations
- Format transformations
- Information retrieval
- Tasks with tight latency requirements

### Gemini Thinking Mode

Gemini 2.0 includes thinking capabilities similar to Claude's extended thinking. The model performs internal reasoning before generating output.

Gemini's approach differs in configuration: thinking mode is a boolean flag rather than a token budget. This simplifies enablement but provides less control over reasoning depth.

### When to Enable Thinking

The decision framework:

1. **Does the task require multi-step reasoning?** (math, planning, logic puzzles) → Likely benefits from thinking
2. **Is latency acceptable?** (batch processing, background jobs) → Thinking is viable
3. **Have simpler approaches failed?** (better prompts, examples, structured output) → Try thinking as optimization

Thinking modes are not a substitute for good prompt design. Clear instructions and examples often outperform thinking-enabled models with vague prompts.

---

## Family-Level Behavioral Consistency

*[2025-12-10]*: **Models within the same family exhibit aligned behavioral patterns.** Claude Opus, Sonnet, and Haiku share training approaches, alignment methodology, and base capabilities. This creates predictable behavior across tiers.

The architectural value: orchestrator-specialist systems rely on behavioral consistency. An orchestrator running on Opus delegates to specialists running on Sonnet or Haiku. If behavioral patterns diverged dramatically between tiers, coordination would require model-specific prompts and handling logic.

**What stays consistent across a family:**

- Instruction-following patterns (how the model interprets prompt structures)
- Tool-use conventions (how it formats tool calls and interprets results)
- Refusal boundaries (what triggers safety responses)
- Output formatting tendencies

**What varies by tier:**

- Reasoning depth and quality
- Context window size
- Speed and cost
- Capability ceiling (complex vs. simple tasks)

### Multi-Model Orchestration Patterns

Family consistency enables specific architectural patterns:

**Capability delegation:** Orchestrator (Opus) handles complex planning and synthesis. Specialists (Sonnet/Haiku) execute well-defined subtasks. Both speak the same "protocol" for tool use and output formatting.

**Cost optimization:** Test with frontier model, deploy with mid-tier model when behavioral consistency is verified. The prompts and tool definitions remain unchanged.

**Graceful degradation:** When frontier models are unavailable (rate limits, outages), fall back to mid-tier models. Family consistency means fallback behavior is predictable rather than arbitrary.

---

## Surprising Behaviors

Model behaviors evolve with training and fine-tuning. Some patterns emerge unexpectedly:

### Tool Selection Preferences

*[2025-12-10]*: Models sometimes prefer certain tool types over others, even when multiple tools could solve a task.

**Observed pattern:** Given a choice between a specialized tool and Bash execution, Claude tends toward Bash for filesystem operations. GPT-4 leans toward specialized tools when available.

This affects tool design. If providing both a `file_search` tool and Bash access, the model's preference determines which gets used. Design tools to align with observed preferences, or remove alternatives to force specific paths.

### Output Format Drift

Models occasionally drift from specified output formats over long conversations. A model instructed to return JSON might start wrapping responses in markdown code blocks after several turns.

**Mitigation:** Reload format requirements in system prompts periodically. For critical formatting (APIs, structured data), validate programmatically and retry on format violations.

### Instruction Fade in Long Contexts

*[2025-12-10]*: **Instructions at the start of long contexts receive less weight than recent messages.** This reflects recency bias—models weight tokens near the end of context more heavily.

The pattern appears most clearly in conversations exceeding 50% of context window capacity. Early instructions ("always format as JSON") degrade in influence as context fills.

**Architectural solutions:**

- **Repeat critical instructions** in system prompts closer to the task
- **Reduce context size** by spawning fresh agents for new tasks
- **Validate outputs** programmatically and regenerate on failures

---

## Anti-Patterns

Common mistakes when working with model behavior:

### Anti-Pattern: Assuming Deterministic Behavior

Treating models as deterministic functions leads to fragile systems. Even at temperature 0, edge cases exist where outputs vary.

**Why it fails:** Systems built assuming determinism break unpredictably. The 1% variance case appears in production at scale.

**Better approach:** Design for probabilistic outputs. Add validation, retry logic, and fallback paths. Treat consistency as an optimization, not a guarantee.

### Anti-Pattern: Ignoring Temperature Effects in Workflows

Setting temperature once and forgetting about it across multi-step workflows.

**Why it fails:** Temperature effects compound. A reasonable 0.7 temperature for single tasks becomes unreliable over ten steps.

**Better approach:** Audit temperature settings per workflow stage. Use temperature 0 for reliability-critical paths. Reserve higher temperature for creative or exploratory phases, isolated from critical execution.

### Anti-Pattern: Model-Specific Prompts Without Abstraction

Writing prompts that exploit quirks of a specific model version without abstraction layers.

**Why it fails:** Model updates break carefully tuned prompts. Switching providers requires rewriting prompts from scratch.

**Better approach:** Design prompts that work across frontier models. Test with multiple providers. When model-specific behavior is required, isolate it in configuration rather than embedding it in prompt text.

---

## Connections

- **To [Context](../4-context/_index.md):** Context length affects instruction fade and recency bias. Multi-agent architectures isolate context, reducing behavioral drift. See [Multi-Agent Context](../4-context/4-multi-agent-context.md) for how context isolation enables deterministic quality.

- **To [Prompt](../2-prompt/_index.md):** Model behavioral patterns interact with prompt structure. Different models interpret the same prompt differently. Clear instruction structure reduces variance. See [Prompt Structuring](../2-prompt/2-structuring.md) for format design patterns.

- **To [Patterns](../6-patterns/_index.md):** Orchestrator pattern relies on family-level behavioral consistency. See [Orchestrator Pattern](../6-patterns/3-orchestrator-pattern.md) for how multi-model systems leverage shared behavioral patterns.

- **To [Practices](../7-practices/_index.md):** Temperature settings and variance management affect cost and reliability. See [Cost and Latency](../7-practices/3-cost-and-latency.md) for how multi-agent architectures trade tokens for deterministic quality.

---

## Sources

- **Anthropic Extended Thinking Documentation**: Temperature incompatibility, minimum 1,024 token budget
- **Google Gemini Documentation**: Temperature 0 for deterministic calls (Gemini 2.0 defaults to 1.0)
- **Multi-Agent LLM Orchestration Research** ([arxiv.org/html/2511.15755](https://arxiv.org/html/2511.15755)): 15× token cost, 80% variance explanation from token usage, zero quality variance in multi-agent systems
- **Anthropic Multi-Agent Research System** ([anthropic.com/engineering/multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system)): Architectural patterns for parallelization
