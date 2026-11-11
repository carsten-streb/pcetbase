#!/usr/bin/env python3
"""Build index.html from template.html by embedding data/data.csv and data/constants.csv.
Run after any edit to the CSVs:  python build.py
It first runs validate.py: soft arithmetic deviations are printed for review,
hard structural errors (schema/FK/star integrity) abort the build. CI runs the
same validate.py as the PR gate.
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))

def esc(t):  # escape for JS template literal
    return t.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

# Method hierarchy for auto-recommendation (CONTRIBUTING selection rule 1):
# direct equilibration > square scheme > open-circuit potentiometry >
# Hess-cycle construction > computed/derived/tabulated values.
def method_rank(method, flags):
    if method == "equil": return 5
    if method == "sq":    return 4
    if method == "OCP":   return 3
    if "hess" in flags:   return 2
    return 1

def autorecommend(data_path=None):
    """Auto-recommendation (deterministic rules only; CONTRIBUTING rules 1-2).
    Groups = rows sharing couple_id (fallback: compound+partner+solvent, lowercased)
    with >1 entries. Manual override (recommended '1' star / '0' suppress) on any
    row freezes the group. Selection within a group:
      a) a concordance-mean row (flag 'avg' AND refs citing BDFE- entry_ids of
         its constituents) gets the star;
      b) else: candidates = rows of the highest method rank present
         (equil > sq > OCP > hess > computed/tabulated);
         BDFE spread among candidates > 0.5 kcal/mol -> no star (conflict,
         reported by validate.py, resolve manually);
         else newest year wins (tie -> most complete square scheme, then first).
    Winner gets recommended='auto'. Idempotent: all 'auto' cleared first.
    Supersession and discord stay manual (recommended=1/0 + recommended_reason
    in couples.csv); never auto-assigned."""
    import csv as _csv
    from collections import defaultdict
    path = data_path or os.path.join(HERE, "data", "data.csv")
    with open(path, newline="", encoding="utf-8") as f:
        rd = _csv.reader(f); head = next(rd); rows = [r for r in rd]
    col = {h: i for i, h in enumerate(head)}
    iRec, iY = col["recommended"], col["year"]
    for r in rows:
        if r[iRec] == "auto": r[iRec] = ""
    groups = defaultdict(list)
    for idx, r in enumerate(rows):
        cid = r[col["couple_id"]] if "couple_id" in col else ""
        k = cid or (r[col["compound"]].lower(), r[col["partner"]].lower(), r[col["solvent"]])
        groups[k].append(idx)
    n_auto = n_conflict = n_manual = 0
    for k, idxs in groups.items():
        if len(idxs) < 2: continue
        if any(rows[i][iRec] in ("1", "0") for i in idxs):
            n_manual += 1; continue
        # a) concordance-mean row: flag 'avg' and refs citing constituent entry_ids
        conc = [i for i in idxs
                if "avg" in rows[i][col["flags"]] and "BDFE-" in rows[i][col["refs"]]]
        if len(conc) == 1:
            rows[conc[0]][iRec] = "auto"; n_auto += 1; continue
        if len(conc) > 1:
            n_conflict += 1; continue  # two mean rows in one couple: fix manually
        # b) method hierarchy
        best = max(method_rank(rows[i][col["method"]], rows[i][col["flags"]]) for i in idxs)
        cand = [i for i in idxs
                if method_rank(rows[i][col["method"]], rows[i][col["flags"]]) == best]
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
    rc = subprocess.run([sys.executable, os.path.join(HERE, "validate.py")]).returncode
    if rc != 0:
        sys.exit("build aborted: hard validation errors (see report above)")
    print("--- build ---")
    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    data = open(os.path.join(HERE, "data", "data.csv"), encoding="utf-8").read()
    const = open(os.path.join(HERE, "data", "constants.csv"), encoding="utf-8").read()
    coup = open(os.path.join(HERE, "data", "couples.csv"), encoding="utf-8").read()
    # deterministic staleness stamp (F8): entry count + release version + data hash
    # (no wall-clock date - the build must stay byte-reproducible for CI's sync check)
    import hashlib, re as _re
    n_rows = data.count("\n") - 1
    m = _re.search(r'version: "([^"]+)"', open(os.path.join(HERE, "CITATION.cff"), encoding="utf-8").read())
    ver = m.group(1) if m else "?"
    stamp = f"{n_rows} measurements, v{ver}, data {hashlib.sha256(data.encode()).hexdigest()[:8]}"
    out = (tpl.replace("__DATA_CSV__", esc(data)).replace("__CONST_CSV__", esc(const))
              .replace("__COUPLES_CSV__", esc(coup)).replace("__BUILD_STAMP__", stamp))
    open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(out)
    print(f"wrote index.html ({len(out)//1024} kB)")

if __name__ == "__main__":
    main()
