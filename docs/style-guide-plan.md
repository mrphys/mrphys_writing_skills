# Plan: building the group style guide from the corpus

Goal: a style guide in three layers, each rule backed by evidence from the group's papers, and checked by
whether drafts written with it read like the group's writing to group members.

```
references/
  style-guide.md            general rules: every paper, every venue
  styles/<category>.md      reconstruction, segmentation, clinical, methods-other (acquisition, computational)
  venues/<venue>.md         MRM, JCMR, Nature family, clinical cardiology journals, ISMRM abstract, arXiv
  exemplars/<category>/     annotated model paragraphs, by section
```
When drafting, a skill loads the general guide, then the category file, then the venue file. If they
conflict, the more specific file wins: venue over category over general, and the paper's own
`CLAUDE.md` over all of them. The general and category files describe how the group *writes*. Venue
files only describe what a journal *requires* (structure, limits, abstract format, reference style,
spelling).

## What the corpus looks like (2026-11-26)

51 papers kept, 48 readable.

| Category | Papers | Venues |
|---|---|---|
| clinical | 21 | 17 clinical journals, 4 JCMR |
| reconstruction | 12 | 7 preprints, 3 MRM, 1 Sci Rep, 1 JMRI |
| segmentation | 10 | 5 preprints, 2 PLoS Comp Biol, 1 JCMR, 1 Sci Rep, 1 Radiol AI |
| acquisition | 2 | MRM, NMR Biomed |
| computational | 2 | Ann Biomed Eng, J R Soc Interface |
| review / other | 4 | |

Consequences for the plan:
- Acquisition and computational are too small for their own guides. Merge them into one
  **methods-other** file for now, and split them once the corpus grows.
- Nature-family journals have only 3 papers, so venue files come mostly from the journals' author
  guidelines, with corpus papers as examples.
- **Journal copy-editing hides the group's own style.** Published text has been edited to the journal's
  house style (hyphens, spelling, "Fig." vs "Figure", heading capitals). Preprints and author
  manuscripts show what the group actually wrote. Treat surface conventions found only in published
  versions as venue rules, not group rules. Where both versions of a paper exist (e.g. Image2Flow,
  the natural-videos paper), comparing them shows directly what the journal changed.
- **Authorship matters.** 20 papers have a group member as last author and 11 as first author. Large
  multicentre clinical papers mostly reflect other people's writing. Weight evidence by authorship.

## Phase 0: Prepare the corpus (no tokens)
1. Retry the 3 failed downloads, and add `.tex` from Overleaf for any key paper that is missing or
   PDF-only.
2. Run quality checks with a script: word count, sections found, leftover fragments. Re-extract or drop
   files that fail.
3. Add three columns to `index.csv`:
   - `weight`: high if a group member is first or last author, low for consortium papers
   - `version`: preprint / author manuscript / published
   - `holdout`: y/n
4. **Choose the held-out set now, before any analysis:** about 2 papers per main category, kept out of
   every later phase and used only in Phase 6. If they leak into the analysis, the evaluation tells you
   nothing.

## Phase 1: Measure the text with a script (no tokens)
`tools/profile_corpus.py` computes these for every paper and section, then summarises them by category,
venue and version:
- sentence and paragraph length, section word counts, which headings are used
- voice: share of passive sentences, how often "we" appears, tense in each section
- spelling: British vs American (-ise/-ize, haemo-/hemo-, artefact/artifact)
- numbers and units: "1.5 T" vs "1.5T", "±", "×", ranges, decimals, how p-values are reported
- figure and table references ("Figure 2" / "Fig. 2" / "(Fig. 2a)"), citation placement
- hedging and claim-strength words ("novel", "significantly", "may", "suggests", "demonstrate")
- abbreviations: how many, defined on first use, defined again in the main text?

Output: `corpus/analysis/profile.md`, tables that show which differences between categories and
venues are large and which are noise. This settles questions like "do clinical papers use more passive
voice?" from data, so the reading in Phase 2 can focus on what a script can't measure.

## Phase 2: Close reading, one paper at a time (the main token cost)
For each paper that isn't held out (high weight first), a subagent fills in a fixed template in
`corpus/analysis/papers/<id>.json`. Every observation must come with a verbatim quote:
- **Introduction:** the sequence of moves (context → problem → gap → contribution), paragraph count, how
  the gap is stated, whether contributions are listed.
- **Methods:** order of subsections, level of detail (parameters inline or in a table), ethics and
  consent wording, how software and code availability are reported.
- **Results:** how much interpretation creeps in, how statistics are written, how figures are brought in.
- **Discussion:** structure (summary → comparison → limitations → future work), how strong claims are,
  how limitations are worded.
- **Abstract:** structured or not, and the order of its parts.
- **Notation and terminology:** symbols, sequence names, preferred terms.
- **Distinctive habits:** recurring phrases, transitions, anything a co-author would recognise.

Cost: about 45 papers × ~10k tokens ≈ 0.5M input tokens. To save tokens, run a stratified pilot first
(the best 3 papers per category, about 12 in total), check the template gives useful results, then run
the rest. A cheaper model works for this step, because the template does most of the thinking.

## Phase 3: Combine the findings into rules
For each candidate rule, count the papers that follow it and the papers that break it, overall and by
category, venue and version:
- Followed by most high-weight papers in **every** category → **general** guide.
- Clearly different between categories → **category** file.
- Found only in published versions, or tied to one journal → **venue** file.
- Mixed with no pattern → write it down as an **open question** for the group to decide; don't make
  it a rule.

Each rule is written as: the rule, a short reason, and 1–2 references to example papers. Rules a script
can check go into `lint-rules.json`, with one rule set per category if needed.

Venue files: fetch the official author guidelines for MRM, JCMR, Sci Rep / Nature Comms, PLoS Comp
Biol, the main cardiology journals and ISMRM abstracts, then compare them with how the group's papers
in that journal actually look.

## Phase 4: Choose example paragraphs
For each main category: 1–2 paragraphs per section (Introduction opening, gap → contribution,
Methods acquisition paragraph, Results paragraph with statistics, Limitations, Conclusion) plus 2
figure captions. Take them from high-weight papers, preferring author versions. Each file starts with a
one-line "why this is a good example".

## Phase 5: Group review
- Publish the draft guide as a page where group members accept, reject or edit each rule.
- PIs decide the open questions (e.g. British vs American spelling, "we" in Methods).
- The agreed version goes into the repo as `v1.0` via a pull request.

## Phase 6: Test it against the held-out papers
For each held-out paper: write a short outline from its text, have `draft-section` regenerate 2–3
sections, then:
- **Script check:** compare the Phase 1 measurements of the draft with the original's and the
  category average.
- **Blind comparison by group members:** show the original next to the draft (and next to a draft
  written without the guide), and ask "which sounds like us?" and "what gives it away?"
- Every "what gives it away" answer becomes a new or corrected rule. Repeat until the drafts are hard
  to tell apart from the originals.

## Phase 7: Connect the guide to the skills
- The paper's `CLAUDE.md` gets `category:` and `venue:` fields. `draft-section` and `style-review` load
  the matching files.
- `lint_tex.py` gets `--category` / `--venue` options to choose rule sets.
- Make re-running the pipeline a routine task as new papers come out (search → classify → download →
  profile → compare differences against the current guide).

## Decisions needed before starting
1. Who counts as "group": which senior authors define the style (affects `weight`)?
2. Include clinical papers led by collaborators, or only ones with a group member as first or last
   author?
3. Venue list: MRM, JCMR, Nature family, clinical cardiology journals, ISMRM abstract. Anything else
   (IEEE TMI, MICCAI)?
4. Pilot first (about 12 papers) or the full corpus straight away?

## Status (2026-11-26)
Scope for v0.1: **reconstruction and segmentation only**. Style authors: V. Muthurangu and J. Steeden
(`weight=high` = VM or JS first or last author). Collaborator-led papers are excluded.

- [x] Phase 0: corpus of 25 reconstruction and segmentation papers (3 added from a search on JS); weights,
  versions and preprint/published pairs recorded; held out: 2406.02553v1, PMC9681557 (reconstruction),
  2209.06117v1 (segmentation).
- [x] Phase 1: `tools/profile_corpus.py` → `corpus/analysis/profile.md` (16 papers).
- [x] Phase 2: 16 papers read with `docs/phase2-template.md` → `corpus/analysis/papers/*.json`; all 858
  quotes checked verbatim against the sources.
- [x] Phase 3: `references/style-guide.md`, `references/styles/{reconstruction,segmentation}.md`,
  `references/open-questions.md`; `lint-rules.json` rebuilt from the evidence. Venue files not started.
- [x] Open questions decided by the group (2026-11-26); written into the guide as [decided] rules and into
  `lint-rules.json` (British spelling except 'artifact', '1.5T', '(i)', spaced ±, en-dash ranges,
  leading-zero p, 'This figure shows…', limitations in the Discussion unless requested).
- [x] Phase 4: 25 annotated verbatim excerpts in `references/exemplars/{reconstruction,segmentation}/`.
- [ ] Phase 5: group review.
- [x] Phase 6, automated part (2026-11-26): 3 held-out papers × 3 sections drafted from content-only notes,
  with the skill (guided) and without it (baseline). `tools/eval_drafts.py` → `corpus/eval/report.md`.
  Guided: 0 lint findings vs 33 for the baseline; matches the original's signature moves in 26/39 cases vs
  19/39 for the baseline; closer to the original on style measurements (0.63 vs 0.73). Over-applies some
  moves (29 used vs 22 in the originals). Blind A/B/C packs for human judging are in `corpus/eval/blind/`
  (key in key.json).
- [ ] Phase 6, human part: VM/JS blind judgements, then turn the feedback into rules.
  [ ] Phase 7: done for loading the category file in the skills; per-category lint and venue files to do.
