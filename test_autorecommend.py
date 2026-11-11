#!/usr/bin/env python3
"""Unit tests for build.autorecommend (couple-layer policy, CONTRIBUTING rules 1-2).
Run: python test_autorecommend.py  (exit 0 = all pass; also run by CI)."""
import csv, os, sys, tempfile
from build import autorecommend

HEAD = ["table","class","bond","compound","partner","solvent","E_a","E_b",
        "pKa_a","pKa_b","E_H2","BDFE","flags","refs","n_H","method","doi",
        "BDFE_pub","E_raw","E_raw_ref","recommended","year","entry_id",
        "couple_id","sigma_BDFE","T_K","conditions"]

def row(**kw):
    r = {h: "" for h in HEAD}
    r.update(kw)
    return r

def run(rows):
    fd, path = tempfile.mkstemp(suffix=".csv"); os.close(fd)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEAD); w.writeheader(); w.writerows(rows)
    autorecommend(path)
    out = {r["entry_id"]: r["recommended"]
           for r in csv.DictReader(open(path, newline="", encoding="utf-8"))}
    os.remove(path)
    return out

def test_manual_override_freezes_group():
    out = run([
        row(entry_id="BDFE-0001", couple_id="CPL-0001", compound="A", solvent="MeCN",
            BDFE="60.0", method="equil", year="2024", recommended="0"),
        row(entry_id="BDFE-0002", couple_id="CPL-0001", compound="A", solvent="MeCN",
            BDFE="60.1", method="sq", year="2020", recommended="1"),
    ])
    assert out["BDFE-0001"] == "0" and out["BDFE-0002"] == "1", out

def test_method_hierarchy_equil_beats_sq():
    out = run([
        row(entry_id="BDFE-0001", couple_id="CPL-0001", compound="A", solvent="MeCN",
            BDFE="60.0", method="equil", year="2020"),
        row(entry_id="BDFE-0002", couple_id="CPL-0001", compound="A", solvent="MeCN",
            BDFE="60.1", method="sq", year="2024"),
    ])
    assert out["BDFE-0001"] == "auto" and out["BDFE-0002"] == "", out

def test_hess_flag_beats_tabulated():
    out = run([
        row(entry_id="BDFE-0001", couple_id="CPL-0001", compound="A", solvent="MeCN",
            BDFE="60.0", flags="hess", year="2020"),
        row(entry_id="BDFE-0002", couple_id="CPL-0001", compound="A", solvent="MeCN",
            BDFE="60.1", year="2024"),
    ])
    assert out["BDFE-0001"] == "auto" and out["BDFE-0002"] == "", out

def test_conflict_in_top_tier_no_star():
    out = run([
        row(entry_id="BDFE-0001", couple_id="CPL-0001", compound="A", solvent="MeCN",
            BDFE="60.0", method="sq", year="2020"),
        row(entry_id="BDFE-0002", couple_id="CPL-0001", compound="A", solvent="MeCN",
            BDFE="61.0", method="sq", year="2024"),
    ])
    assert out["BDFE-0001"] == "" and out["BDFE-0002"] == "", out

def test_year_tiebreak_within_tier():
    out = run([
        row(entry_id="BDFE-0001", couple_id="CPL-0001", compound="A", solvent="MeCN",
            BDFE="60.0", method="OCP", year="2020"),
        row(entry_id="BDFE-0002", couple_id="CPL-0001", compound="A", solvent="MeCN",
            BDFE="60.2", method="OCP", year="2024"),
    ])
    assert out["BDFE-0002"] == "auto" and out["BDFE-0001"] == "", out

def test_concordance_mean_row_wins():
    out = run([
        row(entry_id="BDFE-0001", couple_id="CPL-0001", compound="A", solvent="MeCN",
            BDFE="60.0", method="equil", year="2024"),
        row(entry_id="BDFE-0002", couple_id="CPL-0001", compound="A", solvent="MeCN",
            BDFE="60.2", method="sq", year="2020"),
        row(entry_id="BDFE-0003", couple_id="CPL-0001", compound="A", solvent="MeCN",
            BDFE="60.1", flags="avg", refs="BDFE-0001;BDFE-0002", year="2024"),
    ])
    assert out["BDFE-0003"] == "auto" and out["BDFE-0001"] == "" and out["BDFE-0002"] == "", out

def test_intra_measurement_avg_flag_is_not_concordance():
    # 'avg' without BDFE- refs = averaged O-H sites within one measurement;
    # must NOT be treated as a concordance-mean row
    out = run([
        row(entry_id="BDFE-0001", couple_id="CPL-0001", compound="A", solvent="MeCN",
            BDFE="60.0", flags="avg", method="OCP", year="2022"),
        row(entry_id="BDFE-0002", couple_id="CPL-0001", compound="A", solvent="MeCN",
            BDFE="60.2", flags="avg", method="OCP", year="2024"),
    ])
    assert out["BDFE-0002"] == "auto" and out["BDFE-0001"] == "", out

def test_single_row_couple_untouched():
    out = run([row(entry_id="BDFE-0001", couple_id="CPL-0001", compound="A",
                   solvent="MeCN", BDFE="60.0", method="equil", year="2024")])
    assert out["BDFE-0001"] == "", out

def test_idempotent_auto_cleared_and_reassigned():
    rows = [
        row(entry_id="BDFE-0001", couple_id="CPL-0001", compound="A", solvent="MeCN",
            BDFE="60.0", method="equil", year="2020", recommended="auto"),
        row(entry_id="BDFE-0002", couple_id="CPL-0001", compound="A", solvent="MeCN",
            BDFE="60.1", method="sq", year="2024"),
    ]
    out = run(rows)
    assert out["BDFE-0001"] == "auto" and out["BDFE-0002"] == "", out

if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                fn(); print(f"PASS {name}")
            except AssertionError as e:
                fails += 1; print(f"FAIL {name}: {e}")
    sys.exit(1 if fails else 0)
