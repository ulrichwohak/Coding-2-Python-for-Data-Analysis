# Lecture 18: Regularization and Pipelines

This 38-minute live-coding lecture continues the Airbnb case. Students place imputation,
scaling, and encoding inside a pipeline; tune Ridge and LASSO with cross-validation; inspect
shrinkage; and evaluate the selected workflow once on the untouched holdout.

## Materials

- `regularization_pipelines.ipynb`
- Dataset: `data/raw/airbnb_hackney_course.csv`
- Reconstruction worksheet: `prompts/session04-validation-regularization-reconstruction.md`
- Source backbone: Gábor's Chapter 14 Airbnb LASSO case

## Reconstruction exercise

The generated workflow is treated as adversarial code review. Students audit split order,
preprocessing scope, metric signs, tuning data, random seeds, unknown categories, and the
one-time use of the holdout set.
