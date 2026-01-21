Generate the TABLE_OF_CONTENTS.md file by scanning all chapter files.

## Instructions

1. Find all .md files under chapters/ and appendices/ directories
2. Read the frontmatter from each file to extract:
   - title
   - part (number)
   - part_title
   - chapter (number)
   - section (number)
   - order (sort key like 1.2.0)
3. Sort entries by their `order` field
4. Generate a formatted TABLE_OF_CONTENTS.md with:
   - Parts as major sections (## Part 1: Foundations)
   - Chapters as subsections (### Chapter 1: The Four Pillars)
   - Sections as list items with links

## Output Format

```markdown
# Table of Contents

## Part 1: Foundations

### Chapter 1: Foundations
- [Foundations](chapters/1-foundations/_index.md)
- [Twelve Leverage Points](chapters/1-foundations/1-twelve-leverage-points.md)

### Chapter 2: Prompt
- [Prompt](chapters/2-prompt/_index.md)
...
```

## Notes

- Use relative paths from the repo root for all links
- Group by part_title, then by chapter number
- Section 0 files (_index.md) should show as the chapter entry
- Sections 1+ show as indented list items under the chapter
- Write the result to TABLE_OF_CONTENTS.md at the repo root
