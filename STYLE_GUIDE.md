# Writing Style Guide

This document establishes the writing style for the Agentic Engineering book. All contributors and agents must follow these conventions to ensure consistency.

## Style Profile

**Category:** Technical Practitioner
**Voice:** Third-person only
**Evidence Standard:** Evidence-grounded
**Structure:** Flexible with required elements

---

## Voice Conventions

### Third-Person Only

Write in third-person throughout. Avoid first-person ("I", "we") and second-person ("you").

| Avoid | Use Instead |
|-------|-------------|
| "I've found that context management..." | "Context management tends to..." |
| "You should validate inputs..." | "Input validation prevents..." |
| "We can see that the pattern..." | "The pattern demonstrates..." |
| "When you build agents..." | "When building agents..." |

### Active Voice Preferred

Use active voice for clarity. Passive voice is acceptable when the actor is unknown or irrelevant.

| Passive (Avoid) | Active (Preferred) |
|-----------------|-------------------|
| "Errors are handled by the system" | "The system handles errors" |
| "The prompt is interpreted by the model" | "The model interprets the prompt" |

### Imperative for Instructions

When giving direct guidance, use imperative mood without "you":

| Avoid | Use Instead |
|-------|-------------|
| "You should structure prompts clearly" | "Structure prompts clearly" |
| "You need to validate tool outputs" | "Validate tool outputs" |

---

## Evidence Standards

### Evidence-Grounded Claims

Every significant claim must be grounded in one of:

1. **Observable behavior** - "Models exhibit recency bias, weighting tokens near the end of context more heavily."
2. **Documented patterns** - "The ACE paper demonstrated progressive degradation in dynamic cheatsheet approaches."
3. **Reproducible examples** - Include code or configuration that demonstrates the claim.
4. **Cited sources** - Reference papers, documentation, or prior work when available.

### Unsupported Assertions

Avoid claims that cannot be verified:

| Unsupported | Evidence-Grounded |
|-------------|-------------------|
| "This approach is better" | "This approach reduces token usage by ~40% in tested scenarios" |
| "Always use X" | "X prevents common failure modes: [list specific failures]" |
| "The best practice is..." | "A effective pattern observed across implementations..." |

### Experiential Insights

When documenting experiential observations (not externally validated), use dated attribution:

```markdown
*[2025-12-10]*: Context utilization above 60% correlates with increased error rates in multi-step tasks. (Observed across 50+ agent implementations)
```

The timestamp signals "this was learned at this time" rather than claiming universal truth.

---

## Required Structural Elements

Every chapter/section entry must include:

### 1. Opening Statement
A clear, grounded statement establishing relevance. First 1-2 sentences should answer "what is this and why does it matter?"

```markdown
## Context Management

Context determines what an agent knows at any given moment. Poor context management
leads to capability degradation, hallucination, and task failure.
```

### 2. Concrete Examples
Show before explaining. Examples should be:
- Specific (not "some code" but actual code)
- Contrasted ("Fragile" vs "Robust", "Before" vs "After")
- Minimal (show only what's necessary)

```markdown
### Fragile
```
Handle errors appropriately
```

### Robust
```
When an error occurs:
1. Log the error message and stack trace
2. Return a user-friendly message (never expose internals)
3. Continue execution if possible, exit gracefully if not
```
```

### 3. Connections Section
Link to related chapters/sections with explanation of the relationship:

```markdown
## Connections

- **[Context](../4-context/_index.md)**: Tool outputs become context for subsequent reasoning.
  Large tool outputs can consume context budget rapidly.
- **[Patterns](../6-patterns/_index.md)**: The Plan-Build-Review pattern structures tool use
  across phases.
```

---

## Optional Structural Elements

Include when relevant to the content:

### When to Use / When Not to Use
Prevents cargo-cult adoption:

```markdown
### When to Use
- Multi-step tasks requiring state persistence
- Workflows with clear phase boundaries

### When Not to Use
- Simple single-turn interactions
- Tasks where context freshness is critical
```

### Anti-Patterns
Name what fails and explain why:

```markdown
### Anti-Pattern: Context Dumping

Loading all available information into context regardless of relevance.

**Why it fails:** Dilutes signal with noise. Models weight all tokens, so
irrelevant information competes with relevant information for attention.

**Better approach:** Progressive disclosure—load minimal context initially,
expand based on task needs.
```

### Open Questions
Acknowledge uncertainty rather than false completeness:

```markdown
### Open Questions

- How does context window size interact with reasoning depth?
- What's the optimal ratio of examples to instructions in few-shot prompts?
```

### Tables for Comparisons
Use tables for trade-off analysis and feature comparison:

```markdown
| Approach | Latency | Cost | Complexity |
|----------|---------|------|------------|
| Synchronous | High | Low | Low |
| Async Queue | Medium | Medium | Medium |
| Streaming | Low | High | High |
```

---

## Formatting Conventions

### Headers
- H1 (`#`) - Document title only
- H2 (`##`) - Major sections
- H3 (`###`) - Subsections
- H4 (`####`) - Rarely used, for deep nesting

### Lists
- **Numbered lists** for sequences/steps
- **Bulleted lists** for options/attributes (no implied order)
- **Definition lists** (bold term + description) for glossaries

### Code Blocks
- Always specify language for syntax highlighting
- Keep examples minimal and focused
- Use comments sparingly—code should be self-explanatory

### Emphasis
- **Bold** for key terms on first use
- *Italics* for emphasis within sentences
- `Code` for inline technical terms, file names, commands

---

## Terminology Precision

### Define on First Use
When introducing a term, provide a clear definition:

```markdown
**Context window**—the maximum number of tokens a model can process in a single
invocation. This includes both input (prompt + context) and output (generation).
```

### Consistent Term Usage
Once a term is defined, use it consistently:

| Inconsistent | Consistent |
|--------------|------------|
| "prompt", "instruction", "input" (interchangeably) | "prompt" (for the full input) |
| "agent", "system", "assistant" (interchangeably) | "agent" (for autonomous systems) |

### Avoid Jargon Without Explanation
Technical terms are acceptable; undefined jargon is not:

| Jargon | With Explanation |
|--------|------------------|
| "The RAG pipeline" | "The retrieval-augmented generation (RAG) pipeline" |
| "Use CoT prompting" | "Use chain-of-thought (CoT) prompting—structuring prompts to elicit step-by-step reasoning" |

---

## Sentence Structure

### Short Paragraphs
Maximum 3-4 sentences per paragraph. One idea per paragraph.

### Declarative + Consequence
State a fact, then show why it matters:

```markdown
Transformers use attention to weight input tokens. This means every token in the
context influences output probability—irrelevant tokens add noise to the signal.
```

### Avoid Hedging
Write with appropriate confidence. Avoid weak qualifiers unless uncertainty is genuine:

| Hedged | Direct |
|--------|--------|
| "It might be worth considering..." | "Consider..." |
| "Perhaps the approach could..." | "The approach..." |
| "It seems like this might help" | "This helps when..." |

When genuine uncertainty exists, state it clearly:

```markdown
The relationship between context length and reasoning quality remains unclear.
Some evidence suggests diminishing returns above 8K tokens, but this varies by task type.
```

---

## What This Style Is Not

- **Not academic** - No passive-heavy prose, no "it can be argued that"
- **Not casual** - No colloquialisms, no "basically", no rhetorical questions
- **Not narrative** - No personal anecdotes, no "I remember when"
- **Not exhaustive** - Prioritize clarity over completeness

---

## Checklist for New Content

Before submitting content, verify:

- [ ] Third-person voice throughout (no "I", "we", "you")
- [ ] Claims are evidence-grounded (observable, documented, cited, or dated)
- [ ] Opening statement establishes relevance
- [ ] Concrete examples included (before/after, fragile/robust)
- [ ] Connections section links to related content
- [ ] Short paragraphs (3-4 sentences max)
- [ ] Technical terms defined on first use
- [ ] Active voice preferred
- [ ] No hedging without genuine uncertainty
- [ ] Frontmatter complete (`title`, `description`, `created`, `last_updated`, `tags`, `part`, `chapter`, `section`, `order`)
