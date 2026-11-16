// PCETbase jsdom app test gate (CR-2026-11-11-jsdom-gate; producer spec, builder-committed)
// Runs against the built index.html. Node 18+, jsdom.
// Usage: node test_app.js path/to/index.html
// NOTE: baseline counts (546 measurements / 530 couples / 14 multi-source
// badges) are asserted literally BY DESIGN - bump them in every data PR;
// this doubles as a tripwire against accidental row loss.
const { JSDOM } = require("jsdom");
const fs = require("fs");

const file = process.argv[2] || "index.html";
const html = fs.readFileSync(file, "utf-8");

let pass = 0, fail = 0;
function T(name, cond, info = "") {
  if (cond) { pass++; console.log("PASS " + name); }
  else { fail++; console.log("FAIL " + name + (info ? "  [" + info + "]" : "")); }
}

function newDom(opts = {}) {
  return new JSDOM(html, {
    runScripts: "dangerously",
    url: "https://carsten-streb.github.io/pcetbase/" + (opts.hash || ""),
    pretendToBeVisual: true,
  });
}

const dom = newDom();
const w = dom.window, d = w.document;
const $ = (id) => d.getElementById(id);
const fire = (el, type) => el.dispatchEvent(new w.Event(type, { bubbles: true }));

// ---------- 1. boot + baseline ----------
T("app boots: table rendered", d.querySelectorAll("#tbl tbody tr").length > 0);
const countText = () => $("count").textContent;
T("baseline: couple-collapsed count mentions couples",
  /530 couples \(546 measurements\)/.test(countText()), countText());

// ---------- 2. couple collapse + badge ----------
const bodyRows = () => [...d.querySelectorAll("#tbl tbody tr")];
const badges = bodyRows().filter(r => r.querySelector("button.badge"));
T("multi-source badges present (expect 14)", badges.length === 14, "found " + badges.length);
if (badges.length) {
  const before = bodyRows().length;
  badges[0].querySelector("button.badge").click();
  const after = bodyRows().length;
  T("badge click expands sub-rows", after > before, before + "→" + after);
}

// ---------- 3. alias search ----------
const aliasCases = ["hydroquinone", "BHT", "ferrocene", "magic blue", "menadiol", "Keggin", "TEMPOL-H", "H2Azo", "PW12", "phosphomolybdate", "TiV5"];
for (const a of aliasCases) {
  $("q").value = a; fire($("q"), "input");
  const shown = bodyRows().length;
  T("alias search '" + a + "' > 0 rows", shown > 0, "rows " + shown);
}
$("q").value = ""; fire($("q"), "input");

// ---------- 4. chip solo logic ----------
const chips = [...d.querySelectorAll("#classChips .chip")];
T("10 class chips", chips.length === 10, "found " + chips.length);
if (chips.length) {
  const all = bodyRows().length;
  chips[0].click();
  const solo = bodyRows().length;
  T("chip click = solo (fewer rows)", solo < all && solo > 0, all + "→" + solo);
  chips[0].click();
  T("second click restores all", bodyRows().length === all, "" + bodyRows().length);
}

// ---------- 5. permalink ----------
{
  const dom2 = newDom({ hash: "#BDFE-0406" });
  const d2 = dom2.window.document;
  const det = d2.getElementById("detail");
  T("permalink #BDFE-0406 opens verification panel",
    det && det.style.display === "block" && /BDFE-0406/.test(det.textContent),
    (det ? det.textContent.slice(0, 60) : "no panel"));
  T("permalink panel shows discordant/star reason",
    det && /Discordant/i.test(det.textContent) && /Rule 4/i.test(det.textContent));
}

// ---------- 6. verification panel fields ----------
{
  bodyRows()[0].click();
  const det = $("detail");
  T("panel shows entry_id + couple_id", /BDFE-\d{4}/.test(det.textContent) && /CPL-\d{4}/.test(det.textContent));
  T("panel has permalink #", !!det.querySelector('a[href*="#BDFE-"]'));
  T("panel shows DOI line", /10\.\d{4,}/.test(det.textContent));
}

// ---------- 6b. origin provenance (CR-2026-11-13-origin-provenance) ----------
{
  // filter: "mixed" with recommended-only off -> exactly the 14 stage-1 rows
  const rec = $("recOnly");
  rec.checked = false; rec.dispatchEvent(new w.Event("change"));
  $("orig").value = "mixed"; fire($("orig"), "input");
  const nMixed = bodyRows().length;
  T("origin filter mixed = 15 rows (stage-1 + BDFE-0134)", nMixed === 15, "" + nMixed);
  $("orig").value = ""; fire($("orig"), "input");
  rec.checked = true; rec.dispatchEvent(new w.Event("change"));
  // panel line on the sim-pKa row
  const dom3 = newDom({ hash: "#BDFE-0377" });
  const det3 = dom3.window.document.getElementById("detail");
  T("panel shows Origin: mixed with sim-pKa reason",
    det3 && /Origin: mixed/.test(det3.textContent) && /sim-pKa/.test(det3.textContent),
    det3 ? det3.textContent.slice(0, 80) : "no panel");
  // unclassified row renders the honest empty state
  const dom4 = newDom({ hash: "#BDFE-0001" });
  const det4 = dom4.window.document.getElementById("detail");
  T("panel shows not-yet-classified for empty origin",
    det4 && /not yet classified/.test(det4.textContent));
  // CSV column
  $("csvScope").value = "all";
  const csvO = w.csvText();
  T("csv has origin column with mixed values",
    /(^|,)origin(,|$)/m.test(csvO.split("\n")[0]) && /,mixed,/.test(csvO));
}

// ---------- 6c. square-scheme view (CR-2026-11-13-square-scheme-view) ----------
{
  // full square: BDFE-0090 (FeII(H2O)6) stores all four legs
  const dF = newDom({ hash: "#BDFE-0090" }).window.document;
  const solidF = dF.querySelectorAll('#sqsvg .sqedge[data-state="stored"]').length;
  const stEa0090 = dF.querySelector('#sqsvg .sqedge[data-leg="Ea"]');
  // since the H105 redesign Hess-composed stored values render as derived (dashed)
  T("full-square row: 3 measured edges, hess:E_a leg derived, BDFE diagonal",
    solidF === 3 && stEa0090 && stEa0090.dataset.state === "derived"
      && dF.querySelectorAll("#sqsvg .sqdiag").length >= 1,
    "solid=" + solidF + " Ea=" + (stEa0090 ? stEa0090.dataset.state : "none"));
  // BDFE-0422: E_a + pKa_b solid, E_b/pKa_a dashed-derived, diagonal 52.3
  const d4 = newDom({ hash: "#BDFE-0422" }).window.document;
  const st = l => { const e = d4.querySelector(`#sqsvg .sqedge[data-leg="${l}"]`); return e && e.dataset.state; };
  T("BDFE-0422: Ea/pKaB stored, Eb/pKaA derived, diagonal 52.3",
    st("Ea") === "stored" && st("pKaB") === "stored" && st("Eb") === "derived" && st("pKaA") === "derived"
      && /BDFE\(X–H\) = 52\.3 kcal mol/.test(d4.getElementById("sqsvg").textContent),
    [st("Ea"), st("pKaB"), st("Eb"), st("pKaA")].join("/"));
  // TMH sq+hyd row: hydricity extension with the 1.364 diagonal closing to the stored value
  const dH = newDom({ hash: "#BDFE-0427" }).window.document;
  const sq = dH.getElementById("sqscheme");
  T("TMH hyd row: hydricity cycle renders, closes, outside the square group",
    !!dH.querySelector("#sqsvg #sqhyd .sqdiag.hyd") && !dH.querySelector("#sqsvg #sqsquare .sqdiag.hyd")
      && /1\.364/.test(sq.textContent) && /ΔG°\(H⁻\)/.test(sq.textContent));
  // pair row: notice, no SVG
  const dP = newDom({ hash: "#BDFE-0059" }).window.document;
  T("pair row: notice, no square SVG",
    !!dP.getElementById("sqnote") && !dP.getElementById("sqsvg"));
}

// ---------- 6d. ladder tickboxes (CR-2026-11-13-ladder-tickboxes) ----------
{
  const rungs = () => d.querySelectorAll("#ladder line.rung").length;
  const baseline = rungs();
  // tick 3 couples across classes -> exactly 3 labelled rungs
  const boxes = [...d.querySelectorAll("#tbl tbody .tick")].slice(0, 3);
  boxes.forEach(b => { b.checked = true; b.dispatchEvent(new w.Event("click", { bubbles: true })); });
  const nSel = rungs();
  const labels = d.querySelectorAll("#ladder text").length;
  T("3 ticks -> 3 rungs, banner, all labelled",
    nSel === 3 && /3<\/b> selected/.test($("ladderSel").innerHTML) && labels > 0, nSel + " rungs");
  // filters do not alter the rung set
  $("q").value = "zzz-no-match"; fire($("q"), "input");
  T("search change does not alter selected rungs", rungs() === 3, rungs() + "");
  $("q").value = ""; fire($("q"), "input");
  // clear restores the filtered view
  const clr = d.getElementById("selClear");
  clr.dispatchEvent(new w.Event("click", { bubbles: true, cancelable: true }));
  T("clear selection restores the filtered ladder", rungs() === baseline, rungs() + " vs " + baseline);
}

// ---------- 6e. verification ledger (CR-2026-11-13-verification-ledger) ----------
{
  // review row: Agarwal locator + spot-check
  const dR = newDom({ hash: "#BDFE-0013" }).window.document;
  const vR = dR.getElementById("verifrec");
  T("ledger panel: review row (BDFE-0013) with locator + spot-check",
    vR && /review-table/.test(vR.textContent) && /Agarwal 2022 T6/.test(vR.textContent)
      && /stress test 2026-11-12/.test(vR.textContent),
    vR ? vR.textContent.slice(0, 80) : "no block");
  // TMH primary row
  const dT = newDom({ hash: "#BDFE-0498" }).window.document;
  const vT = dT.getElementById("verifrec");
  T("ledger panel: primary row (BDFE-0498) primary-verified + PR",
    vT && /primary/.test(vT.textContent) && /PR #44/.test(vT.textContent)
      && /spot-check/i.test(vT.textContent));
  // multi-member couple CPL-0470 member shows the cross-check
  const dM = newDom({ hash: "#BDFE-0478" }).window.document;
  const vM = dM.getElementById("verifrec");
  T("ledger panel: multi-member couple cross-check shown",
    vM && /multi-member couple CPL-/.test(vM.textContent));
  // download texts: one row and full ledger row counts
  const one = w.verifText("entry", "BDFE-0013");
  const all = w.verifText("all");
  T("ledger export: 1-row and full counts correct",
    one.trim().split("\n").length === 2 && all.trim().split("\n").length - 1 === 546,
    one.trim().split("\n").length + " / " + (all.trim().split("\n").length - 1));
}

// ---------- 6f. ladder label de-collision (CR-2026-11-14-ladder-label-overlap) ----------
{
  const lbl = [...d.querySelectorAll("#ladder text")].filter(t => t.getAttribute("x") === "224");
  const ys = lbl.map(t => parseFloat(t.getAttribute("y"))).sort((a, b) => a - b);
  let minGap = 1e9;
  for (let i = 1; i < ys.length; i++) minGap = Math.min(minGap, ys[i] - ys[i - 1]);
  T("anchor labels never closer than 11 px",
    lbl.length >= 10 && minGap >= 11,
    lbl.length + " labels, min gap " + minGap.toFixed(1));
}

// ---------- 6g. permanent stress specs (CR-2026-11-12-stress-v1.4) ----------
{
  // TMH multi-method couple CPL-0460: panel shows all three determinations + discordant reason
  const dC = newDom({ hash: "#BDFE-0478" }).window.document;
  const det = dC.getElementById("detail");
  T("CPL-0460 panel: sq/hyd/OCP members + discordant reason",
    det && /53\.8/.test(det.textContent) && /54\.9/.test(det.textContent) && /57\.6/.test(det.textContent)
      && /discordant/i.test(det.textContent),
    det ? det.textContent.slice(0, 60) : "no panel");
  // 5-digit-ID permalink guard: unknown long id must not break boot
  const d5 = newDom({ hash: "#BDFE-10000" }).window.document;
  T("5-digit permalink: app boots, no detail for unknown id",
    d5.querySelectorAll("#tbl tbody tr").length > 0
      && (!d5.getElementById("detail") || d5.getElementById("detail").style.display !== "block"));
}

// ---------- 7. CSV: scope + content ----------
{
  $("csvScope").value = "all"; const csvAll = typeof w.csvText === "function" ? w.csvText() : null;
  if (csvAll !== null) {
    $("csvScope").value = "rec"; const csvRec = w.csvText();
    const nAll = csvAll.trim().split("\n").length - 1;
    const nRec = csvRec.trim().split("\n").length - 1;
    T("csv all = 546 rows", nAll === 546, "" + nAll);
    T("csv recommended = 530 rows (one per couple)", nRec === 530, "" + nRec);
    T("csv has couple_id column", /couple_id/.test(csvAll.split("\n")[0]));
    T("csv has entry_id + metadata columns (F4)",
      ["entry_id","sigma_BDFE","method","T_K","conditions","year"].every(c => csvAll.split("\n")[0].includes(c)));
    T("csv has square-scheme leg columns incl. E_c (stress F5)",
      ["pKa_a","E_a_V","E_b_V","E_c_V","hydricity_kcal"].every(c => csvAll.split("\n")[0].includes(c)));
    { // stress F5 acceptance: a hyd row's exported legs re-close its hydricity (form 1)
      const hd = csvAll.split("\n")[0].split(",");
      const ix = n => hd.indexOf(n);
      const row = csvAll.split("\n").find(l => l.includes("BDFE-0453"));
      const cells = row.split(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/);
      const calc = 1.364*parseFloat(cells[ix("pKa_XH")]) + 23.06*(parseFloat(cells[ix("E_a_V")]) + parseFloat(cells[ix("E_c_V")])) + 79.6;
      const stored = parseFloat(cells[ix("hydricity_kcal")]);
      T("exported legs re-close hydricity on a hyd row (stress F5)", Math.abs(calc - stored) < 0.05, calc.toFixed(3) + " vs " + stored);
    }
    const eids = csvAll.trim().split("\n").slice(1).map(l => l.split(",")[1]);
    T("csv rows uniquely keyed by entry_id", new Set(eids).size === eids.length && eids.every(e => /^BDFE-\d{4,}$/.test(e)));
    T("csv recommended keeps the starred VW5O18 value (63.0 not 63.3)",
      csvRec.split("\n").filter(l => l.includes("VW5O18(OH)")).length === 1 &&
      csvRec.split("\n").find(l => l.includes("VW5O18(OH)")).includes("63.0"));
    const risky = csvAll.split("\n").slice(1).filter(l => /^[=+@]|^-[^0-9]/.test(l));
    T("csv no leading formula chars on lines", risky.length === 0, "risky " + risky.length);
  } else {
    T("csvText() reachable from window", false, "expose for testability");
  }
}

// ---------- 8. unit/scale/header coherence ----------
{
  $("unit").value = "kJ"; fire($("unit"), "input");
  T("ladder header shows kJ", /kJ/.test($("ladderHead").textContent), $("ladderHead").textContent);
  const ticks = [...d.querySelectorAll("#ladder text")].map(t => t.textContent).filter(t => /^\d+$/.test(t)).map(Number);
  T("kJ ticks are round (multiples of 25)", ticks.length > 0 && ticks.every(v => v % 25 === 0), ticks.join(","));
  $("scale").value = "Fc"; fire($("scale"), "input");
  T("ladder header follows scale", /Fc/.test($("ladderHead").textContent) && /Fc/.test($("eHead").textContent));
  $("unit").value = "kcal"; fire($("unit"), "input");
  $("scale").value = "H2"; fire($("scale"), "input");
}

// ---------- 9. calculator fuzz ----------
{
  const cases = [
    ["0.5", "20", true],
    ["", "", false],
    ["abc", "xyz", false],
    ["1e309", "20", false],
    ["-1e309", "20", false],
    ["0.5", "-500", true],
    ["NaN", "20", false],
    ["0,5", "20", false],
  ];
  let crash = 0, out;
  for (const [e, p, expectResult] of cases) {
    try {
      $("uMode").value = "sq"; fire($("uMode"), "change");
      $("uE").value = e; $("uPka").value = p;
      $("uGo").click();
      out = $("uOut").textContent;
      if (!expectResult) {
        T("calc rejects E='" + e + "' pKa='" + p + "'",
          /enter|finite|invalid/i.test(out), "out: " + out.slice(0, 60));
      } else {
        T("calc computes E='" + e + "' pKa='" + p + "'", /kcal|kJ|eV/.test(out), out.slice(0, 60));
      }
    } catch (err) { crash++; T("calc no-crash E='" + e + "'", false, err.message); }
  }
  T("calculator never throws", crash === 0);
  /* K4: solve for the missing leg */
  const setCalc=(e,p,b)=>{$("uMode").value="sq";fire($("uMode"),"change");
    $("uE").value=e;$("uPka").value=p;$("uB").value=b;$("uGo").click();return $("uOut").textContent;};
  // forward case unchanged: E=0.000 vs Fc, pKa=20, MeCN, kJ unit -> 334.7 kJ/mol
  $("unit").value="kJ";fire($("unit"),"input");$("uSolv").value="MeCN";
  const fwd=setCalc("0.000","20","");
  T("K4 forward: E=0, pKa=20, MeCN = 334.7 kJ/mol", /334\.7/.test(fwd), fwd.slice(0,70));
  $("unit").value="kcal";fire($("unit"),"input");
  // solve-for-pKa: TEMPOH/MeCN (stored pKa 41.0, BDFE 66.0; E not measured -
  // compute the eq-10-consistent E in the test, then the solver must return the stored pKa)
  const tempoh=dom.window.eval("D").find(r=>r.name==="TEMPOH"&&r.solvent==="MeCN");
  if(tempoh&&tempoh.pka!=null&&Number.isFinite(tempoh.bdfe)){
    const cg=dom.window.eval("CG")["MeCN"];
    const eCons=((tempoh.bdfe-1.37*tempoh.pka-cg)/23.06).toFixed(4);
    const outP=setCalc(eCons,"",String(tempoh.bdfe));
    T("K4 solve-for-pKa labeled as derived", /derived from the Bordwell equation/.test(outP), outP.slice(0,80));
    const num=(outP.match(/= ([-\d.]+)/g)||[]).map(x=>parseFloat(x.slice(2))).pop();
    T("K4 pKa recovered = stored ("+tempoh.pka+")", Math.abs(num-tempoh.pka)<=0.1, "got "+num);
  } else { T("TEMPOH/MeCN row with pKa+BDFE found", false); }
  // underdetermined input rejected
  const bad=setCalc("0.5","","");
  T("K4 rejects one-value input", /exactly two/i.test(bad), bad.slice(0,60));
  $("uB").value="";
}

// ---------- 9b. K1 pair / HAT feasibility ----------
{
  const D2=dom.window.eval("D");
  const tempoh=D2.find(r=>r.name==="TEMPOH"&&r.solvent==="MeCN");
  const ch=D2.find(r=>r.bond==="C-H"&&r.solvent==="MeCN"&&Number.isFinite(r.bdfe)&&r.nDup===1);
  const h2o=D2.find(r=>r.solvent==="H2O"&&Number.isFinite(r.bdfe)&&r.nDup===1);
  const key=r=>`${r.name}${r.partner?" + "+r.partner:""} [${r.solvent}]`;
  $("unit").value="kcal"; fire($("unit"),"input");
  // same solvent: dG = BDFE(sub) - BDFE(cat), hand-computed
  $("pDon").value=key(ch); $("pAcc").value=key(tempoh); $("pGo").click();
  const out1=$("pOut").textContent;
  const expect=(ch.bdfe-tempoh.bdfe).toFixed(1);
  T("K1 pair: dG equals hand-computed BDFE difference ("+expect+")",
    out1.includes(expect)&&/downhill|uphill|thermoneutral/.test(out1), out1.slice(0,90));
  T("K1 pair: entry_ids shown", /BDFE-\d{4,}/.test(out1));
  // cross-solvent hard block: message, no number
  $("pDon").value=key(h2o); $("pAcc").value=key(tempoh); $("pGo").click();
  const out2=$("pOut").textContent;
  T("K1 cross-solvent hard block", /not supported/i.test(out2)&&!/ΔG°\(HAT\) =/.test(out2), out2.slice(0,80));
}

// ---------- 9b2. R2-1: pair panel marks effective pairs / excited couples ----------
{
  const D2=dom.window.eval("D");
  const pair=D2.find(r=>r.flags.includes("ox-base")&&r.flags.includes("excited")&&r.solvent==="MeCN"&&Number.isFinite(r.bdfe))||D2.find(r=>r.flags.includes("ox-base")&&r.solvent==="MeCN"&&Number.isFinite(r.bdfe));
  const sub=D2.find(r=>r.bond==="C-H"&&r.solvent==="MeCN"&&Number.isFinite(r.bdfe)&&r.nDup===1);
  const key=r=>`${r.name}${r.partner?" + "+r.partner:""} [${r.solvent}]`;
  $("pDon").value=key(sub); $("pAcc").value=key(pair); $("pGo").click();
  const o=$("pOut").textContent;
  T("R2-1: effective-pair marker shown", /reagent pair, not a single/.test(o), o.slice(0,120));
  if(pair.flags.includes("excited"))T("R2-1: excited-state marker shown", /excited-state couple/.test(o));
}

// ---------- 9c. K3 estimator (Kütt 2021, descriptor-free) ----------
{
  // acceptance: eq 3.2, pKa(MeCN)=20 -> pKa(DMF)=9.5 +/- 0.2
  $("kSolv").value="DMF"; fire($("kSolv"),"input");
  $("kFam").value="1"; $("kIn").value="20"; $("kGo").click();
  const o1=$("kOut").textContent;
  T("K3 eq 3.2: pKa(MeCN)=20 -> DMF 9.5 ± 0.2", /9\.5 ± 0\.2/.test(o1), o1.slice(0,80));
  // out-of-range warning (eq 3.2 range 11.0-29.2, input 5)
  $("kIn").value="5"; $("kGo").click();
  const oorTxt=$("kOut").textContent;
  T("K3 out-of-range warning", /Outside calibration range/.test(oorTxt));
  T("R2-2: warning precedes the value", oorTxt.indexOf("Outside calibration range")<oorTxt.indexOf("≈"), oorTxt.slice(0,80));
  // family list contains no POM/metal option
  const fams=[...d.querySelectorAll("#kFam option")].map(o=>o.textContent.toLowerCase()).join("|");
  T("K3 no POM/metal-complex family", !/pom|metal/.test(fams), fams);
  // never stored: estimate does not change CSV row count
  $("csvScope").value="all";
  T("K3 estimate never stored (CSV still 546 rows)", w.csvText().trim().split("\n").length-1===546);
}

// ---------- 9d. K3 stage 2: descriptor-based H2O/DMSO ----------
{
  const setK=(solv,fam)=>{$("kSolv").value=solv;fire($("kSolv"),"input");$("kFam").value=String(fam);fire($("kFam"),"input");};
  // eq 1.2 worked example: x=20, XCO=0, nC=6, MW=94.11 -> 0.55*20+0.13*6+0.0017*94.11-6.5 = 5.4
  setK("H2O",1);
  $("kd_XCO").value="0"; $("kd_nC").value="6"; $("kd_MW").value="94.11";
  $("kIn").value="20"; $("kGo").click();
  T("K3s2 eq 1.2: phenol example -> 5.4 ± 0.3", /5\.4 ± 0\.3/.test($("kOut").textContent), $("kOut").textContent.slice(0,100));
  // eq 2.4 worked example: x=20, nNO2=1, nCF3=0 -> 0.87*20-1.0-8.0 = 8.4
  setK("DMSO",3);
  $("kd_nNO2").value="1"; $("kd_nCF3").value="0";
  $("kIn").value="20"; $("kGo").click();
  T("K3s2 eq 2.4: nitrophenol example -> 8.4 ± 0.6", /8\.4 ± 0\.6/.test($("kOut").textContent), $("kOut").textContent.slice(0,100));
  // descriptor fields appear/disappear with the equation
  T("K3s2 eq 2.4 shows exactly its 2 descriptor fields", d.querySelectorAll("#kDesc input").length===2);
  setK("DMF",0);
  T("K3s2 DMF shows no descriptor fields", d.querySelectorAll("#kDesc input").length===0);
  // negative descriptor rejected
  setK("DMSO",0);
  $("kd_nHBD").value="-1"; $("kIn").value="20"; $("kGo").click();
  T("K3s2 rejects negative descriptor", /non-negative/.test($("kOut").textContent));
}

// ---------- 10. theme toggle ----------
{
  const before = d.documentElement.getAttribute("data-theme") || "auto";
  $("themeBtn").click();
  const after1 = d.documentElement.getAttribute("data-theme");
  T("theme toggle changes data-theme", after1 !== before, before + "→" + after1);
  T("theme persisted to localStorage", !!w.localStorage.getItem("pcetbase-theme"));
}

// ---------- 11. search fuzz (no-crash, no-stuck) ----------
{
  const fuzz = ["<script>alert(1)<\/script>", "'; DROP TABLE--", "))((", "ÄÖÜß", "…", "\\", "\"", "🧪", " ".repeat(500), "a".repeat(2000)];
  let crash = 0;
  for (const f of fuzz) {
    try { $("q").value = f; fire($("q"), "input"); } catch (e) { crash++; }
  }
  $("q").value = ""; fire($("q"), "input");
  T("search fuzz: no crashes", crash === 0);
  T("search fuzz: no injected script element", !d.querySelector("#tbl script"));
  /* method-filter UI (CR-2026-11-12-method-filter-ui) */
  {
    const boxes = [...d.querySelectorAll(".mBox")];
    T("method checkboxes derived from data (6 values, incl. hess)", boxes.length === 6, "found " + boxes.length);
    const hydBox = boxes.find(b => b.dataset.m === "hyd");
    T("hyd checkbox present", !!hydBox);
    const before = w.filtered().length;
    hydBox.checked = false; hydBox.dispatchEvent(new w.Event("change"));
    const after = w.filtered().length;
    T("unticking hyd hides the 31 hyd rows", before - after === 31, before + "->" + after);
    hydBox.checked = true; hydBox.dispatchEvent(new w.Event("change"));
    const rec = d.getElementById("recOnly");
    T("recommended-only toggle default ON", rec.checked === true);
    const rowsCollapsed = d.querySelectorAll("#tbl tbody tr").length;
    rec.checked = false; rec.dispatchEvent(new w.Event("change"));
    const rowsFlat = d.querySelectorAll("#tbl tbody tr").length;
    T("toggle off shows every determination", rowsFlat === 546 && rowsCollapsed < rowsFlat, rowsCollapsed + "/" + rowsFlat);
    rec.checked = true; rec.dispatchEvent(new w.Event("change"));
  }

  T("search recovers to full view", /530 couples/.test(countText()), countText());
}


// ---------- 6h. usability v1.5.x package (CR-2026-11-14-usability-test + CR-2026-11-16-units, PR #65) ----------
{
  // U1: typed names resolve without the "name [solvent]" datalist key
  $("pDon").value = "[Ni(dmpp)2H]+";
  $("pAcc").value = "[HPVW11O40]4-";
  d.getElementById("pGo").dispatchEvent(new w.Event("click", { bubbles: true }));
  const pOut = $("pOut").textContent;
  T("U1: typed pair lookup computes dG = -13.4", /13\.4/.test(pOut) && /downhill/.test(pOut), pOut.slice(0, 120));
  // U1: ambiguous bare name offers clickable candidates
  $("pDon").value = "TEMPOH";
  $("pAcc").value = "[HPVW11O40]4-";
  d.getElementById("pGo").dispatchEvent(new w.Event("click", { bubbles: true }));
  const cands = [...$("pOut").querySelectorAll(".pCand")];
  T("U1: ambiguous name lists >=2 candidates with solvents", cands.length >= 2 && cands.every(b => /TEMPOH/.test(b.textContent) && /\[.+\]/.test(b.textContent)), cands.length + " candidates");
  cands[0] && cands[0].dispatchEvent(new w.Event("click", { bubbles: true }));
  T("U1: clicking a candidate fills the field and evaluates", /TEMPOH/.test($("pDon").value) && /HAT|solvent/i.test($("pOut").textContent));

  // U5: Recommended only + origin filter never silently substitutes a non-star
  // row for a couple that has a star: CPL-0377's 62.5 row must carry the marker
  $("orig").value = "mixed"; fire($("orig"), "input");
  const reps = [...d.querySelectorAll("#tbl tbody tr:not(.sub)")];
  const pvw = reps.find(tr => /HPVW11O40/.test(tr.textContent));
  const marked = reps.filter(tr => tr.querySelector(".starhid"));
  T("U5: starred-value-hidden marker on CPL-0377's substitute row, none on rows already ★",
    pvw && pvw.querySelector(".starhid") && /68\.1 hidden/.test(pvw.textContent)
      && marked.every(tr => !/★ </.test(tr.innerHTML.split("starhid")[0])),
    pvw ? pvw.textContent.slice(0, 90) : "no HPVW11 row");
  const sh = d.querySelector("#tbl tbody .starhid");
  if (sh) sh.dispatchEvent(new w.Event("click", { bubbles: true }));
  T("U5: the marker opens the starred row's panel", sh && /★/.test($("detail").textContent), ($("detail").textContent || "").slice(0, 60));
  $("orig").value = ""; fire($("orig"), "input");

  // U2: origin filter states the classification stage
  const origOpts = [...$("orig").options].map(o => o.textContent).join(" | ");
  T("U2: origin options carry classified counts", /experimental \(\d+ classified/.test(origOpts), origOpts);
  T("U2: note states unclassified count", /\d+ of \d+ entries not yet classified/.test($("origNote").textContent), $("origNote").textContent);

  // U7: default-open panel text carries no internal workflow references
  const jarg = /CR-20\d\d|PR #|[a-z_]+\.csv/;
  let jargHits = [];
  for (const h of ["BDFE-0036", "BDFE-0478", "BDFE-0499", "BDFE-0406"]) {
    const dd = newDom({ hash: "#" + h }).window.document;
    const det = dd.getElementById("detail").cloneNode(true);
    det.querySelectorAll("details").forEach(x => x.remove());
    if (jarg.test(det.textContent)) jargHits.push(h + ": " + det.textContent.match(jarg)[0]);
  }
  T("U7: no CR/PR/file references outside the collapsed curation trail", jargHits.length === 0, jargHits.join("; "));

  // U9/H105: Hess-composed pKa leg renders derived (dashed), measured stays solid
  const d99 = newDom({ hash: "#BDFE-0499" }).window.document;
  const d78 = newDom({ hash: "#BDFE-0478" }).window.document;
  const stOf = (doc, lg) => { const e = doc.querySelector(`#sqsvg .sqedge[data-leg="${lg}"]`); return e ? e.dataset.state : "none"; };
  T("U9/H105: BDFE-0499 pKa(XH) leg derived, BDFE-0478's stored",
    stOf(d99, "pKaB") === "derived" && stOf(d78, "pKaB") === "stored",
    stOf(d99, "pKaB") + " / " + stOf(d78, "pKaB"));

  // U8: sigma label scoped; empty sigma renders "not reported"
  const det99 = d99.getElementById("detail").textContent;
  T("U8: sigma label no longer claims a published BDFE sigma", /σ, published/.test(det99) && !/σ\(BDFE\), published/.test(det99));
  const det36 = newDom({ hash: "#BDFE-0036" }).window.document.getElementById("detail").textContent;
  T("U8: missing sigma shown as not reported", /uncertainty not reported/.test(det36));

  // U11: empty search state + stale panel closes
  $("q").value = "TEMPOH"; fire($("q"), "input");
  const tr0 = d.querySelector("#tbl tbody tr");
  tr0.dispatchEvent(new w.Event("click", { bubbles: true }));
  const panelOpen = $("detail").style.display === "block";
  $("q").value = "zzz-no-such-compound"; fire($("q"), "input");
  T("U11: empty search shows guidance", /No entry matches/.test(d.querySelector("#tbl tbody").textContent));
  T("U11: stale verification panel closes", panelOpen && $("detail").style.display === "none");
  $("q").value = ""; fire($("q"), "input");

  // U10: export columns + constants documented in the UI
  const colsTxt = $("csvColsBody").textContent;
  T("U10: column list names every closure leg", /E_c_V/.test(colsTxt) && /hydricity_kcal/.test(colsTxt) && /sigma_BDFE/.test(colsTxt));
  T("U10: C_Hyd(MeCN) = 79.6 findable from the export UI", /C/.test(colsTxt) && /79\.6/.test(colsTxt), colsTxt.slice(-200));

  // U4: footer stamp names the development state, not the release alone
  const foot = d.querySelector("footer").textContent;
  T("U4: dev build stamp says 'development state after v1.5' with the release DOI",
    /development state after v1\.5/.test(foot) && /release v1\.5: 525 measurements/.test(foot) && /10\.5281\/zenodo\.24222265/.test(foot),
    (foot.match(/Data version[^—]*—[^(]*/) || [""])[0]);

  // U19: no "flag — flag" tautology in the flag legend
  const detD = newDom({ hash: "#BDFE-0406" }).window.document.getElementById("detail").textContent;
  T("U19: derived flag carries a gloss", !/derived<\/b> — derived/.test(detD) && !/\bderived — derived\b/.test(detD));

  // H103 (CR-2026-11-16-units): units on every panel value of a full-square row
  const d139 = newDom({ hash: "#BDFE-0139" }).window.document;
  const det139 = d139.getElementById("detail");
  const bdfeRow = [...det139.querySelectorAll("tr")].find(tr => /^BDFE/.test(tr.textContent));
  const potRows = [...det139.querySelectorAll("tr")].filter(tr => /E°\(/.test(tr.textContent) && !/V vs H/.test(tr.textContent));
  T("units: BDFE-0139 BDFE row carries kcal mol⁻¹", bdfeRow && /kcal mol⁻¹/.test(bdfeRow.textContent), bdfeRow ? bdfeRow.textContent : "no row");
  T("units: every component potential row says V vs", potRows.length >= 2 && potRows.every(tr => /V vs/.test(tr.textContent)), potRows.map(tr => tr.textContent).join(" | ").slice(0, 160));
  T("units: worked equations state stored/delta units", (det139.textContent.match(/kcal mol⁻¹; Δ = /g) || []).length >= 1);
  const dp = JSON.parse(fs.readFileSync("datapackage.json", "utf-8"));
  const missingUnit = [];
  dp.resources.forEach(res => res.schema.fields.forEach(f => {
    if ((f.type === "number" || f.type === "integer") && !f.unit) missingUnit.push(res.name + "." + f.name);
  }));
  T("units: datapackage has a unit for every numeric field", missingUnit.length === 0, missingUnit.join(", "));
}


// ---------- 6i. equation labels + units addendum + square-scheme redesign (PR #67) ----------
{
  // H104: no bare Agarwal equation numbers in visible text (boot + two panels)
  const eqRx = /\beq[ -]?1[08]\b/i;
  const vis = doc => { const b = doc.body.cloneNode(true); b.querySelectorAll("script,style").forEach(x => x.remove()); return b.textContent; };
  const d139 = newDom({ hash: "#BDFE-0139" }).window.document;
  const d478 = newDom({ hash: "#BDFE-0478" }).window.document;
  T("H104: no bare eq 10/18 in visible text (boot, BDFE-0139, BDFE-0478)",
    !eqRx.test(vis(d)) && !eqRx.test(vis(d139)) && !eqRx.test(vis(d478)),
    (vis(d139).match(eqRx) || vis(d) .match(eqRx) || [""])[0]);
  T("H104: Bordwell + H-atom-potential names present in the panel",
    /Bordwell equation/.test(vis(d139)) && /BDFE from the H-atom potential/.test(vis(d139)));

  // units addendum: every number in the worked-equation lines carries a unit (pKa excepted)
  const checkEq = doc => {
    const bad = [];
    doc.querySelectorAll("#detail .eq").forEach(eq => {
      const txt = eq.textContent;
      if (!/BDFE|Hydricity/i.test(txt)) return;
      /* match numbers and look at what follows; pKa values follow "× " after "kcal mol⁻¹ ×" with no unit */
      const re = /(−|-)?\d+\.\d+/g; let m;
      while ((m = re.exec(txt))) {
        const after = txt.slice(m.index + m[0].length, m.index + m[0].length + 22);
        const before = txt.slice(Math.max(0, m.index - 30), m.index);
        const unitAfter = /^\s*(kcal mol⁻¹( V⁻¹)?|V\b|V vs)/.test(after);
        const isPka = /1\.37 kcal mol⁻¹ × $|pK\u2090 = $|× $/.test(before) && !unitAfter && /^[\s)+;]|^$/.test(after);
        if (!unitAfter && !isPka) bad.push(m[0] + " ←" + after.slice(0, 12));
      }
    });
    return bad;
  };
  const d77 = newDom({ hash: "#BDFE-0077" }).window.document;
  const bad77 = checkEq(d77), bad139 = checkEq(d139);
  T("units: every worked-equation number except pKa carries its unit (BDFE-0077 + BDFE-0139)",
    bad77.length === 0 && bad139.length === 0, bad77.concat(bad139).slice(0, 3).join(" | "));
  const hyph = [...d139.querySelectorAll("#detail .eq")].map(e => e.textContent).join(" ");
  T("units: no ASCII hyphen-minus before a digit in the worked equations", !/-\d/.test(hyph),
    (hyph.match(/.{10}-\d.{6}/) || [""])[0]);

  // H105 Part A: redesigned square scheme
  const svg139 = d139.getElementById("sqsvg");
  const arrows139 = svg139 ? svg139.querySelectorAll('[marker-end]').length : 0;
  T("H105: BDFE-0139 square has 5 arrowed legs (4 + diagonal) and corner boxes",
    arrows139 === 5 && svg139.querySelectorAll("#sqsquare rect").length >= 4, "arrows=" + arrows139);
  T("H105: no rotated text in the square scheme", svg139 && !/rotate\(/.test(svg139.innerHTML));
  T("H105: every E-leg label carries V + reference; pKa labels unitless",
    [...svg139.querySelectorAll("#sqsquare text")].every(tx => {
      const s = tx.textContent;
      if (!/E° = /.test(s)) return true;
      return / V/.test(s) && /vs /.test(s);
    }));
  const dH427 = newDom({ hash: "#BDFE-0427" }).window.document;
  T("H105: hydricity cycle outside the square group, with its own worked equation",
    !!dH427.querySelector("#sqsvg #sqhyd") && !dH427.querySelector("#sqsquare #sqhyd")
      && /Hydricity cycle/.test(dH427.getElementById("detail").textContent));

  // H105 Part B: compound-name sub/superscripts + no plain-text pKa nodes
  const h3 = d139.querySelector("#detail h3");
  T("H105: BDFE-0139 name renders (bpy)<sub>2</sub> … <sup>2+</sup>",
    h3 && /<sub>2<\/sub>/.test(h3.innerHTML) && /<sup>2\+<\/sup>/.test(h3.innerHTML)
      && /<sup>II<\/sup>/.test(h3.innerHTML), h3 ? h3.innerHTML.slice(0, 90) : "no h3");
  const walker = d.createTreeWalker(d.body, 4 /* TEXT */);
  const plainPka = [];
  while (walker.nextNode()) {
    const v = walker.currentNode.nodeValue;
    if (/pKa/.test(v) && !/sim-pKa|hess:pKa/.test(v)) {
      const el = walker.currentNode.parentElement;
      if (el && !el.closest("#csvColsBody") && !el.closest("script,style")) plainPka.push(v.trim().slice(0, 40));
    }
  }
  T("H105: no visible text node contains plain 'pKa' (flag tokens + export docs exempt)",
    plainPka.length === 0, plainPka.slice(0, 3).join(" | "));
  T("H105: table shows formatted names (subscript in a bracketed formula)",
    /<sub>/.test(d.querySelector("#tbl tbody").innerHTML));

  // ledger closure names mapped at render (CSV keeps eq18/eq10)
  const vrec = d478.getElementById("verifrec");
  T("H104: ledger panel says 'Bordwell closure', CSV download keeps eq10_residual",
    vrec && /Bordwell closure|H-atom-potential closure/.test(vrec.textContent)
      && /eq10_res/.test(w.verifText("all").split("\n")[0]));
}

// ---------- 6j. curation statement (U20 / H98 a, PR #68) ----------
{
  const cur = d.getElementById("curation");
  T("U20: curation statement in the footer, human-curator line present",
    cur && /How the data were curated/.test(cur.textContent) && /human curator \(C\. Streb\)/.test(cur.textContent)
      && /Curation trail/.test(cur.textContent));
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
