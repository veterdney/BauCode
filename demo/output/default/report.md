# SYNTHETIC wall demo result

> **SYNTHETIC.** Invented demo numbers. This is not a real wall, not an Oekobaudat record,
> and carries no scientific standing. It ranks nothing and makes no product-choice or indoor-air claim.

- Input: synthetic_wall.json (sha256 216b1f966d45d446f0957cef64afbcefde1b781caf43bef244c2d1416b41154d)
- Status: **EVALUATED** (exit 0)

Wall SYN-WALL-1, area 10 m2. Carbon in kgCO2e (GWPtotal A2) for the whole wall.

| quantity | value | coverage |
|---|---|---|
| A1-A3 total | 185 | layers known 3/3 |
| A1-A3 known subtotal | 185 | |
| C1-C4 known subtotal | 21.2 | complete: yes |
| A1-A3 + C1-C4 known subtotal | 206.2 | complete for selected modules: yes |
| D known subtotal (partial; separate, not subtracted) | -2 | complete: no |
| known mass subtotal kg | 150 | complete: no |

| layer | status | products | scenario | thickness m | A1-A3 | C known | C missing | D | mass kg | density note |
|---|---|---|---|---|---|---|---|---|---|---|
| L1 | KNOWN | SYN-P1;SYN-P2;SYN-P3 | SYN-EOL-A | 0.02 | 60 | 1.2 | - | -2 | 100 | not used: m3 reference basis |
| L2 | KNOWN | SYN-P4 | SYN-EOL-B | 0.1 | 75 | 15 | - | UNKNOWN | 50 | used: kg reference basis converted with product density (lib.dens) |
| L3 | KNOWN | SYN-P5 | SYN-EOL-C | - | 50 | 5 | - | 0 | UNKNOWN | not used: m2 reference basis |

## How to read this

- SYNTHETIC demo data; these numbers describe no real wall or product.
- UNKNOWN (null) means not declared or not computable. It is never zero and never a favourable result.
- D is reported separately and is never subtracted from A1-A3 + C1-C4.
- a1_c_known_subtotal is the A1-A3 + C1-C4 known subtotal for the selected modules only; A4, A5 and B modules are outside scope, so it is not a life-cycle total.
- Layer pool statistic: median of product pool (descriptive; not a wall comparison).
- Product sources are listed per layer in `layers.csv` and `result.json`.
- Limits: GWP only; no replacement cycles (B4) or other B modules; no U-value; DRAFT policies for
  partial C coverage, A1-A3 aggregate/submodule overlap and scenario conflicts (see docs/INPUT_SCHEMA.md).
- Scope: "A1-A3 + C1-C4" covers the selected modules only. A4, A5 and B modules are outside scope,
  so "complete for selected modules" never means a complete life cycle.
- Conservative coverage coupling: wall C and D subtotals count only layers with a known A1-A3.
  A layer whose A1-A3 is UNKNOWN adds no C or D to the wall subtotals, and C and D are then reported incomplete,
  even if that layer declares C or D. C and D completeness is therefore never claimed independently of A1-A3.
