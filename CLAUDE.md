# FPL Mini-League Hub

Streamlit app on the public FPL API for a friends' mini-league. Three features:
League Hub (standings/rivalry), Weekly Awards (banter board), Scout (transfers).

## Project layout
- `streamlit_app.py` — entrypoint (`streamlit run streamlit_app.py`); package installed editable.
- `src/fpl_hub/` — `config.py`; `data_access/fpl_api.py` (all API calls, st.cache_data);
  `core/transforms.py` (pure reshaping, no I/O); `league/`, `awards/`, `scout/` (feature
  pages, each with `page.py:render()`); `ui/` (theme = validated dataviz palette, sidebar).
- `tests/` mirrors the package (pure functions only). `docs/fpl-api.md` = probed endpoint map.

## Constraints
- **FPL API**: no auth, no CORS (server-side fetch only). Take endpoint facts from
  `docs/fpl-api.md`, not general knowledge; prices are tenths of £M; many numerics arrive
  as strings; `entry/{id}/event/{gw}/picks/` 404s until the GW deadline — treated as None.
- Pre-season (until GW1, 2026-08-21): bootstrap element stats hold LAST season's values;
  standings/live/picks are empty. Every page must render a sensible empty state.
- Interpreter: `.venv\Scripts\python.exe` (isolated venv, Python 3.13). No `python` on PATH.
- All league members' detail = 1 request per manager per view — capped
  (`config.MAX_LEAGUE_ENTRIES`) and cached; keep `REQUEST_SPACING_S` (corporate IPS).
- Charts follow the dataviz-skill palette in `ui/theme.py`; scatter/all-pairs forms cap at
  3 categorical hues (facet instead); rank lines cap at 8, rest grey.

## Project log
Dated progress → `project-log.md`.
