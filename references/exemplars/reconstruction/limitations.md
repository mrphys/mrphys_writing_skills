# reconstruction · limitations

Verbatim excerpts from group papers (V. Muthurangu / J. Steeden senior authors). Copy the **structure and moves**, not
the content. Where an excerpt predates a group decision, the note says what to do instead. Edits to the
source text are limited to removing conversion artefacts (citation and figure brackets) and the typo fixes
listed for each excerpt.

## 1803.05192v3: Real-time Cardiovascular MR with Spatio-temporal Artifact Suppression using Deep Learning 

**Why:** The core limitation pattern in one paragraph: 'The main limitation is…' → consequence → 'However,' mitigating experiment → what it suggests → 'Nevertheless, further work is necessary…'.

**Edited:** 'we did we did perform' → 'we did perform'

> The main limitation is that the training data was acquired during a breath-hold, while the real-time data was acquired during free-breathing. This means that the network cannot ‘learn’ anything about respiratory motion, and may not be able to correct for this additional motion. However, we did perform an experiment in a single volunteer that demonstrated that the U-Net reconstruction was relatively robust to even large respiratory perturbations. This suggests that the network learns the structure of the noise to be removed, rather than the expected motion of the underlying structures. Nevertheless, further work is necessary to fully understand the effect of motion not apparent in the training data.

## 2605.26127v1: Rapid online deep artifact suppression for real-time spiral bSSFP CMR with blipped-CAIPI s

**Why:** Several limitations: 'This study has several limitations. First… Second… Third… Fourth… Finally…', each with what is needed next.

**Do differently now:** Per the group decision this belongs in the final Discussion paragraphs, not a separate subsection, unless requested.

> This study has several limitations. First, the sample size was small and limited to healthy volunteers; further validation in larger and pathological cohorts is required. In particular, performance in patients with arrhythmia or irregular breathing patterns, where real-time imaging is most clinically valuable, remains to be established. Second, only an SMS factor of two was investigated; higher SMS factors may provide further acceleration but may also increase slice leakage and require retraining of the DL model. Third, all data were acquired on a single scanner platform and field strength, and generalisation to other systems remains to be established. Fourth, the DL model was trained on retrospectively simulated data, which may not fully capture all artifacts present in prospectively acquired RT-SMS data. Future work could incorporate prospectively acquired training data or domain adaptation strategies to further improve robustness. Finally, no comparison was made with alternative DL reconstruction strategies (e.g. unrolled networks), which may offer different trade-offs between quality and speed.
