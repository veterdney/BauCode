"""Strict, standard-library-only contract shared by run_eval.py, grade.py and judge.py.

Trust boundaries: candidate files, judge results and manifests are untrusted input. They are
parsed strictly (no NaN/Infinity, no duplicate JSON keys, no booleans where integers are
expected) and checked against the exact selected case x required-run matrix. Nothing here
calls a network service.
"""
import hashlib, json, math, os, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOLD_PATH = HERE / "golden_v1.jsonl"
CONTRACT_VERSION = "eval-contract-v1"
MANIFEST_SUFFIX = ".manifest.json"
GRADER_METHODS = {"code", "rubric_llm", "code+rubric"}
KNOWN_GATES = frozenset("G-FAB G-UNIT G-SCEN G-D G-DOUBLE G-MIX G-HINDSIGHT G-FALSEABSENT G-OVERCLAIM G-SYCO G-INJECT".split())
GOLD_WARNINGS = []


class ContractError(ValueError):
    """Input that violates the eval contract. Never silently skipped."""


def is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def is_number(x):
    return (is_int(x) or isinstance(x, float)) and not isinstance(x, bool) and math.isfinite(x)


def _reject_constant(name):
    raise ContractError(f"non-finite JSON constant {name} is not allowed")


def _finite_float(text):
    v = float(text)
    if not math.isfinite(v):
        raise ContractError(f"non-finite JSON number {text!r} is not allowed")
    return v


def _no_duplicate_keys(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ContractError(f"duplicate JSON key {k!r}")
        out[k] = v
    return out


def loads_strict(text):
    return json.loads(text, parse_constant=_reject_constant, parse_float=_finite_float,
                      object_pairs_hook=_no_duplicate_keys)


def dumps_canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_text(s):
    return sha256_bytes(s.encode("utf-8"))


def fingerprint(obj):
    return sha256_text(dumps_canonical(obj))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_jsonl(path, label):
    """[(line_number, object)] for every non-blank line; any malformed line raises ContractError."""
    rows = []
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                obj = loads_strict(line)
            except ValueError as exc:
                raise ContractError(f"{label} {path} line {n}: invalid JSON ({exc})") from None
            if not isinstance(obj, dict):
                raise ContractError(f"{label} {path} line {n}: not a JSON object")
            rows.append((n, obj))
    return rows


def write_atomic(path, text):
    """Write text to path via a temp file in the same directory and os.replace (no torn files)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def positive_int(v, what):
    if not is_int(v) or v < 1:
        raise ContractError(f"{what} must be a positive integer, got {v!r}")
    return v


def parse_positive_int_arg(text):
    """argparse type: '3' -> 3; rejects 0, negatives, '1.0', 'true'."""
    import argparse
    t = str(text).strip()
    if not t.isdigit() or int(t) < 1:
        raise argparse.ArgumentTypeError(f"must be a positive integer, got {text!r}")
    return int(t)


def parse_ids_arg(text):
    """'L01,T01' -> ['L01', 'T01']; empty items or duplicates are errors, not ignored."""
    if text is None:
        return None
    ids = [s.strip() for s in str(text).split(",")]
    if not ids or any(not s for s in ids):
        raise ContractError(f"--ids has an empty item: {text!r}")
    if len(set(ids)) != len(ids):
        raise ContractError(f"--ids repeats a case: {text!r}")
    return ids


def load_gold(path=GOLD_PATH):
    del GOLD_WARNINGS[:]
    gold = {}
    for n, c in read_jsonl(path, "gold"):
        cid = c.get("id")
        if not isinstance(cid, str) or not cid:
            raise ContractError(f"gold line {n}: missing or non-string id")
        if cid in gold:
            raise ContractError(f"gold line {n}: duplicate id {cid}")
        positive_int(c.get("runs_k"), f"gold {cid} runs_k")
        if not isinstance(c.get("grader"), dict) or c["grader"].get("method") not in GRADER_METHODS:
            raise ContractError(f"gold {cid}: unknown grader method")
        if not isinstance(c.get("expected"), dict) or not isinstance(c["expected"].get("type"), str):
            raise ContractError(f"gold {cid}: missing expected.type")
        gates = c.get("gates")
        if not isinstance(gates, list) or not all(isinstance(g, str) and g for g in gates):
            raise ContractError(f"gold {cid}: gates must be a list of non-empty strings (an empty list is valid)")
        unknown = sorted(set(gates) - KNOWN_GATES)
        if unknown:
            raise ContractError(f"gold {cid}: unknown gates {unknown}")
        if len(set(gates)) != len(gates):
            # Known defect in golden_v1 (X04 lists G-FAB twice). The committed gold is not edited;
            # the gate is applied once and the defect is reported, not hidden.
            GOLD_WARNINGS.append(f"gold {cid}: duplicate gates {gates} applied once")
            c = dict(c, gates=list(dict.fromkeys(gates)))
        gold[cid] = c
    if not gold:
        raise ContractError(f"gold {path} has no cases")
    return gold


def plan_selection(gold, ids=None, k=None):
    """Selection = ordered case ids and the required runs per case. Validated before any model call."""
    if ids is None:
        ids = list(gold)
    if not isinstance(ids, list) or not ids:
        raise ContractError("selection is empty")
    if any(not isinstance(i, str) for i in ids) or len(set(ids)) != len(ids):
        raise ContractError("selection ids must be unique strings")
    unknown = [i for i in ids if i not in gold]
    if unknown:
        raise ContractError(f"unknown case ids: {', '.join(unknown)}")
    if k is not None:
        positive_int(k, "k")
    return {"ids": list(ids), "k": {i: (k if k is not None else gold[i]["runs_k"]) for i in ids}}


def validate_selection(sel, gold):
    if not isinstance(sel, dict) or set(sel) != {"ids", "k"}:
        raise ContractError("manifest selection must be {'ids': [...], 'k': {...}}")
    plan_selection(gold, sel["ids"])
    if not isinstance(sel["k"], dict) or set(sel["k"]) != set(sel["ids"]):
        raise ContractError("manifest selection k must name exactly the selected ids")
    for cid, v in sel["k"].items():
        positive_int(v, f"manifest k for {cid}")
    return sel


def required_cells(sel):
    return [(cid, run) for cid in sel["ids"] for run in range(1, sel["k"][cid] + 1)]


def manifest_path_for(candidate_path):
    return Path(str(candidate_path) + MANIFEST_SUFFIX)


def runtime_info():
    import platform, sys
    try:
        from importlib import metadata
    except ImportError:  # pragma: no cover
        metadata = None
    pkgs = {}
    for name in ("anthropic", "pandas"):
        try:
            pkgs[name] = metadata.version(name) if metadata else "unknown"
        except Exception:
            pkgs[name] = "not installed"
    return {"python": sys.version.split()[0], "implementation": platform.python_implementation(),
            "platform": platform.platform(), "packages": pkgs}


def git_info(repo):
    import subprocess
    try:
        head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=20)
        dirty = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=no"],
                               capture_output=True, text=True, timeout=20)
        if head.returncode:
            return {"commit": "unavailable"}
        return {"commit": head.stdout.strip(), "tracked_changes": bool(dirty.stdout.strip())}
    except (OSError, subprocess.SubprocessError):
        return {"commit": "unavailable"}