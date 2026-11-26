# segmentation · discussion opening

Verbatim excerpts from group papers (V. Muthurangu / J. Steeden senior authors). Copy the **structure and moves**, not
the content. Where an excerpt predates a group decision, the note says what to do instead. Edits to the
source text are limited to removing conversion artefacts (citation and figure brackets) and the typo fixes
listed for each excerpt.

## 2402.18236v1: Image2Flow: A hybrid image and graph convolutional neural network for rapid patient-specif

**Why:** Novelty stated once as 'To our knowledge, this is the first study that…' [decided] → main findings list → main benefit quantified (~205ms, ~7,000x) → 'We believe…' clinical translation.

**Do differently now:** 'i)' → '(i)' [decided]; '~205ms' → '~205 ms'.

> To our knowledge, this is the first study that uses a graph-based DL model to efficiently segment and estimate flow fields in the pulmonary arteries directly from 3D whole heart data. The main findings of this study were: i) Image2Flow can generate highly accurate pulmonary artery volume-meshes directly from cardiac MRI data, and ii) Image2Flow can also robustly estimate pressure and velocity at mesh vertices. The main benefit of Image2Flow is automatic and rapid inference (~205ms), which is approximately 7,000x faster than manual processing and conventional CFD simulation. We believe the ability to perform rapid ‘CFD-like’ evaluation could aid with clinical translation of hemodynamic simulation in structural and congenital heart disease.

## 2303.11676v1: Deep Learning Pipeline for Preprocessing and Segmenting Cardiac Magnetic Resonance of Sing

**Why:** Priority claim + four numbered findings with graded agreement words ('acceptable', 'moderate') + contrast with previous pipelines.

**Do differently now:** 'i)' → '(i)' [decided]. Prefer 'To our knowledge, this is the first…' [decided] to the flat 'This study is the first description…'.

> This study is the first description of DL automated segmentation of single ventricles. The main findings of this study were: i) It is feasible to create an end-to-end deep learning pipeline that automatically takes CMR exams, extracts SAX cines, performs cropping, and segments the ventricles, ii) There was acceptable agreement between DL and manual segmentation of functional single ventricles in terms of volumes and mass, iii) The pipeline can rapidly and accurately segment large numbers of unseen cases with a high degree of success and iv) There was only moderate agreement between site entered volumes, and both DL and manually segmented core-lab data. Unlike previous segmentation pipelines, our framework processes images straight from an image registry (16) and could process the whole FORCE registry in <40 hours.
