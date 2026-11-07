"""SYNTHETIC GENERATED gallery: seeded fictional assemblies -> demo evaluator -> JSON/CSV/standalone HTML.

Run from the repository root:
  python demo/run_gallery.py                       # generate (seed 20261107) + evaluate + render
  python demo/run_gallery.py --inputs FILE.json    # evaluate your own {"assemblies": [demo inputs]} instead

Every assembly is one baucode-demo-input/1 document evaluated by demo/run_demo.evaluate,
i.e. the same validation and production arithmetic (analysis/lib.py, analysis/model.py) as the
single-wall demo. This file only generates inputs, groups results and renders them.

Generated records are a DEMONSTRATION: not evaluation cases, not GOLD, not a holdout, not
evidence of accuracy, not real assemblies or materials. Output files contain no timestamps or
absolute paths, so repeated runs are byte-identical.

Exit: 0 written (rejected assemblies are expected content), 2 unreadable --inputs file, 1 internal error.
"""
import argparse, csv, hashlib, html, io, json, math, os, random, sys, traceback

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_demo  # noqa: E402  (also puts analysis/ on sys.path)

GENERATOR = 'baucode-gallery-generator/1'
SEED = 20261107
DEFAULT_OUT = 'demo/output/gallery'
REFERENCE_FU_M2 = 1.0
# sharing a reference area says nothing about thermal, structural, fire or acoustic equivalence
EQUIV_NOTE = ('Same reference area (1 m2 of a fictional assembly); equivalence unverified. '
              'Sharing a reference area does not establish thermal, structural, fire or acoustic equivalence.')
KIND = 'GENERATED demonstration records: not evaluation cases, not GOLD, not a holdout, not accuracy evidence, not real assemblies'
# fictional families; names and number ranges are invented and describe no real material
FAMILIES = ('FAM-K fictional board', 'FAM-L fictional block', 'FAM-M fictional foam', 'FAM-N fictional panel', 'FAM-P fictional coating')
EDGES = (['complete'] * 7 + ['partial_c', 'missing_d', 'negative_values', 'true_zero', 'aggregate_overlap', 'submodules_only',
         'partial_submodules', 'empty_pool', 'fu_2m2', 'markup_label',
         'blank_q', 'zero_q', 'nan_q', 'unsupported_unit', 'scenario_conflict', 'b4_module', 'kg_no_density', 'bad_thickness_unit'])


# ---------------------------------------------------------------- generation
class Gen:
    """only rng.random() is used so the stream is stable across Python versions"""
    def __init__(self, seed):
        self.r = random.Random(seed)

    def num(self, lo, hi, nd=2):
        return round(lo + (hi - lo) * self.r.random(), nd)

    def pick(self, seq):
        return seq[int(self.r.random() * len(seq))]


def product(g, gid, k, unit, fam, scen):
    if unit == 'm3':
        a, mods_scale, extra = g.num(5, 400), 1.0, {'density_kg_m3': g.num(30, 1800, 0)}
    elif unit == 'kg':
        a, mods_scale, extra = g.num(0.1, 4), 0.01, {'density_kg_m3': g.num(30, 1800, 0)}
    else:
        a, mods_scale, extra = g.num(0.5, 20), 0.05, {}
    mods = {'A1-A3': a}
    for m in ('C1', 'C2', 'C3', 'C4'):
        mods[m] = round(g.num(0, 20) * mods_scale, 4)
    mods['D'] = round(-g.num(0, 15) * mods_scale, 4)
    p = {'id': f'{gid}-P{k}', 'source': f'generated: {GENERATOR} seed {SEED} assembly {gid} product {k} ({fam})',
         'unit': unit, 'ref_quantity': g.pick((1, 2, 5)), 'scenario': scen, 'modules': mods}
    p.update(extra)
    return p


def base_doc(g, n):
    gid = f'G{n:02d}'
    prods, layers, k = [], [], 0
    plan = (('L1', 3, ('m3', 'kg'), 'mm', (10, 240)), ('L2', 3, ('m3', 'kg'), 'cm', (1, 20)), ('L3', 2, ('m2',), None, None))
    for lid, size, units, tunit, trange in plan:
        fam, unit, scen = g.pick(FAMILIES), g.pick(units), f'GEN-EOL-{g.pick("ABC")}'
        ids = []
        for _ in range(size):
            k += 1
            prods.append(product(g, gid, k, unit, fam, scen))
            ids.append(prods[-1]['id'])
        layer = {'id': lid, 'name': f'{fam} layer', 'product_ids': ids, 'multiplier': 1}
        if tunit:
            layer['thickness'] = {'value': g.num(*trange, 0 if tunit == 'mm' else 1), 'unit': tunit}
        layers.append(layer)
    return {'schema': run_demo.SCHEMA_IN, 'label': run_demo.LABEL,
            'note': f'GENERATED fictional assembly {gid}; reference area = wall.area_m2 of fictional assembly (equivalence unverified)',
            'wall': {'id': gid, 'area_m2': REFERENCE_FU_M2}, 'products': prods, 'layers': layers}


def split3(a):
    a1, a2 = round(a * 0.5, 4), round(a * 0.3, 4)
    return a1, a2, round(a - a1 - a2, 4)


def apply_edge(doc, edge):
    P = doc['products']
    L1 = [p for p in P if p['id'] in doc['layers'][0]['product_ids']]
    L2 = [p for p in P if p['id'] in doc['layers'][1]['product_ids']]
    L3 = [p for p in P if p['id'] in doc['layers'][2]['product_ids']]
    if edge == 'partial_c':
        del L2[0]['modules']['C3']
    elif edge == 'missing_d':
        del L1[0]['modules']['D']
    elif edge == 'negative_values':
        # whole fictional assembly negative so the A1-A3 chart shows a bar left of zero
        for p in P:
            p['modules']['A1-A3'] = -abs(p['modules']['A1-A3'])
    elif edge == 'true_zero':
        for p in L3:
            p['modules'].update({'A1-A3': 0, 'D': 0})
    elif edge == 'aggregate_overlap':
        for p in L1:
            p['modules'].update(zip(('A1', 'A2', 'A3'), split3(p['modules']['A1-A3'])))
    elif edge == 'submodules_only':
        for p in L2:
            p['modules'].update(zip(('A1', 'A2', 'A3'), split3(p['modules'].pop('A1-A3'))))
    elif edge == 'partial_submodules':
        a1, a2, _ = split3(L2[0]['modules'].pop('A1-A3'))
        L2[0]['modules'].update({'A1': a1, 'A2': a2})
    elif edge == 'empty_pool':
        doc['layers'][2]['product_ids'] = []
    elif edge == 'fu_2m2':
        doc['wall']['area_m2'] = 2.0
    elif edge == 'markup_label':
        doc['wall']['id'] += ' <script>alert("x")</script> & \'q\''
        doc['layers'][0]['name'] = '<img src=x onerror=alert(1)> fictional'
    elif edge == 'blank_q':
        L1[0]['ref_quantity'] = ''
    elif edge == 'zero_q':
        L1[0]['ref_quantity'] = 0
    elif edge == 'nan_q':
        L1[0]['ref_quantity'] = 'nan'
    elif edge == 'unsupported_unit':
        L1[0]['unit'] = 'piece'
    elif edge == 'scenario_conflict':
        L1[1]['scenario'] = L1[0]['scenario'] + '-OTHER'
    elif edge == 'b4_module':
        L1[0]['modules']['B4'] = 1.0
    elif edge == 'kg_no_density':
        L1[0]['unit'] = 'kg'
        L1[0].pop('density_kg_m3', None)
    elif edge == 'bad_thickness_unit':
        doc['layers'][0]['thickness']['unit'] = 'in'
    doc['edge'] = edge
    return doc


def generate(seed):
    g = Gen(seed)
    return [apply_edge(base_doc(g, i + 1), e) for i, e in enumerate(EDGES)]


# ---------------------------------------------------------------- evaluation (shared demo path)
def canon_sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()


def category(res):
    if res['status'] == 'REJECTED':
        return 'REJECTED'
    if res['status'] == 'INCOMPLETE_LAYERS':
        return 'INCOMPLETE_LAYERS'
    t = res['totals']
    # carbon-module coverage only; mass completeness is reported in its own column
    return 'EVALUATED_FULL_COVERAGE' if t['c_complete'] and t['d_complete'] else 'EVALUATED_PARTIAL_COVERAGE'


def evaluate_all(docs, inputs_name):
    out = []
    for i, doc in enumerate(docs):
        loc = f'{inputs_name}#/assemblies/{i}'
        res = run_demo.evaluate(doc, input_name=loc, input_sha256=canon_sha(doc))
        wall = doc.get('wall') if isinstance(doc, dict) and isinstance(doc.get('wall'), dict) else {}
        fu = run_demo.number(wall.get('area_m2'))
        out.append({'index': i, 'id': str(wall.get('id', f'#{i}')), 'edge': doc.get('edge') if isinstance(doc, dict) else None,
                    'reference_area_m2': fu, 'same_reference_area': res['status'] != 'REJECTED' and fu == REFERENCE_FU_M2,
                    'input_locator': loc, 'category': category(res), 'result': res})
    return out


# ---------------------------------------------------------------- rendering
E = lambda x: html.escape(str(x), quote=True)


def num(x):
    return '%.6g' % x


def qcell(v, complete=True):
    """known quantity -> number (flagged if only a known part); unknown -> UNKNOWN, never 0"""
    if v is None:
        return 'UNKNOWN'
    return num(v) if complete else f'{num(v)} (known part only)'


def nice_step(span):
    raw = span / 5
    mag = 10 ** math.floor(math.log10(raw)) if raw > 0 else 1
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


def bar_chart(cid, title, desc, rows, series):
    """rows: [(assembly_id, {key: value-or-None, key+'_why': text})]; series: [(key, label, css class)].
    Bars run from a true zero baseline; values not drawn are written as text, never as a zero bar."""
    vals = [r[1][k] for r in rows for k, _, _ in series if r[1][k] is not None]
    lo, hi = min([0.0] + vals), max([0.0] + vals)
    if lo == hi:
        hi = 1.0
    step = nice_step(hi - lo)
    lo, hi = math.floor(lo / step) * step, math.ceil(hi / step) * step
    X0, X1, LBL, BAR, GAP = 190.0, 640.0, 180, 14, 12
    x = lambda v: X0 + (v - lo) / (hi - lo) * (X1 - X0)
    group_h = len(series) * (BAR + 3) + GAP
    H = 30 + len(rows) * group_h + 30
    W = 760
    s = [f'<svg class="chart" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="{cid}-t {cid}-d">',
         f'<title id="{cid}-t">{E(title)}</title><desc id="{cid}-d">{E(desc)}</desc>']
    t = lo
    while t <= hi + step / 1000:
        xv = x(t)
        s.append(f'<line class="grid" x1="{xv:.2f}" x2="{xv:.2f}" y1="24" y2="{H - 26}"/>'
                 f'<text class="tick" x="{xv:.2f}" y="{H - 10}" text-anchor="middle">{E(num(round(t, 10)))}</text>')
        t += step
    z = x(0.0)
    y = 30
    for aid, d in rows:
        short = aid if len(aid) <= 24 else aid[:23] + '…'   # keep inside the 180px label column; full id in tooltip/table
        s.append(f'<text class="rowlabel" x="{LBL}" y="{y + BAR - 2}" text-anchor="end">{E(short)}</text>')
        for k, label, cls in series:
            v = d[k]
            if v is None:
                s.append(f'<text class="muted" x="{z + 4:.2f}" y="{y + BAR - 3}">{E(d.get(k + "_why", "UNKNOWN"))}</text>')
            else:
                xa, xb = sorted((z, x(v)))
                s.append(f'<rect class="{cls}" data-assembly="{E(aid)}" data-series="{E(k)}" data-v="{v!r}" x="{xa:.2f}" y="{y}" '
                         f'width="{max(xb - xa, 0.0):.2f}" height="{BAR}"><title>{E(aid)} {E(label)}: {E(num(v))} kgCO2e</title></rect>')
                tx, anchor = (x(v) + 4, 'start') if v >= 0 else (z + 4, 'start')
                s.append(f'<text class="value" x="{tx:.2f}" y="{y + BAR - 3}" text-anchor="{anchor}">{E(num(v))}</text>')
            y += BAR + 3
        y += GAP
    s.append(f'<line class="zero" id="{cid}-zero" data-x="{z:.2f}" x1="{z:.2f}" x2="{z:.2f}" y1="22" y2="{H - 24}"/>')
    s.append('</svg>')
    return '\n'.join(s)


CSS = """
:root{color-scheme:light;--bg:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--rule:#dddcd6;--grid:#ecebe6;--s1:#2a78d6;--s2:#eb6834;--badge:#7a1f1f}
@media (prefers-color-scheme:dark){:root{color-scheme:dark;--bg:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--rule:#3a3a37;--grid:#2c2c2a;--s1:#3987e5;--s2:#d95926;--badge:#e66767}}
body{background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,sans-serif;margin:0;padding:1.5rem;max-width:1100px}
h1{font-size:1.5rem;margin:.2rem 0}h2{font-size:1.15rem;margin-top:2rem;border-bottom:1px solid var(--rule)}
.badge{display:inline-block;border:3px solid var(--badge);color:var(--badge);font-weight:800;letter-spacing:.08em;padding:.25rem .7rem;font-size:1.2rem}
.note{color:var(--ink2)}table{border-collapse:collapse;margin:.5rem 0;font-size:13px}
th,td{border:1px solid var(--rule);padding:.25rem .45rem;text-align:left;vertical-align:top}td.n{text-align:right;font-variant-numeric:tabular-nums}
caption{text-align:left;font-weight:600;padding:.3rem 0}
.chart text{fill:var(--ink);font-size:11px}.chart .muted{fill:var(--ink2);font-style:italic}.chart .tick{fill:var(--ink2)}
.chart .grid{stroke:var(--grid)}.chart .zero{stroke:var(--ink);stroke-width:1.5}
.s1{fill:var(--s1)}.s2{fill:var(--s2)}
.legend{display:flex;gap:1.2rem;margin:.3rem 0}.sw{display:inline-block;width:12px;height:12px;margin-right:.35rem;vertical-align:-1px}
.sw.s1{background:var(--s1)}.sw.s2{background:var(--s2)}
details{margin:.3rem 0}summary{cursor:pointer}
"""


def render_html(entries, prov):
    comp = [e for e in entries if e['same_reference_area']]
    other = [e for e in entries if not e['same_reference_area'] and e['result']['status'] != 'REJECTED']
    rej = [e for e in entries if e['result']['status'] == 'REJECTED']
    H = ['<!DOCTYPE html>', '<html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>SYNTHETIC GENERATED assembly gallery</title>', f'<style>{CSS}</style></head><body>',
         '<header><p class="badge" id="synthetic-badge">SYNTHETIC &middot; GENERATED</p>',
         '<h1>Fictional assembly gallery (generated demonstration)</h1>',
         f'<p class="note">{E(KIND)}. All numbers are invented and describe no real wall, product or material. '
         'Nothing here ranks assemblies or makes product-choice, indoor-air or hazard claims. '
         'No thermal metric (U-value) is computed or shown. Equivalence to any real assembly is unverified.</p></header>']
    s = prov['summary']
    H += ['<h2 id="summary">Summary</h2>', '<table><caption>Assemblies by outcome</caption><thead><tr><th>outcome</th><th>count</th></tr></thead><tbody>']
    H += [f'<tr><td>{E(k)}</td><td class="n">{v}</td></tr>' for k, v in s['by_category'].items()]
    H += [f'<tr><td>assemblies / product records</td><td class="n">{s["assemblies"]} / {s["product_records"]}</td></tr></tbody></table>']
    fu = f'per {num(REFERENCE_FU_M2)} m2 reference area of a fictional assembly'
    H += ['<h2 id="chart-ac">A1-A3 and C1-C4 per 1 m2 reference area</h2>',
          f'<p class="note equiv">{E(EQUIV_NOTE)}</p>',
          f'<p class="note">kgCO2e (GWPtotal A2) {E(fu)}. Only assemblies with this exact reference area and no rejection are drawn. '
          'A bar is drawn only for a complete quantity; UNKNOWN or partial quantities are written as text (never a zero bar). '
          'Bars start at a true zero line; negative values extend left. Table below is the full fallback.</p>',
          '<div class="legend" id="legend-ac"><span><i class="sw s1"></i>A1-A3 total</span><span><i class="sw s2"></i>C1-C4 total (only when all four declared)</span></div>']
    rows = []
    for e in comp:
        t = e['result']['totals']
        rows.append((e['id'], {'a13': t['a13_total'], 'a13_why': 'UNKNOWN (incomplete layers)',
                               'c': t['c_known_subtotal'] if t['c_complete'] else None,
                               'c_why': 'UNKNOWN' if t['c_known_subtotal'] is None else 'PARTIAL: C known part only, see table'}))
    H.append(bar_chart('chart-ac', 'A1-A3 and C1-C4 per 1 m2 reference area of fictional assemblies (equivalence unverified)',
                       'Grouped horizontal bars, kgCO2e, zero baseline marked; unknown and partial values shown as text. '
                       'Same reference area only; thermal, structural, fire and acoustic equivalence not established.',
                       rows, [('a13', 'A1-A3 total', 's1'), ('c', 'C1-C4 total', 's2')]))
    drows = [(e['id'], {'d': e['result']['totals']['d_known_subtotal'] if e['result']['totals']['d_complete'] else None,
                        'd_why': 'UNKNOWN' if e['result']['totals']['d_known_subtotal'] is None else 'PARTIAL: D known part only, see table'})
             for e in comp]
    H += ['<h2 id="chart-d">Module D, reported separately (not subtracted)</h2>',
          f'<p class="note equiv">{E(EQUIV_NOTE)}</p>',
          f'<p class="note">kgCO2e {E(fu)}. D is never netted against A1-A3 + C1-C4. Negative D extends left of zero.</p>',
          bar_chart('chart-d', 'Module D per 1 m2 reference area of fictional assemblies, separate (equivalence unverified)',
                    'Horizontal bars, kgCO2e, zero baseline marked; D is not subtracted from A1-A3 + C1-C4. Same reference area only; equivalence not established.',
                    drows, [('d', 'D', 's1')])]
    head = ('<thead><tr><th>assembly</th><th>outcome</th><th>layers known</th><th>A1-A3 total</th><th>C1-C4</th>'
            '<th>A1-A3 + C1-C4 known subtotal</th><th>D known subtotal (partial; separate, not subtracted)</th><th>known mass subtotal kg</th>'
            '<th>input locator</th></tr></thead>')

    def row(e):
        r, t = e['result'], e['result']['totals']
        cells = [('a13', qcell(t['a13_total'])), ('c', qcell(t['c_known_subtotal'], t['c_complete'])),
                 ('a1c', qcell(t['a1_c_known_subtotal'], t['c_complete'] and t['layers_complete'])),
                 ('d', qcell(t['d_known_subtotal'], t['d_complete'])), ('mass', qcell(t['mass_known_kg'], t['mass_complete']))]
        return (f'<tr data-assembly="{E(e["id"])}"><td>{E(e["id"])}</td><td>{E(e["category"])}</td><td class="n">{t["layers_known"]}/{t["layers_total"]}</td>'
                + ''.join(f'<td class="n" data-k="{k}">{E(v)}</td>' for k, v in cells) + f'<td><code>{E(e["input_locator"])}</code></td></tr>')
    H += ['<h2 id="table">Table: same reference area (1 m2 of a fictional assembly); equivalence unverified</h2>',
          '<p class="note">kgCO2e for the reference area. "UNKNOWN" = not declared or not computable (never zero); '
          '"(known part only)" = subtotal over declared modules or computable layers. Mass only where thickness and density were given. '
          'A1-A3 + C1-C4 covers the selected modules only; A4, A5 and B modules are outside scope, so no value here is a life-cycle total.</p>',
          f'<table id="tbl-compared"><caption>{E(EQUIV_NOTE)}</caption>{head}<tbody>' + ''.join(row(e) for e in comp) + '</tbody></table>']
    H += ['<h2 id="other-fu">Other reference areas (not placed side by side)</h2>',
          '<p class="note">Different reference area; values are per that area and are deliberately kept out of the 1 m2 table and the charts.</p>',
          f'<table id="tbl-other">{head.replace("<th>assembly</th>", "<th>assembly (reference area)</th>")}<tbody>'
          + ''.join(row(e).replace(f'<td>{E(e["id"])}</td>', f'<td>{E(e["id"])} ({E(num(e["reference_area_m2"]))} m2)</td>', 1) for e in other)
          + '</tbody></table>']
    H += ['<h2 id="rejected">Rejected inputs (no numeric output)</h2>',
          '<table id="tbl-rejected"><thead><tr><th>assembly</th><th>outcome</th><th>error codes</th><th>where</th><th>input locator</th></tr></thead><tbody>']
    for e in rej:
        errs = e['result']['errors']
        H.append(f'<tr data-assembly="{E(e["id"])}"><td>{E(e["id"])}</td><td>REJECTED</td><td>{E(", ".join(x["code"] for x in errs))}</td>'
                 f'<td>{E("; ".join(x["where"] for x in errs))}</td><td><code>{E(e["input_locator"])}</code></td></tr>')
    H.append('</tbody></table>')
    H += ['<h2 id="breakdown">Layer and module breakdown</h2>',
          '<p class="note">Per layer: median of the product pool (descriptive; not a wall comparison). Sources are generated locators, not publications.</p>']
    for e in comp + other:
        H.append(f'<details><summary>{E(e["id"])}: {E(e["category"])}</summary><table><thead><tr><th>layer</th><th>status</th><th>products</th>'
                 '<th>A1-A3</th><th>C known</th><th>C modules</th><th>C missing</th><th>D</th><th>mass kg</th><th>sources</th></tr></thead><tbody>')
        for l in e['result']['layers']:
            H.append(f'<tr><td>{E(l["id"])} {E(l["name"] or "")}</td><td>{E(l["status"] + (" (" + l["reason"] + ")" if l["reason"] else ""))}</td>'
                     f'<td>{E(", ".join(l["products"]) or "-")}</td><td class="n">{E(qcell(l["a13"]))}</td><td class="n">{E(qcell(l["c_known"]))}</td>'
                     f'<td>{E(", ".join(l["c_modules"]) or "-")}</td><td>{E(", ".join(l["c_missing"]) or "-")}</td><td class="n">{E(qcell(l["d"]))}</td>'
                     f'<td class="n">{E(qcell(l["mass_kg"]))}</td><td>{E("; ".join(l["sources"]) or "-")}</td></tr>')
        H.append('</tbody></table></details>')
    H += ['<h2 id="provenance">Provenance</h2>', '<table><tbody>']
    for k in ('generator', 'seed', 'input_source', 'inputs_sha256', 'schema_in', 'schema_out', 'evaluator', 'records_kind'):
        H.append(f'<tr><th>{E(k)}</th><td>{E(prov[k])}</td></tr>')
    H += ['</tbody></table>', '</body></html>']
    return '\n'.join(H) + '\n'


def render_csv(entries):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['label', 'kind', 'assembly', 'edge', 'reference_area_m2', 'same_reference_area_equivalence_unverified', 'category', 'a13_total', 'c_known_subtotal', 'c_complete',
                'a1a3_c1c4_known_subtotal', 'd_known_subtotal', 'd_complete', 'mass_known_kg', 'mass_complete', 'error_codes', 'input_locator'])
    for e in entries:
        r = e['result']
        base = ['SYNTHETIC', 'GENERATED', e['id'], e['edge'] or '-', '-' if e['reference_area_m2'] is None else num(e['reference_area_m2']),
                'yes' if e['same_reference_area'] else 'no', e['category']]
        if r['status'] == 'REJECTED':
            w.writerow(base + ['-'] * 8 + [';'.join(x['code'] for x in r['errors']), e['input_locator']])
            continue
        t = r['totals']
        q = lambda v: 'UNKNOWN' if v is None else repr(v)
        yn = lambda b: 'yes' if b else 'no'
        w.writerow(base + [q(t['a13_total']), q(t['c_known_subtotal']), yn(t['c_complete']), q(t['a1_c_known_subtotal']),
                           q(t['d_known_subtotal']), yn(t['d_complete']), q(t['mass_known_kg']), yn(t['mass_complete']), '-', e['input_locator']])
    return buf.getvalue()


def main(argv=None):
    ap = argparse.ArgumentParser(description='SYNTHETIC GENERATED assembly gallery')
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--seed', type=int, default=SEED)
    ap.add_argument('--inputs', help='evaluate {"assemblies": [baucode-demo-input/1, ...]} instead of generating')
    a = ap.parse_args(argv)
    if a.inputs:
        try:
            with open(a.inputs, 'rb') as fh:
                raw = json.loads(fh.read().decode('utf-8'))
            docs = raw['assemblies']
            if not isinstance(docs, list):
                raise TypeError('assemblies must be a list')
        except (OSError, ValueError, KeyError, TypeError) as e:
            print(f'cannot use --inputs {a.inputs}: {type(e).__name__}: {e}', file=sys.stderr)
            return 2
        src, gen, seed = os.path.basename(a.inputs.replace('\\', '/')), 'user-supplied file', None
    else:
        docs, src, gen, seed = generate(a.seed), 'generated_inputs.json', GENERATOR, a.seed
    inputs_doc = {'label': 'SYNTHETIC', 'kind': KIND, 'generator': gen, 'seed': seed, 'assemblies': docs}
    entries = evaluate_all(docs, src)
    cats = ['EVALUATED_FULL_COVERAGE', 'EVALUATED_PARTIAL_COVERAGE', 'INCOMPLETE_LAYERS', 'REJECTED']
    prov = {'label': 'SYNTHETIC', 'records_kind': KIND, 'generator': gen, 'seed': seed, 'input_source': src,
            'inputs_sha256': canon_sha(docs), 'schema_in': run_demo.SCHEMA_IN, 'schema_out': run_demo.SCHEMA_OUT,
            'evaluator': 'demo/run_demo.py evaluate() -> analysis/lib.py, analysis/model.py',
            'reference_area': f'{num(REFERENCE_FU_M2)} m2 of a fictional assembly; {EQUIV_NOTE}',
            'summary': {'assemblies': len(entries),
                        'product_records': sum(len(d.get('products', [])) for d in docs if isinstance(d, dict)),
                        'by_category': {c: sum(1 for e in entries if e['category'] == c) for c in cats},
                        'same_reference_area_equivalence_unverified': sum(1 for e in entries if e['same_reference_area']),
                        'edges': {e['id']: e['edge'] for e in entries}},
            'equivalence': 'unverified: no independent expected values exist for generated records'}
    os.makedirs(a.out, exist_ok=True)
    files = {'generated_inputs.json': json.dumps(inputs_doc, indent=1, ensure_ascii=False) + '\n',
             'gallery.json': json.dumps({'label': 'SYNTHETIC', 'kind': KIND, 'provenance': prov, 'assemblies': entries},
                                        indent=1, ensure_ascii=False, allow_nan=False) + '\n',
             'gallery.csv': render_csv(entries), 'gallery.html': render_html(entries, prov)}
    for name, body in files.items():
        with open(os.path.join(a.out, name), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(body)
    prov_out = dict(prov, files_sha256={n: hashlib.sha256(b.encode('utf-8')).hexdigest() for n, b in files.items()})
    with open(os.path.join(a.out, 'provenance.json'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(json.dumps(prov_out, indent=1, ensure_ascii=False) + '\n')
    s = prov['summary']
    print(f"SYNTHETIC GENERATED gallery: {s['assemblies']} assemblies, {s['product_records']} product records, seed {seed} -> {a.out}/gallery.html")
    print('  ' + ', '.join(f'{k} {v}' for k, v in s['by_category'].items()) + f" | same reference area (equivalence unverified) {s['same_reference_area_equivalence_unverified']}")
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
