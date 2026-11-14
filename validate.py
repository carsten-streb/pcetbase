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

def write_derived(rows, resid18, resid10, residhyd=None):
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
                    "hyd_residual_kcal", "constants_version"])
        for r in rows:
            e18 = resid18.get(r["entry_id"], "")
            e10 = resid10.get(r["entry_id"], "")
            ehy = (residhyd or {}).get(r["entry_id"], "")
            w.writerow([r["entry_id"], r["compound"], r.get("couple_id", ""),
                        r["class"], r["solvent"], r["method"], r["flags"],
                        r.get("recommended", ""),
                        f"{e18:.3f}" if e18 != "" else "",
                        f"{e10:.3f}" if e10 != "" else "",
                        f"{ehy:.3f}" if ehy != "" else "", cver])
    return path

def load_constants():
    dgh, cg = {}, {}
    ch = {}
    with open(os.path.join(HERE, "data", "constants.csv")) as f:
        for r in csv.DictReader(f):
            if r["key"] == "dGfH": dgh[r["solvent"]] = float(r["value_kcal_or_V"])
            if r["key"] == "CG":   cg[r["solvent"]]  = float(r["value_kcal_or_V"])
            if r["key"] == "CHyd": ch[r["solvent"]]  = float(r["value_kcal_or_V"])
    return dgh, cg, ch

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
    # provenance batch map (CR-2026-11-13-verification-ledger): every entry_id
    # covered by exactly one non-overlapping ID range; ledger (if built) complete
    bpath = os.path.join(HERE, "data", "provenance_batches.csv")
    if not os.path.exists(bpath):
        errors.append("data/provenance_batches.csv missing (verification ledger batch map)")
    else:
        import csv as _csv
        ranges = []
        for b in _csv.DictReader(open(bpath, encoding="utf-8")):
            ranges.append((int(b["range_start"].split("-")[1]), int(b["range_end"].split("-")[1])))
        ranges.sort()
        for (s1, e1), (s2, e2) in zip(ranges, ranges[1:]):
            if s2 <= e1:
                errors.append(f"provenance_batches.csv: ranges {s1}..{e1} and {s2}..{e2} overlap")
        for r in rows:
            n = int(r["entry_id"].split("-")[1]) if r.get("entry_id", "").startswith("BDFE-") else None
            if n is not None and not any(s <= n <= e for s, e in ranges):
                errors.append(f"provenance_batches.csv: {r['entry_id']} not covered by any range")
        vpath = os.path.join(HERE, "derived", "verification.csv")
        # build.py regenerates the ledger right after this validate run, so the
        # staleness check is skipped there (PCETBASE_BUILDING=1); standalone
        # validate.py (CI) still enforces it on the committed tree.
        if os.path.exists(vpath) and os.environ.get("PCETBASE_BUILDING") != "1":
            led = {v["entry_id"] for v in _csv.DictReader(open(vpath, encoding="utf-8"))}
            missing = [r["entry_id"] for r in rows if r.get("entry_id") and r["entry_id"] not in led]
            if missing:
                errors.append(f"derived/verification.csv stale: {len(missing)} entry_ids missing (run build.py), e.g. {missing[:3]}")
    # origin enum (CR-2026-11-13-origin-provenance): exp/comp/mixed/empty only
    for r in rows:
        o = r.get("origin", "")
        if o not in ("", "exp", "comp", "mixed"):
            errors.append(f"data.csv {r.get('entry_id','?')}: invalid origin '{o}' (allowed: exp, comp, mixed, empty)")
    # F7 hardening M1 (stress 2026-11-12): method whitelist
    ALLOWED_METHODS = {"", "equil", "sq", "hyd", "OCP", "hess", "tabulated"}
    for r in rows:
        m = r.get("method", "")
        if m not in ALLOWED_METHODS:
            errors.append(f"data.csv {r.get('entry_id','?')}: unknown method '{m}' (allowed: {', '.join(sorted(v or 'empty' for v in ALLOWED_METHODS))})")
    # F7 hardening M2: method=hyd requires hydricity_kcal
    for r in rows:
        if r.get("method") == "hyd" and not r.get("hydricity_kcal"):
            errors.append(f"data.csv {r.get('entry_id','?')}: method=hyd but hydricity_kcal is empty")
    # F7 hardening M4: numeric fields must parse (clean per-row error, never a traceback)
    NUMERIC_FIELDS = ("E_a", "E_b", "E_c", "E_H2", "pKa_a", "pKa_b", "BDFE_pub", "hydricity_kcal", "sigma_BDFE")
    for r in rows:
        for f in NUMERIC_FIELDS:
            v = r.get(f, "")
            if v:
                try:
                    float(v)
                except ValueError:
                    errors.append(f"data.csv {r.get('entry_id','?')}: non-numeric {f} ('{v}')")
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
        if not re.fullmatch(r"CPL-[0-9]{4,}", cid):
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
    dgh, cg, ch = load_constants()
    rows = list(csv.DictReader(open(os.path.join(HERE, "data", "data.csv"))))
    # F7 hardening M3 (soft): hydricity cycle present but no CHyd constant for the solvent
    for r in rows:
        if r.get("hydricity_kcal") and r.get("E_c") and r.get("solvent") not in ch:
            print(f"SOFT WARN {r.get('entry_id','?')}: hydricity_kcal + E_c stored but no CHyd constant for solvent '{r.get('solvent')}' — diagonal not checked")
    # F7 hardening M7 (soft): limit flag without conditions text
    for r in rows:
        if "limit" in r.get("flags", "") and not r.get("conditions", "").strip():
            print(f"SOFT WARN {r.get('entry_id','?')}: flag 'limit' but conditions is empty (document the limit)")
    n_eq18 = n_eq10 = n_hyd = 0
    flags18, flags10, flagshyd = [], [], []
    resid18, resid10, residhyd = {}, {}, {}
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
        # hydricity diagonal (CR-2026-11-12-tmh-wiedner): dG(H-) = 1.364*pKa(MH)
        # + 23.06*(E_a + E_c) + CHyd(solvent). E_a = E(X*/X-), E_c = E(X+/X*)
        # (Q3 decision: own column, not an E_b overload). 1.364 because Wiedner
        # (Chem. Rev. 2016, Table 1 + SI xlsx) computes every hydricity with
        # 1.364; 1.37 would add a +0.006*pKa convention artifact (Q2 decision).
        # Bordwell/eq 10 stays at 1.37 (Agarwal convention). Active only where
        # hydricity_kcal is populated AND the solvent's CHyd constant exists.
        # form 1: X-H -> X- -> X* -> X+ (E_a + pKa_b); form 2 (oxidized-hydride
        # route, Ciancanelli eq 13; CR-2026-11-12-tmh-morris B3): MH -> MH*+ ->
        # X* -> X+ (E_b + pKa_a).
        hyd_ok = r.get("hydricity_kcal") and r["solvent"] in ch and r.get("E_c")
        if hyd_ok and ((r["E_a"] and r["pKa_b"]) or (r["E_b"] and r["pKa_a"])):
            n_hyd += 1
            if r["E_a"] and r["pKa_b"]:
                calc = 1.364*float(r["pKa_b"]) + 23.06*(float(r["E_a"]) + float(r["E_c"])) + ch[r["solvent"]]
            else:
                calc = 1.364*float(r["pKa_a"]) + 23.06*(float(r["E_b"]) + float(r["E_c"])) + ch[r["solvent"]]
            d = calc - float(r["hydricity_kcal"])
            residhyd[r["entry_id"]] = d
            if abs(d) > 0.5:
                flagshyd.append((name, float(r["hydricity_kcal"]), round(calc,2), round(d,2), "soft" if soft else "CHECK"))
    dpath = write_derived(rows, resid18, resid10, residhyd)
    print(f"rows: {len(rows)} | eq18 checks: {n_eq18} | eq10 cross-checks: {n_eq10} | hydricity checks: {n_hyd} | derived table: {dpath}")
    print(f"\neq18 deviations > 0.3 kcal/mol: {len(flags18)}")
    for f in flags18: print("  ", f)
    print(f"\neq10 deviations > 0.5 kcal/mol: {len(flags10)}")
    for f in flags10: print("  ", f)
    print(f"\nhydricity deviations > 0.5 kcal/mol: {len(flagshyd)}")
    for f in flagshyd: print("  ", f)
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
    # origin soft check: exp claimed where a leg is simulation-fitted
    contradictions = [r["entry_id"] for r in rows if r.get("origin") == "exp"
                      and ("sim-pKa" in r.get("flags", "")
                           or "simulation" in r.get("conditions", "").lower())]
    if contradictions:
        print(f"\nSOFT WARN origin=exp but simulation-fitted leg: {', '.join(contradictions)}")
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
