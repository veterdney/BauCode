# Exact-20 synthetic regression — evidence report

Base commit `f3575fb2d00bcce0a5ba9c1cc576d198da0c8c1e`, branch `review/baucode-verified-20261107`.
All changes are **uncommitted** in the working tree.
Recreated from remote main and the task spec; no earlier patches or logs were used.
Python 3.14 on Windows 11; stdlib only, nothing installed.

These are 20 **exposed SYNTHETIC regression cases** (no holdout, no GOLD set, no statistics).
They are a new case set and are not comparable with any earlier one.
Expected constants are **agent hand-derived (claude-opus-5-5), not human-reviewed**.
A PASS means "the code returns the hand-derived constant for this invented input";
it is not scientific validation and supports no accuracy rate.

## Order of work (freeze before tuning)

1. Captured the original `python analysis/run.py` failure → `review-evidence/baseline_run_py.json` (exit 1, `FileNotFoundError: analysis/products.csv` from `lib.py:2`).
2. Wrote demo inputs and hand-derived expected files, then `tests/exact20_manifest.json`.
   Froze it: sha256 `6911268bde11377778f571f6f43dfa25a99ab5afe84ce295f2de4f37d1e26ecc` (CRLF→LF normalised) in `tests/exact20_manifest.sha256` and `review-evidence/frozen_manifest_hash.json`, together with the original `lib.py`/`model.py`/`run.py` hashes.
3. Wrote `tests/run_exact20.py` against the planned API (new surfaces report NOT RUN until they exist) and ran it on the **untouched** production code → `tests/results_before.json`, sha256 `f696964146ea8f1dc416e5a0d8c2c5a247df3d1dd742ef74fc274fb2fd04f669` (`review-evidence/results_before_hash.json`).
4. Only then changed production code and wrote the demo.
5. Ran the **same harness file** (sha256 `f560546099f948dac81653aac25174eb591e253d4724b53717cb4c4ba1653212`, unchanged since step 3) → `tests/results_after.json`.

The manifest was never edited after freezing; there are no adjudications (`tests/exact20_adjudications.json` does not exist).

## How the baseline exercised original code

The original `lib.py` reads `analysis/products.csv` at import, so `import lib` fails.
Without monkeypatching and without creating a products.csv,
the harness executes the **function definitions only** of the original source (`ast` extraction of `per_m3`, `per_m3_val`, `per_m2`, `norm`)
and records that path on each probe (`"path": "ast-extracted original source ..."`).
Probes that need the importable module or a not-yet-existing surface are NOT RUN with the reason recorded.
C18 reads the legacy expression from `run.py` source in both runs.

## Results: before vs after (same cases, same harness, same oracle)

Case status = worst blocking member (FAIL > NOT RUN > UNKNOWN > PASS).
"nb" = non-blocking member, always listed.

| case | topic | before | after | non-blocking members (after) |
|---|---|---|---|---|
| C01 | q1 × 10 = 10; importable without data | FAIL (import FAIL; per_m2 PASS) | PASS | |
| C02 | 5 m2 / q2 × 10 = 25 | FAIL (area path returned 10, not 5) | PASS | cap_units UNKNOWN |
| C03 | blank q invalid | FAIL (per_m3 1.0; area 10) | PASS | |
| C04 | zero q invalid | FAIL (per_m3 1.0; area 10) | PASS | |
| C05 | −2 / nan / +inf / −inf invalid | FAIL (−0.5, nan, 0.0, −0.0) | PASS | |
| C06 | unsupported units | NOT RUN (per_m3 already None = PASS; demo absent) | PASS | |
| C07 | kg 3/2 × 400 = 600 | NOT RUN (per_m3_val PASS; demo absent) | PASS | |
| C08 | density 200 → 300, single factor | NOT RUN (4 production probes PASS; demo absent) | PASS | |
| C09 | m3 10/2 × 0.1 = 0.5 | NOT RUN (per_m2 PASS; demo absent) | PASS | |
| C10 | 100 mm, 1 m2, 400 → 40 kg | NOT RUN (no conversion surface) | PASS | |
| C11 | 0 and −3 × 2 → 0, −6 | NOT RUN (per_m2 PASS; demo absent) | PASS | |
| C12 | empty pool UNKNOWN | NOT RUN | PASS | |
| C13 | C known 7, C3 missing, D unknown | NOT RUN | PASS | legacy_d_coerced_zero PASS (characterization) |
| C14 | aggregate 10 vs 2+3+5, D −2 separate | NOT RUN (per_m2 PASS) | PASS | |
| C15 | scenario conflict rejected | NOT RUN | PASS | legacy_extract_scenario UNKNOWN |
| C16 | B4 no double count | NOT RUN | PASS | reconciliation NOT RUN |
| C17 | median 3 / 2; tie norm 0.5 | NOT RUN (norm PASS) | PASS | |
| C18 | `pert and penrt` characterization | PASS | PASS | intended_formula UNKNOWN |
| C19 | rendered SYNTHETIC claims | NOT RUN (originals_unchanged PASS) | PASS | legacy_health_finding UNKNOWN |
| C20 | CLI invalid input → exit 2, no numbers | NOT RUN | PASS | injection NOT RUN |

Counts (from the results files, 86 probes in total):

| run | cases PASS / FAIL / UNKNOWN / NOT RUN | blocking probes PASS / FAIL / UNKNOWN / NOT RUN | non-blocking PASS / FAIL / UNKNOWN / NOT RUN | harness exit |
|---|---|---|---|---|
| before (original code) | 1 / 5 / 0 / 14 | 19 / 10 / 0 / 50 | 0 / 0 / 4 / 3 | 1 |
| after (patched) | 20 / 0 / 0 / 0 | 79 / 0 / 0 / 0 | 1 / 0 / 4 / 2 | 0 |
| fault proof (after + hook) | 19 / 1 / 0 / 0 | 77 / 2 / 0 / 0 | 1 / 0 / 4 / 2 | 1 |

The "after" line is 20 PASS **cases** on blocking probes, with 4 UNKNOWN and 2 NOT RUN non-blocking members that remain open.
It is not "20/20 validated".
(In the baseline, `C13.legacy_d_coerced_zero` was NOT RUN; it appears under after as the single non-blocking PASS.)

### Open UNKNOWN / NOT RUN (non-blocking, by policy)

| member | status | why it stays open |
|---|---|---|
| C02.cap_units | UNKNOWN | unit intent of the legacy `abs(a13)<200` area cap is undocumented; cap unchanged |
| C15.legacy_extract_scenario | UNKNOWN | `extract.py:17-20` drops scenario labels; needs the OBD export to exercise |
| C16.reconciliation | NOT RUN | no surface reconciles declared B4 with recalculated replacements; not invented |
| C18.intended_formula | UNKNOWN | intent of `r['pert'] and r['penrt']` unknown; expression unchanged (and `s4` is unused) |
| C19.legacy_health_finding | UNKNOWN | legacy "preferred"/health scores unvalidated; historical finding inaccessible; handoff only, not relabelled |
| C20.injection | NOT RUN | not applicable: deterministic CLI, no model/LLM input surface; none manufactured |

A characterization PASS (C08 fallbacks, C13 legacy D→0, C16, C18) asserts current behaviour only.
C13's legacy D→0 coercion is characterized, not endorsed.

## Tolerance

`math.isclose(rel_tol=1e-9, abs_tol=1e-9)` for numbers; exact match for exit codes, booleans, codes, strings, nulls and lists.
Inputs are short decimals combined by at most four multiplications/divisions, so float64 error is ~1e-15 relative;
every targeted defect (default to 1, ignored q, double density, 1000× unit slip, sign flip, double count) moves a value by ≥ 1e-2 relative.

## Production changes and the failing probe each one answers

| file | change | answers |
|---|---|---|
| `analysis/lib.py` | `ROWS` loaded lazily by `all_rows()`; `select(..., rows=None)` | C01.import FAIL |
| `analysis/lib.py` | `ref_quantity()` + `per_m3_checked()`; `per_m3` no longer does `f(q) or 1` | C03/C04/C05 FAIL |
| `analysis/lib.py` | unused `Umrechungsfaktor auf 1kg` lookup removed (it was never applied) | none (dead code; C08 shows a single density factor before and after) |
| `analysis/lib.py` | `to_metres()`, `layer_mass_kg()` | C10 NOT RUN (no surface) |
| `analysis/model.py` | `per_m2` area path divides by the declared q | C02.per_m2_area FAIL |
| `analysis/model.py` | `rows=` threaded through `sel/cand/layer_stats/assess` | C12/C13/C16/C17 NOT RUN |
| `analysis/model.py` | `pool_median()` (also used by `assess`, legacy 0.0 kept for no data) | C12/C17 |
| `analysis/model.py` | `layer_stats` adds `c_modules`, `d_known`; `assess` adds `complete`, `missing_layers` (numbers unchanged) | C12/C13 |
| `analysis/model.py` | `module_breakdown()` (A1-A3 overlap policy, C coverage, D separate) | C13/C14 |
| `analysis/run.py` | pipeline wrapped in `main()` + `__main__` guard; `git diff -w` shows only those lines | C17.norm importable |
| `demo/run_demo.py` | new demo (validation, pool, totals, rendering) on the production functions above | C01–C20 demo probes |

`python analysis/run.py` still fails exactly as the baseline did (`FileNotFoundError: analysis/products.csv`, now raised from `lib.py:5` on first use) — `review-evidence/cmd_run_py_after_patch.json`, exit 1.
No products.csv was created and no legacy ranking was repaired.

## Deliberately failing run (harness can fail)

`python tests/run_exact20.py --out tests/results_faultproof.json --label faultproof-C07-density-x2 --fault-hook C07-density-x2`
doubles the **actual input** density for C07 only (oracle untouched, manifest hash unchanged in the output).
Result: C07 FAIL (`per_m3_val` 1200 vs 600; demo `layers.0.a13` 1200 vs 600), exit **1**.
Evidence: `tests/results_faultproof.json`, `review-evidence/cmd_faultproof.json`.

## Demo evidence

| command | exit | evidence |
|---|---|---|
| `python demo/run_demo.py` | 0 (185; matches 23 hand values) | `review-evidence/cmd_demo_default.json` |
| `python demo/run_demo.py --input demo/input/synthetic_wall_replaced.json --out demo/output/replaced` | 0 (230; matches 17 hand values) | `review-evidence/cmd_demo_replaced.json` |
| same with `--input demo\input\synthetic_wall_replaced.json` | 0; byte-identical outputs | `review-evidence/cmd_demo_replaced_backslash.json`, `review-evidence/path_check_hashes.json` |
| default input checked against the replaced expected file | 4 (mismatches listed) | `review-evidence/cmd_demo_expected_mismatch.json` |
| harness asked to overwrite `results_before.json` | 3 (refused) | `review-evidence/cmd_harness_before_refuses_overwrite.json` |

C19 additionally checks in-harness: forward-slash, absolute and backslash spellings give byte-identical `result.json`/`layers.csv`/`report.md`.

## Hashes

All sha256, in `review-evidence/final_hashes.json`:
manifest `6911268b…26ecc`, results_before `f6969641…0f669`, results_after `0de58287…80fee`, results_faultproof `a5c004d9…1757d`,
harness `f5605460…53212`.

## Unresolved issues (handoff)

1. `analysis/compare6/compare6.py:65` and `analysis/levels/engine.py:14` still use `f(Bezugsgroesse) or 1` — the same default-to-1 defect on separate legacy paths; not covered by the 20 cases and untouched.
2. Legacy `assess`/`layer_stats` still coerce undeclared D and empty medians to 0.0 and still produce a numeric `life_gwp` for walls with missing layers (now flagged by `complete`/`missing_layers`); `run.py` would still rank them.
3. The q fixes (no default 1; area path ÷ q) would change legacy results for any products.csv rows with blank/0/non-finite q or area rows with q ≠ 1. The size of that effect on the published reports is UNKNOWN; reports were not regenerated and are unchanged.
4. `lib.dens` does not reject nan/negative densities and falls back to bulk density when Rohdichte is 0; only the demo validates its own density input.
5. `extract.py` compares versions as strings (`meta[u]['Version']>v`); noticed, not tested.
6. `run.main()` has not been executed end-to-end after the refactor (needs products.csv); the change is indentation-only per `git diff -w`.
7. `tests/results_before.json` could not be set read-only (needed approval); it is protected by its recorded hash and by the harness refusing to overwrite (exit 3).
8. `analysis/__pycache__/` exists from the first baseline `run.py` invocation; it is untracked, now in `.gitignore`, and was not deleted.
9. `review-evidence/` already contained `task.txt` and `claude-recreation.*` (task text and raw runtime stream). They are not deliverables and should stay out of any commit.

## Final checkpoint (after gallery expansion)

Same session and branch, still uncommitted.
The expansion added files only; production code (`analysis/lib.py`, `model.py`, `run.py`), `demo/run_demo.py`, the harness, the manifest,
`results_before.json` and `results_after.json` are hash-identical to the previous checkpoint (`review-evidence/final2_hashes.json`).

### Exact-20 rerun (unchanged harness, new file)

`python tests/run_exact20.py --out tests/results_final.json --label final-after-gallery-expansion` → exit **0**
(`review-evidence/cmd_harness_final.json`; results sha256 `2d8a98b6…4d99d`; manifest `6911268b…26ecc` unchanged).

| | PASS | FAIL | UNKNOWN | NOT RUN |
|---|---|---|---|---|
| cases (blocking members) | 20 | 0 | 0 | 0 |
| blocking probes | 79 | 0 | 0 | 0 |
| non-blocking probes | 1 | 0 | 4 | 2 |

The 20 PASS cases cover blocking probes only.
They do not settle policy or real-world validity, and these stay open:
C02 cap units UNKNOWN, C15 legacy extract scenario UNKNOWN, C16 B4 reconciliation NOT RUN (alongside a C16 characterization PASS and an actual B4 rejection PASS),
C18 intended formula UNKNOWN (characterization PASS only), C19 legacy health finding UNKNOWN, C20 injection NOT RUN (not applicable).

### Incorrect-input detection inside the fixed 20 (descriptive, not an accuracy rate)

`python tests/confusion_exact20.py tests/results_final.json --out tests/detection_metrics_final.json` (read-only over the results file; exit 0).
Positive = an input the frozen manifest expects to be REJECTED; only the 33 end-to-end demo decision probes are counted.

| run | expected positive | TP | FN | not executed | expected negative | TN | FP | abstained | not executed |
|---|---|---|---|---|---|---|---|---|---|
| before | 15 | 0 | 0 | 15 | 18 | 0 | 0 | 0 | 18 |
| final | 15 | 15 | 0 | 0 | 18 | 15 | 0 | 3 | 0 |

"Abstained" = expected-valid input evaluated as `INCOMPLETE_LAYERS` (C12 ×2, C14 partial submodules): known subtotals only, as the DRAFT policy intends.
A correct rejection is a PASS of that probe, never a harness failure.
The harness failing is shown separately by the C07 fault hook (exit 1, oracle untouched).

Arithmetic, kept separate: of the numeric expectations, max absolute error 2.8e-17 and max relative error 1.2e-16 (final, 67 expectations)
vs 5.0 and 1.0 in the baseline (20 executed expectations; the C02 area path returned 10 instead of 5).

### Generated gallery (demonstration, not evaluation)

`python demo/run_gallery.py` → exit 0 (`review-evidence/cmd_gallery_run.json`).
Seed 20261107, 25 fictional assemblies, 200 product records, schema `baucode-demo-input/1`, evaluator `run_demo.evaluate`.
Outcomes: 13 full carbon-module coverage, 2 partial coverage, 2 incomplete layers, 8 rejected (each with its designed error code); 16 share the 1 m2 functional unit.
Outputs in `demo/output/gallery/` (`gallery.html` `ffc50b00…15cc8`, `gallery.json` `8cab0a67…42e8b`, `generated_inputs.json` `6be82873…4089e`).
These records are not cases, GOLD, holdout or accuracy evidence, and their equivalence to anything real is unverified.

`python demo/check_gallery.py` → exit **0**, 28 supplementary demonstration checks PASS (`review-evidence/cmd_gallery_checks.json`):
repeat runs byte-identical and equal to the saved output; stored results equal direct `evaluate()`; no script/link/img tags, `src`/`href`/`on*` attributes or URLs;
SYNTHETIC/GENERATED badge; two SVG charts with title/desc; legend; separate D chart/column; bars anchored at the zero line with negatives left of it;
UNKNOWN cells for unknown totals; rejected rows without numbers; 2 m2 assembly not charted; markup in labels escaped; no preference/health/safety/recyclability wording;
no thermal metric; both replacement recipes work (single wall still matches its hand-derived file; gallery `--inputs` reproduces the hand-derived 185); originals unchanged vs base.
One check failed on its first run: the escaped injection text `&lt;img src=x` tripped a raw-text regex. That check now parses real attributes. The page was not changed for it.
No browser or visual inspection was performed, and the dataviz palette validator was not run (it needed approval); colours are the documented reference slots 1–2.

### Added limits

- `lib.per_m3_checked` still accepts a nan/negative density from a direct caller. The demo is the validation boundary, documented in `docs/INPUT_SCHEMA.md`; this is not a global fix.
- Legacy `compare6`/`levels` quantity handling and the ranking/health/D/missing-layer semantics remain unverified, isolated from the demo and gallery, and unrepaired.

## Packaging review checkpoint (reviewed)

Same session and branch, still uncommitted.
The manifest (`6911268b…`), the harness (`f5605460…`), production `analysis/*.py` and every earlier results file are unchanged (`review-evidence/reviewed_final_hashes.json`).
Each hypothesis below was reproduced from the actual source before any fix.

1. **Layer product references (`demo/run_demo.py` validate).** `tests/repro_input_boundary.py` builds in-memory variants of the default input. These are supplemental input-boundary reproductions, not exact-20 cases and not an eval statistic.
   Before the fix (`review-evidence/reviewed_repro_boundary_before_fix.json`, exit 1), 3/7 met the boundary expectation:
   - a `{}` or `[]` element raised `TypeError: unhashable` (via the CLI this would be exit 1, not a structured rejection);
   - a duplicate reference was EVALUATED with a re-weighted median (A1-A3 165 instead of the hand-derived 185);
   - a padded product id `' SYN-P4 '` was silently stripped and accepted;
   - number and padded-reference elements were already rejected.

   Fix: a `canonical_id()` check, plus `PRODUCT_REF_INVALID` and `DUPLICATE_PRODUCT_REF` raised before any set/dict lookup.
   After the fix: 7/7, exit 0 (`reviewed_repro_boundary_after_fix.json`, `reviewed_repro_boundary_final.json`).
   Valid inputs are unchanged: the default and replacement `result.json` are byte-identical to before (`4f63c657…`, `28fadfc4…`).
2. **Detection counts (`tests/confusion_exact20.py`).** On a derived copy of `results_final.json` with two actual statuses removed (`review-evidence/reviewed_derived_results_status_removed.json`):
   - before the fix, the expected-valid probe still counted as TN (15) and the expected-invalid one as FN (`reviewed_confusion_unrecognized_before_fix.json`);
   - after the fix, each counts as `unrecognized` in its class: TN 14 and TP 14, with unrecognized 1 + 1 (`reviewed_confusion_unrecognized_after_fix.json`).

   The arithmetic block is now labelled `numeric_assertion_residuals` and states that it includes discrete counts; it is not an accuracy metric.
   The saved real results had no unrecognized statuses, so the observed counts did not change and none are claimed as improved.
3. **Wording (`demo/run_gallery.py`).** "Same-FU comparable" became "same reference area; equivalence unverified" in the JSON/CSV fields, both chart titles and notes, and the table caption.
   The page now states that a shared 1 m2 area does not establish thermal, structural, fire or acoustic equivalence. No calculation changed.
   `check_gallery.py` gained one assertion (the wording appears on both charts and in the caption, and "comparable"/"functional unit" do not appear); no check was relaxed.

| command | exit | result |
|---|---|---|
| `python tests/run_exact20.py --out tests/results_reviewed.json --label reviewed-after-packaging-fixes` | 0 | cases 20/0/0/0; blocking 79/0/0/0; non-blocking 1 PASS, 4 UNKNOWN, 2 NOT RUN (`2a68e2f8…`) |
| `python tests/run_exact20.py --out tests/results_faultproof_reviewed.json --label faultproof-reviewed-C07-density-x2 --fault-hook C07-density-x2` | 1 | C07 FAIL only (`cc5fa872…`) |
| `python tests/confusion_exact20.py tests/results_reviewed.json --out tests/detection_metrics_reviewed.json` | 0 | TP 15 FN 0 unrecognized 0 / TN 15 FP 0 abstained 3 unrecognized 0; max abs residual 2.8e-17 |
| `python demo/run_demo.py` | 0 | 185, matches 23 hand values |
| `python demo/run_demo.py --input demo/input/synthetic_wall_replaced.json --out demo/output/replaced` | 0 | 230, matches 17 hand values |
| `python demo/run_gallery.py` | 0 | 25 assemblies / 200 records; 13 full, 2 partial, 2 incomplete, 8 rejected; 16 same reference area (equivalence unverified); `gallery.html` `6b871220…` |
| `python demo/check_gallery.py` | 0 | 29 supplementary checks PASS |
| `python tests/repro_input_boundary.py` | 0 | 7/7 boundary variants |

The headline "20 PASS" covers blocking probes only.
These remain open: C02 cap units UNKNOWN, C15 extract scenario UNKNOWN, C16 reconciliation NOT RUN (characterization and B4-rejection PASS only),
C18 intended formula UNKNOWN (characterization only), C19 legacy health finding UNKNOWN, C20 injection NOT RUN.
No browser or visual inspection was performed.

## Reproduce

From the repository root:

```
python tests/run_exact20.py --out tests/results_after.json --label after --overwrite   # exit 0
python tests/run_exact20.py --out tests/results_faultproof.json --label faultproof --fault-hook C07-density-x2 --overwrite   # exit 1
python demo/run_demo.py                                                                 # exit 0
python demo/run_demo.py --input demo/input/synthetic_wall_replaced.json --out demo/output/replaced   # exit 0
python analysis/run.py                                                                  # exit 1 (needs products.csv; documented baseline)
python tests/run_exact20.py --out tests/results_final.json --label final --overwrite    # exit 0
python tests/confusion_exact20.py tests/results_final.json                              # exit 0 (descriptive)
python demo/run_gallery.py                                                              # exit 0
python demo/check_gallery.py                                                            # exit 0 (supplementary)
```

## Historical context (evidence-only note, nora, 2026-11-07)

- Earlier, separate suite (prior checkout, not this harness): before fixes 12 PASS / 8 FAIL; after 19 PASS / 1 FAIL. That C19 FAIL was about the committed real report, which cannot be regenerated without the missing input data.
- In this harness, C19 PASS covers only the SYNTHETIC rendered outputs; the historical real-report finding stays UNKNOWN (C19.legacy_health_finding). The two are not the same claim.
- Legacy `python analysis/run.py` still fails (missing `analysis/products.csv`).
