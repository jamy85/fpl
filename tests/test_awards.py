from fpl_hub.awards.compute import gameweek_awards, member_gw_stats

LIVE = {1: 12, 2: 2, 3: 8, 4: 15}
NAMES = {1: "Haaland", 2: "Flopson", 3: "Saka", 4: "Salah"}


def picks_for(captain: int, squad: list[int], bench: list[int], points: int, cost: int = 0, bench_pts: int = 0):
    return {
        "active_chip": None,
        "entry_history": {"points": points, "event_transfers_cost": cost, "points_on_bench": bench_pts},
        "picks": (
            [{"element": e, "multiplier": 2 if e == captain else 1, "is_captain": e == captain} for e in squad]
            + [{"element": e, "multiplier": 0, "is_captain": False} for e in bench]
        ),
    }


def test_member_gw_stats_captain_gap():
    stats = member_gw_stats("Alice", picks_for(2, [1, 2, 3], [4], points=40), LIVE, NAMES)
    assert stats["captain_name"] == "Flopson"
    assert stats["captain_raw"] == 2
    # Best pick includes the bench (Salah, 15) - the pain is real.
    assert stats["best_pick_name"] == "Salah"
    assert stats["captain_missed_by"] == 13


def test_gameweek_awards():
    members = [
        member_gw_stats("Alice", picks_for(2, [1, 2, 3], [], points=40, cost=8), LIVE, NAMES),
        member_gw_stats("Bob", picks_for(1, [1, 2, 3], [], points=60, bench_pts=6), LIVE, NAMES),
    ]
    awards = {a["award"]: a for a in gameweek_awards(members)}
    assert awards["🏆 Gameweek Champion"]["winner"] == "Bob"
    assert awards["🥄 Wooden Spoon"]["winner"] == "Alice"
    assert awards["©️ Captain Fantastic"]["winner"] == "Bob"
    assert awards["🤡 Captain Calamity"]["winner"] == "Alice"
    assert awards["💸 Hit Merchant"]["winner"] == "Alice"
    assert awards["🪑 Bench Blunder"]["winner"] == "Bob"
