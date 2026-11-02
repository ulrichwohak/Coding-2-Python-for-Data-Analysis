# Lecture 00: Course introduction

Opening slides for Coding 2: Python for Data Analysis (ECBS5306), 2 November 2026.

- [Slides for presenting or printing (PDF)](presentation/course-introduction.pdf)
- [Editable slides with speaker notes (PowerPoint)](presentation/course-introduction.pptx)

The introduction covers the six-meeting schedule, assessment, debugging homeworks,
responsible AI use, the project environment, and the first regression case.

## LLMs, CEU AI and FirstRung

- [AI introduction for presenting or printing (PDF)](presentation/llms-ceu-ai-firstrung.pdf)
- [Editable AI introduction with speaker notes (PowerPoint)](presentation/llms-ceu-ai-firstrung.pptx)

This separate deck introduces language models, tokenization, attention, the app around
the model, HTTPS requests through the CEU API, and FirstRung coaching. Start the course
app with `uv run ceu-ai.py`; see the [current app instructions](../../README.md#ceu-ai-in-the-vs-code-terminal)
for setup and file-sharing details.

## Short live demonstration

[Word-vector arithmetic notebook](word_vector_arithmetic.ipynb): four short code cells
show a word vector, compute `king - man + woman`, and use Gensim's analogy helper to find
the closest words. The helper normalizes the vectors and excludes the input words.
It uses pretrained GloVe vectors locally; no CEU credentials or API requests are needed.

Before class, run these commands from the repository root:

```bash
uv sync --locked
uv run python scripts/fetch_data.py
```

The first data preparation now also downloads about 69 MB of word vectors. Later runs
reuse the verified local file. Open the notebook with the course `.venv` kernel.

Continue with [Lecture 12: Simple linear regression](../lecture12-simple-linear-regression/)
and [Lecture 13: Multiple regression and workflow](../lecture13-multiple-regression-workflow/).
