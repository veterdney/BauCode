# Session prompt

Round 5 goal (checkable): `analysis/levels/report` is re-run with values from `data/Building material property dataset.csv`, the change is logged in `analysis/levels/dataset_fill_log.csv`, the scoring-lab artifact (https://claude.ai/artifact/G5d7rnLrZXmDZvH7zGKLn5) and the loop page are rebuilt, and `node analysis/levels/viz/test_loop.mjs` exits 0.

Round 4 goal (done): the research-loop artifact is updated to show round 4, which applies every practice in `RESEARCH-LOOPS.md`.
Done when all of these hold:

1. `node analysis/levels/viz/test_loop.mjs` exits 0.
2. `analysis/levels/viz/loop.html` is republished to https://claude.ai/artifact/AMyhVCVaCXYgJcw2WgMwt6 (same URL).
3. `analysis/loop/TASKS.md`, `PROMPT.md` and `JOURNAL.md` exist and are current.
4. Every finished task is its own commit on branch `add-wall-structure-scoring` (fork `veterdney/claude-impact-lab-2026` only, never `upstream`).

Rules from `RESEARCH-LOOPS.md`:

- Keep a prioritized task list in `analysis/loop/TASKS.md`; take the top task, do it, update the list.
- Run each atomic step in its own subagent; the main session plans and reviews.
- Write the test before the code, and see it fail first.
- Append every result, decision and exchange to `analysis/loop/JOURNAL.md` with date and links.
- Commit after each finished task.

To continue in a new session: `/goal continue the goal described in analysis/loop/PROMPT.md`.
