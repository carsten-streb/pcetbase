"""Fig 6 - POM / TM-hydride region. (a) MeCN ladder zoom 40-75 with dopant grouping
and PVW11 inset; (b) dumbbell of every multi-member couple at the data tag
(CR-2026-11-14-manuscript-figures F-4): x = BDFE - recommended, marker by method,
open marker = sim-pKa, diamond suffix = discordant couple."""
import csv, os
import matplotlib.pyplot as plt
from figcommon import ROOT, load_rows, CLASS_COLORS, provenance, save, display_name, mathname

def main():
    rows = [r for r in load_rows() if r["solvent"] == "MeCN" and r["_bdfe"]]
    pom = [r for r in rows if r["_cls"] == "pom"]
    tmh = [r for r in rows if r["_cls"] == "tmh"]

    fig, (ax, axb) = plt.subplots(1, 2, figsize=(7.08, 4.6),
                                  gridspec_kw={"width_ratios": (1.5, 1.3)})
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
        # lower part of the "V6 / other" column (x 0.75-1.0 of the axes) is empty below
        # 58 kcal/mol; the inset sits there so no ladder line is covered (review-manuscript-v1.6 B2)
        ins = ax.inset_axes((0.785, 0.075, 0.2, 0.37))
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
        ins.set_title(mathname("H[PVW11O40]4-") + "\ndiscordant couple", fontsize=5.5)
    # (b) F-4: one row per multi-member couple (computed, no hard-coded IDs)
    with open(os.path.join(ROOT, "data", "couples.csv"), newline="", encoding="utf-8") as f:
        cmeta = {c["couple_id"]: c for c in csv.DictReader(f)}
    from collections import defaultdict
    g = defaultdict(list)
    for r in load_rows():
        if r["_bdfe"] is not None and r["couple_id"]:
            g[r["couple_id"]].append(r)
    multi = {cid: ms for cid, ms in g.items() if len(ms) > 1}
    npts = sum(len(ms) for ms in multi.values())
    print(f"panel b: {len(multi)} multi-member couples, {npts} points")
    order = sorted(multi.items(), key=lambda kv: (kv[1][0]["_cls"] != "pom", min(m["_bdfe"] for m in kv[1])))
    MK = {"sq": "o", "hyd": "s", "OCP": "^", "equil": "D", "hess": "v", "": "."}
    for yi, (cid, ms) in enumerate(order):
        rec = next((m for m in ms if m["_rec"]), ms[0])
        col = "0.45" if ms[0]["_cls"] == "pom" else CLASS_COLORS.get(ms[0]["_cls"], "0.2")
        dx = [m["_bdfe"] - rec["_bdfe"] for m in ms]
        axb.plot([min(dx), max(dx)], [yi, yi], color=col, lw=0.7, alpha=0.6, zorder=1)
        for m in ms:
            x = m["_bdfe"] - rec["_bdfe"]
            open_mk = "sim-pKa" in m["flags"]
            err = float(m["sigma_BDFE"]) if m["sigma_BDFE"] else None
            axb.errorbar(x, yi, xerr=err, fmt=MK.get(m["method"], "."), ms=4,
                         mfc="white" if open_mk else col, mec=col, color=col,
                         elinewidth=0.6, capsize=1.5, zorder=2)
            if abs(x) > 3 or x < -4:
                pass
        name = display_name(ms[0]["compound"])
        disc = "◆ " if cmeta.get(cid, {}).get("discordant") == "1" else ""
        # discordant marker drawn as its own plain-text label: inside a mathtext
        # string the glyph falls back to a placeholder
        if disc:
            axb.annotate("◆", xy=(0, yi), xytext=(3, 4), textcoords="offset points",
                         fontsize=4.3, color="0.25", fontfamily="DejaVu Sans")
        axb.annotate(f"{name} · {cid}", xy=(0, yi), xytext=(8.5 if disc else 3, 4),
                     textcoords="offset points", fontsize=4.3, color="0.25")
    axb.axvline(0, color="0.8", lw=0.7, zorder=0)
    axb.set_yticks([])
    axb.set_xlabel("BDFE − recommended (kcal mol$^{-1}$)")
    axb.set_ylim(-3.6, len(order) - 0.1)
    hs = [plt.Line2D([], [], marker=MK[m], ls="", mec="0.2", mfc="0.2", ms=4, label=m) for m in ("sq", "hyd", "OCP", "equil")]
    hs.append(plt.Line2D([], [], marker="o", ls="", mec="0.2", mfc="white", ms=4, label="sim-pKa"))
    axb.legend(handles=hs, fontsize=4.8, frameon=False, loc="lower center", ncol=3)
    axb.set_title(f"(b) multi-member couples (n = {len(order)}; grey = POM, ◆ = discordant)", fontsize=7.5, loc="left")
    fig.tight_layout()
    provenance(fig, "scripts/figures/fig6.py")
    save(fig, "fig6")

if __name__ == "__main__":
    main()
