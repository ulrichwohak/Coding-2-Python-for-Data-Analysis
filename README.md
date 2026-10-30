# Coding 2: Python for Data Analysis

Course materials and environment for **Coding 2: Python for Data Analysis** in the MSc Business Analytics Program at CEU.

Dates, room, and institutional calendar details are still to be confirmed.

## Course Overview

Coding 2 continues from the first course in the programming sequence and moves into applied statistical learning workflows in Python. The course begins with linear regression and ends with regression trees, emphasizing reproducible data analysis, model interpretation, validation, and responsible use of large language models in analytic software production.

Students work locally from this repository. Required notebooks, scripts, and synthetic teaching datasets live here so that the course can be run from a reproducible `uv` environment. Homework is delivered as separate per-lecture debugging repositories that students clone and fix.

## Repository Materials

- `lectures/`: session folders from simple linear regression through regression trees.
- Homework debugging repositories: one stand-alone, intentionally buggy repo per lecture (listed in `schedule/session_plan.md`) that students clone and correct.
- `data/`: documentation and generated raw teaching datasets.
- `scripts/fetch_data.py`: creates the local teaching datasets.
- `scripts/check_no_pip.py`: checks that student-facing files use the course environment policy.
- `scripts/check_notebooks.py`: validates notebook JSON, metadata, syntax, and data-reference conventions.
- `schedule/session_plan.md`: ordered session plan with placeholders for unconfirmed dates.

## Setup

Install `uv`, clone this repository, then run:

```bash
uv sync
uv run python scripts/fetch_data.py
```

Open the notebooks from the repository root after syncing the environment and generating data.

For local validation, run:

```bash
uv lock --check
uv sync --locked
uv run python scripts/fetch_data.py
uv run python scripts/check_no_pip.py
uv run python scripts/check_notebooks.py
```

## CEU AI in the VS Code terminal

Use the assistant for the class reconstruction activity after human-first coding, or when
an assignment permits AI. From your local course folder, open a VS Code terminal and run:

```bash
uv run ceu.py
```

The first launch asks for the shared class client ID and secret supplied separately by the
instructor, then lets you choose an available model. Setup is remembered locally; the
secret is hidden while you enter it. Later launches go straight to the prompt.

Type or paste a request and press Enter, for example:

```text
You> Create a Python file that prints the mean of 10, 20, and 30.
Created analysis.py
```

Generated files are saved in the terminal's current folder and appear in VS Code. The tool
shows a diff and asks before replacing existing files; originals are backed up locally.
It does not execute generated code. Inspect, run, test, and explain the result yourself.

Follow-up requests can revise files created in the current session. To share an existing
text file, use `/add analysis.py` (its contents will be sent to CEU with the next request).
Use `/new` for a new conversation, `/model` to change model, and `/quit` to exit. Pasted
multiline requests are sent together when you press Enter.

Credentials and backups stay in the Git-ignored `.ceu/` folder. The credentials file is
not encrypted; anyone who can read it can recover the shared secret. Never put the class
secret in a prompt, notebook, or tracked file. Run `uv run ceu.py --setup` to replace saved
credentials. Conversation history is kept only for the current session. The class account
shares CEU's configured request and spending limits.

## Course Structure

The course is organized as nine substantive sessions:

1. Simple linear regression.
2. Multiple regression and workflow design.
3. Categorical variables and interactions.
4. Diagnostics, residuals, and transformations.
5. Logistic regression for classification.
6. Train/test validation and resampling.
7. Regularization and feature pipelines.
8. Unsupervised learning with clustering and PCA.
9. Regression trees.

Each lecture directory contains a local README and a runnable notebook. Homework for each session is a separate debugging repository (see `schedule/session_plan.md`): a stand-alone analytic project that mirrors the lecture and ships with seeded bugs for students to find and fix.

## Learning Outcomes

By the end of the course, students should be able to:

- Build and interpret regression, classification, clustering, and tree-based models in Python.
- Design reproducible data-analysis workflows with local data files and clear environment management.
- Evaluate models with appropriate diagnostics and validation strategies.
- Translate analytic questions into modeling plans before writing code.
- Use LLMs responsibly for project scoping, implementation planning, and debugging while independently checking correctness.

## AI And LLM Policy

Coding 2 explicitly teaches responsible use of LLMs in analytic software production. Students will practice using LLMs to scope projects, compare implementation plans, review model assumptions, and debug intentionally flawed codebases. LLM outputs must be treated as stochastic drafts that require revision, testing, and independent judgment.

This policy applies to Coding 2. It does not change Coding 1: Coding 1 itself will not use AI tools or LLMs for student course work.

## Attribution And Licensing

The repository is distributed under the MIT License in `LICENSE`.

Attribution details for repository materials are recorded in `NOTICE.md`. Required student materials are stored locally in this repository.

## AI Attribution

This repository was created and developed with assistance from OpenAI language models. The attribution describes the creation process for the repository materials; it is not a statement about student use of AI tools in Coding 1.
