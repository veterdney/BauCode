"""Supplemental input-boundary reproduction for layer product references (NOT an exact-20 case, NOT an eval statistic).

Builds tiny in-memory variants of demo/input/synthetic_wall.json and records what demo.run_demo.evaluate
actually does. Boundary expectation: malformed, non-canonical or duplicate references are REJECTED
(exit 2, no layers/totals); the unmodified control keeps its hand-derived 185.
Exit 0 when every variant meets the expectation, 1 otherwise. Usage: python tests/repro_input_boundary.py
"""
import copy, json, os, sys

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'demo'))
import run_demo  # noqa: E402

with open(os.path.join(ROOT, 'demo', 'input', 'synthetic_wall.json'), encoding='utf-8') as fh:
    BASE = json.load(fh)
with open(os.path.join(ROOT, 'demo', 'expected', 'synthetic_wall.expected.json'), encoding='utf-8') as fh:
    HAND_A13 = json.load(fh)['expect']['totals.a13_total']


def variant(edit):
    d = copy.deepcopy(BASE)
    edit(d)
    return d


def set_ids(layer, ids):
    return lambda d: d['layers'][layer].__setitem__('product_ids', ids)


def pad_product_id(d):
    d['products'][3]['id'] = ' SYN-P4 '   # layer L2 still references 'SYN-P4'


VARIANTS = [
    ('dict_element', set_ids(0, ['SYN-P1', {}, 'SYN-P3']), 'reject'),
    ('list_element', set_ids(0, ['SYN-P1', [], 'SYN-P3']), 'reject'),
    ('number_element', set_ids(0, ['SYN-P1', 5, 'SYN-P3']), 'reject'),
    ('duplicate_reference', set_ids(0, ['SYN-P1', 'SYN-P1', 'SYN-P2', 'SYN-P3']), 'reject'),
    ('whitespace_reference', set_ids(1, [' SYN-P4 ']), 'reject'),
    ('whitespace_product_id', pad_product_id, 'reject'),
    ('control_unmodified', lambda d: None, 'control'),
]


def main():
    rows, ok_all = [], True
    for name, edit, want in VARIANTS:
        try:
            r = run_demo.evaluate(variant(edit), input_name=f'variant:{name}')
            got = {'status': r['status'], 'exit_code': r['exit_code'], 'error_codes': [e['code'] for e in r.get('errors', [])],
                   'has_numbers': 'totals' in r or 'layers' in r,
                   'a13_total': r.get('totals', {}).get('a13_total')}
        except Exception as e:
            got = {'exception': f'{type(e).__name__}: {e}'}
        if want == 'reject':
            ok = got.get('status') == 'REJECTED' and got.get('exit_code') == 2 and not got.get('has_numbers')
        else:
            ok = got.get('status') == 'EVALUATED' and abs(got['a13_total'] - HAND_A13) <= 1e-9 * abs(HAND_A13)
        ok_all &= ok
        rows.append({'variant': name, 'expectation': want, 'meets_expectation': ok, 'actual': got})
        print(f"{'OK  ' if ok else 'MISS'} {name:22} {json.dumps(got)}")
    print(f"input-boundary reproduction: {sum(r['meets_expectation'] for r in rows)}/{len(rows)} variants meet the boundary expectation (supplemental, not an eval statistic)")
    return 0 if ok_all else 1


if __name__ == '__main__':
    sys.exit(main())
