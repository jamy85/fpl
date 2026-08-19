"""Scout page: player finder, fixture-difficulty grid, value scatter."""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from fpl_hub import config
from fpl_hub.core import transforms
from fpl_hub.data_access import fpl_api
from fpl_hub.ui import theme


def _fdr_colorscale() -> list:
    scale = []
    for i in range(1, 6):
        lo, hi = (i - 1) / 5, i / 5
        scale += [[lo, theme.FDR_COLORS[i]], [hi, theme.FDR_COLORS[i]]]
    return scale


def _fixture_heatmap(boot: dict) -> None:
    nxt = transforms.next_event(boot)
    cur = transforms.current_event_id(boot)
    from_event = cur or (nxt["id"] if nxt else 1)
    diff, opp = transforms.fixture_grid(
        fpl_api.fixtures(), boot, from_event, config.FDR_HORIZON_GWS
    )
    fig = go.Figure(
        go.Heatmap(
            z=diff.values,
            x=diff.columns.tolist(),
            y=diff.index.tolist(),
            text=opp.values,
            texttemplate="%{text}",
            textfont=dict(size=10),
            colorscale=_fdr_colorscale(),
            zmin=0.5,
            zmax=5.5,
            xgap=2,
            ygap=2,
            hovertemplate="%{y} · %{x}: %{text} — difficulty %{z}<extra></extra>",
            colorbar=dict(
                title="FDR", tickvals=[1, 2, 3, 4, 5],
                ticktext=["1 easy", "2", "3", "4", "5 hard"],
            ),
        )
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(title=f"Fixture difficulty — next {config.FDR_HORIZON_GWS} gameweeks")
    st.plotly_chart(theme.apply_layout(fig, height=620), width="stretch")


def _value_scatter(df, points_label: str) -> None:
    fig = px.scatter(
        df,
        x="Price",
        y="Points",
        facet_col="Pos",
        category_orders={"Pos": ["GKP", "DEF", "MID", "FWD"]},
        hover_name="Player",
        hover_data={"Team": True, "Selected %": True, "Price": ":.1f"},
        color_discrete_sequence=[theme.CATEGORICAL[0]],
        opacity=0.75,
    )
    fig.update_traces(marker=dict(size=8))
    fig.update_layout(title=f"Value map — {points_label} vs price")
    fig.update_xaxes(title="Price (£M)")
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    st.plotly_chart(theme.apply_layout(fig, height=380), width="stretch")


def render() -> None:
    st.title("🔭 Scout")
    boot = fpl_api.bootstrap()
    df = transforms.players_frame(boot)
    started = transforms.season_started(boot)
    points_label = "points this season" if started else "points last season (2025/26)"
    if not started:
        st.caption("Season hasn't started yet — stats shown are from last season.")

    f1, f2, f3, f4 = st.columns([2, 2, 3, 3])
    with f1:
        positions = st.multiselect("Position", ["GKP", "DEF", "MID", "FWD"])
    with f2:
        price_lo = float(df["Price"].min())
        price_hi = float(df["Price"].max())
        max_price = st.slider("Max price (£M)", price_lo, price_hi, price_hi, 0.5)
    with f3:
        team_pick = st.multiselect("Team", sorted(df["Team"].unique()))
    with f4:
        search = st.text_input("Search player")

    view = df[df["Price"] <= max_price]
    if positions:
        view = view[view["Pos"].isin(positions)]
    if team_pick:
        view = view[view["Team"].isin(team_pick)]
    if search:
        view = view[view["Player"].str.contains(search, case=False)]

    st.dataframe(
        view.sort_values("Points", ascending=False)
        .drop(columns=["id", "team_id"])
        .reset_index(drop=True),
        width="stretch",
        height=350,
    )

    _value_scatter(view, points_label)
    _fixture_heatmap(boot)
