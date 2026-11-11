#!/usr/bin/env python3
"""PCETbase schema migration: measurement/couple two-layer model.

Run from the repo root AFTER any data additions are committed:
    python migrate_couples.py

What it does (idempotent — safe to rerun whenever rows are added):
  1. Adds columns couple_id, sigma_BDFE, T_K, conditions to data/data.csv
     if missing; never touches existing values.
  2. Creates/updates data/couples.csv: one row per (compound, partner,
     solvent). Existing couple_ids, aliases, recommended_reason and
     discordant values are preserved; new couples get the next free
     CPL-NNNN id (ids are never renumbered or reused).
  3. Verifies foreign-key integrity and prints a summary.

Expected output on success (numbers will grow with the dataset):
    data.csv:    <N> measurements, columns OK
    couples.csv: <M> couples (<k> new)
    FK integrity OK
"""
import csv
import sys
from pathlib import Path

DATA = Path("data/data.csv")
COUPLES = Path("data/couples.csv")
NEW_DATA_COLS = ["couple_id", "sigma_BDFE", "T_K", "conditions"]
COUPLE_COLS = ["couple_id", "compound", "partner", "solvent", "bond",
               "class", "aliases", "recommended_reason", "discordant"]


def main():
    if not DATA.exists():
        sys.exit(f"ERROR: {DATA} not found — run from the repo root.")

    with DATA.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit("ERROR: data.csv is empty.")
    eids = [r["entry_id"] for r in rows]
    dups = {e for e in eids if eids.count(e) > 1}
    if dups:
        sys.exit(f"ERROR: duplicate entry_id in data.csv: {sorted(dups)[:5]} "
                 "— fix before migrating (no files were changed).")

    # Load existing couples.csv if present (preserve everything in it)
    couples = {}
    if COUPLES.exists():
        with COUPLES.open(newline="", encoding="utf-8") as f:
            for c in csv.DictReader(f):
                couples[(c["compound"], c["partner"], c["solvent"])] = c

    used_ids = {c["couple_id"] for c in couples.values()}
    next_n = max((int(i.split("-")[1]) for i in used_ids), default=0) + 1

    new_couples = 0
    for r in rows:
        key = (r["compound"], r.get("partner", ""), r["solvent"])
        if key not in couples:
            cid = f"CPL-{next_n:04d}"
            next_n += 1
            new_couples += 1
            couples[key] = {
                "couple_id": cid, "compound": key[0], "partner": key[1],
                "solvent": key[2], "bond": r.get("bond", ""),
                "class": r.get("class", ""), "aliases": "",
                "recommended_reason": "", "discordant": "0",
            }
        # fill couple_id only if empty; add new columns without clobbering
        if not r.get("couple_id"):
            r["couple_id"] = couples[key]["couple_id"]
        for col in NEW_DATA_COLS[1:]:
            r.setdefault(col, "")

    # stable column order: existing order, then any missing new columns
    fieldnames = list(rows[0].keys())
    for col in NEW_DATA_COLS:
        if col not in fieldnames:
            fieldnames.append(col)

    with DATA.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    with COUPLES.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COUPLE_COLS)
        w.writeheader()
        w.writerows(sorted(couples.values(), key=lambda c: c["couple_id"]))

    # integrity checks
    cids = {c["couple_id"] for c in couples.values()}
    assert len(cids) == len(couples), "duplicate couple_id"
    missing = [r["entry_id"] for r in rows if r["couple_id"] not in cids]
    assert not missing, f"rows with unknown couple_id: {missing[:5]}"

    print(f"data.csv:    {len(rows)} measurements, columns OK")
    print(f"couples.csv: {len(couples)} couples ({new_couples} new)")
    print("FK integrity OK")


if __name__ == "__main__":
    main()
