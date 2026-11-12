# Changelog

All star (recommendation) moves and releases are recorded here, newest first.

## Unreleased (toward v1.4)

- 2026-11-12: Rh(Cp*)(ppy)H sq + hyd pair BDFE-0474/0475, couple CPL-0470
  (H20 Option B, Carsten; CR-2026-11-12-tmh-wiedner Addendum A). Star to the
  sq row (rule 1, auto); discordant = 1 set by the builder (independent
  closures differ by 1.2 kcal/mol, HPVW11 precedent). The batch-1 check-src
  on this hydride is superseded by the pair. constants.csv CHyd(MeCN) note
  updated to Q1 = a (decided).

- 2026-11-12: TMH batch 1 (CR-2026-11-12-tmh-wiedner): 47 transition-metal
  hydride rows BDFE-0427..0473 (Wiedner Chem. Rev. 2016 SI xlsx, MeCN;
  23 sq + 24 hyd), CHyd constants (MeCN 79.6 as published, H2O 34.2),
  new E_c column (E(X+/X*), the hydricity leg; Q3 decision), hydricity
  diagonal with 1.364 (Q2 decision) now live: 47 checks, 0 deviations
  > 0.5. Method `hyd` enters the recommendation hierarchy below `sq`.
  Rh(Cp*)(ppy)H held back for an sq+hyd pair (H20/H21). Builder
  corrections on delivery: 8 rows' year field held the page range's
  1925 -> 2002; hyd-row pKa_b regenerated with 1.364.

- 2026-11-12: schema for the TMH (transition-metal hydride) class
  (CR-2026-11-11-tmh-schema): new data column `hydricity_kcal`
  (dG(H-), as published), hydricity closure check in validate.py
  (dG(H-) = 1.37 pKa + 23.06 (E1+E2) + CHyd(solvent); active per
  solvent once the CHyd constants from Wiedner Chem. Rev. 2016
  Table 2 land in constants.csv), `hyd_residual_kcal` in
  derived/analysis.csv, class `tmh` in the app legend. One row per
  determination/closure; couples group multiple closures of the
  same M-H bond. No values or stars changed.

## v1.3 — 2026-11-11

DOI: 10.5281/zenodo.24137124 (all versions: 10.5281/zenodo.24121910)

Dataset: 426 measurements, 421 couples (v1.2: 376 entries). Two-layer
measurement/couple model (couple_id, data/couples.csv, FK-gated),
sigma_BDFE/T_K/conditions columns, 50 new POM measurements (batches 1-3,
campaign complete), aliases for search, CONTRIBUTING governance
(selection rules 1-4, star curation), derived/analysis.csv residual
table on every build, autorecommend by method hierarchy, UI: couple-
collapsed table/ladder, alias search, entry permalinks (#BDFE-NNNN),
CSV download (all vs recommended), theme toggle. PR-only workflow with
server-side branch protection. PRs #1-#17.

Star moves in this release:

- 2026-11-11 (rule 4, curator: C. Streb): ★ [HPVW11O40]4- (1st H) / MeCN assigned manually to BDFE-0406 (68.1, direct-pKa square scheme, Lü 2025) over BDFE-0377 (62.5, CV-simulation-fitted pKa, Nambu 2010, same E°) and BDFE-0407 (70.2, same-paper OCP); discordant = 1 (sq/OCP gap 2.1 kcal/mol unresolved).

- 2026-11-11 (PR #3, rule 1): ★ [V6O7(OH)6(TRIOLNO2)2]2- / MeCN assigned to BDFE-0391 (2024 OCP) after the couple split BDFE-0387/0391 was merged (CPL-0390).
- 2026-11-11 (PR #2, rule 1): ★ [VW5O18(OH)]3- / MeCN moved BDFE-0397 (sq, check-src) → BDFE-0398 (equil) on introduction of the method-hierarchy policy.
- 2026-11-11 (PR #2, rule 1): ★ [V6O11(OH)2(TRIOLNO2)2]2- / MeCN confirmed on BDFE-0389 (2024 OCP, newest within tier).
- 2026-11-11: [HPVW11O40]4- (1st H) / MeCN flagged NO STAR (sq-tier spread 5.6 kcal/mol; rule-4 resolution pending).
- Note: commits 00c3cce and b0e7b03 (33 POM rows, 2026-11-11) were pushed directly to main before the PR-only workflow took effect; all subsequent changes carry a PR review trail.

## v1.2 — 2026-11-11

- Initial public release: 376 entries (complete Agarwal et al. Chem. Rev. 2022 extraction + POM pilot class), auto-recommendation machinery, Zenodo DOI 10.5281/zenodo.24121910.
