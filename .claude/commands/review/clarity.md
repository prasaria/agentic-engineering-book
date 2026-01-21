---
description: Review an entry for clarity and suggest improvements without changing your voice
allowed-tools: Read, Edit
argument-hint: <file-path>
---

# Review Clarity

Review an entry for clarity, coherence, and completeness. Suggest improvements while preserving your voice.

## Philosophy

This is YOUR book. The goal isn't to make it sound polished or "professional" - it's to make YOUR thinking clearer to YOUR future self.

## Expertise

*This section contains domain knowledge that evolves over time. Updated by improve commands.*

### Clarity Improvements That Work
- Replacing vague pronouns with specific nouns ("it" → "the agent")
- Adding a concrete example to abstract claims
- Breaking up run-on sentences that pack too many ideas
- Defining jargon the first time it appears in an entry

### Voice Preservation
- "I've found" and "In my experience" are features, not bugs
- Incomplete thoughts marked with "?" are valuable - don't resolve prematurely
- Lists and fragments are fine when they communicate efficiently
- Preserve hedging language ("seems", "maybe", "probably") - it's honest uncertainty

### When to Suggest Changes
- Ambiguity that will confuse future-you (e.g., "this approach" when multiple approaches discussed)
- Claims without grounding (e.g., "agents fail often" → "agents fail often when context exceeds 100k tokens")
- Sections that jump topics without transition
- Contradictions within the same entry

### Anti-Patterns
- Don't expand terse notes into paragraphs - some things are meant to be brief
- Don't remove sentence fragments that work ("Simple. Direct. Gets it done.")
- Don't formalize casual language ("gonna" → "going to" is usually wrong here)
- Don't add transitions when bullet points are clearer
- Don't suggest changes just to sound more "professional"

## Workflow

1. Read the specified file

2. Analyze for:
   - **Clarity**: Are ideas expressed in a way you'll understand later?
   - **Specificity**: Are claims backed by examples or just abstract?
   - **Coherence**: Do sections flow logically?
   - **Gaps**: Are there obvious missing pieces in the reasoning?
   - **Jargon**: Is terminology used consistently?

3. For each issue found, present:
   - The specific passage
   - What's unclear or could be improved
   - A suggested revision (as one option, not the only way)

4. Important: Do NOT:
   - Rewrite in a generic "AI" voice
   - Add unnecessary formality
   - Remove personality or rough edges that are intentional
   - Expand terse notes that are meant to be terse

5. Ask which suggestions to apply

6. Apply approved changes and update `last_updated`
