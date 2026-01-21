---
title: Tool Selection and Routing
description: How agents decide which tool to use and what causes selection failures
created: 2025-12-10
last_updated: 2025-12-10
tags: [tool-selection, routing, decision-making, tool-use]
part: 1
part_title: Foundations
chapter: 5
section: 2
order: 1.5.2
---

# Tool Selection and Routing

The agent has twenty tools available. Selection accuracy directly impacts task completion. When selection fails, the issue is typically unclear tool descriptions or too many similar-looking options.

---

## Your Mental Model

**Tool selection is prompt-driven reasoning.** The model doesn't "route" based on keywords—it reads tool descriptions and parameters like instructions, then decides which matches the task at hand. Poor selection usually means unclear tool descriptions or too many similar-looking options.

---

## Selection Mechanisms

### Description-Based Selection

The agent reads tool names and descriptions, matching them to the task requirements. This means:
- Tool names matter: `search_codebase` is clearer than `finder_v2`
- Descriptions must distinguish similar tools: "Search git history" vs. "Search current files"
- Parameter schemas signal intent: required `query` parameter suggests search-like behavior

### Context-Driven Filtering

Some patterns reduce the selection space:
- **Role-based restrictions**: Scout agents only see read-only tools (see [Tool Restrictions](3-tool-restrictions.md))
- **Dynamic discovery**: Rarely-used tools hidden until search reveals them (see [Scaling Tools](4-scaling-tools.md))
- **Skill activation**: Temporary tool access when domain-specific mode activates (see [Skills](5-skills-and-meta-tools.md))

---

## Common Selection Failures

### Overlapping Functionality

**Problem**: Two tools do similar things with subtle differences. Agent picks randomly.

**Example**:
- `read_file` - Reads entire file
- `read_file_section` - Reads specific lines

If descriptions don't clarify when to use each, the agent struggles.

**Fix**: Make the distinction explicit in descriptions:
- "Read entire file (use for files <500 lines)"
- "Read specific section by line numbers (use for large files or targeted inspection)"

### Too Many Options

**Problem**: 50+ tools overwhelm the selection process. Agent either picks wrong tool or spends excessive tokens evaluating options.

**Fix**: Use dynamic discovery (see [Scaling Tools](4-scaling-tools.md)) or role-based filtering to reduce visible tool count.

### Vague Descriptions

**Problem**: Tool description doesn't explain when NOT to use the tool.

**Example**: "Searches the database" - for what? Structured queries? Full-text search? Recent records?

**Fix**: Add context and boundaries:
- "Searches database via SQL queries. Use for structured lookups by ID, date range, or indexed fields. For full-text search, use `search_documents` instead."

---

## Improving Selection Accuracy

### Distinctive Naming

Use domain-specific prefixes when managing tool groups:
- `git_commit`, `git_push`, `git_log` (clear grouping)
- Not: `commit`, `push`, `log` (ambiguous without context)

### Comparison Tables in Context

When tools have overlapping use cases, provide selection guidance:

```markdown
| Tool | Use When | Don't Use When |
|------|----------|----------------|
| `search_files` | Finding files by name/path | Searching file contents |
| `grep_contents` | Searching within files | Finding files by name |
```

This can go in the main system prompt or in tool descriptions themselves.

### Constrain When Appropriate

**Don't default to "give the agent everything."** If a build agent doesn't need database access, don't provide database tools. Fewer tools = better selection.

---

## Leading Questions

- How do you measure tool selection accuracy in production?
- When should you merge similar tools vs. keep them separate?
- How does prompt caching affect tool selection overhead?
- What's the relationship between tool count and inference latency?
- Can you predict which tools an agent will struggle to select?

---

## Connections

- **To [Tool Design](1-tool-design.md):** Design determines selectionability
- **To [Tool Restrictions](3-tool-restrictions.md):** Restrictions are a selection optimization
- **To [Scaling Tools](4-scaling-tools.md):** Large tool sets require selection strategies
- **To [Prompt](../2-prompt/_index.md):** Tool descriptions follow prompt design principles
