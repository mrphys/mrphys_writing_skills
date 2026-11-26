#!/usr/bin/env python3
"""Convert a paper PDF to section-structured Markdown for the style corpus (needs PyMuPDF).

Usage: .venv/bin/python tools/pdf_text.py paper.pdf [more.pdf ...]   -> writes paper.md next to each PDF

Handles single-column manuscripts (Word/LaTeX submissions, double-spaced, line numbers) and two-column
journal layouts. Drops page numbers, line numbers, running headers/footers and the reference list
(but keeps figure legends that follow it). Equations come out as plain text and are often garbled:
use LaTeX source when notation matters.
"""
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

try:
    import pymupdf
except ImportError:  # pragma: no cover
    sys.exit("PyMuPDF missing: run with the project venv, e.g. .venv/bin/python tools/pdf_text.py ...")

REF_HEADING = re.compile(r"^(references|bibliography|literature cited)\s*$", re.I)


def page_lines(page):
    """Yield dicts per text line: text, bbox, size, bold. A blank line yields text ''."""
    for block in page.get_text("dict", flags=pymupdf.TEXT_PRESERVE_WHITESPACE)["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block["lines"]:
            spans = [s for s in line["spans"] if s["text"]]
            text = "".join(s["text"] for s in spans).strip()
            visible = [s for s in spans if s["text"].strip()]
            yield {
                "text": text,
                "x0": line["bbox"][0], "y0": line["bbox"][1], "x1": line["bbox"][2], "y1": line["bbox"][3],
                "size": max((s["size"] for s in visible), default=0),
                "bold": bool(visible) and all((s["flags"] & 16) or "bold" in s["font"].lower() for s in visible),
            }


def norm_furniture(t):
    return re.sub(r"\d+", "#", t.strip().lower())


def extract(pdf_path):
    doc = pymupdf.open(pdf_path)
    meta = " ".join(str((doc.metadata or {}).get(k) or "") for k in ("creator", "producer"))
    tex_made = bool(re.search(r"\b(pdf|xe|lua)?(la)?tex\b|tex live|miktex", meta, re.I))  # only TeX hyphenates automatically at line ends
    pages = [list(page_lines(p)) for p in doc]
    sizes = [(p.rect.width, p.rect.height) for p in doc]

    # Running headers/footers: text in the top/bottom 8% that recurs (digits ignored) on >40% of pages.
    furniture = Counter()
    for lines, (_, h) in zip(pages, sizes):
        seen = {norm_furniture(l["text"]) for l in lines if l["text"] and (l["y1"] < 0.08 * h or l["y0"] > 0.92 * h)}
        furniture.update(seen)
    repeated = {t for t, n in furniture.items() if len(pages) > 2 and n > 0.4 * len(pages)}

    body_sizes = [round(l["size"], 1) for lines in pages for l in lines if len(l["text"]) > 40]
    body_size = statistics.mode(body_sizes) if body_sizes else 10

    ordered = []
    for lines, (w, h) in zip(pages, sizes):
        keep = []
        for l in lines:
            t = l["text"]
            if t and (re.fullmatch(r"\d{1,4}", t) or (re.fullmatch(r"(page )?\d+( of \d+)?", t, re.I))):
                continue  # page numbers and manuscript line numbers
            if t and (l["y1"] < 0.08 * h or l["y0"] > 0.92 * h) and norm_furniture(t) in repeated:
                continue
            keep.append(l)
        text_lines = [l for l in keep if l["text"]]
        narrow = [l for l in text_lines if l["x1"] - l["x0"] < 0.55 * w]
        two_col = (len(text_lines) > 10 and len(narrow) > 0.6 * len(text_lines)
                   and any(l["x0"] > 0.45 * w for l in narrow) and any(l["x1"] < 0.55 * w for l in narrow))

        def key(l):
            if not two_col:
                return (0, l["y0"], l["x0"])
            col = 1 if l["x0"] > 0.45 * w else 0
            return (col, l["y0"], l["x0"])

        # Table cells: two or more text lines side by side on the same baseline within one column.
        rows = {}
        for l in text_lines:
            col = 1 if two_col and l["x0"] > 0.45 * w else 0
            rows.setdefault((col, round(l["y0"] / 3)), []).append(l)
        for row in rows.values():
            row.sort(key=lambda l: l["x0"])
            if len(row) > 1 and any(b["x0"] > a["x1"] + 2 for a, b in zip(row, row[1:])):
                for l in row:
                    l["table"] = True
        # Everything inside the vertical span of a table (multi-line header cells, units) belongs to it.
        tables = [l for l in text_lines if l.get("table")]
        if len(tables) >= 4:
            for col in (0, 1):
                cells = [l for l in tables if (1 if two_col and l["x0"] > 0.45 * w else 0) == col]
                if len(cells) >= 4:
                    top, bottom = min(c["y0"] for c in cells) - 30, max(c["y1"] for c in cells)
                    for l in text_lines:
                        same_col = (1 if two_col and l["x0"] > 0.45 * w else 0) == col
                        if same_col and top <= l["y0"] <= bottom and len(l["text"]) < 60:
                            l["table"] = True
        keep = [l for l in keep if not l.get("table")]

        keep.sort(key=key)
        ordered.extend(keep)
        ordered.append({"text": "", "pagebreak": True})

    # Typical gap between consecutive lines inside a paragraph.
    gaps = [b["y0"] - a["y1"] for a, b in zip(ordered, ordered[1:])
            if a.get("text") and b.get("text") and 0 < b["y0"] - a["y1"] < 40]
    line_gap = statistics.median(gaps) if gaps else 3

    out, para, skipping, prev = [], [], False, None

    def flush():
        nonlocal para
        if para and not skipping:
            txt = ""
            for piece in para:
                if txt.endswith("-") and re.search(r"[A-Za-z0-9]-$", txt):
                    if tex_made and re.match(r"[a-z]", piece) and re.search(r"[a-z]-$", txt):
                        txt = txt[:-1] + piece  # undo TeX's end-of-line hyphenation
                    else:
                        txt = txt + piece  # a real hyphen that fell at a line end
                else:
                    txt = f"{txt} {piece}" if txt else piece
            out.append(re.sub(r"\s+", " ", txt).strip())
        para = []

    for l in ordered:
        t = l.get("text", "")
        if l.get("pagebreak"):
            prev = None  # a paragraph can continue across pages
            continue
        if not t:
            flush()
            prev = None
            continue
        is_heading = (len(t) < 90 and not t.endswith((".", ",", ";", ":")) and len(t.split()) <= 12
                      and (l["bold"] or l["size"] > body_size * 1.15) and not re.fullmatch(r"[\W\d]+", t))
        if is_heading:
            flush()
            cont = (prev is not None and prev.get("heading") and abs(prev["size"] - l["size"]) < 0.5
                    and l["y0"] - prev["y1"] < 2.5 * line_gap + 6 and not skipping)
            if cont:  # heading wrapped onto the next line
                out[-1] += " " + t
            else:
                skipping = bool(REF_HEADING.match(t))
                if not skipping:
                    out.append(("# " if l["size"] > body_size * 1.5 else "## ") + t)
            l["heading"] = True
            prev = l
            continue
        if prev is not None and l["y0"] - prev["y1"] > max(1.8 * line_gap, line_gap + 4):
            flush()
        elif prev is not None and l["x0"] - prev["x0"] > 8 and l["y0"] > prev["y0"]:
            flush()  # first-line indent starts a new paragraph
        para.append(t)
        prev = l
    flush()
    cleaned = []
    for para_text in out:
        if para_text.startswith("#"):
            cleaned.append(para_text)
            continue
        para_text = re.sub(r"(?<=[A-Za-z])[\^\"](?=[a-z])", "ff", para_text)  # broken 'ff' ligature glyphs
        tokens = para_text.split()
        numeric = sum(bool(re.fullmatch(r"[\d.,±×x%/:()<>=+\-–−°o]+[a-zA-Z]{0,3}", t)) for t in tokens)
        if len(tokens) >= 4 and numeric > 0.4 * len(tokens):
            continue  # a table row flattened into one line
        if (len(tokens) <= 10 and not re.search(r"[.:;,!?)]$", para_text) and para_text[:1].isupper()
                and not re.search(r"https?://|@", para_text)):
            cleaned.append("### " + para_text)  # unbolded (italic) subheading
            continue
        cleaned.append(para_text)
    md = "\n\n".join(cleaned)
    return f"<!-- extracted from {Path(pdf_path).name} with PyMuPDF; equations may be garbled -->\n\n{md}\n"


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for f in sys.argv[1:]:
        p = Path(f)
        dest = p.with_suffix(".md")
        dest.write_text(extract(p), encoding="utf-8")
        print(f"{dest}  ({len(dest.read_text().split())} words)")


if __name__ == "__main__":
    main()
