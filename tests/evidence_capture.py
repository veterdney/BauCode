"""Run one command (or hash files) and save stdout/stderr/exit as an evidence record.

Usage (from repository root):
  python tests/evidence_capture.py run  OUT.json -- python analysis/run.py
  python tests/evidence_capture.py hash OUT.json FILE [FILE ...]

Stdlib only. The record is plain JSON so a reviewer can rerun the same argv and compare.
"""
import hashlib, json, platform, subprocess, sys, time


def sha256(path):
    with open(path, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main(argv):
    if len(argv) < 3 or argv[0] not in ('run', 'hash'):
        print(__doc__, file=sys.stderr)
        return 64
    mode, out = argv[0], argv[1]
    rec = {'recorded_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
           'python': platform.python_version(), 'platform': platform.platform()}
    if mode == 'run':
        if argv[2] != '--':
            print('expected -- before the command', file=sys.stderr)
            return 64
        cmd = argv[3:]
        # sys.executable keeps the recorded run on the same interpreter as the capture tool
        if cmd and cmd[0] == 'python':
            cmd = [sys.executable] + cmd[1:]
        p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        rec.update(argv=argv[3:], exit_code=p.returncode, stdout=p.stdout, stderr=p.stderr)
    else:
        rec['sha256'] = {path: sha256(path) for path in argv[2:]}
    with open(out, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(rec, fh, indent=1, ensure_ascii=False)
        fh.write('\n')
    print(json.dumps({k: rec[k] for k in rec if k in ('exit_code', 'sha256')}))
    return rec.get('exit_code', 0)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
