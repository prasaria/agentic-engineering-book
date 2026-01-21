---
title: Tool Design
description: Principles for creating well-designed tools that agents can use effectively
created: 2025-12-10
last_updated: 2025-12-10
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
