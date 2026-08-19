"""Entrypoint: streamlit run streamlit_app.py (fpl_hub installed via `pip install -e .`)."""

import streamlit as st

from fpl_hub.awards.page import render as awards_page
from fpl_hub.league.page import render as league_page
from fpl_hub.scout.page import render as scout_page
from fpl_hub.ui.sidebar import league_selector

st.set_page_config(page_title="FPL Mini-League Hub", page_icon="⚽", layout="wide")

league_selector()

st.navigation(
    [
        st.Page(league_page, title="League Hub", icon="🏆", url_path="league", default=True),
        st.Page(awards_page, title="Weekly Awards", icon="🎭", url_path="awards"),
        st.Page(scout_page, title="Scout", icon="🔭", url_path="scout"),
    ]
).run()
