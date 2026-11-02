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
The LLM's code may be more advanced or more complicated than the live-coded version.
Understanding and critically evaluating that code is part of the exercise; generated
implementations are not restricted to beginner-level techniques.

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

Open this repository folder in VS Code, select its `.venv` kernel, and open a module
notebook (or use JupyterLab). Kernels use the notebook's own folder; the VS Code workspace
setting makes this explicit. Data loading is a plain call such as
`pd.read_csv("../../data/raw/hotels_course.csv")`: `../..` goes up two folders to the
repository root. Restart an existing kernel after changing its working-folder setting.

## CEU AI in the VS Code terminal

Use the assistant for the class reconstruction activity after human-first coding, or when
an assignment permits AI. From your local course folder, open a VS Code terminal and run:

```bash
uv run ceu-ai.py
```

The first launch asks for the shared class client ID and secret supplied separately by the
instructor. The app automatically uses **Gemini 3.1 Flash-Lite**; there is no model-selection step.
Setup is remembered locally, and the secret is hidden while you enter it. Later launches
go straight to the prompt. Any model choice saved by an older version is ignored.
If Gemini 3.1 Flash-Lite is unavailable, the app stops rather than switching to another model.

You only need to say **what to create, where to put it, and what analysis to do**. For example:

```text
Create llm_regression.ipynb in the simple linear regression module.
Use the hotel dataset. Show descriptive statistics for price and distance,
draw a scatterplot, and regress price on distance.
```

The app automatically supplies:

- [harness.md](harness.md): the teacher-editable module/data map, verified hotel variable
  meanings, notebook layout, and the reconstruction exercise's coding-style policy;
- a filtered folder tree;
- a fresh catalogue of the five approved course extracts: availability, exact column
  names, types inferred by pandas, and row counts, without row values.

The guide and catalogue are rebuilt for each student prompt and included in every API
call, including file-inspection and correction calls. You do not need to attach the guide
or list variable names. The model can request the selected dataset's preview and relevant
supporting documentation; you will see `Reading ...` messages. If data is missing, run
`uv run python scripts/fetch_data.py` before trying again. If the guide is missing, the app
warns you to restore `harness.md`; it does not silently invent its contents.

The guide handles mechanics, not your analytical decisions: specify any sample restriction
(for example, Vienna hotels), transformation, or special model specification you want.
It does not direct the model to add these silently. If a choice is ambiguous, the model
should ask. Check the generated analysis yourself; context does not guarantee correctness.

Generated files are saved relative to the terminal's current folder and appear in VS Code.
Requested additions, edits, and file deletions apply automatically, without a confirmation
prompt. Afterwards, the app lists each file as `Created`, `Updated`, or `Deleted`.
Before replacing or deleting a file, it saves the original under `.ceu/backups/` and
prints that backup folder. To recover it, copy the corresponding backup to its original
location in VS Code. A fresh clone can restore published material, but not unpushed work.
Deletion is limited to individual existing files, never directories. Credentials,
hidden files, raw datasets, existing CSV datasets, the app, and the guide stay protected.
It does not execute generated code. Inspect, run, test, and explain the result yourself.
The model can return notebook cells as structured data; the app adds the standard Python
notebook metadata and valid cell IDs before saving. Both standard notebook source
formats (text or a list of lines) are accepted. If the model's reply format, generated
code, or notebook structure is invalid, the app reports the problem and requests one
correction when a model call remains. This is one correction in total per student prompt,
not one for every kind of error. A rejected reply is kept only in memory for that
correction; it is not saved or printed. No changes are applied until the whole proposal
passes validation. A reply containing only a message is accepted as an explanation,
with no file changes. Edits made in VS Code while the model is answering still stop a
replacement or deletion so your newer work is not overwritten.

For a CSV read, the app sends a summary: exact column names, types inferred by pandas, row
count, and up to the first five rows. Only this summary is sent, not the full dataset. Long text
values in the preview are shortened. The app reads CSV files up to 10 MB locally; it does
not run an analysis. Existing CSV datasets and all files in `data/raw/` are protected from
overwriting. Only keep data you are permitted to send to CEU in the course workspace.

Ask about existing files in ordinary language. The filename can appear anywhere in
your prompt; no special opening phrase or `/add` command is required. Asking to edit
a file also tells the model to inspect it first. For example:

```text
I want to try a quadratic model. In
modules/module12-simple-linear-regression/llm_lin_reg.ipynb, replace both
regression formulas with second-degree polynomials in distance.
Keep the other analysis unchanged.
```

The model interprets your request and requests relevant file contents through the app;
you will see `Reading ...` messages. Notebooks are not all uploaded at startup. You may
paste an absolute path from VS Code if it is inside this project. `/add path` remains an
optional way to supply a file before the model's first reply.

To keep reconstruction independent, the model is instructed not to copy completed
classroom notebooks or `scripts/build_notebooks.py` unless you ask to use that material.
It is also instructed to respect negations and distinguish quoted examples from requests.
These are instructions to the model, not a language parser or a guarantee of perfect
interpretation. Use `/drop path` when you want the app to block a file or folder from
future reads regardless of the model's interpretation. Excluded paths remain excluded
until explicitly re-enabled. Existing files cannot be replaced without first being read.
Files read or created in the current chat remain available for follow-ups. The model
cannot edit `harness.md`; the instructor can edit it directly in VS Code.

The app can read `.py`, `.ipynb`, `.md`, `.txt`, `.csv`, and `pyproject.toml` files. Text
files and total request context have size limits. Hidden files, environment folders,
symbolic links, credential-named files, local agent instructions, and private assessment
folders are excluded. Saved CEU credentials are also checked for before sending content.
Keep secrets in `.ceu/` or another excluded location, not in ordinary course files:
filename checks cannot identify every kind of confidential content.

Use `/context` to preview the automatic course guide and dataset catalogue without sending
them to CEU, and `/tree` to inspect project paths. The tree is limited to 400 entries. Each prompt
allows at most three rounds of file inspection, with up to four files per round, followed
by a final response (at most four model calls, including any source correction). File
inspection and correction can therefore consume more tokens than a single request.
There is no shell, code execution, or web-browsing tool.
The guide is limited to 16 KB, and the total request remains bounded. Only the five named
course extracts are profiled automatically, not arbitrary CSVs in your folder.
The app requires the working folder to be the course folder containing `ceu-ai.py`; it will
not scan your home folder or a parent workspace by accident.

Relative `/add` paths start at the terminal's working folder; absolute paths inside the
project also work with `/add` and `/drop`. From the course root, use
`/add data/raw/hotels_course.csv`. A generated notebook saved inside a module instead uses
`pd.read_csv("../../data/raw/hotels_course.csv")` because its kernel starts in that module
folder. For example, ask:

```text
Create a notebook in modules/module12-simple-linear-regression/analysis.ipynb.
Find hotels_course.csv, inspect its columns, and regress price and log price on distance.
```

Files read or created in the current session remain context for follow-up requests, and
their contents or CSV summaries are refreshed from disk. You can still use `/add path`
to share an eligible file explicitly; for a CSV, this displays the summary before sending.
Use `/drop path` to exclude a file or folder from subsequent listings, catalogue entries,
and reads; `/drop harness.md` also disables the automatic guide. Previously sent content
cannot be recalled. `/new` clears local conversation and shared files but reloads course
context, retaining these exclusions. `/add` can re-enable an individually excluded file; restarting the app
resets all exclusions. `/quit` exits. Pasted multiline requests are sent together when you
press Enter.

To discuss actual results, use an existing notebook or have the assistant create one.
Run it in VS Code (preferably restart the kernel and run all cells), then **save it with
its outputs**. Name it in your next request and ask the assistant to interpret its saved
text output. `/add` is optional; files already shared in the chat are refreshed from disk.
For example, replacing the path with your notebook's location:

```text
Interpret the saved regression output in modules/module12-simple-linear-regression/analysis.ipynb.
Explain the coefficients, p-values, and model fit. Do not modify the notebook.
```

The assistant does not run the notebook for you. It cannot see unsaved results or inspect
plots as images. Asking for an explanation without edits preserves your saved outputs;
AI-generated notebook revisions have their outputs cleared. Large
notebooks with embedded plots may exceed the text-file limit; paste the relevant text
results instead. The model must not invent results for code that has not been run.

Credentials and backups stay in the Git-ignored `.ceu/` folder. Never put the class secret
in a prompt, notebook, or tracked file. Run `uv run ceu-ai.py --setup` to replace saved
credentials. The credentials file is not encrypted; anyone who can read it can recover the
shared secret. Conversation history is kept only for the current session. The class account
shares CEU's configured request and spending limits.

## Repository materials

- `modules/`: nine substantive topic modules, grouped into six meetings, plus the course introduction.
- [Course introduction](modules/module00-intro/): slides in PDF and editable PowerPoint formats.
- `prompts/`: six human-first reconstruction and audit worksheets.
- `data/README.md`: dataset sources, extract definitions, and preparation decisions.
- `harness.md`: editable course guidance automatically supplied to the CEU assistant.
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

Run these commands from the repository root. The execution check starts each fresh kernel
in the notebook's own folder, matching VS Code and JupyterLab, without changing the
committed files.

## Attribution and licensing

The repository is distributed under the MIT License. The case progression and substantial
parts of the analytic structure are adapted from the MIT-licensed Gábor Békés and Gábor
Kézdi Python and textbook case-study repositories. See `NOTICE.md` for pinned revisions,
dataset handling, and detailed attribution.

## AI Attribution

This repository was created and developed with assistance from OpenAI language models. The
statement documents the creation process for the repository materials; it does not replace
the human-first Coding 2 policy above or alter Coding 1's prohibition on student AI use.
