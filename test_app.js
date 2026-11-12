// PCETbase jsdom app test gate (CR-2026-11-11-jsdom-gate; producer spec, builder-committed)
// Runs against the built index.html. Node 18+, jsdom.
// Usage: node test_app.js path/to/index.html
// NOTE: baseline counts (492 measurements / 479 couples / 12 multi-source
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
  /479 couples \(492 measurements\)/.test(countText()), countText());

// ---------- 2. couple collapse + badge ----------
const bodyRows = () => [...d.querySelectorAll("#tbl tbody tr")];
const badges = bodyRows().filter(r => r.querySelector("button.badge"));
T("multi-source badges present (expect 12)", badges.length === 12, "found " + badges.length);
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
T("9 class chips", chips.length === 9, "found " + chips.length);
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

// ---------- 7. CSV: scope + content ----------
{
  $("csvScope").value = "all"; const csvAll = typeof w.csvText === "function" ? w.csvText() : null;
  if (csvAll !== null) {
    $("csvScope").value = "rec"; const csvRec = w.csvText();
    const nAll = csvAll.trim().split("\n").length - 1;
    const nRec = csvRec.trim().split("\n").length - 1;
    T("csv all = 492 rows", nAll === 492, "" + nAll);
    T("csv recommended = 479 rows (one per couple)", nRec === 479, "" + nRec);
    T("csv has couple_id column", /couple_id/.test(csvAll.split("\n")[0]));
    T("csv has entry_id + metadata columns (F4)",
      ["entry_id","sigma_BDFE","method","T_K","conditions","year"].every(c => csvAll.split("\n")[0].includes(c)));
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
    T("K4 solve-for-pKa labeled as derived", /derived from eq 10/.test(outP), outP.slice(0,80));
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
  T("K3 estimate never stored (CSV still 492 rows)", w.csvText().trim().split("\n").length-1===492);
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
    T("unticking hyd hides the 29 hyd rows", before - after === 29, before + "->" + after);
    hydBox.checked = true; hydBox.dispatchEvent(new w.Event("change"));
    const rec = d.getElementById("recOnly");
    T("recommended-only toggle default ON", rec.checked === true);
    const rowsCollapsed = d.querySelectorAll("#tbl tbody tr").length;
    rec.checked = false; rec.dispatchEvent(new w.Event("change"));
    const rowsFlat = d.querySelectorAll("#tbl tbody tr").length;
    T("toggle off shows every determination", rowsFlat === 492 && rowsCollapsed < rowsFlat, rowsCollapsed + "/" + rowsFlat);
    rec.checked = true; rec.dispatchEvent(new w.Event("change"));
  }

  T("search recovers to full view", /479 couples/.test(countText()), countText());
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
