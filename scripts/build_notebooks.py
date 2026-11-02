"""Build the Coding 2 live-coding notebooks from reviewable cell sources."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip())


def write_notebook(relative_path: str, cells: list) -> None:
    notebook = nbf.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.12"},
        },
    )
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, path)
    print(f"wrote {path.relative_to(ROOT)} ({len(cells)} cells)")


def module12() -> list:
    return [
        md(
            """
            # Module 12: Simple Linear Regression

            **Case:** How is a Vienna hotel's room price associated with its distance from
            the city centre?

            We build the analysis in small, typeable steps. The aim is not merely to run
            `ols`; it is to connect the business question, graph, regression line,
            coefficient units, fitted values, and residuals.

            Adapted from the hotel-price cases in Chapters 7–8 of *Data Analysis for
            Business, Economics, and Policy*.
            """
        ),
        md(
            """
            ## 1. Load and define the analysis sample

            Each row is one hotel offer. `price` is the room price in US dollars and
            `distance_miles` is distance from the city centre. We begin with three- and
            four-star hotels in Vienna so the comparison is reasonably focused.
            """
        ),
        code(
            """
            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd
            import seaborn as sns
            import statsmodels.formula.api as smf

            sns.set_theme(style="whitegrid")
            """
        ),
        code(
            """
            hotels = pd.read_csv("../../data/raw/hotels_course.csv")
            vienna = hotels.query("city == 'Vienna' and accommodation == 'Hotel'").copy()
            vienna.shape
            """
        ),
        code(
            """
            vienna[["hotel_id", "price", "distance_miles", "stars", "rating"]].head()
            """
        ),
        md(
            """
            **Before calculating:** Which direction should the association have? What
            factors besides distance could make two hotel prices different? Those omitted
            variables matter when we interpret the slope.
            """
        ),
        code(
            """
            vienna[["price", "distance_miles", "stars", "rating"]].describe().round(2)
            """
        ),
        md("## 2. See the pattern before fitting a model"),
        code(
            """
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.scatterplot(data=vienna, x="distance_miles", y="price", alpha=0.65, ax=ax)
            ax.set(title="Vienna hotel prices and distance", xlabel="Distance (miles)", ylabel="Price (USD)")
            plt.show()
            """
        ),
        code(
            """
            vienna["distance_group"] = pd.cut(
                vienna["distance_miles"], bins=[0, 1, 2, 4, np.inf], right=False
            )
            group_means = vienna.groupby("distance_group", observed=True)["price"].agg(["mean", "count"])
            group_means.round(1)
            """
        ),
        md(
            """
            The grouped means describe the sample without imposing a straight line. The
            regression line is a compact approximation: it selects the intercept and slope
            that minimize the sum of squared residuals.
            """
        ),
        code(
            """
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.regplot(data=vienna, x="distance_miles", y="price", scatter_kws={"alpha": 0.55}, ax=ax)
            ax.set(title="Linear approximation", xlabel="Distance (miles)", ylabel="Price (USD)")
            plt.show()
            """
        ),
        md("## 3. Estimate and interpret the regression"),
        code(
            """
            simple_model = smf.ols("price ~ distance_miles", data=vienna).fit(cov_type="HC3")
            simple_model.summary()
            """
        ),
        code(
            """
            coefficient_table = pd.DataFrame(
                {
                    "estimate": simple_model.params,
                    "robust_se": simple_model.bse,
                    "ci_low": simple_model.conf_int()[0],
                    "ci_high": simple_model.conf_int()[1],
                }
            )
            coefficient_table.round(2)
            """
        ),
        code(
            """
            intercept = simple_model.params["Intercept"]
            slope = simple_model.params["distance_miles"]
            print(f"Predicted price at the centre: ${intercept:.0f}")
            print(f"Average price difference per additional mile: ${slope:.0f}")
            """
        ),
        md(
            """
            The slope is an **association in dollars per mile**, not the causal effect of
            moving a hotel. Location quality, star category, ratings, and other features
            differ across hotels too.
            """
        ),
        md("## 4. Fitted values, residuals, and predictions"),
        code(
            """
            vienna["fitted_price"] = simple_model.fittedvalues
            vienna["residual"] = simple_model.resid
            vienna[["price", "fitted_price", "residual"]].head().round(1)
            """
        ),
        code(
            """
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.scatterplot(data=vienna, x="fitted_price", y="residual", alpha=0.65, ax=ax)
            ax.axhline(0, color="black", linewidth=1)
            ax.set(title="Residuals reveal what the line misses", xlabel="Fitted price", ylabel="Residual")
            plt.show()
            """
        ),
        code(
            """
            new_distances = pd.DataFrame({"distance_miles": [0.5, 2.0, 5.0]})
            prediction = simple_model.get_prediction(new_distances).summary_frame(alpha=0.05)
            new_distances.join(prediction).round(1)
            """
        ),
        code(
            """
            vienna.nlargest(5, "residual")[
                ["hotel_id", "price", "distance_miles", "fitted_price", "residual"]
            ].round(1)
            """
        ),
        md(
            """
            **Checkpoint:** A large positive residual means the hotel is more expensive
            than the distance-only model predicts. It does not by itself tell us whether
            the hotel is overpriced; the model ignores hotel quality.

            Continue to Module 13, where we add those features deliberately.

            ### Optional extension

            Compare `price ~ distance_miles` with `log_price ~ distance_miles`. Ask how
            the change in outcome scale changes the slope's units and the residual pattern.
            """
        ),
        code(
            """
            log_model = smf.ols("log_price ~ distance_miles", data=vienna).fit(cov_type="HC3")
            pd.DataFrame(
                {"level_model": simple_model.resid, "log_model": log_model.resid}
            ).describe().loc[["mean", "std"]].round(3)
            """
        ),
    ]


def module13() -> list:
    return [
        md(
            """
            # Module 13: Multiple Regression and Workflow Design

            **Case:** Which Vienna hotels appear inexpensive relative to their location and
            observable quality?

            This extends the simple regression from Module 12. We specify candidate
            models, compare them, construct honest interpretations, and distinguish a
            confidence interval for a mean from a prediction interval for one hotel.

            Adapted from Gábor Békés and Gábor Kézdi's advanced hotel-regression materials
            and Chapter 10 case study.
            """
        ),
        code(
            """
            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd
            import seaborn as sns
            import statsmodels.formula.api as smf
            from sklearn.metrics import root_mean_squared_error

            sns.set_theme(style="whitegrid")
            """
        ),
        code(
            """
            hotels = pd.read_csv("../../data/raw/hotels_course.csv")
            vienna = hotels.query("city == 'Vienna' and accommodation == 'Hotel'").copy()
            vienna[["price", "distance_miles", "rating", "stars", "review_count"]].describe().round(2)
            """
        ),
        md(
            """
            ## 1. Translate the question into model specifications

            Distance is the baseline. Rating and star category are observable quality
            measures. We add them in stages so that every change has a substantive reason.
            """
        ),
        code(
            """
            fig, axes = plt.subplots(1, 2, figsize=(12, 4))
            sns.scatterplot(data=vienna, x="rating", y="log_price", hue="stars", ax=axes[0])
            sns.boxplot(data=vienna, x="stars", y="log_price", ax=axes[1])
            axes[0].set(title="Ratings and log price")
            axes[1].set(title="Log price by star category")
            plt.tight_layout()
            plt.show()
            """
        ),
        code(
            """
            model_1 = smf.ols("log_price ~ distance_miles", data=vienna).fit(cov_type="HC3")
            model_2 = smf.ols("log_price ~ distance_miles + rating", data=vienna).fit(cov_type="HC3")
            model_3 = smf.ols(
                "log_price ~ distance_miles + rating + C(stars)", data=vienna
            ).fit(cov_type="HC3")
            """
        ),
        code(
            """
            def model_row(name, model):
                rmse = root_mean_squared_error(vienna["log_price"], model.fittedvalues)
                return {"model": name, "adj_r2": model.rsquared_adj, "aic": model.aic, "rmse_log": rmse}

            comparison = pd.DataFrame(
                [model_row("distance", model_1), model_row("+ rating", model_2), model_row("+ stars", model_3)]
            )
            comparison.round(3)
            """
        ),
        md(
            """
            Adjusted R-squared and AIC describe in-sample fit with different complexity
            penalties. They are useful here, but they are not substitutes for honest
            out-of-sample evaluation; that arrives in Module 17.
            """
        ),
        code(
            """
            terms = ["distance_miles", "rating", "C(stars)[T.3.5]", "C(stars)[T.4.0]"]
            estimates = pd.DataFrame(
                {"estimate": model_3.params, "robust_se": model_3.bse}
            ).loc[terms]
            estimates.round(3)
            """
        ),
        code(
            """
            distance_pct = 100 * (np.exp(model_3.params["distance_miles"]) - 1)
            rating_pct = 100 * (np.exp(model_3.params["rating"]) - 1)
            print(f"One additional mile is associated with {distance_pct:.1f}% different price.")
            print(f"One rating point is associated with {rating_pct:.1f}% different price.")
            """
        ),
        md("## 2. Predict one hotel and express uncertainty"),
        code(
            """
            proposed_hotel = pd.DataFrame(
                {"distance_miles": [2.5], "rating": [4.2], "stars": [4.0]}
            )
            prediction_log = model_3.get_prediction(proposed_hotel).summary_frame(alpha=0.05)
            prediction_log.round(3)
            """
        ),
        code(
            """
            smearing_factor = np.mean(np.exp(model_3.resid))
            columns = ["mean", "mean_ci_lower", "mean_ci_upper", "obs_ci_lower", "obs_ci_upper"]
            prediction_price = np.exp(prediction_log[columns]) * smearing_factor
            prediction_price.round(0)
            """
        ),
        md(
            """
            The confidence interval describes uncertainty about the expected price for
            hotels with these features. The prediction interval is wider because an
            individual hotel's price also contains irreducible variation.
            """
        ),
        md("## 3. Use residuals to find candidates—not conclusions"),
        code(
            """
            vienna["predicted_log_price"] = model_3.fittedvalues
            vienna["residual_log_price"] = model_3.resid
            vienna["predicted_price"] = np.exp(model_3.fittedvalues) * smearing_factor
            """
        ),
        code(
            """
            candidates = vienna.nsmallest(8, "residual_log_price")[
                ["hotel_id", "price", "predicted_price", "distance_miles", "stars", "rating"]
            ]
            candidates.round(1)
            """
        ),
        code(
            """
            fig, ax = plt.subplots(figsize=(7, 5))
            sns.scatterplot(data=vienna, x="predicted_price", y="price", alpha=0.65, ax=ax)
            limits = [vienna["price"].min(), vienna["price"].max()]
            ax.plot(limits, limits, color="black", linestyle="--")
            ax.set(title="Observed versus predicted prices", xlabel="Predicted price", ylabel="Observed price")
            plt.show()
            """
        ),
        md(
            """
            ## Session 1 reconstruction handoff

            Only after completing both regression notebooks, open
            `prompts/session01-regression-reconstruction.md`. The class will specify the
            analysis in plain language, ask an LLM to reconstruct it, and audit the result
            against this human-built reference.

            ### Optional extension: external validity

            Fit the same formula separately in Amsterdam and Barcelona. Compare the
            distance coefficient and prediction error. A stable formula is not guaranteed
            to have stable coefficients in another market.
            """
        ),
        code(
            """
            city_models = {
                city: smf.ols("log_price ~ distance_miles + rating + C(stars)", data=group).fit()
                for city, group in hotels.query("accommodation == 'Hotel'").groupby("city")
            }
            pd.DataFrame(
                {city: {"distance": model.params["distance_miles"], "adj_r2": model.rsquared_adj}
                 for city, model in city_models.items()}
            ).T.round(3)
            """
        ),
    ]


def module14() -> list:
    return [
        md(
            """
            # Module 14: Categorical Variables and Interactions

            We continue with the European hotels case. Categorical coefficients always
            compare groups to a reference category; interactions allow a slope to differ
            across groups. Prediction tables and plots make both ideas easier to explain.
            """
        ),
        code(
            """
            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd
            import seaborn as sns
            import statsmodels.formula.api as smf

            sns.set_theme(style="whitegrid")
            """
        ),
        code(
            """
            hotels = pd.read_csv("../../data/raw/hotels_course.csv")
            hotels.groupby(["city", "accommodation"]).size().unstack(fill_value=0)
            """
        ),
        md("## 1. A categorical predictor is a set of comparisons"),
        code(
            """
            vienna = hotels.query("city == 'Vienna'").copy()
            category_model = smf.ols(
                "log_price ~ distance_miles + rating + C(stars) + C(accommodation)",
                data=vienna,
            ).fit(cov_type="HC3")
            category_model.summary()
            """
        ),
        code(
            """
            category_terms = category_model.params.index[category_model.params.index.str.startswith("C(")]
            pd.DataFrame(
                {"estimate": category_model.params[category_terms], "robust_se": category_model.bse[category_terms]}
            ).round(3)
            """
        ),
        md(
            """
            Statsmodels uses the alphabetically first observed category as the reference
            unless we specify another. The intercept therefore describes a particular
            reference hotel, not an average hotel.
            """
        ),
        code(
            """
            comparison_hotels = pd.DataFrame(
                {
                    "distance_miles": [2.0, 2.0],
                    "rating": [4.0, 4.0],
                    "stars": [4.0, 4.0],
                    "accommodation": ["Apartment", "Hotel"],
                }
            )
            comparison_hotels["predicted_price"] = np.exp(category_model.predict(comparison_hotels))
            comparison_hotels.round(1)
            """
        ),
        md("## 2. Interactions let the distance slope differ"),
        code(
            """
            interaction_model = smf.ols(
                "log_price ~ distance_miles * C(accommodation) + rating + C(stars)",
                data=vienna,
            ).fit(cov_type="HC3")
            interaction_model.summary()
            """
        ),
        code(
            """
            base_slope = interaction_model.params["distance_miles"]
            difference = interaction_model.params["distance_miles:C(accommodation)[T.Hotel]"]
            slopes = pd.Series(
                {"Apartment": base_slope, "Hotel": base_slope + difference}, name="log-price slope"
            )
            slopes.round(3)
            """
        ),
        code(
            """
            grid = pd.DataFrame(
                {
                    "distance_miles": np.tile(np.linspace(0.2, 7, 50), 2),
                    "accommodation": np.repeat(["Apartment", "Hotel"], 50),
                    "rating": 4.0,
                    "stars": 4.0,
                }
            )
            grid["predicted_price"] = np.exp(interaction_model.predict(grid))
            """
        ),
        code(
            """
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.lineplot(data=grid, x="distance_miles", y="predicted_price", hue="accommodation", ax=ax)
            ax.set(title="Interaction shown as different slopes", xlabel="Distance (miles)", ylabel="Predicted price")
            plt.show()
            """
        ),
        md("## 3. City effects and model comparison"),
        code(
            """
            pooled = smf.ols(
                "log_price ~ distance_miles + rating + C(stars) + C(accommodation) + C(city)",
                data=hotels,
            ).fit(cov_type="HC3")
            pooled_interaction = smf.ols(
                "log_price ~ distance_miles * C(city) + rating + C(stars) + C(accommodation)",
                data=hotels,
            ).fit(cov_type="HC3")
            """
        ),
        code(
            """
            pd.DataFrame(
                {
                    "model": ["common distance slope", "city-specific slopes"],
                    "adjusted_r2": [pooled.rsquared_adj, pooled_interaction.rsquared_adj],
                    "aic": [pooled.aic, pooled_interaction.aic],
                }
            ).round(2)
            """
        ),
        md(
            """
            **Interpretation checkpoint:** An interaction coefficient is a *difference in
            slopes*. The clearest explanation usually combines the relevant coefficients
            or shows predicted values, as we did above.

            Continue to Module 15 before running the Session 2 reconstruction exercise.
            """
        ),
    ]


def module15() -> list:
    return [
        md(
            """
            # Module 15: Diagnostics and Transformations

            Diagnostics ask where a model is systematically wrong. We use residual plots,
            a heteroskedasticity test, nonlinear terms, robust uncertainty, and influence
            measures. The goal is a justified revision—not a ritual sequence of tests.
            """
        ),
        code(
            """
            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd
            import seaborn as sns
            import statsmodels.api as sm
            import statsmodels.formula.api as smf
            from sklearn.metrics import root_mean_squared_error
            from statsmodels.stats.diagnostic import het_breuschpagan

            sns.set_theme(style="whitegrid")
            """
        ),
        code(
            """
            hotels = pd.read_csv("../../data/raw/hotels_course.csv")
            vienna = hotels.query("city == 'Vienna' and accommodation == 'Hotel'").copy()
            linear = smf.ols("log_price ~ distance_miles + rating + C(stars)", data=vienna).fit()
            """
        ),
        md("## 1. Look for structure left in the residuals"),
        code(
            """
            diagnostics = vienna.assign(fitted=linear.fittedvalues, residual=linear.resid)
            fig, axes = plt.subplots(1, 2, figsize=(12, 4))
            sns.scatterplot(data=diagnostics, x="fitted", y="residual", alpha=0.65, ax=axes[0])
            axes[0].axhline(0, color="black", linewidth=1)
            sm.qqplot(diagnostics["residual"], line="45", fit=True, ax=axes[1])
            axes[0].set(title="Residuals versus fitted values")
            axes[1].set(title="Normal Q-Q plot")
            plt.tight_layout()
            plt.show()
            """
        ),
        code(
            """
            bp_stat, bp_pvalue, _, _ = het_breuschpagan(linear.resid, linear.model.exog)
            pd.Series({"Breusch-Pagan statistic": bp_stat, "p-value": bp_pvalue}).round(4)
            """
        ),
        md(
            """
            A small p-value is evidence that residual variance changes with the predictors.
            Robust standard errors adjust uncertainty estimates; they do not fix a poor
            conditional-mean specification.
            """
        ),
        code(
            """
            conventional = linear.bse.rename("conventional_se")
            robust = linear.get_robustcov_results(cov_type="HC3")
            robust_se = pd.Series(robust.bse, index=linear.params.index, name="robust_se")
            pd.concat([conventional, robust_se], axis=1).round(4)
            """
        ),
        md("## 2. Test a substantively plausible nonlinear relationship"),
        code(
            """
            quadratic = smf.ols(
                "log_price ~ distance_miles + I(distance_miles ** 2) + rating + C(stars)",
                data=vienna,
            ).fit(cov_type="HC3")
            """
        ),
        code(
            """
            pd.DataFrame(
                {
                    "model": ["linear distance", "quadratic distance"],
                    "aic": [linear.aic, quadratic.aic],
                    "rmse_log": [
                        root_mean_squared_error(vienna["log_price"], linear.fittedvalues),
                        root_mean_squared_error(vienna["log_price"], quadratic.fittedvalues),
                    ],
                }
            ).round(3)
            """
        ),
        code(
            """
            distance_grid = pd.DataFrame(
                {
                    "distance_miles": np.linspace(0.2, 8, 100),
                    "rating": 4.0,
                    "stars": 4.0,
                }
            )
            distance_grid["linear"] = np.exp(linear.predict(distance_grid))
            distance_grid["quadratic"] = np.exp(quadratic.predict(distance_grid))
            """
        ),
        code(
            """
            plot_grid = distance_grid.melt("distance_miles", var_name="model", value_name="predicted_price")
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.lineplot(data=plot_grid, x="distance_miles", y="predicted_price", hue="model", ax=ax)
            ax.set(title="Functional form changes the implied relationship", ylabel="Predicted price")
            plt.show()
            """
        ),
        md("## 3. Back-transform carefully and inspect influence"),
        code(
            """
            smearing = np.mean(np.exp(quadratic.resid))
            vienna["predicted_price"] = np.exp(quadratic.fittedvalues) * smearing
            vienna["price_residual"] = vienna["price"] - vienna["predicted_price"]
            vienna[["price", "predicted_price", "price_residual"]].describe().round(1)
            """
        ),
        code(
            """
            influence = quadratic.get_influence()
            vienna["cooks_distance"] = influence.cooks_distance[0]
            influential = vienna.nlargest(8, "cooks_distance")[
                ["hotel_id", "price", "distance_miles", "rating", "cooks_distance"]
            ]
            influential.round(3)
            """
        ),
        md(
            """
            Influential observations deserve investigation, not automatic deletion. Check
            whether they are errors, unusual but valid cases, or evidence that the model
            misses a relevant feature.

            ## Session 2 reconstruction handoff

            Open `prompts/session02-specification-diagnostics-reconstruction.md`. The audit
            will focus on reference categories, interactions, transformations, residual
            evidence, and whether the generated interpretation overclaims causality.

            ### Optional extension

            Replace the quadratic with `bs(distance_miles, df=4)` from Patsy and compare
            the fitted curve. Greater flexibility must be justified and validated.
            """
        ),
        code(
            """
            spline = smf.ols(
                "log_price ~ bs(distance_miles, df=4) + rating + C(stars)", data=vienna
            ).fit(cov_type="HC3")
            pd.Series({"quadratic_aic": quadratic.aic, "spline_aic": spline.aic}).round(2)
            """
        ),
    ]


def module16() -> list:
    return [
        md(
            """
            # Module 16: Logistic Regression and Classification

            **Case:** Which characteristics are associated with remaining healthy over the
            next survey wave?

            We distinguish probability modeling from classification. The case follows
            Gábor Békés and Gábor Kézdi's SHARE health materials: start with proportions,
            compare the linear probability model and logit, then evaluate probability
            predictions and decision thresholds.
            """
        ),
        code(
            """
            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd
            import seaborn as sns
            import statsmodels.formula.api as smf
            from sklearn.calibration import calibration_curve
            from sklearn.metrics import (
                ConfusionMatrixDisplay, brier_score_loss, classification_report,
                confusion_matrix, log_loss, roc_auc_score, roc_curve,
            )
            from sklearn.model_selection import train_test_split

            sns.set_theme(style="whitegrid")
            """
        ),
        code(
            """
            share = pd.read_csv("../../data/raw/share_health_course.csv")
            variables = ["stayshealthy", "smoking", "ever_smoked", "female", "age", "income10", "eduyears", "bmi", "exerc"]
            share[variables].describe().T.round(2)
            """
        ),
        md("## 1. Begin with observed probabilities"),
        code(
            """
            observed = share.groupby("smoking")["stayshealthy"].agg(["mean", "count"])
            observed.index = observed.index.map({0: "Not currently smoking", 1: "Currently smoking"})
            observed.round(3)
            """
        ),
        code(
            """
            fig, ax = plt.subplots(figsize=(7, 4))
            sns.barplot(data=share, x="smoking", y="stayshealthy", errorbar=("ci", 95), ax=ax)
            ax.set(title="Observed probability of staying healthy", xlabel="Current smoker", ylabel="Proportion")
            plt.show()
            """
        ),
        md("## 2. Linear probability model as a transparent baseline"),
        code(
            """
            lpm = smf.ols(
                "stayshealthy ~ smoking + ever_smoked + female + age + income10 + eduyears + bmi + exerc",
                data=share,
            ).fit(cov_type="HC3")
            lpm.summary()
            """
        ),
        code(
            """
            lpm_predictions = lpm.predict(share)
            pd.Series(
                {"minimum": lpm_predictions.min(), "maximum": lpm_predictions.max(), "outside_0_1": ((lpm_predictions < 0) | (lpm_predictions > 1)).sum()}
            ).round(3)
            """
        ),
        md(
            """
            The LPM coefficient is a change in probability units, but the model can predict
            outside zero and one and assumes constant marginal effects. Logit constrains
            predictions to the probability scale.
            """
        ),
        md("## 3. Separate fitting from evaluation"),
        code(
            """
            train, test = train_test_split(
                share, test_size=0.25, random_state=42, stratify=share["stayshealthy"]
            )
            train.shape, test.shape
            """
        ),
        code(
            """
            formula = "stayshealthy ~ smoking + ever_smoked + female + age + income10 + eduyears + bmi + exerc"
            logit = smf.logit(formula, data=train).fit(disp=False)
            logit.summary()
            """
        ),
        code(
            """
            odds_ratios = pd.DataFrame(
                {"odds_ratio": np.exp(logit.params), "ci_low": np.exp(logit.conf_int()[0]), "ci_high": np.exp(logit.conf_int()[1])}
            )
            odds_ratios.loc[["smoking", "ever_smoked", "female", "age", "eduyears"]].round(3)
            """
        ),
        code(
            """
            marginal_effects = logit.get_margeff(at="overall").summary_frame()
            marginal_effects.head(8).round(4)
            """
        ),
        md("## 4. Evaluate probabilities before choosing a threshold"),
        code(
            """
            test = test.copy()
            test["probability"] = logit.predict(test)
            probability_metrics = pd.Series(
                {
                    "Brier score": brier_score_loss(test["stayshealthy"], test["probability"]),
                    "Log loss": log_loss(test["stayshealthy"], test["probability"]),
                    "ROC AUC": roc_auc_score(test["stayshealthy"], test["probability"]),
                }
            )
            probability_metrics.round(3)
            """
        ),
        code(
            """
            fraction_positive, mean_predicted = calibration_curve(
                test["stayshealthy"], test["probability"], n_bins=8, strategy="quantile"
            )
            fig, ax = plt.subplots(figsize=(6, 5))
            ax.plot(mean_predicted, fraction_positive, marker="o", label="Logit")
            ax.plot([0, 1], [0, 1], linestyle="--", color="black", label="Perfect calibration")
            ax.set(xlabel="Mean predicted probability", ylabel="Observed proportion", title="Calibration on test data")
            ax.legend()
            plt.show()
            """
        ),
        md("## 5. Classification requires a decision threshold"),
        code(
            """
            threshold = 0.5
            test["predicted_class"] = (test["probability"] >= threshold).astype(int)
            matrix = confusion_matrix(test["stayshealthy"], test["predicted_class"])
            matrix
            """
        ),
        code(
            """
            ConfusionMatrixDisplay(matrix).plot(cmap="Blues")
            plt.title("Confusion matrix at threshold 0.50")
            plt.show()
            """
        ),
        code(
            """
            pd.DataFrame(
                classification_report(test["stayshealthy"], test["predicted_class"], output_dict=True)
            ).T.round(3)
            """
        ),
        code(
            """
            threshold_rows = []
            for cutoff in [0.3, 0.5, 0.7]:
                predicted = (test["probability"] >= cutoff).astype(int)
                tn, fp, fn, tp = confusion_matrix(test["stayshealthy"], predicted).ravel()
                threshold_rows.append(
                    {"threshold": cutoff, "false_positive_rate": fp / (fp + tn), "true_positive_rate": tp / (tp + fn)}
                )
            pd.DataFrame(threshold_rows).round(3)
            """
        ),
        code(
            """
            false_positive_rate, true_positive_rate, _ = roc_curve(test["stayshealthy"], test["probability"])
            fig, ax = plt.subplots(figsize=(6, 5))
            ax.plot(false_positive_rate, true_positive_rate)
            ax.plot([0, 1], [0, 1], linestyle="--", color="black")
            ax.set(xlabel="False-positive rate", ylabel="True-positive rate", title="ROC curve")
            plt.show()
            """
        ),
        md(
            """
            ## Session 3 reconstruction handoff

            Open `prompts/session03-binary-outcomes-reconstruction.md`. Compare whether the
            generated workflow keeps probability evaluation separate from classification,
            uses the correct outcome in each metric, and distinguishes coefficients, odds
            ratios, marginal effects, and predicted probabilities.

            ### Optional extension

            Assign different costs to false positives and false negatives, calculate the
            total cost at several thresholds, and select a threshold for that decision—not
            because 0.50 is conventional.
            """
        ),
    ]


def airbnb_setup_cells() -> list:
    return [
        code(
            """
            airbnb = pd.read_csv("../../data/raw/airbnb_hackney_course.csv")
            target = "price_eur"
            numeric = ["accommodates", "bedrooms", "bathrooms", "minimum_nights", "number_of_reviews", "review_score"]
            categorical = ["room_type", "property_type", "superhost", "instant_bookable", "kitchen", "wifi", "elevator"]
            features = numeric + categorical
            X = airbnb[features]
            y = airbnb[target]
            """
        ),
        code(
            """
            X_train, X_holdout, y_train, y_holdout = train_test_split(
                X, y, test_size=0.20, random_state=42
            )
            X_train.shape, X_holdout.shape
            """
        ),
    ]


def module17() -> list:
    cells = [
        md(
            """
            # Module 17: Validation and Resampling

            **Case:** How accurately can listing features predict an Airbnb price in
            Hackney?

            We use an untouched holdout set for final evaluation and cross-validation
            within the remaining data for model comparison. The logic follows Gábor's
            used-car cross-validation case and prepares the Airbnb LASSO workflow.
            """
        ),
        code(
            """
            import matplotlib.pyplot as plt
            import pandas as pd
            import seaborn as sns
            from sklearn.compose import ColumnTransformer
            from sklearn.impute import SimpleImputer
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import root_mean_squared_error
            from sklearn.model_selection import KFold, cross_validate, train_test_split
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import OneHotEncoder

            sns.set_theme(style="whitegrid")
            """
        ),
    ]
    cells.extend(airbnb_setup_cells())
    cells.extend(
        [
            md(
                """
                The holdout set is now closed. We do not use it to choose variables,
                transformations, or tuning values. Repeatedly checking it would turn it
                into another training set.
                """
            ),
            code(
                """
                airbnb[[target] + numeric].describe().T.round(1)
                """
            ),
            code(
                """
                airbnb[features].isna().sum().sort_values(ascending=False).head(8)
                """
            ),
            md("## 1. Build reproducible preprocessing"),
            code(
                """
                numeric_pipe = Pipeline([("impute", SimpleImputer(strategy="median"))])
                categorical_pipe = Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("encode", OneHotEncoder(handle_unknown="ignore")),
                    ]
                )
                preprocess = ColumnTransformer(
                    [("numeric", numeric_pipe, numeric), ("categorical", categorical_pipe, categorical)]
                )
                """
            ),
            code(
                """
                rich_model = Pipeline(
                    [("preprocess", preprocess), ("model", LinearRegression())]
                )
                """
            ),
            md("## 2. Compare a small baseline with the richer model"),
            code(
                """
                baseline_features = ["accommodates"]
                baseline = Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="median")),
                        ("model", LinearRegression()),
                    ]
                )
                """
            ),
            code(
                """
                cv = KFold(n_splits=5, shuffle=True, random_state=42)
                baseline_scores = cross_validate(
                    baseline, X_train[baseline_features], y_train, cv=cv,
                    scoring="neg_root_mean_squared_error", return_train_score=True,
                )
                rich_scores = cross_validate(
                    rich_model, X_train, y_train, cv=cv,
                    scoring="neg_root_mean_squared_error", return_train_score=True,
                )
                """
            ),
            code(
                """
                folds = pd.DataFrame(
                    {
                        "fold": range(1, 6),
                        "baseline_rmse": -baseline_scores["test_score"],
                        "rich_rmse": -rich_scores["test_score"],
                    }
                )
                folds.round(2)
                """
            ),
            code(
                """
                folds[["baseline_rmse", "rich_rmse"]].agg(["mean", "std"]).round(2)
                """
            ),
            code(
                """
                plot_folds = folds.melt("fold", var_name="model", value_name="rmse")
                fig, ax = plt.subplots(figsize=(8, 4))
                sns.pointplot(data=plot_folds, x="fold", y="rmse", hue="model", ax=ax)
                ax.set(title="Performance varies across validation folds", ylabel="RMSE (EUR)")
                plt.show()
                """
            ),
            md("## 3. Evaluate the chosen workflow once"),
            code(
                """
                rich_model.fit(X_train, y_train)
                holdout_prediction = rich_model.predict(X_holdout)
                holdout_rmse = root_mean_squared_error(y_holdout, holdout_prediction)
                print(f"Final holdout RMSE: EUR {holdout_rmse:.2f}")
                """
            ),
            code(
                """
                holdout_results = pd.DataFrame({"observed": y_holdout, "predicted": holdout_prediction})
                fig, ax = plt.subplots(figsize=(6, 5))
                sns.scatterplot(data=holdout_results, x="predicted", y="observed", alpha=0.6, ax=ax)
                ax.plot([20, 400], [20, 400], linestyle="--", color="black")
                ax.set(title="Final holdout predictions")
                plt.show()
                """
            ),
            md(
                """
                **Checkpoint:** Cross-validation estimates variation in performance across
                plausible training samples. The untouched holdout answers a different
                question: how did the selected workflow perform on data it never influenced?

                Continue to Module 18, where regularization is tuned within the same
                training data and evaluated on the same untouched holdout definition.

                ### Optional extension

                Repeat the comparison for `log(price_eur)`. Back-transform the predictions
                and evaluate RMSE in euros, not on the log scale alone.
                """
            ),
        ]
    )
    return cells


def module18() -> list:
    cells = [
        md(
            """
            # Module 18: Regularization and Pipelines

            Ridge and LASSO control model flexibility by shrinking coefficients. Their
            tuning parameter must be selected inside cross-validation, while all imputing,
            scaling, and encoding are fitted anew in each training fold. This follows
            Gábor's Airbnb LASSO case with an explicit scikit-learn pipeline.
            """
        ),
        code(
            """
            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd
            import seaborn as sns
            from sklearn.compose import ColumnTransformer
            from sklearn.impute import SimpleImputer
            from sklearn.linear_model import Lasso, Ridge
            from sklearn.metrics import root_mean_squared_error
            from sklearn.model_selection import GridSearchCV, KFold, train_test_split
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import OneHotEncoder, StandardScaler

            sns.set_theme(style="whitegrid")
            """
        ),
    ]
    cells.extend(airbnb_setup_cells())
    cells.extend(
        [
            md("## 1. Put every learned transformation inside the pipeline"),
            code(
                """
                numeric_pipe = Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                )
                categorical_pipe = Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                )
                preprocess = ColumnTransformer(
                    [("numeric", numeric_pipe, numeric), ("categorical", categorical_pipe, categorical)]
                )
                """
            ),
            code(
                """
                ridge_pipeline = Pipeline(
                    [("preprocess", preprocess), ("model", Ridge())]
                )
                lasso_pipeline = Pipeline(
                    [("preprocess", preprocess), ("model", Lasso(max_iter=20_000))]
                )
                """
            ),
            md("## 2. Tune on training data only"),
            code(
                """
                cv = KFold(n_splits=5, shuffle=True, random_state=42)
                ridge_search = GridSearchCV(
                    ridge_pipeline,
                    {"model__alpha": np.logspace(-2, 3, 10)},
                    cv=cv,
                    scoring="neg_root_mean_squared_error",
                    n_jobs=-1,
                )
                ridge_search.fit(X_train, y_train)
                """
            ),
            code(
                """
                lasso_search = GridSearchCV(
                    lasso_pipeline,
                    {"model__alpha": np.logspace(-2, 2, 10)},
                    cv=cv,
                    scoring="neg_root_mean_squared_error",
                    n_jobs=-1,
                )
                lasso_search.fit(X_train, y_train)
                """
            ),
            code(
                """
                tuning_summary = pd.DataFrame(
                    {
                        "model": ["Ridge", "LASSO"],
                        "best_alpha": [ridge_search.best_params_["model__alpha"], lasso_search.best_params_["model__alpha"]],
                        "cv_rmse": [-ridge_search.best_score_, -lasso_search.best_score_],
                    }
                )
                tuning_summary.round(3)
                """
            ),
            code(
                """
                ridge_path = pd.DataFrame(ridge_search.cv_results_)
                lasso_path = pd.DataFrame(lasso_search.cv_results_)
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.plot(ridge_path["param_model__alpha"].astype(float), -ridge_path["mean_test_score"], marker="o", label="Ridge")
                ax.plot(lasso_path["param_model__alpha"].astype(float), -lasso_path["mean_test_score"], marker="o", label="LASSO")
                ax.set_xscale("log")
                ax.set(xlabel="Regularization strength (alpha)", ylabel="Cross-validated RMSE", title="Tune by validation performance")
                ax.legend()
                plt.show()
                """
            ),
            md("## 3. Inspect shrinkage and sparsity"),
            code(
                """
                best_lasso = lasso_search.best_estimator_
                feature_names = best_lasso.named_steps["preprocess"].get_feature_names_out()
                lasso_coefficients = pd.Series(
                    best_lasso.named_steps["model"].coef_, index=feature_names, name="coefficient"
                )
                lasso_coefficients.sort_values(key=abs, ascending=False).head(15).round(2)
                """
            ),
            code(
                """
                pd.Series(
                    {
                        "total coefficients": len(lasso_coefficients),
                        "exactly zero": (lasso_coefficients == 0).sum(),
                    }
                )
                """
            ),
            md("## 4. Select by cross-validation, evaluate once on holdout"),
            code(
                """
                searches = {"Ridge": ridge_search, "LASSO": lasso_search}
                selected_name = min(searches, key=lambda name: -searches[name].best_score_)
                selected_model = searches[selected_name].best_estimator_
                holdout_prediction = selected_model.predict(X_holdout)
                holdout_rmse = root_mean_squared_error(y_holdout, holdout_prediction)
                print(f"Selected model: {selected_name}")
                print(f"Untouched holdout RMSE: EUR {holdout_rmse:.2f}")
                """
            ),
            code(
                """
                holdout_results = pd.DataFrame({"observed": y_holdout, "predicted": holdout_prediction})
                holdout_results.assign(error=lambda frame: frame["observed"] - frame["predicted"]).describe().round(1)
                """
            ),
            md(
                """
                ## Session 4 reconstruction handoff

                Open `prompts/session04-validation-regularization-reconstruction.md`. Treat
                the generated code as suspect until you verify the split order, the scope
                of preprocessing, the tuning data, the metric sign, and the one-time use of
                the holdout set.

                ### Optional extension

                Add Elastic Net with both `alpha` and `l1_ratio` in the search grid. Explain
                why the larger grid increases computation and why the holdout still must
                not guide either hyperparameter.
                """
            ),
        ]
    )
    return cells


def module19() -> list:
    return [
        md(
            """
            # Module 19: PCA and Clustering

            **Case:** Can several dimensions of management practice be summarized, and do
            firms form useful descriptive groups?

            The management-index and PCA material adapts Gábor's World Management Survey
            feature-engineering lecture. K-means is an extension. Both methods are
            unsupervised: no outcome is used while fitting them.
            """
        ),
        code(
            """
            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd
            import seaborn as sns
            from sklearn.cluster import KMeans
            from sklearn.decomposition import PCA
            from sklearn.metrics import silhouette_score
            from sklearn.preprocessing import StandardScaler

            sns.set_theme(style="whitegrid")
            """
        ),
        code(
            """
            wms = pd.read_csv("../../data/raw/wms_course.csv")
            practices = ["operations", "monitor", "target", "people"]
            wms[practices + ["management", "employees"]].describe().T.round(2)
            """
        ),
        md("## 1. Construct a transparent management index"),
        code(
            """
            wms["management_index"] = wms[practices].mean(axis=1)
            wms[["management_index", "management"]].corr().round(3)
            """
        ),
        code(
            """
            fig, axes = plt.subplots(1, 2, figsize=(12, 4))
            sns.histplot(wms["management_index"], bins=25, ax=axes[0])
            sns.scatterplot(data=wms, x="management_index", y="management", alpha=0.35, ax=axes[1])
            axes[0].set(title="Constructed management index")
            axes[1].set(title="Constructed and published measures")
            plt.tight_layout()
            plt.show()
            """
        ),
        md("## 2. Standardize before variance- and distance-based methods"),
        code(
            """
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(wms[practices])
            pd.DataFrame(X_scaled, columns=practices).agg(["mean", "std"]).round(2)
            """
        ),
        md("## 3. PCA constructs weighted combinations"),
        code(
            """
            pca = PCA()
            scores = pca.fit_transform(X_scaled)
            explained = pd.DataFrame(
                {"component": range(1, 5), "variance_share": pca.explained_variance_ratio_, "cumulative": np.cumsum(pca.explained_variance_ratio_)}
            )
            explained.round(3)
            """
        ),
        code(
            """
            fig, ax = plt.subplots(figsize=(7, 4))
            sns.barplot(data=explained, x="component", y="variance_share", color="steelblue", ax=ax)
            ax.set(title="Variance explained by each component", ylabel="Share of variance")
            plt.show()
            """
        ),
        code(
            """
            loadings = pd.DataFrame(
                pca.components_.T,
                index=practices,
                columns=[f"PC{i}" for i in range(1, 5)],
            )
            loadings.round(3)
            """
        ),
        code(
            """
            wms[["pc1", "pc2"]] = scores[:, :2]
            wms[["management_index", "pc1", "pc2"]].corr().round(3)
            """
        ),
        code(
            """
            fig, ax = plt.subplots(figsize=(8, 5))
            points = ax.scatter(wms["pc1"], wms["pc2"], c=np.log(wms["employees"]), cmap="viridis", alpha=0.55)
            ax.set(title="Firms in principal-component space", xlabel="PC1 score", ylabel="PC2 score")
            fig.colorbar(points, ax=ax, label="Log employees")
            plt.show()
            """
        ),
        md("## 4. Use k-means as a descriptive grouping tool"),
        code(
            """
            candidates = []
            for k in range(2, 7):
                labels = KMeans(n_clusters=k, n_init=20, random_state=42).fit_predict(X_scaled)
                candidates.append({"k": k, "silhouette": silhouette_score(X_scaled, labels)})
            candidate_scores = pd.DataFrame(candidates)
            candidate_scores.round(3)
            """
        ),
        code(
            """
            best_k = int(candidate_scores.loc[candidate_scores["silhouette"].idxmax(), "k"])
            kmeans = KMeans(n_clusters=best_k, n_init=20, random_state=42)
            wms["cluster"] = kmeans.fit_predict(X_scaled)
            print(f"Selected k by silhouette score: {best_k}")
            """
        ),
        code(
            """
            profile = wms.groupby("cluster")[practices + ["management_index", "employees"]].agg(["mean", "count"])
            profile.round(2)
            """
        ),
        code(
            """
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.scatterplot(data=wms, x="pc1", y="pc2", hue="cluster", palette="tab10", alpha=0.6, ax=ax)
            ax.set(title="K-means groups shown in PCA space")
            plt.show()
            """
        ),
        md(
            """
            Cluster numbers are arbitrary, and a short label is only a description of this
            sample. Calling a cluster “high-performing” would require an outcome and a
            separate analysis; k-means did not establish performance or causality.

            ## Session 5 reconstruction handoff

            Open `prompts/session05-unsupervised-reconstruction.md`. Audit whether the LLM
            standardizes before PCA and k-means, distinguishes loadings from scores, keeps
            outcomes out of fitting, and avoids invented cluster narratives.

            ### Optional extension

            Compare country-level means of PC1 and the transparent management index. Ask
            whether their substantive conclusions agree and what sample-composition
            differences could affect the comparison.
            """
        ),
    ]


def module20() -> list:
    return [
        md(
            """
            # Module 20: Regression Trees

            **Case:** Predict the price of a used Toyota Camry from its age and features.

            The sequence follows Gábor's Chapter 15 CART case: begin with age alone, read a
            small tree, compare it with a linear model, expose overfitting, then tune a
            multiple-feature tree and evaluate it on untouched data.
            """
        ),
        code(
            """
            import matplotlib.pyplot as plt
            import pandas as pd
            import seaborn as sns
            from sklearn.compose import ColumnTransformer
            from sklearn.inspection import permutation_importance
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import root_mean_squared_error
            from sklearn.model_selection import GridSearchCV, KFold, train_test_split
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import OneHotEncoder
            from sklearn.tree import DecisionTreeRegressor, plot_tree

            sns.set_theme(style="whitegrid")
            """
        ),
        code(
            """
            cars = pd.read_csv("../../data/raw/used_cars_course.csv")
            cars[["price", "age", "odometer_10k_miles"]].describe().T.round(1)
            """
        ),
        md("## 1. Compare a linear relationship with a shallow tree"),
        code(
            """
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.regplot(data=cars, x="age", y="price", lowess=True, scatter_kws={"alpha": 0.55}, ax=ax)
            ax.set(title="Used-car price and age", ylabel="Price (USD)")
            plt.show()
            """
        ),
        code(
            """
            train, test = train_test_split(cars, test_size=0.25, random_state=42)
            age_tree = DecisionTreeRegressor(max_depth=2, min_samples_leaf=20, random_state=42)
            age_tree.fit(train[["age"]], train["price"])
            """
        ),
        code(
            """
            fig, ax = plt.subplots(figsize=(12, 6))
            plot_tree(age_tree, feature_names=["age"], filled=True, rounded=True, ax=ax)
            ax.set_title("A depth-two regression tree")
            plt.show()
            """
        ),
        code(
            """
            example_ages = pd.DataFrame({"age": [2, 5, 8, 12, 16]})
            example_ages["tree_prediction"] = age_tree.predict(example_ages)
            example_ages.round(0)
            """
        ),
        code(
            """
            age_linear = LinearRegression().fit(train[["age"]], train["price"])
            age_comparison = pd.Series(
                {
                    "linear_test_rmse": root_mean_squared_error(test["price"], age_linear.predict(test[["age"]])),
                    "tree_test_rmse": root_mean_squared_error(test["price"], age_tree.predict(test[["age"]])),
                }
            )
            age_comparison.round(0)
            """
        ),
        md("## 2. Add features through a reproducible pipeline"),
        code(
            """
            target = "price"
            numeric = ["age", "odometer_10k_miles", "dealer"]
            categorical = ["condition", "cylinders", "drive", "area", "trim"]
            features = numeric + categorical
            X_train, y_train = train[features], train[target]
            X_test, y_test = test[features], test[target]
            """
        ),
        code(
            """
            preprocess = ColumnTransformer(
                [
                    ("numeric", "passthrough", numeric),
                    ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical),
                ]
            )
            unrestricted = Pipeline(
                [("preprocess", preprocess), ("model", DecisionTreeRegressor(random_state=42))]
            )
            unrestricted.fit(X_train, y_train)
            """
        ),
        code(
            """
            pd.Series(
                {
                    "training_rmse": root_mean_squared_error(y_train, unrestricted.predict(X_train)),
                    "test_rmse": root_mean_squared_error(y_test, unrestricted.predict(X_test)),
                }
            ).round(0)
            """
        ),
        md(
            """
            A very small training error paired with a much larger test error is evidence of
            overfitting. We restrict the tree using hyperparameters chosen by
            cross-validation—not by looking repeatedly at the test set.
            """
        ),
        md("## 3. Tune complexity on the training data"),
        code(
            """
            tree_pipeline = Pipeline(
                [("preprocess", preprocess), ("model", DecisionTreeRegressor(random_state=42))]
            )
            parameter_grid = {
                "model__max_depth": [2, 3, 4, 5, 7, None],
                "model__min_samples_leaf": [5, 10, 20, 35],
            }
            cv = KFold(n_splits=5, shuffle=True, random_state=42)
            search = GridSearchCV(
                tree_pipeline, parameter_grid, cv=cv,
                scoring="neg_root_mean_squared_error", n_jobs=-1,
            )
            search.fit(X_train, y_train)
            """
        ),
        code(
            """
            results = pd.DataFrame(search.cv_results_)
            results[["param_model__max_depth", "param_model__min_samples_leaf", "mean_test_score"]].assign(
                cv_rmse=lambda frame: -frame["mean_test_score"]
            ).nsmallest(8, "cv_rmse").round(1)
            """
        ),
        code(
            """
            best_tree = search.best_estimator_
            test_prediction = best_tree.predict(X_test)
            print(search.best_params_)
            print(f"Cross-validated training RMSE: {-search.best_score_:.0f}")
            print(f"Untouched test RMSE: {root_mean_squared_error(y_test, test_prediction):.0f}")
            """
        ),
        md("## 4. Interpret the selected tree cautiously"),
        code(
            """
            transformed_names = best_tree.named_steps["preprocess"].get_feature_names_out()
            fitted_tree = best_tree.named_steps["model"]
            importance = pd.Series(fitted_tree.feature_importances_, index=transformed_names)
            importance.sort_values(ascending=False).head(12).round(3)
            """
        ),
        code(
            """
            permutation = permutation_importance(
                best_tree, X_test, y_test, n_repeats=20, random_state=42,
                scoring="neg_root_mean_squared_error",
            )
            pd.Series(permutation.importances_mean, index=features).sort_values(ascending=False).round(2)
            """
        ),
        code(
            """
            fig, ax = plt.subplots(figsize=(16, 8))
            plot_tree(
                fitted_tree, feature_names=transformed_names,
                filled=True, rounded=True, max_depth=3, ax=ax,
            )
            ax.set_title("Top levels of the tuned regression tree")
            plt.show()
            """
        ),
        md(
            """
            Feature importance describes the fitted prediction rule, not a causal effect.
            Correlated features can substitute for one another, and impurity-based
            importance can favor variables offering many possible split points.

            ## Session 6 reconstruction handoff

            Open `prompts/session06-tree-reconstruction.md`. Audit the generated split
            logic, stopping criteria, validation design, metric, feature-importance claims,
            and use of the test set.

            ### Optional extension: cost-complexity pruning

            Obtain the pruning path from the training data, select several candidate
            `ccp_alpha` values, and compare them by cross-validation. This is post-pruning;
            `max_depth` and `min_samples_leaf` are pre-pruning controls.
            """
        ),
        code(
            """
            transformed_train = best_tree.named_steps["preprocess"].transform(X_train)
            pruning_path = DecisionTreeRegressor(random_state=42).cost_complexity_pruning_path(
                transformed_train, y_train
            )
            pd.Series(pruning_path.ccp_alphas).describe(percentiles=[0.5, 0.75, 0.9, 0.95]).round(3)
            """
        ),
    ]


NOTEBOOKS = {
    "modules/module12-simple-linear-regression/simple_linear_regression.ipynb": module12,
    "modules/module13-multiple-regression-workflow/multiple_regression_workflow.ipynb": module13,
    "modules/module14-categorical-variables-interactions/categorical_variables_interactions.ipynb": module14,
    "modules/module15-diagnostics-transformations/diagnostics_transformations.ipynb": module15,
    "modules/module16-logistic-regression/logistic_regression.ipynb": module16,
    "modules/module17-validation-resampling/validation_resampling.ipynb": module17,
    "modules/module18-regularization-pipelines/regularization_pipelines.ipynb": module18,
    "modules/module19-unsupervised-learning/unsupervised_learning.ipynb": module19,
    "modules/module20-regression-tree/regression_tree.ipynb": module20,
}


def main() -> None:
    for path, builder in NOTEBOOKS.items():
        write_notebook(path, builder())


if __name__ == "__main__":
    main()
