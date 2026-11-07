import { readFileSync } from 'node:fs';

const rd = p => readFileSync(p, 'utf8');
let failed = 0;
const check = (name, fn) => {
  try {
    const r = fn();
    if (r === true) console.log(`PASS ${name}`);
    else { failed++; console.log(`FAIL ${name}: ${r}`); }
  } catch (e) { failed++; console.log(`FAIL ${name}: threw ${e.message}`); }
};

function csv(path) {
  const rows = [];
  for (const line of rd(path).split(/\r?\n/)) {
    if (!line.trim()) continue;
    const cells = []; let cur = '', q = false;
    for (const ch of line) {
      if (ch === '"') q = !q;
      else if (ch === ',' && !q) { cells.push(cur); cur = ''; }
      else cur += ch;
    }
    cells.push(cur); rows.push(cells);
  }
  const h = rows.shift();
  return rows.map(r => Object.fromEntries(h.map((k, i) => [k, r[i]])));
}

// extract page data
const html = rd('analysis/levels/viz/loop.html');
const js = html.slice(html.indexOf('<script>') + 8, html.indexOf('</script>'));
const code = js.slice(0, js.search(/^const S=\{/m));
let ST, R, C, PR;
try { ({ ST, R, C, PR } = new Function(code + ';return {ST,R,C,typeof_PR:0,PR:(typeof PR==="undefined"?undefined:PR)}')()); }
catch (e) { console.log(`FAIL extract: ${e.message}`); process.exit(1); }

const kv = (r, label) => { const e = (r?.kv || []).find(x => x[0] === label); if (!e) throw new Error(`kv '${label}' missing`); return e[1]; };
const eq = (a, b) => String(a).replace(/,/g, '') === String(b) ? true : `page '${a}' != file '${b}'`;
const round = id => R.find(r => r.id === id);

check('1 ST has 8 stages, 8th id record', () =>
  ST.length === 8 && ST[7]?.id === 'record' ? true : `length ${ST.length}, last id ${ST[ST.length - 1]?.id}`);

check('2 R has 4 rounds ids 1..4, round 4 title Research-loop', () => {
  if (R.length !== 4 || R.map(r => r.id).join() !== '1,2,3,4') return `ids ${R.map(r => r.id)}`;
  return /research-loop/i.test(R[3].t || '') ? true : `round 4 t='${R[3].t}'`;
});

check('3 C entries well-formed', () => {
  const ids = new Set(ST.map(s => s.id));
  for (const c of C) {
    if (!Array.isArray(c) || c.length !== 4) return `bad entry ${JSON.stringify(c)}`;
    if (![1, 2, 3, 4].includes(c[0])) return `round ${c[0]} out of 1..4`;
    if (!ids.has(c[1])) return `stage '${c[1]}' not in ST`;
  }
  return true;
});

check('4 PR practices', () => {
  if (!Array.isArray(PR)) return 'PR is not defined / not an array';
  if (PR.length !== 5) return `PR length ${PR.length}`;
  const words = ['goal', 'task list', 'subagent', 'test first', 'journal'];
  for (let i = 0; i < 5; i++) {
    const p = PR[i];
    if (typeof p.k !== 'string' || typeof p.file !== 'string') return `PR[${i}] k/file not strings`;
    if (!p.k.toLowerCase().includes(words[i])) return `PR[${i}].k '${p.k}' lacks '${words[i]}'`;
    if (!Array.isArray(p.used) || p.used.length !== 4 || p.used.some(u => typeof u !== 'boolean')) return `PR[${i}].used not 4 bools`;
    if (p.used.join() !== 'false,false,false,true') return `PR[${i}].used ${p.used} != false,false,false,true`;
  }
  return true;
});

check('5a R3 Build-ups = rows in scores_parts.csv', () =>
  eq(kv(round(3), 'Build-ups'), csv('analysis/levels/report/scores_parts.csv').length));
check('5b R3 Interfaces rated = rows in scores_interfaces.csv', () =>
  eq(kv(round(3), 'Interfaces rated'), csv('analysis/levels/report/scores_interfaces.csv').length));
check('5c R3 Top score = rank_weighted 1 score_weighted', () => {
  const top = csv('analysis/levels/report/scores_alternatives.csv').find(r => Number(r.rank_weighted) === 1);
  return eq(kv(round(3), 'Top score'), Number(top.score_weighted).toFixed(1));
});
check('5d R2 Top score = max total in compare6/scores.csv', () =>
  eq(kv(round(2), 'Top score'), Math.max(...csv('analysis/compare6/scores.csv').map(r => Number(r.total))).toFixed(1)));
check('5e R1 note numbers match budget json', () => {
  const note = round(1).note || '';
  const v = y => Number(JSON.parse(rd(`analysis/budget_de_res_${y}.json`)).selected_year_budget.embodied_per_m2).toFixed(2);
  const a = v(2026), b = v(2046);
  if (a !== '354.65' || b !== '41.31') return `json gives ${a}, ${b}`;
  return note.includes('354.65') && note.includes('41.31') ? true : 'note lacks 354.65 and/or 41.31';
});
check('5f R4 Tasks done = count of "- [x]" in TASKS.md', () =>
  eq(kv(round(4), 'Tasks done'), rd('analysis/loop/TASKS.md').split('\n').filter(l => /- \[x\]/.test(l)).length));
check('5g R4 Journal entries = bullet lines in JOURNAL.md', () =>
  eq(kv(round(4), 'Journal entries'), rd('analysis/loop/JOURNAL.md').split('\n').filter(l => l.startsWith('- ')).length));

process.exit(failed ? 1 : 0);
