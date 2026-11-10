#!/usr/bin/env python3
"""Arithmetic validation of data.csv against eq 18 and eq 10 (Agarwal et al. 2022)."""
import csv, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))

def load_constants():
    dgh, cg = {}, {}
    with open(os.path.join(HERE, "data", "constants.csv")) as f:
        for r in csv.DictReader(f):
            if r["key"] == "dGfH": dgh[r["solvent"]] = float(r["value_kcal_or_V"])
            if r["key"] == "CG":   cg[r["solvent"]]  = float(r["value_kcal_or_V"])
    return dgh, cg

def main():
    dgh, cg = load_constants()
    rows = list(csv.DictReader(open(os.path.join(HERE, "data", "data.csv"))))
    n_eq18 = n_eq10 = 0
    flags18, flags10 = [], []
    for r in rows:
        name = f'{r["compound"]}{"/"+r["partner"] if r["partner"] else ""} ({r["solvent"]}, {r["table"]})'
        soft = any(k in r["flags"] for k in ("limit", "approx", "lowprec", "check-src", "dmso-unc"))
        # eq 18: BDFE = 23.06*E(V vs H2) + dGfH
        if r["E_H2"] and r["BDFE"] and r["solvent"] in dgh:
            n_eq18 += 1
            calc = 23.06*float(r["E_H2"]) + dgh[r["solvent"]]
            d = calc - float(r["BDFE"])
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
                if abs(d) > 0.5:
                    flags10.append((name, float(r["BDFE"]), round(float(r["BDFE"])+d,2), round(d,2), "soft" if soft else "CHECK"))
    print(f"rows: {len(rows)} | eq18 checks: {n_eq18} | eq10 cross-checks: {n_eq10}")
    print(f"\neq18 deviations > 0.3 kcal/mol: {len(flags18)}")
    for f in flags18: print("  ", f)
    print(f"\neq10 deviations > 0.5 kcal/mol: {len(flags10)}")
    for f in flags10: print("  ", f)
    # multi-source groups: same compound+solvent more than once
    from collections import Counter
    key = Counter((r["compound"].lower(), r["partner"].lower(), r["solvent"]) for r in rows)
    dups = {k: n for k, n in key.items() if n > 1}
    if dups:
        print(f"\nmulti-source couples (same compound+solvent): {len(dups)}")
        for (c, p, s), n in sorted(dups.items()):
            recs = [r for r in rows if r["compound"].lower() == c and r["partner"].lower() == p and r["solvent"] == s and r.get("recommended") in ("1", "auto")]
            suppressed = [r for r in rows if r["compound"].lower() == c and r["partner"].lower() == p and r["solvent"] == s and r.get("recommended") == "0"]
            if len(recs) == 1:
                mark = "ok (" + ("manual" if recs[0]["recommended"] == "1" else "auto") + ")"
            elif suppressed and not recs:
                mark = "suppressed (manual)"
            elif not recs:
                mark = "NO STAR - conflict >0.5 kcal/mol or policy gap, resolve manually"
            else:
                mark = "MULTIPLE STARS - fix"
            print(f"   {c} / {s}: {n} entries — {mark}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
