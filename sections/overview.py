import streamlit as st

from utils import prep, viz
from utils.constants import SOURCES


def render(df, df_year, y0, y1):
    st.header("2. Vue d'ensemble : un mix qui évolue")
    tot = prep.aggregate(df, ["year"])
    first, last = tot[tot["year"] == y0].iloc[0], tot[tot["year"] == y1].iloc[0]

    st.markdown(f"**À retenir :** pour les régions sélectionnées, la part bas carbone est de "
                f"**{last['low_carbon_share']:.1f} %** en {y1}, contre {first['low_carbon_share']:.1f} % en {y0}.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Production {y1}", f"{last['production_mwh']/1e6:,.0f} TWh".replace(",", " "),
              f"{(last['production_mwh']/first['production_mwh']-1)*100:+.1f} % vs {y0}" if y1 != y0 else None,
              help="Somme des filières, régions sélectionnées.")
    c2.metric("Part bas carbone", f"{last['low_carbon_share']:.1f} %",
              f"{last['low_carbon_share']-first['low_carbon_share']:+.1f} pts" if y1 != y0 else None,
              help="Nucléaire + hydraulique + éolien + solaire + bioénergies, sur la production totale.")
    c3.metric("Part éolien + solaire", f"{last['wind_solar_share']:.1f} %",
              f"{last['wind_solar_share']-first['wind_solar_share']:+.1f} pts" if y1 != y0 else None)
    c4.metric("Taux de couverture", f"{last['coverage']:.0f} %",
              help="Production / consommation de la zone. Au-dessus de 100 %, la zone exporte en net.")

    left, right = st.columns([3, 2])
    with left:
        st.plotly_chart(viz.stacked_mix(tot, "Production annuelle par filière"), width="stretch")
        st.caption("Texte alternatif : aires empilées de la production annuelle en TWh par filière, "
                   "dominée par le nucléaire, avec un éolien et un solaire en croissance.")
    with right:
        st.plotly_chart(
            viz.line_chart(tot, "year", ["low_carbon_share", "wind_solar_share"],
                           title="Parts bas carbone et éolien + solaire", y_label="Part de la production (%)",
                           series_names={"low_carbon_share": "Part bas carbone", "wind_solar_share": "Part éolien + solaire"}),
            width="stretch")
        st.caption("Texte alternatif : deux courbes annuelles en pourcentage de la production.")
