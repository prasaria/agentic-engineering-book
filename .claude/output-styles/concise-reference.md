---
title: Concise Reference Style
description: Minimal, scannable format for quick lookups
created: 2025-12-25
tags: [output-style, reference, scannable]
---

# Concise Reference Style

Optimized for scanning and quick lookups. Maximum information density, minimal prose. Used for command lists, API references, and cheat sheets.

---

## When to Use

**Good fit**:
- Command references
- API documentation
- Cheat sheets
- Quick reference cards
- Tables of contents

**Poor fit**:
- Conceptual explanations
- Tutorials
- Narrative content
- Exploratory writing

---

## Voice Characteristics

**Tone**: Neutral and terse
**POV**: Fragments acceptable (no full sentences needed)
**Sentence Structure**: Minimal—lists and tables preferred
**Technical Level**: Assumes familiarity

---

## Structural Conventions

### Prefer Tables

Tables provide maximum information density for comparisons:

| Command | Description | Example |
|---------|-------------|---------|
| `/do <req>` | Universal entry | `/do add expertise.yaml` |
| `/knowledge:capture <insight>` | Store learning | `/knowledge:capture "pattern X"` |

### Use Definition Lists

For term-definition pairs:

**Term**
: Brief definition

**Another Term**
: Another definition

### Minimal Descriptions

No full paragraphs—fragments are fine:

```markdown
## Commands

- `/book:toc` - Regenerate table of contents
- `/book:chat <q>` - Query book content
- `/knowledge:self-improve <ch>` - Validate expertise
```

### Group Related Items

Use headers to create scannable sections:

```markdown
## Book Management
- `/book:toc` - Table of contents
- `/book:chat` - Conversational queries

## Knowledge Management
- `/knowledge:capture` - Store insights
- `/knowledge:expand` - Add questions
```

---

## Voice Examples

### Good Example: Command Reference

```markdown
## Slash Commands

### Primary Interface
- `/do <requirement>` - Universal entry point

### Book Management
- `/book:toc` - Regenerate TABLE_OF_CONTENTS.md
- `/book:chat <question>` - Conversational queries

### Knowledge
- `/knowledge:capture <insight>` - Store learning
- `/knowledge:expand <file> <topic>` - Add questions
- `/knowledge:self-improve <chapter>` - Validate expertise
```

### Good Example: Configuration Options

| Model | Speed | Cost | Use Case |
|-------|-------|------|----------|
| Haiku | Fast | Low | Simple tasks (test first) |
| Sonnet | Medium | Medium | Balanced (default) |
| Opus | Slow | High | Complex reasoning |

---

## Anti-Examples

### Too Much Prose

```markdown
## Model Selection Commands

When you need to select a model for your agent, you have several options
available. The model selection process is important because it affects both
the quality of results and the cost of operation. Here are the commands you
can use to help with model selection...
```

**Why this fails**: Excessive prose before useful information.

### Verbose Descriptions

```markdown
## Commands

- `/book:toc` - This command will regenerate the table of contents file by scanning all chapter files and extracting their frontmatter metadata to build a hierarchical structure
```

**Why this fails**: Description too long for quick scanning.

---

## Formatting Checklist

- [ ] Tables for comparisons
- [ ] Lists for sequences/options
- [ ] Fragments acceptable (no prose)
- [ ] Maximum information density
- [ ] Scannable structure
- [ ] Grouped by category
- [ ] Consistent formatting

---

## Reference

**Exemplar Content**:
- `CLAUDE.md` - Concise codebase reference
- `.claude/commands/README.md` - Command catalog
- `TABLE_OF_CONTENTS.md` - Book structure
