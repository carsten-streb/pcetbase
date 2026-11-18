"""Fig 4 - coverage/gap map: stacked recommended-couple counts per 5 kcal/mol bin,
by class, MeCN + H2O; separate strip for effective ox/base + red/acid pairs.
Bin parameters adjustable by the 5.3 analysis MC (claude/analysis-brief-5-3.md)."""
import matplotlib.pyplot as plt
from figcommon import (load_rows, recommended_per_couple, CLASS_COLORS, CLASS_LABELS,
                       provenance, save, is_bounded)

BIN_LO, BIN_HI, BIN_W = 5, 110, 5  # BIN_LO 20 -> 5 (CR-2026-11-14-manuscript-figures F-3)

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
        # F-3: computed window brackets replace the per-bin grey shading.
        # Well-characterized subset: recommended discrete couples without
        # estimated/limit/unverified legs; gaps >= 5 kcal/mol between adjacent
        # couples are bracketed, and non-well-characterized couples inside a
        # bracket appear as a hatched "estimated legs only" band.
        SOFT = ("approx", "limit", "check-src", "lowprec", "dmso-unc")
        # EP-02: bounded couples are excluded from the window code (neither bracket end nor band)
        nb = [r for r in discrete if r["class"] != "co2" and is_bounded(r)]
        print(f"{sv}: bounded couples excluded from the window code: {len(nb)} ({', '.join(r['entry_id'] for r in nb)})")
        disc = [r for r in discrete if r["class"] != "co2" and not is_bounded(r)]
        wc = sorted([r for r in disc if not any(f in r["flags"] for f in SOFT)],
                    key=lambda r: r["_bdfe"])
        est = [r for r in disc if any(f in r["flags"] for f in SOFT)]
        ymax0 = max(bottom + [1])
        ybr = ymax0 * 1.02
        for i in range(len(wc) - 1):
            loE, hiE = wc[i], wc[i + 1]
            if hiE["_bdfe"] - loE["_bdfe"] < 5: continue
            x0, x1 = loE["_bdfe"], hiE["_bdfe"]
            ax.plot([x0, x0, x1, x1], [ybr - ymax0 * 0.04, ybr, ybr, ybr - ymax0 * 0.04],
                    color="0.25", lw=0.8, clip_on=False)
            ax.text((x0 + x1) / 2, ybr + ymax0 * 0.03, f"{x0:.1f}–{x1:.1f}",
                    fontsize=5.5, ha="center", va="bottom", color="0.25")
            print(f"bracket {sv}: {x0:.1f} ({loE['entry_id']}) – {x1:.1f} ({hiE['entry_id']})")
            inside = [r for r in est if x0 < r["_bdfe"] < x1]
            if inside:
                bx0 = min(r["_bdfe"] for r in inside); bx1 = max(r["_bdfe"] for r in inside)
                if bx1 - bx0 < 0.6: bx0, bx1 = bx0 - 0.3, bx1 + 0.3
                # band top stays below the bracket and its range label; the label sits
                # beside the band, not on it (review-manuscript-v1.6 B3)
                ytop = (ybr - ymax0 * 0.08) / (ymax0 * 1.15 * 1.12)
                ax.axvspan(bx0, bx1, ymax=ytop, facecolor="none", edgecolor="0.45",
                           hatch="////", lw=0.4, zorder=0)
                ax.text(bx1 + 0.8, ymax0 * 0.45, "estimated\nlegs only",
                        fontsize=5, ha="left", va="center", color="0.35")
        # effective-pair strip above the stacks
        ymax = max(bottom + [1]) * 1.15
        for r in pairs:
            ax.plot(r["_bdfe"], ymax, marker="v", ms=4, color=CLASS_COLORS["pair"],
                    mec="white", mew=0.3, clip_on=False)
        ax.text(0.995, 0.97, f"{sv} · {len(discrete)} couples + {len(pairs)} effective pairs (▼, BDFE_eff tunable)",
                transform=ax.transAxes, fontsize=6.5, ha="right", va="top")
        ax.set_ylabel("★ couples / bin"); ax.set_ylim(0, ymax * 1.12)
    axes[1].set_xlabel("BDFE (kcal mol$^{-1}$)"); axes[1].set_xlim(BIN_LO, BIN_HI)
    h, l = axes[0].get_legend_handles_labels()
    # legend below the axes: inside the H2O panel it covered the hatched band (B3)
    fig.legend(h, l, fontsize=5.5, ncol=5, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, 0.0))
    fig.suptitle("Reagent-space coverage (recommended couples; brackets = windows ≥ 5 kcal/mol between well-characterized couples)", fontsize=8.5)
    fig.tight_layout(rect=(0, 0.07, 1, 0.97))
    provenance(fig, "scripts/figures/fig4.py")
    save(fig, "fig4")

if __name__ == "__main__":
    main()
