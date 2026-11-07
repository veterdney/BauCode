# SYNTHETIC GENERATED assembly gallery

**What.** One command generates 25 fictional assemblies (200 product records, seed `20261107`),
evaluates each one with the single-wall demo evaluator (`demo/run_demo.py` → `analysis/lib.py`, `analysis/model.py`),
and writes a standalone HTML page plus JSON/CSV and the generated inputs.

**Why.** To show, on many invented inputs at once, how the demo handles valid, partial, unknown and invalid data:
unit and reference-quantity edges, partial C, missing D, negative and zero values, A1-A3 overlap,
empty pools, scenario conflicts, B4, missing density, bad thickness units, a different reference area, and markup in labels.

**These records are a demonstration.**
They are not evaluation cases, not GOLD, not a holdout, not evidence of accuracy, and not real assemblies or materials.
Material families (`FAM-K` … `FAM-P`) and all numbers are invented.
No independent expected values exist for them, so equivalence to anything real is unverified.
The 20 frozen regression cases (`tests/exact20_manifest.json`) are separate and unchanged.

## Run

From the repository root:

```
python demo/run_gallery.py          # writes demo/output/gallery/
python demo/check_gallery.py        # supplementary structural checks (not an acceptance suite)
```

Expected output: `25 assemblies, 200 product records, seed 20261107` and
`EVALUATED_FULL_COVERAGE 13, EVALUATED_PARTIAL_COVERAGE 2, INCOMPLETE_LAYERS 2, REJECTED 8 | same reference area (equivalence unverified) 16`.

| file | content |
|---|---|
| `gallery.html` | standalone page: inline CSS and inline SVG, no scripts or external assets |
| `gallery.json` | every evaluator result with input locator, outcome category and `same_reference_area` flag |
| `gallery.csv` | one row per assembly; `UNKNOWN` for unknown quantities, `-` for rejected |
| `generated_inputs.json` | the exact generated inputs (`#/assemblies/<i>` locators) |
| `provenance.json` | generator, seed, schemas, counts, per-edge map, file hashes |

No file contains timestamps or absolute paths, so repeated runs are byte-identical.

## Reading the page

- Carbon is kgCO2e (GWPtotal A2) per reference area: `wall.area_m2` of a fictional assembly (1 m2 here).
  Only assemblies with exactly that area and no rejection appear in the charts and the main table.
  The 2 m2 assembly is listed separately and is never placed beside them.
- Sharing a 1 m2 reference area is **not** functional equivalence:
  thermal, structural, fire and acoustic equivalence is not established, and the page says so on both charts and in the table caption.
- A bar is drawn only for a complete quantity.
  Unknown or partial quantities appear as text ("UNKNOWN", "PARTIAL"), never as a zero bar.
  Bars start at a marked zero line; negative values extend left.
- D has its own chart and column and is never subtracted from A1-C.
- Mass appears only where thickness and density were given, marked "(known part only)" when some layers lack them.
- Rejected assemblies show their error codes and no numbers.
- No thermal metric is computed or shown, and nothing is ranked.
- All identifiers and labels are HTML-escaped, because input JSON is untrusted text.

Outcome categories: `REJECTED` (invalid input), `INCOMPLETE_LAYERS` (some layer has no known A1-A3),
`EVALUATED_PARTIAL_COVERAGE` (C or D not declared everywhere) and `EVALUATED_FULL_COVERAGE` (C1-C4 and D declared for every layer).
Coverage refers to carbon modules only; mass completeness has its own column.

## Replace the inputs

- Other seed: `python demo/run_gallery.py --seed 7 --out demo/output/gallery_seed7`.
- Your own assemblies: write `{"assemblies": [ <baucode-demo-input/1 documents> ]}`
  (schema: [`docs/INPUT_SCHEMA.md`](../docs/INPUT_SCHEMA.md)) and run
  `python demo/run_gallery.py --inputs FILE.json --out demo/output/mine`.
  An unreadable file exits 2.
  `check_gallery.py` exercises this route with the hand-derived default wall (185 kgCO2e); because that wall is 10 m2, it is correctly kept apart from the 1 m2 rows.

## Limits

- No browser was used to inspect the page; `check_gallery.py` checks structure (tags, attributes, bar geometry against the zero line, UNKNOWN cells, escaping, wording), not appearance.
- Chart colours are the dataviz reference slots 1–2 (documented as passing adjacent colour-vision checks); the palette validator was not run in this environment.
- Hover detail uses native SVG `<title>` tooltips only (no scripts).
- Known non-critical display issue: in the Module D chart, the text annotation for G09 (missing D) can be clipped at the chart edge.
  The value in the table and in `gallery.json` / `gallery.csv` is unaffected; the chart is not redesigned in this change.
- Table labels: "A1-A3 + C1-C4 known subtotal" (selected modules only; A4, A5 and B outside scope),
  "D known subtotal (partial; separate, not subtracted)" and "known mass subtotal kg".
  The gallery CSV column is `a1a3_c1c4_known_subtotal`; the per-assembly `result` in `gallery.json` keeps the evaluator key `a1_c_known_subtotal`.
- Density validation lives in the demo input boundary; production `lib.per_m3_checked` itself does not reject nan/negative density.
