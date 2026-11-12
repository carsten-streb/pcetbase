"""Fig 3 - audit: eq 18 residual histogram, sigma by solvent, sigma by class, case boxes."""
import statistics
import matplotlib.pyplot as plt
from figcommon import load_rows, load_analysis, CLASS_COLORS, provenance, save

CASES = [  # writer-final case boxes: 5.1 cases 1, 3, 5, 8
    ("Case 1 · Hess error", "Fe(H₂O)₆²⁺: printed Hess E° does not close (Δ ≈ 0.09 V)"),
    ("Case 3 · transcription swap", "CO₂/CH₄: MeCN and DMF BDFE values exactly swapped vs their E°"),
    ("Case 5 · closure failure", "Shiels 2024: printed 63.8 recomputes to 63.3; citing paper propagates misquotes"),
    ("Case 8 · constants obsolescence", "Fertig 2021 quotes aqueous HPV₂W₁₀ value as MeCN: 4.8 kcal mol⁻¹ shift"),
]

def main():
    ana = load_analysis()
    meta = {r["entry_id"]: r for r in load_rows()}
    prim, revw = [], []
    for a in ana:
        if not a["eq18_residual_kcal"]: continue
        v = float(a["eq18_residual_kcal"])
        (prim if meta[a["entry_id"]]["doi"] else revw).append(v)

    fig = plt.figure(figsize=(7.08, 5.2))
    gs = fig.add_gridspec(2, 2, height_ratios=(1.15, 1), hspace=0.45, wspace=0.3)
    ax_a = fig.add_subplot(gs[0, 0]); ax_b = fig.add_subplot(gs[0, 1]); ax_c = fig.add_subplot(gs[1, 0])

    bins = [x / 10 for x in range(-12, 13)]
    ax_a.hist(revw, bins=bins, color="0.6", alpha=0.7, label=f"review-tabulated (n={len(revw)})")
    ax_a.hist(prim, bins=bins, color="#e34948", alpha=0.7, label=f"primary/recomputed (n={len(prim)})")
    ax_a.set_xlabel("eq 18 residual (kcal mol$^{-1}$)"); ax_a.set_ylabel("entries")
    ax_a.legend(fontsize=6, frameon=False); ax_a.set_title("(a) closure residuals", fontsize=8, loc="left")

    by_solv = {}
    for a in ana:
        if a["eq18_residual_kcal"]:
            by_solv.setdefault(a["solvent"], []).append(float(a["eq18_residual_kcal"]))
    solvs = [s for s, v in sorted(by_solv.items(), key=lambda kv: -len(kv[1])) if len(v) >= 5]
    ax_b.bar(range(len(solvs)), [statistics.pstdev(by_solv[s]) for s in solvs], color="0.45")
    ax_b.set_xticks(range(len(solvs)), solvs, rotation=45, ha="right", fontsize=6)
    ax_b.set_ylabel("σ(eq 18 residual)"); ax_b.set_title("(b) by solvent (n ≥ 5)", fontsize=8, loc="left")

    by_cls = {}
    for a in ana:
        if a["eq18_residual_kcal"]:
            by_cls.setdefault(meta[a["entry_id"]]["_cls"], []).append(float(a["eq18_residual_kcal"]))
    clss = [c for c, v in sorted(by_cls.items(), key=lambda kv: -len(kv[1])) if len(v) >= 5]
    ax_c.bar(range(len(clss)), [statistics.pstdev(by_cls[c]) for c in clss],
             color=[CLASS_COLORS.get(c, "0.45") if c == "pom" else "0.6" for c in clss])
    ax_c.set_xticks(range(len(clss)), clss, rotation=45, ha="right", fontsize=6)
    ax_c.set_ylabel("σ(eq 18 residual)"); ax_c.set_title("(c) by class (POM highlighted)", fontsize=8, loc="left")

    ax_d = fig.add_subplot(gs[1, 1]); ax_d.axis("off")
    y = 1.0
    for title, body in CASES:
        ax_d.text(0, y, title, fontsize=6.5, fontweight="bold", va="top")
        ax_d.text(0, y - 0.09, body, fontsize=6, va="top", wrap=True)
        y -= 0.26
    ax_d.set_title("(d) named audit cases", fontsize=8, loc="left")

    provenance(fig, "scripts/figures/fig3.py")
    save(fig, "fig3")

if __name__ == "__main__":
    main()
