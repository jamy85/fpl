"""Settings shared across the app. Endpoint map: docs/fpl-api.md."""

API_BASE = "https://fantasy.premierleague.com/api"

REQUEST_TIMEOUT_S = 20
# Corporate network resets bursty Python HTTPS - keep a gap between live calls.
REQUEST_SPACING_S = 0.3

BOOTSTRAP_TTL_S = 30 * 60
FIXTURES_TTL_S = 30 * 60
LEAGUE_TTL_S = 10 * 60
ENTRY_TTL_S = 10 * 60

# Safety cap: how many league entries we fetch per-manager detail for.
MAX_LEAGUE_ENTRIES = 50

# How many upcoming gameweeks the fixture-difficulty view shows.
FDR_HORIZON_GWS = 6

PLAYER_PHOTO_URL = (
    "https://resources.premierleague.com/premierleague/photos/players/110x140/p{code}.png"
)
