"""Fig 4 - coverage/gap map: stacked recommended-couple counts per 5 kcal/mol bin,
by class, MeCN + H2O; separate strip for effective ox/base + red/acid pairs.
Bin parameters adjustable by the 5.3 analysis MC (claude/analysis-brief-5-3.md)."""
import matplotlib.pyplot as plt
from figcommon import (load_rows, recommended_per_couple, CLASS_COLORS, CLASS_LABELS,
                       provenance, save)

BIN_LO, BIN_HI, BIN_W = 20, 110, 5  # 5.3 MC may adjust

def main():
    rows = recommended_per_couple(load_rows())
    bins = list(range(BIN_LO, BIN_HI + BIN_W, BIN_W))
    fig, axes = plt.subplots(2, 1, figsize=(7.08, 5.0), sharex=True)
    for ax, sv in zip(axes, ["MeCN", "H2O"]):
        sub = [r for r in rows if r["solvent"] == sv and BIN_LO <= r["_bdfe"] <= BIN_HI]
        pairs = [r for r in sub if r["_cls"] == "pair" or "ox-base" in r["flags"] or "red-acid" in r["flags"]]
        discrete = [r for r in sub if r not in pairs]
        bottom = [0] * (len(bins) - 1)
        for cls, color in CLASS_COLORS.items():
            vals = [r["_bdfe"] for r in discrete if r["_cls"] == cls]
            if not vals: continue
            counts = [sum(1 for v in vals if b <= v < b + BIN_W) for b in bins[:-1]]
            ax.bar([b + BIN_W / 2 for b in bins[:-1]], counts, width=BIN_W * 0.92,
                   bottom=bottom, color=color, label=CLASS_LABELS[cls])
            bottom = [a + c for a, c in zip(bottom, counts)]
        # empty-window annotation
        for i, b in enumerate(bins[:-1]):
            if bottom[i] == 0:
                ax.axvspan(b, b + BIN_W, color="0.92", zorder=0)
        # effective-pair strip above the stacks
        ymax = max(bottom + [1]) * 1.15
        for r in pairs:
            ax.plot(r["_bdfe"], ymax, marker="v", ms=4, color=CLASS_COLORS["pair"],
                    mec="white", mew=0.3, clip_on=False)
        ax.text(0.995, 0.97, f"{sv} · {len(discrete)} couples + {len(pairs)} effective pairs (▼, BDFE_eff tunable)",
                transform=ax.transAxes, fontsize=6.5, ha="right", va="top")
        ax.set_ylabel("★ couples / bin"); ax.set_ylim(0, ymax * 1.12)
    axes[1].set_xlabel("BDFE (kcal mol$^{-1}$)"); axes[1].set_xlim(BIN_LO, BIN_HI)
    axes[0].legend(fontsize=5.5, ncol=3, frameon=False, loc="upper left")
    fig.suptitle("Reagent-space coverage (recommended couples; grey = empty window)", fontsize=9)
    fig.tight_layout(rect=(0, 0.01, 1, 0.97))
    provenance(fig, "scripts/figures/fig4.py")
    save(fig, "fig4")

if __name__ == "__main__":
    main()
