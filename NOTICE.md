# Notice

Substantial parts of the case selection, analytic progression, and live-coding structure
are adapted from materials accompanying:

> Gábor Békés and Gábor Kézdi, *Data Analysis for Business, Economics, and Policy*.

## Python course materials

- Project: `gabors-data-analysis/da-coding-python`
- Source: <https://github.com/gabors-data-analysis/da-coding-python>
- Revision consulted: `ac4dcefcb3b6e54e36e21490948e2edb41a13485`
- License: MIT

Adapted topics include the European hotel regressions, binary-outcome health analysis,
cross-validation logic, Airbnb LASSO workflow, World Management Survey feature engineering
and PCA, and the used-car CART workflow. The Coding 2 versions reorganize the material for
six meetings, update it to a Python 3.12 `uv` environment, use local prepared extracts,
emphasize incremental live coding, and add human-first LLM reconstruction audits.

## Textbook case-study code

- Project: `gabors-data-analysis/da_case_studies`
- Source: <https://github.com/gabors-data-analysis/da_case_studies>
- Revision consulted: `3a4ee299e43ff88d71cd609da42410dad3967c64`
- License: MIT

Relevant cases include Chapters 7–8 and 10 (hotel regressions), Chapter 11 (SHARE health),
Chapter 14 (Airbnb prediction), Chapter 15 (used-car regression trees), and the World
Management Survey case material.

## Data

`scripts/fetch_data.py` downloads source files from the OSF records documented in
`data/README.md`, verifies their SHA-256 hashes, and creates smaller teaching extracts.
Downloaded and prepared data are not committed. The datasets remain subject to their
original documentation and terms; the MIT licenses above apply to the source code and
course repositories, not automatically to every underlying dataset.

## Local course contributions

The k-means extension, reconstruction worksheets, current notebook sequencing, validation
checks, and CEU-specific course framing are original adaptations for Coding 2. The software
dependencies listed in `pyproject.toml` remain governed by their respective licenses.
