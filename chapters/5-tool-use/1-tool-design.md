---
title: Tool Design
description: Principles for creating well-designed tools that agents can use effectively
created: 2025-12-10
last_updated: 2026-01-30
tags: [tool-design, naming, parameters, descriptions, function-calling]
part: 1
part_title: Foundations
chapter: 5
section: 1
order: 1.5.1
---

# Tool Design

Well-designed tools make the difference between an agent that can accomplish tasks and one that constantly struggles with its own interface.

---

## Tool Examples as Design Pattern

*[2025-12-09]*: JSON schemas define structural validity but can't teach usage—that's what examples are for.

**The Gap**: Schemas tell the model what parameters exist and their types, but not:
- When to include optional parameters
- Which parameter combinations make sense together
- API conventions not expressible in JSON Schema

**The Pattern**: Provide 1-5 concrete tool call examples demonstrating correct usage at varying complexity levels.

**Example Structure** (for a support ticket API):
1. **Minimal**: Title-only task—shows the floor
2. **Partial**: Feature request with some reporter info—shows selective use
3. **Full**: Critical bug with escalation, full metadata—shows the ceiling

This progression teaches when to use optional fields, not just that they exist.

**Results**: Internal testing showed accuracy improvement from 72% → 90% on complex parameter handling.

**Best Practices**:
- Use realistic data, not placeholder values ("John Doe", not "{name}")
- Focus examples on ambiguity areas not obvious from schema alone
- Show the minimal case first—don't always demonstrate full complexity
- Keep examples concise (1-5 per tool, not 20)

**See Also**:
- [Prompt: Structuring](../2-prompt/2-structuring.md) — How tool examples relate to broader prompt design principles

**Source**: [Advanced Tool Use - Anthropic](https://www.anthropic.com/engineering/advanced-tool-use)

---

## Rich User Questioning Patterns

*[2026-01-30]*: Orchestration research from cc-mirror reveals sophisticated user clarification patterns that replace text-based menus with rich, decision-guiding question structures.

### Philosophy: Users Need to See Options

**Core insight:** "Users don't know what they want until they see the options"

Asking "What should I prioritize?" yields vague answers. Showing 4 options with descriptions, trade-offs, and recommendations enables informed decisions.

### The 4×4 Maximal Pattern

**Structure:**
- 4 questions addressing different decision dimensions
- 4 options per question with rich descriptions
- Trade-offs and implications explicit
- Recommended option guides optimal choice
- Multi-select support when appropriate

**Example: Feature Implementation Scope Clarification**

```python
AskUserQuestion(
    questions=[
        {
            "text": "What's the primary goal?",
            "options": [
                {
                    "label": "Performance optimization",
                    "description": "Focus on speed and efficiency. May increase code complexity and require more thorough testing.",
                    "recommended": True
                },
                {
                    "label": "Code simplicity",
                    "description": "Prioritize readability and maintainability over raw speed. Easier onboarding, longer execution time."
                },
                {
                    "label": "Feature completeness",
                    "description": "Cover all edge cases and scenarios. Comprehensive but longer timeline. Best for user-facing features."
                },
                {
                    "label": "Quick MVP",
                    "description": "Fast delivery with core features only. Technical debt acceptable. Good for validation before full build."
                }
            ]
        },
        {
            "text": "How should we handle errors?",
            "options": [
                {
                    "label": "Fail fast with clear messages",
                    "description": "Immediate error visibility. Easier debugging but more interruptions. Good for development."
                },
                {
                    "label": "Graceful degradation",
                    "description": "Continue operation with reduced functionality. Better UX but errors may go unnoticed."
                },
                {
                    "label": "Retry with exponential backoff",
                    "description": "Automatic recovery from transient failures. Adds complexity and potential latency."
                },
                {
                    "label": "Log and continue",
                    "description": "Silent failure recovery. Best for non-critical paths. Risk of hidden issues accumulating."
                }
            ]
        },
        {
            "text": "What testing level?",
            "options": [
                {
                    "label": "Unit tests only",
                    "description": "Fast feedback, isolated verification. Misses integration issues. Good for pure logic."
                },
                {
                    "label": "Integration tests",
                    "description": "Verify component interactions. Slower but catches real-world failures. Recommended for APIs."
                },
                {
                    "label": "Full E2E suite",
                    "description": "Complete user flow validation. Highest confidence but longest execution. Expensive to maintain."
                },
                {
                    "label": "Manual testing",
                    "description": "Skip automated tests initially. Fast development but manual verification burden. Technical debt."
                }
            ]
        },
        {
            "text": "Deployment strategy?",
            "options": [
                {
                    "label": "Feature flag rollout",
                    "description": "Deploy to all, enable gradually. Instant rollback. Requires flag infrastructure."
                },
                {
                    "label": "Canary deployment",
                    "description": "Small user percentage first. Catch issues early. Needs monitoring and rollback automation."
                },
                {
                    "label": "Blue-green deployment",
                    "description": "Full environment switch. Zero downtime. Doubles infrastructure cost temporarily."
                },
                {
                    "label": "Direct deployment",
                    "description": "Immediate production rollout. Fastest but highest risk. Acceptable for low-traffic features."
                }
            ]
        }
    ]
)
```

### Anti-Pattern: Text-Based Menus

**Avoid:**
```
Please choose:
1. Fast
2. Cheap
3. Good quality

Which do you prefer?
```

**Problems:**
- No context about trade-offs
- Binary thinking (can't combine attributes)
- Vague options without implications
- No guidance toward optimal choice

### When to Use Maximal Questions

**Good fit:**
- Request admits multiple valid interpretations
- Choices meaningfully affect implementation approach
- Actions carry risk or are difficult to reverse
- User preferences influence trade-offs
- Scope clarification prevents rework

**Poor fit:**
- Decisions are obvious from context
- Only one reasonable approach exists
- User already provided detailed requirements
- Questions would annoy rather than clarify

### Implementation Guidelines

**Option descriptions should include:**
1. What this choice means concretely
2. Primary trade-off or cost
3. When this choice makes sense
4. What happens if this choice is wrong

**The recommended flag signals:**
- Optimal choice given typical constraints
- Not forcing—user can override
- Guides users unfamiliar with domain

**Multi-select enables:**
- "Performance AND simplicity" combinations
- "All of these except X" selections
- Prioritization without forced ranking

**Sources:** [cc-mirror orchestration tools](https://raw.githubusercontent.com/numman-ali/cc-mirror/main/src/skills/orchestration/references/tools.md), [AskUserQuestion pattern documentation](https://raw.githubusercontent.com/numman-ali/cc-mirror/main/src/skills/orchestration/SKILL.md)

---

## Leading Questions

- How do you write tool descriptions that work for both humans and LLMs?
- When should you split one complex tool into multiple simple ones?
- What parameters should be required vs. optional? How do you decide?
- How do naming conventions affect tool selection accuracy?
- What makes a tool description actionable vs. confusing?

---

## Connections

- **To [Tool Selection](2-tool-selection.md):** Design choices directly impact selection accuracy
- **To [Prompt](../2-prompt/_index.md):** Tool descriptions are prompts themselves—see [Model-Invoked vs. User-Invoked Prompts](../2-prompt/_index.md#model-invoked-vs-user-invoked-prompts)
- **To [Scaling Tools](4-scaling-tools.md):** Good design becomes critical when managing dozens of tools
- **To [Orchestrator Pattern](../6-patterns/3-orchestrator-pattern.md):** AskUserQuestion maximal pattern demonstrates rich clarification as coordination tool. Orchestrators use structured questioning before delegation to absorb complexity and radiate simplicity.
