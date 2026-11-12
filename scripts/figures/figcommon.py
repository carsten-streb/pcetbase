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
}
CLASS_LABELS = {
    "arylOH": "Phenols & quinones", "noxyl": "N-oxyls", "smallOH": "O–H small molecules",
    "organicNH": "N–H compounds", "otherXH": "C–H / S–H / CO₂", "pair": "Ox/base + red/acid pairs",
    "metal": "TM complexes", "pom": "POM clusters", "tmh": "TM hydrides (M–H)",
}
DISPLAY_MAP = {"phenol":"arylOH","quinone":"arylOH","aminoxyl":"noxyl","imide":"noxyl",
 "ascorbate":"smallOH","smallOH":"smallOH","nucleoside":"organicNH","nitrogen":"organicNH",
 "amine":"organicNH","arylamine":"organicNH","indole":"organicNH","thiol":"otherXH",
 "CH":"otherXH","nicotinamide":"otherXH","co2":"otherXH","pair":"pair","pom":"pom","tmh":"tmh"}

def display_class(raw):
    return "metal" if raw.startswith("metal") else DISPLAY_MAP.get(raw, raw)

def git_ref():
    try:
        return subprocess.check_output(["git", "describe", "--tags", "--always"],
                                       cwd=ROOT, text=True).strip()
    except Exception:
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
