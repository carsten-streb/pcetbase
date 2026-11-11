#!/usr/bin/env python3
"""Validation of data.csv and couples.csv.

Soft (informational, reviewed by eye): arithmetic closure of eq 18 and eq 10
(Agarwal et al. 2022) beyond thresholds.
Hard (exit 1, fails CI and aborts build.py): schema/structure errors —
missing or unknown couple_id (FK), duplicate or malformed couple_id, bad
bond/discordant values, manual star without recommended_reason on the couple,
multiple stars in one couple.
"""
import csv, hashlib, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
BONDS = {"O-H", "N-H", "S-H", "C-H", "M-H", "X-H"}

def constants_version():
    """Short content hash of constants.csv: a constants update changes every
    row of derived/analysis.csv visibly."""
    with open(os.path.join(HERE, "data", "constants.csv"), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]

def write_derived(rows, resid18, resid10):
    """Canonical derived table (CR-2026-11-11-derived-analysis-table):
    one row per data.csv entry; eq 18/eq 10 residuals (calc - stored,
    kcal/mol) as used by the manuscript's consistency analyses."""
    os.makedirs(os.path.join(HERE, "derived"), exist_ok=True)
    cver = constants_version()
    path = os.path.join(HERE, "derived", "analysis.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["entry_id", "compound", "couple_id", "class", "solvent",
                    "method", "flags", "recommended",
                    "eq18_residual_kcal", "eq10_residual_kcal",
                    "constants_version"])
        for r in rows:
            e18 = resid18.get(r["entry_id"], "")
            e10 = resid10.get(r["entry_id"], "")
            w.writerow([r["entry_id"], r["compound"], r.get("couple_id", ""),
                        r["class"], r["solvent"], r["method"], r["flags"],
                        r.get("recommended", ""),
                        f"{e18:.3f}" if e18 != "" else "",
                        f"{e10:.3f}" if e10 != "" else "", cver])
    return path

def load_constants():
    dgh, cg = {}, {}
    with open(os.path.join(HERE, "data", "constants.csv")) as f:
        for r in csv.DictReader(f):
            if r["key"] == "dGfH": dgh[r["solvent"]] = float(r["value_kcal_or_V"])
            if r["key"] == "CG":   cg[r["solvent"]]  = float(r["value_kcal_or_V"])
    return dgh, cg

def validate_couples(rows):
    """Hard structural checks; returns list of error strings."""
    errors = []
    # F1: entry_id unique (datapackage primaryKey; migrate aborts on it, but
    # migrate does not run on data-only PRs - enforce here for CI)
    seen_eid = {}
    for i, r in enumerate(rows):
        eid = r.get("entry_id", "")
        if not eid:
            errors.append(f"data.csv row {i+2}: empty entry_id")
        elif eid in seen_eid:
            errors.append(f"data.csv: duplicate entry_id '{eid}' (rows {seen_eid[eid]+2} and {i+2})")
        else:
            seen_eid[eid] = i
    # F7: BDFE required and numeric unless the row is flagged ref-conv-missing
    for r in rows:
        if "ref-conv-missing" in r.get("flags", ""):
            continue
        try:
            float(r["BDFE"])
        except (ValueError, KeyError):
            errors.append(f"data.csv {r.get('entry_id','?')}: BDFE empty or non-numeric ('{r.get('BDFE','')}') and not flagged ref-conv-missing")
    cpath = os.path.join(HERE, "data", "couples.csv")
    if not os.path.exists(cpath):
        return ["data/couples.csv missing — run 'python migrate_couples.py'"]
    couples = list(csv.DictReader(open(cpath, newline="", encoding="utf-8")))
    seen = set()
    for c in couples:
        cid = c["couple_id"]
        if not re.fullmatch(r"CPL-[0-9]{4}", cid):
            errors.append(f"couples.csv: malformed couple_id '{cid}'")
        if cid in seen:
            errors.append(f"couples.csv: duplicate couple_id '{cid}'")
        seen.add(cid)
        if c["bond"] and c["bond"] not in BONDS:
            errors.append(f"couples.csv {cid}: bond '{c['bond']}' not in {sorted(BONDS)}")
        if c["discordant"] not in ("0", "1"):
            errors.append(f"couples.csv {cid}: discordant must be 0 or 1, got '{c['discordant']}'")
    # F2: (compound, partner, solvent) unique across couples - a duplicate key
    # silently splits one couple into two (the PR-#3 class of error)
    seen_key = {}
    for c in couples:
        k = (c["compound"], c["partner"], c["solvent"])
        if k in seen_key:
            errors.append(f"couples.csv: duplicate couple key {k} under '{seen_key[k]}' and '{c['couple_id']}'")
        else:
            seen_key[k] = c["couple_id"]
    cmap = {c["couple_id"]: c for c in couples}
    by_couple = {}
    for r in rows:
        cid = r.get("couple_id", "")
        if not cid:
            errors.append(f"data.csv {r['entry_id']}: empty couple_id — run 'python migrate_couples.py'")
            continue
        if cid not in cmap:
            errors.append(f"data.csv {r['entry_id']}: unknown couple_id '{cid}'")
            continue
        by_couple.setdefault(cid, []).append(r)
    for cid, rs in by_couple.items():
        stars = [r for r in rs if r.get("recommended") in ("1", "auto")]
        manual = [r for r in rs if r.get("recommended") in ("1", "0")]
        if len(stars) > 1:
            errors.append(f"{cid}: MULTIPLE STARS ({', '.join(r['entry_id'] for r in stars)}) — fix")
        if manual and not cmap[cid]["recommended_reason"].strip():
            errors.append(f"{cid}: manual recommended=1/0 set but couples.csv recommended_reason is empty")
    print(f"couples.csv: {len(couples)} couples | data rows linked: {sum(len(v) for v in by_couple.values())}")
    return errors

def main():
    dgh, cg = load_constants()
    rows = list(csv.DictReader(open(os.path.join(HERE, "data", "data.csv"))))
    n_eq18 = n_eq10 = 0
    flags18, flags10 = [], []
    resid18, resid10 = {}, {}
    for r in rows:
        name = f'{r["compound"]}{"/"+r["partner"] if r["partner"] else ""} ({r["solvent"]}, {r["table"]})'
        soft = any(k in r["flags"] for k in ("limit", "approx", "lowprec", "check-src", "dmso-unc"))
        # eq 18: BDFE = 23.06*E(V vs H2) + dGfH
        if r["E_H2"] and r["BDFE"] and r["solvent"] in dgh:
            n_eq18 += 1
            calc = 23.06*float(r["E_H2"]) + dgh[r["solvent"]]
            d = calc - float(r["BDFE"])
            resid18[r["entry_id"]] = d
            if abs(d) > 0.3:
                flags18.append((name, float(r["BDFE"]), round(calc,2), round(d,2), "soft" if soft else "CHECK"))
        # eq 10 cross-check, both square-scheme diagonals; a row passes if either closes
        if r["BDFE"] and r["solvent"] in cg:
            devs = []
            if r["E_a"] and r["pKa_b"]:
                devs.append(23.06*float(r["E_a"]) + 1.37*float(r["pKa_b"]) + cg[r["solvent"]] - float(r["BDFE"]))
            if r["E_b"] and r["pKa_a"]:
                devs.append(23.06*float(r["E_b"]) + 1.37*float(r["pKa_a"]) + cg[r["solvent"]] - float(r["BDFE"]))
            if devs:
                n_eq10 += 1
                d = min(devs, key=abs)
                resid10[r["entry_id"]] = d
                if abs(d) > 0.5:
                    flags10.append((name, float(r["BDFE"]), round(float(r["BDFE"])+d,2), round(d,2), "soft" if soft else "CHECK"))
    dpath = write_derived(rows, resid18, resid10)
    print(f"rows: {len(rows)} | eq18 checks: {n_eq18} | eq10 cross-checks: {n_eq10} | derived table: {dpath}")
    print(f"\neq18 deviations > 0.3 kcal/mol: {len(flags18)}")
    for f in flags18: print("  ", f)
    print(f"\neq10 deviations > 0.5 kcal/mol: {len(flags10)}")
    for f in flags10: print("  ", f)
    # multi-source couples, grouped by couple_id
    from collections import defaultdict
    grp = defaultdict(list)
    for r in rows:
        grp[r.get("couple_id") or (r["compound"].lower(), r["partner"].lower(), r["solvent"])].append(r)
    dups = {k: v for k, v in grp.items() if len(v) > 1}
    if dups:
        print(f"\nmulti-source couples: {len(dups)}")
        for k, rs in sorted(dups.items(), key=lambda kv: str(kv[0])):
            recs = [r for r in rs if r.get("recommended") in ("1", "auto")]
            suppressed = [r for r in rs if r.get("recommended") == "0"]
            if len(recs) == 1:
                mark = "ok (" + ("manual" if recs[0]["recommended"] == "1" else "auto") + ")"
            elif suppressed and not recs:
                mark = "suppressed (manual)"
            elif not recs:
                mark = "NO STAR - conflict >0.5 kcal/mol or policy gap, resolve manually"
            else:
                mark = "MULTIPLE STARS - fix"
            print(f"   {rs[0]['compound']} / {rs[0]['solvent']}: {len(rs)} entries — {mark}")
    print("\n--- structural checks (hard) ---")
    errors = validate_couples(rows)
    if errors:
        print(f"HARD ERRORS: {len(errors)}")
        for e in errors: print("  ", e)
        return 1
    print("structural checks OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
