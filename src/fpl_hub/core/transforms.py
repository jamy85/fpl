"""Pure reshaping of raw FPL payloads into frames/lookups. No I/O, no Streamlit."""

import pandas as pd

STATUS_LABELS = {
    "a": "",
    "d": "Doubtful",
    "i": "Injured",
    "s": "Suspended",
    "u": "Unavailable",
    "n": "Not eligible",
}


def team_lookup(boot: dict) -> dict[int, dict]:
    return {t["id"]: t for t in boot["teams"]}


def position_lookup(boot: dict) -> dict[int, str]:
    return {et["id"]: et["singular_name_short"] for et in boot["element_types"]}


def finished_events(boot: dict) -> list[dict]:
    return [e for e in boot["events"] if e["finished"]]


def current_event_id(boot: dict) -> int | None:
    """The in-progress or most recently started GW; None pre-season."""
    cur = [e["id"] for e in boot["events"] if e["is_current"]]
    return cur[0] if cur else None


def next_event(boot: dict) -> dict | None:
    nxt = [e for e in boot["events"] if e["is_next"]]
    return nxt[0] if nxt else None


def season_started(boot: dict) -> bool:
    return current_event_id(boot) is not None or bool(finished_events(boot))


def players_frame(boot: dict) -> pd.DataFrame:
    """One row per player with display-ready columns.

    Before any GW is played, the cumulative stat fields on elements still hold
    LAST season's values - callers should label them accordingly
    (see season_started()).
    """
    teams = team_lookup(boot)
    positions = position_lookup(boot)
    rows = []
    for el in boot["elements"]:
        rows.append(
            {
                "id": el["id"],
                "Player": el["web_name"],
                "Team": teams[el["team"]]["short_name"],
                "Pos": positions[el["element_type"]],
                "Price": el["now_cost"] / 10,
                "Selected %": float(el["selected_by_percent"]),
                "Points": el["total_points"],
                "PPG": float(el["points_per_game"]),
                "Form": float(el["form"]),
                "Minutes": el["minutes"],
                "Goals": el["goals_scored"],
                "Assists": el["assists"],
                "xGI": float(el.get("expected_goal_involvements", 0) or 0),
                "Availability": STATUS_LABELS.get(el["status"], el["status"]),
                "News": el["news"] or "",
                "team_id": el["team"],
            }
        )
    return pd.DataFrame(rows)


def fixture_grid(
    fixture_list: list[dict], boot: dict, from_event: int, horizon: int
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(difficulty, opponent-label) frames: one row per team, one col per GW.

    Difficulty is the FDR 1-5 from the team's perspective; NaN for a blank GW.
    Double GWs keep the harder fixture's rating and join labels with ' + '.
    """
    teams = team_lookup(boot)
    gws = list(range(from_event, min(from_event + horizon, 39)))
    names = [teams[tid]["short_name"] for tid in sorted(teams)]
    diff = pd.DataFrame(index=names, columns=[f"GW{g}" for g in gws], dtype=float)
    opp = pd.DataFrame("", index=names, columns=[f"GW{g}" for g in gws])

    for fx in fixture_list:
        if fx["event"] not in gws:
            continue
        col = f"GW{fx['event']}"
        for me, them, fdr, suffix in (
            (fx["team_h"], fx["team_a"], fx["team_h_difficulty"], "(H)"),
            (fx["team_a"], fx["team_h"], fx["team_a_difficulty"], "(A)"),
        ):
            row = teams[me]["short_name"]
            label = f"{teams[them]['short_name']} {suffix}"
            prev = diff.at[row, col]
            diff.at[row, col] = fdr if pd.isna(prev) else max(prev, fdr)
            opp.at[row, col] = label if not opp.at[row, col] else f"{opp.at[row, col]} + {label}"
    return diff, opp
