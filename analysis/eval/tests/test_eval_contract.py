"""Offline adversarial and regression tests for the eval contract (grade.py, judge.py, run_eval.py,
contract.py, obd_data.py). Standard library only. Every model call is a local fake; no network,
no API key, no Oekobaudat export needed. Each test's docstring states what failure it guards against.

  python -I -m unittest discover -s analysis/eval/tests -v
"""
import copy, json, os, sys, tempfile, types, unittest
from pathlib import Path

EVAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVAL))
import contract as C  # noqa: E402
import grade as G  # noqa: E402
import judge as J  # noqa: E402
import obd_data  # noqa: E402

REF = G.current_reference()


def sel(ids, k=None):
    return C.plan_selection(G.GOLD, ids, k)


def good_struct(cid):
    e = G.GOLD.get(cid, {"expected": {"type": "rubric"}})["expected"]
    return {"in_data": False} if e["type"] == "refusal" else {"value": e.get("value"), "in_data": True}


def rec(cid, run, **kw):
    r = {"id": cid, "run": run, "answer": "ans", "structured": good_struct(cid)}
    r.update(kw)
    return r


def rows(*recs):
    return [(i + 1, r) for i, r in enumerate(recs)]


SRC = {"filename": "fixture.csv", "size_bytes": 10, "rows": 1, "sha256": "a" * 64}
CFG = {"requested_model": "m", "effort": "high", "max_turns": 20}


def fixture_source(d):
    """A small offline fixture pinned by its real sha256 (stands in for the absent export; not the export)."""
    p = Path(d) / "fixture_export.csv"
    p.write_bytes(b"UUID;Modul\nx;A1-A3\n")
    return obd_data.file_provenance(p, rows=1)


def states(rep):
    return [c["state"] for c in rep["cells"]]


def verdict_for(item, score=2, gate="PASS"):
    return {"gates": [{"gate": g, "verdict": gate, "evidence": "e"} for g in item["gates"]],
            "points": [{"point": p, "score": score, "evidence": "e"} for p in J.point_ids(item)]}


def judged_for(item, verdict, served=None, model="judge-m"):
    return {"id": item["id"], "run": item["run"], "binding": item["binding"],
            "judge": dict(J.judge_config(model), served_model=served or model), "verdict": verdict}


def queue_of(records, s):
    with tempfile.TemporaryDirectory() as d:
        q = Path(d) / "q.jsonl"
        G.grade_records(rows(*records), s, ref=REF, write_queue_to=q)
        return [o for _, o in C.read_jsonl(q, "queue")]


class StrictJson(unittest.TestCase):
    def test_nonfinite_and_duplicate_keys_rejected(self):
        """NaN/Infinity/1e999 and duplicate keys must not parse (they could smuggle non-finite scores or shadow fields)."""
        for t in ['{"a": NaN}', '{"a": Infinity}', '{"a": -Infinity}', '{"a": 1e999}', '{"a": 1, "a": 2}']:
            with self.assertRaises(C.ContractError, msg=t):
                C.loads_strict(t)
        self.assertEqual(C.loads_strict('{"a": 1.5}'), {"a": 1.5})

    def test_malformed_candidate_line_is_fatal(self):
        """A malformed JSONL line is an integrity error with its line number, not a skipped row."""
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "c.jsonl"
            p.write_text('{"id": "L01", "run": 1}\n{oops\n', encoding="utf-8")
            with self.assertRaisesRegex(C.ContractError, "line 2"):
                C.read_jsonl(p, "candidate")

    def test_atomic_write_leaves_no_temp(self):
        """Outputs are written via temp file + os.replace; no torn or leftover files."""
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "out.jsonl"
            C.write_atomic(p, "x\n")
            C.write_atomic(p, "y\n")
            self.assertEqual(p.read_text(encoding="utf-8"), "y\n")
            self.assertEqual(os.listdir(d), ["out.jsonl"])


class Selection(unittest.TestCase):
    def test_invalid_k_rejected(self):
        """k=0 used to fall back to the full runs_k (cost hazard) and k<0 gave zero jobs; both must be refused."""
        import argparse
        for bad in ["0", "-1", "1.0", "true", "", " "]:
            with self.assertRaises(argparse.ArgumentTypeError, msg=bad):
                C.parse_positive_int_arg(bad)
        self.assertEqual(C.parse_positive_int_arg("3"), 3)
        for bad in [0, -1, True, False, 1.0, None, "2"]:
            if bad is None:
                continue
            with self.assertRaises(C.ContractError, msg=repr(bad)):
                C.plan_selection(G.GOLD, ["L01"], bad)

    def test_invalid_ids_rejected(self):
        """Empty, blank, duplicate or unknown ids must fail before any run, not be dropped."""
        for bad in ["", "L01,,T01", "L01,L01", " , "]:
            with self.assertRaises(C.ContractError, msg=bad):
                C.parse_ids_arg(bad)
        with self.assertRaises(C.ContractError):
            C.plan_selection(G.GOLD, ["L01", "NOPE"])
        with self.assertRaises(C.ContractError):
            C.plan_selection(G.GOLD, [])
        s = C.plan_selection(G.GOLD, C.parse_ids_arg("L01,T01"), 2)
        self.assertEqual(C.required_cells(s), [("L01", 1), ("L01", 2), ("T01", 1), ("T01", 2)])

    def test_gold_contract(self):
        """Duplicate gold ids and boolean runs_k are refused; the X04 duplicate gate is reported and applied once."""
        base = json.loads(C.GOLD_PATH.read_text(encoding="utf-8").splitlines()[0])
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "g.jsonl"
            p.write_text(json.dumps(base) + "\n" + json.dumps(base) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(C.ContractError, "duplicate id"):
                C.load_gold(p)
            p.write_text(json.dumps(dict(base, runs_k=True)) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(C.ContractError, "runs_k"):
                C.load_gold(p)
            p.write_text(json.dumps(dict(base, gates=["G-NOPE"])) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(C.ContractError, "unknown gates"):
                C.load_gold(p)
        C.load_gold(C.GOLD_PATH)
        self.assertEqual(G.GOLD["X04"]["gates"], ["G-FAB"])
        self.assertTrue(any("X04" in w for w in C.GOLD_WARNINGS))
        self.assertEqual(set(J.GATES), set(C.KNOWN_GATES))


class Matrix(unittest.TestCase):
    def test_complete_valid_runs_retained(self):
        """Valid complete code-graded runs still PASS and the report is integrity-clean."""
        rep = G.grade_records(rows(*[rec("L01", r) for r in (1, 2, 3)]), sel(["L01"]), ref=REF)
        self.assertEqual(states(rep), ["PASS"] * 3)
        self.assertTrue(rep["integrity_ok"], rep["integrity_problems"])

    def test_missing_run_stays_in_denominator(self):
        """Old grader counted only supplied rows (1 of 3 runs -> 100%). Missing runs must be visible and non-passing."""
        rep = G.grade_records(rows(rec("L01", 1)), sel(["L01"]), ref=REF)
        self.assertEqual(states(rep), ["PASS", "MISSING", "MISSING"])
        self.assertFalse(rep["integrity_ok"])
        f = rep["by_family_tier"]["lookup/regression"]
        self.assertEqual((f["pass"], f["required"], f["cases_all_pass"]), (1, 3, 0))

    def test_duplicate_run_rejected(self):
        """Duplicate (id, run) records could inflate pass@1; the cell becomes DUPLICATE."""
        rep = G.grade_records(rows(rec("L01", 1), rec("L01", 1), rec("L01", 2), rec("L01", 3)), sel(["L01"]), ref=REF)
        self.assertEqual(states(rep), ["DUPLICATE", "PASS", "PASS"])
        self.assertFalse(rep["integrity_ok"])

    def test_unknown_and_out_of_range_reported(self):
        """Unknown ids, run 0/-1/k+1, bool/null/string runs are reported, not silently skipped."""
        bad = [rec("ZZZ", 1), rec("L01", 0), rec("L01", -1), rec("L01", 4), rec("L01", True), rec("L01", None), rec("L01", "1")]
        good = [rec("L01", r) for r in (1, 2, 3)]
        rep = G.grade_records(rows(*(good + bad)), sel(["L01"]), ref=REF)
        self.assertEqual(states(rep), ["PASS"] * 3)
        self.assertEqual(len(rep["outside_matrix"]), len(bad))
        self.assertFalse(rep["integrity_ok"])

    def test_empty_candidate(self):
        """An empty candidate file is all MISSING, never an empty 'all pass'."""
        rep = G.grade_records([], sel(["L01", "T01"]), ref=REF)
        self.assertTrue(all(s == "MISSING" for s in states(rep)))
        self.assertFalse(rep["integrity_ok"])

    def test_error_refusal_invalid_states(self):
        """API errors are integrity gaps; refusals are scored failures; malformed records are INVALID."""
        s = sel(["L01"], 3)
        rep = G.grade_records(rows({"id": "L01", "run": 1, "error": "API 500: x", "error_kind": "api"},
                                   {"id": "L01", "run": 2, "error": "refusal (cyber)"},
                                   {"id": "L01", "run": 3, "structured": "1.43"}), s, ref=REF)
        self.assertEqual(states(rep), ["ERROR", "REFUSAL", "INVALID"])
        rep = G.grade_records(rows(rec("L01", 1, structured={"value": 1.43, "in_data": "yes"})), sel(["L01"], 1), ref=REF)
        self.assertEqual(states(rep), ["INVALID"])

    def test_served_model_differs_not_credited(self):
        """With server-side fallback the served model can differ; such runs must not earn credit."""
        r = rec("L01", 1, requested_model="m", served_models=["m", "other"])
        rep = G.grade_records(rows(r), sel(["L01"], 1), ref=REF)
        self.assertEqual(states(rep), ["SERVED_MODEL_DIFFERS"])

    def test_manifest_model_binding(self):
        """Under a manifest every record must carry the manifest's requested model and its served models."""
        m = {"candidate": dict(CFG), "source": SRC}
        s = sel(["L01"], 3)
        ok = {"effort": "high", "max_turns": 20}
        rep = G.grade_records(rows(rec("L01", 1, requested_model="x", served_models=["x"], **ok),
                                   rec("L01", 2, requested_model="m", **ok),
                                   rec("L01", 3, requested_model="m", served_models=["m"], **ok)), s, manifest=m, ref=REF)
        self.assertEqual(states(rep), ["INVALID", "INVALID", "PASS"])

    def test_manifest_candidate_config_exact(self):
        """effort and max_turns must equal the manifest's candidate config exactly (type-strict), errors included."""
        m = {"candidate": dict(CFG), "source": SRC}
        base = dict(requested_model="m", served_models=["m"])
        bad = [dict(effort="low", max_turns=20), dict(effort="high", max_turns=21), dict(effort="high", max_turns=True),
               dict(effort="high", max_turns=20.0), dict(max_turns=20), dict(effort="high")]
        for kw in bad:
            rep = G.grade_records(rows(rec("L01", 1, **base, **kw)), sel(["L01"], 1), manifest=m, ref=REF)
            self.assertEqual(states(rep), ["INVALID"], kw)
        err = {"id": "L01", "run": 1, "error": "API 500", "error_kind": "api", "requested_model": "m", "effort": "max", "max_turns": 20}
        self.assertEqual(states(G.grade_records(rows(err), sel(["L01"], 1), manifest=m, ref=REF)), ["INVALID"])
        good = rec("L01", 1, **base, effort="high", max_turns=20)
        self.assertEqual(states(G.grade_records(rows(good), sel(["L01"], 1), manifest=m, ref=REF)), ["PASS"])

    def test_in_data_strict_bool(self):
        """0/1 (and other values equal to False/True) are not accepted as in_data booleans."""
        for v in (0, 1, 0.0, "false", [], {}):
            rep = G.grade_records(rows(rec("L01", 1, structured={"value": 1.43, "in_data": v})), sel(["L01"], 1), ref=REF)
            self.assertEqual(states(rep), ["INVALID"], repr(v))
        for v in (True, None):
            rep = G.grade_records(rows(rec("L01", 1, structured={"value": 1.43, "in_data": v})), sel(["L01"], 1), ref=REF)
            self.assertEqual(states(rep), ["PASS"], repr(v))

    def test_manifest_source_required_and_bound(self):
        """The manifest must carry a valid source identity; a source-only change (same answers, same reference
        files) makes earlier judge results stale."""
        good = dict(SRC)
        for bad in [None, {}, dict(good, sha256="A" * 64), dict(good, sha256="a" * 63), dict(good, rows=True),
                    dict(good, rows=0), dict(good, size_bytes=0), dict(good, filename="")]:
            with self.assertRaises(C.ContractError, msg=repr(bad)):
                C.validate_source(bad)
        C.validate_source(good)
        with tempfile.TemporaryDirectory() as d:
            mp = Path(d) / "m.json"
            man = {"contract": C.CONTRACT_VERSION, "selection": sel(["D01"], 1), "candidate": dict(CFG),
                   "gold_sha256": C.sha256_file(C.GOLD_PATH), "reference_fingerprint": REF[0]}
            mp.write_text(json.dumps(man), encoding="utf-8")
            with self.assertRaises(C.ContractError):
                G.load_manifest(mp, man["gold_sha256"], REF[0])
            mp.write_text(json.dumps(dict(man, source=good)), encoding="utf-8")
            G.load_manifest(mp, man["gold_sha256"], REF[0])
        s = sel(["D01"], 1)
        r = rec("D01", 1, requested_model="m", served_models=["m"], effort="high", max_turns=20)
        mA = {"candidate": dict(CFG), "source": good}
        mB = {"candidate": dict(CFG), "source": dict(good, sha256="b" * 64)}
        with tempfile.TemporaryDirectory() as d:
            q = Path(d) / "q.jsonl"
            G.grade_records(rows(r), s, manifest=mA, ref=REF, write_queue_to=q)
            it = [o for _, o in C.read_jsonl(q, "queue")][0]
        self.assertEqual(it["binding"]["source_sha256"], "a" * 64)
        j = judged_for(it, verdict_for(it))
        self.assertEqual(states(G.grade_records(rows(r), s, rows(j), manifest=mA, ref=REF)), ["PASS"])
        self.assertEqual(states(G.grade_records(rows(r), s, rows(j), manifest=mB, ref=REF)), ["PENDING_JUDGE"])

    def test_reference_checks_fail_visibly(self):
        """A stale or unavailable reference fingerprint is an integrity problem, not a warning to ignore."""
        cid = next(c for c, v in G.GOLD.items() if v.get("reference_fingerprint") and v["grader"]["method"] == "code")
        r = [rec(cid, k) for k in range(1, G.GOLD[cid]["runs_k"] + 1)]
        self.assertTrue(G.grade_records(rows(*r), sel([cid]), ref=REF)["integrity_ok"])
        self.assertFalse(G.grade_records(rows(*r), sel([cid]), ref=("000000000000", None))["integrity_ok"])
        self.assertFalse(G.grade_records(rows(*r), sel([cid]), ref=(None, "unavailable"))["integrity_ok"])


class CodeChecks(unittest.TestCase):
    def test_bool_and_nonfinite_values_fail(self):
        """bool is not a number and NaN/inf never match."""
        self.assertFalse(G.close(True, 1.0, 0.01))
        self.assertFalse(G.close(float("nan"), 1.0, 0.01))
        self.assertFalse(G.close("inf", 1.0, 0.01))
        self.assertTrue(G.close(1.43, 1.43, 0.01))
        self.assertEqual(G.check(G.GOLD["L07"], {"value": 713.0})[0], False)
        self.assertEqual(G.check(G.GOLD["L07"], {"value": 713})[0], True)

    def test_single_item_rank_no_crash(self):
        """kendall() divided by zero for one-item rankings."""
        self.assertEqual(G.kendall(["a"], ["a"]), 1.0)

    def test_loose_keys_kept_but_collisions_rejected(self):
        """L03 loose scenario keys stay valid; one candidate key cannot satisfy two gold keys."""
        l03 = G.GOLD["L03"]["expected"]["value"]
        loose = {"value": {"Szenario 1: Energier\u00fcckgewinnung": list(l03.values())[0], "recycling": list(l03.values())[1]}}
        self.assertTrue(G.check(G.GOLD["L03"], loose)[0])
        l08 = G.GOLD["L08"]["expected"]["value"]
        self.assertTrue(G.check(G.GOLD["L08"], {"value": dict(l08)})[0])
        collide = {"value": {"fossil and biogenic and luluc": 1.0}}
        self.assertFalse(G.check(G.GOLD["L08"], collide)[0])

    def test_set_one_to_one_matching(self):
        """A single generic name used to satisfy several gold names (M09 min_match 2); now one name = one match."""
        self.assertFalse(G.check(G.GOLD["M09"], {"value": ["Cross laminated timber"], "in_data": True})[0])
        self.assertFalse(G.check(G.GOLD["M09"], {"value": ["a", "timber"], "in_data": True})[0])
        self.assertTrue(G.check(G.GOLD["M09"], {"value": ["HASSLACHER CROSS LAMINATED TIMBER", "best wood CLT"], "in_data": True})[0])
        self.assertTrue(G.check(G.GOLD["L10"], {"value": list(G.GOLD["L10"]["expected"]["value"]), "in_data": True})[0])


class Judge(unittest.TestCase):
    def item(self, cid="D01"):
        return queue_of([rec(cid, 1)], sel([cid], 1))[0]

    def test_verdict_contract(self):
        """Exact unique gates/points, integer 0..2 scores (bool rejected), nothing extra."""
        it = self.item()
        ok = verdict_for(it)
        self.assertTrue(J.evaluate_verdict(it, ok)["judge_pass"])
        bad = []
        v = copy.deepcopy(ok); v["points"].pop(); bad.append(("missing point", v))
        v = copy.deepcopy(ok); v["points"].append(dict(v["points"][0])); bad.append(("duplicate point", v))
        v = copy.deepcopy(ok); v["gates"] = []; bad.append(("empty gates", v))
        v = copy.deepcopy(ok); v["gates"].append({"gate": "G-INJECT", "verdict": "PASS", "evidence": ""}); bad.append(("extra gate", v))
        v = copy.deepcopy(ok); v["gates"].append(dict(v["gates"][0])); bad.append(("duplicate gate", v))
        for s in [True, 3, -1, 1.5, "2", None]:
            v = copy.deepcopy(ok); v["points"][0]["score"] = s; bad.append((f"score {s!r}", v))
        v = copy.deepcopy(ok); v["gates"][0]["verdict"] = "pass"; bad.append(("verdict case", v))
        v = copy.deepcopy(ok); v["extra"] = 1; bad.append(("extra key", v))
        for name, v in bad:
            with self.assertRaises(C.ContractError, msg=name):
                J.evaluate_verdict(it, v)

    def test_threshold_unrounded_and_gate_fail(self):
        """Share uses exact arithmetic (>= 0.8); any gate FAIL fails."""
        it = {"gates": ["G-FAB"], "expected": {"type": "rubric", "points": ["a", "b", "c", "d", "e"]}, "must_include": []}
        def v(scores, gate="PASS"):
            return {"gates": [{"gate": "G-FAB", "verdict": gate, "evidence": ""}],
                    "points": [{"point": f"P{i+1}", "score": s, "evidence": ""} for i, s in enumerate(scores)]}
        self.assertTrue(J.evaluate_verdict(it, v([2, 2, 2, 1, 1]))["judge_pass"])   # 8/10
        self.assertFalse(J.evaluate_verdict(it, v([2, 2, 1, 1, 1]))["judge_pass"])  # 7/10
        self.assertFalse(J.evaluate_verdict(it, v([2] * 5, "FAIL"))["judge_pass"])

    def test_zero_point_policy(self):
        """No points -> judged on gates only (share 1.0); no gates and no points -> invalid; zero gates with points valid."""
        gates_only = {"gates": ["G-FAB"], "expected": {"type": "rubric"}, "must_include": []}
        r = J.evaluate_verdict(gates_only, {"gates": [{"gate": "G-FAB", "verdict": "PASS", "evidence": ""}], "points": []})
        self.assertEqual((r["point_share"], r["judge_pass"]), (1.0, True))
        with self.assertRaises(C.ContractError):
            J.evaluate_verdict({"gates": [], "expected": {"type": "rubric"}, "must_include": []}, {"gates": [], "points": []})
        pts_only = {"gates": [], "expected": {"type": "rubric", "points": ["a"]}, "must_include": []}
        self.assertTrue(J.evaluate_verdict(pts_only, {"gates": [], "points": [{"point": "P1", "score": 2, "evidence": ""}]})["judge_pass"])

    def test_judge_results_binding(self):
        """Valid judge PASS is retained; stale, duplicate, error, served-model-differs and malformed results never pass."""
        s = sel(["D01"], 1)
        r = rec("D01", 1, structured={"value": None, "in_data": True})
        it = queue_of([r], s)[0]
        good = judged_for(it, verdict_for(it))
        st = lambda jr: states(G.grade_records(rows(r), s, rows(*jr), ref=REF))
        self.assertEqual(st([]), ["PENDING_JUDGE"])
        self.assertEqual(st([good]), ["PASS"])
        self.assertEqual(st([judged_for(it, verdict_for(it, score=0))]), ["FAIL"])
        self.assertEqual(st([good, good]), ["PENDING_JUDGE"])
        stale = copy.deepcopy(good); stale["binding"]["answer_sha256"] = "0" * 64
        self.assertEqual(st([stale]), ["PENDING_JUDGE"])
        r2 = dict(r, answer="different answer")
        self.assertEqual(states(G.grade_records(rows(r2), s, rows(good), ref=REF)), ["PENDING_JUDGE"])
        err = {k: v for k, v in good.items() if k != "verdict"}; err["error"] = "judge refusal"
        self.assertEqual(st([err]), ["JUDGE_ERROR"])
        self.assertEqual(st([judged_for(it, verdict_for(it), served="fallback-x")]), ["SERVED_MODEL_DIFFERS"])
        broken = copy.deepcopy(good); broken["verdict"]["points"] = []
        self.assertEqual(st([broken]), ["PENDING_JUDGE"])
        rep = G.grade_records(rows(r), s, rows(good), ref=REF)
        self.assertTrue(rep["integrity_ok"])

    def test_code_fail_not_rescued_and_code_pass_waits(self):
        """code+rubric: a code FAIL stays FAIL even with a judge PASS; a code pass alone is PENDING, never PASS."""
        s = sel(["L03"], 1)
        self.assertEqual(states(G.grade_records(rows(rec("L03", 1)), s, ref=REF)), ["PENDING_JUDGE"])
        wrong = rec("L03", 1, structured={"value": {"Recycling": 1.0}, "in_data": True})
        it = queue_of([rec("L03", 1)], s)[0]
        self.assertEqual(states(G.grade_records(rows(wrong), s, rows(judged_for(it, verdict_for(it))), ref=REF)), ["FAIL"])
        self.assertEqual(queue_of([wrong], s), [])

    def test_judge_one_fake_client(self):
        """judge_one records requested+served model; refusal, exceptions, non-JSON, NaN and bad verdicts become errors."""
        it = self.item()
        class Resp:
            def __init__(self, text, stop="end_turn", model="judge-m"):
                self.content = [types.SimpleNamespace(type="text", text=text)]
                self.stop_reason, self.model = stop, model
        class Client:
            def __init__(self, resp=None, exc=None):
                self.resp, self.exc = resp, exc
                self.beta = types.SimpleNamespace(messages=types.SimpleNamespace(create=self.create))
            def create(self, **kw):
                if self.exc:
                    raise self.exc
                return self.resp
        ok = J.judge_one(Client(Resp(json.dumps(verdict_for(it)))), "judge-m", it)
        self.assertTrue(ok["judge_pass"])
        self.assertEqual((ok["judge"]["requested_model"], ok["judge"]["served_model"]), ("judge-m", "judge-m"))
        self.assertEqual(ok["binding"], it["binding"])
        nan = json.dumps(verdict_for(it)).replace('"score": 2', '"score": NaN', 1)
        for c in [Client(Resp("not json")), Client(Resp(nan)), Client(Resp("{}")), Client(Resp("{}", stop="refusal")),
                  Client(exc=RuntimeError("network down"))]:
            out = J.judge_one(c, "judge-m", it)
            self.assertIn("error", out)
            self.assertNotIn("judge_pass", out)

    def test_judge_main_rejects_duplicate_queue(self):
        """A queue with a repeated (id, run) is refused before any judge call."""
        it = self.item()
        with tempfile.TemporaryDirectory() as d:
            q = Path(d) / "q.jsonl"
            q.write_text((json.dumps(it) + "\n") * 2, encoding="utf-8")
            self.assertEqual(J.main(["--queue", str(q), "--out", str(Path(d) / "o.jsonl")], client=object()), 3)
            self.assertFalse((Path(d) / "o.jsonl").exists())


class FakeAnthropic(types.ModuleType):
    class APIError(Exception):
        def __init__(self, msg, status_code=None):
            super().__init__(msg); self.message, self.status_code = msg, status_code
    class APIStatusError(APIError):
        pass
    class RateLimitError(APIStatusError):
        pass


def fake_resp(model, *, submit=None, stop="tool_use"):
    content = []
    if submit is not None:
        content.append(types.SimpleNamespace(type="tool_use", name="submit_answer", id="t1", input=submit))
    return types.SimpleNamespace(model=model, content=content, stop_reason=stop, stop_details=None,
                                 usage=types.SimpleNamespace(input_tokens=1, output_tokens=1))


class FakeClient:
    def __init__(self, script):
        self.script = list(script)
        self.calls = 0
        self.beta = types.SimpleNamespace(messages=types.SimpleNamespace(create=self.create))
    def create(self, **kw):
        self.calls += 1
        item = self.script.pop(0) if len(self.script) > 1 else self.script[0]
        if isinstance(item, Exception):
            raise item
        return item


class Runner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._saved = sys.modules.get("anthropic")
        sys.modules["anthropic"] = FakeAnthropic("anthropic")
        import run_eval
        cls.R = run_eval

    @classmethod
    def tearDownClass(cls):
        if cls._saved is None:
            sys.modules.pop("anthropic", None)
        else:
            sys.modules["anthropic"] = cls._saved

    def test_cli_validation_before_spend(self):
        """--k 0/-1/true, --workers 0, --max-turns 0 are argparse errors; bad --ids fail planning."""
        for argv in (["--k", "0"], ["--k", "-1"], ["--k", "true"], ["--workers", "0"], ["--max-turns", "0"]):
            with self.assertRaises(SystemExit, msg=argv):
                self.R.parse_args(argv)
        for ids in ["", "L01,,T01", "NOPE", "L01,L01"]:
            with self.assertRaises(C.ContractError, msg=ids):
                self.R.plan(self.R.parse_args(["--ids", ids]), G.GOLD)
        s, jobs = self.R.plan(self.R.parse_args(["--ids", "L01,T01", "--k", "2"]), G.GOLD)
        self.assertEqual(len(jobs), 4)

    def test_run_case_records_models_and_errors(self):
        """Records carry requested+served models; API errors, refusals and missing submits are typed error records."""
        A = sys.modules["anthropic"]
        case = G.GOLD["L01"]
        sub = {"answer": "1.43 kg CO2e per kg", "value_json": "1.43", "in_data": True}
        r = self.R.run_case(FakeClient([fake_resp("m", submit=sub)]), None, case, 1, "m", "high", 3, [])
        self.assertEqual((r["requested_model"], r["served_models"], r["structured"]["value"]), ("m", ["m"], 1.43))
        r = self.R.run_case(FakeClient([fake_resp("fb", submit=sub)]), None, case, 1, "m", "high", 3, [])
        self.assertEqual(r["served_models"], ["fb"])
        r = self.R.run_case(FakeClient([A.APIError("boom", 500)]), None, case, 1, "m", "high", 3, [])
        self.assertEqual(r["error_kind"], "api")
        r = self.R.run_case(FakeClient([fake_resp("m", stop="refusal")]), None, case, 1, "m", "high", 3, [])
        self.assertEqual(r["error_kind"], "refusal")
        r = self.R.run_case(FakeClient([fake_resp("m", stop="end_turn")]), None, case, 1, "m", "high", 2, [])
        self.assertEqual(r["error_kind"], "no_submit")
        raw = dict(sub, value_json="about 1.4")
        r = self.R.run_case(FakeClient([fake_resp("m", submit=raw)]), None, case, 1, "m", "high", 3, [])
        self.assertEqual(r["structured"]["value"], "about 1.4")  # documented raw-string fallback, graded as FAIL
        self.assertFalse(G.check(case, r["structured"])[0])

    def test_offline_end_to_end_no_append(self):
        """Fake-client run -> manifest -> grade (PASS, integrity clean) -> judge merge; rerun into same --out refused."""
        sub = {"answer": "1.43", "value_json": "1.43", "in_data": True}
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "cand.jsonl"
            a = self.R.parse_args(["--ids", "L01,D01", "--k", "1", "--out", str(out), "--model", "m", "--workers", "1"])
            self.R.execute(a, G.GOLD, FakeClient([fake_resp("m", submit=sub)]), None, [], fixture_source(d))
            m = C.loads_strict(C.manifest_path_for(out).read_text(encoding="utf-8"))
            self.assertEqual(m["selection"], {"ids": ["L01", "D01"], "k": {"L01": 1, "D01": 1}})
            q, jr = Path(d) / "q.jsonl", Path(d) / "j.jsonl"
            rep = G.grade(out, judged=jr, queue=q, quiet=True)
            self.assertEqual(states(rep), ["PASS", "PENDING_JUDGE"])
            self.assertFalse(rep["integrity_ok"])
            it = [o for _, o in C.read_jsonl(q, "queue")][0]
            fc = types.SimpleNamespace(beta=types.SimpleNamespace(messages=types.SimpleNamespace(
                create=lambda **kw: types.SimpleNamespace(model="judge-m", stop_reason="end_turn",
                                                          content=[types.SimpleNamespace(type="text", text=json.dumps(verdict_for(it)))]))))
            self.assertEqual(J.main(["--model", "judge-m", "--queue", str(q), "--out", str(jr)], client=fc), 0)
            rep = G.grade(out, judged=jr, queue=q, quiet=True)
            self.assertEqual(states(rep), ["PASS", "PASS"])
            self.assertTrue(rep["integrity_ok"], rep["integrity_problems"])
            with self.assertRaises(C.ContractError):
                self.R.execute(a, G.GOLD, FakeClient([fake_resp("m", submit=sub)]), None, [], {})
            self.assertEqual(len(out.read_text(encoding="utf-8").splitlines()), 2)
            Path(str(out) + ".partial").write_text("", encoding="utf-8")
            out.unlink(); C.manifest_path_for(out).unlink()
            with self.assertRaises(C.ContractError):
                self.R.execute(a, G.GOLD, FakeClient([fake_resp("m", submit=sub)]), None, [], {})

    def test_cli_exit_codes(self):
        """grade.py main: 3 = incomplete or unverifiable (no manifest), 0 = complete under a manifest even with
        scored FAILs, 1 only with --fail-on-fail; --k 0 is a usage error."""
        with tempfile.TemporaryDirectory() as d:
            p, q, none = Path(d) / "c.jsonl", Path(d) / "q.jsonl", str(Path(d) / "none.jsonl")
            p.write_text(json.dumps(rec("L01", 1)) + "\n", encoding="utf-8")
            base = ["--judged", none, "--queue", str(q)]
            self.assertEqual(G.main([str(p), "--ids", "L01"] + base), 3)            # runs 2,3 missing
            self.assertEqual(G.main([str(p), "--ids", "L01", "--k", "1"] + base), 3)  # complete but no manifest
            with self.assertRaises(SystemExit):
                G.main([str(p), "--k", "0"] + base)
            for answer, plain, strict in (("1.43", 0, 0), ("9.99", 0, 1)):
                out = Path(d) / f"run_{answer}.jsonl"
                a = self.R.parse_args(["--ids", "L01", "--k", "1", "--out", str(out), "--model", "m", "--workers", "1"])
                sub = {"answer": answer, "value_json": answer, "in_data": True}
                self.R.execute(a, G.GOLD, FakeClient([fake_resp("m", submit=sub)]), None, [], fixture_source(d))
                self.assertEqual(G.main([str(out)] + base), plain)
                self.assertEqual(G.main([str(out), "--fail-on-fail"] + base), strict)


class SourceData(unittest.TestCase):
    def test_find_csv_ambiguity_and_provenance(self):
        """Several matching exports must be refused (was: silently the last); provenance hashes the bytes used."""
        saved = obd_data.REPO
        with tempfile.TemporaryDirectory() as d:
            try:
                obd_data.REPO = Path(d)
                (Path(d) / "data").mkdir()
                with self.assertRaises(SystemExit):
                    obd_data.find_csv()
                a = Path(d) / "data" / "OBD_2024_II_a.csv"
                a.write_bytes(b"x;y\n1;2\n")
                self.assertEqual(obd_data.find_csv(), a)
                (Path(d) / "data" / "OBD_2024_II_b.csv").write_bytes(b"x\n")
                with self.assertRaisesRegex(SystemExit, "Several"):
                    obd_data.find_csv()
                self.assertEqual(obd_data.find_csv(str(a)), a)
                prov = obd_data.file_provenance(a)
                self.assertEqual(prov["sha256"], C.sha256_file(a))
                self.assertIn("unknown", prov["licence"])
            finally:
                obd_data.REPO = saved

    def test_reference_fingerprint_stdlib_and_missing_file(self):
        """The reference fingerprint no longer needs pandas, matches the gold, and a missing file raises."""
        self.assertEqual(REF, ("32bed6c7507a", None))
        with self.assertRaises(OSError):
            obd_data.reference_fingerprint(["analysis/does-not-exist.csv"])


def run_json(path):
    """Run this module's tests and write one record per test (name, purpose, outcome) to path."""
    import contextlib, io
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    out = []

    class Rec(unittest.TestResult):
        def addSuccess(self, t):
            out.append((t, "ok", ""))

        def addFailure(self, t, err):
            out.append((t, "FAIL", self._exc_info_to_string(err, t)))

        def addError(self, t, err):
            out.append((t, "ERROR", self._exc_info_to_string(err, t)))

        def addSkip(self, t, reason):
            out.append((t, "skipped", reason))

    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        res = suite.run(Rec())
    rows = [{"test": f"{type(t).__name__}.{t._testMethodName}", "purpose": (t._testMethodDoc or "").strip(),
             "outcome": o, "detail": d} for t, o, d in out]
    Path(path).write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return 0 if res.wasSuccessful() and all(r["outcome"] == "ok" for r in rows) else 1


if __name__ == "__main__":
    if sys.argv[1:2] == ["--json"]:
        sys.exit(run_json(sys.argv[2]))
    unittest.main()