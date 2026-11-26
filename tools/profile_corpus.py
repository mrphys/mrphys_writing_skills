#!/usr/bin/env python3
"""Phase 1 of docs/style-guide-plan.md: measure the corpus text (no LLM).

Usage:
  python3 tools/profile_corpus.py [--category reconstruction --category segmentation] [--include-holdout]

Reads corpus/index.csv (rows with keep=y, weight=high, status ok*), loads each paper's text
(Europe PMC markdown, PDF-extracted paper.md, or LaTeX converted with pandoc), splits it into canonical
sections and writes:
  corpus/analysis/profile.md     tables: by category, preprint vs published, journal-edit pairs, phrases
  corpus/analysis/profile.json   per-paper, per-section numbers
"""
import argparse
import csv
import json
import re
import shutil
import statistics as st
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"

SECTIONS = [  # (canonical name, heading regex); first match wins
    ("abstract", r"^abstract|^summary$"),
    ("introduction", r"introduction|^background$"),
    ("theory", r"^theory|^background and theory"),
    ("methods", r"method|materials|^experiment"),
    ("results", r"^results?\b"),
    ("discussion", r"^discussion"),
    ("conclusion", r"^conclusions?"),
    ("_drop", r"^(references?|bibliography|acknowledge?ments?|funding( information)?|conflicts? of interest|"
              r"competing interests?|data availability( statement)?|code availability|ethics( statement)?|"
              r"supporting information|supplementary (material|information)s?|associated data|"
              r"author contributions?|declarations?|key ?words|abbreviations|disclosures?)$"),
    ("captions", r"figure and table captions|figure legends?|captions"),
]
ABBREV = r"\b(Fig|Figs|et al|e\.g|i\.e|vs|approx|cf|Eq|Eqs|Ref|Refs|No|Dr|Sect)\."

BRIT_AM = {  # name: (British regex, American regex)
    "-ise/-ize": (r"\b\w+(is(e|ed|es|ing|ation|ations))\b", r"\b\w+(iz(e|ed|es|ing|ation|ations))\b"),
    "haem-/hem-": (r"\bhaem\w*", r"\bhem(o|a|ody)\w*"),
    "artefact/artifact": (r"\bartefact", r"\bartifact"),
    "colour/color": (r"\bcolour", r"\bcolor"),
    "centre/center": (r"\bcentre", r"\bcenter"),
    "modelling/modeling": (r"\bmodell(ing|ed)", r"\bmodel(ing|ed)\b"),
    "labelled/labeled": (r"\blabell(ed|ing)", r"\blabel(ed|ing)\b"),
    "analyse/analyze": (r"\banalys(e|ed|ing)\b", r"\banalyz(e|ed|ing)\b"),
    "paediatric/pediatric": (r"\bpaediatric", r"\bpediatric"),
    "oedema/edema": (r"\boedema", r"\bedema"),
}
ISE_FALSE = {"rise", "wise", "otherwise", "likewise", "noise", "exercise", "precise", "precisely", "concise",
             "expertise", "advise", "surprise", "promise", "premise", "raise", "raised", "praise", "comprise",
             "comprised", "comprises", "enterprise", "devise", "revise", "revised", "supervise", "supervised",
             "arise", "arises", "arising", "noises", "exercises", "exercised", "exercising", "wisely", "rises",
             "rising", "raising", "promising", "comprising", "premises", "surprising", "denoise", "denoised",
             "denoising", "clockwise", "pairwise", "pixelwise", "voxelwise", "elementwise", "pointwise",
             "framewise", "stepwise", "slicewise", "channelwise", "piecewise", "imprecise", "disguise", "chemise"}

IZE_FALSE = {"size", "sizes", "sized", "resize", "resized", "resizing", "prize", "prizes", "seize", "seized",
             "downsize", "downsized", "oversized", "undersized", "capsize"}

HEDGE = ["may", "might", "could", "possibly", "potentially", "likely", "suggest", "suggests", "appears", "approximately"]
CLAIM = ["demonstrate", "demonstrates", "demonstrated", "show", "shows", "showed", "shown", "novel", "significantly",
         "robust", "outperform", "outperforms", "outperformed", "state-of-the-art", "superior", "feasible",
         "promising", "clinically", "accurate", "first"]
OPENERS = ["However,", "Furthermore,", "In addition,", "Additionally,", "Moreover,", "Therefore,", "Thus,",
           "Importantly,", "Finally,", "Firstly,", "Secondly,", "Overall,", "Consequently,", "Specifically,",
           "Nevertheless,", "In this study,", "In this work,", "In this paper,", "This", "These", "To", "We", "It"]
STOP = set("the a an of to in and or for with on by is are was were be been as at from that this these which it its "
           "we our than using used use into between both each all also can not no".split())


# ---------------------------------------------------------------- loading
def tex_to_md(dirpath):
    cache = dirpath / "source.md"
    if cache.exists():
        return cache.read_text(encoding="utf-8")
    mains = [f for f in dirpath.rglob("*.tex") if "\\documentclass" in f.read_text(errors="replace")]
    main = max(mains or dirpath.rglob("*.tex"), key=lambda f: f.stat().st_size)
    md = ""
    if shutil.which("pandoc"):
        try:
            res = subprocess.run(["pandoc", "-f", "latex", "-t", "markdown_strict", "--wrap=none", main.name],
                                 cwd=main.parent, capture_output=True, text=True, timeout=20)
            md = res.stdout
        except subprocess.TimeoutExpired:  # some macro sets make older pandoc loop forever
            pass
    if len(md.split()) < 1000:  # pandoc failed on custom macros: crude fallback
        t = re.sub(r"(?<!\\)%.*", "", main.read_text(errors="replace"))
        t = re.sub(r"\\(sub)*section\*?\{([^}]*)\}", lambda m: "\n## " + m.group(2) + "\n", t)
        t = re.sub(r"\\begin\{abstract\}", "\n## Abstract\n", t)
        t = re.sub(r"\\begin\{(equation|align|figure|table)\*?\}.*?\\end\{\1\*?\}", " ", t, flags=re.S)
        t = re.sub(r"\\(cite|ref|label|eqref)\w*\{[^}]*\}", "", t)
        t = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{([^{}]*)\})?", lambda m: m.group(3) or "", t)
        md = re.sub(r"[{}]", "", t)
    if not re.search(r"^#+\s*abstract", md, re.I | re.M):  # pandoc drops \begin{abstract}
        src = main.read_text(errors="replace")
        a = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", src, re.S) or \
            re.search(r"\\abstract\{(.*?)\}\s*\n\s*\n", src, re.S)
        if a:
            txt = re.sub(r"(?<!\\)%.*", "", a.group(1))
            txt = re.sub(r"\\(textbf|textit|emph)\{([^}]*)\}", r"\2", txt)
            txt = re.sub(r"\\[a-zA-Z]+\*?(\{[^}]*\})?", "", txt)
            md = "## Abstract\n\n" + re.sub(r"[ \t]+", " ", txt).strip() + "\n\n" + md
    cache.write_text(md, encoding="utf-8")
    return md


def load_text(row):
    p = CORPUS / row["path"]
    if p.is_file():
        return p.read_text(encoding="utf-8")
    if (p / "paper.md").exists():
        return (p / "paper.md").read_text(encoding="utf-8")
    return tex_to_md(p)


def split_sections(md):
    secs, cur, abs_parts = defaultdict(list), "_front", set()
    for block in re.split(r"\n\s*\n", md):
        b = block.strip()
        if not b or b.startswith("<!--"):
            continue
        h = re.match(r"^(#{1,6})\s+(.*)$", b) or re.match(r"^()\*\*(abstract)\*\*$", b, re.I)
        if h and "\n" not in b:
            if len(h.group(1)) > 2:
                continue  # subsections never change the section (e.g. "### Ethics statement" inside Methods)
            title = re.sub(r"^[\dIVX.]+\s+", "", h.group(2).strip().strip("*")).lower().strip(" :")
            abs_words = sum(len(x.split()) for x in secs["abstract"])
            part = re.match(r"^(background|purpose|aims?|objectives?|methods?|materials and methods|results?|"
                            r"conclusions?|significance|findings|interpretation)$", title)
            if (cur == "abstract" and part and abs_words < 450 and title not in abs_parts
                    and not (title == "background" and abs_words > 0)):
                abs_parts.add(title)
                continue  # heading inside a structured abstract
            for name, pat in SECTIONS:
                if re.search(pat, title):
                    cur = name
                    break
            continue
        if re.match(r"^(\*\*)?(fig(ure)?\.?|table)\s*\d", b, re.I):
            secs["captions"].append(b)
            continue
        secs[cur].append(b)
    return {k: v for k, v in secs.items() if not k.startswith("_")}


# ---------------------------------------------------------------- measuring
def clean(p):
    p = re.sub(r"\$[^$]*\$|\\\(.*?\\\)", " MATH ", p)
    p = re.sub(r"\[[\d,\s–-]+\]|\(\s*\)", "", p)  # numeric citation brackets left by conversion
    p = re.sub(r"[*_`#]", "", p)
    return re.sub(r"\s+", " ", p).strip()


def sentences(p):
    p = re.sub(ABBREV, lambda m: m.group(0).replace(".", "§"), p)
    out = re.split(r"(?<=[.!?])\s+(?=[A-Z(\[])", p)
    return [s.replace("§", ".") for s in out if len(s.split()) >= 3]


PASSIVE = re.compile(r"\b(is|are|was|were|be|been|being)\s+(\w+ly\s+)?(\w+(ed|en)|made|done|built|set|run|seen|"
                     r"found|shown|given|taken|known|chosen|held|kept|put|split|cut|fed|led|left|lost|sent|spent|"
                     r"thought|told|understood|written)\b", re.I)


def measure(paras):
    text = " ".join(clean(p) for p in paras)
    sents = [s for p in paras for s in sentences(clean(p))]
    words = text.split()
    nw = max(len(words), 1)
    lw = [w.lower().strip(".,;:()") for w in words]
    cnt = Counter(lw)
    per_k = lambda n: round(1000 * n / nw, 2)
    slen = [len(s.split()) for s in sents]
    m = {
        "words": len(words),
        "paragraphs": len(paras),
        "sentences": len(sents),
        "sent_len_mean": round(st.mean(slen), 1) if slen else 0,
        "sent_len_sd": round(st.pstdev(slen), 1) if slen else 0,
        "para_len_sents": round(len(sents) / max(len(paras), 1), 1),
        "passive_share": round(sum(bool(PASSIVE.search(s)) for s in sents) / max(len(sents), 1), 2),
        "we_per_k": per_k(cnt["we"] + cnt["our"] + cnt["us"]),
        "was_were_per_k": per_k(cnt["was"] + cnt["were"]),
        "is_are_per_k": per_k(cnt["is"] + cnt["are"]),
        "hedge_per_k": per_k(sum(cnt[w] for w in HEDGE)),
        "claim_per_k": per_k(sum(cnt[w] for w in CLAIM)),
        "abbrev_defs_per_k": per_k(len(re.findall(r"\(([A-Z][A-Za-z0-9-]*[A-Z0-9])s?\)", text))),
    }
    return m, text, sents


def conventions(text):
    c = {}
    for name, (br, am) in BRIT_AM.items():
        b = re.findall(br, text, re.I)
        if name == "-ise/-ize":
            b = [w for w in re.findall(r"\b\w+is(?:e|ed|es|ing|ation|ations)\b", text, re.I) if w.lower() not in ISE_FALSE]
            a = [w for w in re.findall(r"\b\w+iz(?:e|ed|es|ing|ation|ations)\b", text, re.I)
                 if w.lower() not in IZE_FALSE]
        else:
            a = re.findall(am, text, re.I)
        c[name] = (len(b), len(a))
    c["field: '1.5 T' vs '1.5T'"] = (len(re.findall(r"\b\d(\.\d)?\s+T\b", text)), len(re.findall(r"\b\d(\.\d)?T\b", text)))
    c["units: '10 ms' vs '10ms'"] = (len(re.findall(r"\d\s+(ms|mm|s|cm|min)\b", text)), len(re.findall(r"\d(ms|mm|cm|min)\b", text)))
    c["percent: '10 %' vs '10%'"] = (len(re.findall(r"\d\s+%", text)), len(re.findall(r"\d%", text)))
    c["fig ref: 'Figure N' vs 'Fig. N'"] = (len(re.findall(r"\bFigures?\s+\d", text)), len(re.findall(r"\bFigs?\.\s*\d", text)))
    c["p-value: 'p<' vs 'P<'"] = (len(re.findall(r"\bp\s*[<=>≤]", text)), len(re.findall(r"\bP\s*[<=>≤]", text)))
    c["mean±SD: '±' uses"] = (len(re.findall(r"±", text)), 0)
    c["ranges: en dash vs hyphen"] = (len(re.findall(r"\d\s*–\s*\d", text)), len(re.findall(r"\d-\d", text)))
    c["oxford comma: ', and' vs ' and' in lists"] = (len(re.findall(r"\w+, \w+(?: \w+)?, and\b", text)),
                                                       len(re.findall(r"\w+, \w+(?: \w+)? and\b", text)))
    c["'real-time' vs 'real time'"] = (len(re.findall(r"real-time", text, re.I)), len(re.findall(r"real time", text, re.I)))
    c["'deep learning' vs 'deep-learning'"] = (len(re.findall(r"deep learning", text, re.I)), len(re.findall(r"deep-learning", text, re.I)))
    return c


def openers(sents):
    c = Counter()
    for s in sents:
        for o in OPENERS:
            if s.startswith(o + ("" if o.endswith(",") else " ")):
                c[o] += 1
                break
    return c


def ngrams(text, n):
    toks = re.findall(r"[a-z][a-z-]+", text.lower())
    return {" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1)}


# ---------------------------------------------------------------- report
def fmt_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(out)


def mean_of(papers, sec, key):
    vals = [p["sections"][sec][key] for p in papers if sec in p["sections"] and p["sections"][sec]["words"] > 80]
    return round(st.mean(vals), 2) if vals else "–"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--category", action="append", default=[])
    ap.add_argument("--include-holdout", action="store_true")
    args = ap.parse_args()
    cats = {c.lower() for c in args.category}

    with (CORPUS / "index.csv").open(newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["keep"].strip().lower() == "y" and r.get("weight") == "high"
                and r["status"].startswith("ok") and (args.include_holdout or r.get("holdout") != "y")
                and (not cats or r["category"].split(";")[0] in cats)]

    papers = []
    for r in rows:
        secs = split_sections(load_text(r))
        p = {"id": r["id"], "title": r["title"], "category": r["category"].split(";")[0], "version": r["version"],
             "journal": r["journal"], "sections": {}, "conv": Counter(), "openers": Counter(), "text": ""}
        for name, paras in secs.items():
            m, text, sents = measure(paras)
            p["sections"][name] = m
            p["text"] += " " + text
            p["openers"] += openers(sents)
        allc = conventions(p["text"])
        p["conv"] = allc
        p["sections_found"] = [s for s in ("abstract", "introduction", "theory", "methods", "results", "discussion",
                                           "conclusion", "captions") if s in secs]
        papers.append(p)

    # Pair members that are published copies are excluded from aggregates (their preprint represents them).
    main_set = [p for p in papers if not p["version"].startswith("published (preprint")]
    by_cat = defaultdict(list)
    for p in main_set:
        by_cat[p["category"]].append(p)

    L = ["# Corpus profile", "",
         f"Papers measured: {len(main_set)} (plus {len(papers) - len(main_set)} published copies of preprints, "
         "used only in the journal-editing comparison). Held-out papers excluded." if not args.include_holdout else "", "",
         "Per-1000-word rates are written /k. Section values are means over papers whose section has >80 words.", ""]

    L += ["## Papers", "", fmt_table(["id", "cat", "version", "words", "sections found", "title"],
          [[p["id"], p["category"][:5], p["version"].split(" ")[0], sum(s["words"] for s in p["sections"].values()),
            ",".join(x[:4] for x in p["sections_found"]), p["title"][:60]] for p in papers]), ""]

    keys = [("sent_len_mean", "sentence length"), ("para_len_sents", "sentences/paragraph"),
            ("passive_share", "passive share"), ("we_per_k", "we/our /k"), ("was_were_per_k", "was/were /k"),
            ("is_are_per_k", "is/are /k"), ("hedge_per_k", "hedges /k"), ("claim_per_k", "claim words /k"),
            ("abbrev_defs_per_k", "abbrev defs /k")]
    secs = ["abstract", "introduction", "methods", "results", "discussion", "conclusion"]
    for cat, group in [("all", main_set)] + sorted(by_cat.items()):
        L += [f"## Section profile: {cat} (n={len(group)})", "",
              fmt_table(["metric"] + secs, [[lbl] + [mean_of(group, s, k) for s in secs] for k, lbl in keys]
                        + [["words"] + [mean_of(group, s, "words") for s in secs]]), ""]

    # Version: preprint vs published, all categories
    pre = [p for p in main_set if p["version"].startswith("preprint")]
    pub = [p for p in main_set if p["version"].startswith("published")]
    L += [f"## Preprint (n={len(pre)}) vs published (n={len(pub)}), whole text", "",
          fmt_table(["metric", "preprint", "published"],
                    [[lbl, mean_of([{"sections": {"x": _whole(p)}} for p in pre], "x", k),
                      mean_of([{"sections": {"x": _whole(p)}} for p in pub], "x", k)] for k, lbl in keys]), ""]

    # Conventions
    conv_names = list(main_set[0]["conv"]) if main_set else []
    L += ["## Conventions (counts: first form / second form)", "",
          "Columns: total across preprints, total across published, papers using only the first form, only the second, both.", "",
          fmt_table(["convention", "preprints", "published", "only 1st", "only 2nd", "both"],
                    [[n, "%d / %d" % tuple(map(sum, zip(*[p["conv"][n] for p in pre]))) if pre else "–",
                      "%d / %d" % tuple(map(sum, zip(*[p["conv"][n] for p in pub]))) if pub else "–",
                      sum(p["conv"][n][0] > 0 and p["conv"][n][1] == 0 for p in main_set),
                      sum(p["conv"][n][1] > 0 and p["conv"][n][0] == 0 for p in main_set),
                      sum(p["conv"][n][0] > 0 and p["conv"][n][1] > 0 for p in main_set)] for n in conv_names]), ""]

    # Journal-editing pairs
    byid = {p["id"]: p for p in papers}
    pairs = [(p, byid.get(re.search(r"published: (\S+)\)", p["version"]).group(1)))
             for p in papers if "published:" in p["version"]]
    pairs = [(a, b) for a, b in pairs if b]
    if pairs:
        L += ["## Journal editing: preprint → published copy of the same paper", "",
              "Conventions that flip between the two versions are set by the journal, not by the group.", ""]
        for a, b in pairs:
            flips = [[n, "%d / %d" % a["conv"][n], "%d / %d" % b["conv"][n]] for n in conv_names
                     if (a["conv"][n][0] > a["conv"][n][1]) != (b["conv"][n][0] > b["conv"][n][1])
                     and sum(a["conv"][n]) + sum(b["conv"][n]) > 2]
            L += [f"**{a['title'][:80]}** ({a['id']} → {b['id']}, {b['journal']})", "",
                  fmt_table(["convention", "preprint", "published"], flips) if flips else "_no convention flips_", ""]

    # Sentence openers
    op = Counter()
    for p in main_set:
        op += p["openers"]
    nsent = sum(s["sentences"] for p in main_set for s in p["sections"].values())
    L += ["## Sentence openers (per 1000 sentences, all papers)", "",
          fmt_table(["opener", "/1000 sentences", "papers using it"],
                    [[o, round(1000 * n / max(nsent, 1), 1), sum(p["openers"][o] > 0 for p in main_set)]
                     for o, n in op.most_common(20)]), ""]

    # Recurrent phrases: 4- and 5-grams used in many papers
    L += ["## Recurrent phrases (4–5 word sequences in ≥ 30% of papers)", ""]
    for n in (5, 4):
        df = Counter()
        for p in main_set:
            df.update(g for g in ngrams(p["text"], n) if sum(w not in STOP for w in g.split()) >= 2)
        thresh = max(3, int(0.3 * len(main_set)))
        common = [(g, c) for g, c in df.most_common(400) if c >= thresh][:30]
        L += [f"**{n}-word**: " + "; ".join(f"“{g}” ({c})" for g, c in common), ""]

    out = CORPUS / "analysis"
    out.mkdir(exist_ok=True)
    (out / "profile.md").write_text("\n".join(L), encoding="utf-8")
    (out / "profile.json").write_text(json.dumps(
        [{k: (dict(v) if isinstance(v, Counter) else v) for k, v in p.items() if k != "text"} for p in papers],
        indent=1, default=list), encoding="utf-8")
    print(f"wrote {out / 'profile.md'} ({len(papers)} papers)")


def _whole(p):
    """Word-weighted whole-paper metrics from section metrics."""
    secs = [s for s in p["sections"].values() if s["words"]]
    tot = sum(s["words"] for s in secs) or 1
    keys = [k for k in secs[0] if k not in ("words", "paragraphs", "sentences")] if secs else []
    w = {k: round(sum(s[k] * s["words"] for s in secs) / tot, 2) for k in keys}
    w["words"] = tot
    return w


if __name__ == "__main__":
    main()
