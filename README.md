# Coding 2: Python for Data Analysis

Course materials and environment for **Coding 2: Python for Data Analysis** in the MSc Business Analytics Program at CEU.

Dates, room, and institutional calendar details are still to be confirmed.

## Course Overview

Coding 2 continues from the first course in the programming sequence and moves into applied statistical learning workflows in Python. The course begins with linear regression and ends with regression trees, emphasizing reproducible data analysis, model interpretation, validation, and responsible use of large language models in analytic software production.

Students work locally from this repository. Required notebooks, exercises, scripts, and synthetic teaching datasets live here so that the course can be run from a reproducible `uv` environment.

## Repository Materials

- `lectures/`: session folders from simple linear regression through regression trees.
- `exercises/`: short 10-20 minute practice notebooks tied to the session plan.
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

Each lecture directory contains a local README and a runnable notebook. Exercises are shorter companion notebooks for practice or homework.

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
