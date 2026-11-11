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

- eq 18: `BDFE(X–H) = 23.06·E°(V vs H2) + ΔG°f(H•)_solv`
- eq 10 (square scheme): `BDFE = 23.06·E° + 1.37·pKa + CG_solv`

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
| `E_a` | E°(X/X⁻) (V vs Fc⁺/⁰ in organic solvents, vs SHE in water) |
| `E_b` | E°(XH⁺/XH), same scale |
| `pKa_a` | pKa(XH⁺) |
| `pKa_b` | pKa(XH) |
| `E_H2` | canonical E°(V vs H2) |
| `BDFE` | kcal/mol (BDFE_eff for pairs; average over `n_H` H atoms where `avg` flag set) |
| `flags` | semicolon list, see below |
| `refs` | original citation numbers inside the source compilation |
| `n_H` | number of H atoms transferred (1 unless stated) |
| `method` | sq (square scheme), OCP, equil — for primary-literature entries |
| `doi` | primary-source DOI for `EXT` entries (review entries carry the review DOI implicitly) |
| `BDFE_pub` | published BDFE where it differs from the recomputed value |
| `E_raw`, `E_raw_ref` | potential exactly as published + its reference electrode (converted via `constants.csv` offsets) |
| `recommended` | `1` manual star, `0` manual suppress, `auto` assigned by policy (see below) |
| `year` | publication year (review-tabulated rows: compilation year 2022) |
| `entry_id` | stable identifier (BDFE-0001 …), never reused |

Flags: `hess` (value derived by Hess's law in the source), `limit` (inequality bound),
`approx`, `lowprec` (2-significant-figure printed value), `dmso-unc` (larger DMSO
constant uncertainty), `lowT` (−80 °C), `excited` (excited-state potential),
`ox-base`/`red-acid` (effective BDFE of a pair), `recomputed` (BDFE recalculated here
from primary measurables with corrected constants), `avg` (average over n_H transfers),
`mixed-CH-NH`, `derived`, `assumed-dGfH`, `ref-conv` (reference-electrode conversion
applied), `ref-conv-missing` (no verified offset on file; no BDFE computed),
`check-src` (internal inconsistency in the source, detected by validation).

### Recommended values (★)

Where several independent measurements exist for one compound/partner/solvent, all are
kept with their sources; one is starred by a deterministic policy (`autorecommend()` in
`build.py`): entries recomputed from primary measurables beat compilation-tabulated
values; within a tier the newest publication wins; if values within the winning tier
disagree by more than 0.5 kcal/mol nothing is starred and the conflict is reported for
manual resolution. Manual `recommended` entries (1/0) always override the policy.

## Workflow

```
edit data/data.csv  →  python build.py  →  index.html regenerated
```

`build.py` runs, in order: the auto-recommendation policy, the full validation
(every row checked by eq 18 and both eq 10 diagonals against the constants), and the
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
(this release v1.3: [doi:10.5281/zenodo.24137124](https://doi.org/10.5281/zenodo.24137124); all versions: [doi:10.5281/zenodo.24121910](https://doi.org/10.5281/zenodo.24121910)). If you use individual values, please also cite the
primary source given in the entry (`doi` column or the review reference number).

## Provenance statement

This database was compiled with AI assistance (Anthropic Claude) under human direction
and review; every value was validated against its thermochemical cycle, and source
inconsistencies found during compilation are flagged `check-src` rather than silently
corrected.


Cross-solvent pKa comparison: empirical estimator per Kütt et al., EJOC 2021, doi:10.1002/ejoc.202001649 (organic acids only; estimates never stored).
