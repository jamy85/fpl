"""League Hub page: standings, rank progression, this-GW captains."""

import plotly.graph_objects as go
import streamlit as st

from fpl_hub.core import transforms
from fpl_hub.data_access import fpl_api
from fpl_hub.league import data
from fpl_hub.ui import theme


def _standings_table(member_rows: list[dict]) -> None:
    rows = []
    for m in member_rows:
        moved = m["last_rank"] - m["rank"] if m["last_rank"] else 0
        arrow = "▲" if moved > 0 else ("▼" if moved < 0 else "–")
        rows.append(
            {
                "Rank": m["rank"],
                "": arrow,
                "Team": m["entry_name"],
                "Manager": m["player_name"],
                "GW": m["event_total"],
                "Total": m["total"],
            }
        )
    st.dataframe(rows, width="stretch", hide_index=True)


def _progression_chart(member_rows: list[dict]) -> None:
    df = data.rank_progression(member_rows)
    if df.empty:
        return
    fig = go.Figure()
    managers = list(df["manager"].unique())
    for i, mgr in enumerate(managers):
        sub = df[df["manager"] == mgr]
        color = theme.CATEGORICAL[i] if i < len(theme.CATEGORICAL) else theme.INK_MUTED
        fig.add_trace(
            go.Scatter(
                x=sub["gw"],
                y=sub["league_rank"],
                mode="lines+markers",
                name=mgr,
                line=dict(color=color, width=2),
                marker=dict(size=8),
                hovertemplate=f"{mgr}<br>GW%{{x}}: rank %{{y}} · %{{customdata}} pts total<extra></extra>",
                customdata=sub["total"],
            )
        )
    fig.update_yaxes(autorange="reversed", dtick=1, title="League rank")
    fig.update_xaxes(dtick=1, title="Gameweek")
    fig.update_layout(title="Race chart — league rank by gameweek")
    st.plotly_chart(theme.apply_layout(fig, height=450), width="stretch")
    if len(managers) > len(theme.CATEGORICAL):
        st.caption(
            f"Only the first {len(theme.CATEGORICAL)} managers get their own colour; the rest are grey."
        )


def _captains_now(member_rows: list[dict], event_id: int, boot: dict) -> None:
    stats = data.gw_member_stats(member_rows, event_id, boot)
    if not stats:
        st.info("Squads for this gameweek aren't visible yet (they unlock at the deadline).")
        return
    st.dataframe(
        [
            {
                "Manager": s["name"],
                "Captain": s["captain_name"],
                "Chip": s["chip"] or "",
                "GW points": s["points"],
                "On bench": s["bench_points"],
            }
            for s in stats
        ],
        width="stretch",
        hide_index=True,
    )


def render() -> None:
    st.title("🏆 League Hub")
    league_id = st.session_state.get("league_id")
    if not league_id:
        st.info(
            "Enter your mini-league ID in the sidebar. Find it on the FPL site: open your "
            "league and copy the number from the URL — `…/leagues/`**`123456`**`/standings/c`."
        )
        return

    league = fpl_api.league_standings(league_id)
    st.subheader(league["league"]["name"])
    boot = fpl_api.bootstrap()
    member_rows = data.members(league_id)

    if not member_rows:
        st.write("No standings yet — the table appears once Gameweek 1 kicks off.")
        joiners = league.get("new_entries", {}).get("results", [])
        if joiners:
            st.write(f"**{len(joiners)} managers have joined so far:**")
            st.dataframe(
                [
                    {"Manager": f"{j['player_first_name']} {j['player_last_name']}", "Team": j["entry_name"]}
                    for j in joiners
                ],
                width="stretch",
                hide_index=True,
            )
        return

    _standings_table(member_rows)
    _progression_chart(member_rows)

    event_id = transforms.current_event_id(boot)
    if event_id:
        st.subheader(f"Gameweek {event_id} squads")
        _captains_now(member_rows, event_id, boot)
