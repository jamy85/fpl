"""Weekly Awards page: the banter board for a finished gameweek."""

import streamlit as st

from fpl_hub.awards.compute import gameweek_awards
from fpl_hub.core import transforms
from fpl_hub.data_access import fpl_api
from fpl_hub.league import data

AWARD_PREVIEW = [
    ("🏆 Gameweek Champion", "Most points (after hits) in the league that week."),
    ("🥄 Wooden Spoon", "Fewest points. Someone has to."),
    ("©️ Captain Fantastic", "Best returning armband in the league."),
    ("🤡 Captain Calamity", "Biggest gap between the captain picked and the best player they already owned."),
    ("🪑 Bench Blunder", "Most points left rotting on the bench."),
    ("💸 Hit Merchant", "Most points burned on transfer hits."),
]


def render() -> None:
    st.title("🎭 Weekly Awards")
    league_id = st.session_state.get("league_id")
    if not league_id:
        st.info("Enter your mini-league ID in the sidebar to unlock the banter board.")

    boot = fpl_api.bootstrap()
    finished = transforms.finished_events(boot)

    if not finished:
        nxt = transforms.next_event(boot)
        when = nxt["deadline_time"][:10] if nxt else "soon"
        st.write(
            f"Awards are handed out after each gameweek finishes — the first ceremony follows "
            f"**Gameweek 1** (deadline {when}). Here's what's up for grabs every week:"
        )
        for name, desc in AWARD_PREVIEW:
            st.markdown(f"**{name}** — {desc}")
        return

    if not league_id:
        return

    gw_ids = [e["id"] for e in finished]
    event_id = st.selectbox("Gameweek", gw_ids, index=len(gw_ids) - 1)
    member_rows = data.members(league_id)
    stats = data.gw_member_stats(member_rows, event_id, boot)
    if not stats:
        st.warning("No squads found for this league and gameweek.")
        return

    for award in gameweek_awards(stats):
        with st.container(border=True):
            st.markdown(f"### {award['award']}: {award['winner']}")
            st.write(award["detail"])

    st.subheader("The full ledger")
    st.dataframe(
        [
            {
                "Manager": s["name"],
                "Points": s["points"],
                "Hits": -s["transfers_cost"],
                "Net": s["net_points"],
                "Captain": f"{s['captain_name']} ({s['captain_raw']})",
                "Best owned": f"{s['best_pick_name']} ({s['best_pick_raw']})",
                "Bench pts": s["bench_points"],
                "Chip": s["chip"] or "",
            }
            for s in sorted(stats, key=lambda s: -s["net_points"])
        ],
        width="stretch",
        hide_index=True,
    )
