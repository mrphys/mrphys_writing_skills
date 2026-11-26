#!/usr/bin/env python3
"""Deterministic style checks for LaTeX manuscripts.

Usage: python3 lint_tex.py <file.tex> [more.tex ...] [--rules path/to/lint-rules.json]

Reports banned phrases, non-preferred variants and acronyms used before definition.
Output lines are `file:line: [rule] message` so they are easy to act on. Stdlib only.
"""
import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_RULES = Path(__file__).resolve().parent.parent / "references" / "lint-rules.json"

# Environments whose contents are not prose.
SKIP_ENVS = ("equation", "align", "figure*", "verbatim", "lstlisting", "tabular")


def strip_comments(line: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", line)


def prose_lines(text: str):
    """Yield (line_no, line) for prose lines, skipping comments and non-prose environments."""
    depth = 0
    for i, raw in enumerate(text.splitlines(), 1):
        line = strip_comments(raw)
        for env in SKIP_ENVS:
            e = re.escape(env)
            depth += len(re.findall(r"\\begin\{" + e + r"\}", line))
            depth -= len(re.findall(r"\\end\{" + e + r"\}", line))
        if depth <= 0 and line.strip():
            depth = max(depth, 0)
            yield i, line


def lint(path: Path, rules: dict):
    text = path.read_text(encoding="utf-8", errors="replace")
    findings = []
    defined = set(rules.get("acronyms_no_definition_needed", []))
    acronym_def = re.compile(r"\(([A-Z][A-Za-z0-9+\-]*[A-Z0-9+])s?\)")
    acronym_use = re.compile(r"(?<![\\{$_A-Za-z])([A-Z][A-Z0-9+\-]{1,}[A-Z0-9+])(?:s)?\b")

    for n, line in prose_lines(text):
        low = line.lower()
        for r in rules.get("banned_phrases", []):
            if re.search(r["pattern"], low):
                findings.append((n, "banned-phrase", r["message"]))
        for r in rules.get("patterns", []):  # case-sensitive
            if re.search(r["pattern"], line):
                findings.append((n, "convention", r["message"]))
        for v in rules.get("preferred_variants", []):
            for bad in v["instead_of"]:
                if re.search(r"(?<![\w$_])" + re.escape(bad) + r"(?![\w}])", line):
                    findings.append((n, "variant", f"use '{v['use']}' instead of '{bad}'"))
        # Definitions on this line count before uses on the same line.
        defined.update(m.group(1) for m in acronym_def.finditer(line))
        for m in acronym_use.finditer(line):
            acr = m.group(1)
            if acr not in defined:
                findings.append((n, "acronym", f"'{acr}' used before definition"))
                defined.add(acr)  # report once per acronym
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    args = ap.parse_args()
    rules = json.loads(args.rules.read_text())
    total = 0
    for f in args.files:
        for n, rule, msg in lint(f, rules):
            print(f"{f}:{n}: [{rule}] {msg}")
            total += 1
    print(f"{total} finding(s)", file=sys.stderr)
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
