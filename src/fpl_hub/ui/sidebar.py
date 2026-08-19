"""Shared sidebar: league-ID input, persisted in the URL query string so a
shared link opens straight onto the right mini-league."""

import streamlit as st


def league_selector() -> None:
    default = st.query_params.get("league", "")
    raw = st.sidebar.text_input(
        "Mini-league ID",
        value=default,
        help="From your league's URL on fantasy.premierleague.com: /leagues/<ID>/standings/c",
    )
    raw = raw.strip()
    if raw.isdigit():
        st.session_state["league_id"] = int(raw)
        st.query_params["league"] = raw
    else:
        st.session_state["league_id"] = None
        if raw:
            st.sidebar.error("League ID should be a number.")
