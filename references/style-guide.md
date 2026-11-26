# Group style guide: general rules

How the group writes, for every paper type. Load this first, then `styles/<category>.md`, then
`venues/<venue>.md` once venue files exist. The more specific file wins on conflicts, and the paper's own
`CLAUDE.md` overrides everything.

**Evidence base (v0.1, 2026-11-26):** 16 reconstruction and segmentation papers with V. Muthurangu or
J. Steeden as first or last author, 2018–2026, mostly author preprints. Counts like (14/16) are the number
of those papers that follow the rule. Rules that apply to both categories are here; category-specific
rules are in `styles/`. Points where the papers disagreed were decided by the group on 2026-11-26
(`open-questions.md`); those decisions are now rules here and are marked **[decided]**. Supporting data: `corpus/analysis/profile.md` (measurements) and `corpus/analysis/papers/*.json`
(per-paper evidence with quotes).

---

## 1. Overall voice

- **Plain, direct and confident about what was shown; hedged about why.** State headline results without
  hedging ("X was ~50× faster than CS"). Hedge explanations and implications ("We believe that this is
  because…", "probably", "may", "could potentially").
- **Sentence length:** about 22 words on average in every section, with Conclusions shorter (about 17).
  Avoid long chains of clauses. One idea per sentence.
- **Connectives carry the argument.** The group relies on a small, recognisable set of sentence-initial
  connectives. Use them; don't swap in synonyms:
  - *However,* (in every paper): contrast, or the limitation of an approach
  - *Unfortunately,*: introduces the problem with the current standard (Introduction)
  - *Nevertheless,*: concedes, then pivots (Results, Limitations, future work)
  - *Thus,* / *Therefore,* / *Consequently,*: consequence or design decision
  - *Importantly,* / *Interestingly,*: flags the key or unexpected result
  - *It should be noted that*: introduces a caveat, exclusion or secondary observation (10/16)
- **Avoid** "novel" (absent from 13/16; where novelty matters, see §5 Discussion), "delve",
  "state-of-the-art" as praise, "paradigm", "groundbreaking", "unprecedented", and adverb stacks.
- **"Proof-of-concept"** is the group's standard self-label for first demonstrations (6/16). Use it in the
  aim, the first Discussion sentence and the limitations, so that scope is stated, not apologised for.

## 2. Abstract

- **Structured** (13/16): `Purpose` (or `Background`), `Methods`, `Results`, `Conclusion`. The label set
  depends on the venue: MRM uses Purpose, JCMR uses Background, and PLoS and CS venues use unstructured
  abstracts. About 250–350 words.
- **Purpose/Background:** clinical need or application → constraint ("However, …") → aim. Write the aim
  as an infinitive ("To develop and evaluate…", "To investigate whether…") or as "In this study, we aim
  to…" / "This study investigates…".
  > "Real-time monitoring of cardiac output (CO) requires low latency reconstruction and segmentation of real-time phase contrast MR (PCMR)…" (2203.13729v1)
- **Results:** headline numbers with mean ± SD and p-values. Speed-ups go as approximate multipliers with
  the raw times in parentheses. State non-significant comparisons as "no significant difference".
  > "RT-SMS reconstruction using deep artifact suppression was ~50× faster than CS (30 s vs 24 min 55 s)." (2605.26127v1)
- **Conclusion:** one or two sentences: what was demonstrated, plus a hedged clinical implication.
  Standard forms:
  > "X was successfully demonstrated in [application]…" (PMC8613539, 2203.13729v1)
  > "This paper demonstrates the potential of using X for Y." (1803.05192v3, 1912.10503v1, 2303.11831v3)
  > "Thus, we believe that this technique may help speed up … CMR in clinical practice." (1912.10503v1, 2506.22532v1)

## 3. Introduction

- **Length:** 3–5 paragraphs, about 400 words. No separate Related Work section (15/16). Weave prior
  work into the problem→solution narrative.
- **Order of moves** (followed by essentially all 16):
  1. Clinical context: why the measurement or examination matters. Present tense.
  2. The problem with the reference standard, introduced with **"Unfortunately,"**.
  3. Existing approaches, each followed by its drawback (**"However,"**). Drawbacks are often listed
     inline: *"However, there are drawbacks to CS including: i) Computationally intensive and
     time-consuming reconstruction, and ii) …"* (1803.05192v3)
  4. The group's own previous work, if relevant, in first person: *"We have previously shown that…"*
  5. The proposal: *"In this study, we propose…"* / *"In this study, we …"*
  6. **The aims, as an inline numbered list in one sentence** (14/16):
     > "The aims of this study were to: i) Investigate…, ii) Acquire…, and iii) Compare…" (1803.05192v3)
     Each item starts with a verb. Separate items with commas, or with semicolons when the items contain
     commas, and put "and" before the last. Past tense ("were") is the default. **[decided]** Number inline
     lists as `(i)`, `(ii)`, `(iii)`, everywhere (aims, findings, problems, augmentations):
     "The aims of this study were to: (i) develop…; (ii) compare…; and (iii) assess…".
- **No bulleted list of contributions.** The aims sentence does that job.
- **Citations are numbered** and attached to claims, never author-led in the Introduction ("Recently, CNNs
  have been shown to be well suited to… (6-8)"). Name authors only when comparing directly with one
  specific study in the Discussion.
- **Tense:** present for established facts; present perfect for developments in the field ("have been
  shown to"); past for the group's own earlier work.

## 4. Methods

- **Voice:** passive past tense for procedures (about two-thirds of sentences); **"we" for decisions**
  ("We chose…", "we opted to…", "We used…"). The procedure is passive and the choice is active.
- **Give the reason for each design choice inline**, in a short clause or a following sentence: "…because…",
  "…to ensure…", "This was done to…". Report preliminary attempts that failed and say what was changed
  ("Thus, …").
- **Subsection order** (most papers): overview (often with a pipeline figure) → training data →
  architecture and training → simulation or in-silico experiments → prospective in vivo study → image
  analysis and metrics → **Statistics (always last)**.
- **Run-in labels** ("Qualitative image evaluation: …", "Acquisition: …") are fine for short sub-paragraphs
  in place of extra heading levels.
- **Acquisition parameters** go inline as a `Parameter: value` list, with the full table referenced:
  > "FOV: 350x262 mm, voxel: 1.82x1.82x6.0 mm, TR/TE: 4.4/1.9 ms, Flip Angle: 30o, VENC: 200 cm/s…" (2103.07541v1)
  > "…(full sequence parameters are shown in Table 1)." (1804.09480v1)
  Always include scanner field strength and vendor/model on first mention: "a 1.5T MRI scanner (Avanto,
  Siemens Medical Solutions, Erlangen, Germany)".
- **Cohorts:** n, then age as mean ± SD (with range where relevant) and sex counts in parentheses. Put
  diagnoses in Supporting Information when there are many.
  > "(mean age: 26±13 years, range: 5-80 years. Male: 299, Female: 201)" (1912.10503v1)
- **Data splits** as a slash triplet (≥8/16):
  > "The dataset was split into 519/69/104 videos for training/validation/testing." (2311.13963v1)
- **Ethics**, close to fixed wording (≥9/16):
  > "This study was approved by the local research ethics committee (ref. 19/LO/1561), and written consent was obtained from all subjects/guardians."
- **Image-quality metrics:** define each one operationally in one sentence (what region, what ratio, which
  cardiac phase), citing the group's earlier paper "as previously described". Edge sharpness is always
  "the maximum gradient of the normalized pixel intensities across the border of [the septum / the vessel
  of interest], as previously described (ref)" (5 papers). For
  non-Cartesian data, note that true SNR is "nontrivial" and use estimated SNR (eSNR). Give Likert scales
  with every anchor in parentheses, and identify observers by initials and years of experience:
  > "5-point Likert scale (5 = non-diagnostic, 4 = poor, 3 = adequate, 2 = good, 1 = excellent)" (2506.22532v1)
- **Statistics** (final subsection), close to fixed wording:
  > "Statistical analyses were performed using SciPy (version 1.10.1) in Python, with a p-value <0.05 considered statistically significant." (2605.26127v1)
  > "All continuous variables are presented as mean (± standard deviation) for normally distributed data, or median (interquartile range) otherwise." (2506.22532v1)
  Name the normality test (Shapiro-Wilk), the paired test (paired t-test / Wilcoxon), the multi-group test
  (repeated-measures ANOVA / Friedman) and the post-hoc test, and use Bland-Altman bias and limits of
  agreement for agreement with the reference standard.
- **Code availability** **[decided]**, always: "The code is available online at:
  https://github.com/mrphys/<repo>". Put it at the end of the relevant Methods subsection or in the
  overview.

## 5. Results

- **Light interpretation only.** Report and compare; keep mechanisms for the Discussion. One short
  interpretive sentence is allowed ("This demonstrates that…").
- **Paragraph pattern:** headline finding → numbers ("X vs Y", mean ± SD, p) → figure/table pointer. Or
  start with the figure pointer for qualitative results:
  > "Representative images are shown in Figure 5 and the corresponding movie can be seen in Supporting Information Video S9." (1803.05192v3)
- **Standard phrasings:**
  - "There were no significant differences (p>0.2) in … between A (value), B (value) and C (value)."
  - "small but statistically significant [over/under]estimation of …", followed by "Nevertheless, …" to
    give the clinical context
  - Agreement graded in words: *excellent* (ICC/r ≥0.9), *good*, *reasonable*, *acceptable*
  - Speed and latency as values with "~N× faster", and latency broken down into its components where relevant
- **Detail goes to Supporting Information**, referred to as "Supporting Information Figure S#/Table S#/Video S#".
- **Tense:** past for what was measured; present for what a figure shows.

## 6. Discussion

- **Opening sentence** (14/16 use one of these):
  > "The main findings of this study were: i) …; ii) …; and iii) …" (8/16, mirroring the aims)
  > "The main finding of this proof-of-concept study was that …" (single-aim papers)
  > "In this study, we demonstrated the feasibility of …"
- **Then, in this order:** why it worked (mechanism, hedged with "We believe that this is because…") →
  comparison with the closest prior work (often the group's own) and the direct baseline → clinical
  implications and translation → limitations → future work.
- **Novelty** **[decided]**, when it needs claiming, is "To our knowledge, this is the first study to…",
  once, in the Discussion. Never "novel".
- **Literature comparison** is mostly qualitative and centred on the baseline the group ran itself.
  Comparisons with published numbers are for segmentation (see `styles/segmentation.md`).
- **Limitations** **[decided]** go in the final paragraphs of the Discussion. Give them their own
  subsection only if the venue or co-authors ask for it. Open with a fixed phrase:
  > "The main limitation of this study was …" / "This study has several limitations."
  Each limitation follows this pattern: **limitation → "However," mitigation or reason → "Nevertheless,"
  what further work is needed.** When there are several, list them as "First(ly), … Second(ly), …
  Finally, …".
- **Future work** sits at the end of Limitations ("Future work will focus on…", "Nevertheless, further
  work is necessary to…"), not in the Conclusion.
- **First person** is used freely ("We have shown", "we believe", "we feel"). "We believe" is the group's
  signature hedge.

## 7. Conclusion

- 1–3 sentences, about 100–200 words at most. Restate what was demonstrated and the practical benefit,
  then end on a hedged clinical implication. No new numbers, no future work.
  > "Rapid free-breathing CMR with online reconstruction is feasible using non-Cartesian RT-SMS bSSFP combined with deep artifact suppression." (2605.26127v1)
  > "Thus, we believe that this technique could be used successfully in the paediatric population." (1804.09480v1)

## 8. Figures, tables and captions

- **In the text:** "Figure N" in full, not "Fig. N" (the journal may change this), with panels written
  "Figure 5.A" or "(Figure 5A)". Tables: "Table N".
- **Captions** **[decided]** start with "This figure shows…" (tables: "This table shows…"), then go panel
  by panel with A), B) (or "From left to right"), colour legends in parentheses, the matching video
  pointer, and abbreviations defined at the end.
  > "Figure 3: This figure shows how SMS slices are…" (2605.26127v1)
  Significance symbols (*, †) are defined in table footnotes, with the test named.
- Show **best, median and worst cases** when showing segmentation or reconstruction examples from a test
  set (see the category files).

## 9. Numbers, units and notation

- **Spelling** **[decided]**: British (optimise, normalise, paediatric, centre, haemodynamic, modelling,
  labelled, analyse, colour), **except "artifact"**, which is always spelled that way, including "deep
  artifact suppression".
- **Mean ± SD** as standard; median [IQR] for non-normal data, stated as such in Statistics.
  **[decided]** Put spaces around ±: "30 ± 1 s", "0.92 ± 0.03".
- **p-values:** lowercase p, "p<0.05", "p=0.009", "(all p<0.001)" (14/16 lowercase; p never written
  "P" in the group's own manuscripts). **[decided]** Always keep the leading zero ("p=0.0004", not
  "p=.0004").
- **Ranges** **[decided]** use an en dash: "1–3 ms", "range: 5–80 years" (`--` in LaTeX).
- **Percentages** with no space: "10%" (15/15 papers that use them).
- **Units** with a space after the number: "30 ms", "15 s", "1.7x1.7 mm". **[decided]** Field strength is
  the exception: "1.5T", "3T", "0.55T" (no space).
- **Approximate values** with a tilde: "~40 ms", "~50×".
- **Multiplication and acceleration:** "18x accelerated", "2.1×2.1×6.0 mm".
- **Fixed terms:** "real-time" (always hyphenated); "deep learning (DL)" (no hyphen); "deep artifact
  suppression" (the group's named technique); "reference-standard"
  (hyphenated as an adjective in recent papers: "reference-standard breath-hold (BH) cine"); "2D+time"
  for dynamic data; "free-breathing".
- **Abbreviations:** define at first use in the abstract **and again** in the main text, as long form plus
  (ABBR). Abbreviations are dense in Methods (about 6 definitions per 1,000 words). Results and Discussion
  should define almost nothing new.
- **Method names:** coined acronyms (FReSCO, HyperSLICE, CLADE, Image2Flow) are introduced in the title or
  aims and used consistently. Compared variants get suffix labels (RT-SMS-DL / RT-SMS-CS, F-DL / CMR-DL).
