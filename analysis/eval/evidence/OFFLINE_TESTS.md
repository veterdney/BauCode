# Offline test evidence

Run 2026-11-07T17:25:47+01:00 on Windows-11-10.0.26300-SP0, Python 3.14.7, git HEAD at run `01d29520a94680a4f1ff060836341ef01a0d6b1d` (branch `docs/baucode-website-first-20261107`; uncommitted changes to tested sources at run: True).

Machine-readable: [offline_tests.json](offline_tests.json). Regenerate: `python -I analysis/eval/tests/run_offline_evidence.py`.

| Check | Command | Exit |
|---|---|---|
| grader_selftest | `python -I analysis/eval/grade.py --selftest` | 0 |
| unit_tests | `python -I -m unittest discover -s analysis/eval/tests -v` | 0 |
| unit_tests_per_test_json | `python -I analysis/eval/tests/test_eval_contract.py --json analysis/eval/evidence/unit_tests.json` | 0 |
| baseline_probes_original_aee18b | `python -I analysis/eval/tests/baseline_probe_aee18b.py` | 0 |

Unit tests: 32 ok of 32 recorded (32 run by discover).

| Test | Outcome | Failure it guards against |
|---|---|---|
| CodeChecks.test_bool_and_nonfinite_values_fail | ok | bool is not a number and NaN/inf never match. |
| CodeChecks.test_loose_keys_kept_but_collisions_rejected | ok | L03 loose scenario keys stay valid; one candidate key cannot satisfy two gold keys. |
| CodeChecks.test_set_one_to_one_matching | ok | A single generic name used to satisfy several gold names (M09 min_match 2); now one name = one match. |
| CodeChecks.test_single_item_rank_no_crash | ok | kendall() divided by zero for one-item rankings. |
| Judge.test_code_fail_not_rescued_and_code_pass_waits | ok | code+rubric: a code FAIL stays FAIL even with a judge PASS; a code pass alone is PENDING, never PASS. |
| Judge.test_judge_main_rejects_duplicate_queue | ok | A queue with a repeated (id, run) is refused before any judge call. |
| Judge.test_judge_one_fake_client | ok | judge_one records requested+served model; refusal, exceptions, non-JSON, NaN and bad verdicts become errors. |
| Judge.test_judge_results_binding | ok | Valid judge PASS is retained; stale, duplicate, error, served-model-differs and malformed results never pass. |
| Judge.test_threshold_unrounded_and_gate_fail | ok | Share uses exact arithmetic (>= 0.8); any gate FAIL fails. |
| Judge.test_verdict_contract | ok | Exact unique gates/points, integer 0..2 scores (bool rejected), nothing extra. |
| Judge.test_zero_point_policy | ok | No points -> judged on gates only (share 1.0); no gates and no points -> invalid; zero gates with points valid. |
| Matrix.test_complete_valid_runs_retained | ok | Valid complete code-graded runs still PASS and the report is integrity-clean. |
| Matrix.test_duplicate_run_rejected | ok | Duplicate (id, run) records could inflate pass@1; the cell becomes DUPLICATE. |
| Matrix.test_empty_candidate | ok | An empty candidate file is all MISSING, never an empty 'all pass'. |
| Matrix.test_error_refusal_invalid_states | ok | API errors are integrity gaps; refusals are scored failures; malformed records are INVALID. |
| Matrix.test_manifest_model_binding | ok | Under a manifest every record must carry the manifest's requested model and its served models. |
| Matrix.test_missing_run_stays_in_denominator | ok | Old grader counted only supplied rows (1 of 3 runs -> 100%). Missing runs must be visible and non-passing. |
| Matrix.test_reference_checks_fail_visibly | ok | A stale or unavailable reference fingerprint is an integrity problem, not a warning to ignore. |
| Matrix.test_served_model_differs_not_credited | ok | With server-side fallback the served model can differ; such runs must not earn credit. |
| Matrix.test_unknown_and_out_of_range_reported | ok | Unknown ids, run 0/-1/k+1, bool/null/string runs are reported, not silently skipped. |
| Runner.test_cli_exit_codes | ok | grade.py main: 3 = incomplete or unverifiable (no manifest), 0 = complete under a manifest even with scored FAILs, 1 only with --fail-on-fail; --k 0 is a usage error. |
| Runner.test_cli_validation_before_spend | ok | --k 0/-1/true, --workers 0, --max-turns 0 are argparse errors; bad --ids fail planning. |
| Runner.test_offline_end_to_end_no_append | ok | Fake-client run -> manifest -> grade (PASS, integrity clean) -> judge merge; rerun into same --out refused. |
| Runner.test_run_case_records_models_and_errors | ok | Records carry requested+served models; API errors, refusals and missing submits are typed error records. |
| Selection.test_gold_contract | ok | Duplicate gold ids and boolean runs_k are refused; the X04 duplicate gate is reported and applied once. |
| Selection.test_invalid_ids_rejected | ok | Empty, blank, duplicate or unknown ids must fail before any run, not be dropped. |
| Selection.test_invalid_k_rejected | ok | k=0 used to fall back to the full runs_k (cost hazard) and k<0 gave zero jobs; both must be refused. |
| SourceData.test_find_csv_ambiguity_and_provenance | ok | Several matching exports must be refused (was: silently the last); provenance hashes the bytes used. |
| SourceData.test_reference_fingerprint_stdlib_and_missing_file | ok | The reference fingerprint no longer needs pandas, matches the gold, and a missing file raises. |
| StrictJson.test_atomic_write_leaves_no_temp | ok | Outputs are written via temp file + os.replace; no torn or leftover files. |
| StrictJson.test_malformed_candidate_line_is_fatal | ok | A malformed JSONL line is an integrity error with its line number, not a skipped row. |
| StrictJson.test_nonfinite_and_duplicate_keys_rejected | ok | NaN/Infinity/1e999 and duplicate keys must not parse (they could smuggle non-finite scores or shadow fields). |

Original PR9 behaviour reproduced on frozen `aee18b14` sources: 18/18 probes (these confirm the old defects; they are not passes of the new code).

| Probe | Defect | Observed on original |
|---|---|---|
| B01 | missing required runs dropped from denominator | lookup               regression     100%    100%     1 |
| B02 | duplicate (id, run) records counted | 3 entries counted for (L01, run 1) |
| B03 | unknown case skipped / out-of-range run accepted | cases graded: ['L01']; ZZZ silently skipped; run 99 accepted |
| B04 | code+rubric credited before the judge ran | L03 ok=True with no judge result |
| B05 | judge error suppresses pending count; rubric-only None excluded | 1 runs need the judge (0 not judged yet) -> judge_queue.jsonl; run judge.py, then grade again. / D01 ok=None |
| B06 | judge cache keyed only by (id, run) | stale judge result applied: ok=True |
| B07 | duplicate judge results overwrite silently | duplicate cache records: last wins, ok=True |
| B08 | empty/missing gate verdicts pass vacuously | empty gates list -> gates_ok=True, judge_pass=True |
| B09 | duplicate point masks a missing point | point 'a' twice, 'b' missing -> share=1.0, pass=True |
| B10 | out-of-range score not checked locally | score 5 accepted -> share=1.25, pass=True |
| B11 | bool accepted as a number | close(True, 1.0)=True |
| B12 | single-item ranking crashes | ZeroDivisionError on one-item ranking |
| B13 | one reported name satisfies several gold names | M09 (min_match 2) with one generic name -> True |
| B15 | reference check silently skipped when obd_data/pandas cannot import | stale_cases() without pandas -> [] |
| S01 | STATIC: --k 0 falls back to full runs_k; --k -1 yields zero jobs | found |
| S02 | STATIC: reruns append to an existing candidate file | found |
| S03 | STATIC: several exports -> the last one is used silently | found |
| S04 | DATA: X04 lists G-FAB twice and the original accepts it | ['G-FAB', 'G-FAB'] |

## Tested source sha256

- `analysis/eval/contract.py` `c271fc5eb4c7efe79b37a1391dc08aa3d622f89ea063b9c2baf02a02e308ecae`
- `analysis/eval/grade.py` `f5381f10ea0caa3ba007050cb0f77ed975fff6de8f43e782d8462fb74f094ec3`
- `analysis/eval/judge.py` `0f41524e05e940079dd28dce963a6a794bbe512275c4072820720870da9c9ca7`
- `analysis/eval/run_eval.py` `778167d05fd52678398711b1db7d03317c27074f98cc4fad42a3ac112607e0a0`
- `analysis/eval/obd_data.py` `708b84dd824ca997b0e86d7538fb563e4a244c4691cdc1e09ac8a14e304f0a04`
- `analysis/eval/obd_tools.py` `c5e037b63d7f1989e5e204191de7029e1e269efcb060cd57abd76a947b0da44b`
- `analysis/eval/golden_v1.jsonl` `e583be41b73eb03620fbfae2a3ded11cd28dd02d404e75be7f101e663a261e93`
- `analysis/eval/tests/test_eval_contract.py` `4691eff35cd5ea39edf18ea55d1fc5bcd6cad04b8b379d1d5826e9a939e6b2c8`
- `analysis/eval/tests/baseline_probe_aee18b.py` `f2fa21a7da21485c4309517a728c9e5b07c33164ef57185e539a12ae4fe97d13`
- `analysis/eval/tests/run_offline_evidence.py` `eee851529b5041dca1c3a3f568d3f40807cffa9ddbecc14c7a191b627c2cdde8`
- `analysis/results_wall_systems.csv` `0923f08e13b0fba10a25bbbeb5c439a7618c7a139cad4237ea91571b9fb478cc`
- `analysis/results_layers.csv` `cc82a11781885bfde2995c0e4b665c3281bf5a6ebb569f7fe7d634ae25ff5142`
- `analysis/levels/report/scores_alternatives.csv` `e8e420c2ed8e53af8fcdb94d92f09fa75066645e5bb0d464e27d93e0111be208`
- `analysis/levels/report/sensitivity.json` `932b58aeeca034822887ab612b274fbf0284ff60cc6c9203be46727b00ad084c`

## Limits

- Offline self-checks of grading/judging/runner logic with fixtures and fake clients only.
- No real model was run; nothing here measures model accuracy, judge calibration or expert agreement.
- Expected answers in golden_v1 are source-derived proposals, not expert-reviewed GOLD or scientific truth.
- load_obd/ObdTools (pandas) and the 51.5 MB export were not exercised; the full eval is not self-contained.
- Package versions for a live run are not pinned (requirements.txt lists anthropic, pandas unversioned); run manifests record the versions actually installed.
- Model names, the fallback beta and API availability are unverified.

## Full output

### grader_selftest (exit 0)

```text
perfect: 105 code-graded runs pass, 39 code+rubric runs pending judge (never PASS without it)
corrupted: 144 runs, all fail
selftest ok (offline grader self-check only; no model, judge or accuracy claim)
```

### unit_tests (exit 0)

```text
est_error_refusal_invalid_states)
API errors are integrity gaps; refusals are scored failures; malformed records are INVALID. ... ok
test_manifest_model_binding (test_eval_contract.Matrix.test_manifest_model_binding)
Under a manifest every record must carry the manifest's requested model and its served models. ... ok
test_missing_run_stays_in_denominator (test_eval_contract.Matrix.test_missing_run_stays_in_denominator)
Old grader counted only supplied rows (1 of 3 runs -> 100%). Missing runs must be visible and non-passing. ... ok
test_reference_checks_fail_visibly (test_eval_contract.Matrix.test_reference_checks_fail_visibly)
A stale or unavailable reference fingerprint is an integrity problem, not a warning to ignore. ... ok
test_served_model_differs_not_credited (test_eval_contract.Matrix.test_served_model_differs_not_credited)
With server-side fallback the served model can differ; such runs must not earn credit. ... ok
test_unknown_and_out_of_range_reported (test_eval_contract.Matrix.test_unknown_and_out_of_range_reported)
Unknown ids, run 0/-1/k+1, bool/null/string runs are reported, not silently skipped. ... ok
test_cli_exit_codes (test_eval_contract.Runner.test_cli_exit_codes)
grade.py main: 3 = incomplete or unverifiable (no manifest), 0 = complete under a manifest even with ... usage: python.exe -m unittest [-h] [--selftest] [--manifest MANIFEST]
                              [--ids IDS] [--k K] [--judged JUDGED]
                              [--queue QUEUE] [--csv CSV]
                              [--json-out JSON_OUT] [--fail-on-fail]
                              [candidate]
python.exe -m unittest: error: argument --k: must be a positive integer, got '0'
ok
test_cli_validation_before_spend (test_eval_contract.Runner.test_cli_validation_before_spend)
--k 0/-1/true, --workers 0, --max-turns 0 are argparse errors; bad --ids fail planning. ... usage: python.exe -m unittest [-h] [--model MODEL]
                              [--effort {low,medium,high,xhigh,max}]
                              [--ids IDS] [--k K] [--max-turns MAX_TURNS]
                              [--workers WORKERS] [--csv CSV] [--out OUT]
                              [--dry-run]
python.exe -m unittest: error: argument --k: must be a positive integer, got '0'
usage: python.exe -m unittest [-h] [--model MODEL]
                              [--effort {low,medium,high,xhigh,max}]
                              [--ids IDS] [--k K] [--max-turns MAX_TURNS]
                              [--workers WORKERS] [--csv CSV] [--out OUT]
                              [--dry-run]
python.exe -m unittest: error: argument --k: must be a positive integer, got '-1'
usage: python.exe -m unittest [-h] [--model MODEL]
                              [--effort {low,medium,high,xhigh,max}]
                              [--ids IDS] [--k K] [--max-turns MAX_TURNS]
                              [--workers WORKERS] [--csv CSV] [--out OUT]
                              [--dry-run]
python.exe -m unittest: error: argument --k: must be a positive integer, got 'true'
usage: python.exe -m unittest [-h] [--model MODEL]
                              [--effort {low,medium,high,xhigh,max}]
                              [--ids IDS] [--k K] [--max-turns MAX_TURNS]
                              [--workers WORKERS] [--csv CSV] [--out OUT]
                              [--dry-run]
python.exe -m unittest: error: argument --workers: must be a positive integer, got '0'
usage: python.exe -m unittest [-h] [--model MODEL]
                              [--effort {low,medium,high,xhigh,max}]
                              [--ids IDS] [--k K] [--max-turns MAX_TURNS]
                              [--workers WORKERS] [--csv CSV] [--out OUT]
                              [--dry-run]
python.exe -m unittest: error: argument --max-turns: must be a positive integer, got '0'
ok
test_offline_end_to_end_no_append (test_eval_contract.Runner.test_offline_end_to_end_no_append)
Fake-client run -> manifest -> grade (PASS, integrity clean) -> judge merge; rerun into same --out refused. ... ok
test_run_case_records_models_and_errors (test_eval_contract.Runner.test_run_case_records_models_and_errors)
Records carry requested+served models; API errors, refusals and missing submits are typed error records. ... ok
test_gold_contract (test_eval_contract.Selection.test_gold_contract)
Duplicate gold ids and boolean runs_k are refused; the X04 duplicate gate is reported and applied once. ... ok
test_invalid_ids_rejected (test_eval_contract.Selection.test_invalid_ids_rejected)
Empty, blank, duplicate or unknown ids must fail before any run, not be dropped. ... ok
test_invalid_k_rejected (test_eval_contract.Selection.test_invalid_k_rejected)
k=0 used to fall back to the full runs_k (cost hazard) and k<0 gave zero jobs; both must be refused. ... ok
test_find_csv_ambiguity_and_provenance (test_eval_contract.SourceData.test_find_csv_ambiguity_and_provenance)
Several matching exports must be refused (was: silently the last); provenance hashes the bytes used. ... ok
test_reference_fingerprint_stdlib_and_missing_file (test_eval_contract.SourceData.test_reference_fingerprint_stdlib_and_missing_file)
The reference fingerprint no longer needs pandas, matches the gold, and a missing file raises. ... ok
test_atomic_write_leaves_no_temp (test_eval_contract.StrictJson.test_atomic_write_leaves_no_temp)
Outputs are written via temp file + os.replace; no torn or leftover files. ... ok
test_malformed_candidate_line_is_fatal (test_eval_contract.StrictJson.test_malformed_candidate_line_is_fatal)
A malformed JSONL line is an integrity error with its line number, not a skipped row. ... ok
test_nonfinite_and_duplicate_keys_rejected (test_eval_contract.StrictJson.test_nonfinite_and_duplicate_keys_rejected)
NaN/Infinity/1e999 and duplicate keys must not parse (they could smuggle non-finite scores or shadow fields). ... ok

----------------------------------------------------------------------
Ran 32 tests in 0.295s

OK
```

### unit_tests_per_test_json (exit 0)

```text

```

### baseline_probes_original_aee18b (exit 0)

```text
{
 "base_commit": "aee18b149c47e7b6851f946dc2383b997675cbcf",
 "frozen_sources_sha256": {
  "grade.py": "dc688616f5d43782962f595fb52625772dfe3f6d1ea96ced912bc8322bfeee00",
  "judge.py": "299bddce933bf9366f1ae4c42156e689c49f691238645b97e97cffed9ddbbfa5",
  "run_eval.py": "6b2f38233d73ac75a4eea9a0b3db5e0d84f3bace8db911162b6fc679f87424e3",
  "obd_data.py": "1bc40b388b4049e86ed4788b56c85894cc948157bb542878e4e1d58a713ee5fa",
  "golden_v1.jsonl": "e583be41b73eb03620fbfae2a3ded11cd28dd02d404e75be7f101e663a261e93"
 },
 "probes": [
  {
   "id": "B01",
   "purpose": "missing required runs dropped from denominator",
   "expected_original_behaviour": "1 of 3 required L01 runs reports pass@1 and pass^k 100%",
   "observed": "lookup               regression     100%    100%     1",
   "reproduced": true
  },
  {
   "id": "B02",
   "purpose": "duplicate (id, run) records counted",
   "expected_original_behaviour": "three copies of run 1 count as three runs",
   "observed": "3 entries counted for (L01, run 1)",
   "reproduced": true
  },
  {
   "id": "B03",
   "purpose": "unknown case skipped / out-of-range run accepted",
   "expected_original_behaviour": "no error for unknown id or run 99",
   "observed": "cases graded: ['L01']; ZZZ silently skipped; run 99 accepted",
   "reproduced": true
  },
  {
   "id": "B04",
   "purpose": "code+rubric credited before the judge ran",
   "expected_original_behaviour": "code part pass alone yields ok=True (counted as pass)",
   "observed": "L03 ok=True with no judge result",
   "reproduced": true
  },
  {
   "id": "B05",
   "purpose": "judge error suppresses pending count; rubric-only None excluded",
   "expected_original_behaviour": "error record counts as judged; D01 dropped from scoring",
   "observed": "1 runs need the judge (0 not judged yet) -> judge_queue.jsonl; run judge.py, then grade again. | D01 ok=None",
   "reproduced": true
  },
  {
   "id": "B06",
   "purpose": "judge cache keyed only by (id, run)",
   "expected_original_behaviour": "a judge pass for any other answer/model is applied",
   "observed": "stale judge result applied: ok=True",
   "reproduced": true
  },
  {
   "id": "B07",
   "purpose": "duplicate judge results overwrite silently",
   "expected_original_behaviour": "FAIL then PASS for the same key -> PASS",
   "observed": "duplicate cache records: last wins, ok=True",
   "reproduced": true
  },
  {
   "id": "B08",
   "purpose": "empty/missing gate verdicts pass vacuously",
   "expected_original_behaviour": "all([]) is True: G-FAB never checked",
   "observed": "empty gates list -> gates_ok=True, judge_pass=True",
   "reproduced": true
  },
  {
   "id": "B09",
   "purpose": "duplicate point masks a missing point",
   "expected_original_behaviour": "duplicating one point fills the share",
   "observed": "point 'a' twice, 'b' missing -> share=1.0, pass=True",
   "reproduced": true
  },
  {
   "id": "B10",
   "purpose": "out-of-range score not checked locally",
   "expected_original_behaviour": "score 5 yields share > 1 and a pass",
   "observed": "score 5 accepted -> share=1.25, pass=True",
   "reproduced": true
  },
  {
   "id": "B11",
   "purpose": "bool accepted as a number",
   "expected_original_behaviour": "True matches 1.0",
   "observed": "close(True, 1.0)=True",
   "reproduced": true
  },
  {
   "id": "B12",
   "purpose": "single-item ranking crashes",
   "expected_original_behaviour": "ZeroDivisionError",
   "observed": "ZeroDivisionError on one-item ranking",
   "reproduced": true
  },
  {
   "id": "B13",
   "purpose": "one reported name satisfies several gold names",
   "expected_original_behaviour": "single name passes a two-match case",
   "observed": "M09 (min_match 2) with one generic name -> True",
   "reproduced": true
  },
  {
   "id": "B15",
   "purpose": "reference check silently skipped when obd_data/pandas cannot import",
   "expected_original_behaviour": "returns [] (no warning)",
   "observed": "stale_cases() without pandas -> []",
   "reproduced": true
  },
  {
   "id": "S01",
   "purpose": "STATIC: --k 0 falls back to full runs_k; --k -1 yields zero jobs",
   "expected_original_behaviour": "source uses (a.k or c['runs_k'])",
   "observed": "found",
   "reproduced": true
  },
  {
   "id": "S02",
   "purpose": "STATIC: reruns append to an existing candidate file",
   "expected_original_behaviour": "source opens out with mode 'a'",
   "observed": "found",
   "reproduced": true
  },
  {
   "id": "S03",
   "purpose": "STATIC: several exports -> the last one is used silently",
   "expected_original_behaviour": "source returns hits[-1]",
   "observed": "found",
   "reproduced": true
  },
  {
   "id": "S04",
   "purpose": "DATA: X04 lists G-FAB twice and the original accepts it",
   "expected_original_behaviour": "duplicate gate in gold",
   "observed": "['G-FAB', 'G-FAB']",
   "reproduced": true
  }
 ],
 "reproduced": 18,
 "total": 18,
 "note": "Shows the ORIGINAL behaviour only; S01-S03 are source inspection, not execution."
}
```

