---
title: Plan-Build-Review Pattern
description: Multi-phase workflow pattern with optional research foundation and feedback loops for continuous improvement
created: 2025-12-08
last_updated: 2025-12-10
tags: [patterns, workflow, feedback-loops, continuous-improvement, research]
part: 2
part_title: Craft
chapter: 6
section: 1
order: 2.6.1
---

# Plan-Build-Review Pattern

A workflow pattern that separates specification from implementation, with optional research phase and feedback loops where production experience continuously improves the process itself.

---

## Core Insight

*[2025-12-10]*: **Bad research compounds exponentially.** One flawed architectural assumption in the Research phase leads to a misguided plan, which generates thousands of lines of incorrect code. Research quality has massive leverage on all downstream outcomes.

The core pattern has three phases (Plan-Build-Improve), with an optional Research phase for complex domains. The four-command expert pattern (Research-Plan-Build-Improve) creates a learning loop where each phase builds on validated understanding:

1. **Research** - Understand the problem space, codebase structure, and dependencies
2. **Plan** - Creates detailed specifications grounded in research findings
3. **Build** - Implements according to the research-backed spec
4. **Improve** - Analyzes what happened and updates the Research/Plan/Build expertise

The Improve phase closes the loop by extracting learnings from actual production usage and updating the expert's knowledge base across all commands, making each iteration smarter than the last.

---

## How It Works

### The Learning Loop

```
    Research (with Expertise)
         ↓
    Plan (with Expertise)
         ↓
    Build (with Expertise)
         ↓
    Production Experience
         ↓
    Improve (updates Expertise)
         ↓
    (feeds back to Research/Plan/Build)
```

### Key Characteristics

- **Mutable Expertise Sections**: Unlike workflows, the Expertise sections in Research/Plan/Build commands are designed to evolve
- **Experience-Driven Evolution**: Learnings come from real production usage, not theory
- **Self-Improving System**: Each cycle makes the next iteration better
- **Persistent Knowledge**: Insights are captured in the prompts themselves, not lost in conversation history

---

## The Research Phase

*[2025-12-10]*: Research is the foundation that determines everything downstream. Before planning what to build, you need to understand:

- **Codebase structure**: Where does relevant code live? What are the existing patterns?
- **Dependencies**: What does this component depend on? What depends on it?
- **Problem causes**: What actually broke? What's the root cause vs. symptoms?
- **Constraints**: What can't change? What assumptions must hold?

### Research as Artifact Generation

The output of research isn't just understanding—it's **concise summary documents** that capture findings:

```markdown
# Research Summary: Feature X Implementation

## Current Architecture
- Component Y handles Z via pattern P
- Dependencies: A, B, C (see /path/to/code)

## Problem Root Cause
- Symptom: Users report timeout
- Cause: Unbounded retry loop in module M
- Evidence: /path/to/logs, line 234

## Constraints
- Cannot change API contract (external clients)
- Must maintain backward compatibility with v1.x

## Recommended Approach
Based on architecture analysis, approach 2 (async queue)
fits existing patterns better than approach 1 (sync retry).
```

These artifacts serve two purposes:
1. **Grounding**: Plan phase references concrete findings, not assumptions
2. **Validation**: Team can review research conclusions before building begins

### The Exponential Compounding Problem

Why research deserves a dedicated phase:

| Research Quality | Plan Accuracy | Lines of Wrong Code | Cost to Fix |
|------------------|---------------|---------------------|-------------|
| Excellent | 95% | ~50 | Hours |
| Good | 80% | ~500 | Days |
| Poor | 50% | ~5,000 | Weeks |
| Terrible | 10% | Complete rewrite | Months |

A 10-minute research mistake can create a 10-week refactoring disaster. The leverage is asymmetric—investing in research quality pays exponential dividends.

### What Good Research Looks Like

**Good:**
- "Module X uses pattern Y (see lines 45-67 in file.py)"
- "Dependency graph shows A→B→C, change must start at C"
- "Root cause: race condition between handlers (reproduced in test)"

**Bad:**
- "The code probably does something with databases"
- "I think this component is important"
- "We should investigate the authentication system"

Good research is specific, sourced, and falsifiable. Bad research is vague and ungrounded.

---

## Implementation in Claude Code

In Claude Code's slash command system, this pattern is implemented through expert command sets:

```
.claude/commands/experts/[domain]-expert/
     [domain]_expert_research.md  # Has ## Expertise section
     [domain]_expert_plan.md      # Has ## Expertise section
     [domain]_expert_build.md     # Has ## Expertise section
     [domain]_expert_improve.md   # Updates the Expertise sections
```

The Improve command:
1. Analyzes recent git changes
2. Identifies successful patterns and learnings
3. Updates ONLY the Expertise sections in Research/Plan/Build commands
4. Keeps workflow sections stable

### Research Command Structure

A typical Research expert command:

```markdown
## Workflow

1. **Understand the Requirement**
   - What problem are we solving?
   - What's the scope?

2. **Explore the Codebase**
   - Use Glob/Grep to find relevant files
   - Read key components
   - Map dependencies

3. **Analyze the Problem**
   - Identify root causes
   - Distinguish symptoms from causes
   - Document constraints

4. **Generate Research Summary**
   - Create concise summary document
   - Include specific file paths and line numbers
   - State conclusions with evidence

## Expertise

*[2025-12-10]*: (Accumulated learnings about researching this domain)
```

---

## When to Use This Pattern

### Good Fit

**Complex, knowledge-intensive domains:**
- Multi-step workflows requiring specialized understanding
- Tasks where learning from experience is valuable
- Situations where patterns emerge over time
- When you want prompts to improve with use

**Indicators you need this pattern:**
- Repeatedly solving similar problems in the same domain
- Accumulating domain-specific best practices
- Need for consistent approach across team/project
- High cost of mistakes (research phase prevents compounding errors)

### Poor Fit

**Simple or one-off tasks:**
- Single-file changes with clear requirements
- Domains with fixed, unchanging requirements
- When expertise doesn't accumulate meaningfully
- Tasks simple enough that planning overhead exceeds benefit

**When simpler approaches work:**
- Ad-hoc changes with no pattern reuse
- Exploratory work where learning isn't transferable
- Domains where external documentation is comprehensive and stable

---

## Connections

- **To [Prompts/Structuring](../2-prompt/2-structuring.md)**: How mutable sections in prompts enable learning
- **To [Claude Code](../9-practitioner-toolkit/1-claude-code.md)**: Concrete implementation in slash command experts
- **To [Evaluation](../7-practices/2-evaluation.md)**: How do you measure if Improve is actually improving?
- **To [Context Management](../4-context/_index.md)**: Research generates artifacts that become context for Plan/Build phases
- **To [Specs as Source Code](../8-mental-models/3-specs-as-source-code.md)**: Plans are executable specifications, not throwaway scaffolding

---

## Related Patterns

- **ReAct Loop**: Similar feedback structure but at inference time, not across sessions
- **Human-in-the-Loop**: Review phase could involve human validation
- **Multi-Agent**: Multiple experts could each use Research-Plan-Build-Improve internally
