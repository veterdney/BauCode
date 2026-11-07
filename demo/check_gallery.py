"""Supplementary demonstration checks for the generated gallery (NOT an acceptance suite, NOT part of exact-20).

Run from the repository root:  python demo/check_gallery.py
Exit 0 when every check passes, 1 otherwise. Stdlib only. No browser is used: these are
structural checks on the generated files, not a visual inspection.
"""
import hashlib, html.parser, json, os, re, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'demo'))
import run_demo, run_gallery  # noqa: E402

SAVED = os.path.join(ROOT, 'demo', 'output', 'gallery')
FILES = ('generated_inputs.json', 'gallery.json', 'gallery.csv', 'gallery.html', 'provenance.json')
BASE = 'f3575fb2d00bcce0a5ba9c1cc576d198da0c8c1e'
ORIGINALS = [':(glob)analysis/**/*.md', ':(glob)analysis/**/*.csv', ':(glob)analysis/**/*.json', ':(glob)analysis/**/*.html',
             'README.md', 'RESEARCH-LOOPS.md', 'LICENSE', 'LICENSE-CC-BY-4.0', '.claude', '.github']
FORBIDDEN = r'\b(preferred|prefer|recommended|recommend|recommendation|health|healthy|safe|safer|safest|safety|best|gold|certified|validated|recyclable|recyclability)\b'
results = []


def check(name, ok, detail=''):
    results.append((name, bool(ok), detail))


def sha(path):
    with open(path, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def run(args):
    return subprocess.run([sys.executable] + args, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')


class Doc(html.parser.HTMLParser):
    """collects table rows (data-assembly + data-k cells), svg rects, zero lines, ids and tags"""
    def __init__(self):
        super().__init__()
        self.tags, self.ids, self.rects, self.zeros, self.rows, self.attrs = [], set(), [], {}, {}, set()
        self._row = self._cell = None
        self._svg = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append(tag)
        self.attrs.update(k.lower() for k in a)
        if 'id' in a:
            self.ids.add(a['id'])
        if tag == 'svg':
            self._svg = a.get('aria-labelledby', '').split()[0].rsplit('-t', 1)[0]
        if tag == 'rect':
            self.rects.append(dict(a, chart=self._svg))
        if tag == 'line' and a.get('class') == 'zero':
            self.zeros[self._svg] = float(a['data-x'])
        if tag == 'tr' and 'data-assembly' in a:
            self._row = self.rows.setdefault(a['data-assembly'], {})
        if tag == 'td' and self._row is not None and 'data-k' in a:
            self._cell = a['data-k']
            self._row[self._cell] = ''

    def handle_endtag(self, tag):
        if tag == 'td':
            self._cell = None
        if tag == 'tr':
            self._row = None

    def handle_data(self, data):
        if self._row is not None and self._cell:
            self._row[self._cell] += data


def main():
    tmp = tempfile.mkdtemp(prefix='gallery_check_')
    try:
        # 1. determinism: two fresh runs and the saved output are byte-identical (no runtime metadata in files)
        outs = []
        for i in range(2):
            p = run(['demo/run_gallery.py', '--out', os.path.join(tmp, f'g{i}')])
            check(f'run {i + 1} exit 0', p.returncode == 0, p.stderr.strip()[-200:])
            outs.append({f: sha(os.path.join(tmp, f'g{i}', f)) for f in FILES})
        saved = {f: sha(os.path.join(SAVED, f)) for f in FILES}
        check('repeat runs byte-identical', outs[0] == outs[1], json.dumps(outs[0])[:120])
        check('saved gallery equals fresh run', outs[0] == saved)

        with open(os.path.join(SAVED, 'gallery.json'), encoding='utf-8') as fh:
            g = json.load(fh)
        with open(os.path.join(SAVED, 'generated_inputs.json'), encoding='utf-8') as fh:
            gin = json.load(fh)
        with open(os.path.join(SAVED, 'gallery.html'), encoding='utf-8') as fh:
            page = fh.read()
        A = g['assemblies']

        # 2. shared evaluator: every stored result equals a direct run_demo.evaluate of the stored input
        same = all(run_demo.evaluate(d, input_name=e['input_locator'], input_sha256=run_gallery.canon_sha(d)) == e['result']
                   for d, e in zip(gin['assemblies'], A))
        check('gallery results == direct demo evaluate()', same and len(A) == len(gin['assemblies']))
        s = g['provenance']['summary']
        check('size/seed recorded', s['assemblies'] == 25 and s['product_records'] == 200 and g['provenance']['seed'] == run_gallery.SEED,
              f"{s['assemblies']} assemblies, {s['product_records']} records, seed {g['provenance']['seed']}")
        check('every invalid edge rejected with no numbers',
              all(e['category'] == 'REJECTED' and 'totals' not in e['result'] and 'layers' not in e['result']
                  for e in A if e['edge'] in ('blank_q', 'zero_q', 'nan_q', 'unsupported_unit', 'scenario_conflict', 'b4_module', 'kg_no_density', 'bad_thickness_unit')))

        # 3. HTML structure
        d = Doc()
        d.feed(page)
        # parsed tags/attributes, so escaped label text such as "&lt;img src=x" (inert) is not mistaken for markup
        check('standalone: no script/link/img/iframe tags, no src/href attributes, no url()/http',
              not ({'script', 'link', 'img', 'iframe', 'object', 'embed'} & set(d.tags))
              and not ({'src', 'href', 'xlink:href'} & d.attrs) and not any(k.startswith('on') for k in d.attrs)
              and not re.search(r'url\(|https?:', page))
        check('inline style present', '<style>' in page)
        check('SYNTHETIC badge and GENERATED label', 'synthetic-badge' in d.ids and 'SYNTHETIC &middot; GENERATED' in page)
        check('two charts with title+desc (role=img)', page.count('role="img"') == 2 and {'chart-ac-t', 'chart-ac-d', 'chart-d-t', 'chart-d-d'} <= d.ids)
        check('legend for two-series chart', 'legend-ac' in d.ids and 'A1-A3 total' in page and 'C1-C4 total' in page)
        check('D separate section and column', 'chart-d' in d.ids and 'not subtracted' in page and '<th>D known subtotal (partial; separate, not subtracted)</th>' in page)
        check('provenance section with seed and generator', 'provenance' in d.ids and str(run_gallery.SEED) in page and run_gallery.GENERATOR in page)
        check('layer/module breakdown present', 'breakdown' in d.ids and page.count('<details>') == sum(1 for e in A if e['category'] != 'REJECTED'))

        # zero baseline: positive bars start at zero, negative bars end at zero
        bad = []
        for r in d.rects:
            v, x, w, z = float(r['data-v']), float(r['x']), float(r['width']), d.zeros[r['chart']]
            if (v >= 0 and abs(x - z) > 0.01) or (v < 0 and abs(x + w - z) > 0.01):
                bad.append(r['data-assembly'])
        neg = [r for r in d.rects if float(r['data-v']) < 0]
        check('bars anchored at true zero', not bad, ','.join(bad))
        check('negative values drawn left of zero in both charts', {r['chart'] for r in neg} == {'chart-ac', 'chart-d'})

        # unknown is never 0; rejected rows carry no numbers; other reference areas never drawn
        comp = [e for e in A if e['same_reference_area']]
        unk_ok = all(d.rows[e['id']]['a13'] == 'UNKNOWN' for e in A if e['category'] == 'INCOMPLETE_LAYERS' and e['same_reference_area'])
        eq = run_gallery.E(run_gallery.EQUIV_NOTE)
        tbl = re.findall(r'<table id="tbl-compared">.*?</table>', page, re.S)[0]
        check('equivalence-unverified wording on both charts and the table caption',
              page.count(f'<p class="note equiv">{eq}</p>') == 2 and f'<caption>{eq}</caption>' in tbl
              and page.count('(equivalence unverified)</title>') == 2 and not re.search(r'comparable|functional unit', page, re.I))
        d_ok = all(d.rows[e['id']]['d'] == 'UNKNOWN' or 'known part only' in d.rows[e['id']]['d']
                   for e in A if e['category'] != 'REJECTED' and not e['result']['totals']['d_complete'])
        check('UNKNOWN rendered for unknown totals (not 0)', unk_ok and d_ok and any(e['category'] == 'INCOMPLETE_LAYERS' for e in comp))
        drawn = {r['data-assembly'] for r in d.rects}
        check('no zero-height stand-in bars for unknown', all(not (e['result']['totals']['a13_total'] is None and e['id'] in
                                                                   {r['data-assembly'] for r in d.rects if r['data-series'] == 'a13'})
                                                               for e in comp))
        rej_rows = re.findall(r'<table id="tbl-rejected">.*?</table>', page, re.S)[0]
        check('rejected rows have no numeric cells', 'class="n"' not in rej_rows and rej_rows.count('<tr data-assembly') == 8)
        other = [e['id'] for e in A if not e['same_reference_area'] and e['category'] != 'REJECTED']
        check('different reference area not charted, listed separately', other and not (set(other) & drawn)
              and all(f'data-assembly="{run_gallery.E(o)}"' in re.findall(r'<table id="tbl-other">.*?</table>', page, re.S)[0] for o in other))

        # escaping of untrusted labels
        check('markup in labels escaped', '<script' not in page and '<img' not in page and '&lt;script&gt;' in page and '&lt;img src=x' in page)
        # the "not GOLD" disclaimer itself is removed before scanning; everything else must be clean
        scan = (page + json.dumps(g, ensure_ascii=False)).replace(run_gallery.E(run_gallery.KIND), '').replace(run_gallery.KIND, '')
        found = sorted({m.group(0).lower() for m in re.finditer(FORBIDDEN, scan, re.I)})
        check('no preference/health/safety/recyclability wording', not found, ','.join(found))
        check('no thermal metric rendered', not re.search(r'W/\(?m2', page) and 'U-value) is computed or shown' in page)

        # 4. replacement recipes still work
        p = run(['demo/run_demo.py', '--input', 'demo/input/synthetic_wall_replaced.json', '--out', os.path.join(tmp, 'replaced')])
        check('single-wall replacement recipe: exit 0 and matches hand-derived file', p.returncode == 0 and 'matches synthetic_wall_replaced.expected.json' in p.stdout)
        with open(os.path.join(ROOT, 'demo', 'input', 'synthetic_wall.json'), encoding='utf-8') as fh:
            wall = json.load(fh)
        with open(os.path.join(ROOT, 'demo', 'expected', 'synthetic_wall.expected.json'), encoding='utf-8') as fh:
            hand = json.load(fh)['expect']['totals.a13_total']
        ip = os.path.join(tmp, 'mine.json')
        with open(ip, 'w', encoding='utf-8') as fh:
            json.dump({'assemblies': [wall]}, fh)
        p = run(['demo/run_gallery.py', '--inputs', ip, '--out', os.path.join(tmp, 'mine')])
        with open(os.path.join(tmp, 'mine', 'gallery.json'), encoding='utf-8') as fh:
            mine = json.load(fh)['assemblies']
        # the 1 m2 reference area differs from this 10 m2 wall, so it must be kept out of the 1 m2 table/charts
        check('gallery --inputs replacement: exit 0, hand-derived 185, kept apart (10 m2 reference area)',
              p.returncode == 0 and len(mine) == 1 and abs(mine[0]['result']['totals']['a13_total'] - hand) <= 1e-9 * max(1, abs(hand))
              and mine[0]['same_reference_area'] is False)
        p = run(['demo/run_gallery.py', '--inputs', os.path.join(tmp, 'absent.json'), '--out', os.path.join(tmp, 'x')])
        check('gallery --inputs unreadable file -> exit 2', p.returncode == 2)

        # 5. original human files unchanged vs base
        p = subprocess.run(['git', 'diff', '--quiet', BASE, '--'] + ORIGINALS, cwd=ROOT)
        check('original reports/visuals unchanged vs base', p.returncode == 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for name, ok, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f'  [{detail}]' if detail and not ok else ''))
    n_fail = sum(1 for _, ok, _ in results if not ok)
    print(f'supplementary gallery checks: {len(results) - n_fail} PASS, {n_fail} FAIL (demonstration checks, not acceptance)')
    return 1 if n_fail else 0


if __name__ == '__main__':
    sys.exit(main())
