# Coding 2: Python for Data Analysis (ECBS5306)

**Academic year** 2026–2027 · **Term** Fall · **Host unit** Department of Economics
**Course level** 7 · **US credits** 1 · **ECTS credits** 2
**Instructor** Ulrich Wohak, PhD · [wohaku@ceu.edu](mailto:wohaku@ceu.edu)
**Meetings** Mondays, 15:40–17:20 · 2 November – 7 December 2026 (6 sessions) · Room TBC
**Course repository** `Coding-2-Python-for-Data-Analysis`

---

## Background and overall aim

**Content.** Coding 2 builds on Coding 1 by moving from foundational Python programming
to applied statistical learning workflows. Students use Python to prepare data, fit and
interpret models, evaluate predictive performance, and communicate analytic results. The
course begins with linear regression and progresses through classification, validation,
regularization, unsupervised learning, and regression trees.

**Relevance.** Regression and related statistical-learning methods are foundational tools
in social science research and industry. They help analysts describe associations, make
predictions, quantify uncertainty, and assess whether results generalize beyond the data
used to fit a model. The course emphasizes not only obtaining output, but also deciding
whether a workflow and its conclusions are trustworthy.

**Position in the sequence.** Coding 1 develops the ability to read and write Python
without AI assistance. Coding 2 puts that foundation to work in larger analytic projects.
Students first build each classroom analysis with the instructor; only then does the class
ask an LLM to reconstruct the workflow and compare the result with the human-built
analysis. Individual LLM use is concentrated in the debugging homeworks. Students remain
responsible for every submitted result and must independently verify AI suggestions.

## Course prerequisites

- ECBS5293 Data Science 1.
- ECBS5294 Data Science 2.
- ECBS5208 Coding 1: Introduction to Python.
- Students are expected to bring their own laptops to every class.

Students should be comfortable with Python variables, data structures, functions,
conditionals, loops, file paths, pandas, plotting, Git, and GitHub. Before Session 1,
students should install `uv`, clone the course repository, and run:

```bash
uv sync
uv run python scripts/fetch_data.py
```

## Waiting list handling

The published study guide lists the following waiting-list priorities:

1. Economics.
2. Department of Network and Data Science and exchange students.
3. All other students meeting the prerequisite criteria.

## Learning outcomes

**Key outcomes.** By the end of the course, students will be able to:

- Build and interpret simple and multiple linear regression models.
- Represent categorical variables, interactions, and nonlinear relationships in a model.
- Diagnose common modeling problems and use appropriate transformations.
- Model binary outcomes with logistic regression and evaluate probability predictions.
- Separate model fitting from model evaluation through holdout and cross-validation
  workflows.
- Use reproducible preprocessing pipelines and tune regularized models without data
  leakage.
- Apply principal component analysis and clustering to explore unlabeled data.
- Fit, tune, and interpret regression trees.
- Communicate model assumptions, limitations, and results clearly.
- Translate a completed analysis into a precise specification and audit an LLM
  reconstruction against the executed evidence.

**Other outcomes.** The course will also develop:

- *Critical thinking* — identify software and analytic errors and decide whether results
  are credible.
- *Quantitative reasoning* — connect modeling choices to the variation in the data and to
  out-of-sample performance.
- *Technology skills* — use Python modeling libraries, JupyterLab, `uv`, Git, and GitHub in
  reproducible projects.
- *Interpersonal communication skills* — explain model output and debugging decisions to
  technical and nontechnical audiences.
- *AI judgment* — use an LLM as an assistant while testing its claims against code, data,
  documentation, and course concepts.

## Learning activities and teaching methods

The course consists of six interactive 100-minute meetings. Students write and discuss the
course notebooks alongside the instructor. They predict results, interpret output, and
make modeling choices as the workflow develops. After completing the human analysis,
each student develops their own prompt, inspects an LLM reconstruction, and identifies
differences in vocabulary, order, implementation, numerical results, and claims. The
human-built and executed notebook remains the reference analysis. Students work locally
in a reproducible `uv` environment.

Homework is completed outside class in separate, intentionally buggy GitHub repositories.
Each homework mirrors the lecture material and asks students to work as an analyst
reviewing a colleague's notebook: reproduce the problem, correct the code, check the
analytic logic, and make the notebook's interpretation consistent with the evidence. This
is where students may also use an LLM individually, while testing and explaining every proposed
change.

## Assessment

Grading is based on a total score out of 100, in line with CEU Department of Economics and
Business grading guidelines. In particular:

- The median student can expect to receive a B+.
- Probably no more than one third of students can expect to receive an A or A−.
- The passing grade is 50%.

The final grade is based on:

| Component | Weight | Detail |
| --- | --- | --- |
| Debugging homeworks | 40% | Six homeworks, one per session. Every homework contributes equally to this component. |
| Closed-book final exam | 60% | Written, closed-book, and no computer. Covers the entire course. The registrar will announce the exam slot. |

### Debugging homeworks

Each homework is a stand-alone GitHub template repository containing a small local
dataset, an `analysis.ipynb` notebook, a `pyproject.toml`, and setup instructions. The
notebook contains at least one software-development error that prevents a correct run and
at least one analytic error that can produce a plausible but incorrect conclusion.

For each homework, students must:

1. Create their own copy of the assigned repository and set up its environment with
   `uv sync`.
2. Run the notebook from top to bottom and reproduce the original failure or suspect
   result.
3. Correct every issue they identify without replacing the intended analytic workflow.
4. Complete the notebook's interpretation prompt using the corrected evidence.
5. Confirm that the final notebook runs from a clean kernel from top to bottom.
6. Commit and push the completed work according to the submission instructions released
   with the assignment.

Homework is assessed on reproducibility, correction of the software and analytic errors,
and whether the interpretation follows from the corrected results. Students must be able
to explain their changes. Deadlines and the submission channel are announced with each
assignment.

## AI and LLM policy

**Human analysis comes first.** During class, students build the analysis with the
instructor before an LLM is used. At the end of each meeting, students each develop their
own prompt asking an LLM to reconstruct the completed workflow. They check what the
response omitted, reordered, renamed, implemented differently, or interpreted incorrectly.
Generated code does not replace the course notebook.

For debugging homeworks, students may use LLMs and AI-enabled coding tools to explain
unfamiliar errors, propose diagnoses, and suggest repairs. Students may not delegate the
entire homework or its interpretation to an AI system and submit the output without
verification.

AI output is a stochastic draft, not an authority. Students are responsible for checking
suggested code against the data, running the complete workflow, consulting documentation,
and deciding whether the analysis is sound. They must be able to explain every line and
every conclusion in submitted work.

AI tools are allowed for the debugging homeworks unless an assignment states otherwise,
but not during the closed-book final exam. This includes LLMs and other machine-learning
writing or coding tools such as ChatGPT, GitHub Copilot, Gemini, Claude, Grammarly, DeepL,
and comparable tools.

## Course contents and schedule

The six scheduled meetings cover nine connected topics stored in numbered lecture folders.
Folder numbers do not identify separate meeting dates: one meeting can cover several
topics, and a topic may continue into a later meeting. There is one debugging homework per
session, for six in total. Assignment releases identify the repository and submission arrangements.

### Session 1 — 2 November · Introduction and simple linear regression

- Analytic questions, outcomes, predictors, and sources of confounding using European
  hotel-price data.
- Simple linear regression, residuals, prediction, and interpreting a slope with units.
- Course introduction and the reproducible project workflow.
- Materials: `lectures/lecture00-intro/` and `lectures/lecture12-simple-linear-regression/`.
- Reconstruction audit: turn the completed regression workflow into an explicit
  specification and compare it with an LLM reconstruction.
- Homework: one assignment on simple linear regression.

### Session 2 — 9 November · Regression workflow, features, and diagnostics

- Continue multiple regression and workflow design, then categorical predictors,
  reference categories, interactions, and model comparison using
  European hotel-price data.
- Residual diagnostics, heteroscedasticity, transformations, and back-transforming
  predictions.
- Materials: `lectures/lecture13-multiple-regression-workflow/`,
  `lectures/lecture14-categorical-variables-interactions/`, and
  `lectures/lecture15-diagnostics-transformations/`.
- Reconstruction audit: check whether an LLM preserves the specification, diagnostic
  sequence, transformations, and interpretation units.
- Homework: one debugging assignment, announced with its release.

### Session 3 — 16 November · Logistic regression

- Binary outcomes, log odds, odds ratios, and probability predictions using SHARE health
  data.
- Classification thresholds, class imbalance, classification metrics, and ROC AUC.
- Materials: `lectures/lecture16-logistic-regression/`.
- Reconstruction audit: compare probability modeling, marginal effects, calibration, and
  threshold choices.
- Homework: one debugging assignment on the session material.

### Session 4 — 23 November · Validation, resampling, and regularization

- Holdout validation, cross-validation, uncertainty across folds, and model complexity
  using Airbnb listings in Hackney.
- Preprocessing pipelines, scaling, encoding, Ridge and Lasso regression, and data leakage.
- Materials: `lectures/lecture17-validation-resampling/` and
  `lectures/lecture18-regularization-pipelines/`.
- Reconstruction audit: look for data leakage, inconsistent splits, preprocessing outside
  the pipeline, and misuse of the final test set.
- Homework: one debugging assignment on the session material.

### Session 5 — 30 November · Unsupervised learning

- Standardization, principal component analysis, k-means clustering, and silhouette
  scores using World Management Survey data.
- Building useful cluster summaries without using an outcome label during fitting.
- Materials: `lectures/lecture19-unsupervised-learning/`.
- Reconstruction audit: check scaling, PCA interpretation, cluster selection, and whether
  outcomes were improperly used while fitting clusters.
- Homework: one debugging assignment on the session material.

### Session 6 — 7 December · Regression trees and synthesis

- Regression-tree structure, tuning depth and leaf size, and honest test-set evaluation
  using used-car price data.
- Feature importance, model visualization, interpretability, and comparison with linear
  models.
- Course synthesis and final-exam preparation.
- Materials: `lectures/lecture20-regression-tree/`.
- Reconstruction audit: compare tuning logic, final evaluation, feature importance, and
  claims about interpretation.
- Homework: one debugging assignment on the session material.

## Course materials and reproducibility

All required lecture materials are stored in the course repository. The notebooks use
local, documented teaching extracts from datasets accompanying the Gábor Békés and Gábor
Kézdi data-analysis materials: European hotels, SHARE health, Airbnb listings, the World
Management Survey, and used-car prices. Source attribution and preparation decisions are
documented in `NOTICE.md` and `data/README.md`. After cloning the repository, students
create the environment and teaching data with:

```bash
uv sync
uv run python scripts/fetch_data.py
```

The nine populated lecture notebooks are grouped into six meetings. The `prompts/`
directory contains the six post-analysis reconstruction worksheets. Each homework
repository has its own environment and local dataset. Follow the README in that repository
and run `uv sync` before opening its notebook. Do not install packages from inside a
notebook.

The official module description is available in the
[CEU Study Guide](https://ceu.studyguide.timeedit.net/modules/ECBS5306?mainTab=module&type=CORE).
The current meeting dates are published in the
[CEU public timetable](https://cloud.timeedit.net/at_ceu/web/public/ri1Y7w9QQQwZY3QYZ5W3780Xy767.html).
