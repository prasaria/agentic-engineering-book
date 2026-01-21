---
title: Practitioner Toolkit
description: Tools for agentic engineering with operational insights
created: 2025-12-08
last_updated: 2025-12-10
tags: [tools, software, toolkit, practitioner]
part: 3
part_title: Perspectives
chapter: 9
section: 0
order: 3.9.0
---

# Practitioner Toolkit

These entries document specific tools used in agentic engineering projects, capturing operational insights rather than reviews. The focus is on what works, what doesn't, and patterns discovered through production use.

---

## Tool Catalog

| Tool | Category | Description |
|------|----------|-------------|
| [Claude Code](1-claude-code.md) | Coding agent | Anthropic's CLI coding agent with subagent system, Skills, and hooks |
| [Google ADK](2-google-adk.md) | Agent framework | Multi-agent-first framework with workflow primitives and state management |

---

## Connections

- **To [Patterns](../6-patterns/_index.md):** Tool capabilities shape which patterns are practical. Orchestrator pattern, plan-build-review, and self-improving experts all depend on specific tool features.
- **To [Context](../4-context/_index.md):** Different tools implement context management differently—Claude Code's Skills use progressive disclosure, ADK uses persistent state with prefixes.
- **To [Tool Use](../5-tool-use/_index.md):** The tools documented here provide concrete implementations of tool use principles—MCP integration, tool restrictions, meta-tools.
