# reconstruction · methods training

Verbatim excerpts from group papers (V. Muthurangu / J. Steeden senior authors). Copy the **structure and moves**, not
the content. Where an excerpt predates a group decision, the note says what to do instead. Edits to the
source text are limited to removing conversion artefacts (citation and figure brackets) and the typo fixes
listed for each excerpt.

## 2605.26127v1: Rapid online deep artifact suppression for real-time spiral bSSFP CMR with blipped-CAIPI s

**Why:** Training in one sentence (optimiser, loss, GPU); data sources as an inline (i)/(ii) list with ethics references; slash-triplet split; pre-processing in one closing sentence.

> The U-Net was trained using an Adam optimizer17 with a structural similarity index measure (SSIM) loss, on an NVIDIA RTX A6000 GPU. Synthetic paired training data were created from retrospectively gated Cartesian breath-hold bSSFP multi-slice short-axis (SAX) cine k-space data from two populations: (i) 64 subjects collected at the Royal Free Hospital, London, United Kingdom (Ethics ref. 21/EE/0037, 17/LO/1499); and (ii) 11 subjects from the publicly available Open-Access Multi-Coil k-Space Dataset for Cardiovascular Magnetic Resonance Imaging (OCMR) dataset (all subjects with fully sampled, multi-slice SAX data)18. The data was split into 59/6/10 subjects for training/validation/testing, with all OCMR data placed in the training set. All datasets were pre-processed by interpolation in image space to a 240×240 matrix, with 24 timeframes.

## PMC8613539: Real-time deep artifact suppression using recurrent U-Nets for low-latency cardiac MRI

**Why:** Software versions, hyperparameters in one sentence, a design choice explained with a 'for memory considerations' reason, hardware and training time.

**Do differently now:** Copy-edited by the journal (MRM): '‐' hyphens and bracketed citations are the journal's.

> The network was implemented and trained using Python (v3.7.7) and TensorFlow (v2.2.0).[24] Training was performed using 100 epochs, an initial learning rate of 0.001, batch size of 4, and an adaptive moment estimation algorithm (Adam).[26] The data are split into time series of 8 frames at training (for memory considerations); however, the states and memory cells are reset only at the end of the complete time series. Training was performed on a Linux workstation (Ubuntu 18.08, Intel Core i9‐7900X, 3.3 GHz) using an NVIDIA Quadro GP100 (16 GB memory). All networks trained in this experiment had ~1.79 million trainable parameters and took 8 h and 40 min to train when training on the full dataset.
