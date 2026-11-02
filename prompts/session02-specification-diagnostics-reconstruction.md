# Session 2: Reconstructing Model Specification and Diagnostics

Use this worksheet after completing Modules 14 and 15.

## Initial prompt

> Improve the hotel-price regression by adding categories, interactions, and diagnostics.

## Develop your specification

The prompt must make explicit:

- which categorical variables enter the model and their reference groups;
- which slope is allowed to vary through an interaction;
- how predictions will communicate that interaction;
- which residual patterns are being investigated;
- the distinction between robust uncertainty and a changed conditional-mean model;
- the candidate nonlinear specification and comparison criteria;
- correct back-transformation and the treatment of influential observations.

## Improved prompt scaffold

> Starting from `data/raw/hotels_course.csv`, reconstruct our analysis of `[QUESTION]`.
> Use `[SAMPLE]` and fit `[MODEL SEQUENCE]`. Make the reference categories explicit.
> Communicate the interaction using `[PREDICTION TABLE OR FIGURE]`. Diagnose the model
> using `[DIAGNOSTICS]`, compare `[FUNCTIONAL FORMS]`, and explain what each diagnostic can
> and cannot establish. Use local data only and state all assumptions.

## Audit the reconstruction

- Does it interpret an interaction as a difference in slopes?
- Are reference categories visible and correctly described?
- Does it react to an actual residual pattern rather than mechanically transform variables?
- Does it confuse robust standard errors with fixing model misspecification?
- Does it delete influential observations without investigating them?
- Does it overstate model fit as causality?
