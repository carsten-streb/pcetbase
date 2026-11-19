# PCETbase — open database of PCET thermochemistry

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24121910.svg)](https://doi.org/10.5281/zenodo.24121910)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Interactive, open database of solution-phase X–H bond dissociation free energies (BDFEs)
and proton-coupled electron transfer (PCET) square-scheme thermochemistry: E°, pKa and
BDFE on self-consistent scales, with per-entry derivation and reference-electrode
provenance, for organic, transition-metal, polyoxometalate (POM) and excited-state couples.

Live app: https://carsten-streb.github.io/pcetbase/ (single self-contained HTML page;
also works offline — just open `index.html`).

## Data model

Canonical value per entry: **E°(V vs H2)** in the stated solvent — the potential of
hydrogenation. Everything else is computed:

- BDFE from the H-atom potential (eq 18 in Agarwal et al. 2022): `BDFE(X–H) = 23.06 kcal/mol/V · E°(V vs H2) + ΔG°f(H•)_solv (kcal/mol)`
- Bordwell equation (square scheme; eq 10 in Agarwal et al. 2022): `BDFE = 23.06 kcal/mol/V · E° + 1.37 kcal/mol · pKa + CG_solv (kcal/mol)`

Constants (ΔG°f(H•), CG, reference-electrode offsets) live in `data/constants.csv`,
each with its literature citation and uncertainty. Values follow Agarwal et al.,
*Chem. Rev.* 2022, 122, 1 (doi:10.1021/acs.chemrev.1c00521) and the correction
doi:10.1021/acs.chemrev.1c00791; pre-correction (2010) constants are never used.

### `data/data.csv` — one row per entry

| column | meaning |
|---|---|
| `table` | source table in the 2022 review (T5–T24), or `EXT` for primary-literature entries |
| `class` | granular compound class (phenol, quinone, aminoxyl, imide, ascorbate, smallOH, nucleoside, nitrogen, amine, arylamine, indole, thiol, CH, nicotinamide, co2, pair, metal-3d, metal-4d5d, pom) |
| `bond` | O-H, N-H, S-H, C-H, M-H, X-H |
| `compound`, `partner` | species; `partner` is the base/acid for oxidant–base / reductant–acid pairs |
| `solvent` | H2O, MeCN, DMSO, DMF, THF, C6H6, CCl4, hexane, toluene, acetone, IPA, gas, … |
| `E_a` | E°(X/X⁻) in V (vs Fc⁺/⁰ in organic solvents, vs SHE in water) |
| `E_b` | E°(XH⁺/XH) in V, same scale |
| `pKa_a` | pKa(XH⁺), unitless |
| `pKa_b` | pKa(XH), unitless |
| `E_H2` | canonical E° in V vs H₂ |
| `BDFE` | in kcal/mol (BDFE_eff for pairs; average over `n_H` H atoms where `avg` flag set) |
| `flags` | semicolon list, see below |
| `refs` | original citation numbers inside the source compilation |
| `n_H` | number of H atoms transferred (1 unless stated) |
| `method` | empty = tabulated (review value); sq (square scheme), hyd (hydricity cycle), OCP (open-circuit potential), equil (equilibrium), hess (Hess combination of measured legs) |
| `doi` | primary-source DOI for `EXT` entries (review entries carry the review DOI implicitly) |
| `BDFE_pub` | published BDFE where it differs from the recomputed value |
| `E_raw`, `E_raw_ref` | potential exactly as published + its reference electrode (converted via `constants.csv` offsets) |
| `E_raw_offset` | E°(Fc⁺/⁰) vs `E_raw_ref` in V as stated by the source itself; used instead of the generic `constants.csv` offset for this row (empty = constants); `conditions` say where the source states it |
| `E_raw_leg` | which stored quantity `E_raw` becomes after conversion: `a` (E_a), `b` (E_b), `c` (E_c), `H2` (E_H2) or `OCP` (open-circuit cell potential of a buffered solution; the buffer pKa is stated in `conditions`); set exactly when `E_raw` is set. `validate.py` checks that the converted value equals the named leg within 0.0005 V and that `ref-conv` is set exactly when `E_raw_ref` is not the solvent's target scale |
| `recommended` | `1` manual star, `0` manual suppress, `auto` assigned by policy (see below) |
| `year` | publication year (review-tabulated rows: compilation year 2022) |
| `entry_id` | stable identifier (BDFE-0001 …), never reused |
| `couple_id` | foreign key to `couples.csv`; groups independent measurements of one couple |
| `sigma_BDFE` | one uncertainty of the stored BDFE in kcal/mol; its kind is recorded in `sigma_type`: `published` (stated, or propagated, by the source authors), `curator-estimate` (estimated by the PCETbase curators for a value they composed or converted where the source states none; documented in `conditions`), `bracket-midpoint` (the stored value is the midpoint of a published bracket and σ covers the bracket). Empty = no uncertainty available; σ is never filled by default per method class |
| `sigma_type` | `published`, `curator-estimate` or `bracket-midpoint` (see `sigma_BDFE`); set exactly when `sigma_BDFE` is set |
| `T_K` | temperature in K (empty = not stated) |
| `conditions` | medium details and caveats, verbatim notes from the source |
| `hydricity_kcal` | hydricity ΔG°(H⁻) in kcal/mol, as published (Wiedner MeCN scale) |
| `E_c` | E°(X⁺/X•) in V on the row's reference scale (hydricity leg) |
| `origin` | exp / comp / mixed; empty = not yet classified |
| `bounds` | inequality bounds as printed in the source: `;`-separated tokens `<field><op>` with field ∈ E_a, E_b, pKa_a, pKa_b, E_H2, BDFE and op ∈ `<`, `>`, `≤`, `≥` (e.g. `E_a<;pKa_b>`); set exactly when the `limit` flag is set. The Explorer shows the operator before the value; the CSV export carries it in `*_rel` columns (ASCII `<`, `>`, `<=`, `>=`) |

Flags: `hess:<leg>` (the named leg is not an independent measurement; obtained from the
other legs by Hess's law, in the source compilation for review-tabulated entries or by
PCETbase for primary-literature entries), `limit` (inequality bound; the bounded fields are in `bounds`),
`approx`, `lowprec` (2-significant-figure printed value), `dmso-unc` (the source or
the curators note a larger uncertainty for this DMSO value; set per row, not on every
DMSO row), `lowT` (measured below room temperature; see `T_K` and `conditions`),
`est-pKa` (pKa estimated or extrapolated in the source), `Ep:<leg>` (the named
potential comes from an irreversible wave, as a peak potential or estimate, or is the
mid-point of a two-electron wave; BDFEs that use it are effective values),
`no-ladder` (BDFE withdrawn from the ladder and from statistics, the row kept for its
other values), `excited` (excited-state potential),
`ox-base`/`red-acid` (effective BDFE of a pair), `recomputed` (BDFE recalculated here
from primary measurables with corrected constants), `avg` (average over n_H transfers;
for n_H = 1 the mean of both closing square-scheme diagonals), `derived-E`
(E°(HQ•/HQ−) derived from the H2Q/Q and HQ•/Q potentials, Agarwal 2022 Table 8 fn c),
`avg-pKa` (pKa averaged over two determinations, Agarwal 2022 Table 18 fn b, c),
`mixed-CH-NH`, `derived`, `assumed-dGfH`, `ref-conv` (reference-electrode conversion
applied), `ref-conv-missing` (no verified offset on file; no BDFE computed),
`check-src` (internal inconsistency in the source, detected by validation).

### Verification ledger

`derived/verification.csv` (build-generated, one row per `entry_id`) records how each
value was obtained and checked: source type and locator, extraction route,
primary-verified status, introducing CR/PR, the closure checks run with their
residuals (copied from `derived/analysis.csv`), cross-checks, independent spot-checks
and a one-line summary. Provenance comes from the hand-maintained batch map
`data/provenance_batches.csv` (one row per contiguous entry-ID range) plus
`data/provenance_overrides.csv` (per-row exceptions). The app's verification panel
shows the record for each entry and offers the ledger as a CSV download. Do not edit
`derived/verification.csv` by hand; edit the two provenance files and rebuild.
Ledger/analysis column names `eq18_residual_kcal` (H-atom-potential closure residual,
kcal/mol) and `eq10_residual_kcal` (Bordwell closure residual, kcal/mol) keep the
source equation numbers of Agarwal et al. 2022 for machine-readability.
`eq10_residual_kcal` is the diagonal closer to the stored BDFE; `eq10_residual_other_kcal`
(ledger: `eq10_res_other`) holds the second diagonal where both are stored.
`derived/analysis.csv` holds equality residuals only: a closure that involves a bound
from `bounds` (indeterminate, not informative or an inequality test) leaves its residual
column empty, and consumers that build statistics should also drop rows flagged
`no-ladder`, as the figure scripts do.

### Recommended values (★)

Where several independent measurements exist for one compound/partner/solvent, all are
kept with their sources and one is starred by the deterministic policy implemented in
`autorecommend()` (`build.py`). The policy (method hierarchy, concordance mean,
spread threshold, manual overrides) is specified once, in
[CONTRIBUTING.md](CONTRIBUTING.md) — that document is normative; this README does not
restate it.

## How the data were curated

PCETbase entries are extracted from the published literature (critical reviews and
primary papers), working from the papers’ tables, text and supporting information.
Each entry stores the primary measurables (potentials with their reference
electrode, pKa values); BDFEs are recomputed from these with one consistent
constant set rather than copied. Every stored value is run through automatic
thermochemical closure checks (Bordwell equation, H-atom potential, hydricity
cycle where applicable) and a structural validation suite; the same checks gate
every change through continuous integration, so a value that does not close
thermochemically cannot enter the database unless a flag documents the deviation. Each entry carries a public
verification record — source, extraction route, whether the primary literature
was page-verified, checks run — shown in its Curation trail and downloadable as
the full verification ledger. All changes enter through reviewed pull requests on
GitHub, and every addition and release is reviewed and approved by a human
curator (C. Streb). Values that could not be fully verified carry explicit flags
rather than silent corrections.

## Workflow

```
edit data/data.csv  →  python build.py  →  index.html regenerated
```

`build.py` runs, in order: the auto-recommendation policy, the full validation
(every row checked by the H-atom-potential closure and by every stored Bordwell diagonal against the constants:
where both diagonals are stored, each must close within 0.5 kcal/mol or the row carries an excusing flag; a
closure that combines an upper and a lower bound from `bounds` is reported as not determinable and not
evaluated), and the
rebuild of the self-contained `index.html` from `template.html`. `validate.py` can be
run alone. Pull requests are gated by the same validation via GitHub Actions: a
contributed value that does not close thermochemically cannot be merged.

## Contributing

Open a pull request editing `data/data.csv` (and `data/constants.csv` for new
constants — page-verified citations required). Please include: primary measurables as
published (`E_raw` + electrode, pKa), solvent, DOI, year, and flags. The CI validation
must pass; entries that only restate a compilation value without primary provenance
will be asked for sources.

## License and citation

Data and code: **CC BY 4.0** (see `LICENSE`). Cite via `CITATION.cff`; archived releases receive DOIs via Zenodo
(this release v1.6: [doi:10.5281/zenodo.24293136](https://doi.org/10.5281/zenodo.24293136); all versions: [doi:10.5281/zenodo.24121910](https://doi.org/10.5281/zenodo.24121910)). If you use individual values, please also cite the
primary source given in the entry (`doi` column or the review reference number).

## Funding

This database is developed as part of the Collaborative Research Center
[SFB 1633 "PCET"](https://uni-goettingen.de/de/683468.html), funded by
Deutsche Forschungsgemeinschaft DFG (grant no: 536858973).

## Provenance statement

This database was compiled with AI assistance (Anthropic Claude) under human direction
and review; every value was validated against its thermochemical cycle, and source
inconsistencies found during compilation are flagged `check-src` rather than silently
corrected.


Cross-solvent pKa comparison: empirical estimator per Kütt et al., EJOC 2021, doi:10.1002/ejoc.202001649 (organic acids only; estimates never stored).
