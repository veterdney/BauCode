"""Grade candidate runs against golden_v1.jsonl.

Candidate file (written by run_eval.py, or by any harness): one JSON object per line
  {"id": "L01", "run": 1, "answer": "<free text>", "structured": {"value": ..., "in_data": true}}

Pass 1, here: code checks and code-checkable gates. Runs that need a judge go to judge_queue.jsonl.
Pass 2, judge.py: writes judge_results.jsonl. Re-running this script merges it.
Reports pass@1 (mean over runs) and pass^k (every run of a case passes) per family and tier.

  python3 -I analysis/eval/grade.py analysis/eval/runs/candidate.jsonl
  python3 -I analysis/eval/grade.py --selftest
"""
import json, sys, unicodedata
from collections import defaultdict
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
GOLD = {c["id"]: c for c in map(json.loads, open(HERE / "golden_v1.jsonl", encoding="utf-8"))}
QUEUE, JUDGED = HERE / "judge_queue.jsonl", HERE / "judge_results.jsonl"


def close(a, b, rel, abs_=None):
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if abs_ is not None and abs(a - b) <= abs_:
        return True
    return abs(a - b) <= rel * max(abs(b), 1e-9)


def kendall(a, b):
    pos = {x: i for i, x in enumerate(b)}
    if set(a) != set(b):
        return -1.0
    pairs = list(combinations(a, 2))
    conc = sum(1 for x, y in pairs if pos[x] < pos[y])
    return (2 * conc - len(pairs)) / len(pairs)


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return "".join(ch for ch in s if ch.isalnum())


def pick(d, key):
    """Value of `key` in d, matching keys loosely (case, accents, punctuation, substrings)."""
    if not isinstance(d, dict):
        return None
    k = norm(key)
    for cand, v in d.items():
        c = norm(cand)
        if c == k or (c and (c in k or k in c)):
            return v
    return None


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
        if not ok and "G-UNIT" in case["gates"] and isinstance(v, (int, float)) and e["value"]:
            r = abs(v / e["value"])
            if r > 50 or r < 0.02:
                gates.append("G-UNIT")
        return (ok and not gates, gates, f"got {v}, want {e['value']}")
    if t == "numeric_set":
        ok = all(close(pick(v, k), x, e.get("tolerance_rel", 0.01)) for k, x in e["value"].items())
        if ok and isinstance(v, dict) and len(v) > len(e["value"]):
            return (False, gates, "extra values reported")
        return (ok, gates, f"got {v}")
    if t == "count":
        if isinstance(e["value"], dict):
            return (all(pick(v, k) == x for k, x in e["value"].items()), gates, f"got {v}")
        return (v == e["value"], gates, f"got {v}")
    if t == "rank":
        v = [str(x).strip() for x in (v or [])] if isinstance(v, list) else []
        want = [str(x) for x in e["value"]]
        return (v == want, gates, f"tau={kendall(v, want):.2f}" if v else "no ranking")
    if t == "set":
        want = e["value"]
        if isinstance(want, dict):
            return (all(norm(pick(v, k)) == norm(x) for k, x in want.items()), gates, f"got {v}")
        got = [norm(x) for x in (v or [])] if isinstance(v, list) else []
        match = lambda w, g: g and (norm(w) in g or g in norm(w))
        hits = sum(1 for w in want if any(match(w, g) for g in got))
        need = e.get("min_match", len(want))
        invented = [g for g in got if not any(match(w, g) for w in want)]
        if invented and need == len(want):
            gates.append("G-FAB")
        return (hits >= need and not gates, gates, f"{hits}/{len(want)} matched")
    return (None, gates, "rubric only")


def stale_cases():
    """Cases whose reference files changed since the gold was built."""
    try:
        from obd_data import REFERENCE_FILES, reference_fingerprint
    except ImportError:
        return []
    now = reference_fingerprint(REFERENCE_FILES)
    return [c["id"] for c in GOLD.values() if c.get("reference_fingerprint") not in (None, now)]


def grade(path, write_queue=True, quiet=False):
    runs = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    judged = {}
    if JUDGED.exists():
        for l in open(JUDGED, encoding="utf-8"):
            r = json.loads(l)
            judged[(r["id"], r["run"])] = r
    per, queue = defaultdict(list), []
    for r in runs:
        case = GOLD.get(r["id"])
        if not case:
            continue
        if r.get("error"):
            per[r["id"]].append({"ok": False, "gates": [], "note": r["error"]})
            continue
        ok, gates, note = check(case, r.get("structured"))
        if case["grader"]["method"] != "code":
            queue.append({"id": r["id"], "run": r.get("run"), "candidate_model": r.get("model"), "prompt": case["prompt"],
                          "expected": case["expected"], "gates": case["gates"], "must_include": case["must_include"],
                          "must_not": case["must_not"], "rubric": case["grader"].get("rubric"), "answer": r.get("answer", ""),
                          "code_result": ok, "code_gate_failures": gates})
            j = judged.get((r["id"], r.get("run")))
            if j and "judge_pass" in j:
                ok = j["judge_pass"] and ok is not False
                note = f"judge share {j['point_share']}, gates_ok {j['gates_ok']}; {note}"
            elif ok is not None:
                note = "code part only, judge pending; " + note
        per[r["id"]].append({"ok": ok, "gates": gates, "note": note})
    if write_queue:
        QUEUE.write_text("".join(json.dumps(q, ensure_ascii=False) + "\n" for q in queue), encoding="utf-8")
    fam = defaultdict(lambda: [0, 0, 0, 0])
    for cid, rs in per.items():
        scored = [x for x in rs if x["ok"] is not None]
        if not scored:
            continue
        key = (GOLD[cid]["family"], GOLD[cid]["tier"])
        fam[key][0] += sum(bool(x["ok"]) for x in scored)
        fam[key][1] += len(scored)
        fam[key][2] += all(x["ok"] for x in scored)
        fam[key][3] += 1
    if not quiet:
        print(f"{'family':20} {'tier':11} {'pass@1':>7} {'pass^k':>7} cases")
        for (f, t), (p, n, a, c) in sorted(fam.items()):
            print(f"{f:20} {t:11} {p / n:7.0%} {a / c:7.0%} {c:5}")
        tp, tn = sum(v[0] for v in fam.values()), sum(v[1] for v in fam.values())
        ta, tc = sum(v[2] for v in fam.values()), sum(v[3] for v in fam.values())
        if tn:
            print(f"{'all':20} {'':11} {tp / tn:7.0%} {ta / tc:7.0%} {tc:5}")
        for cid, x in [(cid, x) for cid, rs in per.items() for x in rs if x["ok"] is False][:30]:
            print(f"  FAIL {cid}: gates={x['gates']} {x['note']}")
        pending = len([q for q in queue if (q["id"], q["run"]) not in judged])
        print(f"{len(queue)} runs need the judge ({pending} not judged yet) -> {QUEUE.name}; run judge.py, then grade again.")
        stale = stale_cases()
        if stale:
            print(f"WARNING: reference files changed since the gold was built; rebuild before trusting {', '.join(stale)}.")
    return per


def selftest():
    import tempfile
    good, bad = [], []
    for cid, c in GOLD.items():
        e = c["expected"]
        if e["type"] == "rubric":
            continue
        st = {"in_data": False} if e["type"] == "refusal" else {"value": e["value"], "in_data": True}
        for k in range(1, c["runs_k"] + 1):
            good.append({"id": cid, "run": k, "answer": "", "structured": st})
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
        bad.append({"id": cid, "run": 1, "answer": "", "structured": wrong})
    # loose key matching: L03 scenario keys written differently must still pass
    l03 = GOLD["L03"]["expected"]["value"]
    loose = {"id": "L03", "run": 9, "structured": {"value": {"Szenario 1: Energierückgewinnung": list(l03.values())[0], "recycling": list(l03.values())[1]}}}
    for label, rows, want in [("perfect", good + [loose], True), ("corrupted", bad, False)]:
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as fh:
            fh.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
        per = grade(fh.name, write_queue=False, quiet=True)
        res = [x["ok"] for rs in per.values() for x in rs if x["ok"] is not None]
        assert res and all(bool(r) is want for r in res), f"{label}: expected all {want}"
        print(f"{label}: {len(res)} code-graded runs, all {'pass' if want else 'fail'}")
    print("selftest ok")


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else grade(sys.argv[1])
