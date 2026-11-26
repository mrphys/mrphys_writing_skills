---
name: style-review
description: Review an mrphys manuscript or section (.tex) against the group's house style and report or apply concrete edits — notation, terminology, tense, abbreviations, units, structure, hedging, captions. Use when the user asks to check, polish, proofread, or "make this sound like us".
---

# Review a manuscript against group style

## Steps
1. Read `../../references/style-guide.md` (relative to this skill's directory), the category file
   `../../references/styles/<category>.md`, `../../references/venues/<venue>.md` if it exists, and the
   paper's `CLAUDE.md` if present. Rules marked **[decided]** are group decisions: flag departures from
   them unless the paper's `CLAUDE.md` or the venue overrides them.
2. Run the deterministic checks first:
   `python3 ../../scripts/lint_tex.py <files.tex>`.
   These findings are mechanical; include them but don't spend judgement on them.
3. Read the target text section by section and check it against each part of the style guide:
   voice/tense, notation consistency (including against the paper's own earlier definitions), abbreviation
   definitions, units and number formatting, section structure, figure/table references and captions,
   and claim strength.
4. Check things the linter cannot: logical flow between paragraphs, claims unsupported by the Results,
   Methods details a reader would need to reproduce the work, and inconsistencies between abstract, body
   and conclusion.

## Output
Unless the user asked you to apply the edits directly, report findings as a list ordered by importance:

```
<file>:<line> — <style-guide section> — <problem>
  suggested: <replacement text>
```

Group purely mechanical fixes (linter output, typography) at the end. Do not rewrite text that already
follows the guide just to change wording. If the user asked for edits to be applied, make them in the
`.tex` and then summarise the substantive changes only.
