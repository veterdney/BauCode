# Three-level scoring of six structural systems — 500 m² residential, Germany, 2–3 storeys, 50 years

Level 1: layer (material) · Level 2: building part (incl. layer compatibility) · Level 3: whole building. All scores 0–100, 100 = best.

Facts come only from the Ökobaudat 2024-II CSV (`data/OBD_2024_II_2026-11-07T11_09_31.csv`, reduced to `analysis/products.csv`): GWP (`GWPtotal (A2)`), PERT, PENRT, SM, HWD, NHWD, density, modules A1-A3 and C1–C4.
The data set has **no** cost, service-life, VOC, moisture-buffering, sound, fire or vapour-resistance data. These are marked **[A]** (ASSUMPTION) and listed in section 6.
Read the ranking as a transparent model: the Environment criterion and part of Well-being are data-driven; Durability, Cost, Compatibility and the rest of Well-being rest on assumptions.

Files: `alt-1.md` … `alt-6.md` (all layer and compatibility tables), `scores_*.csv` (comma-separated, `.` decimal): alternatives, parts, layers, interfaces.

## 1. Summary

Points per criterion are the volume-weighted mean of the part points (each criterion max 20, total max 100).

| Rank | Alternative | Weighted total | Unweighted | Durability /20 | Environment /20 | Well-being /20 | Cost /20 | Compatibility /20 |
|---|---|---|---|---|---|---|---|---|
| 1 | 6. Timber frame + straw infill + clay plaster | **67.0** | 66.8 (rank 1) | 10.9 | 12.3 | 13.8 | 14.3 | 15.7 |
| 2 | 2. Steel frame + composite slabs + mineral wool | **61.2** | 62.3 (rank 2) | 10.5 | 8.7 | 10.0 | 13.2 | 18.9 |
| 3 | 4. Timber-concrete hybrid (CLT walls + composite slabs) | **57.1** | 58.1 (rank 4) | 9.8 | 9.7 | 8.9 | 10.5 | 18.3 |
| 4 | 3. Monolithic masonry (clay block / sand-lime) + mineral insulation | **56.8** | 59.3 (rank 3) | 11.9 | 6.6 | 10.4 | 10.4 | 17.5 |
| 5 | 5. Solid timber (CLT) + wood-fibre insulation | **55.3** | 55.9 (rank 6) | 8.8 | 10.5 | 10.2 | 9.4 | 16.3 |
| 6 | 1. Reinforced concrete frame + EPS ETICS | **54.5** | 56.3 (rank 5) | 10.7 | 6.0 | 9.8 | 11.4 | 16.6 |

Volume weighting changes the totals by -2.6 to +0.2 points. Ranks differ between weighted and unweighted for: 1 (6 vs 5), 3 (4 vs 3), 4 (3 vs 4), 5 (5 vs 6). Ground slab, outer wall, roof and floor carry most of the volume weight; windows carry 1–2 %.

Part scores (0–100):

| Part | 1. RC + EPS | 2. Steel + mineral wool | 3. Masonry | 4. Timber-concrete | 5. Solid timber | 6. Timber frame + straw |
|---|---|---|---|---|---|---|
| Outer wall | 46.7 | 66.4 | 48.4 | 50.6 | 45.3 | 65.3 |
| Inner wall, load-bearing | 58.8 | 65.4 | 60.0 | 64.4 | 63.4 | 72.5 |
| Inner wall, partition | 52.6 | 64.2 | 62.6 | 63.7 | 53.4 | 72.2 |
| Floor slab / ceiling | 58.0 | 55.0 | 58.7 | 51.4 | 54.0 | 71.8 |
| Roof | 56.6 | 63.6 | 64.0 | 61.9 | 60.6 | 70.6 |
| Foundation / ground slab | 57.4 | 57.4 | 57.4 | 58.6 | 58.6 | 59.6 |
| Windows | 64.3 | 64.3 | 64.3 | 56.0 | 56.0 | 56.0 |

Weights (share of building material volume, per alternative):

| Part | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Outer wall | 25 % | 19 % | 29 % | 20 % | 21 % | 23 % |
| Inner wall, load-bearing | 7 % | 7 % | 6 % | 8 % | 7 % | 8 % |
| Inner wall, partition | 6 % | 8 % | 6 % | 7 % | 4 % | 5 % |
| Floor slab / ceiling | 18 % | 15 % | 16 % | 19 % | 21 % | 24 % |
| Roof | 20 % | 21 % | 19 % | 18 % | 17 % | 15 % |
| Foundation / ground slab | 23 % | 29 % | 22 % | 27 % | 27 % | 24 % |
| Windows | 1 % | 2 % | 1 % | 1 % | 1 % | 1 % |

Key data per m² GFA (structure + envelope + windows; windows' volume is small by construction):

| Alternative | GWP A1–A3 (kgCO₂e) | GWP life cycle 50 y (kgCO₂e) | Cost incl. renewals 50 y (€, [A]) |
|---|---|---|---|
| 1. RC + EPS | 204 | 305 | 873 |
| 2. Steel + mineral wool | 134 | 205 | 793 |
| 3. Masonry | 187 | 261 | 952 |
| 4. Timber-concrete | -66 | 178 | 885 |
| 5. Solid timber | -156 | 192 | 871 |
| 6. Timber frame + straw | -25 | 149 | 785 |

## 2. Layer and compatibility tables

One file per alternative, one section per building part: `alt-1.md` … `alt-6.md`. Each section has the layer table, the compatibility table and a short explanation.

## 3. Inner vs. outer wall

| Alt | Outer wall (in→out) | Load-bearing inner wall | Partition | Room-facing layer, 50 % of well-being weight (OW / IL / IP) |
|---|---|---|---|---|
| 1. RC + EPS | RC 200 / EPS 170 / Mineral render 10 | RC 200 | Mineral render 10 / AAC 100 / Mineral render 10 | Paint/covering / Paint/covering / Paint/covering |
| 2. Steel + mineral wool | Gypsum board 25 / VCL / Rock wool 100 / Gypsum board 15 / Rock wool 70 / Mineral render 10 | Gypsum board 25 / Rock wool 100 / Gypsum board 25 | Gypsum board 25 / Rock wool 75 / Gypsum board 25 | Gypsum board / Paint/covering / Paint/covering |
| 3. Masonry | Lime plaster 15 / Brick 365 / Rock wool 70 / Mineral render 10 | Lime plaster 10 / Sand-lime 175 / Lime plaster 10 | Lime plaster 10 / Sand-lime 115 / Lime plaster 10 | Paint/covering / Paint/covering / Paint/covering |
| 4. Timber-concrete | CLT 100 / Rock wool 150 / Mineral render 10 | Gypsum board 15 / CLT 100 / Rock wool 60 / Gypsum board 25 | Gypsum board 25 / KVH 75 / Rock wool 75 / Gypsum board 25 | CLT / Gypsum board / Paint/covering |
| 5. Solid timber | CLT 100 / Wood fibre 170 / Mineral render 10 | CLT 100 / Wood fibre 60 / Gypsum board 25 | CLT 80 | CLT / CLT / CLT |
| 6. Timber frame + straw | Clay plaster 20 / KVH 280 / Straw bale 280 / Lime plaster 25 | Clay plaster 20 / OSB 15 / KVH 140 / Wood fibre 140 / OSB 15 / Clay plaster 20 | Clay plaster 15 / KVH 60 / Wood fibre 60 / Clay plaster 15 | Clay plaster / Clay plaster / Clay plaster |

Why they differ: outer walls must carry weather, insulation (U ≤ 0.20 W/m²K [A]) and moisture control, so they have an outside render or plaster, a thick insulation layer and a vapour-diffusion order that dries outward; inner walls have no U target and instead need mass or lining for sound (separating wall Rw ≥ 53 dB [A]), fire (REI/EI 30 [A]) and thermal mass, and their two faces are both room-facing.

Part scores outer vs. inner (0–100):

| Alt | Outer wall | Inner load-bearing | Partition | Well-being points OW /20 | IL /20 | IP /20 |
|---|---|---|---|---|---|---|
| 1. RC + EPS | 46.7 | 58.8 | 52.6 | 9.2 | 12.6 | 9.7 |
| 2. Steel + mineral wool | 66.4 | 65.4 | 64.2 | 12.2 | 10.1 | 10.4 |
| 3. Masonry | 48.4 | 60.0 | 62.6 | 10.1 | 12.3 | 11.8 |
| 4. Timber-concrete | 50.6 | 64.4 | 63.7 | 6.8 | 10.9 | 10.5 |
| 5. Solid timber | 45.3 | 63.4 | 53.4 | 10.5 | 10.5 | 7.0 |
| 6. Timber frame + straw | 65.3 | 72.5 | 72.2 | 16.5 | 13.8 | 13.3 |

Outer-wall well-being points rank 6 (16.5), 2 (12.2), 5 (10.5), 3 (10.1), 1 (9.2), 4 (6.8); load-bearing inner wall: 6 (13.8), 1 (12.6), 3 (12.3), 4 (10.9), 5 (10.5), 2 (10.1).
The room-facing layer carries 50 % of the weight, so clay plaster (alternative 6) wins on both walls (VOC 5 and buffering 5 [A]); paint on a plastered or concrete surface scores low on buffering [A]. Differences between alternatives 4 and 5 on the outer wall come from the layers behind the same bare CLT (rock wool vs. wood fibre, buffering 2 vs. 4 [A]).

## 4. Score contribution

Share of each criterion in the weighted total, and the part and layer that cost the most points (loss = weight × shortfall from 100).

| Alt | Durab. | Envir. | Well-b. | Cost | Compat. | Part costing most | Layer costing most |
|---|---|---|---|---|---|---|---|
| 1. RC + EPS | 20 % | 11 % | 18 % | 21 % | 30 % | Outer wall (−13.6) | EPS in outer wall (−5.54) |
| 2. Steel + mineral wool | 17 % | 14 % | 16 % | 21 % | 31 % | Foundation / ground slab (−12.4) | RC in foundation / ground slab (−4.57) |
| 3. Masonry | 21 % | 12 % | 18 % | 18 % | 31 % | Outer wall (−15.2) | Brick in outer wall (−9.94) |
| 4. Timber-concrete | 17 % | 17 % | 16 % | 18 % | 32 % | Foundation / ground slab (−11.4) | Wood-concrete slab in floor slab / ceiling (−5.71) |
| 5. Solid timber | 16 % | 19 % | 18 % | 17 % | 30 % | Outer wall (−11.5) | Wood fibre in outer wall (−5.81) |
| 6. Timber frame + straw | 16 % | 18 % | 21 % | 21 % | 23 % | Foundation / ground slab (−9.8) | Straw bale in outer wall (−3.56) |

## 5. Conclusion

**Best overall: alternative 6, Timber frame + straw infill + clay plaster** — 67.0 weighted, 66.8 unweighted. It also leads after volume weighting is removed.

Best when one criterion matters most (weighted points /20):

| Priority | Best alternative | Points | Runner-up |
|---|---|---|---|
| Durability | 3. Masonry | 11.9 | 6. Timber frame + straw (10.9) |
| Environment | 6. Timber frame + straw | 12.3 | 5. Solid timber (10.5) |
| Well-being | 6. Timber frame + straw | 13.8 | 3. Masonry (10.4) |
| Cost | 6. Timber frame + straw | 14.3 | 2. Steel + mineral wool (13.2) |
| Compatibility | 2. Steel + mineral wool | 18.9 | 4. Timber-concrete (18.3) |

Interfaces rated **critical** (each needs the named fix; scores above are before the fix):

| Alt | Part | Interface | Failing check(s) | Fix |
|---|---|---|---|---|
| 1 | Outer wall | EPS / Mineral render | disassembly | structural: render on a soft/polymer/timber base: different movement, reinforcement mesh needed; fire: add a >= 25 mm non-combustible lining or mineral-wool fire barriers; disassembly: plaster/render bonded to polymer insulation: not separable into clean fract |
| 6 | Outer wall | Straw bale / Lime plaster | moisture | moisture: raise sd of the inner vapour control layer (>= 10 m) or move insulation outward; verify by hygrothermal simulation (DIN EN 15026); structural: lime plaster directly on straw: crack risk, needs weather protection and mesh at junctions; fire: add a >=  |

2 of 142 interfaces are critical; the count per alternative is in `scores_interfaces.csv`.


**Best mix.** Taking the best-scoring build-up for each part:

| Part | Taken from | Part score |
|---|---|---|
| Outer wall | 2. Steel + mineral wool | 66.4 |
| Inner wall, load-bearing | 6. Timber frame + straw | 72.5 |
| Inner wall, partition | 6. Timber frame + straw | 72.2 |
| Floor slab / ceiling | 6. Timber frame + straw | 71.8 |
| Roof | 6. Timber frame + straw | 70.6 |
| Foundation / ground slab | 6. Timber frame + straw | 59.6 |
| Windows | 1. RC + EPS | 64.3 |

Volume-weighted score of this mix: **67.4** vs 67.0 for the best single system (6). The gain of +0.4 points comes only from the outer wall (2) and the window (1); a mix needs junction details (different movement, airtightness, thermal bridges) that this model does not score, so it is an upper bound and not worth the added complexity.
Foundation: all six alternatives use a reinforced concrete ground slab; alternatives 4, 5 and 6 insulate it with foam glass and score highest (59.6 for alternative 6). Alternative 6 therefore already is the concrete-foundation, timber-superstructure combination; swapping in another system's ground slab changes nothing material (67.0).

## 6. Assumptions, data gaps, sensitivity

None of the following is in the OBD data set.

| # | ASSUMPTION | Value used | Reason |
|---|---|---|---|
| 1 | Building geometry per m² GFA | outer wall 0.68, windows 0.17, inner load-bearing wall 0.35, partitions 0.50, floor/ceiling 0.60, roof 0.40, ground slab 0.40 m² | 2–3 storeys, ~200 m² footprint, 20 % glazing; no plan given |
| 2 | U-value targets | outer wall 0.20, roof 0.14, ground slab 0.25 W/m²K; windows not solved | stricter than GEG reference values (0.28/0.20/0.35) so the walls need no early retrofit |
| 3 | Thermal conductivity λ | rock wool 0.036, EPS/XPS 0.035, wood fibre 0.040, cellulose 0.039, straw 0.052, foam glass 0.045, brick 0.12, RC 2.0, CLT/KVH 0.13 | no λ in OBD; typical declared values |
| 4 | Vapour resistance μ / sd | e.g. RC 80, brick 8, CLT 50, EPS 40, rock wool 1, wood fibre 5, straw 2; VCL sd 10 m (pitched) or 100 m (flat roof), roof membrane sd 100 m | no μ in OBD; Glaser steady state, Berlin-type design climate per DIN 4108-3 (−5 °C/80 %, 20 °C/50 %, 90 d) |
| 5 | Layer thicknesses and build-ups | see alt-*.md | typical practice; thickness of insulation solved and rounded up to 10 mm |
| 6 | Fire requirement | REI/EI 30 (Gebäudeklasse 3) | 2–3 storeys, ≤ 7 m; GK 4 would need REI 60 and change timber ratings |
| 7 | Sound requirement | Rw ≥ 53 dB separating wall, 54 dB floor, 40 dB outer wall/roof, 35 dB partition, 32 dB window | DIN 4109 style; estimated by mass law R = 32.4 lg m′ − 26 (+4 dB floating screed), or typical framed values for lightweight walls |
| 8 | Service lives (y) | structure 100 (CLT/KVH 100, composite slabs 100), render/ETICS 40, plasterboard 50, paint 12, membranes 30–50, windows 35 | no service-life field in OBD |
| 9 | Ratings 1–5 for moisture/fire/pest, VOC, buffering, sound contribution | per material in `materials.py` | qualitative judgement; OBD has no emissions or hygric data |
| 10 | Cost (€/m³, €/m², € per renewal) | e.g. RC 470 €/m³, CLT 850, rock wool 180, render 4,600 (≈ 55 €/m²), plastic window 520 €/m², timber window 780 €/m² | no cost data in OBD; indicative German installed prices |
| 11 | Operating-cost effect | none (equal for all alternatives) | same GEG standard, floor plan and U-values; not included as an indicator |
| 12 | Level-2 criterion weights | five criteria × 20 pts; interface = mean of four checks (good 100, caution 50, critical 0); criterion 5 = mean of interface mean and whole-build-up score | prescribed by the brief |
| 13 | Gravel and fill | natural-stone EPD scaled to 1,600 kg/m³ bulk density; pumice fill EPD | no gravel EPD in OBD |
| 14 | Clay block | fired brick EPD 'Brick (unfilled)' 365 mm; sand-lime brick for inner walls | clay-block unit EPD not found by name; swap allowed |
| 15 | Hempcrete | straw bale used in alternative 6 | no hempcrete wall EPD in OBD (hemp stone: 2 EPDs) |
| 16 | Wood-concrete slab | one OBD EPD, 274 kg/m² | only one in OBD |

**Data gaps in OBD:** `SM` is empty for most bio-based EPDs (recycled share looks 0); steel sections 3 EPDs, straw 2, cellulose 2, fired brick 3, roof tile 1, timber window 1, composite slab 1; EPDs mix generic, average and specific datasets and are medians; biogenic carbon (negative A1–A3, positive C3) is shown without dynamic accounting; windows are whole-unit EPDs, so frame, glazing and sealant cannot be scored separately; mass-law sound estimates ignore decoupling.

**Sensitivity** (rank of each alternative, weighted score in brackets):

| Scenario | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Base | 6 (54.5) | 2 (61.2) | 4 (56.8) | 3 (57.1) | 5 (55.3) | 1 (67.0) |
| No compatibility criterion (4 criteria) | 6 (47.4) | 2 (52.9) | 3 (49.1) | 5 (48.5) | 4 (48.7) | 1 (64.2) |
| Unweighted parts | 5 (56.3) | 2 (62.3) | 3 (59.3) | 4 (58.1) | 6 (55.9) | 1 (66.8) |
| All assumed ratings neutral (3) | 6 (53.7) | 2 (60.8) | 5 (54.4) | 3 (57.9) | 4 (56.3) | 1 (64.9) |
| Cost criterion neutral | 6 (53.1) | 2 (58.1) | 4 (56.4) | 3 (56.6) | 5 (55.8) | 1 (62.7) |
| Service lives of timber/bio-based layers and timber windows -30 % | 4 (56.7) | 2 (62.4) | 3 (59.0) | 5 (56.6) | 6 (54.3) | 1 (66.6) |

Monte Carlo (400 draws: cost ±20 %, service life ±20 % per material, each 1–5 rating ±1): first place — 1: 0 %, 2: 0 %, 3: 0 %, 4: 0 %, 5: 0 %, 6: 100 %; top three — 1: 0 %, 2: 100 %, 3: 8 %, 4: 80 %, 5: 12 %, 6: 100 %.