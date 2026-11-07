"""Reproduce the reviewed defects on the FROZEN original PR9 sources (main aee18b1), offline.

The original grade.py, judge.py, run_eval.py, obd_data.py and golden_v1.jsonl are read with
`git show aee18b1...:<path>` into a temporary directory and exercised there with small fixtures and
a fake judge client. Nothing in the repository is modified. run_eval.py/obd_data.py need pandas and
the absent export, so their two defects are shown by source inspection only (marked STATIC).

  python -I analysis/eval/tests/baseline_probe_aee18b.py [--out probes.json]

Exit 0 when every probe reproduced the expected ORIGINAL behaviour, 1 otherwise, 2 if git is unavailable.
"""
import contextlib, importlib.util, io, json, subprocess, sys, tempfile, types
from pathlib import Path

BASE = "aee18b149c47e7b6851f946dc2383b997675cbcf"
REPO = Path(__file__).resolve().parents[3]
FILES = ["grade.py", "judge.py", "run_eval.py", "obd_data.py", "golden_v1.jsonl"]


def show(name):
    return subprocess.run(["git", "-C", str(REPO), "show", f"{BASE}:analysis/eval/{name}"], capture_output=True, check=True).stdout


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    out_path = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    try:
        blobs = {n: show(n) for n in FILES}
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"git unavailable or base missing: {exc}", file=sys.stderr)
        return 2
    import hashlib
    probes = []

    def probe(pid, purpose, expected, fn):
        try:
            observed, ok = fn()
        except Exception as exc:  # an exception can itself be the reproduced defect
            observed, ok = f"{type(exc).__name__}: {exc}", False
        probes.append({"id": pid, "purpose": purpose, "expected_original_behaviour": expected,
                       "observed": observed, "reproduced": bool(ok)})

    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        for n, b in blobs.items():
            (d / n).write_bytes(b)
        sys.path.insert(0, str(d))
        g = load(d / "grade.py", "orig_grade")
        j = load(d / "judge.py", "orig_judge")
        gold = g.GOLD

        def run(rows, judged=None):
            cand = d / "cand.jsonl"
            cand.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
            jr = d / "judge_results.jsonl"
            if judged is None:
                jr.unlink(missing_ok=True)
            else:
                jr.write_text("".join(json.dumps(r) + "\n" for r in judged), encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                per = g.grade(str(cand), write_queue=False, quiet=False)
            return per, buf.getvalue()

        L01 = {"value": gold["L01"]["expected"]["value"], "in_data": True}
        L03 = {"value": gold["L03"]["expected"]["value"], "in_data": True}

        def p1():
            per, txt = run([{"id": "L01", "run": 1, "structured": L01}])
            line = next(l for l in txt.splitlines() if l.startswith("lookup"))
            return line.strip(), "100%" in line and len(per["L01"]) == 1
        probe("B01", "missing required runs dropped from denominator", "1 of 3 required L01 runs reports pass@1 and pass^k 100%", p1)

        def p2():
            per, _ = run([{"id": "L01", "run": 1, "structured": L01}] * 3)
            return f"{len(per['L01'])} entries counted for (L01, run 1)", len(per["L01"]) == 3
        probe("B02", "duplicate (id, run) records counted", "three copies of run 1 count as three runs", p2)

        def p3():
            per, _ = run([{"id": "ZZZ", "run": 1, "structured": {}}, {"id": "L01", "run": 99, "structured": L01}])
            return f"cases graded: {sorted(per)}; ZZZ silently skipped; run 99 accepted", "ZZZ" not in per and len(per["L01"]) == 1
        probe("B03", "unknown case skipped / out-of-range run accepted", "no error for unknown id or run 99", p3)

        def p4():
            per, txt = run([{"id": "L03", "run": 1, "structured": L03}])
            return f"L03 ok={per['L03'][0]['ok']} with no judge result", per["L03"][0]["ok"] is True
        probe("B04", "code+rubric credited before the judge ran", "code part pass alone yields ok=True (counted as pass)", p4)

        def p5():
            per, txt = run([{"id": "D01", "run": 1, "answer": "x", "structured": {}}],
                           judged=[{"id": "D01", "run": 1, "error": "judge refusal"}])
            line = next(l for l in txt.splitlines() if "need the judge" in l)
            return f"{line.strip()} | D01 ok={per['D01'][0]['ok']}", "(0 not judged yet)" in line and per["D01"][0]["ok"] is None
        probe("B05", "judge error suppresses pending count; rubric-only None excluded", "error record counts as judged; D01 dropped from scoring", p5)

        def p6():
            per, _ = run([{"id": "D01", "run": 1, "answer": "a completely different answer", "structured": {}}],
                         judged=[{"id": "D01", "run": 1, "judge_pass": True, "point_share": 1.0, "gates_ok": True}])
            return f"stale judge result applied: ok={per['D01'][0]['ok']}", per["D01"][0]["ok"] is True
        probe("B06", "judge cache keyed only by (id, run)", "a judge pass for any other answer/model is applied", p6)

        def p7():
            per, _ = run([{"id": "D01", "run": 1, "answer": "x", "structured": {}}],
                         judged=[{"id": "D01", "run": 1, "judge_pass": False, "point_share": 0, "gates_ok": False},
                                 {"id": "D01", "run": 1, "judge_pass": True, "point_share": 1, "gates_ok": True}])
            return f"duplicate cache records: last wins, ok={per['D01'][0]['ok']}", per["D01"][0]["ok"] is True
        probe("B07", "duplicate judge results overwrite silently", "FAIL then PASS for the same key -> PASS", p7)

        item = {"id": "D01", "run": 1, "prompt": "p", "expected": {"type": "rubric", "points": ["a", "b"]},
                "gates": ["G-FAB"], "must_include": [], "must_not": [], "answer": "x"}

        def fake(verdict):
            text = json.dumps(verdict)
            resp = types.SimpleNamespace(stop_reason="end_turn", content=[types.SimpleNamespace(type="text", text=text)])
            return types.SimpleNamespace(beta=types.SimpleNamespace(messages=types.SimpleNamespace(create=lambda **kw: resp)))

        def p8():
            r = j.judge_one(fake({"gates": [], "points": [{"point": "a", "score": 2, "evidence": ""}] * 2}), "m", item)
            return f"empty gates list -> gates_ok={r['gates_ok']}, judge_pass={r['judge_pass']}", r["judge_pass"] is True
        probe("B08", "empty/missing gate verdicts pass vacuously", "all([]) is True: G-FAB never checked", p8)

        def p9():
            r = j.judge_one(fake({"gates": [{"gate": "G-FAB", "verdict": "PASS", "evidence": ""}],
                                  "points": [{"point": "a", "score": 2, "evidence": ""}] * 2}), "m", item)
            return f"point 'a' twice, 'b' missing -> share={r['point_share']}, pass={r['judge_pass']}", r["judge_pass"] is True
        probe("B09", "duplicate point masks a missing point", "duplicating one point fills the share", p9)

        def p10():
            r = j.judge_one(fake({"gates": [{"gate": "G-FAB", "verdict": "PASS", "evidence": ""}],
                                  "points": [{"point": "a", "score": 5, "evidence": ""}]}), "m", item)
            return f"score 5 accepted -> share={r['point_share']}, pass={r['judge_pass']}", r["judge_pass"] is True and r["point_share"] > 1
        probe("B10", "out-of-range score not checked locally", "score 5 yields share > 1 and a pass", p10)

        def p11():
            return f"close(True, 1.0)={g.close(True, 1.0, 0.01)}", g.close(True, 1.0, 0.01) is True
        probe("B11", "bool accepted as a number", "True matches 1.0", p11)

        def p12():
            try:
                g.kendall(["a"], ["a"])
            except ZeroDivisionError:
                return "ZeroDivisionError on one-item ranking", True
            return "no error", False
        probe("B12", "single-item ranking crashes", "ZeroDivisionError", p12)

        def p13():
            ok = g.check(gold["M09"], {"value": ["Cross laminated timber"], "in_data": True})[0]
            return f"M09 (min_match 2) with one generic name -> {ok}", ok is True
        probe("B13", "one reported name satisfies several gold names", "single name passes a two-match case", p13)

        def p15():
            return f"stale_cases() without pandas -> {g.stale_cases()}", g.stale_cases() == []
        probe("B15", "reference check silently skipped when obd_data/pandas cannot import", "returns [] (no warning)", p15)

        src_run = blobs["run_eval.py"].decode("utf-8")
        src_obd = blobs["obd_data.py"].decode("utf-8")
        probe("S01", "STATIC: --k 0 falls back to full runs_k; --k -1 yields zero jobs", "source uses (a.k or c['runs_k'])",
              lambda: ("found" if '(a.k or c["runs_k"])' in src_run else "absent", '(a.k or c["runs_k"])' in src_run))
        probe("S02", "STATIC: reruns append to an existing candidate file", "source opens out with mode 'a'",
              lambda: ("found" if 'open(out, "a"' in src_run else "absent", 'open(out, "a"' in src_run))
        probe("S03", "STATIC: several exports -> the last one is used silently", "source returns hits[-1]",
              lambda: ("found" if "hits[-1]" in src_obd else "absent", "hits[-1]" in src_obd))
        gx = [json.loads(l) for l in blobs["golden_v1.jsonl"].decode("utf-8").splitlines() if l.strip()]
        x04 = next(c for c in gx if c["id"] == "X04")["gates"]
        probe("S04", "DATA: X04 lists G-FAB twice and the original accepts it", "duplicate gate in gold", lambda: (str(x04), x04 == ["G-FAB", "G-FAB"]))
        sys.path.remove(str(d))

    rep = {"base_commit": BASE, "frozen_sources_sha256": {n: hashlib.sha256(b).hexdigest() for n, b in blobs.items()},
           "probes": probes, "reproduced": sum(p["reproduced"] for p in probes), "total": len(probes),
           "note": "Shows the ORIGINAL behaviour only; S01-S03 are source inspection, not execution."}
    text = json.dumps(rep, ensure_ascii=False, indent=1)
    if out_path:
        Path(out_path).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if rep["reproduced"] == rep["total"] else 1


if __name__ == "__main__":
    sys.exit(main())