"""Read-only client for the public FPL API (no auth needed).

Full endpoint map and gotchas: docs/fpl-api.md. All functions return parsed
JSON. Streamlit's cache_data keeps us polite: bootstrap-static is ~1.5 MB and
only refetched every BOOTSTRAP_TTL_S per server process.
"""

import time

import requests
import streamlit as st

from fpl_hub import config

_session = requests.Session()
_session.headers["User-Agent"] = "fpl-hub (private mini-league dashboard)"
_last_call = 0.0


def _get(path: str, params: dict | None = None):
    global _last_call
    wait = config.REQUEST_SPACING_S - (time.monotonic() - _last_call)
    if wait > 0:
        time.sleep(wait)
    resp = _session.get(
        f"{config.API_BASE}/{path}", params=params, timeout=config.REQUEST_TIMEOUT_S
    )
    _last_call = time.monotonic()
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=config.BOOTSTRAP_TTL_S, show_spinner="Fetching FPL game data…")
def bootstrap() -> dict:
    """Master blob: events (GWs), teams, elements (players), rules."""
    return _get("bootstrap-static/")


@st.cache_data(ttl=config.FIXTURES_TTL_S, show_spinner="Fetching fixtures…")
def fixtures() -> list[dict]:
    return _get("fixtures/")


@st.cache_data(ttl=config.LEAGUE_TTL_S, show_spinner="Fetching league standings…")
def league_standings(league_id: int) -> dict:
    """Classic mini-league: league meta + paged standings, all pages merged."""
    first = _get(f"leagues-classic/{league_id}/standings/")
    results = first["standings"]["results"]
    page = 1
    while first["standings"]["has_next"] and len(results) < config.MAX_LEAGUE_ENTRIES:
        page += 1
        first["standings"] = _get(
            f"leagues-classic/{league_id}/standings/", params={"page_standings": page}
        )["standings"]
        results.extend(first["standings"]["results"])
    first["standings"]["results"] = results[: config.MAX_LEAGUE_ENTRIES]
    return first


@st.cache_data(ttl=config.ENTRY_TTL_S)
def entry(entry_id: int) -> dict:
    """Public manager profile (team name, region, leagues, overall rank)."""
    return _get(f"entry/{entry_id}/")


@st.cache_data(ttl=config.ENTRY_TTL_S)
def entry_history(entry_id: int) -> dict:
    """Per-GW rows this season + past-season totals + chips played."""
    return _get(f"entry/{entry_id}/history/")


@st.cache_data(ttl=config.ENTRY_TTL_S)
def entry_picks(entry_id: int, event_id: int) -> dict | None:
    """The 15 picks for one GW. None if not available yet (404 pre-deadline)."""
    try:
        return _get(f"entry/{entry_id}/event/{event_id}/picks/")
    except requests.HTTPError as err:
        if err.response is not None and err.response.status_code == 404:
            return None
        raise


@st.cache_data(ttl=config.LEAGUE_TTL_S)
def event_live(event_id: int) -> dict:
    """Per-player points for one GW (empty 'elements' before kickoff)."""
    return _get(f"event/{event_id}/live/")


@st.cache_data(ttl=config.ENTRY_TTL_S)
def element_summary(element_id: int) -> dict:
    """One player: remaining fixtures, per-GW history, past seasons."""
    return _get(f"element-summary/{element_id}/")
