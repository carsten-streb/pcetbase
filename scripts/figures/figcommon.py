"""Shared helpers for the PCETbase manuscript figure scripts (CR-2026-11-12-figure-scripts).

Run from anywhere: paths resolve relative to the repo root. Each figX.py writes
figures/figX.svg and figures/figX.png (600 dpi) with a margin provenance line
(git tag/commit + script path) that the writer drops at final composition.
"""
import csv, logging, os, subprocess
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT  = os.path.join(ROOT, "figures")

# Arial per spec; Liberation Sans is the metric-compatible fallback on Linux/CI.
plt.rcParams.update({
    "font.family": ["Arial", "Liberation Sans", "DejaVu Sans"],
    "font.size": 8, "axes.linewidth": 0.8, "svg.fonttype": "none",
})
# mathtext (formula labels, units) in the same sans face as the text
from matplotlib import font_manager as _fm
_avail = {f.name for f in _fm.fontManager.ttflist}
_sans = next((n for n in ("Arial", "Liberation Sans") if n in _avail), "DejaVu Sans")
plt.rcParams.update({"mathtext.fontset": "custom", "mathtext.rm": _sans,
                     "mathtext.it": _sans + ":italic", "mathtext.bf": _sans + ":bold"})

# App palette (template.html light theme), colorblind-checked in the app work.
CLASS_COLORS = {
    "arylOH":   "#2a78d6",  # phenols & quinones
    "noxyl":    "#eb6834",  # N-oxyls
    "smallOH":  "#1baf7a",  # O-H small molecules
    "organicNH":"#eda100",  # N-H compounds
    "otherXH":  "#e87ba4",  # C-H / S-H / CO2
    "pair":     "#008300",  # ox/base + red/acid pairs
    "metal":    "#6250d6",  # TM complexes
    "pom":      "#e34948",  # POM clusters
    "tmh":      "#0d8a86",  # TM hydrides
    "moh":      "#935116",  # metal oxo/hydroxo (M-O-H)
}
CLASS_LABELS = {
    "arylOH": "Phenols & quinones", "noxyl": "N-oxyls", "smallOH": "O–H small molecules",
    "organicNH": "N–H compounds", "otherXH": "C–H / S–H / CO₂", "pair": "Ox/base + red/acid pairs",
    "metal": "TM complexes", "pom": "POM clusters", "tmh": "TM hydrides (M–H)",
    "moh": "Metal oxo/hydroxo (M–O–H)",
}
DISPLAY_MAP = {"phenol":"arylOH","quinone":"arylOH","aminoxyl":"noxyl","imide":"noxyl",
 "ascorbate":"smallOH","smallOH":"smallOH","nucleoside":"organicNH","nitrogen":"organicNH",
 "amine":"organicNH","arylamine":"organicNH","indole":"organicNH","thiol":"otherXH",
 "CH":"otherXH","nicotinamide":"otherXH","co2":"otherXH","pair":"pair","pom":"pom","tmh":"tmh",
 "moh":"moh"}

def display_class(raw):
    return "metal" if raw.startswith("metal") else DISPLAY_MAP.get(raw, raw)

def git_ref():
    """Release version from CITATION.cff (stress CR F2): the watermark names the
    release the figures ship with, independent of when the tag is placed."""
    try:
        with open(os.path.join(ROOT, "CITATION.cff"), encoding="utf-8") as f:
            for line in f:
                if line.startswith("version:"):
                    return "v" + line.split(":", 1)[1].strip().strip('"')
    except Exception:
        pass
    return "unknown"

def load_rows():
    with open(os.path.join(ROOT, "data", "data.csv"), newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["_cls"] = display_class(r["class"])
        r["_bdfe"] = float(r["BDFE"]) if r["BDFE"] else None
        r["_rec"] = r["recommended"] in ("1", "auto")
    return rows

def load_analysis():
    with open(os.path.join(ROOT, "derived", "analysis.csv"), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def recommended_per_couple(rows):
    """One representative row per couple: the starred one, else the single member."""
    from collections import defaultdict
    g = defaultdict(list)
    for r in rows:
        if r["_bdfe"] is None: continue
        g[r["couple_id"] or (r["compound"], r["partner"], r["solvent"])].append(r)
    out = []
    for ms in g.values():
        starred = [r for r in ms if r["_rec"]]
        out.append(starred[0] if starred else ms[0] if len(ms) == 1 else
                   sorted(ms, key=lambda r: r["entry_id"])[0])
    return out

def provenance(fig, script):
    fig.text(0.005, 0.005, f"PCETbase {git_ref()} · {script} · drop at composition",
             fontsize=5, color="0.45", ha="left", va="bottom")

def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, name + ".svg"))
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=600)
    print("wrote figures/%s.svg + .png" % name)

# --- display names for manuscript figures (CR-2026-11-16-figure-labels-pom) ---
# Stored compound names stay as they are; figures show the manuscript notation:
# POM formulae with the protons in front of the bracket, sub/superscripts via
# matplotlib mathtext. Explicit map first, then a generic formatter.
POM_LABELS = {
    "[HPVW11O40]4- (1st H on PVIVW11)": "H[PVW11O40]4-",
    "[HPVW11O40]4-": "H[PVW11O40]4-",
    "[V6O11(OH)2(TRIOLNO2)2]2-": "H2[V6O13(TRIOL^NO2)2]2-",
    "[V6O7(OH)6(TRIOLNO2)2]2-": "H6[V6O13(TRIOL^NO2)2]2-",
    "[V6O9(OH)4(TRIOLNO2)2]2-": "H4[V6O13(TRIOL^NO2)2]2-",
    "[V6O11(OH)2(TRIOLMe)2]2-": "H2[V6O13(TRIOL^Me)2]2-",
    "[V6O9(OH)4(TRIOLMe)2]2-": "H4[V6O13(TRIOL^Me)2]2-",
    "[V6O7(OH)6(TRIOLMe)2]2-": "H6[V6O13(TRIOL^Me)2]2-",
    "[VW5O18(OH)]3-": "H[VW5O19]3-",
    "[HPV2W10O40]": "H[PV2W10O40]5-",
}

import re as _re
def _sub(txt):
    """Digits after a letter or closing bracket become subscripts (mathtext)."""
    return _re.sub(r"(?<=[A-Za-z\)\]])(\d+)", r"_{\1}", txt).replace("*", "^{*}")

def mathname(s):
    """Plain formula -> one matplotlib mathtext string: subscript counts,
    '^X' superscripted (TRIOL substituent, its own counts subscripted),
    trailing charge after the final bracket superscripted with a true minus."""
    charge = ""
    m = _re.search(r"([\]\)])(\d{0,2})([+-])$", s) or _re.search(r"([A-Za-z])()([+-])$", s)
    if m:
        charge = "^{%s{%s}}" % (m.group(2), "-" if m.group(3) == "-" else "+")  # braces: ordinary symbol, no binary-operator spacing
        s = s[:m.start(3) if not m.group(2) else m.start(2)]
    parts = _re.split(r"(\^[A-Za-z0-9]+)", s)
    body = ""
    for part in parts:
        if part.startswith("^"):
            body += "^{\\mathrm{%s}}" % _sub(part[1:])
        else:
            body += "\\mathrm{%s}" % _sub(part).replace("(", "(").replace(" ", "\\ ")
    return "$" + body + charge + "$"

_FORMULA = _re.compile(r"^[A-Za-z0-9()\[\]^*]+(\d{0,2}[+-])?$")
_PREFIX = _re.compile(r"^((?:cis|trans|fac|mer)-)(.*)$")

# descriptive (non-formula) names shortened where the full text collides with the axis
SHORT_LABELS = {"{TiOH} Keggin POT, shell O-H": "{TiOH} Keggin POT"}

def display_name(raw, maxlen=None):
    """Stored compound name -> figure label. POM names go through POM_LABELS
    (proton-in-front form); any other name whose formula part is a plain
    formula gets sub/superscripts; descriptive names stay as plain text.
    maxlen truncates the plain-text remainder only (fig2 label width)."""
    head, sep, tail = raw.partition(" (")
    for k, v in SHORT_LABELS.items():
        if raw.startswith(k):
            return v
    if raw in POM_LABELS or head in POM_LABELS:
        return mathname(POM_LABELS.get(raw, POM_LABELS.get(head)))
    if maxlen is None:
        tail = ""; sep = ""
    pm = _PREFIX.match(head)
    pre, core = (pm.group(1), pm.group(2)) if pm else ("", head)
    if _FORMULA.match(core) and _re.search(r"\d|[+-]$|\*", core):
        rest = (sep + tail) if sep else ""
        if maxlen:
            rest = rest[:max(0, maxlen - len(head))]
        return (r"$\it{%s}$" % pre.rstrip("-") + "-" if pre else "") + mathname(core) + rest
    return (raw[:maxlen] if maxlen else head)
