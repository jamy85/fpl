# FPL Mini-League Hub

A Streamlit app for a friends' Fantasy Premier League mini-league:

- **🏆 League Hub** — live standings, rank race chart, everyone's captain & chips.
- **🎭 Weekly Awards** — auto-generated banter board after each gameweek
  (Gameweek Champion, Wooden Spoon, Captain Calamity, Bench Blunder…).
- **🔭 Scout** — player finder with filters, value-vs-price map, fixture-difficulty grid.

Data comes live from the public FPL API (no login required). Enter your
mini-league ID (from `fantasy.premierleague.com/leagues/<ID>/standings/c`) in the
sidebar — it's kept in the URL so a shared link opens straight onto your league.

## Run locally

```
.venv\Scripts\python.exe -m pip install -e .[dev]
.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

## Deploy for friends

Push to GitHub and point [Streamlit Community Cloud](https://share.streamlit.io)
at `streamlit_app.py` — it installs `requirements.txt` (`-e .`) automatically.

## Tests

```
.venv\Scripts\python.exe -m pytest
```
