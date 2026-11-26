# mrphys-writing

A Claude Code plugin for drafting and reviewing papers in the group's house style.

## Install (group members)
```
/plugin marketplace add <git-url-of-this-repo>
/plugin install mrphys-writing@mrphys
```
For local development: `/plugin marketplace add /path/to/this/folder`.

## Contents
| Path | Purpose |
|---|---|
| `skills/draft-section` | Draft or rewrite a section from notes/outline in group style |
| `skills/style-review` | Check a manuscript against the style guide; report or apply edits |
| `references/style-guide.md` | **The group style** — single source of truth, loaded by every skill |
| `references/lint-rules.json` | Machine-checkable rules (banned phrases, notation variants, acronyms) |
| `references/exemplars/` | Model paragraphs from published group papers |
| `scripts/lint_tex.py` | Deterministic checker: `python3 scripts/lint_tex.py paper.tex` |
| `templates/paper-CLAUDE.md` | Per-paper context file to copy into each paper repo |
| `corpus/` | Source papers for building the style guide (git-ignored) |
| `tools/build_corpus.py` | Finds group papers on Europe PMC + arXiv and downloads their text (see `corpus/README.md`) |

## Changing the style
Edit `references/style-guide.md` (and `lint-rules.json` for mechanical rules) via pull request, so the
group agrees on changes. Bump `version` in `.claude-plugin/plugin.json` when releasing.
