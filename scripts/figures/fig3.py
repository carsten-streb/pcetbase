"""Fig 3 - audit: eq 18 residual histogram, sigma by solvent/class, eq 10
pKa-dependence panel, named case boxes (CR-2026-11-14-manuscript-figures F-2).
Case boxes use the status-doc numbering 1, 3, 5, 6b (writer decision H96)."""
import statistics
import matplotlib.pyplot as plt
from figcommon import load_rows, load_analysis, CLASS_COLORS, provenance, save, display_name, is_bounded, off_ladder

CASES = [  # writer-final case boxes: status-doc cases 1, 3, 5, 6b (labels per CR-2026-11-16-figure-labels-pom)
    ("Case 1 · Hess error", "[Fe(H$_2$O)$_6$]$^{2{+}}$: printed Hess E° does not close (Δ ≈ 0.09 V)"),
    ("Case 3 · transcription swap", "CO$_2$/CH$_4$: MeCN and DMF BDFE values exactly swapped vs their E°"),
    ("Case 5 · closure failure", "Shiels 2024: printed 63.8 kcal mol$^{-1}$ recomputes to 63.3 kcal mol$^{-1}$;\nciting paper propagates misquotes"),
    ("Case 6b · constants obsolescence", "H[PV$_2$W$_{10}$O$_{40}$]$^{5{-}}$: published BDFE on the pre-correction\n$C_\\mathrm{G}$ (75.4 kcal mol$^{-1}$) recomputes to 70.6 kcal mol$^{-1}$ (Δ 4.8 kcal mol$^{-1}$)"),
]

def main():
    meta = {r["entry_id"]: r for r in load_rows()}
    # EP-02: rows with inequality bounds are excluded from all residual statistics
    ana_all = load_analysis()
    ana = [a for a in ana_all if not is_bounded(meta[a["entry_id"]]) and not off_ladder(meta[a["entry_id"]])]
    print(f"no-ladder rows excluded from the statistics (EP-09): "
          f"{', '.join(a['entry_id'] for a in ana_all if off_ladder(meta[a['entry_id']]))}")
    print(f"bounded rows excluded from the statistics: {sum(1 for a in ana_all if is_bounded(meta[a['entry_id']]))} "
          f"({', '.join(a['entry_id'] for a in ana_all if is_bounded(meta[a['entry_id']]))})")
    prim, revw = [], []
    for a in ana:
        if not a["eq18_residual_kcal"]: continue
        v = float(a["eq18_residual_kcal"])
        (prim if meta[a["entry_id"]]["doi"] else revw).append(v)

    fig = plt.figure(figsize=(7.08, 6.6))
    gs = fig.add_gridspec(3, 2, height_ratios=(1.1, 1, 0.62), hspace=0.55, wspace=0.3)
    ax_a = fig.add_subplot(gs[0, 0]); ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0]); ax_d = fig.add_subplot(gs[1, 1])

    bins = [x / 10 for x in range(-12, 13)]
    ax_a.hist(revw, bins=bins, color="0.6", alpha=0.7, label=f"review-tabulated (n={len(revw)})")
    ax_a.hist(prim, bins=bins, color="#e34948", alpha=0.7, label=f"primary/recomputed (n={len(prim)})")
    ax_a.set_xlabel("eq 1 residual (kcal mol$^{-1}$)"); ax_a.set_ylabel("entries")
    ax_a.legend(fontsize=6, frameon=False); ax_a.set_title("(a) closure residuals", fontsize=8, loc="left")

    by_solv = {}
    for a in ana:
        if a["eq18_residual_kcal"]:
            by_solv.setdefault(a["solvent"], []).append(float(a["eq18_residual_kcal"]))
    solvs = [s for s, v in sorted(by_solv.items(), key=lambda kv: -len(kv[1])) if len(v) >= 5]
    ax_b.bar(range(len(solvs)), [statistics.pstdev(by_solv[s]) for s in solvs], color="0.45")
    ax_b.set_xticks(range(len(solvs)), [display_name(s) for s in solvs], rotation=45, ha="right", fontsize=6)
    ax_b.set_ylabel("σ(eq 1 residual) (kcal mol$^{-1}$)"); ax_b.set_title("(b) by solvent (n ≥ 5)", fontsize=8, loc="left")

    by_cls = {}
    for a in ana:
        if a["eq18_residual_kcal"]:
            by_cls.setdefault(meta[a["entry_id"]]["_cls"], []).append(float(a["eq18_residual_kcal"]))
    clss = [c for c, v in sorted(by_cls.items(), key=lambda kv: -len(kv[1])) if len(v) >= 5]
    ax_c.bar(range(len(clss)), [statistics.pstdev(by_cls[c]) for c in clss],
             color=[CLASS_COLORS.get(c, "0.45") if c == "pom" else "0.6" for c in clss])
    ax_c.set_xticks(range(len(clss)), clss, rotation=45, ha="right", fontsize=6)
    ax_c.set_ylabel("σ(eq 1 residual) (kcal mol$^{-1}$)"); ax_c.set_title("(c) by class (POM highlighted)", fontsize=8, loc="left")

    # (d) eq 2 (Bordwell) residual vs pKa for TMH hyd/OCP rows: the 1.364 vs 1.37 factor
    # (selection computed from the data; expect n = 34 at the v1.5 tag)
    pts = []
    for a in ana:
        m = meta[a["entry_id"]]
        if m["class"] == "tmh" and m["method"] in ("hyd", "OCP") and a["eq10_residual_kcal"]:
            pka = m["pKa_b"] or m["pKa_a"]  # form-2 rows close through the oxidized diagonal
            if pka: pts.append((float(pka), float(a["eq10_residual_kcal"])))
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    ax_d.scatter(xs, ys, s=10, color=CLASS_COLORS["tmh"], alpha=0.85, lw=0)
    if xs:
        lo, hi = min(xs), max(xs)
        ax_d.plot([lo, hi], [0.006 * lo, 0.006 * hi], color="0.3", lw=0.9, ls="--")
    ax_d.axhline(0, color="0.8", lw=0.6)
    ax_d.set_xlabel("pK$_a$(XH)"); ax_d.set_ylabel("eq 2 residual (kcal mol$^{-1}$)")
    ax_d.text(0.03, 0.95, "line: 0.006·pK$_a$\n1.364 (hydricity) vs 1.37 (Bordwell) factor",
              transform=ax_d.transAxes, fontsize=5.5, va="top")
    ax_d.set_title(f"(d) hyd/OCP pK$_a$ dependence (n = {len(pts)})", fontsize=8, loc="left")
    mean_res = statistics.mean(ys) if ys else float("nan")
    dev = [abs(y - 0.006 * x) for x, y in pts]
    print(f"panel d: n = {len(pts)}, mean residual {mean_res:+.2f}, max |res - 0.006 pKa| = {max(dev):.3f}" if pts else "panel d empty")

    # (e) named audit cases, spanning the bottom row
    ax_e = fig.add_subplot(gs[2, :]); ax_e.axis("off")
    for i, (title, body) in enumerate(CASES):
        x = 0.0 if i % 2 == 0 else 0.52
        y = 1.0 if i < 2 else 0.42
        ax_e.text(x, y, title, fontsize=6.5, fontweight="bold", va="top")
        ax_e.text(x, y - 0.14, body, fontsize=6, va="top", wrap=True)
    ax_e.set_title("(e) named audit cases", fontsize=8, loc="left")

    n18 = len(prim) + len(revw)
    all18 = prim + revw
    within01 = 100 * sum(1 for v in all18 if abs(v) <= 0.1) / n18
    within03 = 100 * sum(1 for v in all18 if abs(v) <= 0.3) / n18
    n10 = sum(1 for a in ana if a["eq10_residual_kcal"])
    print(f"eq18: n = {n18}, sigma = {statistics.pstdev(all18):.3f}, {within01:.1f}% within 0.1, {within03:.1f}% within 0.3; eq10 n = {n10}")

    provenance(fig, "scripts/figures/fig3.py")
    save(fig, "fig3")

if __name__ == "__main__":
    main()
