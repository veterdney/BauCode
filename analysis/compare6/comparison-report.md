# Comparative scoring of six structural systems — 500 m² residential, Germany, 50 years

Scope per m² gross floor area (GFA): **structure** (slabs, bearing walls/frame) **+ opaque exterior envelope** (0.6 m² per m² GFA, U = 0.20 W/m²K for every alternative).
Windows, services, partitions, floor finishes and foundations are identical in function and excluded.
Facts come only from the Ökobaudat 2024-II export (`data/OBD_2024_II_2026-11-07T11_09_31.csv (processed to analysis/products.csv)`).
Everything not in that data set is marked **ASSUMPTION** and listed in section 6.

**Read this first:** the data set contains no cost, service-life, VOC, moisture-buffering or fire data.
Only the Environment criterion and two Well-being indicators (thermal mass, acoustic mass) are data-driven.
Durability and Cost, and two Well-being indicators, rest on assumptions. The ranking is therefore a transparent model, not a measured result.

## 1. Summary

| Rank | Alternative | Durability /25 | Environment /25 | Well-being /25 | Cost /25 | **Total /100** |
|---|---|---|---|---|---|---|
| 1 | 6 Timber frame + straw + clay plaster | 12.5 | 19.6 | 9.4 | 16.0 | **57.5** |
| 2 | 3 Monolithic masonry + mineral insulation | 12.5 | 4.6 | 19.5 | 12.5 | **49.1** |
| 3 | 4 Timber-concrete hybrid (CLT walls + composite slab) | 13.5 | 11.9 | 9.1 | 8.1 | **42.6** |
| 4 | 1 RC frame + EPS ETICS | 12.5 | 2.9 | 15.6 | 11.2 | **42.2** |
| 5 | 5 Solid timber (CLT) + wood-fibre | 13.5 | 14.3 | 6.9 | 6.4 | **41.1** |
| 6 | 2 Steel frame + composite slab + mineral wool | 13.5 | 8.5 | 8.4 | 8.6 | **39.0** |

Files: `scores.csv`, `indicators_raw.csv`, `indicators_scored.csv` (comma-separated, `.` decimal).

## 2. Score contribution

Share = criterion points ÷ total. Largest loss = 25 minus points; the criterion with the biggest loss is shown.

| Alternative | Durability | Environment | Well-being | Cost | Costs the most points |
|---|---|---|---|---|---|
| 6 Timber frame + straw + clay plaster | 22 % | 34 % | 16 % | 28 % | Well-being (−15.6) |
| 3 Monolithic masonry + mineral insulation | 25 % | 9 % | 40 % | 25 % | Environment (−20.4) |
| 4 Timber-concrete hybrid (CLT walls + composite slab) | 32 % | 28 % | 21 % | 19 % | Cost (−16.9) |
| 1 RC frame + EPS ETICS | 30 % | 7 % | 37 % | 26 % | Environment (−22.1) |
| 5 Solid timber (CLT) + wood-fibre | 33 % | 35 % | 17 % | 15 % | Cost (−18.6) |
| 2 Steel frame + composite slab + mineral wool | 35 % | 22 % | 22 % | 22 % | Well-being (−16.6) |
## 3. Criterion explanations

Raw values are per m² GFA (structure + opaque envelope) unless stated.
Normalisation: min–max across the six alternatives, inverted where lower is better. Scored values are in `indicators_scored.csv`.
Source key: **[OBD]** = OBD 2024-II CSV, median of the matching EPDs (filters and UUIDs in `sources_uuids.json`), columns named in the table. **[A]** = ASSUMPTION (section 6).

Alternatives: **1** RC frame + EPS ETICS · **2** Steel frame + composite slab + mineral wool · **3** Monolithic masonry + mineral insulation · **4** Timber–concrete hybrid · **5** Solid timber (CLT) + wood fibre · **6** Timber frame + straw + clay plaster.

### 3.1 Durability / lifespan (25 pts)

Definition: how long the structure serves, how often parts must be renewed, how well it resists moisture, fire and pests, and whether it can be adapted or reused.
The data set has no service-life or hazard field, so all four indicators except the event count rest on assumptions.

| Indicator | Source | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| Structure service life, y | [A] | 100 | 80 | 100 | 80 | 80 | 60 |
| Envelope renewal events in 50 y (count) | [A] layer lives, count derived | 6 | 6 | 6 | 2 | 2 | 0 |
| Moisture/fire/pest resistance (1–5) | [A] | 5 | 4 | 5 | 4 | 3 | 2 |
| Adaptability / reuse (1–5) | [A] | 2 | 5 | 2 | 3 | 4 | 5 |
| **Points /25** | | **12.5** | **13.5** | **12.5** | **13.5** | **13.5** | **12.5** |

Reasoning: massive systems lead on life and resistance but lose on adaptability and on repainting/render cycles (painted interior surface every 12 y, render and ETICS every 40 y).
Timber and straw walls have few renewal events (clay plaster needs no repaint) but a shorter assumed life and higher moisture risk.
The criterion is nearly flat (12.5–13.5) because the trade-offs cancel out.

### 3.2 Environmental impact (25 pts)

Definition: embodied carbon and primary energy over the 50-year life cycle, renewable and recycled content, and end-of-life burden.
All six indicators are data-driven.

| Indicator | OBD field / module | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| GWP A1–A3, kgCO₂e/m² | `GWPtotal (A2)`, A1-A3 (incl. biogenic uptake) | 119.8 | 79.7 | 104.2 | −116.4 | −195.6 | −105.9 |
| GWP life cycle A1–C incl. replacements, kgCO₂e/m² | `GWPtotal (A2)`, A1-A3 + C1–C4, × renewals | 141.0 | 85.6 | 109.7 | 78.3 | 68.7 | 25.2 |
| Non-renewable primary energy, MJ/m² | `PENRT`, A1-A3 | 1,185 | 983 | 991 | 1,017 | 916 | 406 |
| Renewable primary-energy share | `PERT` ÷ (`PERT`+`PENRT`), A1-A3 | 0.16 | 0.16 | 0.17 | 0.74 | 0.80 | 0.83 |
| Secondary-material share (mass) | `SM` ÷ mass (`Rohdichte`×volume), A1-A3 | 0.04 | 0.14 | 0.07 | 0.03 | 0.00 | 0.00 |
| Landfill waste at end of life, kg/m² | `HWD`+`NHWD`, C1–C4 | 21.6 | 32.5 | 38.9 | 28.2 | 19.7 | 0.3 |
| **Points /25** | | **2.9** | **8.5** | **4.6** | **11.9** | **14.3** | **19.7** |

Total life-cycle GWP for 500 m²: 1: 70.5 t · 2: 42.8 t · 3: 54.9 t · 4: 39.2 t · 5: 34.4 t · 6: 12.6 t CO₂e (A1–C, module D excluded).
Module D (not scored), kgCO₂e/m²: 1: +1.3 · 2: −4.1 · 3: +4.3 · 4: −79.8 · 5: −126.5 · 6: −53.2.

Reasoning:
- Timber and straw show negative A1-A3 values (biogenic uptake) but release most of it in C3, so the life-cycle gap is much smaller than the A1-A3 gap. Alternative 5 has the lowest A1-A3 yet not the lowest life-cycle total.
- Steel has the highest recycled share (14 %) but concrete slabs and rock wool add fossil carbon.
- `SM` is empty for most bio-based EPDs, so a 0.00 share means "not declared", not "none". This indicator is weak.
- EPS and 6 replacement events put alternative 1 last on carbon and primary energy.

### 3.3 Occupant well-being (25 pts)

Definition: indoor air quality, summer comfort, moisture buffering, acoustics.

| Indicator | Source | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| VOC / formaldehyde (1–5, 5 = lowest emissions) | [A] | 4 | 4 | 5 | 3 | 3 | 4 |
| Thermal mass, kg/m² GFA | [OBD] `Rohdichte` × assumed volumes | 1,034 | 325 | 785 | 333 | 152 | 124 |
| Moisture buffering (1–5) | [A] | 1 | 2 | 3 | 4 | 5 | 5 |
| Acoustic mass of slab, kg/m² (mass-law proxy) | [OBD] `Rohdichte`/`Flaechengewicht` | 528 | 228 | 480 | 274 | 85 | 49 |
| **Points /25** | | **15.6** | **8.4** | **19.5** | **9.1** | **6.9** | **9.4** |

Reasoning: mass drives two indicators, so masonry and concrete lead; timber and straw lose.
The mass proxy ignores decoupled floors and floating screeds, which let light timber floors reach good impact sound insulation. It understates timber.
Straw and CLT win on moisture buffering; the CLT hybrid and CLT lose points on glue-related emissions (assumed).

### 3.4 Lifecycle cost (25 pts)

Definition: construction cost, maintenance/replacement cost and operating-cost effects over 50 years.
**The data set has no cost data.** All values are assumptions.

| Indicator | Source | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| Construction cost (structure + envelope), €/m² GFA | [A] | 820 | 880 | 790 | 940 | 980 | 900 |
| Maintenance/renewal over 50 y, €/m² GFA | [A] unit costs × events from [A] lives | 110 | 110 | 110 | 81 | 81 | 0 |
| Operating-cost effect | same GEG standard → equal | 0 | 0 | 0 | 0 | 0 | 0 |
| **Points /25** | | **11.2** | **8.6** | **12.5** | **8.1** | **6.4** | **16.0** |

Reasoning: masonry is cheapest to build; CLT is the dearest. Alternative 6 has no renewal events and so no maintenance cost, which lifts it despite a mid-range build cost.
The operating indicator is identical for all, so every alternative gets a neutral 50 on it.

## 4. Alternative profiles

**1 RC frame + EPS ETICS (42.2, rank 4).** Strong on mass, hence thermal comfort and acoustics, and on assumed service life. Worst environmental profile: highest life-cycle carbon (141 kgCO₂e/m²) and non-renewable primary energy, lowest renewable share. Six renewal events in 50 years (paint, render, bonded EPS system). Trade-off: robust and durable, carbon-heavy.

**2 Steel frame + composite slab + mineral wool (39.0, rank 6).** Best adaptability and the highest recycled share, mid carbon. Low thermal mass and light slabs reduce well-being points, and the assumed cost is high. No criterion wins; it is last overall, but only 2 points behind rank 5.

**3 Monolithic masonry + mineral insulation (49.1, rank 2).** Best well-being in this model (mass, low emissions, moderate buffering) and the lowest construction cost. Environment is weak (110 kgCO₂e/m², 0.17 renewable share) and adaptability is low. Its rank-2 position depends on the assumed VOC and cost values (see section 6).

**4 Timber–concrete hybrid (42.6, rank 3).** Cuts envelope renewal events to a third of the massive systems and has a good renewable share (0.74). Dearer than masonry and concrete. Composite slab gives more mass than pure timber. Based on one OBD composite-slab EPD, so it is a thin data point.

**5 Solid timber CLT + wood fibre (41.1, rank 5).** Best carbon profile among the load-bearing timber options (68.7 kgCO₂e/m²) and lowest A1-A3, with joint-highest moisture buffering. Costs the most (assumed 980 €/m²), lowest mass and acoustic proxy, and moderate moisture risk. Weak on cost and well-being proxies, which drag the total.

**6 Timber frame + straw + clay plaster (57.5, rank 1).** Lowest life-cycle carbon (25 kgCO₂e/m²), lowest primary energy, highest renewable share, nearly no waste and no renewal events. Weakest on durability inputs (assumed 60-year life, moisture risk) and on mass-based well-being proxies. Straw rests on two EPDs, and the build-up is thick. Its lead is large (8 points) but depends on the carbon data being right.

## 5. Conclusion

**Best overall: alternative 6, timber frame with straw infill and clay plaster (57.5 / 100).**
It wins Environment (19.7) and Cost (16.0); it is mid-to-low on Durability (12.5) and Well-being (9.4).
In 2,000 random draws that vary the assumed ratings (±1), service life (±20 %), construction cost (±15 %) and maintenance cost (±30 %), alternative 6 ranks first in 95 % of draws and is always in the top 3.
Ranks 2 to 5 are within 8 points and change with the assumptions: masonry is top-3 in 75 % of draws, the hybrid in 54 %, CLT in 37 %, RC in 25 %, steel in 10 %.

Best if one criterion matters most:

| Priority | Best | Points | Note |
|---|---|---|---|
| Durability | 2, 4, 5 (tie) | 13.5 | Criterion is nearly flat (12.5–13.5); no clear winner |
| Environmental impact | 6 Timber + straw | 19.7 | Followed by 5 (14.3) and 4 (11.9) |
| Occupant well-being | 3 Masonry | 19.5 | Then 1 RC (15.6) |
| Lifecycle cost | 6 Timber + straw | 16.0 | Then 3 Masonry (12.5); the cost data are all assumptions |

## 6. Assumptions and data gaps

None of these values are in the OBD data set.

| # | ASSUMPTION | Value used | Reason | Effect of a different value |
|---|---|---|---|---|
| 1 | Wall and slab quantities per m² GFA | exterior wall 0.6 m², interior bearing wall 0.4 m²; slab 0.22 m³ RC / 0.20 m³ masonry / 0.09 m³ composite / 0.18 m³ CLT / 0.07 m³ KVH + 0.022 m³ OSB; steel frame 28 kg/m²; rebar 100–110 kg/m³ | No project design given; typical residential values | Changes absolute carbon, little effect on order unless timber slabs are much thicker |
| 2 | U-value of the exterior wall | 0.20 W/m²K for all; insulation thickness solved with λ: wood fibre 0.040, rock wool 0.036, EPS 0.035, straw 0.052 | GEG-compliant, same for all alternatives | A looser U cuts insulation carbon equally |
| 3 | Structure service life | 100 / 80 / 100 / 80 / 80 / 60 y | No service-life field in OBD | Neutralising items 3, 5, 6 and 7 together (life 90 y, all ratings 3, cost 870) leaves alternative 6 first at 58.2 |
| 4 | Layer service lives | paint 12 y, render/ETICS 40 y, plasterboard 50 y | Typical practice | Longer lives remove renewals and favour massive systems |
| 5 | Moisture/fire/pest and adaptability ratings (1–5) | see 3.1 | Qualitative judgement | ±1 on one alternative moves its durability points by up to about 2 |
| 6 | VOC and moisture-buffering ratings (1–5) | see 3.3 | OBD has no emission or hygric data | Neutral ratings (all 3) drop masonry to rank 5 (38.7) and leave alternative 6 first (58.2) |
| 7 | Construction cost, €/m² GFA | 790 / 820 / 880 / 900 / 940 / 980 | No cost data in OBD | Equal costs lift masonry and hybrid to 45.0 and CLT to 45.3; alternative 6 stays first (58.2) |
| 8 | Renewal cost per event | paint 12, render 65, insulation 70, plasterboard 35 €/m² wall | No cost data | Higher renewal cost widens alternative 6's cost lead |
| 9 | Operating-cost effect | equal, 0 | Same GEG standard and floor plan | Any real difference (e.g. airtightness, cooling load) would shift cost points |
| 10 | Study scope | structure + opaque envelope only | Same for all; windows, services, partitions excluded | Including them adds a near-constant offset |
| 11 | Clay block | not available as a unit-product in OBD; sand-lime brick 175 mm for bearing walls and fired brick "Brick (unfilled)" 365 mm for the exterior | Swap permitted by the brief | Another unit changes alternative 3 only |
| 12 | Hempcrete | not in OBD as a wall material; straw bale used instead (alternative 6) | Brief allows hempcrete or straw | Hemp stone (2 EPDs) would be similar in carbon |
| 13 | Timber-concrete hybrid slab | one OBD wood-concrete composite slab EPD (274 kg/m²) | Only one in OBD | A different slab shifts alternative 4 by a few points |

Data gaps inside OBD:
- `SM` (secondary material) is empty for most bio-based EPDs, so the recycled-share indicator undervalues them.
- CLT EPDs are 5; straw bale 2; hemp blocks 2; steel sections 3; composite slab 1.
- Medians across EPDs mix generic, average and specific datasets.
- Biogenic carbon: GWPtotal (A2) shows uptake in A1-A3 and release in C3. A 50-year view without dynamic carbon accounting shows the timber benefit mainly as timing, not net storage.
- The acoustic and thermal-mass indicators use mass only, a crude proxy.

Reproduce from the repo root: `python3 -I analysis/compare6/score6.py && python3 -I analysis/compare6/report6.py`.
