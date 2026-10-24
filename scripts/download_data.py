"""Télécharge éCO2mix régional (data.gouv.fr) et produit la table mensuelle data/monthly.csv.

Usage :
    python scripts/download_data.py                  # télécharge le CSV de data.gouv puis agrège
    python scripts/download_data.py fichier.csv      # utilise un CSV déjà téléchargé
    python scripts/download_data.py demo             # jeu synthétique, sans réseau

Les fichiers bruts sont mis en cache dans data/raw/ (non versionnés). Relancer le script
ne retélécharge pas le fichier déjà présent. Les contrôles qualité sont calculés ici.
"""
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from utils.constants import GEOJSON_URL, REGIONS, SOURCES, STEP_HOURS  # noqa: E402
from utils.demo import make_demo  # noqa: E402

CSV_URL = "https://www.data.gouv.fr/api/1/datasets/r/4c308634-d76e-40b0-a777-ab99a8871564"
RAW_DIR = ROOT / "data" / "raw"
RAW_FILE = RAW_DIR / "eco2mix_regional.csv"
OUT = ROOT / "data" / "monthly.csv"
WANTED = {"code_insee_region", "libelle_region", "date", "heure", "date_heure", "consommation", *SOURCES}


def fetch_raw() -> Path:
    """Télécharge le CSV complet (une seule fois, mis en cache dans data/raw)."""
    if RAW_FILE.exists():
        return RAW_FILE
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print("Téléchargement du CSV complet (plusieurs centaines de Mo)...")
    tmp = RAW_FILE.with_suffix(".part")
    with requests.get(CSV_URL, stream=True, timeout=600, allow_redirects=True) as r:
        r.raise_for_status()
        done = 0
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
                done += len(chunk)
                print(f"\r  {done / 1e6:,.0f} Mo", end="")
    tmp.rename(RAW_FILE)
    print()
    return RAW_FILE


def norm(col: str) -> str:
    """Normalise un intitulé : minuscules, sans accents, sans unité, mots séparés par _."""
    c = unicodedata.normalize("NFKD", str(col)).encode("ascii", "ignore").decode().lower()
    c = re.sub(r"\(.*?\)", "", c)          # retire (MW), (%)
    c = re.sub(r"[^a-z0-9]+", "_", c).strip("_")
    return re.sub(r"_mw$", "", c)


ALIASES = {  # intitulé normalisé vers nom interne
    "code_insee_region": "code_insee_region", "region": "libelle_region", "libelle_region": "libelle_region",
    "date": "date", "heure": "heure", "date_heure": "date_heure",
    "consommation": "consommation",
    "nucleaire": "nucleaire", "thermique": "thermique", "hydraulique": "hydraulique",
    "eolien": "eolien", "solaire": "solaire", "bioenergies": "bioenergies",
}


def sniff_sep(path: Path) -> str:
    head = open(path, encoding="utf-8-sig", errors="replace").readline()
    return ";" if head.count(";") >= head.count(",") else ","


def aggregate_file(path: Path, chunksize: int = 400_000) -> pd.DataFrame:
    """Lecture par morceaux : somme mensuelle par région et compteurs de qualité."""
    sep = sniff_sep(path)
    header = pd.read_csv(path, sep=sep, nrows=0, encoding="utf-8-sig").columns.tolist()
    mapping = {}  # intitulé d'origine vers nom interne (première occurrence gagne)
    for col in header:
        name = ALIASES.get(norm(col))
        if name and name not in mapping.values():
            mapping[col] = name
    print("Colonnes reconnues :", mapping)
    if not mapping:
        raise RuntimeError(f"Aucune colonne reconnue. En-tête du fichier : {header[:40]}")
    parts, dups = [], 0
    seen = np.array([], dtype="uint64")  # empreintes des lignes déjà vues, pour les doublons entre morceaux
    for i, df in enumerate(pd.read_csv(path, sep=sep, usecols=list(mapping), chunksize=chunksize,
                                       low_memory=False, encoding="utf-8-sig")):
        df = df.rename(columns=mapping)
        missing = {"code_insee_region", "libelle_region", "date", "consommation"} - set(df.columns)
        if missing:
            raise RuntimeError(f"Colonnes absentes du CSV : {sorted(missing)}. En-tête du fichier : {header}")
        for s_ in SOURCES:
            if s_ not in df.columns:
                df[s_] = float("nan")
        key = "date_heure" if "date_heure" in df.columns else None
        subset = ["code_insee_region", key] if key else ["code_insee_region", "date", "heure"]
        before = len(df)
        h = pd.util.hash_pandas_object(df[subset].astype(str), index=False).to_numpy()
        keep = ~np.isin(h, seen) & ~pd.Series(h).duplicated().to_numpy()
        df = df[keep]
        seen = np.concatenate([seen, h[keep]])
        dups += before - len(df)
        for s_ in SOURCES + ["consommation"]:
            df[s_] = pd.to_numeric(df[s_], errors="coerce")
        df["month"] = pd.to_datetime(df["date"], errors="coerce").dt.to_period("M").dt.to_timestamp()
        df["n_null"] = df[SOURCES].isna().sum(axis=1)
        df["n_neg"] = (df[SOURCES] < 0).sum(axis=1)
        parts.append(df.groupby(["code_insee_region", "libelle_region", "month"], as_index=False).agg(
            **{f"{s_}_mwh": (s_, "sum") for s_ in SOURCES + ["consommation"]},
            n_rows=("date", "size"), n_null=("n_null", "sum"), n_neg=("n_neg", "sum")))
        print(f"\r  morceau {i + 1}", end="")
    print()
    g = pd.concat(parts, ignore_index=True)
    g = g.groupby(["code_insee_region", "libelle_region", "month"], as_index=False).sum()
    for s_ in SOURCES + ["consommation"]:
        g[f"{s_}_mwh"] = g[f"{s_}_mwh"] * STEP_HOURS  # MW moyens sur 30 min vers MWh
    g["n_dup"] = 0
    g.loc[g.index[0], "n_dup"] = dups
    return g.rename(columns={"code_insee_region": "region_code", "libelle_region": "region"})


def download_geojson():
    target = ROOT / "data" / "regions.geojson"
    if target.exists():
        return
    try:
        r = requests.get(GEOJSON_URL, timeout=60)
        r.raise_for_status()
        target.write_bytes(r.content)
    except Exception as e:  # la carte bascule sur des bulles sans GeoJSON
        print("GeoJSON indisponible, carte en bulles :", e)


def main():
    (ROOT / "data").mkdir(exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        make_demo(str(ROOT / "seeds.json")).to_csv(OUT, index=False)
        print("Jeu de démo écrit dans", OUT)
        return
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else fetch_raw()
    out = aggregate_file(path)
    out["region_code"] = out["region_code"].astype(str)
    unknown = sorted(set(out["region"]) - set(REGIONS))
    if unknown:
        print("Régions ignorées (absentes du dictionnaire) :", unknown)
    out = out[out["region"].isin(REGIONS)]
    out.to_csv(OUT, index=False)
    print(len(out), "lignes mensuelles écrites dans", OUT, "de", out["month"].min(), "à", out["month"].max())
    download_geojson()


if __name__ == "__main__":
    main()
