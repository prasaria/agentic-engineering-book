---
description: Add more leading questions to an existing entry based on a topic or angle
allowed-tools: Read, Edit, Glob
argument-hint: <path-to-file> <topic/angle>
---

# Expand Entry

Add more leading questions to an existing knowledge base entry, focused on a specific topic or angle.

## Workflow

1. Parse `$ARGUMENTS` to extract:
   - File path (relative to knowledge base root, e.g., `foundations/prompt` or full path)
   - Topic/angle to expand on

2. Read the existing file

3. Analyze current questions to avoid duplication

4. Generate 3-5 new leading questions that:
   - Focus specifically on the requested topic/angle
   - Build on (don't repeat) existing questions
   - Maintain the interrogative, thought-provoking style
   - Are grounded in practical experience

5. Add new questions under a new subsection (e.g., "### On <topic>")

6. Update `last_updated` in frontmatter

7. Report what was added
