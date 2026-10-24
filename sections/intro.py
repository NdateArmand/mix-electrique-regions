import streamlit as st

from utils.io import LICENSE_TEXT, SOURCE_URL


def render(is_demo: bool):
    st.header("1. Le problème : d'où vient l'électricité de chaque région ?")
    st.markdown(
        """
**Pourquoi c'est important.** La France produit une électricité très peu carbonée, mais ce résultat
n'est pas uniforme : certaines régions concentrent le nucléaire et exportent, d'autres dépendent
des imports ou du thermique fossile. La transition énergétique se joue donc région par région.

**Audience.** Étudiants, citoyens et décideurs locaux qui veulent comparer leur région aux autres.

**Questions auxquelles l'app répond.**
1. Le mix électrique régional se décarbone-t-il, et à quel rythme ?
2. Quelles régions produisent plus qu'elles ne consomment, et lesquelles dépendent des autres ?
3. Que changerait un développement plus rapide de l'éolien et du solaire ? (scénario simple)
"""
    )
    with st.expander("Données, licence et méthode"):
        st.markdown(
            f"""
- **Source** : [éCO2mix régional consolidé et définitif]({SOURCE_URL}), RTE, pas de 30 minutes.
- **Licence** : {LICENSE_TEXT}
- **Méthode** : les données demi-horaires (MW) sont converties en MWh (x 0,5 h) puis agrégées par
  région et par mois. Les ratios sont toujours recalculés à partir des sommes, jamais moyennés.
- **Production** = nucléaire + thermique fossile + hydraulique + éolien + solaire + bioénergies.
  Les échanges physiques et le pompage ne sont pas inclus.
"""
        )
    if is_demo:
        st.warning(
            "Mode démo : le fichier data/monthly.csv est absent, l'application affiche un jeu de "
            "données SYNTHÉTIQUE pour tester l'interface. Lance `python scripts/download_data.py` "
            "pour récupérer les vraies données."
        )
