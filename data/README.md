# Teaching Data

Coding 2 uses course-ready extracts of datasets accompanying Gábor Békés and Gábor
Kézdi's *Data Analysis for Business, Economics, and Policy*. The extracts are prepared by
`scripts/fetch_data.py`; analysis notebooks read only the resulting local CSV files.
The short introductory word-vector demonstration also reads a local pretrained model.

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
| `hotels_vienna_preparation.csv` | 418 | Data inspection and sample preparation before multiple regression | Same hotels-europe price and feature files |
| `share_health_course.csv` | 3,109 | Linear probability model, logit, probability evaluation, classification | [share-health](https://osf.io/3ze58/) |
| `airbnb_hackney_course.csv` | 3,000 | Validation, pipelines, Ridge, and LASSO | [Airbnb London](https://osf.io/7n96w/) |
| `wms_course.csv` | 2,000 | Management index, PCA, and k-means | [World Management Survey](https://osf.io/uzpce/) |
| `used_cars_course.csv` | 477 | Linear benchmark, regression trees, tuning, and pruning | [used-cars](https://osf.io/7gvz9/) |

## Preparation decisions

- Hotels: merge price and feature files; select one-night November 2017 weekday offers in
  Amsterdam, Barcelona, and Vienna; keep hotels and apartments with three to four stars,
  complete core predictors, and prices from 20 to 600 in the source's price units. See
  the currency documentation discrepancy below.
- Vienna preparation: merge the same price and feature files and select one-night
  November 2017 weekday offers in Vienna. Retain all accommodation types, star categories,
  missing ratings, and prices. Select and rename eight columns; do not calculate log prices
  or introduce artificial errors. This is a less processed extract of the upstream tidy
  tables, not the original scrape.
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

## Vienna preparation lesson

`hotels_vienna_preparation.csv` has one row per accommodation offer in the selected
city and stay period. The two source files are joined on `hotel_id` with a many-to-one
validation: the feature table has one row per property, while the full price table
contains repeated properties across stays. In this Vienna slice, all 418 IDs are unique
and there are no exact duplicate rows. Repeated IDs in the full source are not, by
themselves, duplicate observations to delete.

The columns are `hotel_id`, `city`, `accommodation`, `price`, `distance_miles`, `stars`,
`rating`, and `review_count`. `city` comes from `city_actual`; `accommodation` comes from
`accommodation_type`; `review_count` comes from `rating_reviewcount`. `rating` is the
source's customer rating, distinct from the star category and the separate Tripadvisor
rating that is not included. The extract preserves numeric prices without conversion.

There are 35 missing ratings and 35 missing review counts, on the same rows: 32 apartments,
one hotel, one guest house, and one vacation home condo. The other columns have no missing
values. A missing rating is not coded as zero. Prices range from 27 to 1,012.

Among the hotels, exactly one has `review_count == 1`: hotel 22164, with five stars,
customer rating 1.0, price 587, and distance 0.7 miles. This count comes from the source's
`rating_reviewcount` field and describes the customer rating, not the star classification.
Lecture 13 first inspects this row after the descriptive table, then retrieves the point
at rating 1.0 after the plots and confirms the match by hotel ID. The low review count
raises a question about how well the rating represents typical customer experience;
the row remains in the estimation sample.

Lecture 13 includes hotels across all observed star categories and documents these choices:

| Step | Rows remaining | Rows removed at this step |
| --- | ---: | ---: |
| Vienna offers in the selected period | 418 | 0 |
| Hotels | 254 | 164 |
| Complete price, distance, rating, and stars | 253 | 1 |

Before complete-case selection, a distance-only model has 254
eligible rows and a model including rating has 253. The notebook makes the shared
estimation sample explicit instead of relying on model-specific missing-value deletion.
All 253 complete hotels enter the main models, with no price cutoff. Students inspect
the observations on a log-price scatterplot and boxplot before estimation. Hotel 21976 has
price 806 and hotel 22252 has price 1,012; these prices are unusual, but the supplied
data does not establish recording errors. A graphical flag calls for investigation;
it does not automatically justify deletion. Any later exclusion should have a documented
reason and a comparison with the full-sample estimates. The separate `hotels_course.csv`
retains its original three- to four-star selection for the other hotel lectures and
the optional three-city extension, including its documented price restriction.

In Lecture 13, `stars` enters the regression numerically: an additional star has a constant
association with log price, conditional on the other predictors. All star values remain
eligible, including half stars. There is no star reference category in this specification.
This avoids separate coefficients for star values observed only once, while imposing a
linear relationship that students should discuss. The other hotel lectures can use
categorical stars on their documented samples.

### Currency documentation discrepancy

The existing course material labels hotel prices USD, while the
[upstream hotels-europe README](https://gabors-data-analysis.com/datasets/hotels-europe/)
labels `price` EUR. This conflict is unresolved for these pinned source files. The
preparation script performs no currency conversion. Lecture 13 uses neutral price labels;
do not infer a conversion or present either currency as newly verified from the CSV.

## Introductory word-vector demonstration

The same preparation command downloads `source/glove-wiki-gigaword-50.gz` under
`data/raw/`: 400,000 words with 50-dimensional GloVe vectors trained on Wikipedia 2014
and Gigaword. It is a 69,182,535-byte download (about 69 MB), reused after checksum
verification. The full vocabulary is retained; it is not restricted to the four words
in the classroom example. The notebook does not download anything or call an LLM API.

Source: [Gensim's GloVe release](https://github.com/piskvorky/gensim-data/releases/tag/glove-wiki-gigaword-50),
in word2vec text format, from [Stanford GloVe](https://nlp.stanford.edu/projects/glove/).
The [Gensim catalogue](https://github.com/piskvorky/gensim-data/blob/master/list.json)
lists the PDDL license and MD5 `c289bc5d7f2f02c6dc9f2f9b67641813`.
The downloaded file matched that checksum; `fetch_data.py` pins its SHA-256:
`5c55f98957aa9fed8d2ac5fb1dcff57af3b23c5a3ee7af3f7945f8d49198eb24`.

The vectors remain Git-ignored. They are static word embeddings, not the token
embeddings or contextual representations of the course's Gemini model.
