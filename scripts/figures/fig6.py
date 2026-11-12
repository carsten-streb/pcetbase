"""Fig 6 - POM / TM-hydride region. (a) MeCN ladder zoom 40-75 with dopant grouping
and PVW11 inset; (b) TMH M-H strip on the same axis with the Rh(Cp*)(ppy)H
sq/hyd cross-closure dumbbell (BDFE-0474/0475)."""
import matplotlib.pyplot as plt
from figcommon import load_rows, CLASS_COLORS, provenance, save

def main():
    rows = [r for r in load_rows() if r["solvent"] == "MeCN" and r["_bdfe"]]
    pom = [r for r in rows if r["_cls"] == "pom"]
    tmh = [r for r in rows if r["_cls"] == "tmh"]

    fig, (ax, axb) = plt.subplots(1, 2, figsize=(7.08, 4.6), sharey=True,
                                  gridspec_kw={"width_ratios": (2.2, 1)})
    # (a) POM zoom with dopant-axis grouping
    groups = [("V-doped Keggin", lambda n: ("VW11" in n or "PV" in n or "SiV" in n or "SV" in n or "VW12" in n)),
              ("Ti-POT", lambda n: "{Ti" in n),
              ("parent frames", lambda n: n.startswith("[PW12") or n.startswith("[PMo12")),
              ("V6 / other", lambda n: True)]
    assigned = set()
    for gi, (label, test) in enumerate(groups):
        xs = 0.5 + gi
        members = [r for r in pom if r["entry_id"] not in assigned and test(r["compound"])]
        for r in members:
            assigned.add(r["entry_id"])
            if not (40 <= r["_bdfe"] <= 75): continue
            star = "★ " if r["_rec"] else ""
            ax.hlines(r["_bdfe"], xs - 0.38, xs + 0.38, color=CLASS_COLORS["pom"],
                      lw=1.3 if r["_rec"] else 0.8, alpha=0.95 if r["_rec"] else 0.55)
        ax.text(xs, 39.1, label, fontsize=6, ha="center", va="top", rotation=0)
        # V6-TRIOL mini-series connected
        v6 = sorted([r for r in members if "V6" in r["compound"] and 40 <= r["_bdfe"] <= 75],
                    key=lambda r: r["_bdfe"])
        if len(v6) > 1:
            ax.plot([xs] * len(v6), [r["_bdfe"] for r in v6], color=CLASS_COLORS["pom"],
                    lw=0.5, ls=":", marker="o", ms=2)
    ax.set_xlim(0, len(groups)); ax.set_xticks([])
    ax.set_ylim(40, 75); ax.set_ylabel("BDFE (kcal mol$^{-1}$)")
    ax.set_title("(a) POM region, MeCN", fontsize=8, loc="left")
    # PVW11 inset: the discordant 1st-H couple only (3 independent determinations)
    starred = [r for r in rows if r["_cls"] == "pom" and r["_rec"]
               and "HPVW11" in r["compound"] and "1st H" in r["compound"]]
    pvw = [r for r in rows if starred and r["couple_id"] == starred[0]["couple_id"]]
    if pvw:
        ins = ax.inset_axes((0.56, 0.60, 0.42, 0.36))
        ins.set_facecolor("white"); ins.set_zorder(5); ins.patch.set_alpha(1.0)
        pvw = sorted(pvw, key=lambda r: (r["year"], r["entry_id"]))
        for i, r in enumerate(pvw):
            ins.errorbar(i, r["_bdfe"], yerr=float(r["sigma_BDFE"]) if r["sigma_BDFE"] else None,
                         fmt="o", ms=3, color=CLASS_COLORS["pom"], capsize=2)
            if r["_rec"]: ins.annotate("★", (i, r["_bdfe"]), fontsize=7,
                                       xytext=(3, 1), textcoords="offset points")
        ins.set_xticks(range(len(pvw)), [f'{r["year"]}\n{r["method"]}' for r in pvw], fontsize=4.5)
        ins.set_xlim(-0.5, len(pvw) - 0.5)
        ins.tick_params(labelsize=5)
        ins.set_title("[HPVW11O40]⁴⁻ 1st H · discordant ⚠", fontsize=5.5)
    # (b) TMH strip + Rh dumbbell
    rh = {r["entry_id"]: r for r in tmh if r["entry_id"] in ("BDFE-0474", "BDFE-0475")}
    for r in tmh:
        if r["entry_id"] in rh: continue
        if not (40 <= r["_bdfe"] <= 75): continue
        axb.hlines(r["_bdfe"], 0.15, 0.85, color=CLASS_COLORS["tmh"],
                   lw=1.3 if r["_rec"] else 0.7, alpha=0.95 if r["_rec"] else 0.5)
    if len(rh) == 2:
        y1, y2 = rh["BDFE-0474"]["_bdfe"], rh["BDFE-0475"]["_bdfe"]
        axb.plot([1.1, 1.1], [y1, y2], color="0.15", lw=1.2)
        axb.plot([1.1], [y1], marker="o", color="0.15", ms=4)
        axb.plot([1.1], [y2], marker="o", mfc="white", mec="0.15", ms=4)
        axb.annotate("Rh(Cp*)(ppy)H\nsq vs hyd closure\nΔ = %.1f" % abs(y1 - y2),
                     (1.18, (y1 + y2) / 2), fontsize=5.5, va="center")
    axb.set_xlim(0, 2); axb.set_xticks([])
    axb.text(0.04, 0.02, f"n = {len([r for r in tmh if 40 <= r['_bdfe'] <= 75])}",
             transform=axb.transAxes, fontsize=6.5, color="0.35")
    axb.set_title("(b) TM hydrides (M–H)", fontsize=8, loc="left")
    fig.tight_layout()
    provenance(fig, "scripts/figures/fig6.py")
    save(fig, "fig6")

if __name__ == "__main__":
    main()
