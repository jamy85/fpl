from fpl_hub.core import transforms

BOOT = {
    "events": [
        {"id": 1, "finished": True, "is_current": False, "is_next": False},
        {"id": 2, "finished": False, "is_current": True, "is_next": False},
        {"id": 3, "finished": False, "is_current": False, "is_next": True},
    ],
    "teams": [
        {"id": 1, "short_name": "ARS"},
        {"id": 2, "short_name": "CHE"},
    ],
    "element_types": [{"id": 3, "singular_name_short": "MID"}],
    "elements": [
        {
            "id": 10,
            "web_name": "Saka",
            "team": 1,
            "element_type": 3,
            "now_cost": 105,
            "selected_by_percent": "45.2",
            "total_points": 200,
            "points_per_game": "5.9",
            "form": "6.0",
            "minutes": 3000,
            "goals_scored": 15,
            "assists": 10,
            "expected_goal_involvements": "22.5",
            "status": "a",
            "news": "",
        }
    ],
}

FIXTURES = [
    {"event": 2, "team_h": 1, "team_a": 2, "team_h_difficulty": 2, "team_a_difficulty": 4},
    {"event": 3, "team_h": 2, "team_a": 1, "team_h_difficulty": 5, "team_a_difficulty": 3},
]


def test_event_helpers():
    assert transforms.current_event_id(BOOT) == 2
    assert transforms.next_event(BOOT)["id"] == 3
    assert transforms.season_started(BOOT)
    assert [e["id"] for e in transforms.finished_events(BOOT)] == [1]


def test_players_frame():
    df = transforms.players_frame(BOOT)
    row = df.iloc[0]
    assert row["Player"] == "Saka"
    assert row["Team"] == "ARS"
    assert row["Price"] == 10.5
    assert row["xGI"] == 22.5
    assert row["Availability"] == ""


def test_fixture_grid():
    diff, opp = transforms.fixture_grid(FIXTURES, BOOT, from_event=2, horizon=2)
    assert diff.at["ARS", "GW2"] == 2
    assert opp.at["ARS", "GW2"] == "CHE (H)"
    assert diff.at["CHE", "GW3"] == 5
    assert opp.at["CHE", "GW3"] == "ARS (H)"
    assert diff.at["ARS", "GW3"] == 3
