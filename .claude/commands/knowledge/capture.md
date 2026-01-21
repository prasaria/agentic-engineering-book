---
description: Quickly capture a learning or insight and store it in the appropriate location in the book
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
argument-hint: <insight or learning>
---

# Capture Learning

Quickly capture an insight or learning and store it in the appropriate chapter/section, maintaining consistent tone and structure.

## Input Format

`$ARGUMENTS` contains the raw insight/learning. Examples:
- "ReAct loops work better when you explicitly separate reasoning from action in the prompt"
- "Claude tends to over-explain when given vague stopping conditions - be explicit about when to stop"
- "Multi-agent systems need clear handoff protocols or context gets lost between agents"

## Expertise

*This section contains domain knowledge that evolves over time. Updated by improve commands.*

### Location Selection
- Prompt-related insights often belong in `structuring.md` rather than `prompt.md`
- Tool insights split between design (foundations) and usage (practices)
- If debating between patterns/ and practices/, prefer practices/ for "how to" and patterns/ for "what is"
- Journal entries are underused - encourage when insight is exploratory or time-specific

### Extending vs Creating
- Search existing files first - most insights extend rather than create
- New files only when topic is truly distinct (not just a subsection)
- Seedlings should start minimal - resist the urge to flesh out prematurely
- When extending, find the natural section - don't append to bottom

### Tone Matching
- "I've found" refers to the knowledge base author, not the agent executing the command
- Preserve rough edges and incomplete thoughts - this isn't documentation
- Questions are first-class content - don't feel pressure to answer everything
- Terse is good when it captures the essence

### Anti-Patterns
- Don't create stub files with "TODO" sections - better to capture in existing entry
- Avoid promoting insights to top-level files prematurely
- Don't sanitize personal voice into generic technical writing
- Don't timestamp every sentence - only when context matters

## Workflow

1. **Get current date** using `date +%Y-%m-%d` for timestamps

2. **Parse the insight** from `$ARGUMENTS`:
   - Identify the core concept (what was learned)
   - Identify the domain (which pillar or area it relates to)
   - Extract any specific examples or context provided

3. **Determine the appropriate location** by mapping to book structure:

   | If the insight relates to... | Store in... |
   |------------------------------|-------------|
   | Instructing agents, prompt structure | `foundations/prompts/` |
   | Model capabilities, behavior | `foundations/model/` |
   | Context management, RAG, memory | `foundations/context/` |
   | Tool design, MCP, function calling | `foundations/tools/` |
   | ReAct, multi-agent, HITL patterns | `patterns/` |
   | Debugging, evaluation, production | `practices/` |
   | Specific tools (Claude Code, etc.) | `tools/` |
   | Thinking frameworks | `mental-models/` |
   | Doesn't fit elsewhere / time-specific | `journal/` |

4. **Check if a relevant entry exists**:
   - Use `Glob` to find potential matches in the target directory
   - Use `Grep` to search for related concepts in existing files
   - Read the most relevant file(s) to understand current content

5. **If adding to existing entry**:
   - Find the most appropriate section for the insight
   - Add the insight with a timestamp: `*[YYYY-MM-DD]*: Your insight here`
   - Match the existing tone and style (direct, practical, first-person where appropriate)
   - Update `last_updated` in frontmatter to current date
   - If adding to a "growing" entry, consider if content is substantial enough to note

6. **If creating new entry** (only when no existing entry fits):
   - Create with proper frontmatter:
     ```yaml
     ---
     title: Descriptive Title
     description: One-line summary
     created: YYYY-MM-DD
     last_updated: YYYY-MM-DD
     tags: [relevant, tags]
     ---
     ```
   - Start with the insight as the seed content
   - Add 2-3 leading questions that the insight raises
   - Keep it minimal - new entries are meant to grow

7. **If the insight is time-specific or personal reflection**:
   - Store in `journal/YYYY-MM-DD.md`
   - Create or append to the daily journal entry
   - Format: `## HH:MM - Brief Title\n\nInsight content`

## Tone Guidelines

Match the book's voice:
- Direct and practical, not academic
- First-person where appropriate ("I've found that...") - this refers to the knowledge base author, not the agent
- Grounded in real experience, not theoretical
- Questions are valued as much as answers
- Avoid over-explaining - trust the reader

## Timestamp Format

- In frontmatter: `YYYY-MM-DD`
- Inline additions: `*[YYYY-MM-DD]*:` prefix
- Journal entries: `## HH:MM - Title` headers

## Output

Report back with:
- **Location**: Where the insight was stored
- **Action**: Added to existing entry / Created new entry / Added to journal
- **Context**: Brief note on why this location was chosen
- **Connections**: Any related entries that might benefit from linking (don't auto-link, just note)
