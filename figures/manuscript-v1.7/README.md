# Manuscript figures (data: release v1.7)

Data basis: release v1.7 (547 measurements / 531 couples; version DOI minted on Zenodo
after archiving; the DOI-reference PR adds it here). Rendered in the release prep PR
(board H150) from the release content with
`PCETBASE_FIG_FOOTER=0 python scripts/figures/render_all.py`; the release figure set in
`figures/` is the same render with the provenance footer (watermark v1.7).

What the scripts print for this render:
- Fig 2: no-ladder rows not drawn (EP-09): 2 (BDFE-0508, BDFE-0509); bounded rungs carry a ≥/≤ marker.
- Fig 3: bounded rows excluded from the statistics: 5 (BDFE-0093, BDFE-0100, BDFE-0141,
  BDFE-0142, BDFE-0458); no-ladder rows excluded: 2; eq 1 (code eq 18): n = 540,
  σ = 0.101 kcal/mol, 91.9 % within 0.1 kcal/mol, 98.3 % within 0.3 kcal/mol; eq 2 (code eq 10): n = 309;
  panel d: n = 34.
- Fig 4: bounded couples excluded from the window code: MeCN 1 (BDFE-0458), H2O 3
  (BDFE-0093, BDFE-0141, BDFE-0142); brackets MeCN 24.7 to 34.3 kcal/mol and 90.9 to
  103.3 kcal/mol; H2O 26.8 to 49.0 kcal/mol.
- Fig 6: panel b 14 multi-member couples, 30 points.

Changes against `figures/manuscript-v1.6-r2/` follow from the v1.7 data and scripts
(bounds, no-ladder exclusions, corrected BDFE-0038/0039 and BDFE-0507, renamed compounds);
layout is unchanged.
