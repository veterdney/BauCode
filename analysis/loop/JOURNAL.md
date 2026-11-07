# Journal

## 2026-11-07

- Asked whether we used `RESEARCH-LOOPS.md`. Answer: no. Rounds 1–3 used `/loop` only, with no goal, task list, journal, subagents, test-first or per-task commits.
- Decision: round 4 applies all of the practices to the task "update the research-loop artifact". Files: `analysis/loop/PROMPT.md`, `TASKS.md`, `JOURNAL.md`.
- Output so far: the three state files.
- T1 done: subagent wrote `analysis/levels/viz/test_loop.mjs`. First run fails as intended (checks 1, 2, 4, 5f, 5g red; 3, 5a–5e green). Facts for rounds 1–3 already match the report CSVs and budget JSON.
- T2 done: second subagent updated `analysis/levels/viz/loop.html` (8th stage Record, round 4, practices table, three round-4 catches). Test passes, 11 of 11 checks. Not yet viewed in a browser.
- T3 done: viewed in the browser pane. 8 nodes, 4 tabs, no horizontal scroll, no console errors. The round-4 subtitle in the circle centre was too wide and was shortened. Republished to https://claude.ai/artifact/AMyhVCVaCXYgJcw2WgMwt6.
- T4 done: journal updated, branch pushed to the fork (PR veterdney/claude-impact-lab-2026#3). Page numbers synced to the final counts.
- Request: remove the carbon budget (carbonbudget.eu) from the analysis. Removed `05-carbon-budget-api.md`, the five `budget_de_res_*.json`, `results_budget_*.csv`, the budget block in `run.py`, and every mention in the READMEs, limitations, decade notes and the loop page. Test check 5e (budget figures) removed; 10 checks remain and pass. The repo skill `.claude/skills/carbon-budget-api` is not part of the analysis and was left in place.
- Round 5 request: fill the earlier assumptions from `Building material property dataset.md` and `.csv`, re-analyse, rebuild the artifact. Branch is now `new-data-sets` (the user switched; PR #3 is merged), so loop files were restored from `add-wall-structure-scoring` without committing.
- T5 done: `analysis/levels/dataset_fill.py` maps 23 of our materials to dataset rows M02–M38 and fills λ, μ, service life, technical life, moisture, indoor-air, hygric score, cost and U-values. 83 values changed; log in `analysis/levels/dataset_fill_log.csv`. Switch `MATERIAL_DATASET=0` reproduces the baseline.
- T6 done: ranking stays 6, 2, 4, 3; rank 5 and 6 swap (RC frame 55.8, solid timber 55.3). Top score 68.6 (was 67.0). Life-cycle GWP falls for all; cost rises for all but alternative 6.
- T7 done: round-5 checks written first (5 failures), then round 5, five catches and the practices column added to `loop.html`.
- T8 done: both artifacts rebuilt and republished. I did not use a subagent in round 5, so that practice is marked unused for it.
