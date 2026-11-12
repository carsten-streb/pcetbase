# Contributing to PCETbase

PCETbase stores PCET thermochemistry at two levels:

- **Measurement** — one row in `data/data.csv` per independent literature determination. Identified by `entry_id` (`BDFE-NNNN`). Measurement rows are immutable: they are never deleted and never edited except to correct transcription errors against the cited source. Superseded values stay in the database.
- **Couple** — one row in `data/couples.csv` per compound/partner/solvent combination. Identified by `couple_id` (`CPL-NNNN`). The couple carries the alias list used by search, the one-line justification of the current recommendation, and the `discordant` marker.

The website and the default CSV export show one value per couple: the **recommended (★) measurement**. All other measurements of that couple remain visible behind the entry.

## Adding a measurement

1. Fork, then add one row to `data/data.csv` with a fresh `entry_id` (next free number; IDs are never reused).
2. Required fields: `compound`, `solvent`, `bond`, `class`, the measured quantities (`E_raw` with `E_raw_ref`, and/or `pKa_a`/`pKa_b`, and/or `BDFE_pub`), `method`, `doi`, `year`, `couple_id`, and `flags` where any caveat in the source applies.
3. Strongly encouraged: `sigma_BDFE` (published uncertainty in kcal/mol; if the source gives none, leave empty), `T_K`, and `conditions` (electrolyte, ionic strength, pH convention for aqueous entries). Do not assume 298 K; state what the paper states.
4. If the couple is new, add its row to `data/couples.csv` (next free `couple_id`) including at least one alias if the compound has a common trivial name. `python migrate_couples.py` does both steps automatically.
5. Run `python build.py` locally; the same validation runs in CI on every pull request. PRs that fail validation are not reviewed.
6. Values must come from the cited primary source. A PR adding a measurement **never changes a star** — recommendation changes are a separate PR type (below). (Automatic rule-1/2 star assignment by `build.py` on the new data is expected and exempt.)

## Selection rules for the recommended value

Applied in order; rules 1–2 are deterministic and implemented in `build.py` (`recommended = auto`); rules 3–4 are curator judgment recorded as manual `recommended = 1` / `0` plus a `recommended_reason` on the couple.

1. **Method hierarchy.** Direct equilibration against an anchored standard (`equil`) > square scheme from measured E° + pKa (`sq`) > hydricity closure from an independently measured dG(H-) plus potentials (`hyd`; one extra potential and the CHyd constant accumulate uncertainty relative to sq) > open-circuit potentiometry (`OCP`) > Hess-cycle construction (`hess:*` flags) > computed/estimated values. A `hess:*` flag on a `hyd` row marks a derived leg (e.g. a back-calculated pKa) and does not demote the complete hydricity cycle.
2. **Concordance.** Independent measurements agreeing within combined uncertainty are averaged; the mean is stored as its own measurement row with flag `avg` and the constituent `entry_id`s in `refs`, and receives the star.
3. **Supersession.** A newer measurement displaces the star only with a stated reason (e.g. "corrects junction potential in BDFE-0123"), recorded in `recommended_reason`.
4. **Discord.** If measurements disagree beyond ~2 kcal/mol without resolution, the methodologically stronger value is starred, `discordant = 1` is set on the couple, and the spread is displayed.

A single measurement of a couple is trivially its recommended value (rule 1 applied to a set of one).

## Who may move a star

**Principle: stars are moved by argument recorded in public, not by authority.** The curator's role is to apply the written rules above; any star whose `recommended_reason` cannot be reconstructed from those rules is a bug and may be reported as one.

- Anyone may **propose** a recommendation change by opening an issue or a PR labeled `recommendation-change`. The PR must change only the `recommended` fields and `recommended_reason`, and must state which selection rule it applies.
- Only **named curators** (listed below) may merge a `recommendation-change` PR.
- Judgment-call changes (rules 3–4) stay open for a **two-week comment window** before merge. Mechanical applications of rules 1–2 (e.g. a newly added equilibration measurement outranking a Hess-derived star) are routine curation and may be merged immediately.
- **Four-eyes rule** (once more than one curator is named): one curator proposes or endorses, a different curator merges.
- **Conflict of interest:** a curator does not adjudicate a star that touches a measurement from their own group; a disinterested curator decides. Authors of affected measurements are notified on the PR and may argue their case, but hold no veto.
- Every star move appears in `CHANGELOG.md`. Each Zenodo release freezes the full set of recommendations, so a citation of "PCETbase vX.Y" refers to a defined set of starred values even if a star moves later.

### Curators

| Name | Affiliation | Scope note |
|---|---|---|
| Carsten Streb | JGU Mainz | maintainer; recused from stars touching Streb-group POM measurements once a second curator is named |

## Citing

Cite the database release (see `CITATION.cff` / Zenodo DOI) **and** the primary source of every individual value used quantitatively. The `doi` and `refs` fields exist so that this is a copy-paste operation.
