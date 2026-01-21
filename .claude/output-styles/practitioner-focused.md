---
title: Practitioner-Focused Style
description: Direct, hands-on guidance for builders with minimal preamble
created: 2025-12-25
tags: [output-style, practical, concise]
---

# Practitioner-Focused Style

Writing optimized for practitioners who need answers fast. Skip the theory, lead with the pattern, show concrete examples. Used for agent prompts, implementation guides, and quick references.

---

## When to Use

**Good fit**:
- Agent system prompts
- Implementation guides
- How-to documentation
- Quick reference cards
- Command descriptions

**Poor fit**:
- Conceptual overviews
- Academic comparisons
- Exploratory thinking
- Teaching fundamentals

---

## Voice Characteristics

**Tone**: Direct and imperative
**POV**: Second-person acceptable ("Configure X", "Use Y when Z")
**Sentence Structure**: Short paragraphs, 3-4 sentences max
**Technical Level**: Assumes working knowledge

---

## Structural Conventions

### Lead with Action

Start with what to do, not why to do it.

**Pattern**:
```markdown
## [Action]

[What to do in 1-2 sentences]

[Code/config example]

[When/why in 1 sentence]
```

**Example**:
```markdown
## Configure Model Selection

Use Sonnet 4.5 for balanced reasoning and cost:

```yaml
model: sonnet-4.5
```

Downgrade to Haiku only after task-specific testing proves it works.
```

### Prefer Bullets and Lists

Use numbered lists for sequences, bullets for options.

**Sequential steps**:
```markdown
1. Load expertise.yaml
2. Validate against codebase
3. Update discrepancies
4. Check YAML syntax
```

**Options/attributes**:
```markdown
- **Fast**: Haiku (test first)
- **Balanced**: Sonnet (default)
- **Powerful**: Opus (complex reasoning)
```

### Code/Examples Before Explanation

Show concrete implementation first, explain after.

**Good**:
```markdown
## Structure System Prompt

```markdown
# Role
You are a [domain] expert.

# Instructions
- Do X
- Do Y

# Workflow
1. Step A
2. Step B
```

This structure separates mutable knowledge (Role) from stable process (Workflow).
```

**Poor**:
```markdown
## Structure System Prompt

System prompts should separate concerns between the role definition, which may
change over time, and the workflow, which should remain stable. This separation
enables safer updates. Here's how to structure it: [example follows]
```

### Skip Hedging

Be direct. Avoid "might", "could", "perhaps" unless genuine uncertainty.

**Direct**:
```markdown
Use frontier models for agentic work. The capability gap matters.
```

**Hedged** (avoid):
```markdown
You might want to consider using frontier models, as they could potentially
offer better capabilities for agentic work in some cases.
```

---

## Voice Examples

### Good Example: Command Usage

```markdown
## Run Self-Improve

Validate expertise against chapter content:

```bash
/knowledge:self-improve chapters/3-model
```

This checks for:
- Broken references (file paths, line numbers)
- Missing patterns (in book but not expertise)
- YAML syntax errors
- Line count >1000 (triggers trimming)

Fix issues automatically where possible, report others.
```

### Good Example: Tool Design

```markdown
## Design Single-Purpose Tools

Split multi-function tools into focused operations:

**Bad**:
```python
def file_operation(action: str, path: str, options: dict):
    # Confusing, high parameter error rate
```

**Good**:
```python
def read_file(path: str) -> str:
    # Clear purpose, minimal parameters

def write_file(path: str, content: str) -> None:
    # Separate operation, explicit intent
```

Agents make 3x fewer errors with focused tools.
```

---

## Anti-Examples

### Over-Explained

```markdown
## Understanding Model Selection

Model selection is a critical decision in agentic system design. When
building an agent, you'll need to carefully consider various factors
including reasoning capability, cost constraints, latency requirements,
and context window size. Each of these factors interacts with the others
in complex ways that merit careful analysis.

First, let's discuss reasoning capability. Frontier models like Opus and
Sonnet offer superior reasoning compared to smaller models...
```

**Why this fails**: Too much preamble before actionable guidance.

### Vague Guidance

```markdown
## Improve Your Prompts

Good prompts are important for agent success. Make sure your prompts are
clear and well-structured. Include relevant information and avoid being
too verbose or too brief. Test your prompts to see if they work well.
```

**Why this fails**: No concrete patterns, no examples, vague advice.

---

## Formatting Checklist

- [ ] Lead with action or pattern (not theory)
- [ ] Code/examples before explanation
- [ ] Short paragraphs (3-4 sentences max)
- [ ] Bullets for options, numbers for sequences
- [ ] Direct voice (no hedging)
- [ ] Concrete not abstract
- [ ] Skip preamble

---

## Reference

**Exemplar Content**:
- `.claude/agents/experts/knowledge/knowledge-plan-agent.md` - Direct agent prompt
- `chapters/2-prompt/2-structuring.md` - Templates before theory
- `CLAUDE.md` - Concise reference format
