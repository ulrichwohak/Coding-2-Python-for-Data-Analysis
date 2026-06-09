"""Generate deterministic local teaching datasets for Coding 2."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def make_career_outcomes(rng: np.random.Generator) -> pd.DataFrame:
    n = 240
    sectors = np.array(["finance", "public", "retail", "technology"])
    sector = rng.choice(sectors, size=n, p=[0.25, 0.2, 0.25, 0.3])
    experience = rng.gamma(shape=3.0, scale=2.2, size=n).clip(0, 20)
    education = rng.choice([12, 14, 16, 18], size=n, p=[0.12, 0.25, 0.45, 0.18])
    training = rng.normal(38, 16, size=n).clip(0, 100)
    remote = rng.binomial(1, np.where(sector == "technology", 0.62, 0.28))
    ai_tool_use = rng.normal(3.0 + 0.08 * training + 0.7 * remote, 1.7, size=n).clip(0, 10)

    sector_effect = {
        "finance": 8.0,
        "public": -4.0,
        "retail": -7.0,
        "technology": 9.5,
    }
    salary = (
        29
        + 2.7 * experience
        + 2.2 * (education - 12)
        + 0.22 * training
        + 1.5 * ai_tool_use
        + np.array([sector_effect[s] for s in sector])
        + rng.normal(0, 7.5, size=n)
    )

    promotion_score = (
        -4.3
        + 0.22 * experience
        + 0.045 * training
        + 0.32 * ai_tool_use
        + 0.55 * remote
        + np.where(sector == "technology", 0.35, 0.0)
    )
    promotion_probability = 1 / (1 + np.exp(-promotion_score))
    promoted = rng.binomial(1, promotion_probability)

    return pd.DataFrame(
        {
            "experience_years": experience.round(1),
            "education_years": education,
            "training_hours": training.round(1),
            "sector": sector,
            "remote": remote,
            "ai_tool_use": ai_tool_use.round(1),
            "salary_k_eur": salary.round(1),
            "promoted": promoted,
        }
    )


def make_housing_sales(rng: np.random.Generator) -> pd.DataFrame:
    n = 360
    district = rng.choice(["central", "inner_ring", "outer_ring", "suburban"], size=n, p=[0.18, 0.34, 0.3, 0.18])
    size = rng.normal(78, 25, size=n).clip(28, 180)
    rooms = np.maximum(1, np.round(size / rng.normal(28, 5, size=n))).astype(int).clip(1, 7)
    age = rng.gamma(3.0, 14.0, size=n).clip(0, 120)
    transit = rng.binomial(1, np.where(np.isin(district, ["central", "inner_ring"]), 0.72, 0.38))
    renovation = rng.normal(5.5 - 0.025 * age + 1.0 * transit, 1.8, size=n).clip(0, 10)
    district_effect = {
        "central": 120,
        "inner_ring": 65,
        "outer_ring": 18,
        "suburban": -8,
    }
    price = (
        55
        + 4.0 * size
        + 11 * rooms
        - 1.0 * age
        + 22 * transit
        + 13 * renovation
        + 0.014 * size**2
        + np.array([district_effect[d] for d in district])
        + rng.normal(0, 42, size=n)
    )

    return pd.DataFrame(
        {
            "size_sq_m": size.round(1),
            "rooms": rooms,
            "age_years": age.round(1),
            "district": district,
            "near_transit": transit,
            "renovation_score": renovation.round(1),
            "price_k_eur": price.round(1),
        }
    )


def make_campaign_response(rng: np.random.Generator) -> pd.DataFrame:
    n = 320
    segment = rng.choice(["budget", "loyal", "occasional", "premium"], size=n, p=[0.24, 0.28, 0.32, 0.16])
    age = rng.normal(39, 11, size=n).clip(18, 72)
    visits = rng.poisson(np.where(segment == "loyal", 7, np.where(segment == "premium", 5, 3)), size=n)
    emails_opened = rng.binomial(8, np.where(segment == "loyal", 0.58, np.where(segment == "budget", 0.34, 0.43)), size=n)
    discount = rng.choice([0, 5, 10, 15, 20, 25], size=n, p=[0.12, 0.14, 0.24, 0.22, 0.18, 0.10])
    prior_spend = rng.gamma(shape=2.0, scale=np.where(segment == "premium", 95, 48), size=n)
    logit = (
        -3.0
        + 0.18 * visits
        + 0.28 * emails_opened
        + 0.055 * discount
        + 0.004 * prior_spend
        + np.where(segment == "loyal", 0.7, 0)
        + np.where(segment == "budget", -0.35, 0)
    )
    response_probability = 1 / (1 + np.exp(-logit))
    responded = rng.binomial(1, response_probability)

    return pd.DataFrame(
        {
            "age": age.round(0).astype(int),
            "visits_last_month": visits,
            "emails_opened": emails_opened,
            "discount_pct": discount,
            "prior_spend_eur": prior_spend.round(2),
            "segment": segment,
            "responded": responded,
        }
    )


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20260209)
    datasets = {
        "career_outcomes.csv": make_career_outcomes(rng),
        "housing_sales.csv": make_housing_sales(rng),
        "campaign_response.csv": make_campaign_response(rng),
    }
    for name, frame in datasets.items():
        path = RAW / name
        frame.to_csv(path, index=False)
        print(f"wrote {path.relative_to(ROOT)} ({len(frame)} rows)")


if __name__ == "__main__":
    main()
