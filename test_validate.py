#!/usr/bin/env python3
"""Mutation tests for validate.py's hard gates (structure + closure).
Copies data/ to a temp dir, applies one mutation per case, runs validate.py
there, and asserts the expected exit code. Run: python test_validate.py"""
import csv, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

def run_case(name, mutate, expect_fail, msg=None, nomsg=None):
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "data"))
    for f in ("data.csv", "couples.csv", "constants.csv", "provenance_batches.csv", "provenance_overrides.csv"):
        shutil.copy(os.path.join(HERE, "data", f), os.path.join(tmp, "data", f))
    shutil.copy(os.path.join(HERE, "validate.py"), tmp)
    mutate(tmp)
    pr = subprocess.run([sys.executable, os.path.join(tmp, "validate.py")],
                        capture_output=True, text=True)
    rc = pr.returncode
    ok = (rc != 0) if expect_fail else (rc == 0)
    # H123: a hard failure is a per-row message, never a traceback
    if "Traceback" in pr.stderr:
        ok = False
    if msg and not re.search(msg, pr.stdout):
        ok = False
    if nomsg and re.search(nomsg, pr.stdout):
        ok = False
    print(("PASS " if ok else "FAIL ") + name + f" (exit {rc})" + ("" if ok else "\n" + pr.stdout[-600:] + pr.stderr[-600:]))
    shutil.rmtree(tmp)
    return ok

def edit_csv(tmp, fname, fn):
    p = os.path.join(tmp, "data", fname)
    rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
    head = rows[0].keys()
    fn(rows)
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=head); w.writeheader(); w.writerows(rows)

def _shift_bdfe(rows, flags):
    """Closure-gate mutation: first unflagged MeCN row with E_H2 and BDFE gets
    BDFE + 1.0 kcal/mol (eq 18 deviation 1.0 kcal/mol) and the given flags."""
    for x in rows:
        if x["solvent"] == "MeCN" and x["E_H2"] and x["BDFE"] and not x["flags"]:
            x["BDFE"] = f'{float(x["BDFE"]) + 1.0:.1f}'
            x["flags"] = flags
            return

def _row(rows, eid):
    return next(x for x in rows if x["entry_id"] == eid)

def _set(eid, **kw):
    return lambda t: edit_csv(t, "data.csv", lambda r: _row(r, eid).update(**kw))

def main():
    cases = [
        ("clean data passes", lambda t: None, False),
        ("duplicate entry_id fails (F1)",
         lambda t: edit_csv(t, "data.csv", lambda r: r[5].update(entry_id=r[4]["entry_id"])), True),
        ("duplicate couple key fails (F2)",
         lambda t: edit_csv(t, "couples.csv", lambda r: r.append({**r[0], "couple_id": "CPL-9998"})), True),
        ("duplicate couple_id fails",
         lambda t: edit_csv(t, "couples.csv", lambda r: r[1].update(couple_id=r[0]["couple_id"])), True),
        ("broken FK fails",
         lambda t: edit_csv(t, "data.csv", lambda r: r[0].update(couple_id="CPL-9999")), True),
        ("manual star without reason fails",
         lambda t: edit_csv(t, "data.csv", lambda r: r[0].update(recommended="1")), True),
        ("two stars in one couple fails",
         lambda t: edit_csv(t, "data.csv", lambda r: [x.update(recommended="1") for x in r if x["couple_id"] == "CPL-0377"]), True),
        ("unknown method fails (stress M1)",
         lambda t: edit_csv(t, "data.csv", lambda r: r[0].update(method="computedX")), True),
        ("method=hyd without hydricity fails (stress M2)",
         lambda t: edit_csv(t, "data.csv", lambda r: [x.update(hydricity_kcal="") for x in r if x["method"] == "hyd"][:1]), True),
        ("hydricity on CHyd-less solvent passes with soft warning (stress M3)",
         lambda t: edit_csv(t, "data.csv", lambda r: [x.update(solvent="pentane") for x in r if x["method"] == "hyd" and x["solvent"] == "MeCN"][:1] and None), False),
         # pentane: no dGfH, CG or CHyd constant, so only the M3 soft warning applies (hexane has dGfH 51.7 kcal/mol and would now trip the closure gate)
        ("non-numeric E_c fails cleanly (stress M4)",
         lambda t: edit_csv(t, "data.csv", lambda r: [x.update(E_c="abc") for x in r if x["E_c"]][:1]), True),
        ("empty BDFE fails (F7)",
         lambda t: edit_csv(t, "data.csv", lambda r: r[0].update(BDFE="")), True),
        ("unflagged 1 kcal/mol eq 18 deviation fails (closure gate)",
         lambda t: edit_csv(t, "data.csv", lambda r: _shift_bdfe(r, "")), True),
        ("same deviation with flag approx passes (closure gate)",
         lambda t: edit_csv(t, "data.csv", lambda r: _shift_bdfe(r, "approx")), False),
        ("empty BDFE with ref-conv-missing passes (documented convention)",
         lambda t: edit_csv(t, "data.csv", lambda r: r[0].update(BDFE="", flags="ref-conv-missing")), False),
        # H123: non-numeric values give a per-row message, no traceback (closure arithmetic runs after the check)
        ("non-numeric E_H2 fails cleanly with a per-row message (H123)",
         _set("BDFE-0001", E_H2="0.5x"), True, r"BDFE-0001: non-numeric E_H2"),
        ("non-numeric pKa_b fails cleanly with a per-row message (H123)",
         _set("BDFE-0507", pKa_b="21,1"), True, r"BDFE-0507: non-numeric pKa_b"),
        ("non-numeric BDFE fails cleanly with a per-row message (H123)",
         _set("BDFE-0002", BDFE="n/a"), True, r"BDFE-0002: BDFE empty or non-numeric"),
        ("non-numeric E_raw fails cleanly with a per-row message (H123)",
         _set("BDFE-0540", E_raw="0.56 V"), True, r"BDFE-0540: non-numeric E_raw"),
        # EP-01
        ("E_raw without E_raw_leg fails (EP-01)",
         _set("BDFE-0507", E_raw_leg=""), True, r"BDFE-0507: E_raw set but E_raw_leg empty"),
        ("converted E_raw 0.01 V off the named leg fails (EP-01)",
         _set("BDFE-0540", E_raw="0.57"), True, r"BDFE-0540: converted E_raw 0\.1900 V differs from E_b"),
        ("E_raw_leg naming the wrong leg fails (EP-01)",
         _set("BDFE-0541", E_raw_leg="a"), True, r"BDFE-0541: E_raw_leg 'a' but E_a is empty"),
        ("off-target E_raw without ref-conv fails (EP-01)",
         _set("BDFE-0521", flags="derived;approx"), True, r"BDFE-0521: .*flag 'ref-conv' required"),
        ("ref-conv on an on-target raw potential fails (EP-01)",
         _set("BDFE-0413", flags="recomputed;check-src;ref-conv"), True, r"BDFE-0413: flag 'ref-conv' but E_raw_ref 'NHE' already is the target scale"),
        ("OCP row without the buffer pKa in conditions fails (EP-01, M-39)",
         _set("BDFE-0387", conditions="MeCN, OCP"), True, r"BDFE-0387: E_raw_leg OCP but no 'buffer pKa"),
        # EP-02
        ("limit without bounds fails (EP-02)",
         _set("BDFE-0093", bounds=""), True, r"BDFE-0093: flag 'limit' but bounds is empty"),
        ("bounds without limit fails (EP-02)",
         _set("BDFE-0142", flags=""), True, r"BDFE-0142: bounds set but flag 'limit' missing"),
        ("malformed bounds token fails (EP-02)",
         _set("BDFE-0100", bounds="E_a<;pKa_b=>"), True, r"BDFE-0100: bad bounds token"),
        ("both-diagonal rule: unflagged miss on the second diagonal fails (EP-02)",
         _set("BDFE-0111", flags=""), True, r"CLOSURE GATE.*\n.*\(LA\)2\(Mn2\(O\)\(OH\)\).*E_a/pKa_b"),
        ("indeterminate Bordwell diagonals are reported and not evaluated (EP-02: BDFE-0142 pKa_b 30 gives no eq10 deviation)",
         _set("BDFE-0142", pKa_b="30.0"), False, r"BDFE-0142 eq10 E_a/pKa_b\n\s+BDFE-0142 eq10 E_b/pKa_a",
         r"pyRuIIIOH\]2\+ \(H2O, T24\)"),
        # EP-10
        ("sigma_BDFE without sigma_type fails (EP-10)",
         _set("BDFE-0389", sigma_type=""), True, r"BDFE-0389: sigma_BDFE set but sigma_type empty"),
        ("producer-estimate sigma labelled published fails (EP-10)",
         _set("BDFE-0521", sigma_type="published"), True, r"BDFE-0521: conditions call sigma a producer estimate"),
    ]
    fails = sum(0 if run_case(*c) else 1 for c in cases)
    print(f"\n{len(cases)-fails}/{len(cases)} mutation cases pass")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
