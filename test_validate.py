#!/usr/bin/env python3
"""Mutation tests for validate.py's hard structural gate.
Copies data/ to a temp dir, applies one mutation per case, runs validate.py
there, and asserts the expected exit code. Run: python test_validate.py"""
import csv, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

def run_case(name, mutate, expect_fail):
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "data"))
    for f in ("data.csv", "couples.csv", "constants.csv", "provenance_batches.csv", "provenance_overrides.csv"):
        shutil.copy(os.path.join(HERE, "data", f), os.path.join(tmp, "data", f))
    shutil.copy(os.path.join(HERE, "validate.py"), tmp)
    mutate(tmp)
    rc = subprocess.run([sys.executable, os.path.join(tmp, "validate.py")],
                        capture_output=True).returncode
    ok = (rc != 0) if expect_fail else (rc == 0)
    print(("PASS " if ok else "FAIL ") + name + f" (exit {rc})")
    shutil.rmtree(tmp)
    return ok

def edit_csv(tmp, fname, fn):
    p = os.path.join(tmp, "data", fname)
    rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
    head = rows[0].keys()
    fn(rows)
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=head); w.writeheader(); w.writerows(rows)

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
        ("empty BDFE fails (F7)",
         lambda t: edit_csv(t, "data.csv", lambda r: r[0].update(BDFE="")), True),
        ("empty BDFE with ref-conv-missing passes (documented convention)",
         lambda t: edit_csv(t, "data.csv", lambda r: r[0].update(BDFE="", flags="ref-conv-missing")), False),
    ]
    fails = sum(0 if run_case(*c) else 1 for c in cases)
    print(f"\n{len(cases)-fails}/{len(cases)} mutation cases pass")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
