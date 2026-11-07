# Three-level scoring of six structural systems — 500 m² residential, Germany, 2–3 storeys, 50 years

Level 1: layer (material) · Level 2: building part (incl. layer compatibility) · Level 3: whole building. All scores 0–100, 100 = best.

Environmental facts come from the Ökobaudat 2024-II CSV (`data/OBD_2024_II_2026-11-07T11_09_31.csv`, reduced to `analysis/products.csv`): GWP (`GWPtotal (A2)`), PERT, PENRT, SM, HWD, NHWD, density, modules A1-A3 and C1–C4.
Material properties come from `data/Building material property dataset.csv` (40 materials, M01–M40): λ, μ, service life, technical life, moisture resistance, indoor-air risk, hygric score, installed cost and the U-value references (GModG Anlage 1). Every value that replaced an earlier assumption is in `analysis/levels/dataset_fill_log.csv` with the dataset row and its provenance tag. The dataset itself marks most of these as ASSUMED, TYPICAL or UNVERIFIED-STD, so they are better grounded than my first guesses but still not measured data.
Still **[A]** (ASSUMPTION, mine): sound ratings and Rw estimates, fire and sound requirements, building geometry, materials the dataset does not cover (paint, vapour control layer, sealing foil, gravel, dry fill, roof tile, composite slabs), operating cost, and every build-up. Section 6 lists them.
Read the ranking as a transparent model: Environment is data-driven (OBD); Durability, Cost, Compatibility and Well-being now use the material property dataset, whose own provenance is mostly ASSUMED or TYPICAL.

Files: `alt-1.md` … `alt-6.md` (all layer and compatibility tables), `scores_*.csv` (comma-separated, `.` decimal): alternatives, parts, layers, interfaces.

## 1. Summary

Points per criterion are the volume-weighted mean of the part points (each criterion max 20, total max 100).

| Rank | Alternative | Weighted total | Unweighted | Durability /20 | Environment /20 | Well-being /20 | Cost /20 | Compatibility /20 |
|---|---|---|---|---|---|---|---|---|
| 1 | 6. Timber frame + straw infill + clay plaster | **68.6** | 68.2 (rank 1) | 13.1 | 11.9 | 13.4 | 14.1 | 16.0 |
| 2 | 2. Steel frame + composite slabs + mineral wool | **64.0** | 63.6 (rank 2) | 13.4 | 8.3 | 11.5 | 11.8 | 19.0 |
| 3 | 4. Timber-concrete hybrid (CLT walls + composite slabs) | **59.6** | 60.8 (rank 3) | 10.5 | 9.7 | 10.9 | 10.2 | 18.4 |
| 4 | 3. Monolithic masonry (clay block / sand-lime) + mineral insulation | **58.6** | 58.8 (rank 4) | 12.4 | 6.3 | 11.4 | 10.6 | 18.0 |
| 5 | 1. Reinforced concrete frame + EPS ETICS | **55.8** | 55.5 (rank 6) | 12.0 | 6.0 | 11.0 | 10.1 | 16.7 |
| 6 | 5. Solid timber (CLT) + wood-fibre insulation | **55.3** | 56.1 (rank 5) | 8.4 | 10.6 | 10.7 | 8.9 | 16.5 |

Volume weighting changes the totals by -1.3 to +0.4 points. Ranks differ between weighted and unweighted for: 1 (5 vs 6), 5 (6 vs 5). Ground slab, outer wall, roof and floor carry most of the volume weight; windows carry 1–2 %.

Part scores (0–100):

| Part | 1. RC + EPS | 2. Steel + mineral wool | 3. Masonry | 4. Timber-concrete | 5. Solid timber | 6. Timber frame + straw |
|---|---|---|---|---|---|---|
| Outer wall | 46.7 | 71.3 | 51.4 | 50.4 | 43.8 | 67.2 |
| Inner wall, load-bearing | 60.0 | 68.7 | 59.8 | 66.0 | 63.4 | 69.3 |
| Inner wall, partition | 51.9 | 68.2 | 63.0 | 67.3 | 52.6 | 70.7 |
| Floor slab / ceiling | 60.9 | 60.1 | 61.6 | 58.7 | 54.2 | 73.9 |
| Roof | 57.8 | 65.4 | 64.7 | 62.6 | 58.2 | 74.6 |
| Foundation / ground slab | 59.5 | 59.5 | 59.5 | 59.9 | 59.9 | 60.8 |
| Windows | 51.8 | 51.8 | 51.8 | 61.0 | 61.0 | 61.0 |

Weights (share of building material volume, per alternative):

| Part | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Outer wall | 24 % | 16 % | 28 % | 17 % | 18 % | 20 % |
| Inner wall, load-bearing | 8 % | 7 % | 7 % | 9 % | 8 % | 9 % |
| Inner wall, partition | 7 % | 9 % | 7 % | 8 % | 5 % | 5 % |
| Floor slab / ceiling | 19 % | 16 % | 17 % | 21 % | 24 % | 27 % |
| Roof | 18 % | 19 % | 18 % | 16 % | 16 % | 12 % |
| Foundation / ground slab | 23 % | 30 % | 22 % | 28 % | 28 % | 25 % |
| Windows | 1 % | 2 % | 1 % | 1 % | 1 % | 1 % |

Key data per m² GFA (structure + envelope + windows; windows' volume is small by construction):

| Alternative | GWP A1–A3 (kgCO₂e) | GWP life cycle 50 y (kgCO₂e) | Cost incl. renewals 50 y (€, [A]) |
|---|---|---|---|
| 1. RC + EPS | 198 | 288 | 1087 |
| 2. Steel + mineral wool | 129 | 197 | 930 |
| 3. Masonry | 183 | 243 | 1018 |
| 4. Timber-concrete | -72 | 170 | 987 |
| 5. Solid timber | -151 | 172 | 1009 |
| 6. Timber frame + straw | -16 | 140 | 761 |

## 2. Layer and compatibility tables

One file per alternative, one section per building part: `alt-1.md` … `alt-6.md`. Each section has the layer table, the compatibility table and a short explanation.

## 3. Inner vs. outer wall

| Alt | Outer wall (in→out) | Load-bearing inner wall | Partition | Room-facing layer, 50 % of well-being weight (OW / IL / IP) |
|---|---|---|---|---|
| 1. RC + EPS | RC 200 / EPS 120 / Mineral render 10 | RC 200 | Mineral render 10 / AAC 100 / Mineral render 10 | Paint/covering / Paint/covering / Paint/covering |
| 2. Steel + mineral wool | Gypsum board 25 / VCL / Rock wool 100 / Gypsum board 15 / Rock wool 20 / Mineral render 10 | Gypsum board 25 / Rock wool 100 / Gypsum board 25 | Gypsum board 25 / Rock wool 75 / Gypsum board 25 | Gypsum board / Paint/covering / Paint/covering |
| 3. Masonry | Lime plaster 15 / Brick 365 / Rock wool 20 / Mineral render 10 | Lime plaster 10 / Sand-lime 175 / Lime plaster 10 | Lime plaster 10 / Sand-lime 115 / Lime plaster 10 | Paint/covering / Paint/covering / Paint/covering |
| 4. Timber-concrete | CLT 100 / Rock wool 100 / Mineral render 10 | Gypsum board 15 / CLT 100 / Rock wool 60 / Gypsum board 25 | Gypsum board 25 / KVH 75 / Rock wool 75 / Gypsum board 25 | CLT / Gypsum board / Paint/covering |
| 5. Solid timber | CLT 100 / Wood fibre 110 / Mineral render 10 | CLT 100 / Wood fibre 60 / Gypsum board 25 | CLT 80 | CLT / CLT / CLT |
| 6. Timber frame + straw | Clay plaster 20 / KVH 200 / Straw bale 200 / Lime plaster 25 | Clay plaster 20 / OSB 15 / KVH 140 / Wood fibre 140 / OSB 15 / Clay plaster 20 | Clay plaster 15 / KVH 60 / Wood fibre 60 / Clay plaster 15 | Clay plaster / Clay plaster / Clay plaster |

Why they differ: outer walls must carry weather, insulation (U ≤ 0.20 W/m²K [A]) and moisture control, so they have an outside render or plaster, a thick insulation layer and a vapour-diffusion order that dries outward; inner walls have no U target and instead need mass or lining for sound (separating wall Rw ≥ 53 dB [A]), fire (REI/EI 30 [A]) and thermal mass, and their two faces are both room-facing.

Part scores outer vs. inner (0–100):

| Alt | Outer wall | Inner load-bearing | Partition | Well-being points OW /20 | IL /20 | IP /20 |
|---|---|---|---|---|---|---|
| 1. RC + EPS | 46.7 | 60.0 | 51.9 | 9.9 | 12.8 | 10.4 |
| 2. Steel + mineral wool | 71.3 | 68.7 | 68.2 | 13.9 | 11.4 | 11.6 |
| 3. Masonry | 51.4 | 59.8 | 63.0 | 10.7 | 11.7 | 11.1 |
| 4. Timber-concrete | 50.4 | 66.0 | 67.3 | 9.8 | 12.2 | 11.5 |
| 5. Solid timber | 43.8 | 63.4 | 52.6 | 10.0 | 10.6 | 9.5 |
| 6. Timber frame + straw | 67.2 | 69.3 | 70.7 | 15.1 | 11.6 | 10.7 |

Outer-wall well-being points rank 6 (15.1), 2 (13.9), 3 (10.7), 5 (10.0), 1 (9.9), 4 (9.8); load-bearing inner wall: 1 (12.8), 4 (12.2), 3 (11.7), 6 (11.6), 2 (11.4), 5 (10.6).
The room-facing layer carries 50 % of the weight, so clay plaster (alternative 6) wins on both walls (VOC 5 and buffering 5 [A]); paint on a plastered or concrete surface scores low on buffering [A]. Differences between alternatives 4 and 5 on the outer wall come from the layers behind the same bare CLT (rock wool vs. wood fibre, buffering 2 vs. 4 [A]).

## 4. Score contribution

Share of each criterion in the weighted total, and the part and layer that cost the most points (loss = weight × shortfall from 100).

| Alt | Durab. | Envir. | Well-b. | Cost | Compat. | Part costing most | Layer costing most |
|---|---|---|---|---|---|---|---|
| 1. RC + EPS | 22 % | 11 % | 20 % | 18 % | 30 % | Outer wall (−12.8) | RC in floor slab / ceiling (−4.77) |
| 2. Steel + mineral wool | 21 % | 13 % | 18 % | 18 % | 30 % | Foundation / ground slab (−12.2) | RC in foundation / ground slab (−4.90) |
| 3. Masonry | 21 % | 11 % | 19 % | 18 % | 31 % | Outer wall (−13.8) | Brick in outer wall (−10.29) |
| 4. Timber-concrete | 18 % | 16 % | 18 % | 17 % | 31 % | Foundation / ground slab (−11.2) | Wood-concrete slab in floor slab / ceiling (−5.20) |
| 5. Solid timber | 15 % | 19 % | 19 % | 16 % | 30 % | Foundation / ground slab (−11.3) | CLT in floor slab / ceiling (−5.86) |
| 6. Timber frame + straw | 19 % | 17 % | 20 % | 21 % | 23 % | Foundation / ground slab (−9.9) | RC in foundation / ground slab (−3.16) |

## 5. Conclusion

**Best overall: alternative 6, Timber frame + straw infill + clay plaster** — 68.6 weighted, 68.2 unweighted. It also leads after volume weighting is removed.

Best when one criterion matters most (weighted points /20):

| Priority | Best alternative | Points | Runner-up |
|---|---|---|---|
| Durability | 2. Steel + mineral wool | 13.4 | 6. Timber frame + straw (13.1) |
| Environment | 6. Timber frame + straw | 11.9 | 5. Solid timber (10.6) |
| Well-being | 6. Timber frame + straw | 13.4 | 2. Steel + mineral wool (11.5) |
| Cost | 6. Timber frame + straw | 14.1 | 2. Steel + mineral wool (11.8) |
| Compatibility | 2. Steel + mineral wool | 19.0 | 4. Timber-concrete (18.4) |

Interfaces rated **critical** (each needs the named fix; scores above are before the fix):

| Alt | Part | Interface | Failing check(s) | Fix |
|---|---|---|---|---|
| 1 | Outer wall | EPS / Mineral render | disassembly | structural: render on a soft/polymer/timber base: different movement, reinforcement mesh needed; fire: add a >= 25 mm non-combustible lining or mineral-wool fire barriers; disassembly: plaster/render bonded to polymer insulation: not separable into clean fract |
| 6 | Outer wall | Straw bale / Lime plaster | moisture | moisture: raise sd of the inner vapour control layer (>= 10 m) or move insulation outward; verify by hygrothermal simulation (DIN EN 15026); structural: lime plaster directly on straw: crack risk, needs weather protection and mesh at junctions; fire: add a >=  |

2 of 142 interfaces are critical; the count per alternative is in `scores_interfaces.csv`.


**Best mix.** Taking the best-scoring build-up for each part:

| Part | Taken from | Part score |
|---|---|---|
| Outer wall | 2. Steel + mineral wool | 71.3 |
| Inner wall, load-bearing | 6. Timber frame + straw | 69.3 |
| Inner wall, partition | 6. Timber frame + straw | 70.7 |
| Floor slab / ceiling | 6. Timber frame + straw | 73.9 |
| Roof | 6. Timber frame + straw | 74.6 |
| Foundation / ground slab | 6. Timber frame + straw | 60.8 |
| Windows | 4. Timber-concrete | 61.0 |

Volume-weighted score of this mix: **69.3** vs 68.6 for the best single system (6). The gain of +0.7 points comes only from the outer wall (2) and the window (4); a mix needs junction details (different movement, airtightness, thermal bridges) that this model does not score, so it is an upper bound and not worth the added complexity.
Foundation: all six alternatives use a reinforced concrete ground slab; alternatives 4, 5 and 6 insulate it with foam glass and score highest (60.8 for alternative 6). Alternative 6 therefore already is the concrete-foundation, timber-superstructure combination; swapping in another system's ground slab changes nothing material (68.6).

## 6. Assumptions, data gaps, sensitivity

None of the following is in the OBD data set.

| # | ASSUMPTION | Value used | Reason |
|---|---|---|---|
| 1 | Building geometry per m² GFA | outer wall 0.68, windows 0.17, inner load-bearing wall 0.35, partitions 0.50, floor/ceiling 0.60, roof 0.40, ground slab 0.40 m² | 2–3 storeys, ~200 m² footprint, 20 % glazing; the dataset's 4-storey reference house (wall 0.55, roof 0.27, windows 0.18) does not fit the brief |
| 2 | U-value targets | FILLED from the dataset (GModG Anlage 1 reference building): outer wall 0.28, flat/pitched roof 0.20, ground slab 0.35 W/m²K (earlier assumption 0.20 / 0.14 / 0.25) | GEG was replaced by the GModG on 29 July 2026; component limits carried over. EH40 guideline values (0.16 / 0.11) not used |
| 3 | λ and μ | FILLED: single dataset value where given (RC 2.4, mineral render 1.0, screed 1.4); for ranges the earlier value kept when inside the range, else midpoint (lime plaster μ 25) | dataset provenance mostly TYPICAL / UNVERIFIED-STD (DIN 4108-4 and EN ISO 10456 not opened) |
| 4 | Service life and technical life | FILLED: BNB service life 50 y for structure, masonry, plaster and screed (earlier 100); insulation 50 y inside constructions and 40 y as ETICS; windows 30 y; technical life (80 y for concrete and brick, clay plaster) drives the durability indicator | dataset cites BNB 2017 via a summariser; ≥ 50 y is a lower bound |
| 5 | Moisture resistance, indoor-air risk, hygric score | FILLED: dataset ratings (R_D2, IAQ L–H mapped to 5–1, R_WB3) where present; earlier ratings kept for steel, paint and other gaps | dataset marks all of these ASSUMED; no chamber or buffering data except clay vs lime plaster |
| 6 | Cost | FILLED: dataset mid values converted to €/m³ of layer using the thickness the dataset names (e.g. RC 700 €/m³, CLT 1,350, KVH 1,100, rock wool 441, EPS 403, window 675 €/m²); steel 3,750 €/t | only the insulation costs are CITED (reduco.ai); the rest are ASSUMED ±30 % in the dataset |
| 7 | Not covered by the dataset (earlier assumptions kept) | paint/covering, vapour control layer, sealing foil, gravel, dry fill, roof tile, steel-concrete and wood-concrete composite slabs, sound rating 1–5, fire and sound requirements (REI/EI 30 GK 3; Rw 53/54/40/35/32 dB), operating cost | no dataset row; see `materials.py` |
| 8 | Level-2 criterion weights | five criteria × 20 pts; interface = mean of four checks (good 100, caution 50, critical 0); criterion 5 = mean of interface mean and whole-build-up score | prescribed by the brief |
| 9 | Gravel and fill | natural-stone EPD scaled to 1,600 kg/m³ bulk density; pumice fill EPD | no gravel EPD in OBD |
| 10 | Clay block | fired brick EPD 'Brick (unfilled)' 365 mm; sand-lime brick for inner walls | clay-block unit EPD not found by name; dataset M05 covers hollow clay brick (λ 0.07–0.77, kept 0.12) |
| 11 | Hempcrete | straw bale used in alternative 6 | no hempcrete wall EPD in OBD |
| 12 | Wood-concrete slab | one OBD EPD, 274 kg/m² | only one in OBD |

**Data gaps in OBD:** `SM` is empty for most bio-based EPDs (recycled share looks 0); steel sections 3 EPDs, straw 2, cellulose 2, fired brick 3, roof tile 1, timber window 1, composite slab 1; EPDs mix generic, average and specific datasets and are medians; biogenic carbon (negative A1–A3, positive C3) is shown without dynamic accounting; windows are whole-unit EPDs, so frame, glazing and sealant cannot be scored separately; mass-law sound estimates ignore decoupling.

**Sensitivity** (rank of each alternative, weighted score in brackets):

| Scenario | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Base | 5 (55.8) | 2 (64.0) | 4 (58.6) | 3 (59.6) | 6 (55.3) | 1 (68.6) |
| No compatibility criterion (4 criteria) | 5 (48.9) | 2 (56.3) | 4 (50.8) | 3 (51.5) | 6 (48.4) | 1 (65.7) |
| Unweighted parts | 6 (55.5) | 2 (63.6) | 4 (58.8) | 3 (60.8) | 5 (56.1) | 1 (68.2) |
| All assumed ratings neutral (3) | 6 (53.8) | 2 (61.9) | 4 (56.4) | 3 (58.5) | 5 (55.6) | 1 (66.8) |
| Cost criterion neutral | 6 (55.8) | 2 (62.2) | 4 (58.0) | 3 (59.4) | 5 (56.3) | 1 (64.5) |
| Service lives of timber/bio-based layers and timber windows -30 % | 5 (56.6) | 2 (64.6) | 4 (59.2) | 3 (59.6) | 6 (54.7) | 1 (66.1) |

Monte Carlo (400 draws: cost ±20 %, service life ±20 % per material, each 1–5 rating ±1): first place — 1: 0 %, 2: 2 %, 3: 0 %, 4: 0 %, 5: 0 %, 6: 98 %; top three — 1: 0 %, 2: 100 %, 3: 12 %, 4: 86 %, 5: 1 %, 6: 100 %.