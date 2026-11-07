# 05 Carbon budget comparison (carbonbudget.eu)

Skill: `.claude/skills/carbon-budget-api`.
Host `https://carbonbudget.eu`, `dataset_version: v1`, resolved 2026-11-07T12:06Z, source loaded 2026-11-06T15:47Z.
Raw responses: `analysis/budget_de_res_{2026,2036,2046}.json`.

## Inputs

Country `de`, typology `residential` (valid typologies: Culture, Health, Industry, Office, ParkingLogistic, Residential, Retail, Science), 1,000 m² area, completion years 2026, 2036, 2046.
Years 2056 and 2066 return no budget: the API range ends in 2050.

## Budgets (kgCO₂e/m² gross floor area)

| Completion year | Embodied | Operational | Total |
|---|---|---|---|
| 2026 | 354.65 | 156.76 | 511.41 |
| 2036 | 136.70 | 37.33 | 174.03 |
| 2046 | 41.31 | 18.37 | 59.68 |

The embodied budget drops 61 % in the first decade and 70 % in the second.

## Wall share of the embodied budget

Wall carbon (A1-A3 + C) per m² floor area, using 0.6 m² exterior and 0.8 m² interior wall per m² floor area.
Build stage only, one wall type at a time.

| System | kgCO₂e/m² floor | % of 2026 budget | % of 2036 | % of 2046 |
|---|---|---|---|---|
| X7 straw | 9.8 | 2.8 | 7.2 | 23.7 |
| X1 timber frame | 23.3 | 6.6 | 17.1 | 56.4 |
| X2 CLT + wood fibre | 24.2 | 6.8 | 17.7 | 58.5 |
| X5 RC + rock wool | 33.8 | 9.5 | 24.7 | 81.8 |
| X3 brick + rock wool | 37.1 | 10.5 | 27.1 | 89.8 |
| X4 sand-lime + EPS | 37.3 | 10.5 | 27.3 | 90.3 |
| X8 brick + wood fibre | 41.5 | 11.7 | 30.4 | 100.5 |
| X6 AAC + rock wool | 45.8 | 12.9 | 33.5 | 111.0 |
| P6 solid timber | 7.2 | 2.0 | 5.2 | 17.3 |
| P5 clay panel | 11.8 | 3.3 | 8.7 | 28.7 |
| P1 rock wool + plasterboard | 13.5 | 3.8 | 9.9 | 32.7 |
| P7 fired brick | 17.8 | 5.0 | 13.0 | 43.1 |
| P3 sand-lime | 26.1 | 7.4 | 19.1 | 63.2 |
| P4 AAC | 27.3 | 7.7 | 20.0 | 66.0 |

Source: `results_budget_share.csv` (percentages for 2036/2046 rounded here).

## Reading

- In 2026 every wall option fits easily; a mineral exterior wall already takes 10–13 % of the embodied budget.
- By 2046 a monolithic mineral exterior wall alone exceeds the whole embodied budget (X8 100 %, X6 111 %).
  Walls renovated in the 2040s must be bio-based or reused.
- Only the timber/straw systems leave room for structure, slabs, services and finishes after 2036.
- **Not compared:** the budget covers a whole building; this study covers one element.
  The shares show where the wall sits, not whether the building complies.
- **Module scope:** the API does not state which modules its "embodied" value covers; A1–C is assumed.
