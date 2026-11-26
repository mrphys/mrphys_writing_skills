# Open questions for the group

Conventions where the group's own papers disagree. Each needs a decision from VM/JS before it becomes a
rule. Until then the skills **follow the target journal's style, or the first author's preference stated
in the paper's `CLAUDE.md`, and stay consistent within one paper.** Counts are from the 16 analysed
papers. Fill in the Decision field and move the rule into `style-guide.md` (or a venue file).

| # | Question | What the papers do | Suggested default | Decision |
|---|---|---|---|---|
| 1 | British or American spelling? | Each paper is internally consistent but the corpus is split. British: k-t SENSE, CLADE, aortic DNN, fractals. American: HyperSLICE, FReSCO, recurrent U-Net, Image2Flow. Apparently set by the first author. | British (UCL; paediatric, centre, optimise), unless the journal requires American. | |
| 2 | "artefact" or "artifact"? | Split, and mixed within single papers (HyperSLICE, FReSCO, recurrent U-Net). The technique is written "deep artifact suppression" in 6 papers. | Follow #1, but always "deep artifact suppression" for the named technique. | |
| 3 | Field strength: "1.5 T" or "1.5T"? | "1.5T" in 9 papers, "1.5 T" in 2, both in 1. Journals often impose "1.5 T". | "1.5T" in drafts; the venue file can override. | |
| 4 | Numbering inline lists | `i)` 7 papers; `(i)` 4 (all 2023+); `1)` 3. | `(i)`, which recent papers have moved to. | |
| 5 | ± spacing | Older papers "68±8 bpm"; recent ones "30 ± 1 s". | "30 ± 1 s" (spaced). | |
| 6 | Ranges: hyphen or en dash? | Hyphen in 7, en dash in 2, both in 3. Journals change it to an en dash (Sci Rep). | En dash: "1–3 ms". | |
| 7 | How captions open | Noun-phrase title (most), "Shows…" (2506.22532v1), "This figure shows…" (2605.26127v1). | Noun-phrase title, then description. | |
| 8 | "novel" | Absent in 13/16; used in CLADE ("a novel approach") and 1804.09480v1. | Don't use; use "To our knowledge, … first" in the Discussion if needed. | |
| 9 | Separate Limitations subsection? | Own subsection in 11/16; final paragraphs in the rest (often set by venue). | Own subsection unless the venue forbids it. | |
| 10 | Code availability | Every paper since 2023 links github.com/mrphys; earlier papers have none. | Always include, plus a data statement. | |
| 11 | p-values without leading zero ("p=.0004") | Only Image2Flow (PLoS); elsewhere "p=0.009". | "p=0.009"; follow the venue if it requires otherwise. | |
| 12 | Who defines style for clinical papers? | Out of scope for v0.1 (reconstruction and segmentation only). | — | |

Answers:
1. British
2. Artifact
3. 1.5T
4. (i)
5. spaced
6. en dash
7. This figure shows...
8. Use to our knowledge etc
9. separate only if requested
10. include
11. add leading 0
12. out of scope