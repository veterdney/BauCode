# Building research loops with Claude

Practical hints for the [Claude Impact Lab Berlin 2026](README.md),
following the [main presentation](https://docs.google.com/presentation/d/1P4Zf5t-wDYfVolJKKEEeF8e5_DLYYiZpZCzCV7XdRec/edit?usp=sharing).

## Loops in Claude Code

Claude Code has two built-in ways to keep Claude working without you typing the next prompt.
Run `claude update` first, since `/goal` needs Claude Code v2.1.139 or later.

### `/goal <condition>`: work until something is true

You state what "done" looks like,
and Claude keeps working turn after turn until it gets there.
After each turn, a small, fast model checks whether the condition holds.

```
/goal all tests pass and the results are written to report.md
```

- Write a condition Claude can check by itself: a test that passes, a number within a tolerance, a file that exists. "Make it better" never ends.
- `/goal` with no argument shows the current goal, and `/goal clear` stops it.
- Only one goal can be active per session.

### `/loop <interval> <prompt>`: repeat on a timer

Claude re-runs a prompt on a schedule while the session is open.

```
/loop 10m check the simulation and log new results to JOURNAL.md
```

- Intervals use `s`, `m`, `h` or `d`, for example `30s`, `10m`, `2h`.
- The prompt can be a slash command or a skill, for example `/loop 20m /review-pr 42`.
- A scheduled prompt waits until Claude finishes its current turn, so it never interrupts work in progress.
- Loops live only in the current session and expire after a few days. Closing the terminal stops them.

Use `/goal` when you can say what the result should be,
and `/loop` when something needs checking regularly, such as a long computation.
The two work well together.

## Claude Science

[Claude Science](https://claude.com/product/claude-science) is a research workbench:
a desktop app in beta that adds scientific tools, 60+ databases and compute to Claude.

- It runs on your own laptop, lab server or HPC login node, so raw data stays there.
- It runs Python and R, and sends jobs to a Slurm cluster over SSH or to Modal.
- It saves every figure with the code, environment and conversation that produced it.
- A reviewer agent flags wrong citations and figures that don't match their code.
- It is available on paid Claude plans, with a discounted Team plan for academic and nonprofit labs.

Start with the [documentation](https://claude.com/docs/claude-science/overview).

## A good loop prompt

A research loop can run for hours, outlive a single session and fill up the context window.
What keeps it on track is state kept in files, not in Claude's memory.
Start with `/goal` and what you want to achieve, then ask Claude to:

- run each atomic step in its own subagent, keeping the main session for planning and review;
- keep a prioritized task list in a file;
- write a prompt file that lets any new session continue the goal;
- keep a journal of every result and every exchange with you.

A template to adapt:

```
/goal <what you want to achieve, stated so it can be checked,
e.g. "the model reproduces Figure 3 of <paper> within 5%">

Work in a loop:
- Keep a prioritized task list in TASKS.md. Take the top task, do it, then update the list.
- Run each atomic step in its own subagent.
- Before writing any code, write a test showing how it will be used. Then make it pass.
- Keep PROMPT.md up to date, so that a new session told
  "continue the goal described in PROMPT.md" can pick up where you left off.
- Append every result, decision and exchange with me to JOURNAL.md,
  with the date and links to the outputs.
- Commit after each finished task.
```

If the session ends, start a new one with
`/goal continue the goal described in PROMPT.md`.

## Test first

Test-driven development (TDD) is a very important guideline for any research loop:
before writing any code, write a test showing how it would be used.

- The test pins down what the code should do before Claude decides how to do it.
- A passing test is a condition Claude can check by itself, which makes it a natural `/goal`.
- Tests that stay in the repository catch regressions when a later loop iteration changes the code.
- In research code, a test can check a known result: an analytic solution, a published value, a conservation law.

Ask for it explicitly, for example:

```
Before implementing anything, write a failing test that shows how the code will be used.
Then write the code that makes it pass.
```

## Examples

- [plenty-of-room](https://github.com/xemantic/plenty-of-room):
  a research loop in nanotechnology, simulating a DNA-origami actuator.
  Each pass plans, runs and verifies,
  and the evidence goes into a task queue (`TASKS.md`), a journal (`JOURNAL.md`) and a session prompt (`SESSION-PROMPT.md`).
- [claude-plugins](https://github.com/xemantic/claude-plugins):
  a loop that improves a project one issue at a time.
  It ranks open issues, a subagent fixes each one, a second subagent reviews the fix,
  and the loop opens a pull request for a human to review.
