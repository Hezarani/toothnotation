import React, { useState, useMemo } from "react";

/* ---------------------------------------------------------------------------
   ToothNotation — interactive odontogram + converter
   Self-contained: the FDI-canonical conversion logic is ported from the Python
   package so the demo runs with no backend.
--------------------------------------------------------------------------- */

const QUAD = { 1: "UR", 2: "UL", 3: "LL", 4: "LR", 5: "UR", 6: "UL", 7: "LL", 8: "LR" };
const DENT = (q) => (q <= 4 ? "permanent" : "primary");
const ARCH = { UR: "upper", UL: "upper", LL: "lower", LR: "lower" };
const SIDE = { UR: "right", UL: "left", LL: "left", LR: "right" };
const PERM_TYPE = {
  1: "central incisor", 2: "lateral incisor", 3: "canine", 4: "first premolar",
  5: "second premolar", 6: "first molar", 7: "second molar", 8: "third molar",
};
const PRIM_TYPE = {
  1: "central incisor", 2: "lateral incisor", 3: "canine",
  4: "first primary molar", 5: "second primary molar",
};

function fdiToUniversal(fdi) {
  const q = Math.floor(fdi / 10), p = fdi % 10;
  if (q === 1) return String(9 - p);
  if (q === 2) return String(8 + p);
  if (q === 3) return String(25 - p);
  if (q === 4) return String(24 + p);
  const idx = { 5: 5 - p, 6: 4 + p, 7: 15 - p, 8: 14 + p }[q];
  return String.fromCharCode(65 + idx);
}

function fdiToPalmer(fdi) {
  const q = Math.floor(fdi / 10), p = fdi % 10;
  const symbol = q <= 4 ? String(p) : String.fromCharCode(65 + (p - 1));
  return { quadrant: QUAD[q], symbol };
}

function describe(fdi) {
  const q = Math.floor(fdi / 10), p = fdi % 10;
  const quadrant = QUAD[q];
  const dent = DENT(q);
  const type = (dent === "permanent" ? PERM_TYPE : PRIM_TYPE)[p];
  return {
    fdi,
    quadrant,
    dentition: dent,
    arch: ARCH[quadrant],
    side: SIDE[quadrant],
    position: p,
    type,
    name: `${ARCH[quadrant]} ${SIDE[quadrant]} ${type}`,
    universal: fdiToUniversal(fdi),
    palmer: fdiToPalmer(fdi),
  };
}

// Anatomical display order (as if facing the patient).
const PERM_ROWS = {
  upper: [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28],
  lower: [48, 47, 46, 45, 44, 43, 42, 41, 31, 32, 33, 34, 35, 36, 37, 38],
};
const PRIM_ROWS = {
  upper: [55, 54, 53, 52, 51, 61, 62, 63, 64, 65],
  lower: [85, 84, 83, 82, 81, 71, 72, 73, 74, 75],
};

// Palmer bracket = two borders meeting at the corner nearest the midline & occlusal plane.
function palmerBorders(quadrant) {
  const c = "2px solid var(--accent)";
  switch (quadrant) {
    case "UR": return { borderRight: c, borderBottom: c };
    case "UL": return { borderLeft: c, borderBottom: c };
    case "LR": return { borderRight: c, borderTop: c };
    case "LL": return { borderLeft: c, borderTop: c };
    default: return {};
  }
}

const SYSTEMS = [
  { id: "fdi", label: "FDI" },
  { id: "universal", label: "Universal" },
  { id: "palmer", label: "Palmer" },
];

function codeInSystem(info, system) {
  if (system === "fdi") return String(info.fdi);
  if (system === "universal") return info.universal;
  return info.palmer.symbol; // palmer shows the symbol; bracket carries the quadrant
}

function ToothCell({ fdi, system, selected, onSelect }) {
  const info = describe(fdi);
  const isPalmer = system === "palmer";
  const label = codeInSystem(info, system);
  return (
    <button
      className={`tooth ${selected ? "tooth--on" : ""}`}
      onClick={() => onSelect(fdi)}
      title={`${info.name} · FDI ${info.fdi} · Univ ${info.universal} · Palmer ${info.palmer.quadrant}${info.palmer.symbol}`}
      aria-pressed={selected}
    >
      <span className="tooth__crown" aria-hidden />
      <span className="tooth__code" style={isPalmer ? palmerBorders(info.quadrant) : undefined}>
        {label}
      </span>
    </button>
  );
}

function Arch({ codes, system, selected, onSelect, label }) {
  const mid = codes.length / 2;
  return (
    <div className="arch">
      <div className="arch__label">{label}</div>
      <div className="arch__row">
        {codes.map((fdi, i) => (
          <React.Fragment key={fdi}>
            {i === mid && <span className="midline" aria-hidden />}
            <ToothCell fdi={fdi} system={system} selected={selected === fdi} onSelect={onSelect} />
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

// --- live converter ----------------------------------------------------------
function detectSystem(v) {
  const s = v.trim().toUpperCase().replace(/\s/g, "");
  if (!s) return null;
  if (["UR", "UL", "LL", "LR"].includes(s.slice(0, 2))) return "palmer";
  if (s.length === 1 && s >= "A" && s <= "T") return "universal";
  if (/^\d+$/.test(s)) {
    const n = parseInt(s, 10);
    const isFdi = s.length === 2 && QUAD[Math.floor(n / 10)] && (Math.floor(n / 10) <= 4 ? n % 10 >= 1 && n % 10 <= 8 : n % 10 >= 1 && n % 10 <= 5);
    if (isFdi) return "fdi";
    if (n >= 1 && n <= 32) return "universal";
  }
  return null;
}

function toFdi(value, system) {
  const v = value.trim().toUpperCase().replace(/\s/g, "");
  if (system === "fdi") {
    const n = parseInt(v, 10);
    if (Number.isNaN(n)) return null;
    const q = Math.floor(n / 10), p = n % 10;
    const ok = q <= 4 ? p >= 1 && p <= 8 : (q >= 5 && q <= 8 && p >= 1 && p <= 5);
    return ok && QUAD[q] ? n : null;
  }
  if (system === "universal") {
    if (/^\d+$/.test(v)) {
      const n = parseInt(v, 10);
      if (n < 1 || n > 32) return null;
      if (n <= 8) return 10 + (9 - n);
      if (n <= 16) return 20 + (n - 8);
      if (n <= 24) return 30 + (25 - n);
      return 40 + (n - 24);
    }
    if (v.length === 1 && v >= "A" && v <= "T") {
      const idx = v.charCodeAt(0) - 65;
      if (idx <= 4) return 50 + (5 - idx);
      if (idx <= 9) return 60 + (idx - 4);
      if (idx <= 14) return 70 + (15 - idx);
      return 80 + (idx - 14);
    }
    return null;
  }
  if (system === "palmer") {
    const quad = v.slice(0, 2), sym = v.slice(2);
    const tens = { UR: 1, UL: 2, LL: 3, LR: 4 };
    const tensP = { UR: 5, UL: 6, LL: 7, LR: 8 };
    if (!tens[quad]) return null;
    if (/^\d+$/.test(sym)) {
      const p = parseInt(sym, 10);
      return p >= 1 && p <= 8 ? tens[quad] * 10 + p : null;
    }
    if (sym.length === 1 && sym >= "A" && sym <= "E") {
      return tensP[quad] * 10 + (sym.charCodeAt(0) - 65 + 1);
    }
    return null;
  }
  return null;
}

function Converter({ onPick }) {
  const [text, setText] = useState("36");
  const detected = detectSystem(text);
  const fdi = detected ? toFdi(text, detected) : null;
  const info = fdi ? describe(fdi) : null;

  return (
    <div className="panel">
      <div className="panel__title">Convert</div>
      <input
        className="conv__input"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type any code — e.g. 36, 19, UR6, A"
        spellCheck={false}
        aria-label="Tooth code to convert"
      />
      <div className="conv__detected">
        {text.trim() === ""
          ? "Enter an FDI, Universal, or Palmer code."
          : info
          ? <>Detected <b>{SYSTEMS.find((s) => s.id === detected).label}</b></>
          : <span className="conv__err">Not a recognized tooth code.</span>}
      </div>
      {info && (
        <div className="conv__out">
          <Row k="Tooth" v={info.name} />
          <Row k="FDI" v={String(info.fdi)} mono />
          <Row k="Universal" v={info.universal} mono />
          <Row k="Palmer" v={`${info.palmer.quadrant} ${info.palmer.symbol}`} mono />
          <button className="conv__locate" onClick={() => onPick(info.fdi)}>
            Show on chart →
          </button>
        </div>
      )}
    </div>
  );
}

function Row({ k, v, mono }) {
  return (
    <div className="row">
      <span className="row__k">{k}</span>
      <span className={`row__v ${mono ? "mono" : ""}`}>{v}</span>
    </div>
  );
}

function Detail({ fdi }) {
  if (!fdi) {
    return (
      <div className="panel">
        <div className="panel__title">Tooth detail</div>
        <p className="detail__empty">Select a tooth on the chart to see every notation and its clinical metadata.</p>
      </div>
    );
  }
  const info = describe(fdi);
  return (
    <div className="panel">
      <div className="panel__title">Tooth detail</div>
      <div className="detail__name">{info.name}</div>
      <div className="detail__codes">
        <Code label="FDI" value={String(info.fdi)} />
        <Code label="Universal" value={info.universal} />
        <Code label="Palmer" value={`${info.palmer.quadrant} ${info.palmer.symbol}`} />
      </div>
      <div className="detail__meta">
        <span>{info.dentition}</span><span>·</span>
        <span>{info.arch} arch</span><span>·</span>
        <span>{info.side} side</span><span>·</span>
        <span>position {info.position} from midline</span>
      </div>
    </div>
  );
}

function Code({ label, value }) {
  return (
    <div className="code">
      <div className="code__label">{label}</div>
      <div className="code__value mono">{value}</div>
    </div>
  );
}

export default function App() {
  const [system, setSystem] = useState("fdi");
  const [dentition, setDentition] = useState("permanent");
  const [selected, setSelected] = useState(36);

  const rows = dentition === "permanent" ? PERM_ROWS : PRIM_ROWS;
  const count = dentition === "permanent" ? 32 : 20;

  const pick = (fdi) => {
    setSelected(fdi);
    const isPrimary = Math.floor(fdi / 10) >= 5;
    setDentition(isPrimary ? "primary" : "permanent");
  };

  return (
    <div className="wrap">
      <style>{css}</style>

      <header className="head">
        <div className="head__brand">
          <span className="head__mark">◷</span>
          <h1>ToothNotation</h1>
        </div>
        <p className="head__tag">
          Every tooth, in every system. Map and convert between <b>FDI</b> (ISO 3950),
          <b> Universal</b>, and <b>Palmer</b> notation — verified against 293 round-trip tests.
        </p>
      </header>

      <div className="controls">
        <div className="seg" role="group" aria-label="Notation system">
          {SYSTEMS.map((s) => (
            <button
              key={s.id}
              className={`seg__btn ${system === s.id ? "seg__btn--on" : ""}`}
              onClick={() => setSystem(s.id)}
            >
              {s.label}
            </button>
          ))}
        </div>
        <div className="seg seg--ghost" role="group" aria-label="Dentition">
          {["permanent", "primary"].map((d) => (
            <button
              key={d}
              className={`seg__btn ${dentition === d ? "seg__btn--on" : ""}`}
              onClick={() => { setDentition(d); }}
            >
              {d === "permanent" ? "Permanent · 32" : "Primary · 20"}
            </button>
          ))}
        </div>
      </div>

      <section className="chart" aria-label={`Dental chart showing ${count} teeth in ${system} notation`}>
        <Arch codes={rows.upper} system={system} selected={selected} onSelect={pick} label="Upper" />
        <div className="chart__divider"><span>R</span><span className="chart__plane" /><span>L</span></div>
        <Arch codes={rows.lower} system={system} selected={selected} onSelect={pick} label="Lower" />
        {system === "palmer" && (
          <p className="chart__hint">In Palmer, the bracket around each number marks the quadrant — drawn here the way it appears on a paper chart.</p>
        )}
      </section>

      <section className="grid2">
        <Detail fdi={selected} />
        <Converter onPick={pick} />
      </section>

      <footer className="foot">
        FDI is the canonical key internally; every code is derived from it, so there is one source of truth.
        <span className="foot__pkg">pip install toothnotation</span>
      </footer>
    </div>
  );
}

const css = `
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=JetBrains+Mono:wght@400;700&display=swap');

:root{
  --paper:#EEF1F2;
  --surface:#FFFFFF;
  --ink:#16252B;
  --muted:#5C6E75;
  --line:#D7DEE0;
  --accent:#0C7B7B;       /* clinical teal */
  --accent-soft:#E3F0EF;
  --hot:#E2603A;          /* the one warm accent — selection */
  --hot-soft:#FBE7DF;
}
*{box-sizing:border-box}
.wrap{
  font-family:'Space Grotesk',system-ui,sans-serif;
  background:
    radial-gradient(1200px 600px at 50% -10%, #FFFFFF 0%, var(--paper) 60%);
  color:var(--ink);
  min-height:100vh;
  padding:34px 22px 48px;
  max-width:980px;
  margin:0 auto;
}
.mono{font-family:'JetBrains Mono',ui-monospace,monospace}

/* header */
.head{margin-bottom:26px}
.head__brand{display:flex;align-items:center;gap:11px}
.head__mark{
  font-size:26px;color:var(--accent);
  border:2px solid var(--accent);border-radius:9px;
  width:42px;height:42px;display:grid;place-items:center;
}
.head h1{font-size:30px;font-weight:700;letter-spacing:-0.02em;margin:0}
.head__tag{color:var(--muted);max-width:62ch;line-height:1.55;margin:12px 0 0;font-size:15px}
.head__tag b{color:var(--ink);font-weight:500}

/* controls */
.controls{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:22px}
.seg{display:inline-flex;background:var(--surface);border:1px solid var(--line);border-radius:11px;padding:4px;gap:3px}
.seg--ghost{background:transparent}
.seg__btn{
  font:inherit;font-size:14px;font-weight:500;cursor:pointer;
  border:0;background:transparent;color:var(--muted);
  padding:8px 15px;border-radius:8px;transition:all .15s ease;
}
.seg__btn:hover{color:var(--ink)}
.seg__btn--on{background:var(--accent);color:#fff}
.seg--ghost .seg__btn--on{background:var(--ink);color:#fff}

/* chart */
.chart{
  background:var(--surface);border:1px solid var(--line);border-radius:18px;
  padding:26px 20px 20px;box-shadow:0 1px 0 #fff inset, 0 14px 34px -24px rgba(22,37,43,.45);
}
.arch{margin:4px 0}
.arch__label{
  font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);
  text-align:center;margin-bottom:8px;
}
.arch__row{display:flex;justify-content:center;align-items:flex-end;gap:4px;flex-wrap:nowrap}
.midline{width:2px;align-self:stretch;background:var(--line);margin:0 6px;border-radius:2px}

.tooth{
  font:inherit;cursor:pointer;border:0;background:transparent;
  display:flex;flex-direction:column;align-items:center;gap:4px;
  padding:4px 2px;border-radius:8px;transition:transform .12s ease;flex:1 1 0;min-width:0;
}
.tooth:hover{transform:translateY(-3px)}
.tooth:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.tooth__crown{
  width:60%;max-width:26px;aspect-ratio:1/1.15;
  background:linear-gradient(180deg,#FCFEFE,#E7EEEE);
  border:1.5px solid var(--line);border-radius:46% 46% 42% 42%/55% 55% 45% 45%;
  transition:all .14s ease;
}
.tooth--on .tooth__crown{background:linear-gradient(180deg,#FFF1EC,var(--hot-soft));border-color:var(--hot)}
.tooth:hover .tooth__crown{border-color:var(--accent)}
.tooth__code{
  font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:700;line-height:1;
  color:var(--ink);padding:3px 2px;min-width:20px;text-align:center;
}
.tooth--on .tooth__code{color:var(--hot)}

.chart__divider{display:flex;align-items:center;gap:10px;margin:6px 0;color:var(--muted);font-size:12px;font-weight:500}
.chart__plane{flex:1;height:1px;background:repeating-linear-gradient(90deg,var(--line) 0 8px,transparent 8px 14px)}
.chart__hint{color:var(--muted);font-size:13px;text-align:center;margin:14px 0 2px;line-height:1.5}

/* panels */
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:18px}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:20px}
.panel__title{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-bottom:14px}

.detail__empty{color:var(--muted);line-height:1.55;margin:0;font-size:14px}
.detail__name{font-size:21px;font-weight:700;letter-spacing:-0.01em;margin-bottom:16px;text-transform:capitalize}
.detail__codes{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:16px}
.code{background:var(--accent-soft);border-radius:11px;padding:12px 10px;text-align:center}
.code__label{font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);font-weight:700;margin-bottom:6px}
.code__value{font-size:20px;font-weight:700;color:var(--ink)}
.detail__meta{display:flex;flex-wrap:wrap;gap:7px;color:var(--muted);font-size:13px;text-transform:capitalize}

/* converter */
.conv__input{
  width:100%;font:inherit;font-size:16px;padding:12px 14px;border-radius:10px;
  border:1.5px solid var(--line);background:#FBFCFC;color:var(--ink);
}
.conv__input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft)}
.conv__detected{margin:10px 2px 0;font-size:13px;color:var(--muted)}
.conv__detected b{color:var(--accent)}
.conv__err{color:var(--hot)}
.conv__out{margin-top:14px;border-top:1px solid var(--line);padding-top:12px}
.row{display:flex;justify-content:space-between;align-items:center;padding:5px 0}
.row__k{font-size:13px;color:var(--muted)}
.row__v{font-size:15px;font-weight:500;text-transform:capitalize}
.row__v.mono{font-weight:700;text-transform:none}
.conv__locate{
  margin-top:12px;font:inherit;font-size:13px;font-weight:500;cursor:pointer;
  width:100%;padding:9px;border-radius:9px;border:1px solid var(--accent);
  background:transparent;color:var(--accent);transition:all .14s ease;
}
.conv__locate:hover{background:var(--accent);color:#fff}

/* footer */
.foot{
  margin-top:26px;color:var(--muted);font-size:13px;line-height:1.5;
  display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;
}
.foot__pkg{font-family:'JetBrains Mono',monospace;background:var(--ink);color:#fff;padding:7px 12px;border-radius:8px;font-size:12px}

@media (max-width:680px){
  .grid2{grid-template-columns:1fr}
  .tooth__code{font-size:11px}
  .detail__codes{grid-template-columns:1fr}
  .head h1{font-size:25px}
}
@media (prefers-reduced-motion:reduce){
  *{transition:none!important}
  .tooth:hover{transform:none}
}
`;
