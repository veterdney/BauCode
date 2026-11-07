# Demo input schema — `baucode-demo-input/1`

Input for `demo/run_demo.py`.
One JSON file describes one **SYNTHETIC** wall:
its products (each with a declared reference quantity and unit)
and its layers (each a pool of products, a thickness and a multiplier).
All carbon arithmetic runs through the production code in `analysis/lib.py` and `analysis/model.py`.

Everything here is a demo contract for synthetic data.
It is not a validated method for real walls.

## Top level

| field | type | rule |
|---|---|---|
| `schema` | string | must be `"baucode-demo-input/1"` (`SCHEMA_UNSUPPORTED`) |
| `label` | string | must be `"SYNTHETIC"` (`LABEL_NOT_SYNTHETIC`); the demo refuses anything else |
| `wall.id` | string | non-empty (`WALL_ID_MISSING`) |
| `wall.area_m2` | number | finite, > 0 (`WALL_AREA_INVALID`) |
| `products` | list | see below (`PRODUCTS_NOT_LIST`) |
| `layers` | list | at least one (`NO_LAYERS`) |
| `note` | string | optional, ignored |

## Product

| field | type | rule |
|---|---|---|
| `id` | string | non-empty string without leading/trailing whitespace (never silently stripped), unique (`PRODUCT_ID_INVALID`, `DUPLICATE_ID`) |
| `source` | string | non-empty provenance text, carried to every output (`SOURCE_MISSING`) |
| `scenario` | string | non-empty end-of-life scenario label (`SCENARIO_MISSING`) |
| `unit` | string | reference unit: `m3`, `kg` or `m2` (production `qm` is also accepted). Anything else → `UNIT_UNSUPPORTED` |
| `ref_quantity` | number | the declared quantity the module values refer to, e.g. `2` for "per 2 kg". Blank or absent → `REF_QTY_BLANK`; not a number → `REF_QTY_NOT_NUMERIC`; nan/±inf → `REF_QTY_NOT_FINITE`; ≤ 0 → `REF_QTY_NOT_POSITIVE`. **Never defaults to 1.** |
| `density_kg_m3` | number | optional; finite > 0 (`DENSITY_INVALID`). Required for `unit: kg` (`DENSITY_REQUIRED`) |
| `bulk_density_kg_m3` | number | optional fallback used by production `lib.dens` when `density_kg_m3` is absent |
| `modules` | object | GWPtotal (A2) per `ref_quantity` × `unit`, keyed by module. Allowed keys: `A1-A3`, `A1`, `A2`, `A3`, `C1`–`C4`, `D` (`MODULE_UNSUPPORTED`, e.g. `B4`). Values: finite numbers (`MODULE_VALUE_INVALID`). **Omit an undeclared module; do not write 0.** A written `0` is a declared, known zero; negatives are legitimate. |

String quantities such as `"nan"`, `"inf"` or `""` are accepted as JSON only so they can be rejected explicitly.

The demo is the validation boundary for density:
production `lib.per_m3_checked` checks the reference quantity and unit but does **not** reject a nan or negative density on its own,
so callers outside the demo must validate density themselves.

## Layer

| field | type | rule |
|---|---|---|
| `id` | string | non-empty, unique (`LAYER_ID_INVALID`) |
| `name` | string | optional |
| `product_ids` | list | ids from `products`. Each element must be a canonical string (`PRODUCT_REF_INVALID` for objects, lists, numbers, blanks or padded strings), listed once (`DUPLICATE_PRODUCT_REF`, since a repeat would weight the pool median) and known (`UNKNOWN_PRODUCT_ID`). Empty list → layer is UNKNOWN (`EMPTY_POOL`), not an error |
| `thickness` | object | `{"value": number, "unit": "m" | "cm" | "mm"}` via production `lib.to_metres` (`THICKNESS_UNIT_UNSUPPORTED`, `THICKNESS_INVALID`). Required when any pool product is `m3` or `kg` (`THICKNESS_REQUIRED`); optional for `m2` (used only for mass) |
| `multiplier` | number | explicit, finite, > 0 (`MULTIPLIER_INVALID`); scales area (e.g. 2 for both faces) |

## What is computed

Per product (production `model.module_breakdown` → `model.per_m2`):

- `m3`: value / q × thickness → per m2 wall; no density is used.
- `kg`: value / q × density × thickness → per m2 wall; one density factor (production `lib.per_m3_checked`).
- `m2`: value / q → per m2 wall; thickness is not used.

Per layer: value per m2 × `wall.area_m2` × `multiplier`, kgCO2e for the whole wall.
With several products the layer value is the **median of the product pool** (`model.pool_median`):
a descriptive statistic of the listed products, not a comparison of complete walls.
Mass = area × multiplier × thickness × median density (`lib.layer_mass_kg`), or UNKNOWN when thickness or any density is missing.

## DRAFT policies (agent-chosen, not externally reviewed)

| topic | policy |
|---|---|
| empty pool | layer `UNKNOWN` (`EMPTY_POOL`); wall gets only known subtotals, `a13_total` is null, exit 3 |
| A1-A3 aggregate vs A1/A2/A3 | declared aggregate is used; submodules are never added to it (`a13_overlap: true`). Without an aggregate, all three submodules are summed; fewer → layer `UNKNOWN` (`A13_UNDECLARED`) |
| partial C coverage | `c_known` is the subtotal over C modules declared by **every** pool product; `c_missing` lists the rest; `c_complete` is false unless all four are present |
| D | reported separately (`d`, `d_known_subtotal`); never subtracted from A1-C; null unless every pool product declares D |
| scenario | every product needs a label; a pool mixing labels is rejected (`SCENARIO_CONFLICT`) |
| B modules | not supported; rejected rather than ignored, so a declared B4 can never be double counted |

Layer completeness (every layer has a known A1-A3) and module coverage (C, D, mass) are reported separately.

**Conservative coverage coupling (C and D depend on A1-A3).**
Wall `c_known_subtotal`, `d_known_subtotal` and `a1_c_known_subtotal` sum only layers whose A1-A3 is known,
and `c_complete` / `d_complete` require every layer to be KNOWN.
A layer that is UNKNOWN for A1-A3 (`A13_UNDECLARED`) still shows its own `c_known` and `d`,
but adds nothing to the wall C or D subtotals, and C and D are then reported incomplete.
C and D completeness is therefore never claimed independently of A1-A3.
Decoupling would change the C and D subtotals of incomplete walls, so it is not done here (see `DECISIONS.md`).
Mass is not coupled: `mass_known_kg` sums every layer with a computable mass.

**Labels.** `a1_c_known_subtotal` is rendered as "A1-A3 + C1-C4 known subtotal" (selected modules only;
A4, A5 and B are outside scope, so it is never a life-cycle total);
`d_known_subtotal` as "D known subtotal (partial; separate, not subtracted)";
`mass_known_kg` as "known mass subtotal".
Result keys are unchanged because the frozen expected files address them by path.

**Report escaping.** Input-derived text in `report.md` (input name, IDs, scenario, error details) is HTML-escaped,
and `|`, `` ` ``, `\`, `[`, `]` and newlines are entity-encoded, so untrusted text cannot add markup or split a table cell or row.

Product `unit` and thickness `unit` that are not strings (objects, lists) are rejected as `UNIT_UNSUPPORTED` / `THICKNESS_UNIT_UNSUPPORTED`.
Integers too large for a float (e.g. `10**400`) are treated as not finite and rejected with the field's usual code
(`MODULE_VALUE_INVALID`, `DENSITY_INVALID`, `WALL_AREA_INVALID`, `MULTIPLIER_INVALID`, `REF_QTY_NOT_FINITE`, `THICKNESS_INVALID`).

## Outputs and exit codes

`--out DIR` (default `demo/output/default`) receives `result.json`, `layers.csv`, `report.md`
and, when an expected file is used, `expected_check.json`.
Only the input file name and its sha256 are written, never the path,
so output bytes do not depend on how the path was spelled.

| exit | status | meaning |
|---|---|---|
| 0 | `EVALUATED` | every layer has a known A1-A3 |
| 2 | `REJECTED` | invalid input; payload lists `errors`, has no `layers`/`totals` |
| 3 | `INCOMPLETE_LAYERS` | some layer UNKNOWN; only known subtotals |
| 4 | — | result differs from the expected file |
| 1 | — | internal error |

## Replacing the input (recipe)

1. Copy `demo/input/synthetic_wall.json` to `demo/input/<name>.json` and edit it. Keep `"label": "SYNTHETIC"`.
2. Work out the values you expect **by hand**, independently of the code, and write `demo/expected/<name>.expected.json`
   in the same shape as `demo/expected/synthetic_wall.expected.json` (`expect` maps result paths such as `totals.a13_total` to values).
3. Run `python demo/run_demo.py --input demo/input/<name>.json --out demo/output/<name>`.
   The expected file is picked up automatically by stem; exit 4 means your hand values and the code disagree.

Worked example: `synthetic_wall_replaced.json` changes only layer L2 from 100 mm to 160 mm;
its expected file derives A1-A3 230 (was 185) and C 30.2 (was 21.2) by hand.
