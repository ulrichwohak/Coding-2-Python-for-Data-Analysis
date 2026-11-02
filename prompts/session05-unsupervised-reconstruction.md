# Session 5: Reconstructing PCA and Clustering

Use this worksheet after completing Lecture 19.

## Initial prompt

> Find important dimensions and meaningful groups in the management data.

## Develop your specification

Specify:

- the four management-practice variables;
- the transparent average index;
- standardization before PCA and distance-based clustering;
- explained variance, loadings, and scores as different quantities;
- the candidate range for the number of clusters;
- the silhouette criterion and fixed random seed;
- cluster profiles without outcome-guided fitting or invented names.

## Improved prompt scaffold

> Using `data/raw/wms_course.csv`, summarize `[PRACTICE VARIABLES]` with a transparent
> index and PCA. Standardize before fitting. Report `[PCA OUTPUTS]` and distinguish loadings
> from observation scores. Fit k-means for `[K RANGE]` with `random_state=42`, compare
> `[SELECTION METRIC]`, and profile the selected clusters using the original variables. Do
> not use an outcome during fitting and do not assign unsupported narrative labels.

## Audit the reconstruction

- Was standardization performed before both methods?
- Does it distinguish component loadings, scores, and explained variance?
- Was any outcome or post-treatment variable used to create clusters?
- Are cluster numbers treated as arbitrary identifiers?
- Are labels grounded in the profile table?
- Does the response confuse data reduction with causal explanation?
