---
title: Academic-Structured Style
description: Formal research-oriented writing with rigorous structure
created: 2025-12-25
tags: [output-style, academic, formal]
---

# Academic-Structured Style

Formal writing with clear structure, defined terms, and systematic argumentation. Used for research notes, literature reviews, and when communicating with academic audiences.

---

## When to Use

**Good fit**:
- Research summaries
- Literature reviews
- Formal specifications
- Academic paper annotations
- Systematic comparisons

**Poor fit**:
- Implementation guides
- Agent prompts
- Quick reference
- Internal documentation

---

## Voice Characteristics

**Tone**: Formal and objective
**POV**: Third-person exclusively
**Sentence Structure**: Complex, well-structured paragraphs
**Technical Level**: Assumes theoretical background

---

## Structural Conventions

### Standard Sections

1. **Abstract/Summary** - Overview of key points
2. **Introduction** - Context and motivation
3. **Background** - Prior work and definitions
4. **Methodology/Approach** - How the work was done
5. **Results/Findings** - What was discovered
6. **Discussion** - Interpretation and implications
7. **Conclusion** - Summary and future work
8. **References** - Citations

### Term Definitions

Define technical terms on first use:

```markdown
**Context window**—the maximum number of tokens a model can process in a
single invocation, including both input (prompt + context) and output
(generation).
```

### Formal Citations

Use consistent citation format:

```markdown
The ACE framework demonstrates iterative refinement improves reasoning
quality (Smith et al., 2024). This finding aligns with prior work on
self-consistency (Wang et al., 2023) and chain-of-thought prompting
(Wei et al., 2022).
```

### Systematic Comparisons

Present comparisons using structured analysis:

```markdown
## Comparison of Multi-Model Architectures

Three primary architectural patterns emerge from the literature:

1. **Cascading Pattern** - Sequential model invocation with quality gates
   - *Advantage*: Cost optimization through selective model use
   - *Limitation*: Increased latency from sequential execution
   - *Evidence*: Demonstrated in production systems (Jones et al., 2024)

2. **Parallel Pattern** - Concurrent model invocation with consensus
   - *Advantage*: Improved reliability through redundancy
   - *Limitation*: Higher cost from parallel execution
   - *Evidence*: Self-consistency research (Wang et al., 2023)
```

---

## Voice Examples

### Good Example: Research Summary

```markdown
## Abstract

This analysis examines prompt engineering patterns for agentic systems,
synthesizing findings from 50+ production implementations. The research
identifies three primary maturity levels: static prompts (baseline),
contextual prompts (adaptive), and composed prompts (orchestrated).
Evidence suggests composed prompts reduce debugging time by 40% while
increasing initial development time by 25%.

## Background

Prompt engineering for agentic systems differs from single-shot LLM
interactions in several key dimensions. First, agents operate across
multiple invocations, requiring consistency in reasoning approach
(Smith et al., 2024). Second, agents must handle variable context,
necessitating adaptive prompting strategies (Jones & Lee, 2024).
```

### Good Example: Literature Review

```markdown
## Prior Work on Tool Use

Agent tool use has been studied extensively in recent literature.
Wei et al. (2022) demonstrated that tool access improves reasoning
on complex tasks requiring external computation. Chen et al. (2023)
extended this work to multi-step tool invocation, showing cascading
tool use in problem decomposition.

The current work differs from these approaches in two ways. First,
we focus on tool restriction as a security mechanism rather than
capability enhancement. Second, we examine production deployment
patterns rather than controlled experiments.
```

---

## Anti-Examples

### Informal Voice

```markdown
## How We Did It

So we basically looked at a bunch of different prompting approaches
and tried to figure out which ones worked best. We noticed that some
patterns kept showing up, which was pretty interesting. Here's what
we found...
```

**Why this fails**: Too casual, lacks formal structure.

### Missing Citations

```markdown
## Multi-Model Architectures

Multi-model architectures are better than single-model approaches.
They improve reliability and reduce costs. Many researchers have
demonstrated these benefits. The cascading pattern is particularly
effective for production systems.
```

**Why this fails**: Claims lack citations, vague references ("many researchers").

---

## Formatting Checklist

- [ ] Standard section structure (Abstract, Introduction, etc.)
- [ ] Terms defined on first use
- [ ] Formal citations included
- [ ] Third-person throughout
- [ ] Claims supported by references
- [ ] Methodology clearly stated
- [ ] Structured comparisons (not just lists)
- [ ] Conclusions tied to evidence

---

## Reference

**Exemplar Content**:
- Research paper summaries in `.journal/`
- Formal specs in `.claude/plans/`
- Academic paper annotations
