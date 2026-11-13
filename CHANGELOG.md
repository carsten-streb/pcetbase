# Changelog

All star (recommendation) moves and releases are recorded here, newest first.

## v1.4.1 — 2026-11-13

Point release, data unchanged (498/485, identical to v1.4). Version DOI
10.5281/zenodo.24186854. Shipped figure set carries the v1.4 watermark
(content identical to a v1.4.1 render).

### Stress-test fixes (CR-2026-11-12-stress-v1.4 F1–F6, PR #46)
- .zenodo.json + CITATION.cff: scope sentence and keywords extended to the TMH/
  hydricity content; "version": "1.4" added; the two files are field-identical (F1).
- Figure watermark now reads the release version from CITATION.cff instead of
  git describe; set re-rendered as "PCETbase v1.4" (F2).
- App header: prototype disclaimer dropped; data line names Wiedner/Morris 2016
  and the primary literature (F3). Footer and README: neutral "this release: v1.4,
  version DOI minted on Zenodo after archiving" until the DOI-reference PR (F4).
- CSV export: pKa_a, E_a_V, E_b_V, E_c_V columns added, so exported hyd rows
  re-close their hydricity; jsdom gate extended to 73 assertions (F5).
- CONTRIBUTING rule 4 + build.py docstring: cross-closure discord convention
  (~1 kcal/mol, auto star, recorded reason) made explicit (F6).
- Queued: F7 validator hardening + F8 analysis.csv line endings (v1.4.x);
  F9 10k latency + F10 flag question (v1.5).

## v1.4 — 2026-11-12

**Scope:** all transition-metal hydrides from the Wiedner 2016 and Morris 2016
review tables that close a BDFE, primary-verified where the review value was
doubtful or deferred (batch-1 deferral list closed). 498 measurements / 485
couples. Figure set (figures/, Figs 2, 3, 4, 6) rendered from this state by
scripts/figures/render_all.py. Version DOI 10.5281/zenodo.24175058 (archives
the pre-stress-fix tag state b177031; the stress fixes are v1.4.1).

### TMH primary-literature pass P2c (PR #44) - closes the batch-1 deferral list
- 6 new rows (BDFE-0493..0498, CPL-0481..0486): cis-[Rh(depx)2(H)2]+ sq,
  Rh(depx)2H hyd, [Rh(depx)2H]+ hess (Raebiger 2005); [W(Cp)(CO)2(IMes)H]+ and
  [W(Cp)(CO)2(IMes)(H)2]+ hess (Roberts 2011); Co(dppe)2H hyd (Ciancanelli 2002 SI).
- BDFE-0454 W(Cp)(CO)2(IMes)H: BDFE_pub 59.3, derived -> recomputed, primary-check
  note (E_c -1.22 V identified as the effective MeCN-binding-corrected potential).
- Method `hess` scope settled (builder decision on CR open q.2): a row whose
  defining pKa or BDFE is Hess-composed from other measured legs, not only
  Hess-derived hydricities.
- Co(dppe)2 potentials resolved against the primary SI (Results values -0.70/-1.56/
  -2.03 V used in all cycles); P2a rows unaffected.
- Counts: 498 measurements / 485 couples; no new deviations. Last data batch in v1.4.

### TMH primary-literature pass P2b (PR #43)
- 3 new Ru rows from Matsubara et al. JACS 2012 (BDFE-0490..0492, CPL-0478..0480):
  [Ru(tpy)(bpy)H]+ `hyd` (hydricity 39+/-3, sigma 3), [Ru(tpy)(bpy)H]0 and
  [Ru(tpy)(bpy)H]2+ as the first `hess`-method rows (derived from the + hydride's
  measured hydricity plus potentials; both `check-src`: the paper's Scheme 5B BDFEs
  56 and 14 do not close with its own potentials, excess matches its 4.7 kcal/mol
  DFT five-coordinate correction). BDFE values referenced to the solvento product.
- BDFE-0458 [Ru(C6Me6)(bpy)H]+: BDFE_pub 56.0 (lower limit, flag `limit`),
  flags derived -> recomputed, primary-check note. No value change.
- Method `hess` now ranked explicitly (rank 2) in build.py and the app; the method
  filter lists it automatically with label "hess (Hess cycle)".
- [Ru(tpy)(bpy)H]- deferred (no E_a reported; no square-scheme pair).
- Counts: 492 measurements / 479 couples; no new deviations.

### TMH primary-literature pass P2a (PR #42)
- 6 new Co hydride rows from Wiedner-review primaries (BDFE-0484..0489, CPL-0473..0477):
  cis-[H2Co(dppe)2]+ sq/hyd pair (Ciancanelli 2002; spread 0.1 kcal/mol),
  [HCo(dppe)2(MeCN)]2+ (Ciancanelli 2002), [HCo(P4N2)(MeCN)]2+ and Co(P4N2)H
  (Wiedner 2013; hyd row form 2, `approx` Co(I/0) estimate), Co(CpC5F4N)(PtBu2NPh2)H
  oxidised diagonal (Fang 2014, form 2, hydricity filled on a single-determination row).
- BDFE_pub filled on BDFE-0428 (53.0, Fang 2014) and BDFE-0465 (39.7, Wiedner 2013
  completed cycle); flags derived -> recomputed on both.
- Counts: 489 measurements / 476 couples; 12 multi-source badges; no new deviations.

- 2026-11-12: TMH primaries batch P1 (CR-2026-11-12-tmh-primaries-p1):
  8 new rows BDFE-0476..0483 (6 measured-pKa sq second determinations
  on existing couples - Berning 1999 / Curtis 2002 primaries, independent
  of the H2-heterolysis hydricities - plus the Pt(EtXantphos) Pt(III)-H
  and dihydride species, couples CPL-0471/0472). Star moves (rule 1,
  auto, routine curation): six couples' stars move hyd -> sq
  (dmpp/depe/dmpe Ni; dmpp/dmpe Pt; depp Ni). discordant = 1 set on
  CPL-0460 (delta 1.1) and CPL-0464 (delta 1.0); CPL-0430 (0.9) below
  the ~1 kcal/mol line. Value correction BDFE-0427 [Pt(EtXantphos)2H]+
  to the Miedaner 2004 primary: pKa 27.3, BDFE 69.0 -> 67.6, hydricity
  75.8, sigma 2 (Wiedner's 28.3 used a derived anchor). All four Morris
  check-src flags resolved (case-13 candidates = primary arithmetic
  errors copied by Morris); PhCN caveats corrected per the primaries.


- 2026-11-12: Morris cross-check (CR-2026-11-12-tmh-morris): Co(III)-acid
  relabel of BDFE-0443/0465 (pKa and 1e couple moved to pKa_a/E_b, their
  square-scheme meaning; values unchanged; primary-verified vs Ciancanelli
  2002 and Wiedner 2013). BDFE-0443: check-src and approx resolved,
  BDFE_pub 53.7 -> 49.9 (Wiedner cell F29 used the wrong couple -
  source-inconsistency case 11 CONFIRMED). validate.py hydricity diagonal
  gains form 2 (oxidized-hydride route, E_b + pKa_a). Morris notes on 15
  further rows; new check-src on 0427, 0431, 0459, 0462 (primary checks
  pending, H31). No value or star changes.


- 2026-11-12: manuscript figure scripts (CR-2026-11-12-figure-scripts):
  scripts/figures/{figcommon,fig2,fig3,fig4,fig6,render_all}.py render the
  data-derived figure set (SVG + 600 dpi PNG into figures/) from the current
  checkout; release workflow runs render_all.py at the tag so output is
  pinned. First-render verification: derived/analysis.csv residuals at
  v1.3 vs 27e97c7 identical on all 426 rows (only compound labels differ,
  PR #26 relabels) - the 5.1 rerun numbers hold for v1.3. Font: Arial with
  Liberation Sans fallback (CI/Linux).


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
