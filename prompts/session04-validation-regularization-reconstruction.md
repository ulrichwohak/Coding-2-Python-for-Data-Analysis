# Session 4: Reconstructing Validation and Regularization

Use this worksheet after completing Modules 17 and 18.

## Initial prompt

> Build the best regularized model for Airbnb prices and report its accuracy.

## Develop your specification

Require the reconstruction to define:

- the prediction target and candidate features;
- an untouched holdout set;
- missing-value treatment, scaling, and categorical encoding;
- a single pipeline enclosing every learned transformation;
- cross-validation on the training data;
- Ridge and LASSO tuning grids and RMSE;
- selection by cross-validation followed by one holdout evaluation;
- coefficient shrinkage and its limits as an interpretation tool.

## Improved prompt scaffold

> Use `data/raw/airbnb_hackney_course.csv` to predict `price_eur`. Create `[SPLIT DESIGN]`
> with `random_state=42`. Put `[PREPROCESSING]` inside a scikit-learn pipeline. Compare
> `[MODELS]` using `[CROSS-VALIDATION DESIGN]` and `[METRIC]` on training data only. Select
> the model by `[SELECTION RULE]`, then evaluate it once on the untouched holdout. Return a
> numbered plan, runnable code, and an explicit leakage audit.

## Audit the reconstruction

- Was the holdout used during feature choice or tuning?
- Is preprocessing fitted separately inside every validation fold?
- Is the negative-scoring convention converted back correctly?
- Are unknown categories handled at prediction time?
- Does it claim that zero LASSO coefficients prove irrelevance?
- Can every reported metric be traced to the correct data split?
