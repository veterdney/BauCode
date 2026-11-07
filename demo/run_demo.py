"""SYNTHETIC wall demo: one JSON input -> result.json, layers.csv, report.md (stdlib only).

Run from the repository root:
  python demo/run_demo.py
  python demo/run_demo.py --input demo/input/synthetic_wall_replaced.json --out demo/output/replaced

All carbon arithmetic goes through the production code in analysis/ (lib.ref_quantity,
lib.per_m3_checked, lib.to_metres, lib.layer_mass_kg, model.per_m2 via model.module_breakdown,
model.pool_median). This file only validates input, aggregates layers and renders outputs.
Input schema: docs/INPUT_SCHEMA.md.

Exit codes: 0 EVALUATED, 2 REJECTED (invalid input, no numbers), 3 INCOMPLETE_LAYERS,
            4 output differs from the expected file, 1 internal error.
"""
import argparse, csv, hashlib, html, io, json, math, os, sys, traceback

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'analysis'))
import lib, model  # noqa: E402

SCHEMA_IN = 'baucode-demo-input/1'
SCHEMA_OUT = 'baucode-demo-result/1'
LABEL = 'SYNTHETIC'
DEFAULT_INPUT = 'demo/input/synthetic_wall.json'
DEFAULT_OUT = 'demo/output/default'
EXPECTED_DIR = 'demo/expected'
KEY = 'GWPtotal (A2)'
UNIT_TO_PRODUCTION = {'m3': 'm3', 'kg': 'kg', 'm2': 'qm'}
MODULES = ('A1-A3',) + model.A_SUB + model.C_MODS + ('D',)
POOL_STATISTIC = 'median of product pool (descriptive; not a wall comparison)'
EXIT_EVALUATED, EXIT_INTERNAL, EXIT_REJECTED, EXIT_INCOMPLETE, EXIT_EXPECTED_MISMATCH = 0, 1, 2, 3, 4
TOL = 1e-9


def number(x):
    """finite JSON number (not bool) -> float, else None"""
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return None
    try:
        x = float(x)
    except OverflowError:  # a JSON integer beyond float range (e.g. 10**400) is not a finite number
        return None
    return x if math.isfinite(x) else None


def text(x):
    return x.strip() if isinstance(x, str) and x.strip() else None


def canonical_id(x):
    """identifier as given if it is a non-empty string with no surrounding whitespace, else None (never silently stripped)"""
    return x if isinstance(x, str) and x and x == x.strip() else None


def to_record(p):
    """demo product -> production-schema record (the column names analysis/products.csv uses)"""
    unit = p.get('unit')
    # only strings are looked up: a dict/list unit is unhashable; its str() form is then rejected as UNIT_UNSUPPORTED
    mapped = UNIT_TO_PRODUCTION.get(unit) if isinstance(unit, str) else None
    rec = {'Bezugseinheit': mapped or ('' if unit is None else str(unit)),
           'Bezugsgroesse': '' if p.get('ref_quantity') is None else str(p['ref_quantity']),
           'Rohdichte (kg/m3)': '' if p.get('density_kg_m3') is None else repr(float(p['density_kg_m3'])),
           'Schuettdichte (kg/m3)': '' if p.get('bulk_density_kg_m3') is None else repr(float(p['bulk_density_kg_m3'])),
           'Umrechungsfaktor auf 1kg': '', 'Schichtdicke (m)': ''}
    for m, v in p['modules'].items():
        rec[f'{m}|{KEY}'] = repr(float(v))
    return rec


def validate(doc):
    """Return (errors, records, layer_specs). Every problem is reported; nothing defaults silently."""
    errs = []
    err = lambda where, code, detail='': errs.append({'where': where, 'code': code, 'detail': detail})
    if not isinstance(doc, dict):
        err('$', 'INPUT_NOT_OBJECT', 'top level must be a JSON object')
        return errs, {}, []
    if doc.get('schema') != SCHEMA_IN:
        err('schema', 'SCHEMA_UNSUPPORTED', f'expected {SCHEMA_IN!r}')
    if doc.get('label') != LABEL:
        err('label', 'LABEL_NOT_SYNTHETIC', 'this demo only accepts synthetic input')
    wall = doc.get('wall') if isinstance(doc.get('wall'), dict) else {}
    area = number(wall.get('area_m2'))
    if not text(wall.get('id')):
        err('wall.id', 'WALL_ID_MISSING')
    if area is None or area <= 0:
        err('wall.area_m2', 'WALL_AREA_INVALID', 'finite number > 0 required')

    records = {}
    products = doc.get('products')
    if not isinstance(products, list):
        err('products', 'PRODUCTS_NOT_LIST')
        products = []
    for i, p in enumerate(products):
        w = f'products[{i}]'
        if not isinstance(p, dict):
            err(w, 'PRODUCT_NOT_OBJECT')
            continue
        pid = canonical_id(p.get('id'))
        if not pid:
            err(w + '.id', 'PRODUCT_ID_INVALID', 'non-empty string without leading/trailing whitespace')
            continue
        if pid in records:
            err(w + '.id', 'DUPLICATE_ID', pid)
        if not text(p.get('source')):
            err(w + '.source', 'SOURCE_MISSING', 'provenance is required')
        if not text(p.get('scenario')):
            err(w + '.scenario', 'SCENARIO_MISSING', 'a scenario label is required')
        bad = False
        for k in ('density_kg_m3', 'bulk_density_kg_m3'):
            if k in p and (number(p[k]) is None or p[k] <= 0):
                err(f'{w}.{k}', 'DENSITY_INVALID', 'finite number > 0 required when given')
                bad = True
        mods = p.get('modules')
        if not isinstance(mods, dict) or not mods:
            err(w + '.modules', 'MODULES_MISSING')
            continue
        bad_mod = bad
        for m, v in mods.items():
            if m not in MODULES:
                err(f'{w}.modules.{m}', 'MODULE_UNSUPPORTED', f'allowed: {", ".join(MODULES)}')
                bad_mod = True
            elif number(v) is None:
                err(f'{w}.modules.{m}', 'MODULE_VALUE_INVALID', 'finite number required; omit undeclared modules')
                bad_mod = True
        if bad_mod:
            continue
        rec = to_record(p)
        if rec['Bezugseinheit'] == 'qm':
            _, code = lib.ref_quantity(rec)
        else:
            _, code = lib.per_m3_checked(rec)
        if code:
            err(w, code, f"unit={p.get('unit')!r} ref_quantity={p.get('ref_quantity')!r}")
            continue
        records[pid] = {'rec': rec, 'source': p['source'].strip(), 'scenario': text(p.get('scenario')), 'unit': p['unit'],
                        'density': lib.dens(rec)}

    specs = []
    layers = doc.get('layers')
    if not isinstance(layers, list) or not layers:
        err('layers', 'NO_LAYERS', 'at least one layer is required')
        layers = []
    seen = set()
    known_ids = {canonical_id(p.get('id')) for p in products if isinstance(p, dict)} - {None}
    for i, l in enumerate(layers):
        w = f'layers[{i}]'
        if not isinstance(l, dict):
            err(w, 'LAYER_NOT_OBJECT')
            continue
        lid = text(l.get('id'))
        if not lid or lid in seen:
            err(w + '.id', 'LAYER_ID_INVALID', 'non-empty and unique')
        seen.add(lid)
        mult = number(l.get('multiplier'))
        if mult is None or mult <= 0:
            err(w + '.multiplier', 'MULTIPLIER_INVALID', 'explicit finite number > 0 required')
        pids = l.get('product_ids')
        if not isinstance(pids, list):
            err(w + '.product_ids', 'PRODUCT_IDS_NOT_LIST')
            pids = []
        refs = []
        # type/shape checked before any set/dict lookup; a repeated reference would silently weight the pool median
        for pid in pids:
            if canonical_id(pid) is None:
                err(w + '.product_ids', 'PRODUCT_REF_INVALID', repr(pid)[:80])
            elif pid in refs:
                err(w + '.product_ids', 'DUPLICATE_PRODUCT_REF', repr(pid))
            else:
                refs.append(pid)
                if pid not in known_ids:
                    err(w + '.product_ids', 'UNKNOWN_PRODUCT_ID', repr(pid))
        pids = refs
        thick = None
        if l.get('thickness') is not None:
            t = l['thickness'] if isinstance(l['thickness'], dict) else {}
            thick, code = lib.to_metres(t.get('value'), t.get('unit'))
            if code:
                err(w + '.thickness', code, repr(l['thickness']))
        pool = [records[p] for p in pids if p in records]
        if thick is None and any(r['rec']['Bezugseinheit'] != 'qm' for r in pool) and l.get('thickness') is None:
            err(w + '.thickness', 'THICKNESS_REQUIRED', 'm3/kg reference basis needs a layer thickness')
        scen = sorted({r['scenario'] for r in pool if r['scenario']})  # missing labels are already SCENARIO_MISSING
        if len(scen) > 1:
            err(w + '.product_ids', 'SCENARIO_CONFLICT', 'pool mixes scenarios ' + ', '.join(scen))
        specs.append({'id': lid, 'name': l.get('name'), 'pids': list(pids), 'thick': thick, 'mult': mult})
    return errs, records, specs


def evaluate_layer(spec, records, area):
    pool = [records[p] for p in spec['pids']]
    scale = area * spec['mult']
    out = {'id': spec['id'], 'name': spec['name'], 'status': 'KNOWN', 'reason': None,
           'products': spec['pids'], 'sources': [r['source'] for r in pool],
           'scenario': pool[0]['scenario'] if pool else None, 'reference_units': sorted({r['unit'] for r in pool}),
           'thickness_m': spec['thick'], 'multiplier': spec['mult'], 'pool_size': len(pool), 'pool_statistic': POOL_STATISTIC,
           'a13': None, 'a13_source': None, 'a13_overlap': False, 'c_known': None, 'c_modules': [], 'c_missing': list(model.C_MODS),
           'c_complete': False, 'd': None, 'mass_kg': None, 'density_used_kg_m3': None, 'density_note': None}
    units = {r['rec']['Bezugseinheit'] for r in pool}
    if units == {'m3'}:
        out['density_note'] = 'not used: m3 reference basis'
    elif units == {'qm'}:
        out['density_note'] = 'not used: m2 reference basis'
    elif 'kg' in units:
        kg_d = [r['density'] for r in pool if r['rec']['Bezugseinheit'] == 'kg']
        out['density_used_kg_m3'] = model.pool_median(kg_d)
        out['density_note'] = 'used: kg reference basis converted with product density (lib.dens)'
    dens = [r['density'] for r in pool]
    if pool and spec['thick'] is not None and all(d is not None for d in dens):
        out['mass_kg'] = lib.layer_mass_kg(scale, spec['thick'], model.pool_median(dens))
    if not pool:
        out.update(status='UNKNOWN', reason='EMPTY_POOL')
        return out
    bd = [model.module_breakdown(r['rec'], spec['thick'], area=r['rec']['Bezugseinheit'] == 'qm', key=KEY) for r in pool]
    srcs = sorted({b['a13_source'] for b in bd if b['a13_source']})
    out['a13_source'] = srcs[0] if len(srcs) == 1 else ('mixed' if srcs else None)
    out['a13_overlap'] = any(b['a13_overlap'] for b in bd)
    common = [m for m in model.C_MODS if all(m in b['c_by_module'] for b in bd)]
    out['c_modules'] = common
    out['c_missing'] = [m for m in model.C_MODS if m not in common]
    out['c_complete'] = not out['c_missing']
    if common:
        out['c_known'] = model.pool_median([sum(b['c_by_module'][m] for m in common) for b in bd]) * scale
    if all(b['d'] is not None for b in bd):
        out['d'] = model.pool_median([b['d'] for b in bd]) * scale
    if any(b['a13'] is None for b in bd):
        out.update(status='UNKNOWN', reason='A13_UNDECLARED')
        return out
    out['a13'] = model.pool_median([b['a13'] for b in bd]) * scale
    return out


def ssum(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) if xs else None


def evaluate(doc, input_name='<inline>', input_sha256=None):
    head = {'schema': SCHEMA_OUT, 'label': LABEL}
    inp = {'name': input_name, 'sha256': input_sha256}
    errs, records, specs = validate(doc)
    if errs:
        return dict(head, status='REJECTED', exit_code=EXIT_REJECTED, input=inp, errors=errs,
                    notes=['Input rejected; no numeric result is produced for invalid input.'])
    area = float(doc['wall']['area_m2'])
    layers = [evaluate_layer(s, records, area) for s in specs]
    known = [l for l in layers if l['status'] == 'KNOWN']
    complete = len(known) == len(layers)
    a13_sub = ssum(l['a13'] for l in known)
    totals = {
        'layers_known': len(known), 'layers_total': len(layers), 'layers_complete': complete,
        'a13_known_subtotal': a13_sub, 'a13_total': a13_sub if complete else None,
        'c_known_subtotal': ssum(l['c_known'] for l in known),
        'c_complete': complete and all(l['c_complete'] for l in known),
        'a1_c_known_subtotal': ssum([a13_sub, ssum(l['c_known'] for l in known)]) if known else None,
        'd_known_subtotal': ssum(l['d'] for l in known),
        'd_complete': complete and all(l['d'] is not None for l in known),
        'mass_known_kg': ssum(l['mass_kg'] for l in layers),
        'mass_complete': all(l['mass_kg'] is not None for l in layers),
    }
    status = 'EVALUATED' if complete else 'INCOMPLETE_LAYERS'
    return dict(head, status=status, exit_code=EXIT_EVALUATED if complete else EXIT_INCOMPLETE, input=inp,
                wall={'id': doc['wall']['id'], 'area_m2': area},
                units={'carbon': 'kgCO2e (GWPtotal A2) for the whole wall area', 'mass': 'kg', 'thickness': 'm'},
                layers=layers, totals=totals,
                notes=['SYNTHETIC demo data; these numbers describe no real wall or product.',
                       'UNKNOWN (null) means not declared or not computable. It is never zero and never a favourable result.',
                       'D is reported separately and is never subtracted from A1-A3 + C1-C4.',
                       'a1_c_known_subtotal is the A1-A3 + C1-C4 known subtotal for the selected modules only; '
                       'A4, A5 and B modules are outside scope, so it is not a life-cycle total.',
                       'Layer pool statistic: ' + POOL_STATISTIC + '.'])


# ---------------------------------------------------------------- rendering
def fmt(x, none='UNKNOWN'):
    """'UNKNOWN' is reserved for quantities that are genuinely unknown; absent text/optional fields render as '-'"""
    if x is None:
        return none
    if isinstance(x, bool):
        return 'yes' if x else 'no'
    if isinstance(x, float):
        return '%.12g' % x
    if isinstance(x, list):
        return ';'.join(str(v) for v in x) if x else '-'
    return str(x)


# (csv column, result key, rendering of None): quantities -> UNKNOWN, text/optional -> '-'
CSV_COLS = [('layer_id', 'id', '-'), ('status', 'status', '-'), ('reason', 'reason', '-'),
            ('products', 'products', '-'), ('sources', 'sources', '-'), ('scenario', 'scenario', '-'), ('thickness_m', 'thickness_m', '-'),
            ('multiplier', 'multiplier', '-'), ('pool_size', 'pool_size', '-'), ('a13_kgco2e', 'a13', 'UNKNOWN'), ('a13_source', 'a13_source', '-'),
            ('a13_overlap', 'a13_overlap', '-'), ('c_known_kgco2e', 'c_known', 'UNKNOWN'), ('c_modules', 'c_modules', '-'), ('c_missing', 'c_missing', '-'),
            ('c_complete', 'c_complete', '-'), ('d_kgco2e', 'd', 'UNKNOWN'), ('mass_kg', 'mass_kg', 'UNKNOWN'),
            ('density_used_kg_m3', 'density_used_kg_m3', '-'), ('density_note', 'density_note', '-')]


def render_csv(result):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['label', 'wall_id'] + [c for c, _, _ in CSV_COLS])
    for l in result.get('layers', []):
        w.writerow([LABEL, result['wall']['id']] + [fmt(l[k], none) for _, k, none in CSV_COLS])
    return buf.getvalue()


MD_ESCAPES = (('\\', '&#92;'), ('|', '&#124;'), ('`', '&#96;'), ('[', '&#91;'), (']', '&#93;'),
              ('\r\n', '<br>'), ('\r', '<br>'), ('\n', '<br>'))


def md(x):
    """untrusted text -> inert Markdown: HTML escaped, and pipes/newlines entity-encoded so a value can never split a table cell or row"""
    s = html.escape(str(x), quote=False)
    for a, b in MD_ESCAPES:
        s = s.replace(a, b)
    return s


def render_md(result):
    L = ['# SYNTHETIC wall demo result', '',
         '> **SYNTHETIC.** Invented demo numbers. This is not a real wall, not an Oekobaudat record,',
         '> and carries no scientific standing. It ranks nothing and makes no product-choice or indoor-air claim.', '',
         f"- Input: {md(result['input']['name'])} (sha256 {md(result['input']['sha256'])})",
         f"- Status: **{result['status']}** (exit {result['exit_code']})", '']
    if result['status'] == 'REJECTED':
        L += ['Input rejected. No numeric result is produced.', '', '| where | code | detail |', '|---|---|---|']
        L += [f"| {md(e['where'])} | {md(e['code'])} | {md(e['detail'])} |" for e in result['errors']]
        return '\n'.join(L) + '\n'
    t = result['totals']
    L += [f"Wall {md(result['wall']['id'])}, area {fmt(result['wall']['area_m2'])} m2. Carbon in kgCO2e (GWPtotal A2) for the whole wall.", '',
          '| quantity | value | coverage |', '|---|---|---|',
          f"| A1-A3 total | {fmt(t['a13_total'])} | layers known {t['layers_known']}/{t['layers_total']} |",
          f"| A1-A3 known subtotal | {fmt(t['a13_known_subtotal'])} | |",
          f"| C1-C4 known subtotal | {fmt(t['c_known_subtotal'])} | complete: {fmt(t['c_complete'])} |",
          f"| A1-A3 + C1-C4 known subtotal | {fmt(t['a1_c_known_subtotal'])} | complete for selected modules: {fmt(t['c_complete'] and t['layers_complete'])} |",
          f"| D known subtotal (partial; separate, not subtracted) | {fmt(t['d_known_subtotal'])} | complete: {fmt(t['d_complete'])} |",
          f"| known mass subtotal kg | {fmt(t['mass_known_kg'])} | complete: {fmt(t['mass_complete'])} |", '',
          '| layer | status | products | scenario | thickness m | A1-A3 | C known | C missing | D | mass kg | density note |',
          '|---|---|---|---|---|---|---|---|---|---|---|']
    for l in result['layers']:
        L.append(f"| {md(l['id'])} | {md(l['status'])}{' (' + md(l['reason']) + ')' if l['reason'] else ''} | {md(fmt(l['products']))} | {md(fmt(l['scenario'], '-'))} | "
                 f"{fmt(l['thickness_m'], '-')} | {fmt(l['a13'])} | {fmt(l['c_known'])} | {fmt(l['c_missing'])} | {fmt(l['d'])} | {fmt(l['mass_kg'])} | {md(fmt(l['density_note'], '-'))} |")
    L += ['', '## How to read this', ''] + [f'- {n}' for n in result['notes']]
    L += ['- Product sources are listed per layer in `layers.csv` and `result.json`.',
          '- Limits: GWP only; no replacement cycles (B4) or other B modules; no U-value; DRAFT policies for',
          '  partial C coverage, A1-A3 aggregate/submodule overlap and scenario conflicts (see docs/INPUT_SCHEMA.md).',
          '- Scope: "A1-A3 + C1-C4" covers the selected modules only. A4, A5 and B modules are outside scope,',
          '  so "complete for selected modules" never means a complete life cycle.',
          '- Conservative coverage coupling: wall C and D subtotals count only layers with a known A1-A3.',
          '  A layer whose A1-A3 is UNKNOWN adds no C or D to the wall subtotals, and C and D are then reported incomplete,',
          '  even if that layer declares C or D. C and D completeness is therefore never claimed independently of A1-A3.']
    return '\n'.join(L) + '\n'


def write_outputs(result, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    blobs = {'result.json': json.dumps(result, indent=1, ensure_ascii=False, allow_nan=False) + '\n',
             'layers.csv': render_csv(result), 'report.md': render_md(result)}
    for name, body in blobs.items():
        with open(os.path.join(out_dir, name), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(body)
    return list(blobs)


# ---------------------------------------------------------------- expected-file check
def get_path(obj, dotted):
    for part in dotted.split('.'):
        if isinstance(obj, dict) and part in obj:
            obj = obj[part]
        elif isinstance(obj, list) and part.isdigit() and int(part) < len(obj):
            obj = obj[int(part)]
        else:
            return KeyError
    return obj


def same(a, e):
    if e is None or isinstance(e, bool):
        return a is e
    if isinstance(e, (int, float)):
        return not isinstance(a, bool) and isinstance(a, (int, float)) and math.isclose(a, e, rel_tol=TOL, abs_tol=TOL)
    return a == e


def check_expected(result, path):
    with open(path, encoding='utf-8') as fh:
        exp = json.load(fh)
    bad = [{'path': p, 'expected': v, 'actual': None if get_path(result, p) is KeyError else get_path(result, p)}
           for p, v in exp['expect'].items() if get_path(result, p) is KeyError or not same(get_path(result, p), v)]
    return {'expected_file': os.path.basename(path), 'derivation': exp.get('derivation'), 'checked': len(exp['expect']), 'mismatches': bad}


def load(path):
    try:
        with open(path, 'rb') as fh:
            raw = fh.read()
    except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
        return None, None, {'where': 'input', 'code': 'INPUT_NOT_FOUND', 'detail': type(e).__name__}
    sha = hashlib.sha256(raw).hexdigest()
    try:
        return json.loads(raw.decode('utf-8')), sha, None
    except (UnicodeDecodeError, ValueError) as e:
        return None, sha, {'where': 'input', 'code': 'INPUT_NOT_JSON', 'detail': str(e)}


def main(argv=None):
    ap = argparse.ArgumentParser(description='SYNTHETIC wall demo (see docs/INPUT_SCHEMA.md)')
    ap.add_argument('--input', default=DEFAULT_INPUT)
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--expected', help=f'expected-values file; default: {EXPECTED_DIR}/<input stem>.expected.json if it exists')
    ap.add_argument('--no-expected', action='store_true')
    a = ap.parse_args(argv)
    # only the file name goes into outputs, so results do not depend on how the path was spelled
    name = os.path.basename(os.path.normpath(a.input.replace('\\', '/')))
    doc, sha, load_err = load(a.input)
    if load_err:
        result = {'schema': SCHEMA_OUT, 'label': LABEL, 'status': 'REJECTED', 'exit_code': EXIT_REJECTED,
                  'input': {'name': name, 'sha256': sha}, 'errors': [load_err],
                  'notes': ['Input rejected; no numeric result is produced for invalid input.']}
    else:
        result = evaluate(doc, name, sha)
    write_outputs(result, a.out)
    code = result['exit_code']
    print(f"SYNTHETIC demo: {result['status']} -> {a.out}/result.json, layers.csv, report.md")
    if result['status'] == 'REJECTED':
        for e in result['errors']:
            print(f"  REJECTED {e['where']}: {e['code']} {e['detail']}", file=sys.stderr)
        return code
    t = result['totals']
    print(f"  A1-A3 total={fmt(t['a13_total'])} known subtotal={fmt(t['a13_known_subtotal'])} | C known={fmt(t['c_known_subtotal'])} "
          f"complete={fmt(t['c_complete'])} | D separate={fmt(t['d_known_subtotal'])} complete={fmt(t['d_complete'])} (kgCO2e)")
    exp = a.expected
    if exp is None and not a.no_expected:
        stem = os.path.splitext(name)[0]
        cand = os.path.join(ROOT, EXPECTED_DIR, stem + '.expected.json')
        exp = cand if os.path.exists(cand) else None
    if exp and not a.no_expected:
        chk = check_expected(result, exp)
        with open(os.path.join(a.out, 'expected_check.json'), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(json.dumps(chk, indent=1) + '\n')
        if chk['mismatches']:
            print(f"  EXPECTED MISMATCH vs {chk['expected_file']}: {chk['mismatches']}", file=sys.stderr)
            return EXIT_EXPECTED_MISMATCH
        print(f"  matches {chk['expected_file']} ({chk['checked']} agent hand-derived values)")
    return code


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(EXIT_INTERNAL)
