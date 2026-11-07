# 01 Data and scope

Source: `data/OBD_2024_II_2026-11-07T11_09_31.csv` (Ökobaudat 2024-II export, 51.5 MB, `;`-separated, latin-1).

## Shape

- 44,973 rows, 4,308 distinct UUIDs.
- One row per product × life-cycle module (A1-A3, A4, A5, B1–B7, C1–C4, D).
- 100 columns: EN 15804+A1 indicators (GWP, PERE, …) and A2 indicators (`GWPtotal (A2)`, `GWPbiogenic (A2)`, `PM (A2)`, `POCP (A2)`, `HTPnc (A2)`, …).
- 3,824 products have an A2 GWP value.
- Declared units differ: m³, kg, m², pieces, m.
  Windows, doors and fittings dominate the piece-based entries and were left out.

## Reduction

`extract.py` keeps the latest version per UUID and modules A1-A3, A4, A5, B4, C1–C4, D.
Rows with a scenario label are used only if no plain row exists for that module.

## Conversion to per-m² of wall layer

`lib.per_m3` converts each declared unit to per-m³ of material:

- m³: as declared.
- kg: × bulk or raw density.
- m²: ÷ layer thickness.

Layer carbon = per-m³ value × layer thickness in the design.
Area-declared products (wall coverings) are used per m² directly.

## Filters that mattered

- Insulation categories include facade panels (e.g. Rockpanel, density ≈ 1,000 kg/m³).
  A density cap (≤ 200 kg/m³) removes them.
  Without it, rock wool looked like 1,353 kgCO₂e/m³.
- Concrete entries with per-m³ values above 1,500 kgCO₂e were dropped as unit errors (one showed 45,279).
- A product needs at least one of C3/C4, so end-of-life is not silently zero.
  This leaves fired brick with only 3 usable EPDs.
