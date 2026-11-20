#!/usr/bin/env python3
"""Build index.html from template.html by embedding data/data.csv and data/constants.csv.
Run after any edit to the CSVs:  python build.py
It first runs validate.py: flagged closure deviations are printed for review;
hard structural errors (schema/FK/star integrity) and closure deviations beyond
threshold without an excusing flag abort the build. CI runs the
same validate.py as the PR gate.
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))

def esc(t):  # escape for JS template literal
    return t.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

# Method hierarchy for auto-recommendation (CONTRIBUTING selection rule 1):
# direct equilibration > square scheme > hydricity closure > open-circuit
# potentiometry > Hess-cycle construction > computed/derived/tabulated values.
# hyd sits below sq (one extra potential + the CHyd constant accumulate
# uncertainty) and is tested before the hess-flag demotion, so hess:pKa_b
# on a hyd row marks the derived leg without demoting the complete cycle.
def method_rank(method, flags):
    if method == "equil": return 6
    if method == "sq":    return 5
    if method == "hyd":   return 4
    if method == "OCP":   return 3
    if method == "hess":  return 2
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
         (equil > sq > hyd > OCP > hess > computed/tabulated; see method_rank);
         BDFE spread among candidates > 0.5 kcal/mol -> no star (conflict,
         reported by validate.py, resolve manually);
         else newest year wins (tie -> most complete square scheme, then first).
    Winner gets recommended='auto'. Idempotent: all 'auto' cleared first.
    Supersession and discord stay manual (recommended=1/0 + recommended_reason
    in couples.csv). discordant = 1 is never written by this code: a curator sets
    it in couples.csv with a recorded reason (cross-closure sq vs hyd disagreement
    of ~1 kcal/mol or more, or independent values ~2 kcal/mol or more apart;
    CONTRIBUTING rule 4); the star then stays with the automatic hierarchy unless
    the curator freezes it manually."""
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
        w = _csv.writer(f, lineterminator="\n"); w.writerow(head); w.writerows(rows)  # O1: LF, as committed
    print(f"auto-recommendation: {n_auto} starred, {n_conflict} conflict groups (no star), {n_manual} manual-override groups")


def write_verification():
    """derived/verification.csv (CR-2026-11-13-verification-ledger): one row per
    entry_id recording how the value was obtained and checked. Provenance from
    data/provenance_batches.csv (ID-range batch map) + data/provenance_overrides.csv
    (per-row exceptions); residuals copied from derived/analysis.csv."""
    import csv
    data = list(csv.DictReader(open(os.path.join(HERE, "data", "data.csv"), encoding="utf-8")))
    couples = {c["couple_id"]: c for c in csv.DictReader(open(os.path.join(HERE, "data", "couples.csv"), encoding="utf-8"))}
    analysis = {a["entry_id"]: a for a in csv.DictReader(open(os.path.join(HERE, "derived", "analysis.csv"), encoding="utf-8"))}
    batches = list(csv.DictReader(open(os.path.join(HERE, "data", "provenance_batches.csv"), encoding="utf-8")))
    ov = {}
    for o in csv.DictReader(open(os.path.join(HERE, "data", "provenance_overrides.csv"), encoding="utf-8")):
        ov.setdefault(o["entry_id"], {})[o["field"]] = o["value"]
    members = {}
    for r in data:
        members[r["couple_id"]] = members.get(r["couple_id"], 0) + 1
    def batch_of(eid):
        n = int(eid.split("-")[1])
        for b in batches:
            if int(b["range_start"].split("-")[1]) <= n <= int(b["range_end"].split("-")[1]):
                return b
        raise SystemExit(f"verification ledger: {eid} not covered by data/provenance_batches.csv")
    out = []
    for r in data:
        eid = r["entry_id"]; b = batch_of(eid); o = ov.get(eid, {})
        a = analysis.get(eid, {})
        e18, e10, ehy = a.get("eq18_residual_kcal",""), a.get("eq10_residual_kcal",""), a.get("hyd_residual_kcal","")
        e10o = a.get("eq10_residual_other_kcal", "")  # EP-02: second diagonal, where both are stored
        checks = [n for n,v in (("eq18",e18),("eq10",e10),("hyd",ehy)) if v != ""]
        # EP-04 (M-07): a row that stores no E or pKa leg can only be checked for the
        # consistency of its copied E(V vs H2) and BDFE ("copy-consistency")
        legless = not any(r.get(k) for k in ("E_a", "E_b", "E_c", "pKa_a", "pKa_b"))
        if legless and checks == ["eq18"]:
            checks = ["eq18 copy-consistency"]
        soft = ((e18 and abs(float(e18)) > 0.3) or (e10 and abs(float(e10)) > 0.5)
                or (e10o and abs(float(e10o)) > 0.5) or (ehy and abs(float(ehy)) > 0.5))
        outcome = ("soft" if soft else "pass") if checks else "n/a"
        loc = b["source_locator"]
        if "Agarwal" in loc and r.get("table") and r["table"] != "EXT":
            loc = f"Agarwal 2022 {r['table']}"
        delta = ""
        if r.get("BDFE_pub"):
            try: delta = f"{float(r['BDFE']) - float(r['BDFE_pub']):+.1f}"
            except ValueError: pass
        cross = []
        if members.get(r["couple_id"], 1) > 1:
            c = couples.get(r["couple_id"], {})
            cross.append(f"multi-member couple {r['couple_id']} ({members[r['couple_id']]} entries"
                         + (", discordant" if c.get("discordant") == "1" else "") + ")")
        if o.get("cross_checks"): cross.append(o["cross_checks"])
        pv = o.get("primary_verified", b["primary_verified"])
        summary = (f"{b['source_type']} ({loc}), {b['extraction_route']}; primary-verified: {pv}; "
                   + (f"closes by {', '.join(checks)} ({', '.join(f'{c} {v}' for c,v in (('eq18',e18),('eq10',e10 + (f' / other diagonal {e10o}' if e10o else '')),('hyd',ehy)) if v)}) - {outcome}"
                      if checks else ("closures involve bounds only (indeterminate or not informative; see the panel)"
                                      if r.get("bounds") else "no closure applicable"))
                   + (f"; BDFE vs published: {delta}" if delta else "")
                   + (f"; {' / '.join(cross)}" if cross else "")
                   + (f"; spot-check: {o['spot_check']}" if o.get("spot_check") else "")
                   + (f"; flags: {r['flags']}" if r.get("flags") else ""))
        out.append({
            "entry_id": eid, "couple_id": r["couple_id"], "compound": r["compound"],
            "solvent": r["solvent"], "class": r["class"],
            "source_type": b["source_type"], "source_locator": loc,
            "extraction_route": b["extraction_route"], "primary_verified": pv,
            "introduced_in": b["introduced_in"],
            "last_modified_in": o.get("last_modified_in", ""),
            "checks_run": ";".join(checks), "eq18_res": e18, "eq10_res": e10, "hyd_res": ehy,
            "check_outcome": outcome, "bdfe_pub_delta": delta,
            "cross_checks": " / ".join(cross), "spot_check": o.get("spot_check", ""),
            "open_flags": r.get("flags", ""), "summary": summary,
            "eq10_res_other": e10o,
        })
    path = os.path.join(HERE, "derived", "verification.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(out)
    print(f"wrote derived/verification.csv ({len(out)} rows)")

def main():
    print("--- auto-recommendation ---")
    autorecommend()
    print("--- validation ---")
    env = dict(os.environ, PCETBASE_BUILDING="1")  # ledger regenerated below
    rc = subprocess.run([sys.executable, os.path.join(HERE, "validate.py")], env=env).returncode
    if rc != 0:
        sys.exit("build aborted: hard validation errors (see report above)")
    write_verification()
    print("--- build ---")
    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    data = open(os.path.join(HERE, "data", "data.csv"), encoding="utf-8").read()
    const = open(os.path.join(HERE, "data", "constants.csv"), encoding="utf-8").read()
    coup = open(os.path.join(HERE, "data", "couples.csv"), encoding="utf-8").read()
    verif = open(os.path.join(HERE, "derived", "verification.csv"), encoding="utf-8").read()
    # deterministic staleness stamp (F8): entry count + release version + data hash
    # (no wall-clock date - the build must stay byte-reproducible for CI's sync check)
    # U4 (CR-2026-11-14-usability-test): name the release only when the data match it;
    # otherwise say "development state after vX". RELEASE is updated by each release-prep PR.
    import hashlib, re as _re
    # EP-13 (M-58): the stamp keys on the data hash and a code hash (template.html),
    # not on version + row count; code SHAs cannot be embedded reproducibly (CI
    # rebuilds on a merge commit), so the code is identified by its content hash.
    RELEASE = {"version": "1.7", "measurements": 547, "doi": "minted on Zenodo after archiving",  # DOI-reference PR fills the DOI
               "data_hash": "3afe3771", "code_hash": "79fa3ea6"}
    n_rows = data.count("\n") - 1
    m = _re.search(r'version: "([^"]+)"', open(os.path.join(HERE, "CITATION.cff"), encoding="utf-8").read())
    ver = m.group(1) if m else "?"
    h = hashlib.sha256(data.encode()).hexdigest()[:8]
    ch = hashlib.sha256(tpl.encode()).hexdigest()[:8]
    if h == RELEASE["data_hash"] and ch == RELEASE["code_hash"]:
        stamp = f"{n_rows} measurements, release v{RELEASE['version']}, data {h}"
    elif h == RELEASE["data_hash"]:
        stamp = f"{n_rows} measurements, release v{RELEASE['version']} data {h}, code changed since the release (code {ch})"
    else:
        stamp = (f"{n_rows} measurements — development state after v{RELEASE['version']} "
                 f"(release v{RELEASE['version']}: {RELEASE['measurements']} measurements, "
                 f"doi:{RELEASE['doi']}), data {h}, code {ch}")
    _legless = [line for line in __import__("csv").DictReader(data.splitlines())
                if not any(line.get(k) for k in ("E_a", "E_b", "E_c", "pKa_a", "pKa_b"))]
    n_legless = len(_legless)
    # review-pr-81 N1: legless rows stored as bounds get no copy-consistency check
    n_legless_bound = sum(1 for line in _legless if line.get("bounds"))
    out = (tpl.replace("__DATA_CSV__", esc(data)).replace("__CONST_CSV__", esc(const))
              .replace("__COUPLES_CSV__", esc(coup)).replace("__VERIF_CSV__", esc(verif)).replace("__BUILD_STAMP__", stamp)
              .replace("__N_LEGLESS__", str(n_legless))
              .replace("__N_LEGLESS_VAL__", str(n_legless - n_legless_bound))
              .replace("__N_LEGLESS_BOUND__", str(n_legless_bound)))
    open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(out)
    print(f"wrote index.html ({len(out)//1024} kB)")

if __name__ == "__main__":
    main()
