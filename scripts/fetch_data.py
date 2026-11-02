"""Download and prepare the local teaching datasets for Coding 2.

The analysis datasets accompany Gabor Bekes and Gabor Kezdi's *Data Analysis for
Business, Economics, and Policy*. The introduction also uses pretrained GloVe
word vectors. Notebooks never access these URLs directly: this script verifies
the source files and writes small, course-ready analysis extracts.
"""

from __future__ import annotations

import hashlib
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SOURCE = RAW / "source"


@dataclass(frozen=True)
class SourceFile:
    filename: str
    url: str
    sha256: str


SOURCES = {
    "hotels_price": SourceFile(
        "hotels_price.csv",
        "https://osf.io/p6tyr/download",
        "f86a8d6a1c525d3811acea1e43b00a6ffca7d76e296d739880022b5e80b6d765",
    ),
    "hotels_features": SourceFile(
        "hotels_features.csv",
        "https://osf.io/utwjs/download",
        "4c8e13164556f70dbc00d4bf4ecc14651cb921cda929c6662cf291c963ec8e33",
    ),
    "share_health": SourceFile(
        "share_health.csv",
        "https://osf.io/3ze58/download",
        "b33a92720449ed41bf1bd022595e4a1c8645dd0d31a3793f0c9bfe325f9014ab",
    ),
    "airbnb_london": SourceFile(
        "airbnb_london.csv",
        "https://osf.io/7n96w/download",
        "661581d6ef8c2f19c00de0c39997f1b5825b983a8cef2fcd5b991396dbe8a3a1",
    ),
    "wms": SourceFile(
        "wms.csv",
        "https://osf.io/uzpce/download",
        "736af40a69737d364f41461c315c61b0febaec5a896998ed66d1c362e339827f",
    ),
    "used_cars": SourceFile(
        "used_cars.csv",
        "https://osf.io/7gvz9/download",
        "4db49a2ac9ea87e0cc6df95477d5f17a21ba94fd118f85e70d93befaaca0a819",
    ),
    "word_vectors": SourceFile(
        "glove-wiki-gigaword-50.gz",
        "https://github.com/piskvorky/gensim-data/releases/download/"
        "glove-wiki-gigaword-50/glove-wiki-gigaword-50.gz",
        "5c55f98957aa9fed8d2ac5fb1dcff57af3b23c5a3ee7af3f7945f8d49198eb24",
    ),
}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download(source: SourceFile) -> Path:
    path = SOURCE / source.filename
    if path.exists() and file_hash(path) == source.sha256:
        return path

    request = urllib.request.Request(
        source.url,
        headers={"User-Agent": "Coding-2-CEU/2026 (teaching data fetch)"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        path.write_bytes(response.read())

    actual = file_hash(path)
    if actual != source.sha256:
        path.unlink(missing_ok=True)
        raise RuntimeError(
            f"Checksum mismatch for {source.filename}: expected {source.sha256}, got {actual}"
        )
    return path


def prepare_hotels(paths: dict[str, Path]) -> pd.DataFrame:
    prices = pd.read_csv(paths["hotels_price"])
    features = pd.read_csv(paths["hotels_features"])
    hotels = prices.merge(features, on="hotel_id", validate="many_to_one")

    required = ["price", "distance", "stars", "rating"]
    keep = (
        hotels["city_actual"].isin(["Amsterdam", "Barcelona", "Vienna"])
        & hotels["accommodation_type"].isin(["Apartment", "Hotel"])
        & hotels["year"].eq(2017)
        & hotels["month"].eq(11)
        & hotels["weekend"].eq(0)
        & hotels["nnights"].eq(1)
        & hotels["stars"].between(3, 4)
        & hotels["price"].between(20, 600)
        & hotels[required].notna().all(axis=1)
    )
    columns = [
        "hotel_id",
        "city_actual",
        "accommodation_type",
        "price",
        "distance",
        "stars",
        "rating",
        "rating_reviewcount",
    ]
    course = hotels.loc[keep, columns].rename(
        columns={
            "city_actual": "city",
            "accommodation_type": "accommodation",
            "distance": "distance_miles",
            "rating_reviewcount": "review_count",
        }
    )
    return course.assign(log_price=np.log(course["price"])).sort_values("hotel_id")


def prepare_share_health(path: Path) -> pd.DataFrame:
    share = pd.read_csv(path)
    columns = [
        "ID",
        "country_str",
        "stayshealthy",
        "smoking",
        "ever_smoked",
        "female",
        "age",
        "income10",
        "eduyears",
        "bmi",
        "exerc",
    ]
    course = share[columns].dropna().rename(
        columns={"ID": "person_id", "country_str": "country"}
    )
    integer_columns = [
        "person_id",
        "stayshealthy",
        "smoking",
        "ever_smoked",
        "female",
        "income10",
        "exerc",
    ]
    course[integer_columns] = course[integer_columns].astype(int)
    return course.reset_index(drop=True)


def prepare_airbnb(path: Path) -> pd.DataFrame:
    airbnb = pd.read_csv(path, low_memory=False)
    airbnb["price_eur"] = (
        airbnb["price"].astype(str).str.replace(r"[$,]", "", regex=True).astype(float)
    )
    airbnb = airbnb.loc[
        airbnb["neighbourhood_cleansed"].eq("Hackney")
        & airbnb["price_eur"].between(20, 400)
        & airbnb["accommodates"].between(1, 8)
    ].copy()

    columns = {
        "id": "listing_id",
        "price_eur": "price_eur",
        "accommodates": "accommodates",
        "bedrooms": "bedrooms",
        "bathrooms": "bathrooms",
        "minimum_nights": "minimum_nights",
        "number_of_reviews": "number_of_reviews",
        "review_scores_rating": "review_score",
        "room_type": "room_type",
        "property_type": "property_type",
        "host_is_superhost": "superhost",
        "instant_bookable": "instant_bookable",
        "Kitchen": "kitchen",
        "Wireless Internet": "wifi",
        "Elevator in building": "elevator",
    }
    course = airbnb[list(columns)].rename(columns=columns)
    course = course.dropna(subset=["listing_id", "price_eur", "room_type", "property_type"])
    course["listing_id"] = course["listing_id"].astype(int)
    if len(course) > 3000:
        course = course.sample(3000, random_state=42)
    return course.sort_values("listing_id").reset_index(drop=True)


def prepare_wms(path: Path) -> pd.DataFrame:
    wms = pd.read_csv(path, low_memory=False)
    columns = [
        "firmid",
        "wave",
        "country",
        "operations",
        "monitor",
        "target",
        "people",
        "management",
        "emp_firm",
    ]
    course = wms[columns].dropna().rename(
        columns={
            "firmid": "firm_id",
            "wave": "year",
            "emp_firm": "employees",
        }
    )
    course = course.loc[course["employees"].between(10, 10_000)].copy()
    if len(course) > 2000:
        course = course.sample(2000, random_state=42)
    return course.sort_values(["firm_id", "year"]).reset_index(drop=True)


def prepare_used_cars(path: Path) -> pd.DataFrame:
    cars = pd.read_csv(path)
    keep = (
        cars["Hybrid"].eq(0)
        & cars["fuel"].eq("gas")
        & ~cars["condition"].isin(["new", "fair"])
        & cars["price"].between(500, 25_000)
        & cars["odometer"].le(100)
        & ~(
            cars["price"].lt(1000)
            & (cars["condition"].eq("like new") | cars["age"].lt(8))
        )
        & cars["transmission"].ne("manual")
        & ~cars["type"].isin(["truck", "pickup"])
    )
    course = cars.loc[keep].copy()
    course["trim"] = np.select(
        [course["LE"].eq(1), course["XLE"].eq(1), course["SE"].eq(1)],
        ["LE", "XLE", "SE"],
        default="base",
    )
    course = course[
        [
            "price",
            "age",
            "odometer",
            "condition",
            "cylinders",
            "drive",
            "dealer",
            "area",
            "trim",
        ]
    ].rename(columns={"odometer": "odometer_10k_miles"})
    categorical = ["condition", "cylinders", "drive", "area", "trim"]
    course[categorical] = course[categorical].fillna("unknown")
    return course.reset_index(drop=True)


def write_dataset(name: str, frame: pd.DataFrame) -> None:
    path = RAW / name
    frame.to_csv(path, index=False)
    print(f"wrote {path.relative_to(ROOT)} ({len(frame)} rows, {len(frame.columns)} columns)")


def main() -> None:
    SOURCE.mkdir(parents=True, exist_ok=True)
    paths = {name: download(source) for name, source in SOURCES.items()}
    print(f"ready {paths['word_vectors'].relative_to(ROOT)} (pretrained word vectors)")
    write_dataset("hotels_course.csv", prepare_hotels(paths))
    write_dataset("share_health_course.csv", prepare_share_health(paths["share_health"]))
    write_dataset("airbnb_hackney_course.csv", prepare_airbnb(paths["airbnb_london"]))
    write_dataset("wms_course.csv", prepare_wms(paths["wms"]))
    write_dataset("used_cars_course.csv", prepare_used_cars(paths["used_cars"]))


if __name__ == "__main__":
    main()
