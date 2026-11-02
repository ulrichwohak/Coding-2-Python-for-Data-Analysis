# Teaching Data

Coding 2 uses course-ready extracts of datasets accompanying Gábor Békés and Gábor
Kézdi's *Data Analysis for Business, Economics, and Policy*. The extracts are prepared by
`scripts/fetch_data.py`; notebooks read only the resulting local CSV files.

Run from the repository root:

```bash
uv run python scripts/fetch_data.py
```

The first run downloads and verifies the source files. Later runs reuse a source file only
when its SHA-256 checksum matches the value recorded in the script. Both source downloads
and prepared extracts remain under `data/raw/` and are ignored by Git.

Notebooks run from their own lecture folders and load data directly, for example:
`pd.read_csv("../../data/raw/hotels_course.csv")`. The `../..` goes up two folders to
the repository root. No path-search setup code is needed.

## Prepared files

| File | Rows | Purpose | Source |
| --- | ---: | --- | --- |
| `hotels_course.csv` | 821 | Simple and multiple regression, categorical variables, interactions, diagnostics | [hotels-europe price](https://osf.io/p6tyr/) and [features](https://osf.io/utwjs/) |
| `share_health_course.csv` | 3,109 | Linear probability model, logit, probability evaluation, classification | [share-health](https://osf.io/3ze58/) |
| `airbnb_hackney_course.csv` | 3,000 | Validation, pipelines, Ridge, and LASSO | [Airbnb London](https://osf.io/7n96w/) |
| `wms_course.csv` | 2,000 | Management index, PCA, and k-means | [World Management Survey](https://osf.io/uzpce/) |
| `used_cars_course.csv` | 477 | Linear benchmark, regression trees, tuning, and pruning | [used-cars](https://osf.io/7gvz9/) |

## Preparation decisions

- Hotels: merge price and feature files; select one-night November 2017 weekday offers in
  Amsterdam, Barcelona, and Vienna; keep hotels and apartments with three to four stars,
  complete core predictors, and prices from 20 to 600 USD.
- SHARE health: keep complete observations for health status, smoking, demographics,
  education, income, BMI, exercise, and country.
- Airbnb: select Hackney listings priced from 20 to 400 with capacity up to eight; keep a
  deterministic sample of 3,000 and retain selected missing values so preprocessing can be
  taught honestly inside a pipeline.
- WMS: keep complete firm-wave records for four management-practice dimensions and firms
  with 10 to 10,000 employees; take a deterministic sample of 2,000.
- Used cars: follow the source case's Camry filters and derive a readable trim category;
  retain missing categorical values as `unknown` rather than silently dropping them.

The source repositories are MIT-licensed, but the underlying datasets remain governed by
their original documentation and terms. See `NOTICE.md` for code and case-study attribution.
