# Le mix électrique des régions françaises : dashboard de data storytelling

Application Streamlit (projet individuel EFREI, #EFREIDataStories2026).

## Histoire racontée
Accroche, contexte, enseignements, suites : l'électricité française est très peu carbonée, mais les
régions sont très différentes. L'app compare la part bas carbone, le taux de couverture
(production / consommation), la part éolien + solaire, et propose un scénario simple.

## Données
- **Source** : [Données éCO2mix régionales consolidées et définitives](https://www.data.gouv.fr/datasets/donnees-eco2mix-regionales-consolidees-et-definitives), RTE via Open Data Réseaux Énergies.
- **Licence** : Licence Ouverte 2.0 (Etalab). Pas de temps de 30 minutes, converti en MWh puis agrégé par région et par mois.
- Les fichiers bruts ne sont pas versionnés : un script les télécharge et les met en cache.

## Installation et lancement
```
pip install -r requirements.txt
python scripts/download_data.py
streamlit run app.py
```
Sans réseau, `python scripts/download_data.py demo` crée un jeu SYNTHÉTIQUE (graine dans `seeds.json`)
pour tester l'interface. Sans `data/monthly.csv`, l'app bascule seule en mode démo et l'affiche clairement.
Équivalent avec `make install`, `make data`, `make run`.

## Structure
```
app.py                 point d'entrée, filtres, cache
sections/              intro, overview, deep_dives, conclusions
utils/                 io (chargement), prep (nettoyage, indicateurs), viz (graphiques), constants, demo
scripts/download_data.py   téléchargement, cache, contrôles qualité, agrégation mensuelle
data/                  monthly.csv, regions.geojson (générés)
```

## Choix techniques
- `st.cache_data` sur le chargement et la préparation, agrégation mensuelle en amont (quelques milliers de lignes).
- Ratios recalculés depuis les sommes, jamais moyennés.
- Qualité : doublons, valeurs vides, valeurs négatives et complétude calculés pendant l'agrégation.
- Accessibilité : axes et unités étiquetés, palette contrastée, descriptions textuelles sous chaque graphique.

## Limites
Valeurs vides traitées comme 0, échanges et pompage ignorés, années récentes parfois seulement consolidées,
scénario de sensibilité sans valeur prédictive.

## Points à finaliser avant rendu
URL de déploiement (Streamlit Community Cloud), vidéo de démo de 2 à 4 minutes, storyboard, archive
`StApp26_<numero>_NOM_DE1.zip` (adapter au groupe).
