# SYNTHETIC wall demo

**What.** A one-command, stdlib-only demo that turns a synthetic wall description (JSON) into
`result.json`, `layers.csv` and `report.md`,
using the same production conversion code as `analysis/` (`lib.py`, `model.py`).
It needs no real data: `analysis/products.csv` is not required.

**Why.** The legacy pipeline (`python analysis/run.py`) cannot run without the Oekobaudat-derived `analysis/products.csv`,
which is not in the repository.
The demo exercises the reference-quantity, unit, density, module-coverage and unknown-handling paths on invented numbers,
so they can be checked by hand.

**Run** (from the repository root):

```
python demo/run_demo.py
```

Expected: `EVALUATED`, exit 0, A1-A3 total 185 kgCO2e, and
`matches synthetic_wall.expected.json (23 agent hand-derived values)`.
Outputs land in `demo/output/default/`.

**Replace the input.** See the recipe in [`docs/INPUT_SCHEMA.md`](../docs/INPUT_SCHEMA.md#replacing-the-input-recipe).
Worked example:

```
python demo/run_demo.py --input demo/input/synthetic_wall_replaced.json --out demo/output/replaced
```

**Generated gallery.** `python demo/run_gallery.py` writes a standalone HTML/JSON/CSV gallery of 25 generated fictional assemblies;
see [`GALLERY.md`](GALLERY.md). Generated records are a demonstration, not evaluation cases.

**Regression cases.** `python tests/run_exact20.py --out tests/results_after.json --label after --overwrite`
runs the 20 frozen synthetic cases; details in [`tests/REPORT.md`](../tests/REPORT.md).

**Limits.**

- SYNTHETIC only; the input must say so and the output says so on every artefact.
- Expected values are agent hand-derived and not human-reviewed.
- GWP only; no B modules, replacement cycles, U-values, rankings or scores.
- The partial-C, A1-A3 overlap, D and scenario rules are DRAFT policies (see `docs/INPUT_SCHEMA.md`).
- Nothing here validates the legacy rankings, the "preferred" systems or the well-being/health scores in `analysis/`.
- "A1-A3 + C1-C4 known subtotal" covers the selected modules only; A4, A5 and B modules are outside scope,
  so "complete for selected modules" never means a complete life cycle.
  The result key stays `a1_c_known_subtotal` because the frozen expected files address it by that path.

**Compatibility and scope (upstream dataset).**
Upstream PR #4 (commit `63f8bdb3`) adds `data/Building material property dataset.csv` and `.md`,
a curated dataset mixing sources and assumed values.
This branch stays on base `f3575fb2` and does not contain that commit (not present in this checkout),
so nothing here touches it; when merged, it is preserved untouched.
The demo does not consume it, and it is not a drop-in `analysis/products.csv` (different columns and provenance).
This synthetic addition has no adapter for it (note: upstream PR #5, dddec8d5, separately adds analysis/levels/dataset_fill.py for the 3-level scoring; not integrated or tested here), its ratings are not an oracle for any check here,
and this branch performs no dataset validation.
