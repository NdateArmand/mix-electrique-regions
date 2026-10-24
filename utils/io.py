"""Chargement des données : table mensuelle locale produite par scripts/download_data.py."""
import json
from pathlib import Path

import pandas as pd

from .demo import make_demo

ROOT = Path(__file__).resolve().parent.parent
MONTHLY_CSV = ROOT / "data" / "monthly.csv"
GEOJSON_PATH = ROOT / "data" / "regions.geojson"

LICENSE_TEXT = (
    "Données éCO2mix régionales consolidées et définitives, RTE via Open Data Réseaux "
    "Énergies, Licence Ouverte 2.0 (Etalab). Le code de ce projet est fourni à titre pédagogique."
)
SOURCE_URL = "https://www.data.gouv.fr/datasets/donnees-eco2mix-regionales-consolidees-et-definitives"


def load_data():
    """Retourne (table mensuelle, is_demo). Bascule sur le jeu synthétique si le CSV est absent."""
    if MONTHLY_CSV.exists():
        return pd.read_csv(MONTHLY_CSV, parse_dates=["month"]), False
    return make_demo(str(ROOT / "seeds.json")), True


def load_geojson():
    if GEOJSON_PATH.exists():
        return json.loads(GEOJSON_PATH.read_text(encoding="utf-8"))
    return None
