# Wall material selection from Ökobaudat 2024-II

Goal: pick preferred **exterior** and **interior** wall constructions and the products for them.
Walls must work at design time and survive decade-spaced renovations.
Criteria: carbon, sustainability, well-being and health.

## Result

| | Preferred system | Score (0–1) | Practical fallback |
|---|---|---|---|
| Exterior | **X7 Timber post + straw bale + clay/lime plaster** | 0.94 | **X2 Solid timber + wood-fibre ETICS** (0.53) or **X1 Timber frame + wood-fibre** (0.46) |
| Interior | **P5 Clay panels + timber stud + wood-fibre + clay plaster** | 0.78 | **P6 Solid timber panel** (0.76) where acoustics allow |

X7 wins under all three weightings (equal, carbon-heavy, well-being-heavy).
It rests on only two straw EPDs and has the weakest moisture-robustness score of the exterior set.
Treat X2/X1 as the low-risk choice when straw is not permitted or not buildable on site.
Mineral systems (X3–X6) cost 2–4× the life-cycle carbon and lose the biogenic benefit.
X4 (sand-lime brick + EPS ETICS) is last on every criterion.

## Files

| File | Content |
|---|---|
| [01-data-and-scope.md](01-data-and-scope.md) | What the CSV holds, how it was reduced |
| [02-method-and-assumptions.md](02-method-and-assumptions.md) | Layers, thermal target, lifecycle, scoring, all assumptions |
| [03-exterior-walls.md](03-exterior-walls.md) | Exterior ranking and reasoning |
| [04-interior-walls.md](04-interior-walls.md) | Interior ranking and reasoning |
| [06-decade-renovation.md](06-decade-renovation.md) | Replacement events per decade |
| [07-product-selection.md](07-product-selection.md) | Concrete OBD products per layer |
| [08-limitations-next-steps.md](08-limitations-next-steps.md) | What is weak, what to verify |

CSV outputs use `,` as delimiter and `.` as decimal separator.
The source file `data/OBD_2024_II_*.csv` uses `;` and is not changed.

| CSV | Content |
|---|---|
| `products.csv` | One row per latest-version OBD product, A2 indicators per module |
| `results_wall_systems.csv` | Scores and indicators per system |
| `results_layers.csv` | Layer-level carbon, thickness, service life |
| `results_decade_timeline.csv` | Embodied carbon per renovation window |
| `results_products.csv` | Top-3 EPDs per layer for the top-3 systems per class |

Reproduce: `python3 -I analysis/extract.py && python3 -I analysis/run.py` from the repo root.

## Progress log

1. Profiled the CSV. Done.
2. Reduced CSV to one record per product and module (`extract.py`). Done.
3. Defined 8 exterior and 7 interior assemblies, solved insulation thickness (`model.py`). Done.
4. Scored carbon, sustainability, well-being, with sensitivity (`run.py`). Done.
5. Selected products and wrote report. Done.

## Follow-up studies

- `compare6/comparison-report.md`: six structural systems, four equally weighted criteria.
- `levels/report/README.md`: three-level scoring (layer, building part, building) with Glaser checks and layer-compatibility tables; one file per alternative (`alt-1.md` … `alt-6.md`).
  Reproduce: `python3 -I analysis/levels/report.py` from the repo root.
- `eval/README.md`: golden eval set (72 cases) for an AI agent doing this kind of material comparison, with runner, grader and judge.
  Check it: `python3 -I analysis/eval/grade.py --selftest` from the repo root.
