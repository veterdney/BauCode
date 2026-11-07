# 03 Exterior walls

All values per m² wall, U = 0.20 W/m²K, 60-year study period, kgCO₂e.
Median EPD per layer.

| Rank | System | A1-A3 | C1–C4 | Replacements | **Life A1–C** | D | Renewable share | Disassembly | Carbon | Sust. | Well. | **Total** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | X7 Timber post + straw bale + clay/lime plaster | −41.4 | 57.7 | 0.0 | **16.3** | −24.0 | 0.80 | 4.5 | 1.00 | 1.00 | 0.81 | **0.94** |
| 2 | X2 Solid timber + wood-fibre ETICS | −83.0 | 123.3 | 29.1 | **69.4** | −68.1 | 0.73 | 4.0 | 0.36 | 0.68 | 0.54 | **0.53** |
| 3 | X8 Monolithic brick + wood-fibre top-up | 53.2 | 16.0 | 21.1 | **90.3** | −15.1 | 0.37 | 3.3 | 0.11 | 0.44 | 0.96 | **0.51** |
| 4 | X1 Timber frame + wood-fibre | −35.2 | 74.1 | 18.9 | **57.8** | −34.3 | 0.61 | 4.0 | 0.50 | 0.66 | 0.21 | **0.46** |
| 5 | X3 Monolithic brick + rock-wool top-up | 63.8 | −1.9 | 13.8 | **75.6** | −2.7 | 0.14 | 2.8 | 0.29 | 0.26 | 0.78 | **0.44** |
| 6 | X6 Aerated concrete + rock-wool top-up | 73.1 | 3.3 | 19.4 | **95.8** | −2.8 | 0.17 | 2.3 | 0.05 | 0.18 | 0.58 | **0.27** |
| 7 | X5 Reinforced concrete + rock-wool ETICS | 51.0 | 5.4 | 18.6 | **74.9** | −2.6 | 0.15 | 2.0 | 0.30 | 0.11 | 0.38 | **0.26** |
| 8 | X4 Sand-lime brick + EPS ETICS | 50.0 | 12.2 | 37.4 | **99.6** | −13.6 | 0.10 | 2.3 | 0.00 | 0.06 | 0.00 | **0.02** |

Source: `results_wall_systems.csv`.

## Reading

- **Carbon.** Bio-based walls store carbon at A1-A3, then release most of it at end of life (C3).
  X7 has the lowest 60-year total because straw and clay add almost no fossil carbon and nothing is replaced.
  X1 has lower raw life carbon (57.8) than X2 (69.4), but X2 scores higher on well-being and renewable share.
- **Mineral walls.** Fossil A1-A3 of 50–73 kgCO₂e/m², no biogenic offset, 14–37 kg more from render/ETICS cycles.
- **EPS ETICS (X4).** Two bonded 40-year cycles, lowest renewable share, and 3× the smog potential (POCP) of the others.
- **Monolithic brick (X8 vs X3).** Wood-fibre top-up beats rock wool on renewables and carbon, and keeps the clay plaster/brick vapour-open.
- **Sensitivity.** X7 stays first with carbon-heavy (0.95) and well-being-heavy (0.91) weights.
  The order of ranks 2–5 changes: X8 passes X2 when well-being is weighted 50 % (0.62 vs 0.53).

## Recommendation

1. **X7** where a straw-bale wall of about 0.4 m total thickness is acceptable.
2. **X2 or X1** as the standard timber option.
   Choose X2 for exposed timber inside and a thinner wall; X1 for the lower carbon.
3. **X8** if a mineral, massive wall is required.
