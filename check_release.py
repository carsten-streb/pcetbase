#!/usr/bin/env python3
"""Release-metadata and ledger check (CR-2026-11-20-automated-review-loop, change 1; board H159).

Fails (exit 1, one line per problem) when
  1. .zenodo.json does not parse as JSON;
  2. CITATION.cff does not validate (cffconvert --validate; required with --strict);
  3. the CITATION.cff top-level doi is not allowed: allowed are the concept DOI and, once
     the DOI-reference PR has filled it, the DOI in build.py RELEASE["doi"]; a version DOI
     from VERSION_DOIS is accepted only for its own version, also in RELEASE["doi"]
     (review-pr-83 N7);
  4. the version string differs between CITATION.cff, .zenodo.json, build.py RELEASE,
     the footer stamp of the built index.html and the newest versioned CHANGELOG heading;
  5. ledger: a row with a primary DOI sits in a review batch of data/provenance_batches.csv
     without being listed in REVIEW_VALUE_WITH_PRIMARY_DOI below (lesson review-pr-70 B1:
     a corrected row whose values now come from a primary kept its review-table batch line).

Run: python check_release.py [--strict] [--root DIR]
build.py runs it without --strict (the cffconvert step is skipped if cffconvert is not
installed); CI runs it with --strict.
"""
import csv, json, os, re, subprocess, sys

CONCEPT_DOI = "10.5281/zenodo.24121910"
# Version DOIs of published releases (DOI chain). Each DOI is accepted (CITATION.cff top-level
# doi, build.py RELEASE["doi"]) only while the release version is its own version, so a
# release-prep PR that keeps the previous DOI fails. Add each new version DOI here in its
# DOI-reference PR.
VERSION_DOIS = {
    "10.5281/zenodo.24137124": "v1.3",
    "10.5281/zenodo.24175058": "v1.4",
    "10.5281/zenodo.24186854": "v1.4.1",
    "10.5281/zenodo.24222265": "v1.5",
    "10.5281/zenodo.24293136": "v1.6",
    "10.5281/zenodo.24563718": "v1.7",
}
# Rows inside a review batch whose doi field names the primary paper while the stored values
# are the review's tabulated values (doi = attribution; checked against the primary where the
# conditions say so). Any other primary-DOI row in a review batch fails: either it belongs to a
# primary batch line of its own, or a curator adds it here with the reason.
REVIEW_VALUE_WITH_PRIMARY_DOI = {
    "BDFE-0099": "Agarwal 2022 Table 23 value; legs page-verified in Gupta & Borovik 2003",
    "BDFE-0100": "Agarwal 2022 Table 23 value; legs page-verified in Gupta & Borovik 2003",
    "BDFE-0105": "Agarwal 2022 Table 23 value; doi names the primary (EP-08 rename)",
    "BDFE-0132": "Agarwal 2022 Table 23 value; primary cited in conditions",
    "BDFE-0133": "Agarwal 2022 Table 23 value; page-verified vs Dhar 2016",
    "BDFE-0134": "Agarwal 2022 Table 23 value; page-verified vs Dhar 2015",
    "BDFE-0427": "Wiedner 2016 SI value; primary named in conditions",
    "BDFE-0524": "Warren 2010 Table 21 value; primary named in conditions",
}


def read(root, rel):
    return open(os.path.join(root, rel), encoding="utf-8").read()


def check(root, strict):
    err = []
    # 1 .zenodo.json
    zen = None
    try:
        zen = json.loads(read(root, ".zenodo.json"))
    except Exception as e:
        err.append(f".zenodo.json does not parse as JSON: {e}")
    cff = read(root, "CITATION.cff")
    # 2 cffconvert (CLI)
    import shutil
    exe = shutil.which("cffconvert")
    if not exe:
        if strict:
            err.append("cffconvert is not installed (pip install cffconvert); --strict needs it")
        else:
            print("note: cffconvert not installed; CITATION.cff schema check skipped (CI runs it)")
    else:
        pr = subprocess.run([exe, "--validate", "-i", os.path.join(root, "CITATION.cff")],
                            capture_output=True, text=True)
        if pr.returncode != 0:
            lines = [l for l in (pr.stdout + pr.stderr).strip().splitlines() if l.strip()]
            err.append("CITATION.cff fails cffconvert --validate: " + (lines[-1] if lines else "?"))
    # build.py RELEASE dict
    bp = read(root, "build.py")
    rv = re.search(r'RELEASE = \{"version": "([^"]+)"', bp)
    rd = re.search(r'RELEASE = \{[^}]*?"doi": "([^"]*)"', bp, re.S)
    rel_ver = rv.group(1) if rv else None
    rel_doi = rd.group(1) if rd else ""
    if not rel_ver:
        err.append("build.py: RELEASE version not found")
    # 3 CITATION.cff doi
    m = re.search(r"^doi:\s*(\S+)", cff, re.M)
    cdoi = m.group(1).strip('"') if m else None
    cur = f"v{rel_ver}" if rel_ver else None
    allowed = {CONCEPT_DOI}
    if re.match(r"10\.\d{4,}/", rel_doi):
        if VERSION_DOIS.get(rel_doi, cur) != cur:
            err.append(f"build.py: RELEASE doi {rel_doi} is the {VERSION_DOIS[rel_doi]} version DOI, "
                       f"but RELEASE version is {rel_ver}; reset it until the DOI-reference PR")
        else:
            allowed.add(rel_doi)
    if cdoi is None:
        err.append("CITATION.cff: no top-level doi")
    elif VERSION_DOIS.get(cdoi, cur) != cur:
        err.append(f"CITATION.cff: top-level doi {cdoi} is the {VERSION_DOIS[cdoi]} version DOI; "
                   f"use the concept DOI {CONCEPT_DOI} until the DOI-reference PR")
    elif cdoi not in allowed:
        err.append(f"CITATION.cff: top-level doi {cdoi} is neither the concept DOI nor build.py RELEASE doi ({rel_doi})")
    # 4 version strings
    vers = {}
    m = re.search(r'^version:\s*"?([^"\n]+)"?', cff, re.M)
    vers["CITATION.cff"] = m.group(1).strip() if m else None
    vers[".zenodo.json"] = str(zen.get("version")) if isinstance(zen, dict) else None
    vers["build.py RELEASE"] = rel_ver
    # the footer stamp (build.py): "N measurements, release vX, data h", "... release vX data h,
    # code changed ..." or "N measurements — development state after vX (...)"
    m = re.search(r"\d+ measurements(?:, release v| — development state after v)(\d[\w.]*)",
                  read(root, "index.html"))
    vers["index.html footer stamp"] = m.group(1) if m else None
    m = re.search(r"^## v(\d[\w.]*)", read(root, "CHANGELOG.md"), re.M)
    vers["CHANGELOG newest version heading"] = m.group(1) if m else None
    if len(set(vers.values())) != 1:
        err.append("version strings differ: " + "; ".join(f"{k} {v}" for k, v in vers.items()))
    # 5 ledger
    rows = list(csv.DictReader(open(os.path.join(root, "data", "data.csv"), encoding="utf-8")))
    batches = list(csv.DictReader(open(os.path.join(root, "data", "provenance_batches.csv"), encoding="utf-8")))
    num = lambda e: int(e.split("-")[1])
    review = []
    for b in batches:
        if b["source_type"].startswith("review"):
            dois = set(re.findall(r"10\.\d{4,}/[^\s),;]+", b["source_locator"]))
            review.append((num(b["range_start"]), num(b["range_end"]), b["source_locator"][:60], dois))
    review_dois = set().union(*(d for *_, d in review)) if review else set()
    for r in rows:
        n, doi = num(r["entry_id"]), r.get("doi", "").strip()
        for s, e, loc, dois in review:
            if s <= n <= e and doi and doi not in review_dois and r["entry_id"] not in REVIEW_VALUE_WITH_PRIMARY_DOI:
                err.append(f"ledger: {r['entry_id']} has primary doi {doi} but sits in the review batch "
                           f"BDFE-{s:04d}..{e:04d} ({loc}); give it its own primary batch line or list it "
                           f"in check_release.py REVIEW_VALUE_WITH_PRIMARY_DOI")
    return err, vers


def main():
    strict = "--strict" in sys.argv
    root = os.path.dirname(os.path.abspath(__file__))
    if "--root" in sys.argv:
        root = sys.argv[sys.argv.index("--root") + 1]
    err, vers = check(root, strict)
    for e in err:
        print("RELEASE CHECK ERROR: " + e)
    if err:
        sys.exit(1)
    print(f"release metadata OK (version {vers['CITATION.cff']} in CITATION.cff, .zenodo.json, "
          f"RELEASE, footer, CHANGELOG); ledger OK")


if __name__ == "__main__":
    main()
