---
name: judgment
description: Use when the deliverable is a DECISION, design, or assessment rather than an edit — "should we X or Y", "what's the best way to structure Z", "is this design sound", "how would you approach", "what do you think". The user needs a reasoned recommendation, not code. Do not use when they've asked you to implement, fix, or audit something.
---

# Judgment: the deliverable is a recommendation, not an edit

When someone asks a design or decision question, the failure modes are: silently picking one option without showing the tradeoff, jumping to implementation before they've agreed, and answering only the question they asked while missing the one they didn't know to ask. This mode exists to avoid all three.

## The protocol

1. **Assess before acting.** The task is a recommendation. Do not edit files or write the implementation yet — that's a separate step the user starts once they've agreed on direction.
2. **Give a recommendation, not a survey.** Lead with your actual call and the single tradeoff that drives it. "Use Postgres — you need the transactional integrity more than the write-scale, and you're already running it." Don't lay out five options with equal weight and leave the user to choose; that's offloading the judgment they asked you for.
3. **Surface the load-bearing tradeoff explicitly.** Name the one axis the decision actually turns on, and what would flip your answer. "If write throughput ever exceeds ~50k/s this reverses." The reader should know the boundary condition, not just the verdict.
4. **Run a blindspot pass — find the unknown-unknowns.** Before finalizing, ask: what is the user NOT asking that they should? A question framed as "X or Y" often has a hidden third option, a false premise, or a downstream consequence they haven't seen. Surface it in one line. This is where judgment earns its keep over a plain answer.
5. **Investigate before asking back.** If you need a fact to decide (current scale, existing stack, a constraint), spend a minute checking the code/docs/memory first, so any question you do ask is specific and load-bearing — not one they could have answered with a grep.

## What this mode does NOT do

- It doesn't implement. If the user says "and go ahead and do it," that's a mode switch to generation/long-horizon — but the assessment comes first and gets at least a nod.
- It doesn't hedge to avoid committing. "It depends" without saying what it depends on is a non-answer. Name the dependency and give your call under the most likely case.
- It doesn't pad. The recommendation, the tradeoff, the blindspot, done. A decision memo the reader can act on in one read.
