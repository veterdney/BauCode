"""Supplementary P2 reproduction (NOT an exact-20 case, NOT an eval statistic).

Builds tiny in-memory variants of demo/input/synthetic_wall.json and calls demo.run_demo / analysis.lib directly:
  a) product unit given as {} or []                  -> REJECTED, error code, exit 2, no numbers, no exception
  b) lib.to_metres with unit {} / [] and layer thickness unit {} / [] -> error code, no exception
  c) integers too large for float (10**400)          -> REJECTED with an error code, no exception, no numbers
  d) report.md: raw HTML, pipes and newlines in input name, IDs, scenario and error details are escaped,
     so no raw <script> survives, table rows keep their cell count and the text is still present
Exit 0 only when every expectation holds, 1 otherwise. Usage: python tests/repro_p2.py
"""
import copy, json, os, re, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'demo'))
import run_demo  # noqa: E402
import lib  # noqa: E402  (run_demo puts analysis/ on sys.path)

with open(os.path.join(ROOT, 'demo', 'input', 'synthetic_wall.json'), encoding='utf-8') as fh:
    BASE = json.load(fh)

HUGE = 10 ** 400
EVIL = 'X<script>alert(1)</script>|pipe\nnext'


def variant(edit):
    d = copy.deepcopy(BASE)
    edit(d)
    return d


def setp(i, key, value):
    return lambda d: d['products'][i].__setitem__(key, value)


def setmod(i, mod, value):
    return lambda d: d['products'][i]['modules'].__setitem__(mod, value)


def set_thick(layer, key, value):
    return lambda d: d['layers'][layer]['thickness'].__setitem__(key, value)


def first_with_thickness():
    return next(i for i, l in enumerate(BASE['layers']) if isinstance(l.get('thickness'), dict))


TL = first_with_thickness()

REJECT_VARIANTS = [
    ('a.unit_dict', setp(0, 'unit', {})),
    ('a.unit_list', setp(0, 'unit', [])),
    ('b.thickness_unit_dict', set_thick(TL, 'unit', {})),
    ('b.thickness_unit_list', set_thick(TL, 'unit', [])),
    ('c.huge_ref_quantity', setp(0, 'ref_quantity', HUGE)),
    ('c.huge_module_value', setmod(0, 'A1-A3', HUGE)),
    ('c.huge_density', setp(0, 'density_kg_m3', HUGE)),
    ('c.huge_area', lambda d: d['wall'].__setitem__('area_m2', HUGE)),
    ('c.huge_multiplier', lambda d: d['layers'][0].__setitem__('multiplier', HUGE)),
    ('c.huge_thickness_value', set_thick(TL, 'value', HUGE)),
]


def run_reject(name, edit):
    try:
        r = run_demo.evaluate(variant(edit), input_name=f'variant:{name}')
        got = {'status': r['status'], 'exit_code': r['exit_code'], 'error_codes': [e['code'] for e in r.get('errors', [])],
               'has_numbers': 'totals' in r or 'layers' in r}
        ok = got['status'] == 'REJECTED' and got['exit_code'] == 2 and bool(got['error_codes']) and not got['has_numbers']
    except Exception as e:
        got, ok = {'exception': f'{type(e).__name__}: {e}'}, False
    return ok, got


def run_to_metres(unit):
    try:
        v, code = lib.to_metres(1, unit)
        return v is None and isinstance(code, str) and bool(code), {'value': v, 'code': code}
    except Exception as e:
        return False, {'exception': f'{type(e).__name__}: {e}'}


def run_cli_unit_dict():
    """end-to-end CLI: exit 2, REJECTED result.json without numbers, no traceback on stderr"""
    tmp = tempfile.mkdtemp(prefix='repro_p2_')
    try:
        ip = os.path.join(tmp, 'unit_dict.json')
        with open(ip, 'w', encoding='utf-8') as fh:
            json.dump(variant(setp(0, 'unit', {})), fh)
        p = subprocess.run([sys.executable, os.path.join(ROOT, 'demo', 'run_demo.py'), '--input', ip, '--out', os.path.join(tmp, 'out')],
                           cwd=ROOT, capture_output=True, text=True)
        payload = {}
        rp = os.path.join(tmp, 'out', 'result.json')
        if os.path.exists(rp):
            with open(rp, encoding='utf-8') as fh:
                payload = json.load(fh)
        got = {'exit': p.returncode, 'status': payload.get('status'), 'error_codes': [e['code'] for e in payload.get('errors', [])],
               'has_numbers': 'totals' in payload or 'layers' in payload, 'traceback': 'Traceback' in p.stderr}
        return p.returncode == 2 and got['status'] == 'REJECTED' and got['error_codes'] and not got['has_numbers'] and not got['traceback'], got
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def table_blocks(md):
    """list of tables, each a list of row cell counts (header first); a pipe inside a cell must not split it"""
    blocks, cur = [], None
    for line in md.split('\n'):
        if line.startswith('|'):
            cur = cur if cur is not None else []
            cur.append(len(line.strip().strip('|').split('|')))
        elif cur is not None:
            blocks.append(cur)
            cur = None
    if cur is not None:
        blocks.append(cur)
    return blocks


def md_check(result, expected_rows):
    md = run_demo.render_md(result)
    blocks = table_blocks(md)
    shape_ok = all(len(set(b)) == 1 for b in blocks)
    rows_ok = [len(b) - 2 for b in blocks] == expected_rows  # minus header and separator
    no_raw = not re.search(r'<\s*script', md, re.I)
    intact = 'alert(1)' in md and '&lt;script&gt;' in md
    got = {'tables_rows': [len(b) - 2 for b in blocks], 'consistent_cells': shape_ok, 'raw_script': not no_raw, 'text_present': intact}
    return shape_ok and rows_ok and no_raw and intact, got


def evil_evaluated():
    d = copy.deepcopy(BASE)
    d['wall']['id'] = EVIL
    d['layers'][0]['id'] = 'L' + EVIL
    d['layers'][0]['name'] = EVIL
    for p in d['products']:
        p['scenario'] = 'S' + EVIL
    old = d['products'][0]['id']
    d['products'][0]['id'] = 'P' + EVIL
    for l in d['layers']:
        l['product_ids'] = ['P' + EVIL if x == old else x for x in l['product_ids']]
    return run_demo.evaluate(d, input_name='in' + EVIL)


def evil_rejected():
    d = copy.deepcopy(BASE)
    d['products'][0]['unit'] = EVIL
    d['products'][1]['modules'][EVIL] = 1.0
    return run_demo.evaluate(d, input_name='in' + EVIL)


def main():
    rows = []
    for name, edit in REJECT_VARIANTS:
        rows.append((name, *run_reject(name, edit)))
    rows.append(('a.cli_unit_dict', *run_cli_unit_dict()))
    for name, unit in (('b.lib_to_metres_dict', {}), ('b.lib_to_metres_list', [])):
        rows.append((name, *run_to_metres(unit)))
    try:
        r = evil_evaluated()
        assert r['status'] in ('EVALUATED', 'INCOMPLETE_LAYERS'), r.get('errors')
        rows.append(('d.markdown_evaluated', *md_check(r, [6, len(r['layers'])])))
    except Exception as e:
        rows.append(('d.markdown_evaluated', False, {'exception': f'{type(e).__name__}: {e}'}))
    try:
        r = evil_rejected()
        rows.append(('d.markdown_rejected', *md_check(r, [len(r['errors'])])))
    except Exception as e:
        rows.append(('d.markdown_rejected', False, {'exception': f'{type(e).__name__}: {e}'}))
    for name, ok, got in rows:
        print(f"{'OK  ' if ok else 'MISS'} {name:26} {json.dumps(got)}")
    n_ok = sum(ok for _, ok, _ in rows)
    print(f'P2 reproduction: {n_ok}/{len(rows)} expectations hold (supplementary, not an eval statistic)')
    return 0 if n_ok == len(rows) else 1


if __name__ == '__main__':
    sys.exit(main())
