# 07 Product selection

Products come from Ökobaudat 2024-II.
Ranking: lowest A1-A3 + C1–C4 per m² of wall layer, valid until 2026 or later, within the layer's category filter.
Top 3 per layer are in `results_products.csv` (with UUID, dataset type, validity, declaration owner).
The first product below is rank 1; "alt" is rank 2.

## Exterior X7 (preferred)

| Layer | Product | Type | Valid | UUID |
|---|---|---|---|---|
| Plaster (both sides) | Asanto universal clay plaster | specific | 2029 | `2a26078b-9770-4568-bd29-57b847b60e60` |
| alt | Levita clay plaster UP2 | specific | 2029 | `ea1b700e-af18-42b2-96ca-d1ad49c05a6f` |
| Posts | Rubner sawn timber, kiln dried, machine graded | average | 2028 | `1121ded4-ec6e-4e09-b4ce-9410b5325688` |
| Straw bale | FASBA Baustroh 100 kg/m³ | specific | 2029 | `00fe2655-02ad-4ded-925a-af9b8f1a27c8` |
| alt | Straw insulation (Sphera, generic) | generic | 2026 | `e45e2b55-a8c4-4037-bc7d-e3718c4e28f3` |

## Exterior X2 / X1 (fallback)

| Layer | Product | Type | Valid | UUID |
|---|---|---|---|---|
| Timber | Rubner sawn timber, kiln dried | average | 2028 | `1121ded4-ec6e-4e09-b4ce-9410b5325688` |
| alt | Hasslacher finger-jointed solid timber & GLT | average | 2026 | `792a0e85-3893-4aa3-8613-4898b9838fae` |
| Wood-fibre insulation | Wood fibre insulation, dry process (German average) | representative | 2028 | `5bfeefee-ad4c-474e-8efe-fbed20dc776a` |
| alt | best wood FLEX 50 (Holzwerk Schneider) | specific | 2028 | `bdf06e12-4ed3-4f87-b935-9cbbd23a7f6d` |
| Render | Levita topcoat plaster OP 1 | specific | 2029 | `f65425e4-7069-4042-966c-3cb5aa447411` |

Note: the CSV contains sawn and finger-jointed timber, not CLT panels.
For X2 the timber layer stands in for CLT; ask the CLT supplier for its own EPD.

## Exterior X8 (massive mineral option)

| Layer | Product | Type | Valid | UUID |
|---|---|---|---|---|
| Brick | Brick (unfilled), Bundesverband der Deutschen Ziegelindustrie | average | 2026 | `30514538-fcb4-483b-b5d5-c108d2037536` |
| Wood-fibre top-up | Wood fibre insulation, dry process (German average) | representative | 2028 | `5bfeefee-ad4c-474e-8efe-fbed20dc776a` |
| Render | Levita topcoat plaster OP 1 | specific | 2029 | `f65425e4-7069-4042-966c-3cb5aa447411` |
| Interior plaster | Asanto universal clay plaster | specific | 2029 | `2a26078b-9770-4568-bd29-57b847b60e60` |

The unfilled brick EPD expires in 2026; check for the 2027 update.

## Interior P5 (preferred)

| Layer | Product | Type | Valid | UUID |
|---|---|---|---|---|
| Panel | Rammed earth wall (Sphera), **placeholder** | generic | 2026 | `4b42a944-ff7e-4540-a46b-c21074255143` |
| Frame | Rubner sawn timber | average | 2028 | `1121ded4-ec6e-4e09-b4ce-9410b5325688` |
| Insulation | Wood fibre insulation, dry process | representative | 2028 | `5bfeefee-ad4c-474e-8efe-fbed20dc776a` |
| Plaster | Asanto universal clay plaster | specific | 2029 | `2a26078b-9770-4568-bd29-57b847b60e60` |

## Interior P6 / P7

- P6: Rubner sawn timber, `1121ded4-ec6e-4e09-b4ce-9410b5325688` (replace by a solid-wood panel EPD when available).
- P7: Brick (unfilled) `30514538-fcb4-483b-b5d5-c108d2037536`, Asanto clay plaster `2a26078b-9770-4568-bd29-57b847b60e60`, cellulose-based wallcovering `51fa051b-38fb-422f-96e2-b2ee6e6f9445`.

## Why these, not the median

The median was used to rank systems fairly.
Product choice then takes the lowest-carbon EPD per layer.
Prefer **specific** datasets (manufacturer-declared) over **average/generic** ones for the final specification.
