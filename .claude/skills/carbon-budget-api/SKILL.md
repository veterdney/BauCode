---
name: carbon-budget-api
description: Compute project-specific building carbon budgets (kgCO2eq/m², embodied + operational) and compare them to an LCA result, using the public API at https://carbonbudget.eu. Use when a task needs reference carbon budgets by country, building typology and completion year.
---

# Carbon Budget API

Public HTTP API, no auth.
Base URL: `https://carbonbudget.eu`

All values below were verified against the live API on 2026-11-07.
The upstream docs are partly stale (they list 3 countries, 2025–2050, lower-case typologies);
trust the discovery calls below over any docs.

## Workflow

1. **Discover** valid inputs — do not hardcode countries, years or typologies:
   - `curl -s 'https://carbonbudget.eu/referencevalues?summary=1'` → `countries`, `years`, `from_year`, `to_year`, `dataset_version`
   - `curl -s 'https://carbonbudget.eu/referencevalues?country=de'` → `typologies` (valid names for that country) and per-year `records`
2. **Compute** with `POST /budget`.
3. **Read** `selected_year_budget` (budget for the completion year) and, if an LCA was sent, `delta_to_lca`.

## Endpoints

| Method + path | Returns |
|---|---|
| `GET /referencevalues?summary=1` | countries, years, range, `dataset_version` |
| `GET /referencevalues?country=<cc>` | typologies + all reference records (`embodied_per_m2`, `operational_per_m2`, `total_per_m2` by year and typology) |
| `GET /referencevalues` | CSV download of all reference data |
| `POST /budget` | budget calculation (JSON body) |
| `GET /api/labels?lang=en-US` | UI label dictionary (rarely needed) |
| `GET /api/health` | `{"ok":true}` |

Verified today: 31 countries (`at be bg ch cn cy cz de dk ee es fi fr gb gr hr hu ie it lt lu lv mt nl no pl pt ro se si sk`), years 2020–2050.
German typologies: `Culture Health Industry Office ParkingLogistic Residential Retail Science`.

## POST /budget

Request fields:

| Field | Req | Aliases | Notes |
|---|---|---|---|
| `country` | ✓ | | ISO alpha-2, case-insensitive |
| `completion_year` | ✓ | `completionYear`, `year` | within `from_year`..`to_year` |
| `typologies` | ✓ | `areas`, `shares` | see formats below |
| `total_area_m2` | if shares | `totalAreaM2`, `total_area` | gross floor area m² |
| `project_lca_per_m2` | | `projectLcaPerM2`, `lca` | kgCO₂eq/m²; enables `delta_to_lca` |
| `project_name` | | `projectName` | echoed back |

Typology formats (pick one):

```json
{"typologies": {"residential": 4500, "office": 2000}}
{"total_area_m2": 6500, "typologies": {"residential": {"share": 0.69}, "office": {"share": 0.31}}}
{"typologies": [{"typology": "residential", "area": 4500}, {"typology": "office", "area": 2000}]}
```

Typology names matched case-insensitively (`residential` works for `Residential`); the echoed `request.typologies` is lower-cased.
Shares are normalised against `total_area_m2` (0.69 × 6500 = 4485 m²), so they need not sum to exactly 1.

Example:

```bash
curl -s -X POST https://carbonbudget.eu/budget \
  -H 'Content-Type: application/json' \
  -d '{"country":"de","completion_year":2034,"project_lca_per_m2":420,
       "typologies":{"residential":4500,"office":2000}}' \
  | jq '{selected_year_budget, delta_to_lca}'
```

Verified output (2026-11-07):

```json
{"selected_year_budget":{"year":2034,"embodied_per_m2":202.34,"operational_per_m2":66.34,"total_per_m2":268.67,"total_absolute":1746364.97},
 "delta_to_lca":{"lca_per_m2":420,"delta_per_m2_absolute":151.33,"delta_per_m2_percent":56.32,"delta_total_absolute":983635.03}}
```

Response keys: `metadata` (dataset_version, resolved_at, source_loaded_at), `request` (normalised input incl. `input_basis`: `area`|`share`), `annual_mix_budget_per_m2_by_year` (one entry per year in range, same shape as `selected_year_budget`), `selected_year_budget`, `delta_to_lca` (null without LCA), `supported_range`.

## Interpreting results

- Budgets fall steeply by year (DE residential+office mix: ~1133 → ~269 kgCO₂eq/m² from 2020 → 2034), so a later `completion_year` means a stricter budget.
- `delta_*` **positive = project LCA exceeds budget** (over budget); negative = within budget.
- `total_absolute` = `total_per_m2` × total area (kgCO₂eq, not tonnes).
- LCA is compared against `total_per_m2` (embodied + operational). If your LCA covers embodied only, compare to `embodied_per_m2` yourself instead.

## Errors

Shape: `{"error":{"code":"...","message":"..."}}`, HTTP 400 unless noted.
Codes seen live: `UNKNOWN_COUNTRY`, `YEAR_OUT_OF_RANGE`, `UNKNOWN_TYPOLOGY`, `INVALID_JSON`, `MISSING_TOTAL_AREA`, `METHOD_NOT_ALLOWED` (405, e.g. `GET /budget`).
Also documented: `MISSING_COUNTRY`, `MISSING_COMPLETION_YEAR`, `MISSING_TYPOLOGIES`, `EMPTY_TYPOLOGY_INPUT`, `INVALID_TYPOLOGY_VALUES`, `INTERNAL_ERROR` (500).
`UNKNOWN_TYPOLOGY` → re-fetch `?country=<cc>` and use a name from `typologies`; some typology/country/year combos may lack data.

## Notes

- Always send `Content-Type: application/json` on POST.
- The dataset is versioned (`dataset_version: "v1"`); a `"v"` body field is documented as not yet active.
- Cite `dataset_version` and `resolved_at` from `metadata` when reporting numbers.
