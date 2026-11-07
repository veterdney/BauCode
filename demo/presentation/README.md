# BauCode landscape 180-second pitch (HTML)

Open `demo/presentation/index.html` directly in a browser, or serve the extracted bundle root with `python3 -m http.server 8765 --bind 127.0.0.1` (Windows: `py -3 -m http.server 8765 --bind 127.0.0.1`) and visit `/demo/presentation/index.html`. A server is optional for viewing. No JavaScript, external fonts/assets, network dependencies or in-browser Python. Relative local links expose saved inputs/outputs/evidence. JSON/Markdown/CSV display or download behavior depends on the browser. The Python terminal commands regenerate outputs; opening saved evidence does not run tests.

## Layout
Wide viewports use a **horizontal** CSS scroll-snap deck (one fullscreen-sized panel at a time) with sticky panel anchors and previous/next links. Narrow viewports and print stack panels vertically; print hides chrome. No automatic timer or simulated execution.

Suggested sequence is exactly 20+45+40+35+25+15 = 180 seconds, ordered as: Why → research question → loop → saved result + negative control → limits → reproduce/next. Keyboard focus, skip link, semantic tables and details/summary work without scripts. Browser visual rehearsal is separate and is not claimed by this edit.

## Provenance / publication boundary
Working copy rooted at `baucode-landscape-20261107/` from the portable preservation bundle recorded at HEAD `305345a394d0019dc4c5cc51aff508c2a54dea77`. This directory edits only the presentation wrapper (HTML/CSS/README/manifests); it neither recalculates results nor changes original source/tests/oracles. **No merge is authorized** by this proposal. New publication hashes are content identity, not claims of tests rerun on a later commit.

The supplied photo is the existing stripped `team.jpg` already in the presentation folder (orientation preserved; metadata removed upstream). Roles/roster were supplied, not inferred from face positions or individual contributions.

## Narrow v1 gate clarification (wording only; no rerun)
The saved policy checks exactly the pinned fork-to-main delta: 40 byte-content paths, 9 required absences, one explicit Python AST wrapper exception. It does not verify chmod/executable-mode bits or preserve the whole repository. Separate v1 50/50 is not comparable all-green20. Original suite 19/20 and gallery 28/29 FAIL records remain immutable. History guards 2/15→15/15 are recorded prior before/after, not a new measurement from this HTML edit. HumanNode 14 PASS and P2 15/15 are saved records. Optional probes remain 1 PASS / 4 UNKNOWN / 2 NOT RUN. Deliberate fault C07 exits 1 with existing C19 failure retained.

The exact20 contains exposed fixed synthetic regressions, not holdout or scientific evaluation. Selected lifecycle boundary, C/D coupling to A1–A3-known layers, unit/reference-equivalence caveats, and missing legacy products.csv remain disclosed on the page. No new features/model/research validity are supplied by the wrapper.

## Bounded readability correction
Heading styling now applies only to the first direct strong child of each loop article; numeric emphasis inside paragraphs stays inline. Loop cards permit word wrapping and the Test sentence separates default, replacement and gallery. Browser recheck pending; no visual PASS claimed here. Integration starts from c2cc9d4f1c4ba6c72ab02ed0ca15353df15b54a8; earlier saved code evidence records305345a plus then-uncommitted preservation tooling. Fresh candidate reruns, if performed, are recorded separately, never relabelled as the old snapshot.
