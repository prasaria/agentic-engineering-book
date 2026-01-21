---
description: Review an entry and suggest additional questions based on what's been written
allowed-tools: Read, Edit
argument-hint: <file-path>
---

# Review Questions

After you've written content in an entry, this command analyzes what you wrote and suggests follow-up questions to go deeper.

## Expertise

*This section contains domain knowledge that evolves over time. Updated by improve commands.*

### Question Types That Work
- Specificity prompts: "Can you give an example from a real project?"
- Edge cases: "When does this pattern break down?"
- Comparative: "How does this differ from [related concept]?"
- Causal: "What causes this to happen? What are the second-order effects?"
- Temporal: "Has your thinking on this changed? Why?"

### Effective Follow-ups
- Point to gaps without being prescriptive about how to fill them
- Questions that make you pause and think are better than ones with obvious answers
- Challenge assumptions gently - "Is this always true or just in certain contexts?"
- Connect to other entries - "How does this relate to your thinking on X?"

### Anti-Patterns
- Avoid generic questions that could apply to any topic
- Don't ask questions you can answer yourself - let the author discover
- Don't overwhelm with too many questions - 2-3 per section maximum
- Avoid "yes/no" questions - use "how/why/when" instead
- Don't ask about things that are intentionally left unexplored

## Workflow

1. Read the specified file

2. Identify sections where you've written substantive content (not just the template)

3. For each substantive section:
   - Analyze the claims, insights, or experiences described
   - Generate 2-3 follow-up questions that:
     - Push for more specificity ("Can you give an example?")
     - Explore edge cases ("What about when X?")
     - Challenge assumptions ("Is this always true?")
     - Connect to other concepts ("How does this relate to Y?")

4. Present questions organized by section

5. Ask which questions to add to the entry

6. For approved questions, add them under the relevant section with a "### Follow-up" heading

7. Update `last_updated` in frontmatter
