---
name: draft-section
description: Draft or rewrite a section of an mrphys manuscript (Introduction, Theory, Methods, Results, Discussion, Conclusion, abstract) in the group's house style, from notes, an outline, bullet points, results or an existing rough draft. Use when the user asks to write, draft, expand, or rewrite part of a paper.
---

# Draft a manuscript section in group style

## Before writing
1. Read `../../references/style-guide.md` (relative to this skill's directory) in full. It overrides your
   default writing habits wherever they conflict. Then read the category file
   `../../references/styles/<category>.md` for the paper's `category:` (from its `CLAUDE.md`; if none is
   given, infer it from the paper and say which you used), and `../../references/venues/<venue>.md` if one
   exists. The more specific file wins. Rules marked **[decided]** are group decisions: apply them unless
   the paper's `CLAUDE.md` or the venue explicitly requires otherwise.
2. Read the example file for the requested section, `../../references/exemplars/<category>/<section>.md`
   (e.g. `reconstruction/introduction-aims.md`, `segmentation/limitations.md`). If the category has no file
   for that section, use the other category's. Match the structure, moves, sentence length and level of
   detail, not the content, and apply each excerpt's "Do differently now" note.
3. Read the paper's own `CLAUDE.md` if present: target journal, key claims, notation, file locations.
   Paper-specific notation overrides the general style guide.
4. Find the inputs: the user's notes/outline, existing `.tex` for neighbouring sections, the `.bib` file,
   and figure files or captions referenced by this section.

If the target journal, the section, or the core claim is unclear and cannot be found in the files, ask
one concise question before drafting.

## Writing rules
- Write LaTeX that drops into the existing manuscript: same macros, `\cite{}` keys, `\ref{}` labels.
- **Cite only keys that exist in the project's `.bib`.** Where a citation is needed and none fits, insert
  `\cite{TODO:<short description>}` rather than inventing a reference.
- Do not invent numbers, parameters, or results. Use `\todo{...}` (or `[TODO: ...]` if no todo package is
  loaded) for anything the inputs do not supply — scan parameters, subject counts, statistics.
- Keep claims within what the results support; follow the hedging rules in the style guide.

## After writing
1. Run the deterministic checks on the edited file:
   `python3 ../../scripts/lint_tex.py <file.tex>` (path relative to this skill's directory) and fix what it reports.
2. Give the user a short note: what was drafted, every `TODO` left in, and any place where you departed
   from the outline and why.
