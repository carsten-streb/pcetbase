"""Render the full manuscript figure set (Figs 2, 3, 4, 6) from the current checkout.
Release workflow: run at the tag so output is pinned (python scripts/figures/render_all.py)."""
import fig2, fig3, fig4, fig6
for m in (fig2, fig3, fig4, fig6):
    m.main()
