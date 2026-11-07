# Golden eval set: alternative-material construction comparison

A task evaluation set for an AI agent that compares building materials and structural systems from Ökobaudat data,
the way the analyses in this repository do.
It measures whether the agent can be trusted with that task:
getting the numbers right,
handling dirty data,
saying "not in the data" instead of inventing,
and advising developers without overclaiming.

72 cases, version `v1`, data frozen at **2026-11-07**.

## Files

| File | What it is |
|---|---|
| `golden_v1.jsonl` | The cases, one JSON object per line |
| `golden_v1.csv` | The same cases flattened, for a spreadsheet |
| `build_golden.py` | Regenerates the set; every computable gold value is computed from the sources, not typed in |
| `obd_data.py` | Loads the frozen export and fingerprints the reference files |
| `obd_tools.py` | Read-only data tools for the agent under test |
| `run_eval.py` | Runs the agent on the cases and writes a candidate file |
| `grade.py` | Code grader, pass@1 and pass^k report, judge queue; `--selftest` checks the set against itself |
| `judge.py` | LLM judge for the rubric half; its verdicts merge back into `grade.py` |
| `rubrics.md` | Gates, rubrics, judge prompt and calibration plan (`judge.py` holds the exact prompt used) |
| `contract.py` | Strict, standard-library checks shared by the runner, grader and judge |
| `tests/` | Offline adversarial and regression tests, and probes of the original PR9 behaviour |
| `evidence/` | Recorded results of those offline checks: [OFFLINE_TESTS.md](evidence/OFFLINE_TESTS.md), [offline_tests.json](evidence/offline_tests.json) |

## Sources (frozen)

1. Ökobaudat 2024-II export of 2026-11-07: 44,973 rows, 4,308 datasets, `;`-separated, cp1252.
   It is not committed (51.5 MB); put it at `data/OBD_2024_II_<timestamp>.csv` as for the other analyses, or pass `--csv`.
   The scripts refuse any other row count, and refuse to guess when several exports match.
   The row count is not an identity check: `run_eval.py` records the export's sha256, size and rows in the run manifest.
   No canonical hash is published, so that shows which bytes were used, not that they are the authentic export;
   origin and licence are recorded as unknown.
   `analysis/extract.py` reads the same export as latin-1; strings with bytes 0x80–0x9F can differ between the two.
2. The reference analysis in this repository: `analysis/results_*.csv` and `analysis/levels/report/`.
   Cases that read them carry a `reference_fingerprint`.
   If those files are re-run, `grade.py` warns and names the cases to rebuild.
3. The criteria-coverage analysis (developer and architect criteria against the scoring lab) for the decision cases.

Nothing after the freeze date may be used.
Asking for it is itself a test (M11, T06).

## What the set covers

| Family | Cases | Tier | Grading | What it catches |
|---|---|---|---|---|
| lookup | 10 | regression | code | wrong column, module or sign; counting rows as products |
| unit_conversion | 8 | regression | code | per kg vs m³ vs m²; reference quantity ≠ 1 (VOLCALITE is declared per 1,000 kg) |
| data_trap | 10 | regression (1 capability) | gate + code or judge | outliers (an aluminium profile at 41,671 kg CO₂e/kg), cladding panels in the insulation category, summed scenarios, A1/A2/A3 double counting, A1 vs A2 indicator mixing, expiry, module D in the headline, piece-based units |
| missing_data | 11 | 9 regression, 2 capability | gate + code | invented fire classes, Rw, VOC, cost, λ, service life, building location, steel studs; and the reverse, false absence |
| assembly_calc | 9 | regression | code | forgotten replacements, module D added, wrong replacement count |
| ranking | 8 | regression | code (exact order, Kendall tau as partial credit) or judge | ranking by carbon alone; lowest A1–A3 taken as lowest life cycle |
| decision_reasoning | 10 | capability | judge | confident, plausible but wrong advice to a developer or architect |
| adversarial | 6 | regression | judge | sycophancy, module-D pressure, marketing overclaim, false premise, injected instruction in data |

35 cases are graded by code alone, 13 by code plus a judge, 24 by the judge alone.
At the default `runs_k`, one full pass is 248 agent runs.
Regression cases should sit near 100 %; a drop is an alarm.
Capability cases are the hill to climb; when one saturates it moves into the regression suite.

## How it follows the eval principles

- **Define done before running.**
  Every case carries `expected` (type, value or rubric points, unit, tolerance), the `failure_mode` it targets and its `provenance`.
- **Gate first, then grade.**
  Routes that are never acceptable fail the run outright: fabricated numbers, unit errors, module D in the headline, summed scenarios, injected instructions.
  See `rubrics.md`.
- **Hallucination under missing data.**
  11 cases ask for things the export does not hold.
  The right answer is "not in the data" plus a real next step.
- **The reverse check.**
  M09 and M10 ask for things that are there.
  `07-product-selection.md` and `08-limitations-next-steps.md` say the export has no CLT panels; it has five CLT datasets and three hemp blocks and panels.
  The gold follows the data, so an agent that repeats the reference fails.
- **Frozen at the decision date.**
  The tools serve only the 2026-11-07 export and the repository files; there is no web access.
- **Run many times.**
  `runs_k` is 5 for the decision and adversarial cases and 3 for the rest.
  Report pass^k next to pass@1: a 75 % agent passes three runs in a row only 42 % of the time,
  and a developer acting on one answer needs it right every time.
- **Strict judge.**
  0/1/2 per point, binary gates, structured output, and a calibration step against expert labels (≥ 85 % agreement) before judge scores count.
- **Evals are code.**
  The set is built by a script from frozen sources, so a reviewer can diff it, rerun it and trace every gold value.

## The agent under test

`run_eval.py` gives the agent four read-only tools over the frozen sources and nothing else:

| Tool | Returns |
|---|---|
| `search_datasets` | datasets whose name or category matches, with declared quantity, unit, densities, validity |
| `get_dataset` | all metadata and every module row of one dataset, as declared |
| `category_values` | one indicator for one module across a category, as declared |
| `read_repo_file` | files under `analysis/` (not `analysis/eval/`) and the material property dataset |

The tools do no arithmetic, plausibility filtering or unit conversion, because those are what the cases test.
The gold files are not readable by the agent.
Each run ends with `submit_answer`, which carries the free-text answer and a structured block:

```json
{"id": "U03", "run": 1, "answer": "…", "structured": {"value": 4.09, "in_data": true}}
```

Each case's `answer_format` tells the agent the shape of `value` without giving the answer away.
Missing-data cases get the same kind of hint as answerable ones.

Defaults: `claude-opus-5-5` at effort `high`, server-side refusal fallback on (`fallbacks: "default"`).
A refusal that survives the fallback counts as a failed run.
The full trajectory of every run (tool calls, turns, tokens) is kept in the candidate file for path review.

## Run it

From the repository root, after `pip install -r analysis/eval/requirements.txt` and with Claude API credentials set:

```bash
python3 -I analysis/eval/grade.py --selftest
```

```bash
python3 -I analysis/eval/run_eval.py --ids L01,T01,M09,D01 --k 1 --out analysis/eval/runs/smoke.jsonl
```

```bash
python3 -I analysis/eval/grade.py analysis/eval/runs/smoke.jsonl
```

```bash
python3 -I analysis/eval/judge.py
```

```bash
python3 -I analysis/eval/grade.py analysis/eval/runs/smoke.jsonl
```

The second `grade.py` call merges the judge's verdicts.
`run_eval.py` writes `<out>.manifest.json` next to the candidate file; `grade.py` reads it to know the required runs.
`run_eval.py --dry-run` prints the first request and the number of runs without calling the API.
To rebuild the set after the reference analysis changes: `python3 -I analysis/eval/build_golden.py`.

Every run costs money.
Start with the smoke run above, look at the trajectories, then run the full set.

## Grading contract (fail-closed)

The grader and judge treat candidate files, judge results and manifests as untrusted input.
Each rule below has an offline test in [`tests/test_eval_contract.py`](tests/test_eval_contract.py);
the recorded results, commands, exit codes, runtime and tested-source sha256 are in [`evidence/OFFLINE_TESTS.md`](evidence/OFFLINE_TESTS.md).

- **Exact run matrix.** Every selected case × run 1..k gets one state. Missing, duplicate, unknown or out-of-range records are reported and never dropped from the denominator. `--k`, `--workers` and `--max-turns` must be positive integers; `--ids` must be unique known ids. All checked before any model call.
- **States.** PASS, FAIL and REFUSAL are scored results. MISSING, DUPLICATE, INVALID, ERROR, PENDING_JUDGE, JUDGE_ERROR and SERVED_MODEL_DIFFERS are integrity gaps. Only PASS earns credit.
- **Every gate counts.** A code+rubric run passes only if the code check and the judge both pass; a failed code check is not rescued by the judge. A code pass alone stays PENDING_JUDGE.
- **Judge verdicts.** Each case gate and each point (`P1`…`Pn`) must appear exactly once. Scores must be the integers 0, 1 or 2 (no booleans). The share is computed unrounded against 0.8. A case with no points is judged on its gates alone; a case with neither is invalid. `grade.py` re-validates the stored verdict rather than trusting a stored `judge_pass`.
- **Judge results are bound.** Each result carries the binding of the run it judged: answer and structured-value hashes, candidate requested and served models and config, case fingerprint, reference fingerprint and judge-prompt hash. It also carries the judge's requested and served model. Stale, duplicate or malformed results are rejected.
- **Run manifest required.** It must carry the exact candidate config (requested model, effort, max_turns) and a valid source identity (export sha256, filename, size, rows). Every record must match that config exactly. The source sha256 is part of each judge binding, so a source-only change makes earlier judge results stale. `grade.py --csv` re-verifies the bytes when the export is available. No canonical export hash is assumed.
- **Served model.** The server-side fallback can answer with another model. Runs record `served_models`, and runs served by a model other than the requested one earn no credit.
- **Strict JSON.** No NaN, Infinity or overflowing numbers like `1e999`, and no duplicate keys. `in_data` must be `true`, `false` or `null` by identity (0/1 are rejected). Malformed lines stop grading with a line number.
- **Name matching.** An exact normalized match wins. A loose match (one contains the other, shorter side ≥ 4 characters) must be unique, and one reported name or key can satisfy only one gold item. This is a deliberate change. One generic name no longer satisfies several gold names (M09), but the loose scenario keys of L03 still pass.
- **No silent appends.** `run_eval.py` streams to an exclusively created `<out>.partial` and renames it to `<out>` when done; it refuses an existing output. Queue, judge results, manifest and JSON report are written atomically.
- **Reference files.** A missing or changed reference fingerprint is an integrity failure, not a warning. The fingerprint no longer needs pandas.
- **Exit codes.** `grade.py` exits 0 only when every required run is scored and nothing is stale or unverifiable (a run manifest is required). It exits 3 on any integrity gap. Scored FAILs are results; `--fail-on-fail` turns them into exit 1.
- **Known gold defect.** X04 lists `G-FAB` twice. The committed gold is not edited; the gate is applied once and reported as a gold warning.

## Limits of this version

- **The rubric points are not yet expert-reviewed.**
  The numeric gold is computed and self-tested.
  The points for the decision and adversarial cases should be reviewed by an LCA practitioner or architect before judge scores are trusted.
- **The judge defaults to Claude Sonnet 5.5**, the same model family as the candidate.
  Same-family judges favour their own outputs; `judge.py` warns.
  Calibrate it against about 120 hand-labelled transcripts, or swap in a judge from another family.
- **No real model has been run yet.**
  The runner, grader and judge were exercised end to end with a mock client only.
  The 72 cases are source-derived proposed cases. The grader self-checks and offline tests with fake clients are recorded, but there are no real-model results and no calibrated, independent expert validation. No aggregate accuracy or pass^k claim is made.
- **The full run is not self-contained.**
  It needs the absent 51.5 MB export and pandas; `load_obd` and the data tools are not covered by the offline tests.
  `requirements.txt` does not pin versions; run manifests record the installed versions.
  Model names, the fallback beta and API availability are unverified.
- **Assembly and ranking cases test reproduction of the lab's method**, not ground truth about buildings.
- **Property-dataset values are not numeric gold.**
  The dataset tags them ASSUMED or TYPICAL, so they appear only as context.
- **No cost, schedule, fire or acoustic gold**, because no trusted source exists in the inputs.
  Those topics appear only as missing-data and decision cases.

## Keeping it alive

- Turn every production failure into a case, and rerun the full set on every model or prompt change.
- When a capability case passes reliably, move it to the regression tier.
- Next additions: pairwise cases (two reports for the same brief), trajectory checks (did the agent filter categories before a median, did it check units before converting), an office typology once the lab supports it.
