# Session 6: Reconstructing a Regression-Tree Workflow

Use this worksheet after completing Module 20.

## Initial prompt

> Predict used-car prices with a decision tree, tune it, and explain the important features.

## Develop your specification

Make the prompt explicit about:

- the target, numeric features, and categorical features;
- the training/test split and random seed;
- the age-only tree and linear comparison;
- preprocessing for the multiple-feature tree;
- the deliberately unrestricted overfit model;
- cross-validated depth and minimum-leaf tuning;
- one final test evaluation;
- tree visualization, split interpretation, and two kinds of feature importance;
- pre-pruning versus cost-complexity post-pruning.

## Improved prompt scaffold

> Use `data/raw/used_cars_course.csv` to predict `price`. First compare `[AGE-ONLY
> MODELS]`. Then build a preprocessing-and-tree pipeline for `[FEATURE SET]`. Demonstrate
> overfitting, tune `[COMPLEXITY PARAMETERS]` by cross-validation on training data, and
> evaluate once on the test set. Visualize the selected tree and report `[IMPORTANCE
> METHODS]` with their limitations. Use `random_state=42` and include a leakage audit.

## Audit the reconstruction

- Can we manually trace example observations through the displayed splits?
- Did the test set influence the complexity choice?
- Does it distinguish pre-pruning controls from `ccp_alpha` pruning?
- Does it compare training, validation, and test errors correctly?
- Are feature importances described as predictive rather than causal?
- Does it acknowledge correlated predictors and split-point bias?
