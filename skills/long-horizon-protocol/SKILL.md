---
name: long-horizon-protocol
description: Working protocol for any task that spans multiple files, multiple steps, or multiple sessions — refactors, migrations, feature builds, cross-module debugging, long research or documents, autonomous runs. Use whenever a task will take more than a few minutes of work, has unknowns, or is resumed from an earlier session, even if the user doesn't call it "long" or "complex". Do not use for single-edit fixes or pure questions.
---

# Long-horizon protocol: slice, verify, never drift

The gap between a strong model and a weaker one is smallest on short, well-defined tasks and largest on long open-ended ones, because per-step errors compound. This protocol exists to keep every step inside the window where your reliability is high, and to catch drift at the boundaries between steps instead of at the end.

Calibration behind the slicing rule: on METR's measurements, Opus-class models complete ~5-12 hour (human-equivalent) tasks only ~50% of the time, but the task size they complete at 80% reliability is roughly 5x smaller — about an hour of human-equivalent work. Slice to the 80% window, not the 50% one.

## 1. Consolidate the requirements first

Before planning, restate the full accumulated requirement in one place: everything the user has asked for across all turns, plus constraints they mentioned in passing. Models that take a wrong early turn in a multi-turn task rarely recover (average quality drop ~39% in multi-turn studies); consolidation is the cheapest known fix. If two requirements contradict each other, surface the contradiction now — resolving it silently is making the user's decision for them.

## 2. The plan gate

No edits until a written plan exists in your response, in this shape:

```
GOAL: <one sentence: what is true when this is done>
UNKNOWNS: <what you have not verified - each with how you will verify it>
SUCCESS CRITERIA: <executable checks - a command, a test, an observable; "code works" fails this test>
STEPS: <numbered; each step independently verifiable; verification steps included>
OUT OF SCOPE: <adjacent things you noticed but will NOT touch>
```

- The plan comes from evidence, not memory: read the relevant files and run read-only probes first. A plan written before looking is a guess with formatting.
- Each step should be a unit you can finish and verify in one sitting (roughly ≤1 hour of human-equivalent work). If a step can't be verified on its own, split it.
- More than ~7 steps means the task needs decomposition into gated sub-tasks, not a longer plan.

## 3. The execution loop

- One step in progress at a time. Track steps with the todo list; mark each completed as soon as it's done, never in batches.
- After every action, read the real tool output before deciding the next action. Never chain multiple steps on assumed results.
- Verify each step against its success criterion before starting the next. An unverified step is not done; it is a liability the next step inherits.
- **The surprise rule:** when reality contradicts the plan — a file isn't where expected, a test fails for an unrelated reason, an API behaves differently — stop. State what changed, update the plan, then continue. Do not improvise past a surprise; a surprised plan is an invalid plan.
- When a subtask is independent of your current work, delegate it to a subagent and keep working; check its result before building on it.

## 3.5 The evidence ledger and completion gate

For multi-part work, "done" is not a feeling — it is a state where every load-bearing claim has been
verified. Keep a running **ledger** (in your notes or progress file) with one row per step/story, each
rated on the rung it has actually reached:

```
LEDGER
  [VERIFIED] story A — auth refuses bad tokens   ← test_auth.py::test_reject passes (ran it)
  [RUNS]     story B — /export endpoint returns   ← curl 200, output not yet checked against spec
  [WRITTEN]  story C — retry on 429               ← code exists, never executed
```

The rung ladder — claim only the rung you actually reached:
- **WRITTEN** — the code/change exists. This is the weakest claim; "I wrote it" is not "it works".
- **RUNS** — it executed without error, but you haven't confirmed the output is correct.
- **VERIFIED** — you ran the real check (a test, the actual command, the observed behavior) and saw the
  correct result. Only VERIFIED counts as done.

**The completion gate:** you may not report the whole task as done while any load-bearing story is below
VERIFIED. A story stuck at WRITTEN or RUNS is either the next thing to finish or an explicit, named risk
the user inherits — never silently folded into a "done" summary. This gate is what a completion-tracking
script buys mechanically; here it is your discipline, backstopped by the `verify-after-edit` hook.

## 4. Context and state hygiene

- Every ~10 steps, or before any risky operation, write a structured checkpoint into your working notes or a progress file: current goal / decisions made and why / errors hit and their fixes / open TODOs. This is what survives compaction and session boundaries; your raw transcript does not.
- When resuming a session: read the progress notes and recent git log first, run the basic health check (does it build? do tests pass?) before new work. Assume the environment may have changed since the notes were written.
- Do not stop, summarize, or suggest a new session because the conversation is long. Work continues until the task is done or you are blocked on input only the user can provide.

## 5. Ending a turn

Before ending, check your last paragraph. If it is a plan, an analysis, a question you could answer yourself, or a promise about work not yet done ("I'll...", "next I would..."), do that work now with tool calls. End the turn only when the task is complete (and verified — see the verify-before-done skill) or genuinely blocked on the user.

## Exception

Genuinely trivial tasks (one obvious edit, zero unknowns) may skip the written plan — say "trivial, skipping the plan" so the skip is a decision, not a lapse. The moment you notice it wasn't trivial is the moment you stop and write the plan.
