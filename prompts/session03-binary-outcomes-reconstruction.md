# Session 3: Reconstructing a Binary-Outcome Analysis

Use this worksheet after completing Lecture 16.

## Initial prompt

> Predict whether people remain healthy and evaluate the classifier.

## Develop your specification

Clarify:

- the outcome and its positive class;
- observed proportions, the LPM baseline, and the logit model;
- the train/test split and random seed;
- coefficients, odds ratios, marginal effects, and predicted probabilities;
- probability metrics before classification metrics;
- calibration, Brier score, log loss, and ROC AUC;
- threshold choice and the costs of false positives and false negatives.

## Improved prompt scaffold

> Using `data/raw/share_health_course.csv`, analyze `[QUESTION]`. The positive outcome is
> `[POSITIVE CLASS]`. Use a stratified split with `random_state=42`. Fit `[MODELS]` on the
> training data and explain the differences among `[QUANTITIES]`. Evaluate probability
> predictions using `[METRICS]`; only then classify using `[THRESHOLD RULE]` and report
> `[CLASSIFICATION OUTPUTS]`. Do not use the test set for model fitting or specification.

## Audit the reconstruction

- Does it evaluate on observations excluded from fitting?
- Does it distinguish log odds, odds ratios, marginal effects, and probabilities?
- Does it calculate ROC AUC from probabilities rather than class labels?
- Does it treat 0.50 as a decision rather than a universal truth?
- Does its interpretation preserve the positive-class definition?
- Which metric names differ from the terms used during live coding?
