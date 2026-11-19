#!/usr/bin/env python3
"""Validation of data.csv and couples.csv.

Closure gate (exit 1 since CR-2026-11-17-si-findings item 5): a closure deviation
beyond threshold (eq 18 > 0.3 kcal/mol; eq 10 and hydricity > 0.5 kcal/mol)
fails unless an excusing flag documents it (approx, limit, lowprec, check-src,
dmso-unc); flagged deviations are listed as "soft" for review.
Hard (exit 1, fails CI and aborts build.py): schema/structure errors —
missing or unknown couple_id (FK), duplicate or malformed couple_id, bad
bond/discordant values, manual star without recommended_reason on the couple,
multiple stars in one couple, non-numeric numeric fields (checked first, so
a bad value gives a per-row message instead of a traceback; H123), E_raw
without E_raw_leg or with a converted value that does not match the named leg,
`ref-conv` present iff E_raw_ref is off the solvent's target scale (EP-01),
`limit` without `bounds` or vice versa, malformed bounds (EP-02), and
sigma_BDFE without sigma_type or vice versa (EP-10).
Both Bordwell diagonals are checked where both are stored (EP-02): each
diagonal beyond 0.5 kcal/mol needs an excusing flag. A diagonal that combines
an upper and a lower bound is not evaluated ("indeterminate"); bounds of the
same direction on calc and stored BDFE are "not informative"; a bound on only
one side is tested as an inequality (review-pr-79 F1). Only equality residuals
go into derived/analysis.csv.
Flags are matched by token after splitting on ";" and ":" (N2).
"""
import csv, hashlib, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
BONDS = {"O-H", "N-H", "S-H", "C-H", "M-H", "X-H"}
EXCUSING = ("limit", "approx", "lowprec", "check-src", "dmso-unc")
NUMERIC_FIELDS = ("E_a", "E_b", "E_c", "E_H2", "pKa_a", "pKa_b", "BDFE_pub",
                  "hydricity_kcal", "sigma_BDFE", "E_raw", "T_K", "E_raw_offset")
BOUND_FIELDS = ("E_a", "E_b", "pKa_a", "pKa_b", "E_H2", "BDFE")
BOUND_OPS = {"<": "U", "≤": "U", ">": "L", "≥": "L"}  # U = upper bound, L = lower bound
E_RAW_LEGS = {"a": "E_a", "b": "E_b", "c": "E_c", "H2": "E_H2", "OCP": None}
SIGMA_TYPES = ("published", "curator-estimate", "bracket-midpoint")

def flag_tokens(flags):
    """N2: flags as a token set; 'hess:pKa_b' yields 'hess:pKa_b', 'hess', 'pKa_b'."""
    out = set()
    for f in (flags or "").split(";"):
        f = f.strip()
        if not f:
            continue
        out.add(f)
        out.update(p for p in f.split(":") if p)
    return out

def has_flag(r, name):
    return name in flag_tokens(r.get("flags", ""))

def parse_bounds(s):
    """'E_a<;BDFE≥' -> {'E_a': '<', 'BDFE': '≥'}; raises ValueError on a bad token."""
    out = {}
    for tok in (s or "").split(";"):
        tok = tok.strip()
        if not tok:
            continue
        op = tok[-1]
        field = tok[:-1]
        if op not in BOUND_OPS or field not in BOUND_FIELDS:
            raise ValueError(f"bad bounds token '{tok}' (field in {', '.join(BOUND_FIELDS)}; op in < > ≤ ≥)")
        if field in out:
            raise ValueError(f"duplicate bounds field '{field}'")
        out[field] = op
    return out

def closure_state(bounds, legs):
    """How a closure residual d = calc - stored BDFE can be read (review-pr-79 F1).
    The legs (E, pKa) enter calc with positive coefficients, so a bounded leg
    makes calc a bound in the same direction; the stored BDFE sits on the other
    side of the residual. Returns (state, sign):
      ('free', None)             no bound involved: d is an equality residual
      ('indeterminate', None)    legs combine an upper and a lower bound
      ('not-informative', None)  calc and stored BDFE are bounds in the same
                                 direction (two lower bounds constrain nothing)
      ('inequality', 'le'|'ge')  a real test: d <= 0 ('le') or d >= 0 ('ge')."""
    ld = {BOUND_OPS[bounds[f]] for f in legs if f in bounds}
    if len(ld) > 1:
        return "indeterminate", None
    ld = next(iter(ld), None)          # 'L': true BDFE >= calc
    bd = BOUND_OPS[bounds["BDFE"]] if "BDFE" in bounds else None  # 'L': true BDFE >= stored
    if ld is None and bd is None:
        return "free", None
    if ld and bd and ld == bd:
        return "not-informative", None
    if ld:                              # legs bounded (BDFE free or bounded the other way)
        return "inequality", ("le" if ld == "L" else "ge")
    return "inequality", ("ge" if bd == "L" else "le")   # only BDFE bounded: calc is exact

def on_target_scale(ref, solvent):
    """Fc in organic solvents; SHE or NHE (NHE = SHE convention) in water."""
    return ref in ("SHE", "NHE") if solvent == "H2O" else ref in ("Fc", "Fc+/0")

def constants_version():
    """Short content hash of constants.csv: a constants update changes every
    row of derived/analysis.csv visibly."""
    with open(os.path.join(HERE, "data", "constants.csv"), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]

def write_derived(rows, resid18, resid10, residhyd=None, resid10w=None):
    """Canonical derived table (CR-2026-11-11-derived-analysis-table):
    one row per data.csv entry; eq 18/eq 10 residuals (calc - stored,
    kcal/mol) as used by the manuscript's consistency analyses.
    eq10_residual_kcal: the diagonal closest to the stored BDFE (definition
    unchanged since v1.5); eq10_residual_other_kcal: the other diagonal where
    both determinate diagonals are stored (EP-02 both-diagonal rule)."""
    os.makedirs(os.path.join(HERE, "derived"), exist_ok=True)
    cver = constants_version()
    path = os.path.join(HERE, "derived", "analysis.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")  # O1: LF, as committed
        w.writerow(["entry_id", "compound", "couple_id", "class", "solvent",
                    "method", "flags", "recommended",
                    "eq18_residual_kcal", "eq10_residual_kcal",
                    "hyd_residual_kcal", "constants_version",
                    "eq10_residual_other_kcal"])
        for r in rows:
            e18 = resid18.get(r["entry_id"], "")
            e10 = resid10.get(r["entry_id"], "")
            ehy = (residhyd or {}).get(r["entry_id"], "")
            e10w = (resid10w or {}).get(r["entry_id"], "")
            w.writerow([r["entry_id"], r["compound"], r.get("couple_id", ""),
                        r["class"], r["solvent"], r["method"], r["flags"],
                        r.get("recommended", ""),
                        f"{e18:.3f}" if e18 != "" else "",
                        f"{e10:.3f}" if e10 != "" else "",
                        f"{ehy:.3f}" if ehy != "" else "", cver,
                        f"{e10w:.3f}" if e10w != "" else ""])
    return path

def load_constants(full=False):
    dgh, cg = {}, {}
    ch, eh2, refoff = {}, {}, {}
    with open(os.path.join(HERE, "data", "constants.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["key"] == "dGfH": dgh[r["solvent"]] = float(r["value_kcal_or_V"])
            if r["key"] == "CG":   cg[r["solvent"]]  = float(r["value_kcal_or_V"])
            if r["key"] == "CHyd": ch[r["solvent"]]  = float(r["value_kcal_or_V"])
            if r["key"] == "EH2vsFc": eh2[r["solvent"]] = float(r["value_kcal_or_V"])
            if r["key"].startswith("refoff:"):
                refoff[(r["key"][7:], r["solvent"])] = float(r["value_kcal_or_V"])
    if full:
        return dgh, cg, ch, eh2, refoff
    return dgh, cg, ch

def numeric_errors(rows):
    """H123 / stress M4: every numeric field parses; runs before any closure
    arithmetic, so a bad value is a per-row error, never a traceback."""
    errors = []
    for r in rows:
        for f in NUMERIC_FIELDS:
            v = r.get(f, "")
            if v:
                try:
                    float(v)
                except ValueError:
                    errors.append(f"data.csv {r.get('entry_id','?')}: non-numeric {f} ('{v}')")
        # F7: BDFE required and numeric unless the row is flagged ref-conv-missing
        if has_flag(r, "ref-conv-missing") and not r.get("BDFE"):
            continue
        try:
            float(r["BDFE"])
        except (ValueError, KeyError):
            errors.append(f"data.csv {r.get('entry_id','?')}: BDFE empty or non-numeric ('{r.get('BDFE','')}') and not flagged ref-conv-missing")
    return errors

def readme_errors(rows):
    """EP-04 (M-07): the README curation statement names the number of entries that
    store no E or pKa leg; it must match the data."""
    n = sum(1 for r in rows if not any(r.get(k) for k in ("E_a", "E_b", "E_c", "pKa_a", "pKa_b")))
    try:
        txt = open(os.path.join(HERE, "README.md"), encoding="utf-8").read()
    except OSError:
        return []
    m = re.search(r"for (\d+) entries the source tabulates only", txt)
    if not m:
        return ["README.md: curation statement ('for N entries the source tabulates only ...') not found"]
    if int(m.group(1)) != n:
        return [f"README.md: curation statement says {m.group(1)} entries without stored legs; data.csv has {n}"]
    return []

def schema_errors(rows, eh2, refoff):
    """EP-01 (E_raw_leg, ref-conv), EP-02 (bounds), EP-10 (sigma_type).
    Assumes numeric_errors() passed."""
    errors = []
    for r in rows:
        eid = r.get("entry_id", "?")
        # --- EP-01: which leg a raw potential belongs to
        leg = r.get("E_raw_leg", "")
        if leg and leg not in E_RAW_LEGS:
            errors.append(f"data.csv {eid}: invalid E_raw_leg '{leg}' (allowed: {', '.join(E_RAW_LEGS)})")
            continue
        if r.get("E_raw"):
            if not r.get("E_raw_ref"):
                errors.append(f"data.csv {eid}: E_raw without E_raw_ref")
                continue
            if not leg:
                errors.append(f"data.csv {eid}: E_raw set but E_raw_leg empty (a, b, c, H2 or OCP)")
                continue
            raw, ref, solv = float(r["E_raw"]), r["E_raw_ref"], r["solvent"]
            target = on_target_scale(ref, solv)
            off = 0.0 if target else refoff.get((ref, solv))
            if r.get("E_raw_offset"):
                # EP-05 / review-pr-79 O5: the offset the source itself states wins
                if target:
                    errors.append(f"data.csv {eid}: E_raw_offset set but E_raw_ref '{ref}' already is the target scale in {solv}")
                    continue
                off = float(r["E_raw_offset"])
                if "stated" not in r.get("conditions", "").lower() and "states" not in r.get("conditions", "").lower():
                    errors.append(f"data.csv {eid}: E_raw_offset set but conditions do not say where the source states it")
            if target:
                for fl in ("ref-conv", "ref-conv-missing"):
                    if has_flag(r, fl):
                        errors.append(f"data.csv {eid}: flag '{fl}' but E_raw_ref '{ref}' already is the target scale in {solv}")
            elif off is None:
                if not has_flag(r, "ref-conv-missing"):
                    errors.append(f"data.csv {eid}: no refoff:{ref} constant for {solv}; flag 'ref-conv-missing' required")
                if has_flag(r, "ref-conv"):
                    errors.append(f"data.csv {eid}: flag 'ref-conv' but no refoff:{ref} constant for {solv}")
            else:
                if not has_flag(r, "ref-conv"):
                    errors.append(f"data.csv {eid}: E_raw_ref '{ref}' is off the {solv} target scale; flag 'ref-conv' required")
                if has_flag(r, "ref-conv-missing"):
                    errors.append(f"data.csv {eid}: flag 'ref-conv-missing' but refoff:{ref} exists for {solv}")
            if off is not None:
                conv = raw - off
                if leg == "OCP":
                    # M-39: the buffer pKa of the cell potential is stored in conditions;
                    # E(V vs H2) = E_OCP(vs Fc) - E(H+/H2 vs Fc) + 0.05916 V x pKa (1:1 buffer)
                    m = re.search(r"buffer pKa(?:\([^)]*\))? (-?[0-9.]+)", r.get("conditions", ""))
                    if not m:
                        errors.append(f"data.csv {eid}: E_raw_leg OCP but no 'buffer pKa <value>' in conditions")
                    elif r.get("E_H2") and solv in eh2:
                        calc = conv - eh2[solv] + 0.05916 * float(m.group(1))
                        if abs(calc - float(r["E_H2"])) > 0.003:
                            errors.append(f"data.csv {eid}: OCP cell potential with buffer pKa {m.group(1)} gives E_H2 {calc:.4f} V vs H2, stored {r['E_H2']} (tolerance 0.003 V)")
                else:
                    col = E_RAW_LEGS[leg]
                    stored = r.get(col, "")
                    if col == "E_H2" and stored and solv in eh2:
                        conv = conv - eh2[solv]
                    if not stored:
                        errors.append(f"data.csv {eid}: E_raw_leg '{leg}' but {col} is empty")
                    elif abs(conv - float(stored)) > 0.0005:
                        errors.append(f"data.csv {eid}: converted E_raw {conv:.4f} V differs from {col} {stored} V by more than 0.0005 V")
        elif leg:
            errors.append(f"data.csv {eid}: E_raw_leg '{leg}' but E_raw empty")
        if r.get("E_raw_offset") and not r.get("E_raw"):
            errors.append(f"data.csv {eid}: E_raw_offset set but E_raw empty")
        # EP-03: Ep:<leg> names a stored potential leg
        for t in (r.get("flags") or "").split(";"):
            if t.startswith("Ep:"):
                lg = t[3:]
                if lg not in ("E_a", "E_b", "E_c"):
                    errors.append(f"data.csv {eid}: flag '{t}' names no potential leg (E_a, E_b, E_c)")
                elif not r.get(lg):
                    errors.append(f"data.csv {eid}: flag '{t}' but {lg} is empty")
            elif t == "Ep":
                errors.append(f"data.csv {eid}: flag 'Ep' needs the leg it applies to (Ep:E_a, Ep:E_b or Ep:E_c)")
        # --- EP-02: bounds
        try:
            b = parse_bounds(r.get("bounds", ""))
        except ValueError as ex:
            errors.append(f"data.csv {eid}: {ex}")
            b = {}
        lim = has_flag(r, "limit")
        if lim and not r.get("bounds", "").strip():
            errors.append(f"data.csv {eid}: flag 'limit' but bounds is empty")
        if r.get("bounds", "").strip() and not lim:
            errors.append(f"data.csv {eid}: bounds set but flag 'limit' missing")
        for fld in b:
            if not r.get(fld):
                errors.append(f"data.csv {eid}: bounds names {fld}, which is empty")
        # --- EP-10: sigma_type
        st, sg = r.get("sigma_type", ""), r.get("sigma_BDFE", "")
        if st and st not in SIGMA_TYPES:
            errors.append(f"data.csv {eid}: invalid sigma_type '{st}' (allowed: {', '.join(SIGMA_TYPES)})")
        if sg and not st:
            errors.append(f"data.csv {eid}: sigma_BDFE set but sigma_type empty")
        if st and not sg:
            errors.append(f"data.csv {eid}: sigma_type set but sigma_BDFE empty")
        cond = r.get("conditions", "").lower()
        if sg and "producer estimate" in cond and st != "curator-estimate":
            errors.append(f"data.csv {eid}: conditions call sigma a producer estimate but sigma_type is '{st}'")
        if st == "curator-estimate" and "estimate" not in cond:
            errors.append(f"data.csv {eid}: sigma_type curator-estimate but conditions do not document the estimate")
        if st == "bracket-midpoint" and "midpoint" not in cond:
            errors.append(f"data.csv {eid}: sigma_type bracket-midpoint but conditions do not name the bracket midpoint")
    return errors

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
        btype = {}  # Agarwal 2022 review-table batches only: their rows carry an Agarwal table (T5..T24)
        for b in _csv.DictReader(open(bpath, encoding="utf-8")):
            if b["source_type"] == "review-table" and "Agarwal" in b["source_locator"]:
                btype[(int(b["range_start"].split("-")[1]), int(b["range_end"].split("-")[1]))] = "Agarwal 2022 review-table"
        for r in rows:
            n = int(r["entry_id"].split("-")[1]) if r.get("entry_id", "").startswith("BDFE-") else None
            if n is not None and not any(s <= n <= e for s, e in ranges):
                errors.append(f"provenance_batches.csv: {r['entry_id']} not covered by any range")
            # EP-11 (M-19): a primary-literature row may not sit in a review-table batch
            if n is not None and r.get("table") == "EXT":
                for (s, e), t in btype.items():
                    if s <= n <= e:
                        errors.append(f"provenance_batches.csv: {r['entry_id']} has table EXT but sits in the {t} batch {s}..{e}")
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
    # F7 hardening M4 and the BDFE requirement: see numeric_errors() (runs first)
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
    dgh, cg, ch, eh2, refoff = load_constants(full=True)
    rows = list(csv.DictReader(open(os.path.join(HERE, "data", "data.csv"), encoding="utf-8")))
    # H123: numeric parse and schema checks run before any closure arithmetic
    pre = numeric_errors(rows)
    if not pre:
        pre = schema_errors(rows, eh2, refoff) + readme_errors(rows)
    if pre:
        print("--- structural checks (hard) ---")
        print(f"HARD ERRORS: {len(pre)}")
        for e in pre: print("  ", e)
        return 1
    # F7 hardening M3 (soft): hydricity cycle present but no CHyd constant for the solvent
    for r in rows:
        if r.get("hydricity_kcal") and r.get("E_c") and r.get("solvent") not in ch:
            print(f"SOFT WARN {r.get('entry_id','?')}: hydricity_kcal + E_c stored but no CHyd constant for solvent '{r.get('solvent')}' — diagonal not checked")
    # EP-03 (soft): lowT without a temperature
    for r in rows:
        if has_flag(r, "lowT") and not r.get("T_K"):
            print(f"SOFT WARN {r.get('entry_id','?')}: flag 'lowT' but T_K is empty")
    # F7 hardening M7 (soft): limit flag without conditions text
    for r in rows:
        if has_flag(r, "limit") and not r.get("conditions", "").strip():
            print(f"SOFT WARN {r.get('entry_id','?')}: flag 'limit' but conditions is empty (document the limit)")
    n_eq18 = n_eq10 = n_hyd = 0
    flags18, flags10, flagshyd = [], [], []
    resid18, resid10, residhyd, resid10w = {}, {}, {}, {}
    indeterminate, noninf, ineq = [], [], []
    for r in rows:
        name = f'{r["compound"]}{"/"+r["partner"] if r["partner"] else ""} ({r["solvent"]}, {r["table"]})'
        soft = any(has_flag(r, k) for k in EXCUSING)
        bnd = parse_bounds(r.get("bounds", ""))
        # eq 18: BDFE = 23.06*E(V vs H2) + dGfH
        if r["E_H2"] and r["BDFE"] and r["solvent"] in dgh:
            st, sg = closure_state(bnd, ("E_H2",))
            calc = 23.06*float(r["E_H2"]) + dgh[r["solvent"]]
            d = calc - float(r["BDFE"])
            if st == "indeterminate":
                indeterminate.append(f"{r['entry_id']} eq18")
            elif st == "not-informative":
                noninf.append(f"{r['entry_id']} eq18")
            elif st == "inequality":
                ok = d <= 0.3 if sg == "le" else d >= -0.3
                ineq.append(f"{r['entry_id']} eq18 calc - stored {'<=' if sg == 'le' else '>='} 0: {d:+.2f} kcal/mol {'ok' if ok else 'VIOLATED'}")
                if not ok:
                    flags18.append((name + " [bound]", float(r["BDFE"]), round(calc,2), round(d,2), "soft" if soft else "CHECK"))
            else:
                n_eq18 += 1
                resid18[r["entry_id"]] = d
                if abs(d) > 0.3:
                    flags18.append((name, float(r["BDFE"]), round(calc,2), round(d,2), "soft" if soft else "CHECK"))
        # eq 10, both square-scheme diagonals (EP-02): every determinate diagonal
        # that is stored must close within 0.5 kcal/mol or carry an excusing flag
        if r["BDFE"] and r["solvent"] in cg:
            devs = []
            for e, p, lab in (("E_a", "pKa_b", "E_a/pKa_b"), ("E_b", "pKa_a", "E_b/pKa_a")):
                if not (r[e] and r[p]):
                    continue
                st, sg = closure_state(bnd, (e, p))
                d = 23.06*float(r[e]) + 1.37*float(r[p]) + cg[r["solvent"]] - float(r["BDFE"])
                if st == "indeterminate":
                    indeterminate.append(f"{r['entry_id']} eq10 {lab}")
                    continue
                if st == "not-informative":
                    noninf.append(f"{r['entry_id']} eq10 {lab}")
                    continue
                if st == "inequality":
                    ok = d <= 0.5 if sg == "le" else d >= -0.5
                    ineq.append(f"{r['entry_id']} eq10 {lab} calc - stored {'<=' if sg == 'le' else '>='} 0: {d:+.2f} kcal/mol {'ok' if ok else 'VIOLATED'}")
                    if not ok:
                        flags10.append((name + f" [{lab}, bound]", float(r["BDFE"]), round(float(r["BDFE"])+d,2), round(d,2), "soft" if soft else "CHECK"))
                    continue
                devs.append((lab, d))
            if devs:
                n_eq10 += 1
                best = min(devs, key=lambda x: abs(x[1]))
                resid10[r["entry_id"]] = best[1]
                if len(devs) == 2:
                    resid10w[r["entry_id"]] = [x for x in devs if x is not best][0][1]
                for lab, d in devs:
                    if abs(d) > 0.5:
                        flags10.append((name + (f" [{lab}]" if len(devs) == 2 else ""), float(r["BDFE"]),
                                        round(float(r["BDFE"])+d,2), round(d,2), "soft" if soft else "CHECK"))
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
    dpath = write_derived(rows, resid18, resid10, residhyd, resid10w)
    print(f"rows: {len(rows)} | eq18 checks: {n_eq18} | eq10 cross-checks: {n_eq10} | hydricity checks: {n_hyd} | derived table: {dpath}")
    print(f"\neq18 deviations > 0.3 kcal/mol: {len(flags18)}")
    for f in flags18: print("  ", f)
    print(f"\nindeterminate closures (upper and lower bound combined, not evaluated): {len(indeterminate)}")
    for f in indeterminate: print("  ", f)
    print(f"not informative (calc and stored BDFE are bounds in the same direction): {len(noninf)}")
    for f in noninf: print("  ", f)
    print(f"inequality checks (one side bounded, tested as an inequality): {len(ineq)}")
    for f in ineq: print("  ", f)
    print(f"\neq10 deviations > 0.5 kcal/mol (each stored diagonal): {len(flags10)}")
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
                      and (has_flag(r, "sim-pKa")
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
    unflagged = [f for f in flags18 + flags10 + flagshyd if f[-1] == "CHECK"]
    print("\n--- closure gate (hard) ---")
    if unflagged:
        print(f"CLOSURE GATE: {len(unflagged)} closure deviation(s) without a flag that documents them")
        for f in unflagged: print("  ", f)
        return 1
    print("closure gate OK (every deviation beyond threshold carries an excusing flag)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
