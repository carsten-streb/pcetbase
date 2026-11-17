# Manuscript figures, revision 2 (data: tag v1.6)

Data basis: release v1.6 (tag v1.6 @ f7c72e2, doi:10.5281/zenodo.24293136).
Scripts: `scripts/figures/` on main after the H132 PR (review-manuscript-v1.6 B2, B3),
run in a worktree at tag v1.6 with `PCETBASE_FIG_FOOTER=0 python scripts/figures/render_all.py`.

Changes against `figures/manuscript-v1.6/` (PR #74), layout only, no data change:
- fig6: the H[PVW11O40]4− inset moved to the empty lower part of the "V6 / other"
  column, so the V6 lines (60.6 to 69.2 kcal/mol) and the V6-TRIOL series are visible.
- fig4: hatched "estimated legs only" bands end below the window brackets, their
  label sits beside the band, the class legend sits below the axes.
- fig2, fig3, fig4, fig6: no "drop at composition" provenance footer. fig2 and fig3
  are otherwise identical to the PR #74 renders (checked by rendering with the
  footer on and comparing the SVG).
