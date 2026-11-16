# Session 2: Reconstructing Model Specification and Diagnostics

Use this worksheet at the end of the meeting covering Lectures 13–15. Include only
the steps completed in class.

## Initial prompt

> Improve the hotel-price regression by adding categories, interactions, and diagnostics.

## Develop your specification

The prompt must make explicit:

- the starting extract and the observation unit;
- missing-value and identifier checks, sample restrictions, and the count excluded at each step;
- how log prices and a common sample for model comparisons are constructed;
- how distance and rating coefficients change as controls enter, alongside R-squared and sample size;
- the constant log-price change per additional star assumed by Lecture 13's numeric predictor;
- how a log-price scatterplot and boxplot flag observations for investigation before estimation;
- how the hotel with one recorded review is traced from the descriptive-table follow-up to the plotted point using its ID;
- the evidence needed to justify an exclusion, with all complete hotels retained in the initial analysis;
- which categorical variables enter the model and their reference groups;
- which star-category comparisons are allowed to differ across cities through an interaction;
- how predictions for the observed properties are compared with their actual log prices;
- which residual patterns are being investigated;
- the distinction between robust uncertainty and a changed conditional-mean model;
- the candidate nonlinear specification and comparison criteria;
- log-scale predictions, intervals, and residual comparisons in Lecture 13;
- the treatment of influential observations and any transformations covered in later lectures.

## Improved prompt scaffold

> Starting from `[LOCAL DATASET]`, reconstruct our analysis of `[QUESTION]`.
> Inspect `[DATA QUALITY CHECKS]`, construct `[VARIABLES]`, and document `[SAMPLE RULES]`
> with counts before and after each restriction. Fit `[MODEL SEQUENCE]` on the same
> observations. Before estimation, plot `[VARIABLES AND SCALES]` and explain which
> observations warrant investigation; justify any exclusions. Make reference categories
> explicit where categorical predictors are used.
> Explain the interaction and compare observed and predicted log prices. Diagnose the model
> using `[DIAGNOSTICS]`, compare `[FUNCTIONAL FORMS]`, and explain what each diagnostic can
> and cannot establish. Use local data only and state all assumptions.

For Lecture 13, start from `data/raw/hotels_vienna_preparation.csv`; using the prepared
`hotels_course.csv` would skip the preparation exercise. Lectures 14–15 and the optional
three-city extension use `data/raw/hotels_course.csv`. Name the relevant file for each part
you reconstruct, and omit steps not yet covered. Lecture 14 starts with city differences,
then adds accommodation type. It introduces distance, rating and star categories before
comparing a common star-category pattern with city-specific patterns. The final interaction
model omits accommodation type; record this change in controls explicitly. All four models
use the same three-city sample. Predictions for the observed properties stay in log-price units.

## Audit the reconstruction

- Does it start from the intended extract and preserve the original data?
- Are missing ratings kept distinct from zeros, and exclusions explained and counted?
- Does it check the observation unit before treating repeated IDs as duplicates?
- Do the candidate models use the same observations?
- Does it explain what is held constant when comparing coefficients, without treating higher R-squared as causal evidence?
- Does it distinguish numeric stars in Lecture 13 from categorical stars in Lecture 14?
- Does it keep Lecture 13 predictions, intervals, and residual comparisons in log-price units?
- Does it distinguish a sample restriction from a verified data error?
- Does it use plots before estimation and avoid deleting observations solely because they look unusual?
- Does it connect the one-review hotel to the plotted observation by ID, and distinguish customer rating from star classification?
- Does it interpret a city-by-stars interaction as a difference in within-city star-category comparisons?
- Does it distinguish overall city price differences from star-category differences within a city?
- Are reference categories visible and correctly described?
- Does it react to an actual residual pattern rather than mechanically transform variables?
- Does it confuse robust standard errors with fixing model misspecification?
- Does it delete influential observations without investigating them?
- Does it overstate model fit as causality?
