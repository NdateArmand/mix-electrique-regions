# Le mix électrique des régions françaises

Projet individuel de data storytelling avec Streamlit, cours Data Visualization (EFREI Paris),
projet proposé par le Prof. Mano Joseph Mathew.

## Question
Comment le mix électrique des régions françaises a-t-il évolué depuis 2013, et qu'est-ce qui
différencie les régions ? L'application suit un fil simple : pourquoi ce sujet, l'évolution dans le
temps, la comparaison des régions, la qualité des données, puis ce qu'on retient.

## Données
- Jeu de données : [éCO2mix régional consolidé et définitif](https://www.data.gouv.fr/datasets/donnees-eco2mix-regionales-consolidees-et-definitives), RTE, via data.gouv.fr.
- Licence : Licence Ouverte 2.0 (Etalab).
- Contenu : consommation et production par filière (nucléaire, thermique, hydraulique, éolien, solaire, bioénergies), par région, toutes les 30 minutes.
- Fonds de carte : contours simplifiés des régions de France (dépôt gregoiredavid/france-geojson).

## Ce que fait le traitement
Le script `scripts/download_data.py` :
1. télécharge le CSV de data.gouv (plusieurs centaines de Mo, mis en cache dans `data/raw/`) ;
2. le lit par morceaux, supprime les doublons et compte les valeurs vides et négatives ;
3. convertit les puissances (MW, pas de 30 minutes) en énergie (MWh) ;
4. agrège par région et par mois dans `data/monthly.csv`, la seule table utilisée par l'app.

L'application ignore les années incomplètes (2026 s'arrête en août). Les ratios (part bas carbone,
part éolien + solaire, taux de couverture) sont toujours recalculés à partir des sommes.

## Contenu de l'application
- Barre latérale : régions, période, indicateur (part bas carbone, part éolien + solaire, taux de couverture).
- Trois chiffres clés liés aux filtres.
- Trois visuels interactifs : courbe d'évolution, classement des régions, carte.
- Une section qualité des données.

## Lancer le projet
```
pip install -r requirements.txt
python scripts/download_data.py
streamlit run app.py
```
Si le téléchargement automatique échoue, télécharger le CSV depuis la page du jeu de données puis
lancer `python scripts/download_data.py chemin/du/fichier.csv`.

## Fichiers
```
app.py                       application Streamlit
utils/identity.py            bloc d'identification de la barre latérale
utils/constants.py, demo.py  utilisés par le script de téléchargement
scripts/download_data.py     téléchargement, nettoyage, agrégation
data/monthly.csv             table mensuelle par région
data/regions.geojson         contours des régions
assets/efrei_logo.png        logo
requirements.txt             dépendances
app_complet.py               version plus riche (scénario, petits graphiques), non utilisée dans le rendu
```

## Limites
- Les valeurs vides sont comptées comme 0. C'est correct pour une filière absente d'une région
  (pas de nucléaire en Bretagne), mais cela peut cacher un manque de mesure.
- La production ne tient pas compte des échanges entre régions ni du pompage : le taux de
  couverture décrit une capacité de production, pas une autonomie réelle.
- Les données récentes sont consolidées, pas toujours définitives.
- Les valeurs négatives sont laissées telles quelles.
- Aucune causalité n'est établie, l'analyse reste descriptive.

## Pistes de suite
Ajouter les échanges physiques entre régions, l'intensité carbone et les prix de l'électricité.
