"""Chart palette + plotly styling. Values are the validated reference palette
(light mode) from the dataviz method - swap here, nowhere else."""

import plotly.graph_objects as go

# Categorical slots, fixed order (CVD-validated for adjacent pairs; cap at 3
# hues for scatter/all-pairs forms - facet or gray-out beyond that).
CATEGORICAL = [
    "#2a78d6",  # blue
    "#eb6834",  # orange
    "#1baf7a",  # aqua
    "#eda100",  # yellow
    "#e87ba4",  # magenta
    "#008300",  # green
    "#4a3aa7",  # violet
    "#e34948",  # red
]

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
NEUTRAL_FILL = "#f0efec"

# FDR 1 (easiest) -> 5 (hardest): diverging blue <-> red around neutral gray.
FDR_COLORS = {1: "#256abf", 2: "#9ec5f4", 3: "#f0efec", 4: "#ec9b8a", 5: "#d03b3b"}
FDR_TEXT = {1: "#ffffff", 2: "#0b0b0b", 3: "#0b0b0b", 4: "#0b0b0b", 5: "#ffffff"}

FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'


def apply_layout(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        height=height,
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        font=dict(family=FONT, color=INK_SECONDARY, size=13),
        title_font=dict(color=INK, size=15),
        margin=dict(l=10, r=10, t=40, b=10),
        hoverlabel=dict(bgcolor="#ffffff", font=dict(family=FONT, color=INK)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    fig.update_xaxes(gridcolor=GRID, linecolor=BASELINE, zerolinecolor=GRID, tickfont=dict(color=INK_MUTED))
    fig.update_yaxes(gridcolor=GRID, linecolor=BASELINE, zerolinecolor=GRID, tickfont=dict(color=INK_MUTED))
    return fig
