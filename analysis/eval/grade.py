"""Grade candidate runs against golden_v1.jsonl, fail-closed.

Candidate file (written by run_eval.py, or by any harness): one JSON object per line
  {"id": "L01", "run": 1, "answer": "<free text>", "structured": {"value": ..., "in_data": true}}
or an error record {"id": "L01", "run": 1, "error": "...", "error_kind": "api" | "refusal" | "no_submit"}.

The required matrix is every selected case x run 1..k. It comes from the run manifest that
run_eval.py writes next to the candidate file (<candidate>.manifest.json), else from --ids/--k,
else all cases at their runs_k. Every required cell gets exactly one state:
  PASS, FAIL, REFUSAL (scored results) or
  MISSING, DUPLICATE, INVALID, ERROR, PENDING_JUDGE, JUDGE_ERROR, SERVED_MODEL_DIFFERS (integrity).
Only PASS earns credit; missing or pending cells stay in the denominator. Unknown case ids and
out-of-range runs are reported, never silently skipped.

Pass 1, here: code checks and code-checkable gates. Runs the judge must decide go to judge_queue.jsonl.
Pass 2, judge.py: writes judge_results.jsonl. Re-running this script merges it; a judge result is
used only if its binding (answer, candidate model/config, case, reference and prompt fingerprints)
matches the current run exactly. Stale, duplicate or malformed judge results are rejected.

Exit codes: 0 = complete and valid (scored FAILs are results, not errors; use --fail-on-fail to
exit 1 when any run failed); 3 = integrity problem (anything not fully graded, stale reference
files, gold/manifest mismatch); 2 = usage error.

  python3 -I analysis/eval/grade.py analysis/eval/runs/candidate.jsonl
  python3 -I analysis/eval/grade.py --selftest
"""
import argparse, json, sys, unicodedata
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import contract as C
import judge as J

GOLD_PATH = HERE / "golden_v1.jsonl"
GOLD = C.load_gold(GOLD_PATH)
QUEUE, JUDGED = HERE / "judge_queue.jsonl", HERE / "judge_results.jsonl"
SCORED = ("PASS", "FAIL", "REFUSAL")
STATES = SCORED + ("MISSING", "DUPLICATE", "INVALID", "ERROR", "PENDING_JUDGE", "JUDGE_ERROR", "SERVED_MODEL_DIFFERS")
EXIT_OK, EXIT_FAILED_RUNS, EXIT_USAGE, EXIT_INTEGRITY = 0, 1, 2, 3


def close(a, b, rel, abs_=None):
    if isinstance(a, bool) or isinstance(b, bool):
        return False
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError, OverflowError):
        return False
    if not (C.is_number(a) and C.is_number(b)):
        return False
    if abs_ is not None and abs(a - b) <= abs_:
        return True
    return abs(a - b) <= rel * max(abs(b), 1e-9)


def kendall(a, b):
    pos = {x: i for i, x in enumerate(b)}
    if set(a) != set(b):
        return -1.0
    pairs = list(combinations(a, 2))
    if not pairs:
        return 1.0
    conc = sum(1 for x, y in pairs if pos[x] < pos[y])
    return (2 * conc - len(pairs)) / len(pairs)


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return "".join(ch for ch in s if ch.isalnum())


def loose_match(a, b):
    """Normalized names match when equal, or when one contains the other and the shorter has >= 4 characters."""
    if not a or not b:
        return False
    if a == b:
        return True
    return min(len(a), len(b)) >= 4 and (a in b or b in a)


_NONE = object()


def match_keys(d, wanted):
    """Map each wanted key to one candidate key: an exact normalized match wins, else a unique loose match.
    A key that matches ambiguously, or a candidate key claimed by two wanted keys, counts as missing."""
    if not isinstance(d, dict):
        return {w: _NONE for w in wanted}
    chosen = {}
    for w in wanted:
        wn = norm(w)
        exact = [c for c in d if norm(c) == wn]
        hits = exact or [c for c in d if loose_match(norm(c), wn)]
        chosen[w] = hits[0] if len(hits) == 1 else None
    used = Counter(c for c in chosen.values() if c is not None)
    return {w: (d[c] if c is not None and used[c] == 1 else _NONE) for w, c in chosen.items()}


def pick(d, key):
    """Back-compatible single-key lookup with the same policy as match_keys."""
    v = match_keys(d, [key])[key]
    return None if v is _NONE else v


def set_hits(want, got):
    """Maximum one-to-one matching: one reported name can satisfy only one gold name."""
    got = list(dict.fromkeys(g for g in got if g))
    adj = [[j for j, g in enumerate(got) if loose_match(g, norm(w))] for w in want]
    owner = {}

    def augment(i, seen):
        for j in adj[i]:
            if j not in seen:
                seen.add(j)
                if j not in owner or augment(owner[j], seen):
                    owner[j] = i
                    return True
        return False

    hits = sum(augment(i, set()) for i in range(len(want)))
    invented = [g for j, g in enumerate(got) if not any(j in a for a in adj)]
    return hits, invented


def check(case, st):
    """Return (code_pass or None, failed gates, note)."""
    e, st = case["expected"], st or {}
    t, v = e["type"], st.get("value")
    gates = []
    if t == "refusal":
        if st.get("in_data") is not False or isinstance(v, (int, float)):
            gates.append("G-FAB")
        return (not gates, gates, "")
    if "G-FALSEABSENT" in case["gates"] and st.get("in_data") is False:
        return (False, ["G-FALSEABSENT"], "claimed absent")
    if t == "numeric":
        ok = close(v, e["value"], e.get("tolerance_rel", 0.01), e.get("tolerance_abs"))
        if not ok and "G-UNIT" in case["gates"] and C.is_number(v) and e["value"]:
            r = abs(v / e["value"])
            if r > 50 or r < 0.02:
                gates.append("G-UNIT")
        return (ok and not gates, gates, f"got {v}, want {e['value']}")
    if t == "numeric_set":
        got = match_keys(v, list(e["value"]))
        ok = all(close(None if got[k] is _NONE else got[k], x, e.get("tolerance_rel", 0.01)) for k, x in e["value"].items())
        if ok and isinstance(v, dict) and len(v) > len(e["value"]):
            return (False, gates, "extra values reported")
        return (ok, gates, f"got {v}")
    if t == "count":
        if isinstance(e["value"], dict):
            got = match_keys(v, list(e["value"]))
            return (all(C.is_int(got[k]) and got[k] == x for k, x in e["value"].items()), gates, f"got {v}")
        return (C.is_int(v) and v == e["value"], gates, f"got {v}")
    if t == "rank":
        v = [str(x).strip() for x in (v or [])] if isinstance(v, list) else []
        want = [str(x) for x in e["value"]]
        return (v == want, gates, f"tau={kendall(v, want):.2f}" if v else "no ranking")
    if t == "set":
        want = e["value"]
        if isinstance(want, dict):
            got = match_keys(v, list(want))
            return (all(got[k] is not _NONE and got[k] is not None and norm(got[k]) == norm(x) for k, x in want.items()), gates, f"got {v}")
        got = [norm(x) for x in (v or [])] if isinstance(v, list) else []
        hits, invented = set_hits(want, got)
        need = e.get("min_match", len(want))
        if invented and need == len(want):
            gates.append("G-FAB")
        return (hits >= need and not gates, gates, f"{hits}/{len(want)} matched")
    return (None, gates, "rubric only")


def current_reference():
    """(fingerprint or None, problem or None). A missing checker or file is a visible problem, not a skip."""
    try:
        from obd_data import REFERENCE_FILES, reference_fingerprint
        return reference_fingerprint(REFERENCE_FILES), None
    except (ImportError, OSError) as exc:
        return None, f"reference fingerprint unavailable: {type(exc).__name__}: {exc}"


def stale_cases(ids=None, now=None):
    """Selected cases whose reference files changed since the gold was built."""
    if now is None:
        now, _ = current_reference()
    ids = list(GOLD) if ids is None else ids
    return [cid for cid in ids if GOLD[cid].get("reference_fingerprint") not in (None, now)]


def queue_item(case, r):
    item = {"id": r["id"], "run": r["run"], "candidate_model": r.get("requested_model", r.get("model")),
            "prompt": case["prompt"], "expected": case["expected"], "gates": case["gates"],
            "must_include": case["must_include"], "must_not": case["must_not"], "rubric": case["grader"].get("rubric"),
            "answer": r.get("answer", ""), "code_result": None, "code_gate_failures": []}
    return item


def binding(case, r, item, ref_fp):
    return {"contract": C.CONTRACT_VERSION, "id": r["id"], "run": r["run"], "case_sha256": C.fingerprint(case),
            "reference_fingerprint": ref_fp, "answer_sha256": C.sha256_text(r.get("answer", "")),
            "structured_sha256": C.fingerprint(r.get("structured")),
            "candidate_requested_model": r.get("requested_model", r.get("model")),
            "candidate_served_models": r.get("served_models"),
            "candidate_config": {"effort": r.get("effort"), "max_turns": r.get("max_turns")},
            "judge_prompt_sha256": J.prompt_sha256(item)}


def record_problem(r, manifest):
    """Shape check of one candidate record; None if acceptable."""
    if "error" in r:
        if not isinstance(r["error"], str) or not r["error"].strip():
            return "error must be a non-empty string"
        if r.get("error_kind") not in (None, "api", "refusal", "no_submit"):
            return "unknown error_kind"
    else:
        if not isinstance(r.get("structured"), dict):
            return "structured must be an object"
        if not isinstance(r.get("answer", ""), str):
            return "answer must be a string"
        if r["structured"].get("in_data") not in (True, False, None):
            return "structured.in_data must be true, false or null"
    if manifest is not None:
        want = manifest["candidate"]["requested_model"]
        if r.get("requested_model", r.get("model")) != want:
            return f"requested model differs from manifest ({want})"
        if "error" not in r:
            served = r.get("served_models")
            if not isinstance(served, list) or not served or not all(isinstance(s, str) for s in served):
                return "served_models must be a non-empty list of strings"
    return None


def load_manifest(path, gold_sha, ref_fp):
    m = C.loads_strict(Path(path).read_text(encoding="utf-8"))
    if not isinstance(m, dict) or m.get("contract") != C.CONTRACT_VERSION:
        raise C.ContractError(f"manifest {path}: contract must be {C.CONTRACT_VERSION}")
    C.validate_selection(m.get("selection"), GOLD)
    cand = m.get("candidate")
    if not isinstance(cand, dict) or not isinstance(cand.get("requested_model"), str) or not cand["requested_model"]:
        raise C.ContractError(f"manifest {path}: candidate.requested_model missing")
    problems = []
    if m.get("gold_sha256") != gold_sha:
        problems.append("gold file changed since the run (manifest gold_sha256 differs)")
    if ref_fp is not None and m.get("reference_fingerprint") != ref_fp:
        problems.append("reference files changed since the run (manifest reference_fingerprint differs)")
    return m, problems


def grade_records(records, sel, judged_rows=None, manifest=None, ref=None, write_queue_to=None):
    """Pure grading of parsed records. records/judged_rows: [(line, obj)]. Returns the report dict."""
    ref_fp, ref_problem = ref if ref is not None else current_reference()
    problems = [ref_problem] if ref_problem else []
    stale = stale_cases(sel["ids"], ref_fp) if ref_fp else [c for c in sel["ids"] if GOLD[c].get("reference_fingerprint")]
    if stale:
        problems.append(f"reference fingerprint does not match gold for {', '.join(stale)}; rebuild before trusting")
    required = C.required_cells(sel)
    req_set = set(required)
    by_key, extra = defaultdict(list), []
    for n, r in records:
        cid, run = r.get("id"), r.get("run")
        if not isinstance(cid, str) or not C.is_int(run):
            extra.append({"line": n, "problem": "id must be a string and run an integer (not bool)"})
        elif (cid, run) not in req_set:
            extra.append({"line": n, "id": cid, "run": run,
                          "problem": "unknown case" if cid not in sel["k"] else f"run outside 1..{sel['k'][cid]}"})
        else:
            by_key[(cid, run)].append((n, r))
    if extra:
        problems.append(f"{len(extra)} record(s) outside the required matrix")

    cells, queue, items = {}, [], {}
    for key in required:
        cid, run = key
        case, lst = GOLD[cid], by_key.get(key, [])
        if not lst:
            cells[key] = {"state": "MISSING", "note": "no record"}
            continue
        if len(lst) > 1:
            cells[key] = {"state": "DUPLICATE", "note": f"lines {[n for n, _ in lst]}"}
            continue
        n, r = lst[0]
        bad = record_problem(r, manifest)
        if bad:
            cells[key] = {"state": "INVALID", "note": f"line {n}: {bad}"}
            continue
        if "error" in r:
            refusal = r.get("error_kind") == "refusal" or (r.get("error_kind") is None and r["error"].startswith("refusal"))
            cells[key] = {"state": "REFUSAL" if refusal else "ERROR", "note": r["error"]}
            continue
        served = r.get("served_models")
        want_model = r.get("requested_model", r.get("model"))
        if isinstance(served, list) and served and any(s != want_model for s in served):
            cells[key] = {"state": "SERVED_MODEL_DIFFERS", "note": f"requested {want_model}, served {served}"}
            continue
        ok, gates, note = check(case, r.get("structured"))
        if case["grader"]["method"] == "code":
            cells[key] = {"state": "PASS" if ok is True else "FAIL", "gates": gates, "note": note}
            continue
        if ok is False:
            cells[key] = {"state": "FAIL", "gates": gates, "note": "code part failed; the judge cannot rescue it. " + note}
            continue
        item = queue_item(case, r)
        item["code_result"], item["code_gate_failures"] = ok, gates
        item["binding"] = binding(case, r, item, ref_fp)
        queue.append(item)
        items[key] = item
        cells[key] = {"state": "PENDING_JUDGE", "gates": gates, "note": ("code part passed; " if ok else "") + "judge pending"}

    judge_models, orphans = set(), 0
    groups = defaultdict(list)
    for n, j in judged_rows or []:
        k = (j.get("id"), j.get("run"))
        if not isinstance(k[0], str) or not C.is_int(k[1]):
            problems.append(f"judge result line {n}: bad id/run")
            continue
        groups[k].append((n, j))
    for k, lst in groups.items():
        if k not in items:
            orphans += 1
            continue
        cell = cells[k]
        if len(lst) > 1:
            cell["note"] = f"judge pending: duplicate judge results (lines {[n for n, _ in lst]}) rejected"
            continue
        n, j = lst[0]
        if j.get("binding") != items[k]["binding"]:
            cell["note"] = f"judge pending: stale judge result (line {n}) does not match this answer/case/model/prompt"
            continue
        cfg = j.get("judge")
        if not isinstance(cfg, dict) or not isinstance(cfg.get("requested_model"), str):
            cell["note"] = f"judge pending: judge result line {n} lacks judge config"
            continue
        if "error" in j:
            cell.update(state="JUDGE_ERROR", note=f"judge error: {j['error']}")
            continue
        served = cfg.get("served_model")
        if served != cfg["requested_model"]:
            cell.update(state="SERVED_MODEL_DIFFERS", note=f"judge requested {cfg['requested_model']}, served {served}")
            continue
        try:
            res = J.evaluate_verdict(items[k], j.get("verdict"))
        except C.ContractError as exc:
            cell["note"] = f"judge pending: invalid verdict (line {n}): {exc}"
            continue
        judge_models.add(served)
        cell.update(state="PASS" if res["judge_pass"] else "FAIL",
                    note=f"judge share {res['point_share']:.3f}, gates_ok {res['gates_ok']}; {cell['note']}")
    if write_queue_to is not None:
        C.write_atomic(write_queue_to, "".join(json.dumps(q, ensure_ascii=False, allow_nan=False) + "\n" for q in queue))

    counts = Counter(c["state"] for c in cells.values())
    unscored = sum(v for s, v in counts.items() if s not in SCORED)
    if unscored:
        problems.append(f"{unscored} required run(s) not fully graded")
    fam = defaultdict(lambda: {"required": 0, "pass": 0, "cases": 0, "cases_all_pass": 0})
    for cid in sel["ids"]:
        f = fam[f"{GOLD[cid]['family']}/{GOLD[cid]['tier']}"]
        states = [cells[(cid, r)]["state"] for r in range(1, sel["k"][cid] + 1)]
        f["required"] += len(states)
        f["pass"] += states.count("PASS")
        f["cases"] += 1
        f["cases_all_pass"] += all(s == "PASS" for s in states)
    return {"contract": C.CONTRACT_VERSION, "selection": sel, "required_runs": len(required),
            "counts": {s: counts.get(s, 0) for s in STATES}, "by_family_tier": dict(sorted(fam.items())),
            "integrity_ok": not problems, "integrity_problems": problems, "outside_matrix": extra,
            "orphan_judge_results": orphans, "gold_warnings": list(C.GOLD_WARNINGS), "judge_models": sorted(judge_models), "reference_fingerprint": ref_fp,
            "cells": [{"id": cid, "run": run, **cells[(cid, run)]} for cid, run in required],
            "scope": "Source-derived proposed cases; descriptive only. No calibrated, expert or scientific validation."}


def print_report(rep):
    print(f"{'family/tier':32} {'pass@1':>7} {'pass^k':>7} cases  (denominator = all required runs)")
    tp = tn = ta = tc = 0
    for key, f in rep["by_family_tier"].items():
        print(f"{key:32} {f['pass'] / f['required']:7.0%} {f['cases_all_pass'] / f['cases']:7.0%} {f['cases']:5}")
        tp, tn, ta, tc = tp + f["pass"], tn + f["required"], ta + f["cases_all_pass"], tc + f["cases"]
    if tn:
        print(f"{'all':32} {tp / tn:7.0%} {ta / tc:7.0%} {tc:5}")
    print("states: " + ", ".join(f"{s} {n}" for s, n in rep["counts"].items() if n))
    for c in [c for c in rep["cells"] if c["state"] != "PASS"][:30]:
        print(f"  {c['state']} {c['id']} run {c['run']}: gates={c.get('gates', [])} {c['note']}")
    for x in rep["outside_matrix"][:10]:
        print(f"  OUTSIDE {x}")
    if rep["orphan_judge_results"]:
        print(f"  note: {rep['orphan_judge_results']} judge result(s) for runs that need no judge were ignored")
    for w in rep.get("gold_warnings", []):
        print(f"GOLD WARNING: {w}")
    for p in rep["integrity_problems"]:
        print(f"INTEGRITY: {p}")
    if rep["counts"]["PENDING_JUDGE"]:
        print("Run judge.py on the queue, then grade again.")


def grade(path, sel=None, manifest_path=None, judged=JUDGED, queue=QUEUE, csv=None, quiet=False):
    gold_sha = C.sha256_file(GOLD_PATH)
    ref = current_reference()
    records = C.read_jsonl(path, "candidate")
    manifest, extra_problems = None, []
    mpath = Path(manifest_path) if manifest_path else C.manifest_path_for(path)
    if mpath.exists():
        manifest, extra_problems = load_manifest(mpath, gold_sha, ref[0])
        if sel is not None and sel != manifest["selection"]:
            raise C.ContractError("--ids/--k disagree with the run manifest selection")
        sel = manifest["selection"]
        if csv is not None:
            src = (manifest.get("source") or {}).get("sha256")
            if src != C.sha256_file(csv):
                extra_problems.append("--csv bytes differ from the export recorded in the manifest")
    elif manifest_path:
        raise C.ContractError(f"manifest not found: {mpath}")
    if manifest is None:
        if sel is None:
            sel = C.plan_selection(GOLD)
            extra_problems.append("no run manifest: required matrix assumed = all cases at runs_k; run config and served model unverified")
        else:
            extra_problems.append("no run manifest: selection declared via --ids/--k; run config and served model unverified")
    judged_rows = C.read_jsonl(judged, "judge results") if judged and Path(judged).exists() else []
    rep = grade_records(records, sel, judged_rows, manifest, ref, write_queue_to=queue)
    if extra_problems:
        rep["integrity_problems"] = extra_problems + rep["integrity_problems"]
        rep["integrity_ok"] = False
    rep["candidate_sha256"] = C.sha256_file(path)
    rep["gold_sha256"] = gold_sha
    if not quiet:
        print_report(rep)
    return rep


def selftest():
    """Offline self-check of the code grader on the set itself. Not a model or accuracy result."""
    ids = [cid for cid, c in GOLD.items() if c["expected"]["type"] != "rubric"]
    sel = C.plan_selection(GOLD, ids)
    good, bad = [], []
    for cid in ids:
        c, e = GOLD[cid], GOLD[cid]["expected"]
        st = {"in_data": False} if e["type"] == "refusal" else {"value": e["value"], "in_data": True}
        if e["type"] == "numeric":
            wrong = {"value": e["value"] * (1000 if "G-UNIT" in c["gates"] else 1.2)}
        elif e["type"] == "refusal":
            wrong = {"value": 42.0, "in_data": True}
        elif e["type"] == "rank":
            wrong = {"value": list(reversed(e["value"]))}
        elif "G-FALSEABSENT" in c["gates"]:
            wrong = {"in_data": False}
        else:
            wrong = {"value": None}
        for k in range(1, sel["k"][cid] + 1):
            good.append((0, {"id": cid, "run": k, "answer": "", "structured": st}))
            bad.append((0, {"id": cid, "run": k, "answer": "", "structured": wrong}))
    rg, rb = grade_records(good, sel), grade_records(bad, sel)
    code = [c for c in rg["cells"] if GOLD[c["id"]]["grader"]["method"] == "code"]
    mixed = [c for c in rg["cells"] if GOLD[c["id"]]["grader"]["method"] != "code"]
    assert code and all(c["state"] == "PASS" for c in code), "perfect code-graded runs must pass"
    assert mixed and all(c["state"] == "PENDING_JUDGE" for c in mixed), "code+rubric runs must wait for the judge"
    assert all(c["state"] == "FAIL" for c in rb["cells"]), "corrupted runs must all fail"
    l03 = GOLD["L03"]["expected"]["value"]
    loose = {"value": {"Szenario 1: Energierückgewinnung": list(l03.values())[0], "recycling": list(l03.values())[1]}}
    assert check(GOLD["L03"], loose)[0] is True, "loose L03 scenario keys must still pass"
    print(f"perfect: {len(code)} code-graded runs pass, {len(mixed)} code+rubric runs pending judge (never PASS without it)")
    print(f"corrupted: {len(rb['cells'])} runs, all fail")
    print("selftest ok (offline grader self-check only; no model, judge or accuracy claim)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("candidate", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--manifest", help="run manifest (default: <candidate>.manifest.json if present)")
    ap.add_argument("--ids", help="declare the selection when there is no manifest")
    ap.add_argument("--k", type=C.parse_positive_int_arg, help="declare runs per case when there is no manifest")
    ap.add_argument("--judged", default=str(JUDGED))
    ap.add_argument("--queue", default=str(QUEUE))
    ap.add_argument("--csv", help="optional: verify the export bytes against the manifest")
    ap.add_argument("--json-out", help="write the full machine-readable report here (atomic)")
    ap.add_argument("--fail-on-fail", action="store_true", help="exit 1 when a complete grading has any FAIL/REFUSAL")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest()
        return EXIT_OK
    if not a.candidate:
        ap.error("candidate file required")
    try:
        sel = None
        if a.ids is not None or a.k is not None:
            sel = C.plan_selection(GOLD, C.parse_ids_arg(a.ids), a.k)
        rep = grade(a.candidate, sel, a.manifest, a.judged, a.queue, a.csv)
    except (C.ContractError, OSError) as exc:
        print(f"INTEGRITY: {exc}", file=sys.stderr)
        return EXIT_INTEGRITY
    if a.json_out:
        C.write_atomic(a.json_out, json.dumps(rep, ensure_ascii=False, indent=1, allow_nan=False) + "\n")
    if not rep["integrity_ok"]:
        return EXIT_INTEGRITY
    if a.fail_on_fail and (rep["counts"]["FAIL"] or rep["counts"]["REFUSAL"]):
        return EXIT_FAILED_RUNS
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())