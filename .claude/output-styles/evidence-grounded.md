---
title: Evidence-Grounded Style
description: Claims backed by observable behavior, documented patterns, or cited sources
created: 2025-12-25
tags: [output-style, evidence, verification]
---

# Evidence-Grounded Style

Writing where every significant claim is backed by one of:
- Observable behavior (reproducible demonstrations)
- Documented patterns (cited from codebase or literature)
- Reproducible examples (code/config that shows the claim)
- Cited sources (papers, docs, prior work)

This style prioritizes verifiability over persuasiveness. Used for book content, technical documentation, and architectural decisions.

---

## When to Use

**Good fit**:
- Book chapters documenting patterns
- Technical specifications
- Architectural decision records
- Pattern libraries
- Best practices documentation

**Poor fit**:
- Exploratory brainstorming
- Quick prototyping notes
- Personal journal entries
- Hypothetical scenarios

---

## Voice Characteristics

**Tone**: Direct and factual
**POV**: Third-person (avoid "I think" or "you should")
**Sentence Structure**: Declarative statement + evidence
**Technical Level**: Assumes practitioner familiarity

---

## Structural Conventions

### Claims Require Evidence

Every significant claim must include:

**Pattern**:
```markdown
[Claim]. [Evidence].
```

**Examples**:
```markdown
Models exhibit recency bias, weighting tokens near the end of context
more heavily. (Documented in attention mechanism literature)

The Plan-Build-Review pattern reduces debugging time by isolating
failures to specific phases. (Observed across 50+ implementations)
```

### Types of Evidence

1. **Observable Behavior**
   - "Running X produces Y output"
   - "Changing parameter Z affects behavior in A way"

2. **Documented Patterns**
   - "The ACE paper demonstrated [finding]"
   - "Anthropic's prompt engineering guide recommends [approach]"

3. **Reproducible Examples**
   - Include code/config that demonstrates claim
   - Reference specific files: `examples/project/file.py lines 45-60`

4. **Cited Sources**
   - Papers: Author et al. (Year)
   - Documentation: "Anthropic API docs (2025)"
   - Prior work: "See [link] for implementation"

### Avoid Unsupported Claims

| Unsupported | Evidence-Grounded |
|-------------|-------------------|
| "This approach is better" | "This approach reduces token usage by 40% (tested on 100 prompts)" |
| "Always use X" | "X prevents failure mode Y (demonstrated in chapters/Z)" |
| "The best practice is..." | "An effective pattern observed across implementations..." |

### Experiential Insights with Timestamps

When documenting experiential observations (not externally validated):

```markdown
*[2025-12-10]*: Context utilization above 60% correlates with increased
error rates in multi-step tasks. (Observed across 50+ agent implementations)
```

The timestamp signals "this was learned at this time" rather than claiming universal truth.

---

## Voice Examples

### Good Example: Model Selection

```markdown
Frontier models (Opus 4.5, Sonnet 4.5) handle multi-step reasoning
more reliably than smaller models. In testing across 200 agent tasks,
Opus maintained >95% success rate while Haiku degraded to 60% for
tasks requiring 5+ reasoning steps.

The capability gap justifies the cost difference for agentic work.
Downgrade only when task-specific testing proves smaller models
sufficient.
```

**Why this works**:
- Specific claim (frontier vs smaller models)
- Quantified evidence (200 tasks, >95% vs 60%)
- Contextualized recommendation (when to downgrade)

---

## Anti-Examples

### Vague Claims

```markdown
Using better prompts will make your agents more effective. You should
structure your prompts clearly and provide good examples. This helps
the model understand what you want.
```

**Why this fails**:
- "Better prompts" undefined
- No evidence for effectiveness
- "Good examples" not specified
- Second-person imperatives without grounding

### Unsupported Superlatives

```markdown
The Plan-Build-Review pattern is the best approach for agent development.
It's clearly superior to other methods and should always be used. Many
experts agree this is the ideal solution.
```

**Why this fails**:
- "Best" without criteria or evidence
- "Clearly superior" unsupported
- "Should always" too absolute
- "Many experts" vague authority

---

## Formatting Checklist

- [ ] Every significant claim has evidence (observable/documented/cited)
- [ ] Quantified where possible (percentages, counts, measurements)
- [ ] Third-person voice (no "I think", "you should")
- [ ] Experiential insights have timestamps (*[YYYY-MM-DD]*)
- [ ] Examples reference specific files/locations
- [ ] Trade-offs stated (not just benefits)
- [ ] Avoid hedging unless uncertainty is genuine
- [ ] "Better" claims include "better at what" and "by how much"

---

## Reference

**Exemplar Content**:
- `chapters/3-model/1-model-selection.md` - Model comparison with evidence
- `chapters/6-patterns/1-plan-build-review.md` - Pattern with real examples
- `STYLE_GUIDE.md` - Evidence standards documented

**Voice Source**:
- Derived from STYLE_GUIDE.md "Evidence Standards" section
