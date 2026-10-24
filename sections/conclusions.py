import streamlit as st

from utils import prep


def render(df, df_all, y0, y1):
    st.header("4. Qualité des données et limites")
    q = prep.quality_report(df_all)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lignes brutes agrégées", f"{q['rows_raw']:,}".replace(",", " "))
    c2.metric("Doublons supprimés", f"{q['dup_rows']:,}".replace(",", " "))
    c3.metric("Cellules vides (filières)", f"{q['null_pct']:.2f} %")
    c4.metric("Valeurs négatives", f"{q['neg_cells']:,}".replace(",", " "))

    comp = prep.completeness_by_region_year(df_all)
    pivot = comp.pivot(index="region", columns="year", values="completeness_pct").round(1)
    st.markdown("**Complétude** : part des demi-heures présentes par région et par année (100 = complet).")
    st.dataframe(pivot, width="stretch")
    st.markdown(
        """
**Validations appliquées** : types, doublons région et mois, valeurs vides remplacées par 0 pour les
filières absentes d'une région (par exemple le nucléaire en Bretagne), contrôle de complétude.

**Limites** :
- Les valeurs vides sont traitées comme une production nulle, ce qui est exact pour une filière absente
  mais masque d'éventuels trous de mesure.
- La production ne tient pas compte des échanges ni du pompage, le taux de couverture n'est donc pas
  une mesure d'autonomie réelle.
- Les années récentes sont consolidées, pas toujours définitives.
- Le scénario est un exercice de sensibilité, pas une prévision, et aucune causalité n'est établie.
"""
    )

    st.header("5. Enseignements et suites")
    tot = prep.aggregate(df, ["year"])
    a, b = tot[tot["year"] == y0].iloc[0], tot[tot["year"] == y1].iloc[0]
    st.success(
        f"**Enseignements.** (1) La part éolien + solaire passe de {a['wind_solar_share']:.1f} % à "
        f"{b['wind_solar_share']:.1f} % entre {y0} et {y1}. (2) Les écarts entre régions restent très "
        "marqués, surtout à cause de la localisation du nucléaire et de l'hydraulique. (3) Le scénario "
        "montre l'effet limité de l'éolien et du solaire dans les régions déjà très bas carbone, et "
        "plus fort là où le thermique pèse."
    )
    st.markdown("**Suites possibles** : ajouter les échanges entre régions, l'intensité carbone horaire, "
                "et les prix de l'électricité pour relier mix et coûts.")
