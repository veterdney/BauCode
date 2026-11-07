"""Descriptive input-rejection counts and arithmetic error over an EXISTING exact-20 results file.

Not an acceptance suite: it re-reads a results JSON written by tests/run_exact20.py,
changes nothing, and always exits 0 when the file is readable (3 otherwise).

Positive = input that the frozen manifest expects to be REJECTED (invalid/unsupported).
Only end-to-end demo probes (op demo_eval / demo_cli) are counted, because only they
make an accept/reject decision. Abstention (INCOMPLETE_LAYERS on an expected-valid input)
and probes that did not execute are reported separately, never folded into TN/TP.

Usage: python tests/confusion_exact20.py tests/results_final.json [--out PATH]
"""
import argparse, json, math, sys

MISSING = object()
RECOGNIZED = ('REJECTED', 'EVALUATED', 'INCOMPLETE_LAYERS')


def get_path(obj, dotted):
    for part in dotted.split('.'):
        if isinstance(obj, dict) and part in obj:
            obj = obj[part]
        elif isinstance(obj, list) and part.isdigit() and int(part) < len(obj):
            obj = obj[int(part)]
        else:
            return MISSING
    return obj


def numeric_pairs(m):
    """(where, expected, actual) for every numeric expectation of an executed probe"""
    e, a = m['expected'], m.get('actual')
    out = []
    if isinstance(e.get('value'), (int, float)) and not isinstance(e.get('value'), bool):
        out.append(('value', e['value'], a))
    for k, v in e.get('fields', {}).items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            out.append((k, v, a.get(k, MISSING) if isinstance(a, dict) else MISSING))
    for p, v in e.get('paths', {}).items():
        if isinstance(v, (int, float)) and not isinstance(v, bool) and p not in ('exit_code',):
            out.append((p, v, get_path(a, p)))
    for i, v in enumerate(e.get('list', [])):
        out.append((f'[{i}]', v, a[i] if isinstance(a, list) and i < len(a) else MISSING))
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('results')
    ap.add_argument('--out')
    a = ap.parse_args(argv)
    try:
        with open(a.results, encoding='utf-8') as fh:
            res = json.load(fh)
    except (OSError, ValueError) as e:
        print(f'cannot read {a.results}: {e}', file=sys.stderr)
        return 3
    c = dict(TP=0, FN=0, FP=0, TN=0, abstained_on_valid=0, not_executed=0, unrecognized_positive=0, unrecognized_negative=0)
    rows, errs = [], []
    for case in res['cases']:
        for m in case['members']:
            if m['op'] in ('demo_eval', 'demo_cli'):
                pre = 'payload.' if m['op'] == 'demo_cli' else ''
                positive = m['expected'].get('paths', {}).get(pre + 'status') == 'REJECTED'
                if 'actual' not in m:
                    c['not_executed'] += 1
                    cell = 'NOT_EXECUTED'
                else:
                    st = get_path(m['actual'], pre + 'status')
                    if st not in RECOGNIZED:
                        # missing/unknown status is not a decision; never let it fall through to TN or FN
                        cell = 'UNRECOGNIZED'
                        c['unrecognized_positive' if positive else 'unrecognized_negative'] += 1
                    elif positive:
                        cell = 'TP' if st == 'REJECTED' else 'FN'
                    elif st == 'REJECTED':
                        cell = 'FP'
                    elif st == 'INCOMPLETE_LAYERS':
                        cell = 'ABSTAINED'
                        c['abstained_on_valid'] += 1
                    else:
                        cell = 'TN'
                    if cell in c:
                        c[cell] += 1
                rows.append({'probe': m['id'], 'expected_positive': positive, 'cell': cell})
            if 'actual' in m:
                for where, e, act in numeric_pairs(m):
                    if act is MISSING or isinstance(act, bool) or not isinstance(act, (int, float)) or not math.isfinite(act):
                        errs.append({'probe': m['id'], 'where': where, 'expected': e, 'actual': None if act is MISSING else act, 'abs': None, 'rel': None})
                    else:
                        ab = abs(act - e)
                        errs.append({'probe': m['id'], 'where': where, 'expected': e, 'actual': act, 'abs': ab, 'rel': ab / abs(e) if e else None})
    # denominators come from the frozen expectation, so unexecuted probes stay visible inside them
    pos = sum(1 for r in rows if r['expected_positive'])
    neg = len(rows) - pos
    c['not_executed_positive'] = sum(1 for r in rows if r['expected_positive'] and r['cell'] == 'NOT_EXECUTED')
    c['not_executed_negative'] = c['not_executed'] - c['not_executed_positive']
    fin = [x for x in errs if x['abs'] is not None]
    out = {
        'source_results': a.results, 'source_label': res.get('label'), 'manifest_sha256': res.get('manifest_sha256'),
        'definition': 'positive = input the frozen manifest expects REJECTED; counted over end-to-end demo probes only',
        'counts': c, 'denominators': {'expected_positive': pos, 'expected_negative': neg, 'decision_probes': len(rows)},
        'abstention_note': 'ABSTAINED = expected-valid input evaluated as INCOMPLETE_LAYERS (known subtotals only); intended by C12/C14 policy, not a TN',
        'unrecognized_note': 'UNRECOGNIZED = executed probe whose actual status is missing or not one of ' + '/'.join(RECOGNIZED) + '; an unknown outcome, outside TP/FN/FP/TN',
        'coverage': {'positive_decided': c['TP'] + c['FN'], 'negative_decided': c['TN'] + c['FP'] + c['abstained_on_valid']},
        'caveat': 'exposed synthetic regression probes; counts describe these probes only and support no general accuracy rate',
        'numeric_assertion_residuals': {
            'note': 'residual |actual-expected| over every numeric assertion, including discrete counts (pool_size, layers_known); not an accuracy metric',
            'assertions': len(errs), 'non_numeric_actual': len(errs) - len(fin),
            'max_abs_residual': max((x['abs'] for x in fin), default=None),
            'max_rel_residual': max((x['rel'] for x in fin if x['rel'] is not None), default=None)},
        'probes': rows,
    }
    text = json.dumps(out, indent=1) + '\n'
    if a.out:
        with open(a.out, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(text)
    r = out['numeric_assertion_residuals']
    print(f"positives {pos}: TP {c['TP']} FN {c['FN']} unrecognized {c['unrecognized_positive']} not-executed {c['not_executed_positive']} | "
          f"negatives {neg}: TN {c['TN']} FP {c['FP']} abstained {c['abstained_on_valid']} unrecognized {c['unrecognized_negative']} not-executed {c['not_executed_negative']} | "
          f"numeric assertion residuals n={r['assertions']} max_abs {r['max_abs_residual']} max_rel {r['max_rel_residual']}")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
