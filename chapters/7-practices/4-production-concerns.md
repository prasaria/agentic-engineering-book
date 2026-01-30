---
title: Production Concerns
description: Running agents reliably at scale
created: 2025-12-08
last_updated: 2025-12-10
tags: [practices, production, reliability, operations, monitoring, hooks]
part: 2
part_title: Craft
chapter: 7
section: 4
order: 2.7.4
---

# Production Concerns

Demo agents are easy. Production agents are hard. This is where the craft lives.

---

## Connections

- **To [Evaluation](2-evaluation.md):** How does prod monitoring relate to eval?
- **To [Debugging](1-debugging-agents.md):** How do you debug production issues?
- **Human-in-the-Loop:** How do humans fit into production operations?

---

## Production War Stories

*Document production incidents, what happened, what you learned:*

### Multi-Agent Production Lessons

*[2025-12-09]*: Hard-won lessons from practitioners running multi-agent systems at scale (including a 400K LOC codebase). These patterns emerge repeatedly across production deployments.

**Context Switching Kills Productivity**

"It is better to start with fresh context on a fresh problem rather than using an existing context." Don't try to salvage a degraded agent—boot a new one. The cost of context confusion exceeds the cost of restarting. In multi-agent systems, this is even more important: let each subagent start fresh and focused rather than inheriting accumulated state.

**CLAUDE.md as Convention Encoding**

Document project conventions in CLAUDE.md. Agents read this to understand boundaries, patterns, and expectations. For large codebases, this is essential—agents can't infer all conventions from code alone. Investing time in clear specs saves 10× in agent iterations. The alternative is watching agents repeatedly violate conventions you thought were obvious.

**Lifecycle Hooks for Control**

Wire hooks at critical transitions:
- **PreToolUse**: Validate commands before execution (catch dangerous operations)
- **SubagentStop**: Record outputs, promote artifacts, log what was accomplished
- **ErrorEscalation**: Notify human overseers when agents fail or hit edge cases

These hooks provide observability and control points without requiring constant human monitoring.

**The Orchestrator Observes Itself**

*[2025-12-09]*: Hooks enable a powerful pattern—the orchestrator becomes self-aware of its own operations. PreToolUse and PostToolUse hooks capture every Claude Code action, creating real-time visibility into agent behavior.

This enables:
- **Cost Tracking**: Measure token consumption per tool invocation, per subagent, per task
- **Audit Trails**: Log every agent action with context—who did what, when, and why
- **Real-Time Monitoring**: Detect patterns, anomalies, or runaway agents as they happen
- **Platform Self-Awareness**: The system knows what it's doing while it's doing it

Traditional software logs after the fact. Hooks let platforms observe themselves *during execution*. This is the foundation for production-grade agent operations—you can't manage what you can't measure, and you can't measure what you can't observe.

**Implementation Pattern**: Wire PostToolUse hooks to write structured logs (JSON) containing tool name, parameters, results, duration, and cost estimates. Aggregate these logs for operational dashboards showing agent activity in real-time.

**See Also**:
- [Tool Use: Tool Restrictions as Security Boundaries](../5-tool-use/3-tool-restrictions.md#tool-restrictions-as-security-boundaries) — How hooks integrate with tool permission boundaries
- [Claude Code Hooks Documentation](/.claude/ai_docs/claude-code/hooks.md) — Complete technical reference

**Test-First Discipline**

The test-first pattern works remarkably well with multi-agent systems:
1. Dedicate a test-writing subagent to create tests that currently fail
2. Verify the tests actually fail (don't skip this)
3. Implementer subagent makes tests pass without changing tests
4. Review subagent validates the changes

This creates natural quality gates and makes progress measurable. Agents write better code when following this discipline—they have clear success criteria.

**Dedicated Review Gate**

Maintain a dedicated code-review subagent as a final gate. Configure it to enforce:
- Linting and style conventions
- Complexity bounds (cyclomatic complexity, file length)
- Security checks (no secrets, no dangerous patterns)

This catches issues before they reach humans, and the reviewing agent doesn't have the sunk-cost bias of having written the code.

**Documentation Investment**

Time spent on clear specs saves 10× in agent iterations. If you're watching agents go in circles, the problem is usually upstream in the specification, not in the agents themselves. Write clear specs once, save debugging time forever.

**Opus 4.5 for Orchestration**

Practitioner consensus: Opus 4.5 is particularly effective at managing teams of subagents. It handles the coordination overhead well and produces more coherent multi-agent workflows than smaller models used for orchestration.

**Sources**: [How I Manage 400K Lines of Code with Claude Code](https://blockhead.consulting/blog/claude_code_workflow_july_2025), [Claude Agent SDK Best Practices](https://skywork.ai/blog/claude-agent-sdk-best-practices-ai-agents-2025/), [Multi-Agent Orchestration: Running 10+ Claude Instances](https://dev.to/bredmond1019/multi-agent-orchestration-running-10-claude-instances-in-parallel-part-3-29da)

### Google Cloud Deployment Gotchas

*[2025-12-09]*: Hard-won lessons from practitioners deploying Google ADK agents to production. These are framework-agnostic lessons that apply broadly—they just happen to surface most visibly with ADK on Google Cloud.

**Infrastructure Permissions**

Enable Cloud Run Admin API *before* deployment. Missing permissions fail with cryptic errors that don't obviously point to the permission issue. This isn't ADK-specific—it's a Google Cloud pattern. Before deploying anything, verify required APIs are enabled.

**Environment Variable Naming**

Generic environment variable names conflict with system variables. `MODEL` is particularly problematic—it conflicts with Google Cloud's internal variables.

The fix: prefix everything. Use `GEMMA_MODEL_NAME` instead of `MODEL`, `ADK_API_KEY` instead of `API_KEY`. This namespacing prevents silent conflicts that cause mysterious runtime behavior.

**MCP Session Affinity**

MCP connections are stateful. At scale, this means:
- Load balancers need session affinity (sticky sessions)
- Connection loss requires reconnection handling
- Horizontal scaling is constrained by state distribution

Plan load balancing accordingly. Stateless is easy; stateful requires architecture decisions.

**Asyncio Everywhere**

ADK and MCP both assume async-first Python. Common mistakes:
- Writing sync tool implementations (blocks the event loop)
- Forgetting `await` on async calls
- Not using async context managers for connections

Default to `async def` for everything. Sync code in an async codebase serializes naturally parallel operations—you lose the concurrency benefits without obvious errors.

**The "Works Locally, Fails in Cloud" Pattern**

Local development hides many issues:
- Environment variable sources differ (local shell vs. Cloud Run secrets)
- Network topology changes (localhost vs. VPC)
- Permission models differ (local user vs. service account)

Always test in a staging environment that mirrors production. "It works on my machine" is particularly dangerous with agent systems where subtle environment differences cause behavioral changes.

**See Also**: [Google ADK: Production Lessons](../9-practitioner-toolkit/2-google-adk.md#production-lessons) — ADK-specific deployment experiences

