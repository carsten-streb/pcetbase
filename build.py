#!/usr/bin/env python3
"""Build index.html from template.html by embedding data/data.csv and data/constants.csv.
Run after any edit to the CSVs:  python build.py
It first runs validate.py and refuses to build on hard validation errors? No —
it prints the validation report and always builds; review the report yourself.
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))

def esc(t):  # escape for JS template literal
    return t.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

def autorecommend():
    """Auto-recommendation per policy (status doc, decided 2026-11-11):
    groups = same compound+partner+solvent with >1 entries.
    Manual override: recommended '1' (star) or '0' (suppress) on any row -> group untouched.
    Tier 1: primary entries (method set or 'recomputed' flag) beat tabulated.
    Within the winning tier: BDFE spread > 0.5 kcal/mol -> no star (resolve manually,
    reported by validate.py); else newest year wins; tie -> most complete square scheme,
    then first occurrence. Winner gets recommended='auto'. Idempotent: all 'auto' cleared first."""
    import csv as _csv
    from collections import defaultdict
    path = os.path.join(HERE, "data", "data.csv")
    with open(path, newline="", encoding="utf-8") as f:
        rd = _csv.reader(f); head = next(rd); rows = [r for r in rd]
    col = {h: i for i, h in enumerate(head)}
    iRec, iY = col["recommended"], col["year"]
    for r in rows:
        if r[iRec] == "auto": r[iRec] = ""
    groups = defaultdict(list)
    for idx, r in enumerate(rows):
        k = (r[col["compound"]].lower(), r[col["partner"]].lower(), r[col["solvent"]])
        groups[k].append(idx)
    n_auto = n_conflict = n_manual = 0
    for k, idxs in groups.items():
        if len(idxs) < 2: continue
        if any(rows[i][iRec] in ("1", "0") for i in idxs):
            n_manual += 1; continue
        def is_primary(i):
            return rows[i][col["method"]] != "" or "recomputed" in rows[i][col["flags"]]
        cand = [i for i in idxs if is_primary(i)] or idxs
        vals = [float(rows[i][col["BDFE"]]) for i in cand if rows[i][col["BDFE"]] != ""]
        if vals and max(vals) - min(vals) > 0.5:
            n_conflict += 1; continue
        def completeness(i):
            return sum(1 for c in ("E_a", "E_b", "pKa_a", "pKa_b") if rows[i][col[c]] != "")
        win = sorted(cand, key=lambda i: (-int(rows[i][iY] or 0), -completeness(i), i))[0]
        rows[win][iRec] = "auto"; n_auto += 1
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = _csv.writer(f); w.writerow(head); w.writerows(rows)
    print(f"auto-recommendation: {n_auto} starred, {n_conflict} conflict groups (no star), {n_manual} manual-override groups")

def main():
    print("--- auto-recommendation ---")
    autorecommend()
    print("--- validation ---")
    subprocess.run([sys.executable, os.path.join(HERE, "validate.py")])
    print("--- build ---")
    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    data = open(os.path.join(HERE, "data", "data.csv"), encoding="utf-8").read()
    const = open(os.path.join(HERE, "data", "constants.csv"), encoding="utf-8").read()
    out = tpl.replace("__DATA_CSV__", esc(data)).replace("__CONST_CSV__", esc(const))
    open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(out)
    print(f"wrote index.html ({len(out)//1024} kB)")

if __name__ == "__main__":
    main()
