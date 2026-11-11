// PCETbase jsdom app test gate (CR-2026-11-11-jsdom-gate; producer spec, builder-committed)
// Runs against the built index.html. Node 18+, jsdom.
// Usage: node test_app.js path/to/index.html
// NOTE: baseline counts (426 measurements / 421 couples / 4 multi-source
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
  /421 couples \(426 measurements\)/.test(countText()), countText());

// ---------- 2. couple collapse + badge ----------
const bodyRows = () => [...d.querySelectorAll("#tbl tbody tr")];
const badges = bodyRows().filter(r => r.querySelector("button.badge"));
T("multi-source badges present (expect 4)", badges.length === 4, "found " + badges.length);
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
T("8 class chips", chips.length === 8, "found " + chips.length);
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
    T("csv all = 426 rows", nAll === 426, "" + nAll);
    T("csv recommended = 421 rows (one per couple)", nRec === 421, "" + nRec);
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
  T("search recovers to full view", /421 couples/.test(countText()), countText());
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
