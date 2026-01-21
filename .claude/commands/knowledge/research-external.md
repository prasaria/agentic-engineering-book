---
description: Research external sources for book content updates using parallel specialized agents
allowed-tools: Task, Read, Write, Glob, Grep, Bash(date)
argument-hint: <research topic> [--date-range <natural language or YYYY-MM-DD:YYYY-MM-DD>]
---

# Research External Sources

Investigate external sources (official documentation, academic papers, practitioner articles) to identify learnings relevant to the agentic engineering book. Spawns specialized researcher agents in parallel to fetch and analyze content from multiple source types, then synthesizes findings into actionable book content update recommendations with citations.

## Input Format

`$ARGUMENTS` contains the research topic and optional date range. Examples:
- `tool calling patterns in production systems`
- `multi-agent orchestration --date-range last 3 months`
- `context window management --date-range last 6 months`
- `RAG patterns --date-range 2024-01-01:2024-12-31`
- `retrieval-augmented generation patterns --date-range last year`

**Supported date range formats:**
- Natural language: `last 3 months`, `last 6 months`, `last year`, `last 2 weeks`
- Explicit dates: `YYYY-MM-DD:YYYY-MM-DD` (start:end)

## Workflow

1. **Get Today's Date**
   - Run `date +%Y-%m-%d` to get the current date
   - This anchors all relative date calculations

2. **Parse Arguments**
   - Extract research topic from `$ARGUMENTS`
   - Check for `--date-range` flag
   - If date range is natural language, convert to explicit dates:
     - `last N months` → calculate start date as N months before today
     - `last N weeks` → calculate start date as N weeks before today
     - `last year` → calculate start date as 12 months before today
   - End date defaults to today if not specified
   - Validate: start < end, end not in future

3. **Create cache directory** if needed:
   ```
   .claude/.cache/research/external/
   ```

4. **Spawn coordinator agent** using Task tool:
   ```
   Task(
     subagent_type: "external-research-coordinator-agent",
     prompt: """
     Research the following topic across external sources:

     Topic: {research_topic}
     Date Range: {date_range or "none"}

     Coordinate parallel research across:
     1. Official documentation (Google ADK, Claude Code SDK, OpenAI, Anthropic)
     2. Academic papers (arxiv.org, Google Scholar)
     3. Recent articles and practitioner blogs

     Generate comprehensive report with gap analysis and actionable recommendations.
     """
   )
   ```

5. **Wait for completion** and receive synthesis report

6. **Save research report** to cache:
   ```
   .claude/.cache/research/external/{topic-slug}-{YYYY-MM-DD}.md
   ```

7. **Display final report** with:
   - Research summary
   - Findings by source type
   - Cross-source synthesis
   - Knowledge base gap analysis
   - Recommended updates with citations
   - Suggested `/knowledge:capture` commands

## Output Format

The command displays the coordinator's final synthesis report, which includes:

### Research Question
> {research topic}

### Findings by Source Type
- **Official Documentation**: Key concepts, APIs, patterns from docs
- **Academic Research**: Papers, methodologies, findings
- **Practitioner Insights**: Real-world experiences, production lessons

### Cross-Source Synthesis
- Consensus patterns appearing across multiple sources
- Unique insights from specific source types
- Contradictions and trade-offs

### Knowledge Base Gap Analysis
- Existing coverage mapped to book structure
- Identified gaps with supporting citations

### Recommended Updates
Priority-ranked update suggestions with:
- Target file path
- Action type (extend/new section/new entry)
- Insight phrased as learning
- Source citations
- Reasoning for priority

### Suggested Captures
Ready-to-use `/knowledge:capture` commands with citations

### All Citations
Numbered list of all URLs referenced

---

## Integration Points

**Follow-up Commands:**
- `/knowledge:capture "insight..."` - Capture recommended insights
- `/knowledge:link [file]` - Find connections with new knowledge
- `/book:toc` - Regenerate table of contents if new entries added
- `/orchestrators:knowledge` - Run full workflow for complex additions

**Research Report Usage:**
- Reports saved to `.claude/.cache/research/external/` for reference
- Citations formatted for easy addition to frontmatter
- Gap analysis informs content expansion priorities

---

*Research conducted across 3 source types: official documentation, academic papers, practitioner articles*
