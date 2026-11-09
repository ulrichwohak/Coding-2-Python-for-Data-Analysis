# Lecture 13: Multiple Regression and Workflow Design

This lecture extends the Vienna hotel model with ratings and numeric stars.
You will inspect missingness and identifiers, document sample
restrictions, construct log prices, and inspect unusual observations using a log-price
scatterplot and boxplot. Then follow coefficient changes as rating and stars enter on a
common sample, interpret R-squared and adjusted R-squared, predict a proposed hotel's
log price, distinguish confidence and prediction intervals, and investigate residuals.

## Materials

- `multiple_regression_workflow.ipynb`
- Starting dataset: `data/raw/hotels_vienna_preparation.csv`
- Optional three-city extension: `data/raw/hotels_course.csv`
- Reconstruction worksheet: `prompts/session02-specification-diagnostics-reconstruction.md`
- Source backbone: Gábor Békés and Gábor Kézdi's advanced hotel-regression materials and
  Chapter 10 case study

## Data preparation

The starting file contains 418 Vienna accommodation offers, including 35 missing ratings.
It retains all accommodation types and star categories and the source's unusual prices.
The preparation section keeps all 254 hotels, then excludes one with a missing rating.
All 253 complete hotels enter the main models, with no price cutoff. A log-price scatterplot
against rating and a log-price boxplot by stars show these observations before estimation.
Identify points to investigate and consider the evidence needed for a correction or
exclusion. The current analysis retains
the unusual prices; it does not equate a boxplot flag with a verified error.
Sample restrictions define the analysis population; an unusual price is not automatically
a data error. See `data/README.md` for provenance, counts, and the unresolved currency labels
in the published documentation. The lecture does not convert currencies.

## Connect the summary table to the plots

Investigate the minimum review count of one in `.describe()`. Record the hotel's ID,
stars, and customer rating, then locate it in the rating–log-price scatterplot.
Use the ID to check that both lookups identify the same observation. The review count
describes the customer rating, not the star classification. What can a single review
tell you about typical customer experience?
Other unusual points remain visible; this is one investigation, not a definition of all
outliers. The exercise does not exclude the hotel or introduce a review-count cutoff.

## Reading the regression sequence

The main regression table places models in columns and coefficients in rows. Begin with
the distance row, then follow the rating row as stars enter. Identify what is
held constant in each column and check that the observation count stays the same.
R-squared describes fit to log prices in this sample;
adding controls cannot lower it. Adjusted R-squared accounts for the number of predictors.
Coefficient changes alone do not establish causality. The later table retains HC3 robust
standard errors for the full model.

Stars enter numerically, with one coefficient for an additional star and no reference
category. This assumes a constant association with log price for each one-star increment,
holding distance and rating fixed. Half-star increments contribute half that log-price
difference. The assumption pools information across the scale, including sparsely observed
star values. Lecture 14 introduces the alternative of separate category coefficients.

## Prediction scale

Predictions, confidence intervals, prediction intervals, residual comparisons, and the
observed-versus-predicted plot stay in log-price units. The confidence interval concerns
mean log price for hotels with the proposed features; the prediction interval concerns
one hotel's log price. The notebook's optional percentage-change cell interprets
coefficients and does not convert predicted log prices into price-level predictions.

## Reconstruction exercise

After completing the analysis in class, write your own prompt specifying the completed
steps. Audit the generated plan and code against your class notebook for starting data,
exclusions, sample sizes, transformations, model
sequence, the numeric-star assumption, log-scale intervals and residuals, and causal overstatement.
