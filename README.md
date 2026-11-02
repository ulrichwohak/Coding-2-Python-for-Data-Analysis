# Coding 2: Python for Data Analysis

Course materials and environment for **Coding 2: Python for Data Analysis** in the MSc
Business Analytics Program at CEU.

The course meets on Mondays from 15:40 to 17:20, 2 November–7 December 2026. The room is
still to be confirmed.

## Course overview

Coding 2 continues from the first course in the programming sequence and develops applied
statistical-learning workflows in Python. The course moves from regression to probability
models, honest validation, regularization, unsupervised learning, and regression trees.
Students learn to connect an analytic question to code, evidence, model limitations, and a
reproducible decision process.

The central classroom method is **human-first live coding**. Students build each notebook
with the instructor before an LLM is introduced. At the end of each scheduled meeting, the
students each develop their own prompt asking an LLM to reconstruct the completed
workflow. They audit the generated responses against the human-built notebook for
vocabulary, ordering, implementation, numerical results, and analytic correctness.

LLM use continues through the separate debugging homeworks. Students may use an
LLM to propose diagnoses and fixes, but they remain responsible for executing, testing,
interpreting, and explaining every change.

## Setup

Install `uv`, clone this repository, and run:

```bash
uv sync --locked
uv run python scripts/fetch_data.py
uv run jupyter lab
```

Open a module notebook in VS Code or JupyterLab and run its setup cells first. The setup
finds the project folder and sets `data_dir`, so loading data works from either the project
root or the notebook's own folder. A terminal and a notebook kernel can have different
working folders.

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
You> Create a Python file that reads data/raw/hotels_course.csv and prints its column names.
Created analysis.py
```

Generated files are saved in the terminal's current folder and appear in VS Code. The tool
shows a diff and asks before replacing existing files; originals are backed up locally.
It does not execute generated code. Inspect, run, test, and explain the result yourself.

Follow-up requests can revise files created in the current session. To share an existing
text file, use `/add analysis.py` (its contents will be sent to CEU with the next request).
Use `/new` for a new conversation, `/model` to change model, and `/quit` to exit. Pasted
multiline requests are sent together when you press Enter.

Credentials and backups stay in the Git-ignored `.ceu/` folder. Never put the class secret
in a prompt, notebook, or tracked file. Run `uv run ceu.py --setup` to replace saved
credentials. The credentials file is not encrypted; anyone who can read it can recover the
shared secret. Conversation history is kept only for the current session. The class account
shares CEU's configured request and spending limits.

## Repository materials

- `modules/`: nine substantive topic modules, grouped into six meetings, plus the course introduction.
- [Course introduction](modules/module00-intro/): slides in PDF and editable PowerPoint formats.
- `prompts/`: six human-first reconstruction and audit worksheets.
- `data/README.md`: dataset sources, extract definitions, and preparation decisions.
- `scripts/fetch_data.py`: downloads verified source files and creates local course extracts.
- `scripts/build_notebooks.py`: reproducibly builds the module notebooks from reviewable cells.
- `scripts/execute_notebooks.py`: executes each module in a fresh kernel without modifying sources.
- `scripts/check_no_pip.py`: enforces the course environment policy in student-facing files.
- `scripts/check_notebooks.py`: validates notebook JSON, metadata, syntax, outputs, and data references.
- `schedule/session_plan.md`: dates, pacing, reconstruction prompts, and debugging homeworks.
- `Coding-2-Python-for-Data-Analysis-Syllabus.md`: full course syllabus.

## Six-session structure

Sessions are scheduled class meetings. Modules are topic units: one meeting can cover
several modules, and a module can continue into a later meeting. The plan below shows the
intended grouping. See the [dated session plan](schedule/session_plan.md) for module links
and homework information.

1. Course introduction and simple linear regression using the European hotels case.
2. Continue multiple regression, categorical variables, interactions, diagnostics, and transformations using the same case.
3. Logistic regression, probability evaluation, and classification using SHARE health data.
4. Validation, pipelines, Ridge, and LASSO using Airbnb listings in Hackney.
5. PCA and clustering using the World Management Survey.
6. Regression trees and course synthesis using used-car prices.

Each 100-minute meeting combines live coding, individual LLM reconstruction, and discussion
of the comparison. Pacing depends on progress through the modules. Optional notebook
extensions provide additional depth when the live coding moves quickly.

## Assessment

- **Debugging homeworks: 40%.** Six homeworks, one per session, equally weighted within this component.
- **Final exam: 60%.** Written, closed-book, and without a computer. The registrar will announce the slot.
- **Passing threshold: 50/100 overall.**

Assignment releases specify deadlines and submission instructions. The
[syllabus](Coding-2-Python-for-Data-Analysis-Syllabus.md) contains the full assessment policy.

## Learning outcomes

By the end of the course, students should be able to:

- build and interpret regression, probability, regularization, clustering, PCA, and tree workflows;
- translate a substantive question into an ordered, reproducible analysis specification;
- evaluate models with appropriate diagnostics, cross-validation, and untouched holdout data;
- place learned preprocessing inside resampling workflows and detect data leakage;
- distinguish probability prediction from classification and justify a decision threshold;
- communicate coefficients, predictions, uncertainty, residuals, and limitations with correct units;
- compare hand-built and LLM-generated workflows without treating unfamiliar terminology as authority;
- use LLMs for reconstruction and debugging while independently testing every claim.

## AI and LLM policy

Module analysis is completed by hand with the instructor before any LLM reconstruction.
Each student's prompt functions as an analytic specification: it records the question,
data, required steps, outputs, constraints, and checks. Generated responses are stochastic
comparison objects and are not canonical course solutions.

LLMs may be used in the debugging homeworks unless an assignment says otherwise. Students
must be able to explain every submitted line and conclusion. LLMs and other AI-enabled
writing or coding tools are not permitted during the closed-book final exam.

This policy applies to Coding 2. Coding 1 remains a separate course in which students do not
use AI tools or LLMs for coursework.

## Validation

Run the CI-equivalent checks with:

```bash
uv lock --check
uv sync --locked
uv run python scripts/fetch_data.py
uv run python scripts/check_no_pip.py
uv run python scripts/check_notebooks.py
uv run python scripts/execute_notebooks.py
uv run python scripts/test_ceu.py
```

The execution check starts each fresh kernel in the notebook's own folder, matching a
normal notebook launch, without changing the committed files. To also check execution
from the project root:

```bash
uv run python scripts/execute_notebooks.py --working-directory project
```

## Attribution and licensing

The repository is distributed under the MIT License. The case progression and substantial
parts of the analytic structure are adapted from the MIT-licensed Gábor Békés and Gábor
Kézdi Python and textbook case-study repositories. See `NOTICE.md` for pinned revisions,
dataset handling, and detailed attribution.

## AI Attribution

This repository was created and developed with assistance from OpenAI language models. The
statement documents the creation process for the repository materials; it does not replace
the human-first Coding 2 policy above or alter Coding 1's prohibition on student AI use.
