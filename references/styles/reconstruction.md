# Category style: reconstruction (incl. acceleration, artifact suppression, super-resolution)

Adds to `../style-guide.md`. Evidence: 12 reconstruction papers (1803.05192v3, 1804.09480v1,
1912.10503v1, 2103.07541v1, 2203.13729v1, 2302.02688v2, 2303.11831v3, 2311.13963v1, 2506.22532v1,
2603.29922v1, 2605.26127v1, PMC8613539).

## Story shape
- **The problem is almost always time:** scan time, breath-holds, reconstruction time or latency. Frame the
  clinical context around what a faster or real-time method makes possible (free breathing, children,
  exercise, interventions, online use on the scanner).
- **CS is the default baseline** to beat on speed and to match on quality. Name it in the Introduction
  ("Unfortunately, CS reconstructions are computationally intensive…") and compare against it in every
  experiment. Add a second DL baseline where one is reasonable (e.g. VarNet, SToRM, SMORE, LR-DIP).
- **Validate step by step:** simulation or in-silico test data first (with ground truth), then a
  prospective in vivo study against the **reference-standard breath-hold** acquisition. Say why
  explicitly: "Demonstrating reconstruction accuracy on synthetic low-resolution test data… [then]
  prospective…" (1912.10503v1).

## Methods specifics
- **Training data:** say where the data came from (retrospective clinical, public dataset, natural videos,
  synthetic) and how undersampled or "synthetic" inputs were simulated from it. Put 'synthetic' and
  'ground truth' in single quotes at first use (several papers).
- **Network:** "The network was based on a 3D UNet architecture (ref) with the following specific
  modifications: i) …; ii) …". Training goes in one sentence: optimiser, learning rate, epochs, batch size,
  loss (often SSIM or MAE), GPU.
- **Online or inline implementation:** describe deployment on the scanner (Gadgetron, used in 5 papers)
  and give the hardware, because latency claims depend on it.
- **Image quality has two tiers:**
  - simulation: SSIM, PSNR, MAE/NRMSE against ground truth
  - in vivo: edge sharpness, eSNR, CNR, and blinded qualitative scoring (Likert with anchors, or ranking
    when comparing reconstructions of the same raw data: "Likert scoring lacks granularity when comparing
    different reconstructions of the same raw data. Therefore, ranking was used", 2302.02688v2)
- **Clinical agreement:** ventricular volumes (EDV, ESV, EF, SV) or flow against the reference standard by
  Bland-Altman ("bias ± 1.96 SD" / limits of agreement) and ICC.

## Results specifics
- **Report time first when time is the point:** acquisition time and reconstruction time as mean ± SD,
  with "~N× faster than CS" and the raw values in parentheses. Break latency down into its components
  ("the gridded reconstruction took on average 33 ms, deep artifact suppression 19 ms and other
  processes 5ms").
- **Always address hallucination** for DL reconstructions: "There were no obvious hallucinated features at
  any of the acceleration factors" (PMC8613539) in Results, and come back to it in Limitations: "In our
  study, we did not observe any obvious hallucinations. However, it is a possible risk of our approach…"
  (2302.02688v2).
- State failures plainly: "The standard U-net results were inadequate for k-t SENSE priors…"
  (2103.07541v1).
- Point to videos for dynamic data ("Supporting Information Video S#").

## Discussion specifics
- Compare mainly with **the group's own previous reconstruction** and the CS baseline, not with published
  numbers. Prior frameworks are compared on hardware and latency ("using only a single mid-range GPU
  rather than multi-GPUs").
- **Explain mechanisms** in hedged form: "We believe that the superior image quality of … is because…".
- **Usual limitations:**
  - small healthy-volunteer cohorts
  - training on breath-hold data but testing on free-breathing data
  - no assessment of diagnostic accuracy
  - generalisation to other sequences, vendors or field strengths
  - risk of hallucination

  Each is followed by what is needed next (a larger, multi-centre or patient study).
