# Project log (newest first)

## 2026-08-19 — Scout price slider clipped Haaland (£15.5M)
- Root cause: hardcoded slider range 3.5–15.0 in `scout/page.py`. Fix: derive
  min/max from `df["Price"]`. Verified via headless AppTest: slider 4.0–15.5.

## 2026-08-19 — API probe + v1 scaffold
- Probed the public FPL API live (all endpoints 200, no auth): map + gotchas → `docs/fpl-api.md`.
  Season context: 2026/27 GW1 deadline 2026-08-21T17:30Z — all per-GW data empty until then.
- Scaffolded v1 Streamlit app (src/fpl_hub hierarchy, editable install): League Hub,
  Weekly Awards (pure `awards/compute.py` + tests), Scout (filters, value scatter,
  FDR heatmap). Verified: pytest green + headless `streamlit run` smoke test.
