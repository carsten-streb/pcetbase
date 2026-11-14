# Changelog

All star (recommendation) moves and releases are recorded here, newest first.

## Unreleased (toward v1.5)

### Ladder labels: de-collision + revised archetype anchors (PR #57)
- Anchor and selection-mode labels no longer overlap: labels are pushed apart
  to a 12.5 px minimum gap (clamped to the plot area) and any label moved off
  its rung gets a thin leader line back to it.
- Anchor list revised (Carsten 2026-11-14) to 18 archetypes spaced across the
  full BDFE range (8.6-125.1): [Ru(tpy)(bpy)H]2+, *Ir(ppy)3, N2/N2H2,
  [Co(bpy)2(H2O)H]2+, CO2/CO, DuBois [Ni(PR2NR'2)2H]+ (R = Me), CpCr(CO)3H,
  HCo(CO)4, TEMPOH, [VW12O40]3-, O2/H2O, PhOH, tryptophan, NHPI, CH4,
  thymidine, H2O, acetylene. Label cut 14 -> 18 chars; label margin widened
  (plot width unchanged), so no anchor name is cut mid-formula.
- Gate 88 -> 89 (minimum-gap invariant).

### UI wording round: method labels, tooltips, chips, headline (PR #48)
- Methods block retitled "BDFE determination method" with the hierarchy
  sub-line; labels per Carsten's review: tabulated (review data), equil
  (equilibrium data), sq (square scheme: pKa + E deg), hyd (hydricity cycle),
  OCP (open-circuit potential), hess (Hess combination); hover tooltips per
  method.
- Class chips are multi-select: all-on -> click solos, further clicks
  add/remove, empty restores all. Pair chip "oxidant + base / reductant +
  acid"; metal chip "TM complexes (non-hydride)"; alias-aware search
  placeholder.
- Headline (suggestion A): "PCETbase - open proton-coupled electron transfer
  (PCET) thermochemistry: BDFE, E deg, pKa, hydricity"; new sub-line; <title>
  matches.

### Verification ledger: per-entry record of how each value was checked (PR #56)
- Build-generated derived/verification.csv, one row per entry_id: source type
  and locator, extraction route, primary-verified, introducing CR/PR, last
  modification, closure checks with residuals (byte-copied from analysis.csv),
  outcome vs the validate.py soft thresholds, BDFE-vs-published delta,
  cross-checks (multi-member couples, Morris 2016 second-review pass),
  stress-test spot-checks (25 IDs, 2026-11-12 sample) and a generated
  one-line summary.
- Provenance inputs: hand-maintained data/provenance_batches.csv (13 ID
  ranges, PR-verified) + data/provenance_overrides.csv (50 per-row entries).
- validate.py: hard errors on uncovered entry_ids, overlapping ranges and a
  stale ledger; CI build-sync now diffs verification.csv.
- App: "Verification record" block in the panel + CSV download (this entry /
  full ledger). datapackage verification resource; README + CONTRIBUTING
  (producer provenance-line rule). Gate 84 -> 88.

### Ladder tick boxes: per-couple selection mode (PR #55)
- Leading checkbox per table row (couple-keyed, session-only Set; no
  localStorage). No ticks = today's filtered ladder, unchanged. >= 1 tick =
  selection mode: the ladder shows only ticked couples, every rung labelled,
  banner with count + show all / clear selection; "show all" keeps the ticks.
- Header controls "select visible" / "clear". Filters, chips and search never
  mutate the tick set; a ticked couple filtered out of the table stays on the
  ladder. Sub-row ticks tick their couple (one rung per couple invariant).
- Calculator marker renders in both modes. UI-only, no schema change.
- Gate 81 -> 84 (selection rendering, filter independence, clear).

### Square-scheme view in the verification panel (PR #54)
- SVG thermochemical square for every non-pair row with >= 2 stored legs:
  corners XH(.+)/X(.)/XH/X(-), stored legs solid with values, eq-10-derivable
  legs dashed "(derived)", a wholly missing diagonal rendered dashed with its
  joint sum constraint (one undetermined corner), unknown legs greyed.
  BDFE diagonal always shown; E_c + hydricity rows get the X+ corner and the
  1.364 hydricity diagonal. Pair rows show a one-line notice instead.
- Theme-aware (CSS variables); corner labels generic for formula strings.
- Gate 77 -> 81 (full square, derived-edge marking, hydricity extension,
  pair exclusion).

### Origin provenance: exp/comp/mixed column + filter (PR #53)
- New data.csv column origin (enum exp/comp/mixed/empty; datapackage +
  validate.py hard enum check, soft warn on origin=exp with a
  simulation-fitted leg). Classification is incremental: empty = not yet
  classified, never guessed; gas-phase rows deliberately NOT bulk-labelled.
- Stage-1 pass (from stored conditions text): 14 rows classified mixed
  (simulation-fitted legs: the 10 DigiSim POM titration rows BDFE-0377..0386,
  the two W(Cp)(CO)2(IMes)H rows, the two Co(P4N2)H rows). No stored leg is
  DFT-computed, so comp is currently empty.
- UI: Origin filter (all/experimental/computational/mixed/not classified),
  superscript c/m markers in the table, origin in the ladder tooltip,
  Origin line in the verification panel, origin column in the CSV export.
- Gate 73 -> 77 (filter count, panel lines, CSV column).

### TMH round 2a: first aqueous Co-H entries - TMH campaign complete (PR #52)
- 3 new rows (BDFE-0521..0523), all approx with explicit sigma_BDFE per the
  H64 drop rule: [HCo(CN)5]3- 56.5 hess sigma 4.5 (Halpern 1971 kinetic pKa
  ca. 20; Lim & Anson 1971 Hess-composed E(II/I) -1.27 V vs SCE);
  rac-[Co(HMD)(H2O)H]2+ 38.1 sq sigma 2.5 (Creutz 1991 pKa 11.5; E(II/I)
  -1.32 V vs SHE estimated from the Fujita 1991 MeCN E1/2);
  [Co(bpy)2(H2O)H]2+ 37.1 sq sigma 3 (Creutz 1984 pKa 6.9; Schwarz 1985
  ladder E(II/I) -1.09 V vs NHE).
- The two macrocycle/polypyridine hydrides (37-38 kcal/mol) are the weakest
  M-H bonds in the database. Water now holds 7 TMH rows on 7 hydrides.
- Rh(Cp*)(bpy)H+ dropped at step 0 (ring protonation, Pitman & Miller 2016);
  meso-HMD, cobaltocene and Rh(en)2 out of scope (H64).

### TMH phase P5: group-6/7/8/9 carbonyl hydrides in MeCN (PR #51)
- 11 new rows (BDFE-0510..0520), all MeCN sq full cycles: anion oxidation
  potentials from Tilset & Parker 1989 (DCV peak + kinetic dimerization
  shift), hydride pKas from Moore/Sullivan/Norton 1986. Group 6 (CpMo(CO)3H,
  CpW(CO)3H, Cp*Mo(CO)3H, CpW(CO)2(PMe3)H) also carry the oxidised diagonal
  (E_b, pKa_a) from Ryan/Tilset/Parker 1990. BDFEs 58.6-68.6.
- Reference bases rescaled to the current MeCN scale (Tshepelevitsh 2019)
  where a value exists; morpholinium and p-CF3-anilinium kept as published
  (Carsten decision, H81); phenolate case check-src.
- M1 (approved, H81): BDFE-0126 CpCr(CO)3H rescaled (pKa_b 13.53), E_b
  +0.668 V added, BDFE 54.9 -> 55.3.
- Published values in these papers are enthalpy BDEs (constant 50.3);
  BDFE_pub left empty, each row's conditions give the published BDE.

### TMH phase P4: aqueous primaries + Fe4N cluster (PR #50)
- 6 new rows (BDFE-0504..0509): Pitman/Brereton/Miller 2016 water hydricities,
  [Cp*Ir(bpy-COO)H]- and [(cymene)Ru(bpy-COO)H]-, each stored twice - to the
  aquo complex and, as its own couple with the suffix "(to hydroxo complex)",
  to the hydroxo complex (the 5.2 kcal/mol gap is the product-state term,
  Carsten decision Q2); [Rh(bpy)2(H2O)H]2+ (Schwarz & Creutz 1983 potentials,
  Chou 1982 pKa, method hess); [Fe4N(CO)12H]- in MeCN (Taheri 2015, sq,
  check-src: pKa rescaled 20.3 -> 21.1 on the current MeCN acidity scale via
  benzoic acid 20.7 -> 21.5 (Kutt 2021), BDFE 44.4 vs published 47).
- Water now holds 6 TMH rows on 4 hydrides; both potential-pKa entries of
  Wiedner 2016 Table 4 are in.

### TMH phase P3: OCP hydricities + first aqueous TMH row (PR #49)
- 5 new rows (BDFE-0499..0503): three OCP hydricity determinations (Smith &
  Miller 2024) on CPL-0460/0433/0454 - the first OCP-method TMH rows; the
  heterobimetallic [Cp*Ir(H)(mu-bpm)Ru(bpy)2]3+ (Brereton 2016) in MeCN and in
  water (first aqueous TMH row; CHyd(H2O) 34.2, CG(H2O) 52.8).
- Stars (manual freeze, builder decision on CR open q.1): CPL-0433 and CPL-0454
  keep the sq row starred (hierarchy sq > OCP); CPL-0454 set discordant
  (sq vs OCP 1.3 kcal/mol); CPL-0460's discord reason now lists the OCP value
  (three-method spread 3.8 kcal/mol).
- BDFE-0469: primary-check note (Price 2002), no value change.
- Counts: 503 measurements / 487 couples; no new deviations.

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
