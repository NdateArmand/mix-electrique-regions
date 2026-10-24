"""Nettoyage, indicateurs et tables dérivées (feature engineering)."""
import numpy as np
import pandas as pd

from .constants import LOW_CARBON, RENEWABLE, SOURCES, WIND_SOLAR

MWH_COLS = [f"{s}_mwh" for s in SOURCES]


def clean_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """Types, tri et suppression des doublons région-mois."""
    out = df.copy()
    out["month"] = pd.to_datetime(out["month"])
    out["year"] = out["month"].dt.year
    out = out.drop_duplicates(["region", "month"]).sort_values(["region", "month"])
    return out.reset_index(drop=True)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute production totale, parts et taux de couverture."""
    out = df.copy()
    out[MWH_COLS] = out[MWH_COLS].fillna(0.0)
    out["production_mwh"] = out[MWH_COLS].sum(axis=1)
    out["low_carbon_mwh"] = out[[f"{s}_mwh" for s in LOW_CARBON]].sum(axis=1)
    out["renewable_mwh"] = out[[f"{s}_mwh" for s in RENEWABLE]].sum(axis=1)
    out["wind_solar_mwh"] = out[[f"{s}_mwh" for s in WIND_SOLAR]].sum(axis=1)
    return out


def aggregate(df: pd.DataFrame, by: list) -> pd.DataFrame:
    """Somme les énergies puis recalcule les ratios (jamais de moyenne de ratios)."""
    cols = MWH_COLS + ["production_mwh", "low_carbon_mwh", "renewable_mwh",
                       "wind_solar_mwh", "consommation_mwh"]
    g = df.groupby(by, as_index=False)[cols].sum()
    return add_ratios(g)


def add_ratios(g: pd.DataFrame) -> pd.DataFrame:
    prod = g["production_mwh"].replace(0, np.nan)
    cons = g["consommation_mwh"].replace(0, np.nan)
    g["low_carbon_share"] = 100 * g["low_carbon_mwh"] / prod
    g["renewable_share"] = 100 * g["renewable_mwh"] / prod
    g["wind_solar_share"] = 100 * g["wind_solar_mwh"] / prod
    g["nuclear_share"] = 100 * g["nucleaire_mwh"] / prod
    g["fossil_share"] = 100 * g["thermique_mwh"] / prod
    g["coverage"] = 100 * g["production_mwh"] / cons
    return g


def quality_report(df: pd.DataFrame) -> dict:
    """Indicateurs de qualité calculés pendant l'agrégation (voir download_data.py)."""
    rows = int(df["n_rows"].sum())
    return {
        "rows_raw": rows,
        "months": int(len(df)),
        "dup_rows": int(df["n_dup"].sum()),
        "null_cells": int(df["n_null"].sum()),
        "neg_cells": int(df["n_neg"].sum()),
        "null_pct": 100 * df["n_null"].sum() / max(rows * len(SOURCES), 1),
    }


def completeness_by_region_year(df: pd.DataFrame) -> pd.DataFrame:
    """Part des demi-heures théoriques effectivement présentes, par région et année."""
    g = df.groupby(["region", "year"], as_index=False)["n_rows"].sum()
    days = g["year"].map(lambda y: 366 if pd.Timestamp(year=int(y), month=1, day=1).is_leap_year else 365)
    g["completeness_pct"] = (100 * g["n_rows"] / (days * 48)).clip(upper=100)
    return g
