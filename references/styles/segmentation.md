# Category style: segmentation (incl. DL pipelines from image to measurement)

Adds to `../style-guide.md`.

**Thin evidence: treat these rules as provisional.** Only 4 papers: 2303.11676v1 (single-ventricle
pipeline), PMC13237537 (open-source mouse segmentation), 2402.18236v1 (Image2Flow) and 2208.12156v2
(DNN aortic CFD). The last two are mainly deep-learning surrogates for CFD, labelled segmentation by the
"deep learning → segmentation or reconstruction" rule. The great-artery segmentation paper (2209.06117v1)
is held out for testing. Add papers before treating anything here as settled.

## Story shape
- **The problem is manual analysis**: slow, operator-dependent and hard to scale to registries or
  longitudinal studies. "However, current manual segmentation approaches are time-consuming…"
  (PMC13237537).
- **The gap is usually a population or task** that existing models don't cover: congenital or
  single-ventricle hearts, small animals, joint segmentation and simulation. "However, most DL models are
  trained and validated on structurally normal hearts (9–11)…" (2303.11676v1).
- **Priority claims are more common than in reconstruction papers** (3/4): "To our knowledge, this is the
  first…" / "This study is the first description of…". Keep to one such claim, made in the Discussion;
  only resource and dataset papers repeat it in the abstract and conclusion.

## Methods specifics
- **Pipelines are described stage by stage** ("Stage 1: Cine Stack Extraction", "Stage 2: Short-Axis
  Identification", …), each with task, training data and split, architecture and loss. Put
  hyperparameters in Supporting Information.
- **Ground truth:** say who segmented, their experience, and any review step. A single operator is the
  usual limitation, so mitigate it (second observer, expert review).
- **Augmentations** as an inline numbered list with values: "(i) rotation (±15°) … (vii) …".
- **Clinical quantities are defined by formula in prose:** "Ejection fraction (EF) was calculated as
  (EDV-ESV)/EDV, and stroke volume (SV) as EDV-ESV."
- **External or multi-site test sets** are named by their source or field strength ("internal 9.4T test
  dataset").

## Results specifics
- **Accuracy:** Dice (with HD/ASSD where relevant) per structure and phase. Use **median (IQR)** when
  distributions are skewed (2/4), stated in Statistics.
- **Clinical agreement:** Bland-Altman and ICC for EDV, ESV, EF and mass against manual segmentation, then
  **compare with human inter-observer variability**, which is the key reference point: "Overall, the DL
  model performed comparably to a secondary human observer…" (PMC13237537).
- **Show best, median and worst cases** (by Dice) in a figure (3/4).
- Report processing time per image or per examination against manual analysis time.

## Discussion specifics
- **Comparisons with the literature are named and numerical**, unlike reconstruction papers: "Xu et al.
  employed a 2D UNet with leave-one-out validation on 12 mouse datasets, reporting Dice coefficients of
  0.89…" (PMC13237537). They may go in a "Comparison with previous studies" subsection.
- Explain residual disagreement anatomically (basal and apical slices, outflow tracts) or by
  institution-specific practice.
- **Usual limitations:** single-operator ground truth, a single centre or vendor, structures not
  segmented (e.g. RV), and a simplified downstream model (for CFD surrogates).
