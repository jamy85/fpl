"""Weekly award logic. Pure functions - inputs are plain dicts, no I/O."""


def member_gw_stats(
    name: str, picks: dict, live_points: dict[int, int], player_names: dict[int, str]
) -> dict:
    """Distill one manager's gameweek from their picks + the GW's live points.

    live_points maps element id -> raw (unmultiplied) GW points.
    """
    entry_hist = picks["entry_history"]
    squad = picks["picks"]
    captain = next(p for p in squad if p["is_captain"])
    bench = [p for p in squad if p["multiplier"] == 0]
    raw = lambda p: live_points.get(p["element"], 0)

    best = max(squad, key=raw)
    return {
        "name": name,
        "points": entry_hist["points"],
        "net_points": entry_hist["points"] - entry_hist["event_transfers_cost"],
        "transfers_cost": entry_hist["event_transfers_cost"],
        "bench_points": entry_hist["points_on_bench"],
        "captain_name": player_names.get(captain["element"], "?"),
        "captain_raw": raw(captain),
        "best_pick_name": player_names.get(best["element"], "?"),
        "best_pick_raw": raw(best),
        "captain_missed_by": raw(best) - raw(captain),
        "chip": picks.get("active_chip"),
    }


def _leaders(members: list[dict], key, reverse: bool = True) -> tuple[list[dict], object]:
    ranked = sorted(members, key=key, reverse=reverse)
    top_val = key(ranked[0])
    return [m for m in ranked if key(m) == top_val], top_val


def _names(winners: list[dict]) -> str:
    return " & ".join(m["name"] for m in winners)


def gameweek_awards(members: list[dict]) -> list[dict]:
    """The banter board for one finished GW. members = member_gw_stats() dicts."""
    if not members:
        return []
    awards = []

    champs, pts = _leaders(members, lambda m: m["net_points"])
    awards.append(
        {
            "award": "🏆 Gameweek Champion",
            "winner": _names(champs),
            "detail": f"{pts} points (after hits) — everyone else, take notes.",
        }
    )

    spoons, pts = _leaders(members, lambda m: m["net_points"], reverse=False)
    awards.append(
        {
            "award": "🥄 Wooden Spoon",
            "winner": _names(spoons),
            "detail": f"{pts} points. The bar was on the floor and they brought a shovel.",
        }
    )

    caps, pts = _leaders(members, lambda m: m["captain_raw"])
    awards.append(
        {
            "award": "©️ Captain Fantastic",
            "winner": _names(caps),
            "detail": f"{caps[0]['captain_name']} returned {pts} raw points with the armband.",
        }
    )

    flops, missed = _leaders(members, lambda m: m["captain_missed_by"])
    if missed > 0:
        awards.append(
            {
                "award": "🤡 Captain Calamity",
                "winner": _names(flops),
                "detail": (
                    f"Captained {flops[0]['captain_name']} ({flops[0]['captain_raw']} pts) while "
                    f"{flops[0]['best_pick_name']} ({flops[0]['best_pick_raw']} pts) watched from the same squad. "
                    f"{missed} points left on the armband."
                ),
            }
        )

    benched, pts = _leaders(members, lambda m: m["bench_points"])
    if pts > 0:
        awards.append(
            {
                "award": "🪑 Bench Blunder",
                "winner": _names(benched),
                "detail": f"{pts} points sat on the bench doing absolutely nothing for the cause.",
            }
        )

    hitters, cost = _leaders(members, lambda m: m["transfers_cost"])
    if cost > 0:
        awards.append(
            {
                "award": "💸 Hit Merchant",
                "winner": _names(hitters),
                "detail": f"Took -{cost} in transfer hits. Bold. Expensive. Probably regrettable.",
            }
        )

    return awards
