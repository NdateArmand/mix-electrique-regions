import json

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.identity import render_identity

st.set_page_config(page_title="Mix électrique des régions", layout="wide")

BAS_CARBONE = ["nucleaire", "hydraulique", "eolien", "solaire", "bioenergies"]
TOUTES = BAS_CARBONE + ["thermique"]


@st.cache_data
def charger():
    df = pd.read_csv("data/monthly.csv", parse_dates=["month"])
    df["annee"] = df["month"].dt.year
    # on garde seulement les années complètes
    nb_mois = df.groupby("annee")["month"].nunique()
    df = df[df["annee"].isin(nb_mois[nb_mois == 12].index)].copy()
    cols = [c + "_mwh" for c in TOUTES]
    df[cols] = df[cols].fillna(0)
    df["production"] = df[cols].sum(axis=1)
    df["bas_carbone"] = df[[c + "_mwh" for c in BAS_CARBONE]].sum(axis=1)
    df["eolien_solaire"] = df["eolien_mwh"] + df["solaire_mwh"]
    return df


def indicateurs(g):
    """g est un tableau déjà sommé (par région ou par année)."""
    g = g.copy()
    g["Part bas carbone (%)"] = 100 * g["bas_carbone"] / g["production"]
    g["Part éolien + solaire (%)"] = 100 * g["eolien_solaire"] / g["production"]
    g["Taux de couverture (%)"] = 100 * g["production"] / g["consommation_mwh"]
    return g


try:
    df = charger()
except FileNotFoundError:
    st.error("data/monthly.csv est introuvable. Lance d'abord : python scripts/download_data.py")
    st.stop()

render_identity()
with st.sidebar:
    st.header("Filtres")
    toutes_regions = sorted(df["region"].unique())
    regions = st.multiselect("Régions", toutes_regions, default=toutes_regions)
    annees = sorted(df["annee"].unique())
    debut, fin = st.select_slider("Période", options=annees, value=(annees[0], annees[-1]))
    indicateur = st.selectbox("Indicateur", ["Part bas carbone (%)", "Part éolien + solaire (%)",
                                             "Taux de couverture (%)"])

if not regions:
    st.warning("Choisis au moins une région.")
    st.stop()

d = df[df["region"].isin(regions) & df["annee"].between(debut, fin)]

st.title("Le mix électrique des régions françaises")
st.caption("Source : éCO2mix régional (RTE), data.gouv.fr, Licence Ouverte 2.0.")

# Contexte
st.header("Pourquoi ce sujet ?")
st.write(
    "L'électricité française est en grande partie bas carbone, mais cette moyenne cache de gros "
    "écarts entre régions. On regarde comment le mix a évolué depuis 2013 et ce qui différencie "
    "les régions."
)

# Chiffres clés (dernière année de la période)
sommes = d.groupby("annee")[["production", "bas_carbone", "eolien_solaire", "consommation_mwh"]].sum()
sommes = indicateurs(sommes).reset_index()
derniere = sommes[sommes["annee"] == fin].iloc[0]
premiere = sommes[sommes["annee"] == debut].iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric(f"Production en {fin}", f"{derniere['production'] / 1e6:.0f} TWh")
c2.metric("Part bas carbone", f"{derniere['Part bas carbone (%)']:.1f} %",
          f"{derniere['Part bas carbone (%)'] - premiere['Part bas carbone (%)']:+.1f} points depuis {debut}")
c3.metric("Taux de couverture", f"{derniere['Taux de couverture (%)']:.0f} %",
          help="Production divisée par consommation. Au-dessus de 100 %, la zone produit plus qu'elle ne consomme.")

# Graphique 1 : évolution
st.header("Une électricité de plus en plus bas carbone")
fig1 = px.line(sommes, x="annee", y=["Part bas carbone (%)", "Part éolien + solaire (%)"], markers=True,
               labels={"annee": "Année", "value": "Part de la production (%)", "variable": ""})
st.plotly_chart(fig1, width="stretch")

# Graphique 2 : classement
st.header("Des régions très différentes")
par_region = indicateurs(d[d["annee"] == fin].groupby(["region", "region_code"])[
    ["production", "bas_carbone", "eolien_solaire", "consommation_mwh"]].sum().reset_index())
fig2 = px.bar(par_region.sort_values(indicateur), x=indicateur, y="region", orientation="h",
              labels={"region": ""}, title=f"{indicateur}, {fin}")
st.plotly_chart(fig2, width="stretch")

# Graphique 3 : carte
with open("data/regions.geojson", encoding="utf-8") as f:
    geo = json.load(f)
fig3 = px.choropleth_map(par_region, geojson=geo, locations="region_code", featureidkey="properties.code",
                         color=indicateur, hover_name="region", map_style="carto-positron",
                         center={"lat": 46.6, "lon": 2.4}, zoom=4.3, opacity=0.8,
                         title=f"{indicateur}, {fin}")
st.plotly_chart(fig3, width="stretch")

# Qualité des données
st.header("Qualité des données")
lignes = int(df["n_rows"].sum())
q1, q2, q3 = st.columns(3)
q1.metric("Lignes brutes traitées", f"{lignes:,}".replace(",", " "))
q2.metric("Doublons supprimés", int(df["n_dup"].sum()))
q3.metric("Valeurs vides (filières)", f"{100 * df['n_null'].sum() / (lignes * 6):.1f} %")
st.write(
    "Les valeurs vides sont comptées comme 0, ce qui est logique pour une filière absente d'une région "
    "(pas de nucléaire en Bretagne) mais peut cacher un manque de mesure. "
    f"Il y a aussi {int(df['n_neg'].sum())} valeurs négatives, laissées telles quelles. "
    "Les années incomplètes (2026) sont exclues."
)

# Conclusion
st.header("Ce qu'on retient")
st.write(
    f"- La part bas carbone passe de {premiere['Part bas carbone (%)']:.1f} % en {debut} à "
    f"{derniere['Part bas carbone (%)']:.1f} % en {fin}.\n"
    "- Les régions qui ont du nucléaire produisent bien plus qu'elles ne consomment, "
    "l'Île-de-France presque pas.\n"
    "- Limite : on ne tient pas compte des échanges d'électricité entre régions. "
    "Une suite possible serait de les ajouter."
)
