# Integrated-main checkpoint — draft remains not ready

Upstream integrated: `8336cb6ab602d96b26b36390274dcb47cf05ac1c` (human PRs #4–#7). Previous review head: `93471028e7a8fe92f83cbe759887733fdd8dba45`. This is an ordinary branch merge; no rebase, reset, force push, PR merge, paid run or Claude call.

## Resolution and human-work preservation
The only merge conflict was `analysis/run.py`. The current upstream pipeline, including its carbon-budget removal, is retained inside the import-safe `main()` wrapper. A static AST comparison verifies that unwrapping it reproduces upstream exactly. Every other upstream-changed path/deletion matches upstream. Human levels adapter, datasets, views, loop files and GitHub Pages assets remain unchanged relative to that upstream. Evidence: `review-evidence/integration-final-20261107/upstream-preservation.json`.

## Actual integrated results — failures retained
Commands ran from repository root on the merge-pending candidate, with previous HEAD and exact upstream recorded in each JSON. No new implementation changes occurred during tests. Source/oracle hashes before and after match for all tracked Python/MJS sources, the exact20 manifest and demo expected JSON. This is a scoped code/oracle immutability check, not a claim that generated outputs or every untracked file are immutable.

| command / evidence ID | actual exit | outcome |
|---|---:|---|
| exact20, `01_exact20.json` | 1 | 19 PASS / 1 FAIL (C19.originals_unchanged); 78/79 required probes PASS |
| isolated density fault, `02_faultproof.json` | 1 | C07 fails as intended AND existing C19 preservation-baseline failure remains |
| default demo, `03_demo.json` | 0 | fixed hand-derived expectations matched |
| replacement, `04_replacement.json` | 0 | fixed replacement expectations matched |
| generated gallery, `05_gallery.json` | 0 | 25 fictional assemblies / 200 generated records |
| gallery checks, `06_gallery_checks.json` | 1 | 28 PASS / 1 FAIL, original-file comparison against old base |
| product reference boundary, `07_references.json` | 0 | 7/7 supplementary checks |
| P2 boundary/Markdown probes, `08_p2.json` | 0 | 15/15 supplementary checks |
| human `node analysis/levels/viz/test_loop.mjs`, `09_human_node.json` | 0 | 14 checks PASS |
| descriptive detection counts, `10_detection.json` | 0 | counts only, not acceptance or general accuracy |
| legacy `analysis/run.py`, `11_legacy_missing_input.json` | 1 | missing `analysis/products.csv`; expected limitation, not fixed |

Full command arguments, stdout/stderr and expected/actual exits: `review-evidence/integration-final-20261107/`. New same-case results: `tests/results_integrated_20261107.json`, `tests/results_integrated_fault_20261107.json`.

The two original-file checks compare against frozen base `f3575fb2`, so correctly integrating human changes makes their unchanged-from-old-base assertions false. This is a demonstrated baseline scope mismatch, not permission to overwrite human files. Their actual FAIL statuses and nonzero exits are preserved. The manifest and harness were not changed to manufacture a pass. A separate latest-upstream preservation audit passes; it does not relabel frozen C19. A reviewed versioned preservation-baseline policy is still required before calling the suite green.

Optional probes remain 1 PASS / 4 UNKNOWN / 2 NOT RUN. Synthetic C19 rendered claims remain distinct from the historical handoff-only legacy health finding. No GOLD, holdout, real-wall, health, compliance or functional-equivalence validation is claimed. C/D conservative A1–A3 coupling, bounded numeric hardening and minor chart clipping with table fallback remain disclosed.

## Readiness
Draft / NOT READY: frozen preservation-baseline policy unresolved; legacy data absent; full legacy pipeline and scientific equivalence unverified. GitHub conflict status must be rechecked after push. Test evidence is tied to the recorded candidate/source hashes, not fabricated CI or an assertion that future main changes are integrated.

An initial capture invocation accidentally launched argumentless Python and was stopped before any test started. Its empty local logs are excluded; the complete evidence directory above comes from the corrected guarded invocation.
