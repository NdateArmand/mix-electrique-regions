"""Bloc d'identification affiché dans la barre latérale (à gauche) : logo, étudiant, cours, projet."""
from pathlib import Path

import streamlit as st

# A MODIFIER : remplace les valeurs entre crochets par les tiennes
FULL_NAME = "NDATE TCHEBEBIA ARMAND CLAUDE"
PROGRAM = "Cycle ingénieur, Data Engineering"
YEAR = "M1"
EMAIL = "armand.ndate-tchebebebia@efrei.net"
LINKEDIN = "https://www.linkedin.com/in/armand-ndate"
GITHUB = "https://github.com/NdateArmand"
COURSE = "Data Visualization"
PROJECT_BY = "Projet proposé par : Prof. Mano Joseph Mathew"
PROF_CONTACT = "mano.mathew@efrei.fr"

LOGO = Path(__file__).resolve().parent.parent / "assets" / "efrei_logo.png"


def render_identity():
    with st.sidebar:
        if LOGO.exists():
            st.image(str(LOGO), width=160)
        else:
            st.markdown("### EFREI Paris")
        st.markdown(
            f"**{FULL_NAME}**  \n{PROGRAM}, {YEAR}  \n"
            f"{EMAIL}  \n[LinkedIn]({LINKEDIN}) | [GitHub]({GITHUB})"
        )
        st.markdown(f"**{COURSE}**  \n{PROJECT_BY}  \n{PROF_CONTACT}")
        st.divider()
