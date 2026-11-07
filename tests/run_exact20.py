"""Exact-20 synthetic regression harness (stdlib only).

Runs every probe of tests/exact20_manifest.json against the real production code
(analysis/lib.py, analysis/model.py, analysis/run.py) and the demo (demo/run_demo.py),
then writes a results JSON with per-probe PASS / FAIL / UNKNOWN / NOT RUN.

Usage (from the repository root):
  python tests/run_exact20.py --out tests/results_after.json --label after [--overwrite]
  python tests/run_exact20.py --out tests/results_faultproof.json --label faultproof --fault-hook C07-density-x2

Exit: 0 all cases PASS; 1 any case FAIL; 2 no FAIL but some case NOT RUN/UNKNOWN;
      3 manifest hash mismatch, refused overwrite, or harness error.

Where a production module cannot be imported (the base commit loads analysis/products.csv
at import time), pure legacy functions (per_m3, per_m3_val, per_m2, norm) are executed from
their original source text via ast extraction; the result records that path. Nothing is
monkeypatched and no products.csv is created.
"""
import argparse, ast, hashlib, importlib.util, inspect, json, math, os, platform, re, shutil
import subprocess, sys, tempfile, time, traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(ROOT, 'analysis')
MANIFEST = 'tests/exact20_manifest.json'
MANIFEST_SHA = 'tests/exact20_manifest.sha256'
DEMO = 'demo/run_demo.py'
REL_TOL = ABS_TOL = 1e-9
FAULT_HOOKS = ('C07-density-x2',)
MISSING = object()
# keep __pycache__ out of the working tree (in-process imports and child processes)
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'


class NotRun(Exception):
    """Probe could not be exercised (surface absent / module not importable)."""


def canonical_sha256(path):
    with open(path, 'rb') as fh:
        # CRLF normalised so a Windows checkout with autocrlf still verifies
        return hashlib.sha256(fh.read().replace(b'\r\n', b'\n')).hexdigest()


# ---------------------------------------------------------------- production access
class Production:
    def __init__(self):
        self.lib = self.model = self.run = None
        self.import_error = None
        if ANALYSIS not in sys.path:
            sys.path.insert(0, ANALYSIS)
        try:
            import lib, model  # noqa: E401
            self.lib, self.model = lib, model
            import run
            self.run = run
        except Exception as e:  # recorded, never hidden
            self.import_error = f'{type(e).__name__}: {e}'
        self._ast = None

    def path(self):
        return 'import' if self.import_error is None else 'ast-extracted original source (module import failed: %s)' % self.import_error

    def ast_ns(self):
        """Execute only the function definitions of the original files (no module-level data load)."""
        if self._ast is None:
            ns = {}
            exec(compile('import csv, re, math, statistics as st', '<ast-prelude>', 'exec'), ns)
            for rel, keep in (('analysis/lib.py', None), ('analysis/model.py', {'per_m2'}), ('analysis/run.py', {'norm'})):
                with open(os.path.join(ROOT, rel), encoding='utf-8') as fh:
                    tree = ast.parse(fh.read(), rel)
                body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and (keep is None or n.name in keep)]
                exec(compile(ast.Module(body=body, type_ignores=[]), rel, 'exec'), ns)
            self._ast = ns
        return self._ast

    def fn(self, module, name, legacy=True):
        mod = getattr(self, module)
        if mod is not None:
            if not hasattr(mod, name):
                raise NotRun(f'surface absent: {module}.{name}')
            return getattr(mod, name), 'import'
        if legacy:
            ns = self.ast_ns()
            if name in ns:
                return ns[name], self.path()
        raise NotRun(f'production module {module} not importable ({self.import_error}); {module}.{name} cannot be exercised')

    def needs_rows(self, module, name):
        f, how = self.fn(module, name, legacy=False)
        if 'rows' not in inspect.signature(f).parameters:
            raise NotRun(f'surface absent: {module}.{name} has no injectable rows parameter')
        return f, how


def load_demo():
    path = os.path.join(ROOT, DEMO)
    if not os.path.exists(path):
        raise NotRun(f'surface absent: {DEMO} does not exist')
    spec = importlib.util.spec_from_file_location('run_demo', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- comparison
def jsonable(x):
    if isinstance(x, float) and not math.isfinite(x):
        return repr(x)
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    return repr(x)


def matches(actual, expected):
    if expected is None:
        return actual is None
    if isinstance(expected, bool):
        return actual is expected
    if isinstance(expected, (int, float)):
        if isinstance(actual, bool) or not isinstance(actual, (int, float)):
            return False
        return math.isclose(actual, expected, rel_tol=REL_TOL, abs_tol=ABS_TOL)
    if isinstance(expected, list):
        return isinstance(actual, (list, tuple)) and len(actual) == len(expected) and all(matches(a, e) for a, e in zip(actual, expected))
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(k in actual and matches(actual[k], v) for k, v in expected.items())
    return actual == expected


def get_path(obj, dotted):
    cur = obj
    for part in dotted.split('.'):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return MISSING
    return cur


def judge(actual, expect):
    """Return (status, mismatches) for an executed probe."""
    bad = []
    if 'value' in expect and not matches(actual, expect['value']):
        bad.append({'expected': expect['value'], 'actual': jsonable(actual)})
    if 'list' in expect and not matches(actual, expect['list']):
        bad.append({'expected': expect['list'], 'actual': jsonable(actual)})
    if 'equals' in expect and not matches(actual, expect['equals']):
        bad.append({'expected': expect['equals'], 'actual': jsonable(actual)})
    for k, v in expect.get('fields', {}).items():
        a = actual.get(k, MISSING) if isinstance(actual, dict) else MISSING
        if a is MISSING or not matches(a, v):
            bad.append({'field': k, 'expected': v, 'actual': 'MISSING' if a is MISSING else jsonable(a)})
    for p, v in expect.get('paths', {}).items():
        a = get_path(actual, p)
        if a is MISSING or not matches(a, v):
            bad.append({'path': p, 'expected': v, 'actual': 'MISSING' if a is MISSING else jsonable(a)})
    for p in expect.get('absent', []):
        a = get_path(actual, p)
        if a is not MISSING:
            bad.append({'path': p, 'expected': 'absent', 'actual': jsonable(a)})
    return ('PASS' if not bad else 'FAIL'), bad


# ---------------------------------------------------------------- fault hook
def apply_fault(case_id, args, hook):
    """Perturb the ACTUAL input (never the oracle) so a deliberately failing run can be shown."""
    if hook != 'C07-density-x2' or case_id != 'C07':
        return args, False
    args = json.loads(json.dumps(args))
    rec = args.get('record')
    if rec and rec.get('Rohdichte (kg/m3)'):
        rec['Rohdichte (kg/m3)'] = str(float(rec['Rohdichte (kg/m3)']) * 2)
    for p in (args.get('doc') or {}).get('products', []):
        if 'density_kg_m3' in p:
            p['density_kg_m3'] = p['density_kg_m3'] * 2
    return args, True


# ---------------------------------------------------------------- ops
def tup_asm(asm):
    return [tuple(x) for x in asm]


def run_cli(input_path, out_dir):
    p = subprocess.run([sys.executable, DEMO, '--input', input_path, '--out', out_dir],
                       cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    payload = None
    rp = os.path.join(out_dir, 'result.json')
    if os.path.exists(rp):
        with open(rp, encoding='utf-8') as fh:
            payload = json.load(fh)
    return p, payload


def read_outputs(out_dir):
    out = {}
    for name in ('result.json', 'layers.csv', 'report.md'):
        with open(os.path.join(out_dir, name), 'rb') as fh:
            out[name] = fh.read()
    return out


def op_exec(op, args, prod):
    """Return (actual, how). Raise NotRun when the surface cannot be exercised."""
    if op == 'import_production':
        code = "import sys; sys.path.insert(0, 'analysis'); import lib, model, run"
        p = subprocess.run([sys.executable, '-c', code], cwd=ROOT, capture_output=True, text=True)
        tail = (p.stderr.strip().splitlines() or [''])[-1]
        return (p.returncode == 0), f'subprocess exit {p.returncode}' + (f'; {tail}' if tail else '')
    if op == 'per_m3':
        f, how = prod.fn('lib', 'per_m3')
        return f(args['record'], args['mod']), how
    if op == 'per_m3_val':
        f, how = prod.fn('lib', 'per_m3_val')
        return f(args['record'], args['mod']), how
    if op == 'per_m2':
        f, how = prod.fn('model', 'per_m2')
        return f(args['record'], args['mod'], args['thick'], area=args['area']), how
    if op == 'norm':
        f, how = prod.fn('run', 'norm')
        return f(args['vals'], args['higher_better']), how
    if op == 'ref_quantity':
        f, how = prod.fn('lib', 'ref_quantity', legacy=False)
        q, code = f(args['record'])
        return {'q': q, 'code': code}, how
    if op == 'to_metres':
        f, how = prod.fn('lib', 'to_metres', legacy=False)
        m, code = f(args['value'], args['unit'])
        return {'m': m, 'code': code}, how
    if op == 'layer_mass_kg':
        f, how = prod.fn('lib', 'layer_mass_kg', legacy=False)
        return f(args['area_m2'], args['thickness_m'], args['density']), how
    if op == 'pool_median':
        f, how = prod.fn('model', 'pool_median', legacy=False)
        return f(args['values']), how
    if op == 'layer_stats':
        f, how = prod.needs_rows('model', 'layer_stats')
        res = f(args['layer'], args['thick'], rows=args['rows'])
        return (res[0] if res else {'_empty_pool': True}), how
    if op == 'assess':
        f, how = prod.needs_rows('model', 'assess')
        return f('synthetic probe', tup_asm(args['asm']), args['kind'], rows=args['rows']), how
    if op in ('source_expr_s4', 'source_s4_unused'):
        with open(os.path.join(ROOT, 'analysis/run.py'), encoding='utf-8') as fh:
            tree = ast.parse(fh.read(), 'analysis/run.py')
        fdef = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
        how = 'ast: original source expression in analysis/run.py run()'
        if op == 'source_s4_unused':
            loads = [n for n in ast.walk(fdef) if isinstance(n, ast.Name) and n.id == 's4' and isinstance(n.ctx, ast.Load)]
            return (len(loads) == 0), how
        asg = next(n for n in ast.walk(fdef) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 's4' for t in n.targets))
        elt = asg.value.args[0].elt
        lam = ast.Expression(ast.Lambda(args=ast.arguments(posonlyargs=[], args=[ast.arg('r')], kwonlyargs=[], kw_defaults=[], defaults=[]), body=elt))
        ast.fix_missing_locations(lam)
        return eval(compile(lam, 'analysis/run.py', 'eval'))(args['r']), how + f' line {elt.lineno}: {ast.unparse(elt)}'
    if op == 'demo_eval':
        demo = load_demo()
        if 'input_file' in args:
            with open(os.path.join(ROOT, args['input_file']), 'rb') as fh:
                raw = fh.read()
            doc, name, sha = json.loads(raw), os.path.basename(args['input_file']), hashlib.sha256(raw).hexdigest()
        else:
            doc, name, sha = args['doc'], '<manifest-inline>', None
        return demo.evaluate(doc, input_name=name, input_sha256=sha), 'in-process demo.evaluate'
    if op == 'demo_cli':
        load_demo()
        tmp = tempfile.mkdtemp(prefix='exact20_cli_')
        try:
            if 'input_path' in args:
                ip = args['input_path']
            else:
                ip = os.path.join(tmp, 'input.json')
                with open(ip, 'w', encoding='utf-8') as fh:
                    fh.write(args['raw_text'] if 'raw_text' in args else json.dumps(args['doc']))
            p, payload = run_cli(ip, os.path.join(tmp, 'out'))
            return {'exit_code': p.returncode, 'payload': payload}, 'subprocess demo CLI'
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    if op == 'demo_render':
        load_demo()
        tmp = tempfile.mkdtemp(prefix='exact20_render_')
        try:
            rel = args['input_file']
            if args['check'] == 'determinism':
                spellings = [rel.replace('\\', '/'), os.path.join(ROOT, *rel.split('/'))]
                if os.sep == '\\':
                    spellings.append(rel.replace('/', '\\'))
                blobs = []
                for i, sp in enumerate(spellings):
                    p, _ = run_cli(sp, os.path.join(tmp, f'out{i}'))
                    if p.returncode != 0:
                        return False, f'CLI exit {p.returncode} for spelling {i}'
                    blobs.append(read_outputs(os.path.join(tmp, f'out{i}')))
                return all(b == blobs[0] for b in blobs), f'{len(spellings)} path spellings (forward, absolute' + (', backslash)' if os.sep == '\\' else ')')
            p, payload = run_cli(rel, os.path.join(tmp, 'out'))
            files = read_outputs(os.path.join(tmp, 'out'))
            texts = {k: v.decode('utf-8') for k, v in files.items()}
            rows = list(__import__('csv').DictReader(texts['layers.csv'].splitlines()))
            if args['check'] == 'labels':
                ok = payload.get('label') == 'SYNTHETIC' and rows and all(r['label'] == 'SYNTHETIC' for r in rows) and 'SYNTHETIC' in texts['report.md']
                return bool(ok), 'rendered files'
            if args['check'] == 'unknown':
                lay = next(l for l in payload['layers'] if l['id'] == args['layer_id'])
                row = next(r for r in rows if r['layer_id'] == args['layer_id'])
                ok = lay[args['json_field']] is None and row[args['csv_field']] == 'UNKNOWN' and 'UNKNOWN' in texts['report.md']
                return ok, f"json={lay[args['json_field']]!r} csv={row[args['csv_field']]!r}"
            if args['check'] == 'forbidden':
                found = sorted({f'{k}:{m.group(0)}' for k, t in texts.items() for m in re.finditer(args['pattern'], t, re.I)})
                return found, 'regex over result.json, layers.csv, report.md'
            raise ValueError(f"unknown render check {args['check']}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    if op == 'git_unchanged':
        try:
            p = subprocess.run(['git', 'diff', '--quiet', args['base'], '--'] + args['pathspecs'], cwd=ROOT, capture_output=True, text=True)
        except FileNotFoundError:
            raise NotRun('git not available')
        if p.returncode not in (0, 1):
            raise NotRun(f'git diff failed: {p.stderr.strip()}')
        return p.returncode == 0, 'git diff --quiet vs base'
    if op == 'static_imports':
        found = []
        for rel in args['files']:
            path = os.path.join(ROOT, rel)
            if not os.path.exists(path):
                raise NotRun(f'surface absent: {rel}')
            with open(path, encoding='utf-8') as fh:
                tree = ast.parse(fh.read(), rel)
            for n in ast.walk(tree):
                names = []
                if isinstance(n, ast.Import):
                    names = [a.name for a in n.names]
                elif isinstance(n, ast.ImportFrom) and n.module:
                    names = [n.module]
                elif isinstance(n, ast.Call) and getattr(n.func, 'id', None) == '__import__' and n.args and isinstance(n.args[0], ast.Constant):
                    names = [n.args[0].value]
                found += [f'{rel}:{x}' for x in names if x.split('.')[0] in args['forbidden']]
        return sorted(found), 'ast import scan'
    raise ValueError(f'unknown op {op}')


def run_probe(case_id, probe, prod, hook):
    res = {'id': probe['id'], 'kind': probe['kind'], 'op': probe['op'], 'blocking': probe['blocking'], 'expected': probe['expect']}
    if probe.get('note'):
        res['note'] = probe['note']
    if probe['op'] == 'declared':
        res.update(status=probe['expect']['status'], reason=probe['expect']['reason'], path='declared (no execution)')
        return res
    args, faulted = apply_fault(case_id, probe['args'], hook)
    if faulted:
        res['fault_hook_applied'] = hook
    try:
        actual, how = op_exec(probe['op'], args, prod)
    except NotRun as e:
        res.update(status='NOT RUN', reason=str(e))
        return res
    except Exception as e:
        res.update(status='FAIL', reason=f'exception: {type(e).__name__}: {e}', traceback_tail=traceback.format_exc().strip().splitlines()[-3:])
        return res
    status, bad = judge(actual, probe['expect'])
    res.update(status=status, path=how, actual=jsonable(actual))
    if bad:
        res['mismatches'] = bad
    return res


def case_status(members):
    blocking = [m['status'] for m in members if m['blocking']]
    for s in ('FAIL', 'NOT RUN', 'UNKNOWN'):
        if s in blocking:
            return s
    return 'PASS'


def git_state():
    try:
        head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=all', '--', 'analysis', 'demo', 'tests', 'docs', 'README.md'],
                               cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
        return head, [d for d in dirty if '__pycache__' not in d]
    except FileNotFoundError:
        return None, None


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--out', required=True)
    ap.add_argument('--label', required=True)
    ap.add_argument('--overwrite', action='store_true')
    ap.add_argument('--fault-hook', choices=FAULT_HOOKS)
    # argparse's default exit 2 would collide with the NOT RUN/UNKNOWN exit code
    ap.error = lambda msg: (print(f'usage error: {msg}', file=sys.stderr), sys.exit(3))
    a = ap.parse_args(argv)
    os.chdir(ROOT)  # production code uses repo-root relative paths
    if os.path.exists(a.out) and not a.overwrite:
        print(f'refusing to overwrite {a.out} (pass --overwrite)', file=sys.stderr)
        return 3
    with open(MANIFEST_SHA, encoding='utf-8') as fh:
        frozen = fh.read().split()[0]
    actual_sha = canonical_sha256(MANIFEST)
    if actual_sha != frozen:
        print(f'manifest hash mismatch: frozen {frozen} actual {actual_sha}', file=sys.stderr)
        return 3
    with open(MANIFEST, encoding='utf-8') as fh:
        manifest = json.load(fh)
    prod = Production()
    cases = []
    for c in manifest['cases']:
        members = [run_probe(c['id'], p, prod, a.fault_hook) for p in c['probes']]
        cases.append({'id': c['id'], 'title': c['title'], 'evidence': c['evidence'], 'policy_state': c['policy_state'],
                      'status': case_status(members), 'members': members})
    count = lambda xs: {s: sum(1 for x in xs if x == s) for s in ('PASS', 'FAIL', 'UNKNOWN', 'NOT RUN')}
    allm = [m for c in cases for m in c['members']]
    summary = {'cases': count([c['status'] for c in cases]), 'cases_total': len(cases),
               'probes_blocking': count([m['status'] for m in allm if m['blocking']]),
               'probes_nonblocking': count([m['status'] for m in allm if not m['blocking']]), 'probes_total': len(allm)}
    sc = summary['cases']
    exit_code = 1 if sc['FAIL'] else (2 if sc['NOT RUN'] or sc['UNKNOWN'] else 0)
    head, dirty = git_state()
    out = {'label': a.label, 'recorded_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
           'manifest': MANIFEST, 'manifest_sha256': actual_sha, 'fault_hook': a.fault_hook,
           'python': platform.python_version(), 'platform': platform.platform(), 'git_head': head, 'git_changed_paths': dirty,
           'production_import': prod.import_error or 'ok', 'tolerance': {'rel': REL_TOL, 'abs': ABS_TOL},
           'summary': summary, 'exit_code': exit_code, 'cases': cases}
    text = json.dumps(out, indent=1, ensure_ascii=False, allow_nan=False).replace(ROOT.replace('\\', '\\\\'), '<repo>')
    with open(a.out, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text + '\n')
    for c in cases:
        ms = ' '.join(f"{m['id'].split('.', 1)[1]}={m['status']}{'' if m['blocking'] else '(nb)'}" for m in c['members'])
        print(f"{c['id']} {c['status']:8} {ms}")
    print(f"cases {sc} | blocking probes {summary['probes_blocking']} | non-blocking {summary['probes_nonblocking']} | exit {exit_code}")
    return exit_code


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        sys.exit(3)
