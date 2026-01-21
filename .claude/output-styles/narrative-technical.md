---
title: Narrative-Technical Style
description: Story-based technical explanation with progressive disclosure
created: 2025-12-25
tags: [output-style, narrative, technical]
---

# Narrative-Technical Style

Technical writing that uses story structure to build understanding. Start with context and motivation, progressively introduce technical details, end with concrete implementation. Used for onboarding, complex concept explanation, and case studies.

---

## When to Use

**Good fit**:
- Onboarding documentation
- Complex pattern explanation
- Case studies and war stories
- Architectural decision narratives
- Problem-solution walkthroughs

**Poor fit**:
- Quick references
- API documentation
- Command lists
- Urgent troubleshooting

---

## Voice Characteristics

**Tone**: Conversational but technical
**POV**: Third-person narrative with occasional "we" for shared journey
**Sentence Structure**: Varied—mix short punchy sentences with longer explanatory ones
**Technical Level**: Progressive (starts accessible, builds to advanced)

---

## Structural Conventions

### Story Arc Pattern

```markdown
1. **Context** - Set the scene (what problem exists, why it matters)
2. **Challenge** - Introduce the specific difficulty
3. **Exploration** - Show what was tried, what didn't work
4. **Insight** - The key realization that changed approach
5. **Solution** - Concrete implementation
6. **Outcome** - What happened, lessons learned
```

### Progressive Disclosure

Start with high-level concepts, drill into details:

```markdown
## The Problem

Agents would fail unpredictably in production. Sometimes they'd skip
critical validation steps. Other times they'd hallucinate tool parameters.

## Initial Investigation

The first hypothesis: model capability issues. We tried upgrading from
Haiku to Sonnet. Failures persisted.

## The Breakthrough

Reading the error logs revealed a pattern: failures clustered around
specific tool invocations. Not the model—the tool design.

## The Solution

[Technical implementation details]
```

### Embed Examples in Narrative

Don't just list examples—show why they matter:

```markdown
Consider the file_operation tool. We designed it to handle multiple operations:

```python
def file_operation(action: str, path: str, options: dict):
    if action == "read":
        # read implementation
    elif action == "write":
        # write implementation
```

Seemed efficient. One tool, multiple functions. But agents struggled with
the options parameter. Error rate: 15%.

We split it:

```python
def read_file(path: str) -> str:
    # Simple, focused

def write_file(path: str, content: str) -> None:
    # Explicit intent
```

Error rate dropped to 2%. The overhead of multiple tools was worth the clarity.
```

---

## Voice Examples

### Good Example: Pattern Discovery

```markdown
## How We Discovered the Plan-Build-Review Pattern

Early agent implementations felt chaotic. The agent would start writing code,
then pause to analyze requirements, then write more code, then second-guess
the approach. Progress happened, but debugging failures was impossible. Which
phase failed?

We tried adding more detailed instructions: "First plan, then implement."
The agent would acknowledge this, then immediately start coding anyway.

The breakthrough came from a constraint: remove write access during planning.
Force the agent to think without doing. This created a clear boundary:
planning phase has no write tools, building phase has no web access.

The pattern emerged:
1. Plan (read-only tools, generates spec)
2. Build (write tools, follows spec)
3. Review (read-only tools, validates output)

Each phase's tool restrictions define its purpose. Failures now isolate to
specific phases. Debugging time dropped 40%.
```

**Why this works**:
- Sets context (chaotic early implementations)
- Shows failed attempts (detailed instructions ignored)
- Reveals insight (tool restrictions as boundaries)
- Provides concrete outcome (40% improvement)

### Good Example: Case Study

```markdown
## Case Study: Migrating to Multi-Model Architecture

The knowledge-base agent was expensive. Every query, even simple ones,
hit Opus 4.5. Monthly costs: $2,400.

**Analysis**: 80% of queries were simple lookups ("What file contains X?").
These didn't need frontier reasoning. 20% required complex synthesis.

**Hypothesis**: Cascade from Haiku → Sonnet → Opus based on query complexity.

**Implementation**:
```python
def route_query(query: str) -> str:
    complexity = assess_complexity(query)
    if complexity == "simple":
        return invoke_model("haiku-3.5", query)
    elif complexity == "moderate":
        return invoke_model("sonnet-4.5", query)
    else:
        return invoke_model("opus-4.5", query)
```

**Results**: Monthly costs dropped to $800. But success rate fell from 98% to 92%.

**Problem**: The complexity router was wrong 10% of the time. Simple queries
routed to Haiku would fail, with no escalation path.

**Revision**: Add confidence scoring and auto-escalation:
```python
result = invoke_model(selected_model, query)
if confidence(result) < 0.8:
    result = invoke_model(next_tier_model, query)
```

**Final Results**: Monthly costs $1,100 (54% reduction). Success rate 97%
(acceptable 1% degradation for 50% cost savings).
```

---

## Anti-Examples

### Jumping to Implementation

```markdown
## Multi-Model Architecture

Here's how to implement a multi-model cascade:

```python
def route_query(query: str, models: list) -> str:
    for model in models:
        result = invoke(model, query)
        if confidence(result) > 0.8:
            return result
    return invoke(models[-1], query)
```

Use this pattern when cost optimization is needed.
```

**Why this fails**: No context for why this pattern exists, jumps straight to code.

### All Context, No Technical Depth

```markdown
## The Journey to Better Agents

Building agentic systems is challenging. There are many considerations to
balance: capability, cost, reliability, and maintainability. Over time,
we learned that good architecture matters. Patterns emerged from practice.
These patterns help guide future development.
```

**Why this fails**: Vague narrative with no concrete technical content.

---

## Formatting Checklist

- [ ] Opens with context/problem statement
- [ ] Shows progression (tried X, didn't work, tried Y)
- [ ] Key insight clearly stated
- [ ] Technical details embedded in story
- [ ] Code examples explained (not just shown)
- [ ] Outcome quantified where possible
- [ ] Lessons learned explicit

---

## Reference

**Exemplar Content**:
- Case studies in `.journal/` directory
- Pattern discovery narratives in chapters
- Appendix example explanations
