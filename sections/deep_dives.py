import streamlit as st

from utils import prep, viz
from utils.constants import SOURCES, SOURCE_LABELS
from utils.io import load_geojson

METRICS = {
    "Part bas carbone (%)": "low_carbon_share",
    "Taux de couverture production / consommation (%)": "coverage",
    "Part éolien + solaire (%)": "wind_solar_share",
    "Part nucléaire (%)": "nuclear_share",
    "Part thermique fossile (%)": "fossil_share",
}


def render(df, y0, y1, metric_label):
    st.header("3. Analyses approfondies : comparer les régions")
    metric = METRICS[metric_label]
    reg_last = prep.aggregate(df[df["year"] == y1], ["region", "region_code"])

    best = reg_last.sort_values(metric, ascending=False).iloc[0]
    worst = reg_last.sort_values(metric, ascending=True).iloc[0]
    st.markdown(f"**À retenir :** en {y1}, pour « {metric_label} », l'écart va de **{worst[metric]:.0f}** "
                f"({worst['region']}) à **{best[metric]:.0f}** ({best['region']}).")

    t_map, t_rank, t_trend, t_whatif = st.tabs(["Carte", "Classement", "Tendances par région", "Et si ? (scénario)"])

    with t_map:
        st.plotly_chart(viz.map_chart(reg_last, metric, load_geojson(), metric_label, f"{metric_label}, {y1}"),
                        width="stretch")
        st.caption("Texte alternatif : carte de France des régions colorées selon l'indicateur choisi.")

    with t_rank:
        st.plotly_chart(viz.bar_chart(reg_last, metric, "region", title=f"Classement, {y1}",
                                      x_label=metric_label, y_label="", color=metric),
                        width="stretch")
        st.caption("Texte alternatif : barres horizontales classant les régions selon l'indicateur.")
        if metric == "coverage":
            st.info("Au-dessus de 100 %, la région produit plus qu'elle ne consomme (exportatrice nette). "
                    "Cet indicateur ignore les échanges physiques, il décrit la capacité de production.")

    with t_trend:
        by_ry = prep.aggregate(df, ["region", "year"])
        st.plotly_chart(
            viz.small_multiples(by_ry, "year", metric, "region", title=f"{metric_label} par région",
                                y_label=metric_label), width="stretch")
        st.caption("Texte alternatif : une petite courbe par région, avec la même échelle verticale.")

    with t_whatif:
        st.markdown("**Hypothèse documentée** : on multiplie la production éolienne et solaire de "
                    f"{y1} par un facteur, la consommation et les autres filières restent inchangées. "
                    "Le surplus supposé remplace d'abord le thermique fossile. Ce n'est pas une prévision.")
        factor = st.slider("Multiplier l'éolien + solaire par", 1.0, 4.0, 1.5, 0.1,
                           help="1,0 = situation actuelle.")
        d = reg_last.copy()
        extra = d["wind_solar_mwh"] * (factor - 1)
        replaced = extra.where(extra < d["thermique_mwh"], d["thermique_mwh"])
        d["new_low"] = 100 * (d["low_carbon_mwh"] + extra) / (d["production_mwh"] + extra - replaced)
        d["gain"] = d["new_low"] - d["low_carbon_share"]
        c1, c2 = st.columns(2)
        c1.metric("Part bas carbone (zone)", f"{100*(d['low_carbon_mwh'].sum()+extra.sum())/(d['production_mwh'].sum()+extra.sum()-replaced.sum()):.1f} %",
                  f"{(100*(d['low_carbon_mwh'].sum()+extra.sum())/(d['production_mwh'].sum()+extra.sum()-replaced.sum())) - 100*d['low_carbon_mwh'].sum()/d['production_mwh'].sum():+.1f} pts")
        c2.metric("Thermique fossile évité", f"{replaced.sum()/1e6:.2f} TWh")
        st.plotly_chart(viz.bar_chart(d, "gain", "region", title="Gain de part bas carbone par région (points)",
                                      x_label="Gain (points de pourcentage)", y_label="", color="gain", text_fmt=".1f"),
                        width="stretch")
