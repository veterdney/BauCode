"""Run the offline checks and record what actually ran, for reviewers who will not execute code.

  python -I analysis/eval/tests/run_offline_evidence.py

Runs, with this interpreter and no network:
  1. python -I analysis/eval/grade.py --selftest
  2. python -I -m unittest discover -s analysis/eval/tests -v
  3. python -I analysis/eval/tests/test_eval_contract.py --json analysis/eval/evidence/unit_tests.json
  4. python -I analysis/eval/tests/baseline_probe_aee18b.py   (original PR9 sources, frozen via git show)
and writes analysis/eval/evidence/offline_tests.json (machine-readable), unit_tests.json and OFFLINE_TESTS.md.
The tested sources are identified by sha256 at run time (the evidence cannot contain the hash of
the commit that adds it); compare them with the committed files.
"""
import datetime, hashlib, json, platform, re, subprocess, sys
from pathlib import Path

EVAL = Path(__file__).resolve().parents[1]
REPO = EVAL.parents[1]
OUT = EVAL / "evidence"
SOURCES = ["analysis/eval/contract.py", "analysis/eval/grade.py", "analysis/eval/judge.py", "analysis/eval/run_eval.py",
           "analysis/eval/obd_data.py", "analysis/eval/obd_tools.py", "analysis/eval/golden_v1.jsonl",
           "analysis/eval/tests/test_eval_contract.py", "analysis/eval/tests/baseline_probe_aee18b.py",
           "analysis/eval/tests/run_offline_evidence.py",
           "analysis/results_wall_systems.csv", "analysis/results_layers.csv",
           "analysis/levels/report/scores_alternatives.csv", "analysis/levels/report/sensitivity.json"]
COMMANDS = [("grader_selftest", ["analysis/eval/grade.py", "--selftest"]),
            ("unit_tests", ["-m", "unittest", "discover", "-s", "analysis/eval/tests", "-v"]),
            ("unit_tests_per_test_json", ["analysis/eval/tests/test_eval_contract.py", "--json", "analysis/eval/evidence/unit_tests.json"]),
            ("baseline_probes_original_aee18b", ["analysis/eval/tests/baseline_probe_aee18b.py"])]


def sha(p):
    return hashlib.sha256((REPO / p).read_bytes()).hexdigest()


def scrub(text):
    """Replace local temp/repo paths in captured output (they identify the machine, not the result)."""
    import os, tempfile
    for path, label in ((tempfile.gettempdir(), "<TMP>"), (os.path.realpath(tempfile.gettempdir()), "<TMP>"), (str(REPO), "<REPO>")):
        text = text.replace(path, label)
    return re.sub(r"[A-Za-z]:\\Users\\[^\\\s]+\\AppData\\Local\\Temp", "<TMP>", text)


def git(*args):
    r = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else "unavailable"


def main():
    started = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    runs = []
    for name, args in COMMANDS:
        r = subprocess.run([sys.executable, "-I", *args], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
        runs.append({"name": name, "command": "python -I " + " ".join(args), "exit_code": r.returncode,
                     "stdout": scrub(r.stdout), "stderr": scrub(r.stderr)})
    unit = runs[1]
    summary = re.search(r"Ran (\d+) tests? in", unit["stderr"])
    tests = json.loads((OUT / "unit_tests.json").read_text(encoding="utf-8"))
    probes = json.loads(runs[3]["stdout"]) if runs[3]["exit_code"] in (0, 1) else None
    doc = {
        "kind": "offline test evidence (no model calls, no network, no Oekobaudat export)",
        "started": started,
        "git_head_at_run": git("rev-parse", "HEAD"),
        "git_branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "uncommitted_changes_to_tested_sources_at_run": bool(git("status", "--porcelain", "--", *SOURCES)),
        "runtime": {"python": platform.python_version(), "implementation": platform.python_implementation(),
                    "platform": platform.platform()},
        "tested_sources_sha256": {p: sha(p) for p in SOURCES},
        "commands": [{k: v for k, v in r.items() if k not in ("stdout", "stderr")} for r in runs],
        "unit_tests": {"ran_by_discover": int(summary.group(1)) if summary else None, "per_test_file": "unit_tests.json",
                       "recorded": len(tests), "passed": sum(t["outcome"] == "ok" for t in tests),
                       "results": [{k: t[k] for k in ("test", "outcome", "purpose")} for t in tests]},
        "baseline_probes": probes,
        "limits": [
            "Offline self-checks of grading/judging/runner logic with fixtures and fake clients only.",
            "No real model was run; nothing here measures model accuracy, judge calibration or expert agreement.",
            "Expected answers in golden_v1 are source-derived proposals, not expert-reviewed GOLD or scientific truth.",
            "load_obd/ObdTools (pandas) and the 51.5 MB export were not exercised; the full eval is not self-contained.",
            "Package versions for a live run are not pinned (requirements.txt lists anthropic, pandas unversioned); run manifests record the versions actually installed.",
            "Model names, the fallback beta and API availability are unverified.",
        ],
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "offline_tests.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    lines = [f"# Offline test evidence", "", f"Run {started} on {doc['runtime']['platform']}, Python {doc['runtime']['python']}, "
             f"git HEAD at run `{doc['git_head_at_run']}` (branch `{doc['git_branch']}`; uncommitted changes to tested sources at run: "
             f"{doc['uncommitted_changes_to_tested_sources_at_run']}).", "",
             "Machine-readable: [offline_tests.json](offline_tests.json). Regenerate: `python -I analysis/eval/tests/run_offline_evidence.py`.", "",
             "| Check | Command | Exit |", "|---|---|---|"]
    lines += [f"| {r['name']} | `{r['command']}` | {r['exit_code']} |" for r in runs]
    u = doc["unit_tests"]
    lines += ["", f"Unit tests: {u['passed']} ok of {u['recorded']} recorded ({u['ran_by_discover']} run by discover).", ""]
    lines += ["| Test | Outcome | Failure it guards against |", "|---|---|---|"]
    lines += [f"| {t['test']} | {t['outcome']} | {' '.join(t['purpose'].split()).replace('|', '/')} |" for t in tests]
    if probes:
        lines += ["", f"Original PR9 behaviour reproduced on frozen `{probes['base_commit'][:8]}` sources: "
                  f"{probes['reproduced']}/{probes['total']} probes (these confirm the old defects; they are not passes of the new code).", "",
                  "| Probe | Defect | Observed on original |", "|---|---|---|"]
        lines += [f"| {p['id']} | {p['purpose']} | {str(p['observed']).replace('|', '/')} |" for p in probes["probes"]]
    lines += ["", "## Tested source sha256", ""] + [f"- `{p}` `{h}`" for p, h in doc["tested_sources_sha256"].items()]
    lines += ["", "## Limits", ""] + [f"- {x}" for x in doc["limits"]]
    lines += ["", "## Full output", ""]
    for r in runs:
        lines += [f"### {r['name']} (exit {r['exit_code']})", "", "```text", (r["stdout"] + r["stderr"]).rstrip()[-6000:], "```", ""]
    (OUT / "OFFLINE_TESTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    bad = [r["name"] for r in runs if r["exit_code"] != 0]
    print(f"wrote {OUT / 'offline_tests.json'} and OFFLINE_TESTS.md; non-zero exits: {bad or 'none'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())