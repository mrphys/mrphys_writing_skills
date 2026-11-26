# Corpus (not committed)

Put the group's papers here as source material for building `references/style-guide.md`.
Everything in this folder except this README is git-ignored: papers may be under copyright or unpublished.

To fill it automatically from Europe PMC (open-access full text) and arXiv (LaTeX source):
```
python3 tools/build_corpus.py search --orcid <ORCID> --author "Surname AB" --arxiv-author "Firstname Surname" \
    --affiliation "University College London" --since 2018
python3 tools/build_corpus.py classify    # suggests reconstruction/segmentation/computational/acquisition/clinical/review/other
# review corpus/index.csv: fix categories, set keep=n on rows to drop
.venv/bin/python tools/build_corpus.py download [--category reconstruction ...]
```
Some arXiv preprints have only a PDF, no LaTeX source. With the project venv (`python3 -m venv .venv &&
.venv/bin/pip install pymupdf`), `download` turns these into `paper.md` automatically. Without it they are
marked `pdf-only`; convert them later with `.venv/bin/python tools/build_corpus.py extract`, or any PDF by hand
with `.venv/bin/python tools/pdf_text.py some.pdf`.
Papers that are not open access will be missing; add their .tex from Overleaf by hand.

Preferred formats, best first:
1. LaTeX source (`.tex`, e.g. downloaded from Overleaf) — exact text, notation and structure, cheapest to read.
2. Plain text / Markdown extracted from PDFs with `pdftotext -layout` (poppler) or PyMuPDF.
3. PDFs as a last resort — Claude can read them directly, but it costs far more tokens per page.
