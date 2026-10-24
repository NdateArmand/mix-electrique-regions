"""Constantes partagées : sources d'énergie, groupes, libellés et centroïdes des régions."""

SOURCES = ["nucleaire", "thermique", "hydraulique", "eolien", "solaire", "bioenergies"]
LOW_CARBON = ["nucleaire", "hydraulique", "eolien", "solaire", "bioenergies"]
RENEWABLE = ["hydraulique", "eolien", "solaire", "bioenergies"]
WIND_SOLAR = ["eolien", "solaire"]

SOURCE_LABELS = {
    "nucleaire": "Nucléaire",
    "thermique": "Thermique fossile",
    "hydraulique": "Hydraulique",
    "eolien": "Éolien",
    "solaire": "Solaire",
    "bioenergies": "Bioénergies",
}

# Palette lisible (contrastes suffisants sur fond blanc)
SOURCE_COLORS = {
    "nucleaire": "#6a3d9a",
    "thermique": "#4d4d4d",
    "hydraulique": "#1f78b4",
    "eolien": "#33a02c",
    "solaire": "#ff7f00",
    "bioenergies": "#8c6d31",
}

# Pas de temps des données éCO2mix régionales : 30 minutes
STEP_HOURS = 0.5

# Nom éCO2mix : (code INSEE, latitude, longitude du centre approximatif)
REGIONS = {
    "Auvergne-Rhône-Alpes": ("84", 45.45, 4.60),
    "Bourgogne-Franche-Comté": ("27", 47.25, 4.80),
    "Bretagne": ("53", 48.20, -2.90),
    "Centre-Val de Loire": ("24", 47.50, 1.70),
    "Grand Est": ("44", 48.65, 6.00),
    "Hauts-de-France": ("32", 50.05, 2.80),
    "Normandie": ("28", 49.10, 0.30),
    "Nouvelle-Aquitaine": ("75", 45.20, 0.30),
    "Occitanie": ("76", 43.70, 2.10),
    "Pays de la Loire": ("52", 47.45, -0.80),
    "Provence-Alpes-Côte d'Azur": ("93", 43.95, 6.00),
    "Île-de-France": ("11", 48.70, 2.50),
}

GEOJSON_URL = (
    "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/"
    "regions-version-simplifiee.geojson"
)
