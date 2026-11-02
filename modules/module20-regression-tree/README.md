# Module 20: Regression Trees

This 70-minute live-coding module follows Gábor's used-car CART case. Students read a
shallow tree, compare it with a linear age model, expose overfitting, tune complexity by
cross-validation, evaluate on untouched data, and qualify feature-importance claims.

## Materials

- `regression_tree.ipynb`
- Dataset: `data/raw/used_cars_course.csv`
- Reconstruction worksheet: `prompts/session06-tree-reconstruction.md`
- Source backbone: Gábor Békés and Gábor Kézdi's Chapter 15 regression-tree case

## Reconstruction exercise

The final audit checks manual split tracing, pre-pruning versus post-pruning terminology,
validation design, RMSE, feature-importance limitations, and whether the generated code
lets test data influence the selected tree.
