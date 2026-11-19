## What this PR changes

- Rows touched (entry_id) and the source of every new or changed value (DOI, table/page):
- Provenance line: source_type / extraction_route / primary_verified
- Does it move a star? (A data PR never does; star changes are a separate `recommendation-change` PR, CONTRIBUTING.md.)

## Checks

- [ ] `python build.py` runs clean and the build leaves no uncommitted change
- [ ] every number carries its unit; potentials name their reference scale
- [ ] new flags are glossed (FLAG_GLOSS in template.html and the README flag list)
- [ ] rule-11 review needed? (schema, validation or rendering change, or ≥ 2 change requests)
