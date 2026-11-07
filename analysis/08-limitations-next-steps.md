# 08 Limitations and next steps

## Limitations

1. **Well-being scores are expert judgement.**
   The CSV has no indoor-air, VOC, moisture or acoustic data.
   Only POCP (smog potential of production) comes from the data.
   Replace the five scores in `run.py` (`WB`) with measured or standardised values.
2. **Thin data for some layers.**
   Straw bale: 2 EPDs. Cellulose: 2. Hemp: 2. Fired brick: 3 (after the end-of-life filter). Clay panels: 4, mixed with rammed earth.
   X7 and P5 are the top picks and rest on the thinnest data.
3. **Biogenic carbon.**
   The 60-year net of timber systems is small because the carbon is released at C3.
   The benefit is real only if the timber is reused, or if timing counts.
   A dynamic LCA or a "storage" accounting would change the order of X1/X2 against the mineral systems.
4. **Assumed values** (λ, service life, disassembly score) are listed in step 02.
   A ±30 % change in service life can reorder ranks 2–5 of the exterior list.
5. **X7 constructability.**
   About 0.4 m thick, needs building-authority acceptance (e.g. a general approval), and has the weakest moisture-robustness score.
6. **Operational energy not modelled.**
   Every exterior system is held at U = 0.20 W/m²K, so heating demand is equal.
7. **Steel-stud drywall and CLT panels** are not in the data under matching categories and were not scored.

## Next steps

1. Replace placeholders: CLT panel EPD, clay board EPD, steel-stud partition.
2. Add moisture (hygrothermal) simulation for X7 and X1 before committing.
3. Run sensitivity on service life ±30 % and on a dynamic biogenic-carbon method.
4. Re-run for other typologies (office).
