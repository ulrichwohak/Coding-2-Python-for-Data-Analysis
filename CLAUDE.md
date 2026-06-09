# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Course materials for **Coding 2: Python for Data Analysis** (MSc Business Analytics, CEU). This is a teaching repository, not an application: the "code" is mostly Jupyter notebooks (`lectures/`) plus three Python support scripts. Sessions run from simple linear regression (session 12) through regression trees (session 20). Treat correctness, reproducibility, and the conventions below as the product.

`course repo.md` (gitignored, local-only) is the authoritative spec for how this repo is structured and how a future course should be built the same way. Read it before any structural change. `AGENTS.md` (also gitignored) holds standing instructions — currently: do not remove the `AI Attribution` section from `README.md`.

## Commands

`uv` is the only supported environment tool. Never use `pip`/`pipenv`/`%pip`/`!pip` in student-facing files — `check_no_pip.py` fails CI on those (the only allowed mention is a warning telling students not to use them).

```bash
uv sync                                   # create/update the env from uv.lock
uv run python scripts/fetch_data.py       # generate data/raw/*.csv (required before notebooks run)
```

Full local acceptance sequence — this mirrors CI (`.github/workflows/checks.yml`) and must pass before finishing work:

```bash
uv lock --check
uv sync --locked
uv run python scripts/fetch_data.py
uv run python scripts/check_no_pip.py
uv run python scripts/check_notebooks.py
```

For documentation-only changes, at minimum run `uv run python scripts/check_no_pip.py`.

There is no unit-test suite. The two `check_*.py` scripts are the test gate; they validate files statically and never execute notebooks. To check one notebook, point the script's logic at it or just run the full check — it reports failures per file/cell with paths.

GitHub work goes through the `gh` CLI; the token lives in `.secrets.md` (gitignored — keep it secret).

## Architecture and conventions

**Per-session layout.** Each session N pairs an in-repo lecture (`lectures/lectureN-topic/`: a `README.md` + one `topic.ipynb`) with a row in `schedule/session_plan.md`; adding or renaming a session means updating both. Homework is *not* stored here — it is a separate GitHub repo per lecture, `ulrichwohak/coding2-debug-N-topic` (see the session plan for links). Dataset/topic names use snake_case for files inside a lecture; directories use `lectureN-topic` with matching topic slugs.

**Data flow.** Notebooks never download data and never read remote URLs. `scripts/fetch_data.py` deterministically generates (seeded RNG) three synthetic CSVs into `data/raw/`, which is gitignored except `.gitkeep`. Notebooks read them via local relative paths `data/raw/<name>.csv` and are meant to be opened from the repo root. The datasets:
- `career_outcomes.csv` — regression + classification (salary, promotion).
- `housing_sales.csv` — nonlinear structure for validation, transformations, trees.
- `campaign_response.csv` — classification, pipelines, clustering.

To add or change teaching data, edit `fetch_data.py` (keep it seeded/deterministic) and document it in `data/README.md` — do not commit generated CSVs.

**Notebook standards enforced by `check_notebooks.py`.** Every notebook must be valid JSON; use kernelspec `display_name: "Python 3 (ipykernel)"` / `name: "python3"`; have code cells with `execution_count: null` and **no stored outputs** (clear outputs before committing); contain only `markdown`/`raw`/`code` cells; and have syntactically valid Python in every code cell (`ast.parse`). No `read_csv("http...")`, `read_excel("http...")`, or pip commands. Because every code cell must parse, avoid pseudo-code or `...`-style fragments in code cells — put prose in markdown.

**Local-only files (gitignored), do not commit:** `.secrets.md`, `AGENTS.md`, `course repo.md`, `.venv/`, `data/raw/*`. The `.gitignore` excludes these intentionally; don't "fix" it by tracking them.

## Pedagogical constraints that affect edits

- The course teaches responsible LLM use (scoping/planning + debugging). Lecture READMEs include an "LLM Practice" note tied to the session — preserve that pattern when editing lectures.
- Homework debugging repos (intentionally buggy forks) are created as **separate** repositories, never inside this one.
- Homework lives in separate per-lecture debugging repos (`ulrichwohak/coding2-debug-N-topic`), each a stand-alone `uv` project that mirrors the lecture and ships with one seeded software bug (a hard error) plus one silent, lecture-specific analytic bug; the corrected version is kept on a `solutions` branch. They are not part of this repo.
- Dependencies live in `pyproject.toml` (Python `>=3.12,<3.13`); change them via `uv` so `uv.lock` stays in sync and `uv lock --check` passes.
