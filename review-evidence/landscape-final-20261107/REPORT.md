# Horizontal presentation final candidate — actual reruns

HEAD c2cc9d4f1c4ba6c72ab02ed0ca15353df15b54a8; pinned/latest fetched main 8336cb6ab602d96b26b36390274dcb47cf05ac1c. Five presentation paths dirty. Candidate source SHA256 `c2261c188a2456e0168488e7993717eaf145388629a779c1ed2453d5cc99641f` over 199 tracked files. No assertion that a future publication commit was rerun.

Tracked before/after identical: True. Original frozen manifest, harness, gallery checker and v1 policy/checker unchanged.

| command record | actual exit | expected recording exit |
|---|---:|---:|
| 01_preservation.json | 0 | 0 |
| 02_controls.json | 0 | 0 |
| 03_exact20.json | 1 | 1 |
| 04_fault.json | 1 | 1 |
| 05_default.json | 0 | 0 |
| 06_replacement.json | 0 | 0 |
| 07_gallery.json | 0 | 0 |
| 08_gallery_checks.json | 1 | 1 |
| 09_references.json | 0 | 0 |
| 10_p2.json | 0 | 0 |
| 11_human_node.json | 0 | 0 |
| 12_detection.json | 0 | 0 |
| 13_legacy_missing_input.json | 1 | 1 |

Original exact20 remains19PASS/1FAIL (C19.originals_unchanged),78/79 required probes. Original gallery remains28PASS/1FAIL. These are FAIL, not acceptance PASS. Separate preservation v1 and four falsification controls do not relabel the original suite. Fault additionally fails C07 and returns1. Optional1PASS/4UNKNOWN/2NOTRUN. Default/replacement185/230; generated200records/25assemblies are demonstration, not independent evaluations. Legacy products.csv remains missing.

New result names and per-command actual stdout/exits are recorded separately. Full raw diagnostic files and fresh generated outputs are outside the repository; public command records replace personal roots and omit legacy traceback body while retaining raw hashes. No raw model streams, prompts or credentials included. Source snapshot excludes untracked files, mode/chmod bits and new run records. This is not science, health, equivalence, GOLD/holdout or general-accuracy validation. Freeze chronology recorded, not authenticated. BOX review does not replay Git objects.

44 relative links checked: True; no JavaScript/external dependency. Browser visual review is a separate gate, not an execution-runner result.

Material blockers: none beyond explicitly preserved original-scope FAILs/unknowns.
