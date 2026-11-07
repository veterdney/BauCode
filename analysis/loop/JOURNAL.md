# Journal

## 2026-11-07

- Asked whether we used `RESEARCH-LOOPS.md`. Answer: no. Rounds 1–3 used `/loop` only, with no goal, task list, journal, subagents, test-first or per-task commits.
- Decision: round 4 applies all of the practices to the task "update the research-loop artifact". Files: `analysis/loop/PROMPT.md`, `TASKS.md`, `JOURNAL.md`.
- Output so far: the three state files.
- T1 done: subagent wrote `analysis/levels/viz/test_loop.mjs`. First run fails as intended (checks 1, 2, 4, 5f, 5g red; 3, 5a–5e green). Facts for rounds 1–3 already match the report CSVs and budget JSON.
- T2 done: second subagent updated `analysis/levels/viz/loop.html` (8th stage Record, round 4, practices table, three round-4 catches). Test passes, 11 of 11 checks. Not yet viewed in a browser.
