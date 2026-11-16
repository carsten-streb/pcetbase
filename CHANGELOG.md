# Changelog

## Unreleased (toward v1.7)

### Manuscript figures at v1.6 (PR #74; board H119 step 2)
- figures/manuscript-v1.6/: fig2/3/4/6 (PNG 600 dpi + SVG) rendered from tag v1.6
  (f7c72e2) with the PR #71 label layer; watermark v1.6. Content identical to the
  release set figures/ (normalised SVG comparison). figures/manuscript-v1.5/ unchanged.

### v1.6 DOI references (PR #73)
- Version DOI 10.5281/zenodo.24293136 (Zenodo, 2026-11-16) in the footer citation
  line, README, CITATION.cff and the build.py RELEASE stamp; tag v1.6 @ f7c72e2.

## v1.6 — 2026-11-16 (doi:10.5281/zenodo.24293136)

Data freeze at PR #70: **547 measurements / 531 couples** (v1.5: 525 / 509).
Scope since v1.5: MOH campaign completed (P2–P4 + citation chase: Cu tricopper
ladder and aqueous Tolman variants, Mn series, Fe aqua/hydroxo series in water,
Zr/Co heterobimetallic OCP, Ni(PS3″) aqua; enrichments of BDFE-0099, -0100,
-0132, -0133, -0134); **one correction of a v1.5 value (BDFE-0525, 110.1 →
81.5 kcal/mol)**; usability package (typed pair lookup, filter counts, σ
labelling, export disclosure, dev/release footer stamp); square-scheme redesign
with named worked equations and a unit on every value; curation statement;
manuscript figure scripts with label layer (renders pinned to v1.5 under
figures/manuscript-v1.5/). No v1.5.1 was tagged (H98): the v1.5.x work below
ships in this release. Release figure set (figures/) re-rendered, watermark v1.6.

### Release prep v1.6 (PR #72)
- CITATION.cff / .zenodo.json version 1.6; footer stamp RELEASE 1.6 / 547
  measurements; footer and README name v1.6 with neutral DOI wording until the
  version DOI mints (DOI-reference PR follows); jsdom U4 assertion moved from the
  development-state stamp to the release stamp.
- Review fixes (H121): CITATION.cff top-level doi = concept DOI
  10.5281/zenodo.24121910 (was the v1.5 version DOI; B2); keyword
  "metal-oxo/hydroxo complexes" in CITATION.cff and .zenodo.json (N1).

### Correction of a v1.5 value + MOH citation chase (PR #70; CR-2026-11-16-moh-0525-correction + CR-2026-11-16-moh-chase)
- **v1.6 correction of a v1.5 value: BDFE-0525** [(LD)FeIII(OH)]− / [(LD)FeIV(O)]−
  (LD = H3buea, DMSO). v1.5 stored E_a +0.34 V vs Fc+/0 and BDFE 110.1 kcal/mol,
  taken from Warren 2010 Table 21, which tabulated the irreversible 2003 wave;
  the primary group re-measured the couple reversibly at −0.90 V vs Fc+/0
  (Lacy et al. 2010). Corrected: E_a −0.90 V vs Fc+/0, E_H2 1.25 V vs H2,
  BDFE 81.5 kcal/mol; pKa_b 25.0 page-verified (Gupta & Borovik 2003); flags
  `dmso-unc;check-src` (`check-src` for the unstated solvent of the Lacy CV),
  σ empty, doi 10.1021/ja1047818. The v1.5 release (doi:10.5281/zenodo.24222265)
  stays as published; this entry documents the change.
- Verification ledger: BDFE-0525 now has its own batch line (source_type
  `primary`: Lacy et al. 2010 E leg, Gupta & Borovik 2003 pKa leg); BDFE-0524
  keeps the Warren 2010 Table 21 line (review finding B1, H121).
- BDFE-0547 [NiII(PS3″)(OH2)]− / [NiIII(PS3″)(OH)]− (Pan et al. 2025, DMSO):
  oxidized-diagonal storage, E_b −0.68 V vs Fc+/0, pKa_a 33.8 (midpoint of the
  32.5–35 bracket), BDFE 98.6 kcal/mol, `approx;dmso-unc`, σ 2.0 kcal/mol —
  the highest O–H BDFE in class `moh`.
- BDFE-0099 and BDFE-0100 page-verified against Gupta & Borovik 2003 Table 1
  (doi/year/conditions; stored values kept, recomputations within 0.1 kcal/mol).
- Builder decisions: chase q.1 midpoint + `approx` + σ confirmed; q.2 the 0525
  correction and its amendment applied in one commit (v1.5 state → final state).
- 547 measurements / 531 couples. MOH campaign complete.
### Manuscript figure labels (PR #71; CR-2026-11-16-figure-labels-pom)
- scripts/figures/figcommon.py: `POM_LABELS` display map (stored name →
  proton-in-front manuscript form, e.g. H[PVW11O40]4−, H2[V6O13(TRIOL^NO2)2]2−,
  H[VW5O19]3−), `mathname()` / `display_name()` for sub/superscripts in every
  formula label, mathtext set in the same sans face as the text. Stored compound
  names unchanged.
- fig3: axes renamed to the manuscript numbering (eq 1 residual, eq 2 residual),
  unit kcal mol−1 on every axis including the σ panels; case boxes typeset.
- fig2/fig3/fig4/fig6 re-rendered from tag 7da97ac (v1.5 data) into
  figures/manuscript-v1.5/. Plotted data arrays identical to the PR #66 renders
  (checked artist by artist); fig4 re-rendered only for the shared font change.

### MOH P4 (PR #69; CR-2026-11-16-moh-p4)
- 5 rows BDFE-0542..0546: Molla et al. 2024 [FeII(L5R)(OH2)]+ / [FeIII(L5R)(OH)]+
  series in water (R = OMe, H, Cl, NO2; all four legs from the pH-independent
  segments of Pourbaix diagrams, BDFE = mean of both diagonals 67.2–69.0 kcal/mol,
  flag `avg`; Pourbaix origin stated in each conditions string) and Feresin et
  al. 2025 HO–Zr(MesNPiPr2)3CoCNtBu (THF, direct OCP 0.503 V vs H2,
  BDFE 63.6 kcal/mol, σ 1.0 kcal/mol; heterobimetallic MS-CPET).
- BDFE-0132 [(F8TPP)FeIII(OOH)] enriched from Kim et al. 2020 (page-verified):
  BDFE 72.1 → 72.4 kcal/mol recomputed from the same legs, `lowT;recomputed`,
  T 193 K, σ 0.7 kcal/mol; class metal-3d kept (Karlin heme set stays together).
- Builder decisions: q.1 (a) as delivered (both Molla diagonals close within
  the gates; deviation lists unchanged); q.2 no new `pourbaix` flag; q.3 0132
  keeps metal-3d; q.4 shipped as its own PR (no rule-11 review needed).
- 546 measurements / 530 couples.

### MOH P3: manganese series (PR #64)
- 8 rows (BDFE-0534..0541), all primaries page-read, all oxidized-diagonal
  (form-2) storage: Barman/Borovik 2019 H3bpuea-R series (DMSO, 5 rows
  68.1-70.3; published on the pre-Correction C 71.1, recomputed with CG
  68.0); Moore/Doerrer 2023 pinF MnII-aqua (THF, 68.3, approx + sigma 3);
  Lee/Cho 2024 TBDAP aqua-hydroxo/bis-aqua (MeCN, 73.0/74.7; published
  75.3/77.3 used the erroneous 2010 CG 54.9, SCE potentials converted with
  the PCETbase refoff).
- No rows: Opalade 2021 + the dpaq5R series (DFT-calculated only; the
  literature list's experimental-looking values were a planning error,
  corrected); Wijeratne 2014 (no pKa).
- 541/525; jsdom baselines bumped.

### MOH P2: tricopper ladder + aqueous Tolman variants (PR #63)
- 8 rows (BDFE-0526..0533), all primaries page-read: Mondal 2024 tricopper
  TREN4 MCO model in MeCN - six mu-OH2/mu-OH/mu-O couples 44.7-78.1 kcal/mol
  with two direct OCP anchors (53.0 +/- 1.2, 57.1 +/- 1.11) and four
  Hess-propagated rows (one form-2); Dhar 2018 water-soluble charged Tolman
  variants [SO3LGCu(OH2)]2- 83.9 and [NMe3LGCu(OH2)]2+ 87.5 (first aqueous
  Cu-OH2 rows). All Tolman BDEs recomputed to BDFEs, nothing copied.
- Enrichments: BDFE-0134 page-verified vs Dhar 2015 + oxidized diagonal
  stored (E_b 0.345 V, pKa_a 11.7 from CV simulation -> sim-pKa, origin
  mixed); BDFE-0133 page-verified vs Dhar 2016 (+doi/year/sigma).
- 533/517; jsdom baselines bumped (mixed = 15).

### v1.5.x work (untagged, shipped in v1.6)

#### Curation statement (PR #68; usability U20, H98 a)
- "How the data were curated" statement (wording cleared by C. Streb,
  2026-11-16) added as a collapsible section in the footer, linked from the
  header, and as a README section.

#### Square-scheme redesign, equation names, units ground rule (PR #67; CR-2026-11-16-square-scheme-typography, CR-2026-11-16-equation-labels, CR-2026-11-16-units addendum)
UI/wording/docs only — no data value changed.
- Square scheme rebuilt on the manuscript Scheme 1 model: corner species boxes
  (the X–H species named, with sub/superscripts), arrowheads on every leg,
  stacked horizontal labels (transfer, symbol = value with unit, reference
  scale), the BDFE diagonal labelled horizontally on a filled box with
  E°(H•), hydricity as its own cycle below the square with a worked
  hydricity-cycle equation, plain-word legend, no rotated or clipped text.
  Hess-composed stored legs render dashed (derived); supersedes the PR #65
  interim leg style.
- User-facing equation names: "Bordwell equation" and "BDFE from the H-atom
  potential" replace the bare "eq 10"/"eq 18" (source equation numbers of
  Agarwal et al. 2022 now live in ⓘ tooltips); ledger closure names mapped at
  render time ("Bordwell closure", "H-atom-potential closure"); file column
  names eq10_/eq18_residual_kcal kept and documented in README + datapackage.
- Units ground rule (rule 10) in the worked equations: every number carries
  its unit and reference scale (23.06 kcal mol⁻¹ V⁻¹ × (−1.920 V vs Fc+/0) …);
  pKa stays unitless; U+2212 minus throughout displayed values (table, panel,
  scheme); long equation lines wrap instead of clipping.
- Render-time sub/superscripts for compound names across table, panel, ladder
  labels, tooltips and scheme (data files and CSV exports keep plain text);
  oxidation states and trailing charges superscripted, formula digits
  subscripted; "pKa" as plain text eliminated from visible UI text (pKₐ / pK
  with subscript).
- Plain-language ledger follow-up: "eq-10 closures recomputed" → "Bordwell
  closures recomputed" in two provenance ranges.
- jsdom gate 112 → 124 assertions.

#### Manuscript figure scripts at v1.5 (PR #66; CR-2026-11-14-manuscript-figures)
Scripts only — no data, app or schema change; the committed renders under
figures/manuscript-v1.5/ are produced from the v1.5 tag data (7da97ac) with the
revised scripts (watermark "PCETbase v1.5").
- figcommon.py: class `moh` added to colours/labels/display map (F-1).
- fig3.py: case boxes renumbered to the status-doc cases 1, 3, 5, 6b; new
  panel (d) eq 10 residual vs pKa for the 34 TMH hyd/OCP rows with the
  0.006·pKa line (1.364 vs 1.37 factor); boxes now panel (e) (F-2).
- fig4.py: BIN_LO 20 → 5; computed window brackets (gaps ≥ 5 kcal/mol between
  adjacent well-characterized recommended couples) replace the per-bin grey
  shading; estimated-legs-only couples inside a bracket drawn hatched (F-3).
- fig6.py: panel (b) replaced by the dumbbell of all 14 multi-member couples
  (30 points; marker by method, open = sim-pKa, ◆ = discordant, POM grey) (F-4).
#### Usability + units package (PR #65; CR-2026-11-14-usability-test, CR-2026-11-16-units)
UI, wording and documentation only — no data value changed.
- Pair/HAT panel resolves typed names (exact key → unique name/alias → unique
  substring → clickable candidate list); cross-solvent guard unchanged (U1).
- Origin filter options carry classified counts and a classification-stage
  note (U2, label part); README star-policy paragraph replaced by a pointer to
  CONTRIBUTING, and the header links CHANGELOG and "How values are recommended
  and verified" (U3, U14).
- Footer stamp distinguishes a release build from a development state: now
  "541 measurements — development state after v1.5 (release v1.5: 525
  measurements, doi:10.5281/zenodo.24222265)" (U4; RELEASE constant in build.py).
- A couple whose ★ row is hidden by the active filters marks its substitute
  row "★ <value> hidden by filter" (click opens the starred row) (U5).
- Internal workflow references (CR/PR IDs, file and column names) moved out of
  the default-open verification panel into the collapsed "Curation trail"
  (recommendation reasons and conditions notes shown there verbatim) (U7, render part).
- σ row relabelled "σ, published (quantity as stated in the source; see
  conditions)"; a missing σ now renders "uncertainty not reported in the
  source" (U8, label part; the BDFE-0499 value check is H99).
- Square scheme: stored legs that are Hess-composed (flag hess:<leg>) get
  their own dotted style and legend entry; wider margins and two-line vertical
  labels end the clipped "(derived, sum only)" text; sum-constraint and
  diagonal labels carry kcal/mol (U9).
- CSV export: a "column list & constants" disclosure documents every export
  column and the per-solvent C_G / ΔG°f(H•) / C_Hyd values (U10).
- Empty search shows guidance instead of a bare empty table, and an open
  verification panel closes when its entry leaves the filtered set (U11).
- Permalink link labelled; E° and pKa table headers explain their semantics,
  back-calculated pKa values render italic with a tooltip; calculator formats
  negative potentials in parentheses and states error propagation into the
  solved quantity; horizontal overflow of wide panels contained; header now
  says stored values are recomputed live as a consistency check; complete
  flag-gloss list (U13–U19).
- Units rule (CR-2026-11-16-units): every displayed value carries its unit —
  worked-equation stored/Δ values and coefficient units, BDFE-input label
  follows the active energy unit, square-scheme diagonals in kcal/mol;
  datapackage.json now has a `unit` for every numeric field; README column
  table extended to all 30 columns with units.
- Verification ledger: extraction_route strings rewritten in plain reader
  language ("extracted from PDF tables", "extracted from SI spreadsheet
  (xlsx)" …) — provenance content unchanged (Carsten 2026-11-14).
- jsdom gate 91 → 112 assertions (typed pair lookup, candidate list, ★-hidden
  marker, jargon scrub, composed-leg style, empty state, stamp, units,
  datapackage units).

#### v1.5 DOI references (PR #62)
- Zenodo archived the v1.5 release: version DOI 10.5281/zenodo.24222265
  (minted 2026-11-14). Footer, README and CITATION.cff now cite it; this
  commit is the citable v1.5 state for testers.

#### Header wording (PR #61)
- Headline gains "database"; sub-line: "(BDFEs)" spelled out, "standard redox
  potential" before E deg; <title> matches. Carsten's reviewed text 2026-11-14.
  UI wording only - the v1.5 tag (7da97ac) and data are unchanged.


All star (recommendation) moves and releases are recorded here, newest first.

## v1.5 — 2026-11-14

**Data scope (freeze at PR #58): 525 measurements / 509 couples, 30 columns, 10
classes.** Scope sentence: v1.4.1 plus the complete TMH primary campaign (P3,
P4, P5, citation-chase round 2a — all Wiedner/Morris-derived hydrides that
close a BDFE, primary-verified), the first MOH rows (Warren 2010 Table 21
gap-fill), the origin provenance layer, the square-scheme view, ladder
tickboxes + archetype anchors, the verification ledger and the v1.5 UI
wording round. Data CRs filed after this freeze target v1.6.

### Catch-up: validator hardening + line endings + F10 convention (PR #59)
- Stress F7 (M1-M7) in validate.py: method whitelist (hard), method=hyd
  requires hydricity_kcal (hard), clean per-row errors for non-numeric
  fields instead of tracebacks (hard), soft warnings for hydricity cycles
  on CHyd-less solvents and for limit flags without conditions text (4
  pre-existing Agarwal-era limit rows now warn, documented). Mutation gate
  9 -> 13 cases.
- Permanent jsdom specs from the stress report: CPL-0460 three-method panel
  (sq/hyd/OCP + discordant reason) and the 5-digit-permalink boot guard.
  Gate 89 -> 91.
- F8: .gitattributes normalizes all CSVs to LF (ends the analysis.csv
  line-ending churn).
- F10: convention recorded in CONTRIBUTING - a primary's own in-paper
  derived pKa stays unflagged; hess:* is for PCETbase-composed legs.
- No data rows touched (v1.5 data freeze at 525/509).

### MOH campaign P1: class moh + first MeOH rows (PR #58)
- New class moh (metal-oxo/hydroxo/aqua O-H couples) with its own chip
  "metal oxo/hydroxo (M-O-H)"; datapackage class enum extended (also adds the
  previously missing tmh value). Existing metal-3d/metal-4d5d rows untouched.
- 2 rows (BDFE-0524/0525), the Warren 2010 Table 21 entries Agarwal 2022
  dropped: (Py5)FeII(MeOH)2+ (first MeOH rows, BDFE 78.6; the review's
  bracketed pKa_a fails Hess closure - source-inconsistency candidate #17)
  and [(LD)FeIIIOH]- (Borovik FeIII-OH/FeIV-O, DMSO, BDFE 110.1 - among the
  strongest O-H bonds stored). Both approx + sigma + check-src; BDFEs
  recomputed with corrected CG, never copied from the 2010 review.
- build.py/validate.py: the ledger-staleness check is now skipped during the
  build's inner validate run (PCETBASE_BUILDING=1) and enforced standalone,
  fixing a build abort on any data change after PR #56.
- 525 measurements / 509 couples; jsdom baselines bumped (chips 10).

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
