# SYNTHETIC wall demo

Start with the unchanged human [team website](../docs/index.html), [lab](../docs/lab.html) and [research loop](../docs/loop.html); then open the [sparse presentation](presentation/index.html) for added checks. Human-site JavaScript and external Google Fonts remain authored; exploratory rankings are not validated recommendations or this demo's evaluation method. The presentation wrapper is offline/no-JavaScript and displays saved outputs, not a browser calculator. Repository HTML links are files, not a verified deployed Pages URL.

## Run from the repository root

Python 3 standard library only: no pip packages, API or real dataset needed. `run_demo.py` uses production conversions in `analysis/lib.py` and `analysis/model.py` and writes JSON, CSV and Markdown.

Linux / macOS:
```sh
python3 demo/run_demo.py
python3 demo/run_demo.py --input demo/input/synthetic_wall_replaced.json --out demo/output/replaced
python3 demo/run_gallery.py
```

Windows, if the Python launcher is installed:
```powershell
py -3 demo/run_demo.py
py -3 demo/run_demo.py --input demo/input/synthetic_wall_replaced.json --out demo/output/replaced
py -3 demo/run_gallery.py
```

These commands genuinely regenerate outputs; opening saved HTML or evidence does not execute Python/tests. The default and replacement use the same declared 10 m2 wall area with L2 thickness 100 -> 160 mm, yielding A1-A3 185 -> 230 kgCO2e in the saved examples. Same area does not establish functional/thermal equivalence. Files are in `demo/output/default/` and `demo/output/replaced/`; the [standalone gallery](output/gallery/gallery.html) covers 200 generated records / 25 fictional assemblies, not 200 independent evaluations. See [gallery scope](GALLERY.md).

## Replace the input

Follow the [schema and replacement recipe](../docs/INPUT_SCHEMA.md#replacing-the-input-recipe). Copy a sample to `my_wall.json`, retain the SYNTHETIC label, and edit documented fields:

```sh
python3 demo/run_demo.py --input my_wall.json --out demo/output/mine --no-expected
# Windows: py -3 demo/run_demo.py --input my_wall.json --out demo/output/mine --no-expected
```

`--no-expected` provides no independent oracle comparison. Default/replacement expectations are [agent-derived files](expected/synthetic_wall.expected.json), not human-reviewed GOLD; all fixed cases are exposed regressions, not holdout. Do not overwrite historical audit results when replaying checks; use new result names in a full Git checkout.

## Recorded evidence, not a new audit

- [Final command/exit report](../review-evidence/landscape-final-20261107/REPORT.md) and [detailed summary](../review-evidence/landscape-final-20261107/SUMMARY.json).
- [Presentation-only binding](../review-evidence/sparse-presentation-20261107/SOURCE_BINDING.json) distinguishes prior tested source from later wrapper changes. This docs-only follow-up has no functional changes or new test/CI-green claim.
- Original unchanged exact20: **19 PASS / 1 FAIL**, 78/79 required probes; gallery: **28 PASS / 1 FAIL**. Failures remain FAIL (old-base preservation assertions). Deliberate C07 density fault exits 1 alongside existing C19.
- Separate historical preservation v1: **50 protected paths**, four isolated mutation controls rejected. Not all-green20 or whole-repository protection. [Pinned policy](../tests/human_main_preservation_v1.json) and [scope/report](../tests/HUMAN_MAIN_PRESERVATION_V1_REPORT.md) remain unchanged. These two README paths are outside that pinned human-main delta (which includes `analysis/README.md`); the historical PASS is not a whole-repository guarantee or a fresh docs-candidate audit. No new preservation PASS is claimed.
- Optional probes remain 1 PASS / 4 UNKNOWN / 2 NOT RUN. Full preservation replay requires original Git objects/checkout; saved files or a portable ZIP are not a full audit.

## Limits and current integration

SYNTHETIC only. No scientific, general-accuracy, real-wall, health, compliance or preferred-system claim. Legacy rankings/scores are exploratory and unvalidated here; no U-value or functional equivalence is calculated. Historical legacy health findings are separate from synthetic C19 rendered checks.

Selected A1-A3 + C1-C4 known subtotal excludes A4/A5/B: it is not a complete lifecycle. D is separate and never netted against A-C; UNKNOWN is not zero. Wall C/D coverage conservatively counts only A1-A3-known layers, not independently complete C/D coverage. Partial C, aggregate/submodule overlap and scenario rules remain DRAFT; see the schema. Incoming numeric hardening is bounded, not universal overflow handling.

The integrated repository now includes the human [curated dataset](../data/Building%20material%20property%20dataset.csv) and [levels dataset adapter](../analysis/levels/dataset_fill.py). The synthetic demo does not consume that dataset/adapter or validate their ratings, assumptions or equivalence. They are not a drop-in `analysis/products.csv` for the legacy pipeline, which still cannot run without that missing file. This follow-up changes only the two README files; human website/report, calculations, datasets, tests/oracles and recorded results are untouched.
