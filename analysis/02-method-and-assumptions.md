# 02 Method and assumptions

## Functional equivalence

- Exterior walls: 1 m², U ≤ 0.20 W/m²K (stricter than the 0.24 GEG limit, so the wall does not need re-insulation within the first decades).
  Insulation thickness is solved per system: `d = (1/U − 0.17 − R_other) · λ_eq`.
  Monolithic brick and aerated concrete get a top-up insulation layer to reach the same U.
- Interior walls: 1 m² non-load-bearing partition, no thermal target.
  Acoustics and fire are scored qualitatively, not computed.

## Layer model (see `model.py`)

Each layer takes the **median** of all matching EPDs.
Median avoids cherry-picking one product.
The best products are chosen later (step 07).

| Layer | λ (W/mK) | Service life (y) | Disassembly 1–5 |
|---|---|---|---|
| Structural timber / KVH | 0.13 | 100 | 5 |
| Wood-fibre insulation | 0.040 | 60 (40 if bonded under render) | 5 |
| Cellulose | 0.039 | 60 | 5 |
| Straw bale | 0.052 | 60 | 5 |
| Rock wool | 0.036 | 60 (40 as ETICS) | 3 |
| EPS | 0.035 | 40 as ETICS | 2 |
| Fired brick | 0.12 | 100 | 2 |
| Sand-lime brick | 0.99 | 100 | 3 |
| Aerated concrete | 0.10 | 100 | 2 |
| Reinforced concrete | 2.0 | 100 | 1 |
| Plasterboard | 0.25 | 50 | 3 |
| Mineral render | 0.80 | 40 | 2 |
| Clay/lime plaster | 0.80 | 60 | 4 |
| Clay panels | 0.50 | 60 | 5 |
| Wall covering / paint | – | 12 | 3 |

λ, service lives and disassembly scores are **assumptions** from typical practice, not from the CSV.

## Life cycle

- Study period 60 years.
- Layer carbon = A1-A3 + C1–C4.
- Replacements = `ceil(60 / life) − 1`; each repeats A1-A3 + C.
- Module D is reported separately, never added to the headline value.
- Biogenic carbon: `GWPtotal (A2)` already contains the negative uptake in A1-A3 and the release in C3.
  Timber systems therefore show strongly negative A1-A3 and positive C.
  The net over 60 years is small, so the benefit is mainly **timing** and lower fossil emissions.

## Scoring (0–1, min-max across systems of the same class)

| Criterion | Weight inside | Inputs |
|---|---|---|
| Carbon | – | 60-year life-cycle GWP A1–C (lower is better) |
| Sustainability | 0.4 / 0.4 / 0.2 (interior: 0.3 / 0.3 / 0.2 / 0.2) | renewable primary-energy share (PERT/(PERT+PENRT)); mean disassembly score; share of carbon caused by replacements; interior only: adaptability |
| Well-being & health | 0.75 / 0.25 | mean of 5 expert scores (moisture buffering, low emissions, summer comfort, acoustics, moisture-damage robustness); POCP from the data (smog) |

Total = mean of the three.
Sensitivity: carbon-heavy (0.5/0.25/0.25) and well-being-heavy (0.25/0.25/0.5), both in `results_wall_systems.csv`.

## Wall area per floor area (for the budget comparison)

0.6 m² exterior wall and 0.8 m² interior wall per m² gross floor area.
Typical residential values, not project-specific.
