# Decisions

## 2026-11-07 — synthetic exact-20 regression and demo (uncommitted, branch review/baucode-verified-20261107)

- **Lazy, injectable product loading.** `lib.ROWS` loads on first use via `all_rows()`; `select/sel/cand/layer_stats/assess` take `rows=`.
  Why: the package could not be imported without `analysis/products.csv`. Rejected: fabricating a products.csv, monkeypatching `open`/`ROWS`.
- **Reference quantity never defaults.** `lib.ref_quantity` rejects blank/0/negative/non-finite; `per_m3` returns None; `per_m2` area path divides by q.
  Why: `f(q) or 1` turned blank and 0 into 1 and the area path ignored q. Rejected: keeping legacy parity for those rows.
- **Legacy rankings not repaired.** `assess`/`layer_stats` keep their numbers (undeclared D → 0.0, missing layers skipped); they only gain `complete`, `missing_layers`, `c_modules`, `d_known`.
  Why: out of scope and unverifiable without real data. Rejected: rewriting the scoring.
- **DRAFT demo policies.** Aggregate A1-A3 wins over submodules (never summed together); partial C → known subtotal + coverage; D separate; mixed scenarios in a pool rejected; B modules rejected.
  Rejected: inventing B4 reconciliation or scenario weighting.
- **Generated gallery reuses the demo evaluator.** `demo/run_gallery.py` calls `run_demo.evaluate` per fictional assembly (seed 20261107, 25 assemblies, 200 records) and only renders.
  Why: no parallel arithmetic; an invalid assembly is rejected before any comparison. Rejected: a second acceptance suite or treating generated records as evaluation cases.
- **Gallery charts draw complete quantities only, same functional unit only.** Unknown/partial → text; other FUs listed separately; no scripts or external assets.
  Rejected: plotting known subtotals as if complete, mixing 1 m2 and 2 m2 values.
- **Packaging review.** Malformed, padded or duplicate product references are rejected before lookup (a dict reference used to crash; a duplicate silently re-weighted the median: 165 vs 185).
  Unrecognized statuses in detection counts are "unrecognized", never TN/FN. "Same reference area; equivalence unverified" replaces "same-FU comparable".

## 2026-11-07 — P2 input-boundary and wording fixes (uncommitted, same branch)

- **C/D stay coupled to A1-A3 coverage (conservative).** Wall C/D subtotals sum only A1-A3-known layers; C/D completeness needs every layer KNOWN. Documented in the report limits and docs/INPUT_SCHEMA.md.
  Why: decoupling changes the C/D subtotals of incomplete walls (a numeric change, not a tiny one). Rejected: independent C/D completeness.
- **Labels renamed, keys kept.** "A1-A3 + C1-C4 known subtotal", "D known subtotal (partial; separate, not subtracted)", "known mass subtotal"; result key `a1_c_known_subtotal` unchanged (frozen expected paths); gallery CSV column renamed `a1a3_c1c4_known_subtotal`.
  Rejected: renaming result.json keys.
- **report.md escapes untrusted text with HTML entities** (`&#124;` for `|`, `<br>` for newlines, HTML-escaped); untrusted values are no longer in code spans.
  Why: entities are decoded after GFM cell splitting, so no input can split a cell; backslash escaping breaks on input ending in `\`. Rejected: backslash escaping.
