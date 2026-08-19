"""Assemble league-level views from per-entry API calls (cached in fpl_api)."""

import pandas as pd

from fpl_hub.awards.compute import member_gw_stats
from fpl_hub.data_access import fpl_api


def members(league_id: int) -> list[dict]:
    """Standings rows: entry, player_name, entry_name, rank, total, event_total."""
    return fpl_api.league_standings(league_id)["standings"]["results"]


def rank_progression(member_rows: list[dict]) -> pd.DataFrame:
    """Long frame (gw, manager, total, league_rank) built from entry histories."""
    rows = []
    for m in member_rows:
        for gw_row in fpl_api.entry_history(m["entry"])["current"]:
            rows.append(
                {
                    "gw": gw_row["event"],
                    "manager": m["player_name"],
                    "gw_points": gw_row["points"] - gw_row["event_transfers_cost"],
                    "total": gw_row["total_points"],
                }
            )
    if not rows:
        return pd.DataFrame(columns=["gw", "manager", "gw_points", "total", "league_rank"])
    df = pd.DataFrame(rows)
    df["league_rank"] = df.groupby("gw")["total"].rank(method="min", ascending=False).astype(int)
    return df


def gw_member_stats(member_rows: list[dict], event_id: int, boot: dict) -> list[dict]:
    """member_gw_stats() for every league member with picks available for the GW."""
    live = fpl_api.event_live(event_id)["elements"]
    live_points = {el["id"]: el["stats"]["total_points"] for el in live}
    player_names = {el["id"]: el["web_name"] for el in boot["elements"]}
    stats = []
    for m in member_rows:
        picks = fpl_api.entry_picks(m["entry"], event_id)
        if picks is None:
            continue
        stats.append(member_gw_stats(m["player_name"], picks, live_points, player_names))
    return stats
