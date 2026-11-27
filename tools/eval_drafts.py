#!/usr/bin/env python3
"""Phase 6 of docs/style-guide-plan.md: compare original vs guided vs baseline drafts of held-out papers.

Layout (all under corpus/eval/, git-ignored):
  originals/<id>/<section>.md          extracted from the held-out paper
  drafts/guided/<id>/<section>.(tex|md)   written with the draft-section skill
  drafts/baseline/<id>/<section>.(tex|md) written with no style guide
Sections: introduction, discussion, conclusion.

Writes:
  report.md        measurements, lint findings and signature moves per version, plus a summary
  blind/<id>-<section>.md + blind/key.json   A/B/C packs with citations stripped, for human judges
"""
import json
import random
import re
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "scripts"))
import profile_corpus as pc  # noqa: E402
import lint_tex  # noqa: E402

EVAL = ROOT / "corpus" / "eval"
SECTIONS = ["introduction", "discussion", "conclusion"]
VERSIONS = ["original", "guided", "baseline"]
METRICS = [("sent_len_mean", "sentence length"), ("passive_share", "passive share"), ("we_per_k", "we/our /k"),
           ("hedge_per_k", "hedges /k"), ("claim_per_k", "claim words /k"), ("words", "words")]
MOVES = {
    "introduction": [("aims sentence", r"\b(aims?|objectives?|purpose) of (this|the|our) (study|work|paper)"),
                     ("inline (i) list", r"\(i\)|\bi\)|\b1\)"), ("'Unfortunately,'", r"\bUnfortunately,"),
                     ("'However,'", r"\bHowever,"), ("own prior work", r"\b[Ww]e have (previously|recently)"),
                     ("contribution bullets", r"(?m)^\s*([-*•]|\\item)"), ("'novel'", r"\bnovel\b")],
    "discussion": [("'main finding(s)'", r"\bmain findings?\b"), ("'To our knowledge'", r"\bTo our knowledge"),
                   ("'We believe'", r"\b[Ww]e believe"), ("limitation opener", r"\b(main limitation|several limitations|limitations? of (this|our|the) (study|work))"),
                   ("'Nevertheless,'", r"\bNevertheless,"), ("'It should be noted'", r"\bIt should be noted"),
                   ("'novel'", r"\bnovel\b")],
    "conclusion": [("demonstrated / feasible", r"demonstrates? the potential|successfully demonstrated|is feasible|we have (shown|demonstrated)"),
                   ("'Thus, we believe'", r"\bThus, we believe"), ("future work in conclusion", r"\b[Ff]uture (work|studies)"),
                   ("'novel'", r"\bnovel\b")],
}


def find(version, pid, sec):
    base = EVAL / ("originals" if version == "original" else f"drafts/{version}") / pid
    for ext in (".md", ".tex"):
        if (base / f"{sec}{ext}").exists():
            return base / f"{sec}{ext}"
    return None


def latex_to_text(t):
    t = re.sub(r"(?<!\\)%.*", "", t)
    t = re.sub(r"\\(sub)*section\*?\{[^}]*\}", "", t)
    t = re.sub(r"\\(textbf|textit|emph)\{([^}]*)\}", r"\2", t)
    t = t.replace("--", "–").replace("\\%", "%").replace("~", " ").replace("$\\pm$", "±")
    t = re.sub(r"\$([^$]*)\$", r"\1", t)
    return t


def strip_citations(t):
    t = re.sub(r"\s*\\cite[pt]?\{[^}]*\}", "", t)
    t = re.sub(r"\s*\[\s*R?\d+(\s*[,–-]\s*R?\d+)*\s*\]", "", t)
    t = re.sub(r"\s*\[\s*TODO[^\]]*\]", "", t)
    t = re.sub(r"\s*\((\d+)(\s*[,–-]\s*\d+)*\)", "", t)
    t = re.sub(r"(?<=[a-z)])(\d{1,2}(?:[,–-]\d{1,2})*)(?=[\s.,;:])", "", t)  # superscripts from PDF text
    return t


def paragraphs(path):
    t = path.read_text(encoding="utf-8")
    if path.suffix == ".tex":
        t = latex_to_text(t)
    return [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip() and not p.strip().startswith("#")]


def main():
    rules = json.loads((ROOT / "references" / "lint-rules.json").read_text())
    ids = sorted(p.name for p in (EVAL / "originals").iterdir() if p.is_dir())
    L = ["# Phase 6: held-out drafting test", "",
         "Original = the held-out paper's own text. Guided = drafted with the draft-section skill (style guide,",
         "category file, exemplars). Baseline = drafted from the same notes with no style guide.", ""]
    dist = {v: [] for v in ("guided", "baseline")}
    lintc = {v: [] for v in VERSIONS}
    movehits = {v: 0 for v in VERSIONS}
    agree = {v: 0 for v in ("guided", "baseline")}
    movetot = 0
    rng = random.Random(6)
    key = {}
    for pid in ids:
        L += [f"## {pid}", ""]
        for sec in SECTIONS:
            paths = {v: find(v, pid, sec) for v in VERSIONS}
            if not all(paths.values()):
                L += [f"### {sec}: missing {[v for v, p in paths.items() if not p]}", ""]
                continue
            m, texts, lints = {}, {}, {}
            for v, p in paths.items():
                paras = paragraphs(p)
                m[v], _, _ = pc.measure([strip_citations(x) for x in paras])
                texts[v] = "\n\n".join(paras)
                lints[v] = len(lint_tex.lint(p, rules))
                lintc[v].append(lints[v])
            L += [f"### {sec}", "", pc.fmt_table(["metric"] + VERSIONS,
                  [[lbl] + [m[v][k] for v in VERSIONS] for k, lbl in METRICS]
                  + [["lint findings"] + [lints[v] for v in VERSIONS]]), ""]
            rows = []
            for name, pat in MOVES[sec]:
                hits = {v: bool(re.search(pat, texts[v])) for v in VERSIONS}
                rows.append([name] + ["✓" if hits[v] else "·" for v in VERSIONS])
                if "novel" not in name and "bullets" not in name and "future work in" not in name:
                    movetot += 1
                    for v in VERSIONS:
                        movehits[v] += hits[v]
                    for v in agree:
                        agree[v] += hits[v] == hits["original"]
            L += [pc.fmt_table(["signature move"] + VERSIONS, rows), ""]
            for v in ("guided", "baseline") if sec != "conclusion" else ():  # conclusions too short to measure
                d = [abs(m[v][k] - m["original"][k]) / (abs(m["original"][k]) + 1) for k, _ in METRICS[:-1]]
                dist[v].append(st.mean(d))
            order = VERSIONS[:]
            rng.shuffle(order)
            key[f"{pid}-{sec}"] = dict(zip("ABC", order))
            B = [f"# {pid} · {sec}", "",
                 "Three versions of the same section, in random order, with citations removed. Which one",
                 "sounds most like our group? Which least? What gives each one away?", ""]
            for lab, v in zip("ABC", order):
                B += [f"## Version {lab}", "", strip_citations(texts[v]), ""]
            (EVAL / "blind").mkdir(exist_ok=True)
            (EVAL / "blind" / f"{pid}-{sec}.md").write_text("\n".join(B), encoding="utf-8")
    (EVAL / "blind" / "key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    L[5:5] = ["## Summary", "",
              pc.fmt_table(["", "original", "guided", "baseline"], [
                  ["signature moves present", f"{movehits['original']}/{movetot}", f"{movehits['guided']}/{movetot}",
                   f"{movehits['baseline']}/{movetot}"],
                  ["lint findings (total)", sum(lintc["original"]), sum(lintc["guided"]), sum(lintc["baseline"])],
                  ["moves matching the original (used iff the original uses them)", "–",
                   f"{agree['guided']}/{movetot}", f"{agree['baseline']}/{movetot}"],
                  ["mean distance from original on style metrics, intro + discussion (lower = closer)", "0",
                   round(st.mean(dist["guided"]), 3) if dist["guided"] else "–",
                   round(st.mean(dist["baseline"]), 3) if dist["baseline"] else "–"]]),
              "", "Originals predate the group decisions, so their lint findings are mostly old conventions.", ""]
    (EVAL / "report.md").write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {EVAL / 'report.md'} and {len(key)} blind packs")


if __name__ == "__main__":
    main()
