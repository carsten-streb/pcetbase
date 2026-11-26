#!/usr/bin/env python3
"""Mutation tests for check_release.py (board H159; CR-2026-11-20-automated-review-loop).
Copies the release files to a temp dir, applies one mutation per case, runs
check_release.py --strict there and asserts the exit code and message.
The first five failing cases reproduce historical review blockers.
Run: python test_release.py"""
import os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = ["CITATION.cff", ".zenodo.json", "build.py", "index.html", "CHANGELOG.md",
         "check_release.py", "data/data.csv", "data/provenance_batches.csv"]


def sub(rel, old, new, count=1):
    def f(t):
        p = os.path.join(t, rel)
        s = open(p, encoding="utf-8").read()
        assert old in s, f"mutation anchor not found in {rel}: {old[:60]}"
        open(p, "w", encoding="utf-8").write(s.replace(old, new, count))
    return f


def sub_re(rel, pattern, new):
    def f(t):
        p = os.path.join(t, rel)
        s = open(p, encoding="utf-8").read()
        s2, n = re.subn(pattern, new, s, count=1, flags=re.M)
        assert n == 1, f"mutation pattern not found in {rel}: {pattern}"
        open(p, "w", encoding="utf-8").write(s2)
    return f


def set_doi(eid, doi):
    def f(t):
        import csv
        p = os.path.join(t, "data", "data.csv")
        rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
        head = list(rows[0].keys())
        for r in rows:
            if r["entry_id"] == eid:
                r["doi"] = doi
        with open(p, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=head); w.writeheader(); w.writerows(rows)
    return f


def both(*fs):
    def f(t):
        for g in fs:
            g(t)
    return f


def run_case(name, mutate, expect_fail, msg=None):
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "data"))
    for rel in FILES:
        shutil.copy(os.path.join(HERE, rel), os.path.join(tmp, rel))
    mutate(tmp)
    pr = subprocess.run([sys.executable, os.path.join(tmp, "check_release.py"), "--strict", "--root", tmp],
                        capture_output=True, text=True)
    ok = (pr.returncode != 0) if expect_fail else (pr.returncode == 0)
    if "Traceback" in pr.stderr:
        ok = False
    if msg and not re.search(msg, pr.stdout):
        ok = False
    print(("PASS " if ok else "FAIL ") + name + f" (exit {pr.returncode})"
          + ("" if ok else "\n" + pr.stdout[-600:] + pr.stderr[-600:]))
    shutil.rmtree(tmp)
    return ok


def main():
    cases = [
        ("unchanged release files pass", lambda t: None, False, r"release metadata OK"),
        ("review-pr-83 B1: unescaped quotes in .zenodo.json fail",
         sub(".zenodo.json", "“Corrections to the v1.6 archive”", '"Corrections to the v1.6 archive"'),
         True, r"\.zenodo\.json does not parse as JSON"),
        ("review-pr-83 B2: CITATION.cff v1.7 with the v1.6 version DOI fails",
         sub("CITATION.cff", "doi: 10.5281/zenodo.24121910\n", "doi: 10.5281/zenodo.24293136\n"),
         True, r"top-level doi 10\.5281/zenodo\.24293136 is the v1\.6 version DOI"),
        ("review-pr-72 B2: CITATION.cff with the v1.5 version DOI fails",
         sub("CITATION.cff", "doi: 10.5281/zenodo.24121910\n", "doi: 10.5281/zenodo.24222265\n"),
         True, r"is the v1\.5 version DOI"),
        ("review-pr-70 B1: BDFE-0525 back in the Warren review-table batch fails",
         sub("data/provenance_batches.csv", "BDFE-0524,BDFE-0524,", "BDFE-0524,BDFE-0525,"),
         True, r"ledger: BDFE-0525 has primary doi 10\.1021/ja1047818 but sits in the review batch BDFE-0524\.\.0525"),
        ("a primary DOI on an unlisted Agarwal review-table row fails",
         set_doi("BDFE-0001", "10.1021/ja1047818"),
         True, r"ledger: BDFE-0001 has primary doi"),
        ("CITATION.cff that fails the CFF schema fails (cffconvert)",
         sub_re("CITATION.cff", r'^date-released: "[^"]*"', 'date-released: "20 November 2026"'),
         True, r"CITATION\.cff fails cffconvert --validate"),
        ("version mismatch .zenodo.json 1.6 vs 1.7 fails",
         sub(".zenodo.json", '"version": "1.7"', '"version": "1.6"'),
         True, r"version strings differ: .*\.zenodo\.json 1\.6"),
        ("version mismatch in the newest CHANGELOG heading fails",
         sub("CHANGELOG.md", "## v1.7 — ", "## v1.7.1 — "),
         True, r"version strings differ: .*CHANGELOG newest version heading 1\.7\.1"),
        ("version mismatch in build.py RELEASE fails",
         sub("build.py", 'RELEASE = {"version": "1.7"', 'RELEASE = {"version": "1.8"'),
         True, r"version strings differ: .*build\.py RELEASE 1\.8"),
        ("version mismatch in the built footer stamp fails",
         sub("index.html", "measurements, release v1.7, data", "measurements, release v1.6, data"),
         True, r"version strings differ: .*index\.html footer stamp 1\.6"),
        ("a development-state stamp naming the same release passes",
         sub("index.html", "547 measurements, release v1.7, data 3afe3771",
             "548 measurements — development state after v1.7 (release v1.7: 547 measurements, doi:x), data 00000000"),
         False, r"release metadata OK"),
        ("CITATION.cff doi that is neither concept nor RELEASE doi fails",
         sub("CITATION.cff", "doi: 10.5281/zenodo.24121910\n", "doi: 10.5281/zenodo.11111111\n"),
         True, r"neither the concept DOI nor build\.py RELEASE doi"),
        ("after the DOI-reference PR: version DOI in RELEASE and CITATION.cff passes",
         both(sub("build.py", '"doi": "minted on Zenodo after archiving"', '"doi": "10.5281/zenodo.99999999"'),
              sub("CITATION.cff", "doi: 10.5281/zenodo.24121910\n", "doi: 10.5281/zenodo.99999999\n")),
         False, r"release metadata OK"),
        ("an Unreleased section above the newest version heading passes (main after release)",
         sub("CHANGELOG.md", "## v1.7 — ", "## Unreleased (toward v1.8)\n- nothing yet\n\n## v1.7 — "),
         False, r"release metadata OK"),
    ]
    fails = sum(0 if run_case(*c) else 1 for c in cases)
    print(f"\n{len(cases)-fails}/{len(cases)} release-check cases pass")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
