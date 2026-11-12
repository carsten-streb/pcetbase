"""Fig 2 - ladder overview: H2O / MeCN / DMSO panels, recommended couples only."""
import matplotlib.pyplot as plt
from figcommon import (load_rows, recommended_per_couple, CLASS_COLORS, CLASS_LABELS,
                       provenance, save)

LANDMARK_KEYS = ["TEMPOH", "AscH- (ascorbate)", "hydroperoxyl", "toluene",
                 "[HPVW11O40]4- (1st", "{TiOH} Keggin POT, shell O-H (1st", "phenol ("]
DGH = {"H2O": 52.8, "MeCN": 52.0, "DMSO": 53.4}  # eq 18 secondary axis (Agarwal T1)

def landmarks(sub):
    """One labeled entry per keyword per panel, preferring the starred row."""
    out = []
    for key in LANDMARK_KEYS:
        hits = [r for r in sub if key.lower() in r["compound"].lower()]
        if hits:
            out.append(sorted(hits, key=lambda r: not r["_rec"])[0])
    return out

def main():
    rows = recommended_per_couple(load_rows())
    fig, axes = plt.subplots(1, 3, figsize=(7.08, 4.3), sharey=True)
    for ax, sv in zip(axes, ["H2O", "MeCN", "DMSO"]):
        sub = [r for r in rows if r["solvent"] == sv]
        for r in sub:
            pairish = ("ox-base" in r["flags"]) or ("red-acid" in r["flags"]) or r["_cls"] == "pair"
            ax.hlines(r["_bdfe"], 0.15, 0.85, colors=CLASS_COLORS.get(r["_cls"], "0.3"),
                      lw=1.0, linestyles="dashed" if pairish else "solid", alpha=0.85)
        marked = sorted(landmarks(sub), key=lambda r: r["_bdfe"])
        ylab = None
        for r in marked:
            y = r["_bdfe"]
            ylab = y if ylab is None else max(y, ylab + 3.2)  # min label spacing
            ax.annotate(r["compound"][:22], xy=(0.87, y), xytext=(0.95, ylab),
                        fontsize=5.5, va="center", ha="left", color="0.2",
                        arrowprops=dict(arrowstyle="-", lw=0.4, color="0.55"))
        ax.set_xlim(0, 1.6); ax.set_xticks([])
        ax.set_title(sv, fontsize=9)
        ax.text(0.04, 0.02, f"n = {len(sub)}", transform=ax.transAxes, fontsize=7, color="0.35")
        if sv in DGH:
            sec = ax.secondary_yaxis("right",
                functions=(lambda b, d=DGH[sv]: (b - d) / 23.06,
                           lambda e, d=DGH[sv]: 23.06 * e + d))
            sec.tick_params(labelsize=6)
            if sv == "DMSO": sec.set_ylabel("E° (V vs H₂)", fontsize=7)
    axes[0].set_ylim(15, 115)
    axes[0].set_ylabel("BDFE (kcal mol$^{-1}$)")
    handles = [plt.Line2D([], [], color=c, lw=2, label=CLASS_LABELS[k])
               for k, c in CLASS_COLORS.items()]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=6, frameon=False,
               bbox_to_anchor=(0.5, 0.005))
    fig.suptitle("PCETbase recommended BDFE ladders", fontsize=10)
    fig.tight_layout(rect=(0, 0.15, 1, 0.97))
    provenance(fig, "scripts/figures/fig2.py")
    save(fig, "fig2")

if __name__ == "__main__":
    main()
