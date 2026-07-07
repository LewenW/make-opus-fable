---
name: debugging
description: Use when the task is to find and fix the cause of a specific failure — "why is X broken", "this test fails", "fix the bug", "it crashes when…", a stack trace, a wrong output, flaky behavior. The deliverable is a located root cause and a minimal fix, not a broad review. Do not use for finding ALL defects in code (that is deep-audit) or for writing new features.
---

# Debugging: locate the cause by evidence, never guess-and-retry

Debugging fails in one predictable way: patching the symptom you can see instead of the cause you haven't
found, then retrying variations until something seems to work. That produces fixes that don't hold and
churn that hides the real defect. The load-bearing work is *locating* the cause; the edit that follows is
usually small. Treat it as science, not trial and error.

## The loop

**1. Reproduce it first — deterministically.** You cannot fix what you cannot trigger. Get a reliable
repro (a command, a test, an input) that fails every time before changing anything. If it's flaky,
finding what makes it deterministic *is* the bug hunt. No repro → say so; don't fix blind.

**2. Read the actual error, all of it.** The stack trace, the failing assertion, the real values. The
bug is usually named in the output you skimmed. Trace to the exact line, not the general area.

**3. Form a hypothesis with a falsifier.** State what you believe is wrong and the single observation
that would prove you wrong: "I think `x` is None here — if so, logging it prints None." A hypothesis you
can't test is a guess. Then test it (print, breakpoint, a probe) and read the result.

**4. Isolate — binary-search the fault.** Halve the surface: does it fail with a minimal input? Before a
given line? With the dependency stubbed? Bisect commits (`git bisect`) if it regressed. Each step should
eliminate half the remaining suspects, converging on the one line/state that's wrong.

**5. Confirm the causal chain before fixing.** You should be able to say "input A → state B at line C →
wrong output D." If you can't trace the mechanism end to end, you've found *a* smell, not *the* cause —
keep going. A fix aimed at a mechanism you can't state is a guess in disguise.

**6. Fix the cause, minimally.** Change what's actually broken, nothing else (scope discipline still
applies — surface adjacent issues, don't bundle them). Then **re-run the exact repro** and confirm it now
passes, plus the cases around it that the fix could affect. A fix you haven't re-run is a hypothesis.

## Hard rules

- **Never retry a failed approach verbatim.** If a change didn't work, the model of the problem was
  wrong — update the hypothesis, don't rerun the same thing hoping for a different result.
- **Don't fix two things at once.** One change per hypothesis, so the repro tells you which change did
  what. Bundled fixes make an ambiguous result.
- **Symptom ≠ cause.** "Added a null check and it stopped crashing" often just moves the crash. Ask why
  the value was null; fix *that* unless the null is genuinely valid input.
- **If you're stuck after a few cycles**, stop and report the honest state: the repro, what you ruled
  out, the current best hypothesis, and what you'd probe next — don't keep flailing silently.

Cross-cutting: `/verify-before-done` on the fix (re-run the repro is the proof); if the failure surface
spans many files, `/deep-audit` to find *all* instances once you understand the one.
