# 04 Interior walls

Non-load-bearing partitions, per m² wall, 60 years, kgCO₂e.
Finish repainting every 12 years is included (4 repaints), which explains most of the "replacements" column for painted systems.

| Rank | System | A1-A3 | C1–C4 | Replacements | **Life A1–C** | D | Renewable share | Disassembly | Total |
|---|---|---|---|---|---|---|---|---|---|
| 1 | P5 Clay panels + timber stud + wood-fibre + clay plaster | −8.2 | 23.0 | 0.0 | **14.8** | −12.8 | 0.61 | 4.8 | **0.78** |
| 2 | P6 Solid timber panel 80 mm | −56.2 | 65.1 | 0.0 | **9.0** | −30.7 | 0.88 | 5.0 | **0.76** |
| 3 | P7 Fired brick 115 + lime plaster | 21.8 | 0.5 | 10.8 | **33.0** | −3.0 | 0.15 | 3.0 | **0.52** |
| 4 | P3 Sand-lime brick 115 + plaster | 29.5 | 3.1 | 21.8 | **54.5** | −2.9 | 0.18 | 2.5 | **0.34** |
| 5 | P2 Timber stud + cellulose + 2×2 plasterboard | −0.2 | 19.7 | 21.3 | **40.9** | −6.3 | 0.35 | 4.3 | **0.31** |
| 6 | P1 Timber stud + rock wool + 2×2 plasterboard | 5.0 | 11.9 | 21.3 | **38.2** | −4.5 | 0.25 | 3.7 | **0.27** |
| 7 | P4 Aerated concrete 100 + plaster | 32.0 | 2.1 | 21.8 | **55.9** | −2.8 | 0.19 | 2.0 | **0.19** |

Source: `results_wall_systems.csv`.

## Reading

- Dry-built, mono-material partitions (P5, P6, P1, P2) can be taken apart and reused when floor plans change over the decades.
  Masonry partitions (P3, P4, P7) are cheap in carbon at the start but cannot be moved without demolition.
- P5 and P6 avoid painted finishes, so no 12-year repaint cycle.
- Plasterboard partitions (P1, P2) are lowest in the well-being score: low moisture buffering and weak summer comfort.
- P7 (fired brick) beats P3 and P4 because the EPD set is small and favourable.
  Only 3 usable fired-brick EPDs exist, so treat its rank as indicative.

## Caveats

- **P5 clay panels:** the "Clay panels / adobe" category mixes adobe and a generic rammed-earth wall.
  The best-ranked entry for the panel layer is the rammed-earth dataset, which is not a 44 mm board.
  Its low carbon (1.1 kg/m²) is therefore uncertain.
  Verify with a manufacturer EPD before specifying.
- **P6 solid timber (80 mm):** poor acoustics (Rw about 30 dB) limit it to low-demand partitions.
  Between dwellings use P5 with extra mass or P7.
- Steel-stud drywall, the most common partition, has no matching category in the CSV and was not scored.

## Recommendation

1. **P5** for general partitions in residential and office layouts that will change.
2. **P6** for low-acoustic, exposed-timber rooms.
3. **P7** (masonry) only for separating walls that need mass and will not move.
