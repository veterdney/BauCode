# Claude Impact Lab Berlin 2026

Materials of the [Berlin | Claude Impact Lab x Foresight Institute — AI Research Loops for Open Science Problems](https://luma.com/claude-wmbq),
co-hosted by [Foresight Institute](https://foresight.org/).

Scientists bring the open problems in their research they most want AI help with,
and we spend a day building on them.

## BauCode: website first, then added checks

1. Open the [team website](docs/index.html) locally; it links to the human [lab](docs/lab.html) and [research loop](docs/loop.html). The authored site uses JavaScript and external Google Fonts. Its exploratory rankings are not validated recommendations or our evaluation method.
2. Open the [sparse presentation](demo/presentation/index.html) for the bounded research loop and added checks. This wrapper is offline/no-JavaScript and shows **saved outputs**, not a live calculator.
3. Follow the [synthetic demo guide](demo/README.md) and [replaceable input schema](docs/INPUT_SCHEMA.md). These links point to repository files, not an asserted deployed Pages URL.

### Quick run from the repository root

Python 3, standard library only; no pip packages or API required. These terminal commands genuinely regenerate outputs:

```sh
# Linux / macOS
python3 demo/run_demo.py
python3 demo/run_demo.py --input demo/input/synthetic_wall_replaced.json --out demo/output/replaced
python3 demo/run_gallery.py
```

```powershell
# Windows, if the Python launcher is installed
py -3 demo/run_demo.py
py -3 demo/run_demo.py --input demo/input/synthetic_wall_replaced.json --out demo/output/replaced
py -3 demo/run_gallery.py
```

Default/replacement saved A1-A3 totals are 185/230 kgCO2e for the same declared 10 m2 wall area; that is not functional equivalence. Outputs are under `demo/output/`; [gallery HTML](demo/output/gallery/gallery.html) is viewable without Python. Opening saved HTML/evidence does not execute tests.

### Evidence and limits

- [Recorded commands, exits and limitations](review-evidence/landscape-final-20261107/REPORT.md); [presentation-only source binding](review-evidence/sparse-presentation-20261107/SOURCE_BINDING.json). Audits belong to prior recorded candidates and were content-bound to accepted versions, not rerun for this docs-only change. No CI-green claim.
- Original exact20 remains **19 PASS / 1 FAIL** (78/79 required probes); original gallery **28 PASS / 1 FAIL**. Separate historical preservation v1 covers 50 paths with four mutation controls; it is not comparable all-green20. Optional probes remain 1 PASS / 4 UNKNOWN / 2 NOT RUN.
- **The historical 50-path PASS is not a new audit or a whole-repository guarantee.** The pinned policy protects selected human-main delta paths (including `analysis/README.md`), not this root README or `demo/README.md`. No new preservation PASS is claimed, and no checker/oracle was weakened or retargeted; [policy scope](tests/HUMAN_MAIN_PRESERVATION_V1_REPORT.md) remains unchanged.
- Invented SYNTHETIC data and exposed agent-derived expectations, not human-reviewed GOLD or holdout. No scientific, general-accuracy, health or compliance validation. The 200 generated records / 25 assemblies are a demonstration, not independent evaluations.
- Selected A1-A3 + C1-C4 subtotal only; A4/A5/B excluded, not full lifecycle. D stays separate and is never netted against A-C; UNKNOWN is not zero. Conservative C/D coupling and DRAFT policies remain in the schema. The legacy pipeline still needs its missing `analysis/products.csv`; the synthetic demo does not.

## Presentation

The [main presentation](https://docs.google.com/presentation/d/1P4Zf5t-wDYfVolJKKEEeF8e5_DLYYiZpZCzCV7XdRec/edit?usp=sharing) of the event.

## Building research loops

See [Building research loops with Claude](RESEARCH-LOOPS.md) for practical hints on keeping Claude working on your problem: `/goal`, `/loop` and more.

## Join the conversation

[![Discord](https://img.shields.io/discord/811561179280965673?logo=discord&logoColor=white)](https://discord.gg/vQktqqN2Vn)

Questions, team formation, or want to keep your research loop going after the event?
Join the [xemantic Discord server](https://discord.gg/vQktqqN2Vn) and say hi.

## Links

- [Foresight Institute](https://foresight.org/)
- [Claude Science](https://claude.com/product/claude-science)
- [Æthos](https://aethos.org/)

## Licenses of your projects

By default, everything built today is shared under
Apache 2.0 for code and CC BY 4.0 for text,
and donated to Foresight Institute.
Your team may choose another open-source license
if every member agrees:
add the license file to your repository and name it in your submission issue.
If your work builds on GPL or AGPL code, that license may apply.

## License

This repository is dual-licensed:

- **Code** is licensed under the [Apache License 2.0](LICENSE).
- **Written material** — problem descriptions, results summaries and other documentation —
  is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-CC-BY-4.0).
