"""Separate human-main preservation policy v1; never changes frozen exact20 outcomes.

Freeze expectations from pinned Git objects: python tests/check_human_main_v1.py --freeze
Check candidate: python tests/check_human_main_v1.py --out FILE.json
Falsify in isolated temporary fixtures: add --self-test.
Exit 0 PASS, 1 preservation/probe FAIL, 2 policy/tool ERROR. Stdlib; no source execution.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FORK = 'f3575fb2d00bcce0a5ba9c1cc576d198da0c8c1e'
UPSTREAM = '8336cb6ab602d96b26b36390274dcb47cf05ac1c'
POLICY = ROOT / 'tests/human_main_preservation_v1.json'
MARKER = "EXTR=run(EXT,'ext'); INTR=run(INT,'int')"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(*argv):
    return subprocess.check_output(['git', *argv], cwd=ROOT, stderr=subprocess.PIPE)


def upstream_bytes(path):
    return git('show', UPSTREAM + ':' + path)


def wrapper_source(source):
    lines = source.decode('utf-8').splitlines()
    positions = [i for i, line in enumerate(lines) if line == MARKER]
    if len(positions) != 1:
        raise ValueError('pinned upstream pipeline marker is not unique')
    i = positions[0]
    return ('\n'.join(lines[:i] + ['def main():'] + ['    ' + line for line in lines[i:]] +
                      ['', "if __name__=='__main__':", '    main()']) + '\n').encode('utf-8')


def ast_sha(data):
    tree = ast.parse(data.decode('utf-8'))
    return digest(ast.dump(tree, include_attributes=False).encode('utf-8'))


def expected_policy():
    raw = git('diff', '--no-renames', '--name-status', FORK, UPSTREAM).decode('utf-8')
    rows = []
    for line in raw.splitlines():
        status, path = line.split('\t', 1)
        q = PurePosixPath(path)
        if q.is_absolute() or '..' in q.parts or '\\' in path or ':' in path:
            raise ValueError('unsafe protected Git path')
        if status == 'D':
            rows.append({'path': path, 'change': status, 'rule': 'absent'})
        elif status in ('A', 'M'):
            source = upstream_bytes(path)
            mode = git('ls-tree', UPSTREAM, '--', path).decode('utf-8').split()[0]
            if mode != '100644':
                raise ValueError('v1 supports only pinned regular-file modes')
            if path == 'analysis/run.py':
                rows.append({'path': path, 'change': status, 'rule': 'upstream_plus_main_wrapper_ast',
                             'upstream_sha256': digest(source), 'expected_ast_sha256': ast_sha(wrapper_source(source))})
            else:
                rows.append({'path': path, 'change': status, 'rule': 'exact_bytes', 'sha256': digest(source)})
        else:
            raise ValueError('unreviewed Git delta status: ' + status)
    return {'schema': 'baucode-human-main-preservation/1', 'fork': FORK, 'upstream': UPSTREAM,
            'scope': 'Every path added, modified or deleted by pinned human main since fork; no exclusions.',
            'normalization': 'Exact Git blob bytes for regular files; no newline normalization. One explicit AST wrapper exception.',
            'exception': 'analysis/run.py must equal pinned upstream with only its top-level pipeline inside zero-argument main() and an exact __main__ guard; comments/formatting are not AST claims.',
            'outside_scope': 'Pre-existing synthetic overlay on .gitignore, analysis/lib.py and analysis/model.py is not in this human-main delta. Not functional/numeric/scientific validation or a replacement for frozen exact20.',
            'protected': sorted(rows, key=lambda row: row['path'])}


def inspect(root, policy):
    rows = []
    for rule in policy['protected']:
        path = root.joinpath(*PurePosixPath(rule['path']).parts)
        parents = [root.joinpath(*PurePosixPath(rule['path']).parts[:i])
                   for i in range(1, len(PurePosixPath(rule['path']).parts) + 1)]
        item = {'path': rule['path'], 'rule': rule['rule']}
        try:
            if any(p.is_symlink() for p in parents):
                item.update(status='FAIL', reason='symlink forbidden')
            elif rule['rule'] == 'absent':
                item.update(status='FAIL' if path.exists() else 'PASS', reason='must remain absent')
            elif not path.is_file():
                item.update(status='FAIL', reason='required regular file missing or replaced by non-file')
            else:
                raw = path.read_bytes()
                observed = ast_sha(raw) if rule['rule'] == 'upstream_plus_main_wrapper_ast' else digest(raw)
                expected = rule.get('expected_ast_sha256', rule.get('sha256'))
                item.update(status='PASS' if observed == expected else 'FAIL', observed_sha256=observed)
        except (OSError, UnicodeError, SyntaxError) as exc:
            item.update(status='FAIL', reason=type(exc).__name__)
        rows.append(item)
    failed = sum(r['status'] != 'PASS' for r in rows)
    return {'status': 'FAIL' if failed else 'PASS', 'protected_paths': len(rows), 'failed_paths': failed, 'paths': rows}


def falsify(policy):
    """Construct from upstream, then mutate ONLY temporary files; never original human files."""
    probes = []
    with tempfile.TemporaryDirectory(prefix='baucode_policy_v1_') as tmp:
        root = Path(tmp)
        for rule in policy['protected']:
            if rule['rule'] == 'absent':
                continue
            p = root / rule['path']
            p.parent.mkdir(parents=True, exist_ok=True)
            raw = upstream_bytes(rule['path'])
            p.write_bytes(wrapper_source(raw) if rule['rule'] == 'upstream_plus_main_wrapper_ast' else raw)
        probes.append({'id': 'upstream_control', 'expected': 'PASS', 'actual': inspect(root, policy)['status']})
        p = root / 'analysis/README.md'
        original = p.read_bytes()
        p.write_bytes(original + b'\nDELIBERATE PROTECTED CONTENT MUTATION\n')
        probes.append({'id': 'changed_protected_content', 'expected': 'FAIL', 'actual': inspect(root, policy)['status']})
        p.write_bytes(original)
        held = p.with_name('README.held')
        p.rename(held)
        probes.append({'id': 'missing_protected_file', 'expected': 'FAIL', 'actual': inspect(root, policy)['status']})
        held.rename(p)
        deleted = next(r['path'] for r in policy['protected'] if r['rule'] == 'absent')
        p = root / deleted
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b'DELIBERATE RESURRECTION OF HUMAN DELETION\n')
        probes.append({'id': 'resurrected_human_deletion', 'expected': 'FAIL', 'actual': inspect(root, policy)['status']})
        p.unlink()  # temporary fixture only
        p = root / 'analysis/run.py'
        p.write_bytes(p.read_bytes() + b'\nprint("DELIBERATE EXTRA EXECUTABLE STATEMENT")\n')
        probes.append({'id': 'extra_statement_outside_wrapper', 'expected': 'FAIL', 'actual': inspect(root, policy)['status']})
    return {'status': 'PASS' if all(p['actual'] == p['expected'] for p in probes) else 'FAIL', 'probes': probes,
            'scope': 'Independent policy falsification controls, not additional exact20 cases or accuracy evidence.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--freeze', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--out')
    a = ap.parse_args()
    expected = expected_policy()  # expectations always derived from pinned Git, never candidate bytes
    if a.freeze:
        if a.self_test or a.out:
            raise ValueError('freeze is separate from checks')
        with POLICY.open('x', encoding='utf-8', newline='\n') as fh:
            fh.write(json.dumps(expected, indent=1) + '\n')
        print('FROZEN', POLICY.name, digest(POLICY.read_bytes()), 'paths', len(expected['protected']))
        return 0
    raw = POLICY.read_bytes()
    if json.loads(raw) != expected:
        raise ValueError('policy differs from pinned Git-derived v1 expectations')
    payload = {'schema': expected['schema'], 'head': git('rev-parse', 'HEAD').decode().strip(), 'upstream': UPSTREAM,
               'policy_sha256': digest(raw), 'checker_sha256': digest(Path(__file__).read_bytes()),
               'mode': 'temporary_falsification' if a.self_test else 'candidate_preservation',
               'result': falsify(expected) if a.self_test else inspect(ROOT, expected)}
    if a.out:
        with Path(a.out).open('x', encoding='utf-8', newline='\n') as fh:
            fh.write(json.dumps(payload, indent=1) + '\n')
    print(json.dumps(payload, indent=1))
    return 0 if payload['result']['status'] == 'PASS' else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({'status': 'ERROR', 'error_type': type(exc).__name__, 'detail': 'Policy/tool failure; no preservation PASS claimed.'}))
        sys.exit(2)
