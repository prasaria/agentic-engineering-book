# Output Styles

This directory contains reusable style guides that agents can reference when generating content. Each style defines voice, structure, and formatting conventions for specific contexts.

## Available Styles

| Style | When to Use | Voice | Format |
|-------|-------------|-------|--------|
| [Evidence-Grounded](evidence-grounded.md) | Book content, technical docs | Third-person, factual | Claims + evidence |
| [Practitioner-Focused](practitioner-focused.md) | Agent prompts, how-tos | Direct, imperative | Action-first, examples |
| [Academic-Structured](academic-structured.md) | Research summaries, formal specs | Formal, objective | Standard sections, citations |
| [Narrative-Technical](narrative-technical.md) | Story-driven explanations | Story + technical | Context → pattern → code |
| [Concise-Reference](concise-reference.md) | Quick lookups, cheat sheets | Terse, neutral | Tables, lists, fragments |

## How to Use

**In Agent Prompts**:
```markdown
## Instructions

- Follow the [Evidence-Grounded](.claude/output-styles/evidence-grounded.md) style
- Every claim requires evidence (observable/documented/cited)
- Use third-person voice throughout
```

**In Command Descriptions**:
```markdown
Generate output using [Practitioner-Focused](.claude/output-styles/practitioner-focused.md) style:
- Lead with action
- Code examples before explanation
- Direct voice, no hedging
```

## Style Selection Guide

```
Need to...                    → Use this style
────────────────────────────────────────────────
Document patterns             → Evidence-Grounded
Write agent prompts           → Practitioner-Focused
Summarize research            → Academic-Structured
Explain complex concepts      → Narrative-Technical
Create quick reference        → Concise-Reference
```

## Agent Integration

Agents declare their output style via frontmatter field, then reference in Instructions section.

**Frontmatter Pattern:**
```yaml
---
name: knowledge-question-agent
description: Answers questions about knowledge patterns
tools: Read, Glob, Grep
model: haiku
color: cyan
output-style: concise-reference
---
```

**Instructions Reference Pattern:**
```markdown
## Instructions

**Output Style:** Follow `.claude/output-styles/concise-reference.md` conventions
- Use tables for comparisons
- Bullets for sequences
- Fragments acceptable (no full paragraphs)
```

**4-Agent Expert Pattern Defaults:**
- **Question agents**: `concise-reference` (scannable Q&A, haiku model)
- **Plan agents**: `academic-structured` (rigorous specs, standard sections)
- **Build agents**: `practitioner-focused` (action-first, code examples)
- **Improve agents**: `evidence-grounded` (timestamped, git-backed claims)

## Adding New Styles

1. Copy template from existing style
2. Define:
   - When to use (good fit / poor fit)
   - Voice characteristics (tone, POV, structure)
   - Formatting conventions
   - Examples (good + anti-examples)
3. Add to table above
4. Reference from agents/commands as needed
