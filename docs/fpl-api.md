# FPL API reference (probed live 2026-08-19)

Base: `https://fantasy.premierleague.com/api/` — public, **no auth** for everything below.
Plain `curl` works from this machine. Space requests out (corporate IPS resets bursts).
JSON throughout. IDs are stable within a season only (player `code` is stable across seasons).

## Season context at probe time
- 2026/27 season, **GW1 deadline 2026-08-21T17:30Z** — nothing played yet, so all
  "current season" arrays were empty but every endpoint's shape was confirmed.
- ~5.97M registered managers; 592 players (`elements`); 380 fixtures.

## Endpoints (all verified 200)

### `bootstrap-static/` (~1.5 MB) — the master blob, fetch once & cache
- `events` [38]: gameweeks — deadlines, `is_current`/`is_next`, `finished`, and once played:
  `average_entry_score`, `highest_score`, `most_captained`, `most_transferred_in`, `top_element`, `chip_plays`.
- `elements` [592]: players, **109 fields each** — price (`now_cost`, tenths of £M), `selected_by_percent`,
  `form`, `total_points`, `event_points`, per-season stats (goals, assists, CS, minutes, bonus, BPS),
  xG/xA/xGI/xGC, ICT index, `status` (a=available/i=injured/s=suspended/u=unavailable) + `news` text,
  transfers in/out, price-change projections, `chance_of_playing_next_round`, `photo` code.
- `teams` [20]: names, short names, strength ratings (home/away, attack/defence).
- `element_types` [4]: GKP/DEF/MID/FWD squad rules.
- `chips` [8]: wildcard ×2, plus others, with valid GW windows.
- `game_config.scoring`: full scoring rules.
- Player photos: `https://resources.premierleague.com/premierleague/photos/players/110x140/p{photo_code}.png` (element `code`).

### `fixtures/` — all 380 fixtures
`event` (GW), `kickoff_time`, teams, scores, `team_h_difficulty`/`team_a_difficulty` (FDR 1-5),
`stats` (goals/assists/cards/bonus/BPS per fixture once played). `?event=N` filters one GW.

### `element-summary/{player_id}/` — one player deep-dive
- `fixtures`: their remaining fixtures with difficulty.
- `history`: per-GW rows this season (points, minutes, xG…, opponent, price at the time).
- `history_past`: **past seasons** totals (5 seasons for established players).

### `event/{gw}/live/` — live per-player points during a GW
`elements[].stats` (points, bonus, BPS, minutes…) + `explain` (points breakdown). Empty pre-season.

### `entry/{manager_id}/` — public manager profile
Team name, manager name, region, `favourite_team`, `years_active`, overall points/rank,
`leagues.classic` (all their mini-leagues with ranks), `last_deadline_value`/`bank`.

### `entry/{manager_id}/history/`
- `current`: per-GW rows (points, total, overall rank, GW rank, bank, team value, transfers, points on bench).
- `past`: every past season (season_name, total_points, rank) — entry 1 goes back to 2014/15.
- `chips`: which chip played in which GW.

### `entry/{manager_id}/event/{gw}/picks/`
The 15 picks (element id, position 1-15, `is_captain`/`is_vice_captain`, multiplier),
`active_chip`, `automatic_subs`, `entry_history` for that GW. **404 until the entry has a team
for a played/current GW** (pre-season it 404s — not an error in our code).

### `entry/{manager_id}/transfers/` — full transfer history (in/out, prices, GW).

### `leagues-classic/{league_id}/standings/` — mini-league table
`league` meta + `standings.results` (entry id, player_name, entry team name, rank, last_rank,
event_total, total). Paged via `?page_standings=N`, `has_next`. League id 314 = overall.
H2H variant: `leagues-h2h/{id}/standings/`.

### `event-status/` — bonus-added / league-update status per GW day.

### Requires login cookie (not probed, needs auth): `my-team/{id}/`, current-GW picks before deadline, `me/`.

## Gotchas
- Prices are integers in tenths (`now_cost: 60` = £6.0M). Many numeric stats arrive as **strings** ("4.4").
- `dream-team/{gw}/` 404s until the GW is played.
- Mini-league standings only populate after GW1; before that `results` is `[]`.
- No CORS for browser calls from other origins — a shared web app needs a tiny server-side proxy/cache
  (also polite: cache bootstrap-static, don't refetch per user).
