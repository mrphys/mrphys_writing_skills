# segmentation · results

Verbatim excerpts from group papers (V. Muthurangu / J. Steeden senior authors). Copy the **structure and moves**, not
the content. Where an excerpt predates a group decision, the note says what to do instead. Edits to the
source text are limited to removing conversion artefacts (citation and figure brackets) and the typo fixes
listed for each excerpt.

## PMC13237537: Open-source pre-clinical image segmentation: mouse cardiac magnetic resonance imaging data

**Why:** Figure pointers first, then a one-line agreement verdict with ICC bounds across all test sets, then the only significant differences reported with values and p.

**Do differently now:** '24.8 ± 7.1, respectively. p = 0.007' → '…, respectively; p=0.007'. Journal style 'Fig. 5' → write 'Figure 5'.

> Bland–Altman and correlation plots for the internal 9.4T test dataset are shown in Fig. 5, and for the external test datasets (7T and 11.7T) are shown in Fig. 6. There was good agreement between clinical metrics from ground-truth manual segmentations and DL segmentations in all test datasets, in terms of EDV (ICC ≥ 0.94), ESV (ICCs ≥ 0.95), SV (ICC ≥ 0.89), EF (ICC ≥ 0.85), and myocardial mass at both ED ( r ≥ 0.87) and ES (ICC ≥ 0.88). The only statistically significant differences between clinical metrics from ground-truth manual segmentations and DL segmentations were found in the 11.7T external test dataset, with slightly lower ESV (23.6 ± 7.1 vs. 24.8 ± 7.1, respectively. p = 0.007), resulting in slightly higher SV (37.1 ± 6.8 vs. 36.0 ± 6.3, respectively. p = 0.017), slightly higher EF (61.6 ± 6.4 vs. 59.6 ± 6.0, respectively, p = 0.006).

## 2303.11676v1: Deep Learning Pipeline for Preprocessing and Segmenting Cardiac Magnetic Resonance of Sing

**Why:** Results sentence that points to the best/median/worst figure: the standard way of presenting segmentation examples.

> Figure 3 shows examples of ventricle segmentation through the pipeline for the best, median and worst cases (regardless of systolic or diastolic phase), based on Dice score (movies of all frames in supplementary information).
