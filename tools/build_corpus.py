#!/usr/bin/env python3
"""Build a style corpus of group papers from Europe PMC (open-access full text) and arXiv (LaTeX source).

Two steps, so nothing is downloaded until you have checked the list:

  1. Search (fast, metadata only) -> writes corpus/index.csv with a `keep` column:
     python3 tools/build_corpus.py search --orcid 0000-0002-1825-0097 \
         --author "Smith JA" --arxiv-author "Jane Smith" --affiliation "University College London" --since 2018
  2. Suggest a category per paper (reconstruction / segmentation / computational / acquisition / clinical / review / other;
     anything using deep learning is limited to segmentation or reconstruction) from
     title + abstract, using the editable keyword rules in tools/category_rules.json:
     python3 tools/build_corpus.py classify
  3. Open index.csv, fix categories and set keep=n on rows you don't want, then download all or some:
     python3 tools/build_corpus.py download [--category reconstruction --category segmentation]
     Some arXiv preprints have no LaTeX source, only a PDF. Run download with .venv/bin/python (PyMuPDF installed)
     to convert those to text automatically, or convert them later with the `extract` command.

Downloads to:
  corpus/epmc/<PMCID>.md          section-structured text (abstract, body, figure captions)
  corpus/arxiv/<id>/...           extracted LaTeX source (.tex/.bib/.bbl/.sty/.cls only)

Names are ambiguous ("Smith J" matches many people): prefer --orcid, and use --affiliation.

Stdlib only. Nothing is uploaded except the search terms sent to the two public APIs.
"""
import argparse
import csv
import gzip
import html
import io
import json
import re
import sys
import tarfile
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

UA = {"User-Agent": "corpus-builder/0.1 (research style corpus; python-urllib)"}
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
ARXIV_API = "https://export.arxiv.org/api/query"
KEEP_EXT = {".tex", ".bib", ".bbl", ".sty", ".cls", ".bst"}


def get(url, binary=False, retries=3):
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                data = r.read()
                return data if binary else data.decode("utf-8", errors="replace")
        except Exception as e:  # noqa: BLE001
            if attempt == retries - 1:
                raise
            print(f"  retry ({e})", file=sys.stderr)
            time.sleep(3 * (attempt + 1))


def clean_title(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(t or ""))).strip().rstrip(".")


def norm_title(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


# ---------------------------------------------------------------- Europe PMC
def epmc_search(query):
    cursor, out = "*", []
    while True:
        params = {"query": query, "format": "json", "resultType": "core", "pageSize": 100, "cursorMark": cursor}
        res = json.loads(get(f"{EPMC}/search?{urllib.parse.urlencode(params)}"))
        out += res.get("resultList", {}).get("result", [])
        nxt = res.get("nextCursorMark")
        if not nxt or nxt == cursor or not res.get("resultList", {}).get("result"):
            return out
        cursor = nxt


def text_of(el):
    """Flatten a JATS element to text, using LaTeX for formulas where the XML provides it."""
    if el is None:
        return ""
    parts = [el.text or ""]
    for ch in el:
        tag = ch.tag.split("}")[-1]
        if tag in ("inline-formula", "disp-formula"):
            tex = ch.find(".//tex-math")
            if tex is not None and (tex.text or "").strip():
                t = re.sub(r"\\documentclass.*?\\begin\{document\}|\\end\{document\}", "", tex.text, flags=re.S).strip()
                parts.append(t if t.startswith("$") else f"${t}$")
            else:
                parts.append(" ".join(ch.itertext()))
        elif tag == "xref":
            parts.append(f"[{''.join(ch.itertext())}]")
        elif tag in ("fig", "table-wrap"):
            pass  # captions are collected separately
        else:
            parts.append(text_of(ch))
        parts.append(ch.tail or "")
    return re.sub(r"[ \t\r\f\v]+", " ", "".join(parts)).strip()


def jats_to_md(xml_text, meta):
    root = ET.fromstring(xml_text)
    lines = [f"# {meta['title']}", "",
             f"<!-- {meta['journal']} {meta['year']} | {meta['doi']} | {meta['pmcid']} | license: {meta['license']} -->", ""]
    abstract = root.find(".//abstract")
    if abstract is not None:
        lines += ["## Abstract", ""]
        for node in abstract.iter():
            tag = node.tag.split("}")[-1]
            if tag == "title":
                lines += [f"**{text_of(node)}**", ""]
            elif tag == "p":
                lines += [text_of(node), ""]

    def walk_sec(sec, level):
        t = sec.find("title")
        if t is not None:
            lines.extend(["#" * min(level, 6) + " " + text_of(t), ""])
        for ch in sec:
            tag = ch.tag.split("}")[-1]
            if tag == "p":
                lines.extend([text_of(ch), ""])
            elif tag == "sec":
                walk_sec(ch, level + 1)
            elif tag in ("list",):
                for item in ch.findall(".//list-item"):
                    lines.append("- " + " ".join(text_of(p) for p in item.findall("p")))
                lines.append("")
            elif tag == "disp-formula":
                tex = ch.find(".//tex-math")
                if tex is not None:
                    lines.extend([f"$$ {text_of(tex)} $$", ""])

    body = root.find(".//body")
    if body is not None:
        for sec in body.findall("sec"):
            walk_sec(sec, 2)
        for p in body.findall("p"):
            lines.extend([text_of(p), ""])

    caps = []
    for fig in root.iter():
        tag = fig.tag.split("}")[-1]
        if tag in ("fig", "table-wrap"):
            label = text_of(fig.find("label"))
            cap = fig.find("caption")
            if cap is not None:
                caps.append(f"**{label}** " + " ".join(text_of(c) for c in cap if c.tag.split('}')[-1] in ('title', 'p')))
    if caps:
        lines += ["## Figure and table captions", ""] + [c + "\n" for c in caps]
    return "\n".join(lines)


def safe_extract(data, dest):
    """Extract only LaTeX-related files from an arXiv e-print, refusing absolute or '..' paths."""
    dest.mkdir(parents=True, exist_ok=True)
    raw = gzip.decompress(data) if data[:2] == b"\x1f\x8b" else data
    if raw.lstrip()[:5] == b"%PDF-":  # author submitted a PDF only; there is no LaTeX source
        (dest / "paper.pdf").write_bytes(raw)
        return "pdf-only"
    try:
        with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
            for m in tf.getmembers():
                p = Path(m.name)
                if not m.isfile() or p.is_absolute() or ".." in p.parts or p.suffix.lower() not in KEEP_EXT:
                    continue
                target = dest / p
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(tf.extractfile(m).read())
    except tarfile.ReadError:
        if raw.lstrip()[:1] in (b"\\", b"%"):  # a single gzipped .tex file
            (dest / "main.tex").write_bytes(raw)
        else:
            return "no-tex-source (PDF only)"
    return "ok" if any(dest.rglob("*.tex")) else "no-tex-source"


def pdf_to_md(dest):
    """Convert dest/paper.pdf to dest/paper.md if PyMuPDF is available. Returns the new status or None."""
    pdf = dest / "paper.pdf"
    if not pdf.exists():
        return None
    if (dest / "paper.md").exists():
        return "ok (pdf text)"
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import pdf_text
    except SystemExit:  # PyMuPDF not installed in this interpreter
        return None
    (dest / "paper.md").write_text(pdf_text.extract(pdf), encoding="utf-8")
    return "ok (pdf text)"


FIELDS = ["keep", "holdout", "weight", "category", "category_source", "version", "source", "id", "year", "journal",
          "title", "group_authors", "aff_match", "n_authors", "pubtype", "doi", "license", "path", "status"]
RULES = Path(__file__).resolve().parent / "category_rules.json"


def read_index(index):
    with index.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:  # tolerate indexes written before a column existed
        for k in FIELDS:
            r.setdefault(k, "")
    return rows


def write_index(index, rows):
    with index.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def group_authors(rec, names, orcids, affiliation):
    """Return (n_authors, 'Name@position;...', affiliation-matched?) for the listed group members."""
    authors = rec.get("authorList", {}).get("author", [])
    hits, aff_ok = [], False
    for i, a in enumerate(authors, 1):
        orcid = (a.get("authorId") or {}).get("value", "")
        if any(a.get("fullName", "").lower() == n.lower() for n in names) or orcid in orcids:
            pos = "last" if i == len(authors) and i > 1 else str(i)
            hits.append(f"{a.get('fullName', '')}@{pos}")
            affs = " ".join(x.get("affiliation", "") for x in (a.get("authorAffiliationDetailsList") or {}).get("authorAffiliation", []))
            affs += " " + a.get("affiliation", "")
            if affiliation and affiliation.lower() in affs.lower():
                aff_ok = True
    return len(authors), ";".join(hits), ("y" if aff_ok else "n") if affiliation else ""


# ---------------------------------------------------------------- search
def search_epmc(args, rows, seen):
    clauses = [f'AUTH:"{a}"' for a in args.author] + [f'AUTHORID:"{o}"' for o in args.orcid]
    if not clauses:
        return
    q = f"({' OR '.join(clauses)}) AND IN_EPMC:y AND NOT SRC:PPR"
    if args.since:
        q += f" AND PUB_YEAR:[{args.since} TO 3000]"
    if args.affiliation:
        q += f' AND AFF:"{args.affiliation}"'
    print(f"Europe PMC query: {q}", file=sys.stderr)
    recs = epmc_search(q)
    print(f"  {len(recs)} records with full text in Europe PMC", file=sys.stderr)
    for rec in recs:
        title = clean_title(rec.get("title"))
        if not rec.get("pmcid") or norm_title(title) in seen:
            continue
        seen.add(norm_title(title))
        pubtype = "; ".join(rec.get("pubTypeList", {}).get("pubType", []))
        n, hits, aff = group_authors(rec, args.author, args.orcid, args.affiliation)
        skip = re.search(r"review|editorial|letter|comment|erratum|correction", pubtype, re.I) and "research" not in pubtype.lower()
        rows.append({"keep": "n" if skip else "y", "source": "epmc", "id": rec["pmcid"], "year": rec.get("pubYear", ""),
                     "journal": rec.get("journalInfo", {}).get("journal", {}).get("title", ""), "title": title,
                     "group_authors": hits, "aff_match": aff, "n_authors": n, "pubtype": pubtype,
                     "doi": rec.get("doi", ""), "license": rec.get("license", ""),
                     "path": f"epmc/{rec['pmcid']}.md", "status": "not downloaded"})


def search_arxiv(args, rows, seen):
    ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    for name in args.arxiv_author:
        q = f'au:"{name}"'
        if args.arxiv_cats:
            q += " AND (" + " OR ".join(f"cat:{c}" for c in args.arxiv_cats) + ")"
        print(f"arXiv query: {q}", file=sys.stderr)
        feed = ET.fromstring(get(f"{ARXIV_API}?{urllib.parse.urlencode({'search_query': q, 'max_results': 300})}"))
        time.sleep(3)
        entries = feed.findall("a:entry", ns)
        print(f"  {len(entries)} records", file=sys.stderr)
        for e in entries:
            title = clean_title(e.findtext("a:title", "", ns))
            year = e.findtext("a:published", "", ns)[:4]
            if norm_title(title) in seen or (args.since and year and int(year) < args.since):
                continue
            seen.add(norm_title(title))
            aid = e.findtext("a:id", "", ns).rsplit("/abs/", 1)[-1]
            authors = [a.findtext("a:name", "", ns) for a in e.findall("a:author", ns)]
            hits = [f"{a}@{'last' if i == len(authors) and i > 1 else i}" for i, a in enumerate(authors, 1)
                    if a.lower() in (x.lower() for x in args.arxiv_author)]
            rows.append({"keep": "y", "source": "arxiv", "id": aid, "year": year,
                         "journal": e.findtext("x:journal_ref", "", ns), "title": title, "group_authors": ";".join(hits),
                         "aff_match": "", "n_authors": len(authors), "pubtype": "preprint", "doi": e.findtext("x:doi", "", ns),
                         "license": "", "path": "arxiv/" + re.sub(r"[^\w.\-]", "_", aid), "status": "not downloaded"})


# ---------------------------------------------------------------- classify
def fetch_abstracts(rows, cache_path):
    """Fill a {id: abstract} cache from Europe PMC (batched by PMCID) and arXiv (batched id_list)."""
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    need = [r for r in rows if r["id"] not in cache]
    epmc_ids = [r["id"] for r in need if r["source"] == "epmc"]
    for i in range(0, len(epmc_ids), 40):
        q = " OR ".join(f"PMCID:{x}" for x in epmc_ids[i:i + 40])
        for rec in epmc_search(q):
            cache[rec.get("pmcid", "")] = re.sub(r"<[^>]+>", " ", html.unescape(rec.get("abstractText", "")))
    ns = {"a": "http://www.w3.org/2005/Atom"}
    ax_ids = [r["id"] for r in need if r["source"] == "arxiv"]
    for i in range(0, len(ax_ids), 50):
        batch = ax_ids[i:i + 50]
        feed = ET.fromstring(get(f"{ARXIV_API}?{urllib.parse.urlencode({'id_list': ','.join(batch), 'max_results': len(batch)})}"))
        for e in feed.findall("a:entry", ns):
            aid = e.findtext("a:id", "", ns).rsplit("/abs/", 1)[-1]
            cache[aid] = re.sub(r"\s+", " ", e.findtext("a:summary", "", ns)).strip()
        time.sleep(3)
    cache_path.write_text(json.dumps(cache, indent=1, ensure_ascii=False), encoding="utf-8")
    return cache


def suggest_category(title, abstract, pubtype, rules):
    """Return (label, reason). See the _comment in category_rules.json for the order rules are applied in."""
    rv = rules.get("review", {})
    if (rv.get("pubtype") and re.search(rv["pubtype"], pubtype or "", re.I)
            and not re.search(r"research-article", pubtype or "", re.I)) \
            or any(re.search(pat, title, re.I) for pat in rv.get("title", [])):
        return "review", "review"
    scores = {}
    for cat, pats in rules["categories"].items():
        sc = 0
        for pat in pats:
            if re.search(pat, title, re.I):
                sc += rules["title_weight"]
            elif re.search(pat, abstract, re.I):
                sc += rules.get("abstract_weight", {}).get(cat, 1)
        scores[cat] = sc
    dl = rules.get("deep_learning", {})
    is_dl = any(re.search(pat, f"{title} {abstract}", re.I) for pat in dl.get("patterns", []))
    pool = dl["allowed"] if is_dl else list(rules["categories"])
    ranked = sorted(pool, key=lambda c: -scores[c])  # stable: earlier categories win ties
    top = ranked[0]
    if not is_dl and scores[top] < rules["min_score"]:
        return "other", ""
    labels = [top] + [c for c in ranked[1:2] if scores[c] and scores[c] >= rules["secondary_fraction"] * scores[top]]
    return ";".join(labels), "deep-learning" if is_dl else ""


def classify(rows, outdir, overwrite):
    rules = json.loads(RULES.read_text())
    abstracts = fetch_abstracts(rows, outdir / "abstracts.json")
    for r in rows:
        if r["category"] and r["category_source"] != "auto" and not overwrite:
            continue  # never touch a hand-set label
        r["category"], why = suggest_category(r["title"], abstracts.get(r["id"], ""), r.get("pubtype", ""), rules)
        r["category_source"] = "auto"
        print(f"  {r['category']:<28} {why:<14} {r['title'][:70]}", file=sys.stderr)


# ---------------------------------------------------------------- download
def download(row, outdir):
    dest = outdir / row["path"]
    if dest.exists():
        if row["source"] == "arxiv":
            if any(dest.rglob("*.tex")):
                return "ok"
            if (dest / "paper.pdf").exists():
                return pdf_to_md(dest) or "pdf-only"
        else:
            return "ok"
    if row["source"] == "arxiv":
        status = safe_extract(get(f"https://arxiv.org/e-print/{row['id']}", binary=True), dest)
        time.sleep(3)  # arXiv asks for <= 1 request / 3 s
        if status == "pdf-only":
            status = pdf_to_md(dest) or status
        return status
    meta = {k: row[k] for k in ("title", "journal", "year", "doi", "license")} | {"pmcid": row["id"]}
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(jats_to_md(get(f"{EPMC}/{row['id']}/fullTextXML"), meta), encoding="utf-8")
    time.sleep(0.3)
    return "ok"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="find candidate papers and write index.csv (no downloads)")
    s.add_argument("--orcid", action="append", default=[], help="ORCID iD (repeatable) - most reliable")
    s.add_argument("--author", action="append", default=[], help='Europe PMC name, e.g. "Smith JA" (repeatable)')
    s.add_argument("--arxiv-author", action="append", default=[], help='full name for arXiv, e.g. "Jane Smith" (repeatable)')
    s.add_argument("--affiliation", help='e.g. "University College London"; filters Europe PMC hits')
    s.add_argument("--since", type=int, help="earliest publication year")
    s.add_argument("--arxiv-cats", nargs="*", default=["physics.med-ph", "eess.IV", "eess.SP", "cs.CV", "cs.LG"])
    c = sub.add_parser("classify", help="suggest a category per paper from title+abstract (rules in tools/category_rules.json)")
    c.add_argument("--overwrite", action="store_true", help="also relabel rows whose category was set by hand")
    sub.add_parser("extract", help="convert pdf-only downloads to text (run with .venv/bin/python, needs PyMuPDF)")
    d = sub.add_parser("download", help="download every row of index.csv with keep=y")
    d.add_argument("--category", action="append", default=[],
                   help="only download rows with this category (repeatable; matches primary or secondary label)")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "corpus")
    args = ap.parse_args()
    index = args.out / "index.csv"

    if args.cmd == "search":
        if not (args.author or args.orcid or args.arxiv_author):
            ap.error("give at least one --orcid, --author or --arxiv-author")
        rows, seen = [], set()
        search_arxiv(args, rows, seen)  # first, so LaTeX source wins over XML for the same paper
        search_epmc(args, rows, seen)
        args.out.mkdir(parents=True, exist_ok=True)
        for r in rows:
            r.setdefault("category", ""); r.setdefault("category_source", "")
        write_index(index, sorted(rows, key=lambda r: r["year"], reverse=True))
        print(f"\n{len(rows)} candidates ({sum(r['keep'] == 'y' for r in rows)} keep=y). "
              f"Review {index}, then run: classify, download", file=sys.stderr)
        return

    rows = read_index(index)
    if args.cmd == "classify":
        classify(rows, args.out, args.overwrite)
        write_index(index, rows)
        print(f"\nCategories written to {index}. Edit any wrong ones by hand: "
              "hand-set labels are kept on re-runs.", file=sys.stderr)
        return

    if args.cmd == "extract":
        for row in rows:
            if row["status"] == "pdf-only":
                row["status"] = pdf_to_md(args.out / row["path"]) or "pdf-only"
                if row["status"] == "pdf-only":
                    sys.exit("PyMuPDF not found: run with .venv/bin/python tools/build_corpus.py extract")
                print(f"  {row['id']:<22} {row['status']:<14} {row['title'][:60]}", file=sys.stderr)
        write_index(index, rows)
        return

    wanted = {c.lower() for c in args.category}
    for row in rows:
        if row["keep"].strip().lower() != "y":
            continue
        if wanted and not wanted & {c.strip().lower() for c in row["category"].split(";")}:
            continue
        try:
            row["status"] = download(row, args.out)
        except Exception as e:  # noqa: BLE001
            row["status"] = f"failed: {e}"
        print(f"  {row['id']:<22} {row['status']:<12} {row['title'][:60]}", file=sys.stderr)
        write_index(index, rows)  # after every paper, so an interrupted run keeps its progress
    write_index(index, rows)
    print(f"\n{sum(r['status'] == 'ok' for r in rows)} papers in corpus.", file=sys.stderr)


if __name__ == "__main__":
    main()
