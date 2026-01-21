---
title: Context as Code
description: Treat agent knowledge like software, not documents
created: 2025-12-10
last_updated: 2025-12-10
tags: [mental-models, context, knowledge-management, versioning]
part: 3
part_title: Perspectives
chapter: 8
section: 4
order: 3.8.4
---

# Context as Code

**Treat agent knowledge like software, not documents.**

This extends the "Specs as Source Code" mental model beyond specifications to all context artifacts: knowledge bases, expertise files, tool descriptions, and system prompts. If it shapes agent behavior, it's source code.

---

## Your Mental Model

**Knowledge artifacts are source code.** Version control them, test them, refactor them, and document them with the same rigor you apply to Python or JavaScript. When you edit an agent's context without tracking what changed and why, you're cowboy-coding in production.

Knowledge bases aren't documentation—they're the runtime instructions that determine agent behavior. Treating them as "just text files" is like treating your application code as "just text files" and editing it in Notepad without version control.

---

## What This Looks Like in Practice

The ACE playbook format exemplifies context as code:

```
[str-00001] helpful=5 harmful=0 :: Use structured output for complex tasks
[cal-00003] helpful=8 harmful=0 :: Token cost = (input + output) * rate
[mis-00004] helpful=6 harmful=0 :: Don't retry on rate limits without backoff
[con-00002] helpful=7 harmful=0 :: Context window = working memory
[too-00001] helpful=9 harmful=0 :: Grep before Edit to avoid blind writes
```

Each line is:
- **Uniquely identified** (`[prefix-ID]`) - enables precise references, easy refactoring
- **Performance tested** (`helpful=X harmful=Y`) - like unit tests for knowledge
- **Category-organized** (`str-`, `cal-`, `mis-`, `con-`, `too-`) - modular design
- **Self-describing** (the content itself explains what it does)

---

## Software Engineering Patterns Applied to Context

### Version Control: Track Changes, Enable Rollback

```bash
# Traditional documentation
docs/agent-knowledge.md  # edited directly, no history

# Context as code
git log --oneline knowledge/strategies.md
a3f2b1c Add retry strategy for transient failures
e4d5c6f Remove deprecated authentication approach
f7g8h9i Refactor error handling strategies

git diff e4d5c6f..a3f2b1c knowledge/strategies.md
- [str-00015] helpful=2 harmful=3 :: Use basic auth for API calls
+ [str-00015] helpful=8 harmful=0 :: Use OAuth2 with refresh tokens
```

When agent behavior regresses, you can `git bisect` to find which knowledge change caused it.

### Testing: Helpful/Harmful Counters as Unit Tests

```
# Before testing
[str-00023] :: Always validate user input

# After testing (knowledge has test results)
[str-00023] helpful=12 harmful=0 :: Always validate user input
```

The counters are like test pass/fail metrics:
- `helpful > 0, harmful = 0` → Proven valuable, keep it
- `helpful = 0, harmful > 0` → Causes problems, remove or refactor
- `helpful > 0, harmful > 0` → Context-dependent, needs conditions

You can track these over time like code coverage metrics.

### Modular Organization: Category Prefixes, Unique IDs

```
strategies/
  str-00001.md  # High-level approaches
  str-00002.md
calculations/
  cal-00001.md  # Formulas and computations
  cal-00003.md
mistakes/
  mis-00001.md  # Anti-patterns to avoid
  mis-00004.md
concepts/
  con-00001.md  # Domain knowledge
  con-00002.md
tools/
  too-00001.md  # Tool usage patterns
  too-00005.md
```

Just like code modules, categories enable:
- **Focused loading**: Only load relevant categories for specific tasks
- **Dependency tracking**: `[str-00012]` references `[con-00003]` and `[too-00007]`
- **Easier refactoring**: Move entries between categories without breaking references

### Refactoring: Semantic Deduplication

```
# Before refactoring (duplication)
[str-00008] :: For database queries, use connection pooling
[str-00015] :: When connecting to databases, use a connection pool
[too-00023] :: Database access should use connection pooling

# After refactoring (DRY principle)
[str-00008] helpful=15 harmful=0 :: Use connection pooling for database access
# References: too-00023, db-architecture.md
```

Like code refactoring, you extract common patterns, eliminate redundancy, and maintain a single source of truth.

### Documentation: Each Entry is Self-Describing

```
# Weak (requires external context)
[str-00042] :: Use the pattern

# Strong (self-contained)
[str-00042] helpful=6 harmful=0 :: For multi-step workflows, use plan-build-review pattern to separate planning from execution
```

Like good function names and docstrings, each knowledge entry should be understandable in isolation.

---

## When to Apply This Model

### Good Fit

**Production agent systems**: When agents run in production, their knowledge determines user-facing behavior. Treat it with production code rigor.

**Multi-agent systems**: When knowledge is shared across multiple agents, version control and testing prevent one agent's changes from breaking another.

**Evolving domains**: When knowledge needs frequent updates (new APIs, changing policies), treating context as code makes evolution traceable and reversible.

**Team collaboration**: When multiple people contribute to agent knowledge, version control and structure prevent conflicts and enable review.

### Poor Fit

**Prototype exploration**: When you're still figuring out what knowledge the agent needs, heavyweight structure slows discovery. Start informal, formalize later.

**Static, finished systems**: If the knowledge is complete and won't change, the overhead of treating it as source code isn't justified.

**Single-person, short-lived projects**: For quick experiments, simple text files work fine. Add structure when the project grows.

---

## The Continuum: From Documents to Code

```
Documents                                                    Code
    │                                                         │
    ├─ Plain text notes (no structure)                       │
    ├─ Markdown with sections (light structure)              │
    ├─ Structured markdown with metadata (ACE playbook)      │
    ├─ Machine-parseable format with schema (JSON/YAML)      │
    └─ Formal specifications with validation (contracts) ────┘
```

You don't need to jump straight to the "code" end. The ACE playbook hits a sweet spot: human-readable markdown with just enough structure (IDs, counters, categories) to enable software engineering practices.

---

## Implications

### Knowledge Reviews Like Code Reviews

```markdown
# PR: Update authentication strategies

Changes to knowledge/strategies/:
  - [str-00042] helpful=2 harmful=5 :: Use basic auth
  + [str-00042] helpful=8 harmful=0 :: Use OAuth2 with PKCE flow
  + [str-00058] helpful=0 harmful=0 :: For mobile apps, use refresh token rotation

Reviewer: "str-00042 improvement looks good. For str-00058, have we tested
harmful=0? Refresh token rotation can cause issues if not handled correctly."
```

### Knowledge Regression Testing

```python
def test_agent_follows_knowledge():
    """Verify agent applies knowledge correctly."""
    agent = load_agent_with_knowledge("knowledge/strategies.md")

    # Test that str-00042 is applied
    response = agent.handle_auth_request(mock_request)
    assert response.auth_method == "OAuth2"
    assert response.uses_pkce == True

    # Increment helpful counter if successful
    increment_helpful("str-00042")
```

### Knowledge Metrics

```
# Knowledge health dashboard
Total entries: 247
  Proven (helpful > 5, harmful = 0): 89 (36%)
  Untested (helpful = 0, harmful = 0): 143 (58%)
  Problematic (harmful > 0): 15 (6%)

Recent changes (last 7 days):
  + 12 new entries
  ~ 8 modified entries
  - 3 removed entries

Coverage by category:
  str- (strategies): 67 entries
  cal- (calculations): 23 entries
  mis- (mistakes): 34 entries
  con- (concepts): 89 entries
  too- (tools): 34 entries
```

---

## Common Pitfalls

### Over-Engineering Early

**Problem**: Creating elaborate versioning and testing infrastructure before you know what knowledge the agent needs.

**Solution**: Start with simple markdown. Add structure (IDs, categories, counters) when you have enough entries that organization becomes painful. Add testing when you have enough history to know what "helpful" looks like.

### Treating All Context Equally

**Problem**: Applying heavy structure to ephemeral context that doesn't need it (one-off prompts, temporary instructions).

**Solution**: Distinguish between:
- **Core knowledge** (long-lived, reused, tested) → Treat as code
- **Task-specific context** (one-off, temporary) → Keep lightweight
- **Generated content** (can be regenerated) → Don't version control

### Losing the Human-Readable Aspect

**Problem**: Making context so structured and formal that humans can't easily read and edit it.

**Solution**: The ACE playbook maintains readability. Avoid formats that require parsing tools to understand. Markdown with light structure is the sweet spot.

---

## Connections

- **To [Specs as Source Code](3-specs-as-source-code.md)**: Context as code extends this mental model beyond specs to all knowledge artifacts
- **To [Knowledge Evolution](../7-practices/6-knowledge-evolution.md)**: Practical patterns for evolving knowledge bases over time
- **To [Self-Improving Experts](../6-patterns/2-self-improving-experts.md)**: Expertise files are context that agents execute—they're source code for behavior
- **To [Context](../4-context/_index.md)**: The mechanics of how context enters the agent's working memory
