"""Jeu de données SYNTHÉTIQUE servant uniquement à tester l'application hors ligne."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .constants import REGIONS

# profil de base (GWh par mois) : conso, nucléaire, hydro, éolien, solaire, bio, thermique
PROFILES = {
    "Auvergne-Rhône-Alpes": (5200, 2600, 1700, 90, 40, 70, 120),
    "Bourgogne-Franche-Comté": (1700, 0, 330, 70, 25, 25, 20),
    "Bretagne": (1550, 0, 40, 160, 25, 30, 90),
    "Centre-Val de Loire": (1500, 3600, 5, 130, 30, 20, 20),
    "Grand Est": (3000, 5200, 330, 330, 40, 40, 80),
    "Hauts-de-France": (3300, 3500, 3, 330, 30, 45, 380),
    "Normandie": (1900, 3100, 3, 130, 20, 25, 180),
    "Nouvelle-Aquitaine": (3200, 1700, 330, 120, 140, 50, 60),
    "Occitanie": (2700, 1600, 650, 130, 130, 35, 40),
    "Pays de la Loire": (2100, 0, 3, 140, 30, 35, 260),
    "Provence-Alpes-Côte d'Azur": (2900, 0, 1100, 15, 110, 30, 420),
    "Île-de-France": (4700, 0, 1, 1, 10, 55, 280),
}


def make_demo(seed_file: str = "seeds.json") -> pd.DataFrame:
    seeds = json.loads(Path(seed_file).read_text()) if Path(seed_file).exists() else {}
    rng = np.random.default_rng(seeds.get("random_seed", 42))
    y0, y1 = seeds.get("demo_start_year", 2013), seeds.get("demo_end_year", 2024)
    rows = []
    for region, (code, *_rest) in REGIONS.items():
        cons, nuc, hyd, wind, sol, bio, therm = PROFILES[region]
        for ts in pd.date_range(f"{y0}-01-01", f"{y1}-12-01", freq="MS"):
            t = ts.year - y0
            season = 1 + 0.25 * np.cos((ts.month - 1) / 12 * 2 * np.pi)
            noise = lambda s=0.06: rng.normal(1, s)
            days = ts.days_in_month
            rows.append(dict(
                region_code=code, region=region, month=ts,
                consommation_mwh=cons * 1000 * season * noise(0.03) * (1 - 0.004 * t),
                nucleaire_mwh=nuc * 1000 * (1.1 - 0.5 * (season - 1)) * noise(0.05),
                thermique_mwh=therm * 1000 * max(0.25, 1 - 0.05 * t) * season * noise(0.1),
                hydraulique_mwh=hyd * 1000 * noise(0.15),
                eolien_mwh=wind * 1000 * (1 + 0.12 * t) * (1.2 - 0.4 * (season - 1)) * noise(0.2),
                solaire_mwh=sol * 1000 * (1 + 0.22 * t) * (2 - season) * noise(0.1),
                bioenergies_mwh=bio * 1000 * (1 + 0.04 * t) * noise(0.03),
                n_rows=days * 48, n_dup=0, n_null=int(rng.integers(0, 4)), n_neg=0,
            ))
    return pd.DataFrame(rows)
