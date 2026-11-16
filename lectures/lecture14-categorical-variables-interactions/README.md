# Lecture 14: Categorical Variables and Interactions

This live-coding lecture builds a regression around three questions:

1. How do prices differ across Amsterdam, Barcelona and Vienna?
2. How do hotels and apartments differ in price, holding city constant?
3. Do the 3.5-versus-3 and 4-versus-3 star comparisons differ across cities?

All models use the same 821 offers in the prepared extract, which includes hotels and
apartments with 3, 3.5 or 4 stars. The existing sample restrictions are documented in
`data/README.md`; the notebook adds no city filter. Short boxplot cells introduce each
question, and cross-tabulations show the number of observations in the category combinations.
These initial plots show unadjusted comparisons.

Start with city alone: the intercept and city coefficients reproduce mean log prices by city.
Then add accommodation type and examine how the interpretation and city coefficients change.
For the third question, add distance, rating and star categories with a common star pattern
across cities. Finally, interact city with stars to allow that pattern to differ. The final
specification omits accommodation type, so the last two models differ in both their controls
and their interaction structure.

Reference categories are explicitly Amsterdam, Apartment and 3 stars. Omitting their
indicator columns does not remove their observations. All models use HC0 standard errors;
in the final model, distance and rating associations remain common across cities.

A short prediction section applies the final model to the observed properties. It displays
the first ten observed and predicted log prices alongside the predictors. Two questions ask
where the model overpredicts or underpredicts, and why properties in the same city and star
category can have different predictions. A residual plot shows observed minus predicted log
price against predicted log price, with a zero line; a third question asks about patterns
and changes in the spread. These are fitted values for the estimation sample,
not an evaluation of prediction performance on new data.

## Materials

- `categorical_variables_interactions.ipynb`
- Dataset: `data/raw/hotels_course.csv`
- Source backbone: the European hotels, multiple-regression, and external-validity cases

## Learning outcomes

Students should be able to identify reference categories, distinguish city price levels from
within-city star comparisons, combine main and interaction coefficients, and compare
observed log prices with model predictions for the same properties.
