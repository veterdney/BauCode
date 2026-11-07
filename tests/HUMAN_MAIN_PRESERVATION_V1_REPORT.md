# Human-main preservation v1 — separate scope, uncommitted gate candidate

Local and remote review head at start: `305345a394d0019dc4c5cc51aff508c2a54dea77`. Pinned human main: `8336cb6ab602d96b26b36390274dcb47cf05ac1c`; fork: `f3575fb2d00bcce0a5ba9c1cc576d198da0c8c1e`.

## Architecture / freeze
`tests/human_main_preservation_v1.json` contains every path in the pinned fork-to-human-main Git delta, with expectations derived from upstream Git blobs, never observed candidate bytes: 40 exact-byte files, 9 required absences (inherited human deletions), and exactly one explicit exception for `analysis/run.py`. That exception compares the full AST against the upstream source transformed only by the reviewed zero-argument `main()` wrapper and exact `__main__` guard. It does not permit arbitrary extra functions/statements. Comments and formatting are not AST claims.

`tests/check_human_main_v1.py` is a separate stdlib checker. It rederives the complete v1 policy from pinned Git on every run and errors if the frozen policy differs. Required files missing/replaced, content changes, forbidden symlinks, or resurrected deletions fail. Tool/policy errors exit 2, preservation failures exit 1, PASS exits 0. Exact-byte comparison deliberately does not normalize line endings (this checkout uses core.autocrlf=false).

Scope is the 50-path human-main delta, not all repository files. Existing synthetic modifications to `.gitignore`, `analysis/lib.py` and `analysis/model.py` are outside that delta, not newly excluded human-delta files. Functional/numeric checks remain in the original frozen suite. No original manifest, harness, generic gallery predicate or prior FAIL result was edited.

Freeze before reruns: `review-evidence/preservation-v1-20261107/freeze.json`.
Policy SHA256: `2c98c252eecd19671cf70863fbf73a4595c09558152db078a4afe428819133ac`.
Checker SHA256: `29a479a0ffb6104b6fb6476667aa7842f3dc81453355b55266b35fdeb02a3950`.

## Fresh results on this uncommitted policy candidate
All commands, actual stdout/stderr and exits: `review-evidence/preservation-v1-20261107/01_policy.json` through `13_legacy_missing_input.json`. Head/baseline and relative CWD are recorded. The expected exit 1 on original known-failing suites records their actual failure, not a relabelled PASS.

| scope | actual outcome |
|---|---|
| Separate preservation v1 | exit 0; 50 protected paths PASS |
| Policy falsification controls | exit 0; valid upstream fixture PASS; changed content, missing file, resurrected deletion and extra executable statement each return preservation FAIL as expected |
| Original exact20, unchanged | exit 1; 19 PASS / 1 FAIL (C19.originals_unchanged); required probes 78 PASS / 1 FAIL |
| Original isolated density-fault run | exit 1; C07 deliberately FAIL plus unchanged C19 FAIL |
| Original generic gallery checker | exit 1; 28 PASS / 1 FAIL (old-base original-file comparison) |
| Default / replacement / generated gallery | exit 0 each; default/replacement fixed expectations match; generated demo remains 200 invented records / 25 fictional assemblies |
| Product-reference / P2 supplementary | exit 0; 7/7 and 15/15 |
| Human Node loop | exit 0; 14 checks PASS |
| Detection summary | exit 0; descriptive only, no accuracy claim |
| Legacy pipeline | exit 1; missing products.csv, no fabricated data |

The falsification controls construct a temporary fixture solely from upstream Git objects and mutate only that fixture. Correct rejection is a successful falsification probe, not a production preservation PASS. The real human files are never mutated by those probes. No checks execute source from the fixture.

Original-scope FAILs remain FAIL: their unchanged-from-f357 assertions are false after importing legitimate human changes. The separate v1 PASS is not a comparable all-green20 claim and does not rewrite historical results. Optional probes remain 1 PASS / 4 UNKNOWN / 2 NOT RUN. Historical legacy C19 health findings remain distinct from synthetic C19 rendered checks.

Before/after hashes match across the 170-file snapshot: all pre-existing tracked files plus the new checker, policy and freeze record: see `before.json`, `after.json`, `immutability.json` (the reported 170 is the total snapshot cardinality, not 170 new checks). Fresh result names are `tests/results_preservation_v1_20261107.json`, `tests/results_preservation_v1_fault_20261107.json`, `tests/detection_metrics_preservation_v1_20261107.json`. Old files were not overwritten.

## Replay / limits
```
python tests/check_human_main_v1.py --out NEW_POLICY_RESULT.json
python tests/check_human_main_v1.py --self-test --out NEW_FALSIFICATION_RESULT.json
```
Do not rerun `--freeze` on the existing policy file: exclusive creation refuses overwrite. The checker requires the two pinned local Git objects and was exercised with Python 3.14.7. It is preservation tooling, not scientific acceptance. No GOLD/holdout/general reliability/real-wall/health/compliance claim; conservative C/D coupling and remaining scientific unknowns are unchanged.

STOPPED BEFORE STAGING/COMMIT/PUSH for artifact review. Original PR remains draft; no publication/readiness change is implied by this local policy candidate.
