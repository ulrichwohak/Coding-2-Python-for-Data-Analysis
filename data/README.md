# Data

The course uses small synthetic datasets generated locally by `scripts/fetch_data.py`.

Run this command from the repository root before opening the notebooks:

```bash
uv run python scripts/fetch_data.py
```

The script writes CSV files to `data/raw/`:

- `career_outcomes.csv`: salary and promotion outcomes for regression and classification examples.
- `housing_sales.csv`: housing-price data with nonlinear structure for validation, transformations, and trees.
- `campaign_response.csv`: customer-response data for classification, pipelines, and clustering examples.

The generated files are ignored by Git so notebooks always read local data without storing generated raw files in the repository.
