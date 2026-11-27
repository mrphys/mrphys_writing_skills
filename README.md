# mrphys-writing

A Claude Code plugin for drafting and reviewing papers in the group's house style. It has two skills:

- **draft-section** writes or rewrites a section (Introduction, Methods, Results, Discussion,
  Conclusion, abstract) from your notes, an outline or a rough draft.
- **style-review** checks a manuscript against the group style guide and reports or applies fixes.

Both skills load the same style guide (`references/style-guide.md`), so changing the guide changes how
both of them behave.

---

## Part 1: Using the plugin

### 1. Install it (once)
In any Claude Code session:
```
/plugin marketplace add mrphys/mrphys_writing_skills
/plugin install mrphys-writing@mrphys
```
Restart Claude Code. To check it worked, run `/plugin`: `mrphys-writing` should be listed as installed.

To get the latest version after someone changes the style guide:
```
/plugin marketplace update mrphys
```

### 2. Set up each paper (once per paper)
Copy the template into the paper's repository (for example, an Overleaf project synced with git) as
`CLAUDE.md`:
```
cp templates/paper-CLAUDE.md ~/path/to/my-paper/CLAUDE.md
```
Then fill it in. The fields that matter most:

| Field | Why it matters |
|---|---|
| `category` | `reconstruction` or `segmentation`. Selects the category style file and the example paragraphs. |
| `venue` | Target journal. Journal requirements override group rules. |
| Core claims | What the paper must convince a reviewer of. Drafts are built around these claims. |
| Paper-specific notation | Symbols and terms defined in this paper. These override the general guide. |
| Files | Where the `.tex`, `.bib` and figures live. |

If `CLAUDE.md` is missing, the skills guess the category from the paper and tell you which one they used.

### 3. Draft a section
Start `claude` in the paper's folder and ask in plain language, for example:
```
Draft the Discussion from my notes in notes/discussion.md
Rewrite sections/introduction.tex in group style
Write the abstract for MRM from the current main.tex
```
or call the skill directly: `/mrphys-writing:draft-section`.

What to expect:
- LaTeX that fits into your manuscript, using your existing macros, `\cite{}` keys and `\ref{}` labels.
- It only cites keys that exist in your `.bib`. Where a reference is needed but none fits, it writes
  `\cite{TODO:<what is needed>}`. Search for `TODO:` before submitting.
- If the journal, the section or the main claim is unclear, it asks one question before drafting.

### 4. Review a manuscript
```
Style-review sections/methods.tex
Check main.tex against the group style and apply the edits
```
or `/mrphys-writing:style-review`.

By default you get a list ordered by importance, one item per problem:
```
sections/methods.tex:42 — Units — "1.5 T" should be "1.5T"
  suggested: ... at 1.5T ...
```
Ask it to "apply the edits" if you want the changes made in the file.

### 5. Run the linter on its own (optional, no Claude needed)
The mechanical checks (banned phrases, preferred spellings, acronyms used before they are defined) can
be run directly. It needs only standard Python:
```
python3 /path/to/mrphys_writing_skills/scripts/lint_tex.py main.tex sections/*.tex
```
Output lines look like `file:line: [rule] message`.

---

## Part 2: Modifying the plugin

### How the plugin is put together
| Path | What it is | Edit it when |
|---|---|---|
| `references/style-guide.md` | **The group style.** Loaded by both skills. Rules marked **[decided]** are group decisions. | You want to change how the group writes |
| `references/styles/<category>.md` | Rules that apply to one category only | A rule applies only to reconstruction or only to segmentation |
| `references/venues/<venue>.md` | Journal-specific rules (*no files written yet*) | Adding MRM, JCMR etc. Name the file after the `venue:` value in `CLAUDE.md` |
| `references/lint-rules.json` | Rules the linter checks automatically | A rule can be checked with a regex |
| `references/exemplars/<category>/<section>.md` | Model paragraphs from group papers, with notes on why each one is a good example | You want drafts to imitate a better paragraph |
| `references/open-questions.md` | Conventions the group has not settled, and the decisions made so far | Recording a new decision |
| `skills/*/SKILL.md` | Step-by-step instructions each skill follows | Changing what a skill *does*, not the style |
| `templates/paper-CLAUDE.md` | Per-paper setup file | Adding a field the skills should read |
| `.claude-plugin/plugin.json` | Plugin name and version | Every release |

The more specific file wins: paper `CLAUDE.md` > venue file > category file > `style-guide.md`.

### Common changes

**Change a style rule.** Edit `references/style-guide.md` (or the category file). Write each rule as the
rule itself, a short reason, and 1–2 example papers, the same way the existing rules are written. If it
was a group decision, mark it **[decided]** and record it in `references/open-questions.md`.

**Add a rule the linter checks.** Add an entry to `references/lint-rules.json`:
```json
"banned_phrases": [
  {"pattern": "\\bnovel\\b", "message": "Avoid 'novel'. State what is new."}
]
```
- `banned_phrases`: matched against lowercased text.
- `patterns`: case-sensitive regexes.
- `preferred_variants`: exact-text swaps, e.g. `{"use": "artifact", "instead_of": ["artefact"]}`.
- `acronyms_no_definition_needed`: acronyms that don't need defining (e.g. `MRI`).

Then test it on a real paper: `python3 scripts/lint_tex.py some-paper.tex`.

**Add an example paragraph.** Copy a paragraph *verbatim* from a published group paper into
`references/exemplars/<category>/<section>.md` with its **Why**, **Do differently now** and **Edited**
fields. See `references/exemplars/README.md`.

**Add a venue file.** Create `references/venues/<venue>.md` (e.g. `mrm.md`) with the journal's
requirements. Both skills will start using it for papers whose `CLAUDE.md` names that venue.

### Test your changes before publishing
Load your local copy instead of the installed version:
```
claude --plugin-dir /path/to/mrphys_writing_skills
```
or add the folder as a local marketplace:
```
/plugin marketplace add /path/to/mrphys_writing_skills
/plugin install mrphys-writing@mrphys
```
Then run both skills on a paper you know well and check that the change shows up.

### Publish a change
1. Make the change on a branch and open a pull request, so the group can agree on style changes.
2. Bump `version` in `.claude-plugin/plugin.json` (e.g. `0.1.0` → `0.2.0`).
3. After merging, group members run `/plugin marketplace update mrphys`.

---

## Part 3: Rebuilding the style guide from the group's papers (tools)

The style guide was built from the group's own papers, following `docs/style-guide-plan.md`. Use these
tools to add new papers, re-measure the corpus, or check whether a change to the guide improved the
drafts. Everything they produce goes into `corpus/`, which is git-ignored, because the papers may be under
copyright or unpublished.

### Setup
The linter, `build_corpus.py`, `profile_corpus.py` and `eval_drafts.py` need only standard Python. PDF
conversion needs PyMuPDF in a virtual environment:
```
python3 -m venv .venv && .venv/bin/pip install pymupdf
```
`profile_corpus.py` uses [pandoc](https://pandoc.org) to read LaTeX sources if it is installed
(`brew install pandoc`). Without pandoc it uses a cruder fallback.

### The pipeline
| Step | Command | Output |
|---|---|---|
| 1. Find papers | `python3 tools/build_corpus.py search --orcid <ORCID> --author "Surname AB" --arxiv-author "First Surname" --affiliation "University College London" --since 2018` | `corpus/index.csv` (metadata only, nothing downloaded) |
| 2. Suggest categories | `python3 tools/build_corpus.py classify` | `category` column in `index.csv` |
| 3. Check the list by hand | Edit `corpus/index.csv`: fix categories, set `keep=n` to drop rows, set `weight` (high = VM or JS first or last author), `version` and `holdout` | |
| 4. Download | `.venv/bin/python tools/build_corpus.py download [--category reconstruction ...]` | `corpus/epmc/`, `corpus/arxiv/` |
| 5. Convert PDF-only papers | `.venv/bin/python tools/build_corpus.py extract`, or for a single file `.venv/bin/python tools/pdf_text.py paper.pdf` | `paper.md` next to each PDF |
| 6. Measure the style | `python3 tools/profile_corpus.py [--category reconstruction]` | `corpus/analysis/profile.md` and `profile.json` |
| 7. Close reading | Ask Claude to read each paper using `docs/phase2-template.md` | `corpus/analysis/papers/<id>.json` |
| 8. Update the rules | Ask Claude to compare the findings with the current guide (Phase 3 of the plan) | Edits to `references/` |
| 9. Test on held-out papers | Put drafts in `corpus/eval/`, then run `python3 tools/eval_drafts.py` | `corpus/eval/report.md`, plus blind A/B/C packs in `corpus/eval/blind/` |

Notes:
- **Prefer ORCID** in `search`. Names like "Smith J" match many people.
- **Choose held-out papers (`holdout=y`) before analysing anything.** They are left out of steps 6–8 so
  that step 9 is a fair test. If they leak into the analysis, the test tells you nothing.
- Papers that are not open access will be missing. Add their `.tex` from Overleaf by hand; LaTeX is the
  best source format.
- `tools/category_rules.json` holds the keyword rules `classify` uses. Edit it if papers are put in the
  wrong category.

### Testing a change with `eval_drafts.py`
This tool checks whether drafts written with the guide sound more like the group than drafts written
without it. Layout, all under `corpus/eval/`:
```
originals/<id>/<section>.md              text from the held-out paper
drafts/guided/<id>/<section>.(tex|md)    written with draft-section from a content-only outline
drafts/baseline/<id>/<section>.(tex|md)  written from the same outline with no style guide
```
Sections are `introduction`, `discussion` and `conclusion`. The report compares sentence length, passive
voice, hedging, the group's signature moves and lint findings for each version. Give the blind packs
to group members and ask "which sounds like us, and what gives it away?" Turn each answer into a new
or corrected rule.

See `docs/style-guide-plan.md` for the full method and its current status.
