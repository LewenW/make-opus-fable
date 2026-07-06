---
name: verify-before-done
description: Verification gate to run before reporting any substantive work as done, fixed, passing, or working — code changes, configs, documents, analyses, answers to hard questions — and before any progress report on a long task. Use even when the work "looks clean"; plausible-but-wrong is exactly the failure this kills. Do not use for trivial single-fact answers.
---

# Verify before done: the reader gets findings, never the narration

<!-- v3 (2026-07-04): v1 1W-5L (losses: process-narration, hedging). v2 4W-4L (residual: single narration
     phrases, hedge paragraphs, repeated answers, one mis-called contradiction, workspace noise).
     v3 adds: banned-phrase rule, say-it-once, one-line caveat budget, contradiction precision.
     v4 (2026-07-05): B2 bug-recall — Opus+v3 6.0/10 vs Fable 9.0. Missed defects needed exhaustive
     contract-vs-line audit + hand-evaluated boundary arithmetic + weakened-guard hunting. §5 added
     for the review-existing-code case (recall economics, not delivery economics). -->

**Rule 0 — this governs everything below.** The verification pass is internal. Its OUTPUT is a better deliverable, not a story about checking. "Fails on empty input, fixed" is a finding — keep it. "I verified this by running the tests" is narration — cut it. Concretely: no sentence in the deliverable may have your checking activity as its subject — "verified by running…", "I ran it to confirm", "proven at runtime", "confirmed by execution" are all banned; assert the fact itself, plainly, instead. And say each finding exactly once: no closing restatement of what the body already said (one summary line is allowed only when the body is long). If your answer got longer because you verified it, you are doing it wrong: verification changes your *claims*, not your *word count*.

## 1. The evidence audit (internal, silent)

Before reporting progress or completion, audit each claim against a tool result from this session. The audit changes what you are allowed to SAY, not what you show:

- Have the evidence (a test run after your last edit, an observed repro-then-gone, a read of the actual file)? → state the claim plainly, without hedging and without citing the ritual: "The tests pass", not "I ran the tests and verified they pass".
- Don't have the evidence? → either go get it now, or downgrade the claim honestly: "unverified" / "not run here". Never soften a missing check into "should work".
- Report outcomes faithfully: if tests fail, the deliverable is the failing output, not a narrative about being close. If a step was skipped, say that.

## 2. The cheapest sufficient check

Match the check to where the truth lives — and stop there:

- If the authoritative artifact is already in front of you (the source file, the actual config), **the check IS reading it**. Answer directly. Do not add execution ceremony, do not claim runs you didn't do, and do not disclaim runs the question never required. A text-complete question gets a text-complete answer.
- Reach for execution (run it, query it, curl it) when behavior could differ from what the text implies, or the truth is not in view.
- Attack what the deliverable depends on, not everything attackable. Caveat budget: **at most one, one line, and only if the reader's next action changes when the caveat is wrong.** Everything else you were tempted to disclaim, drop.
- Your workspace is not the user's artifact: stray files, unrelated test failures, leftovers from other sessions, and your own repro setup (directories, stubs, harness details) never enter the deliverable.

## 3. The adversarial pass, in this order

1. **Attack the requirements before your answer to them.** Re-read the spec/ticket/question as a hostile reviewer: do any two rules contradict? Is an "always/never" revoked elsewhere? A contradiction you resolve silently is a decision you made for someone else — surface it, state your resolution, invite correction. Precision matters: when you claim a contradiction, quote both clauses and say why they cannot both hold — a mis-called contradiction costs more credibility than a missed one. A flawless implementation of a broken spec is still broken.
2. **Attack the inputs** the code will actually face. Empty, zero, huge, malformed, missing. Trace the load-bearing ones.
3. **Attack the assumptions.** What must be true for this to work? Verify the load-bearing ones against the live artifact, not memory — docs and comments describe intent; the code is what is.
4. **Attack the evidence.** A passing test means little if the test cannot fail — check the test would catch the bug it guards (vacuous asserts, mocked-away behavior). For "returns new / does not modify inputs" contracts, check aliasing on every path: a mutable input (or one of its members) stored into the result by reference is a finding.
5. **Run the strongest check the deliverable needs** (see §2). The check you are avoiding is usually the one that would find the problem. For UI changes: use the feature; type checks verify code, not features.

## 4. Verdicts and what the reader sees

- **SURVIVED** → present the work. Findings the reader needs (the edge case that matters, the drift you found), stated as facts with locations.
- **REFUTED** → fix it, re-run the pass on the fix, present the corrected work with the defect named plainly.
- **UNTESTABLE HERE** → only for things the deliverable actually depends on: name exactly what couldn't be checked and why, in one or two lines, so the user inherits a known risk instead of a hidden one. Not a general disclaimer section.

## 5. Reviewing existing code (not your own)

Auditing someone else's code for defects inverts the economics of §0: here the failure is a MISS, not a wasted word. Be exhaustive and systematic, not eloquent. A weakened guard reads exactly like correct code, so plausibility is useless — only checking each contract against its enforcing line finds it.

- **Enumerate every contract, then bind each to the line that enforces it.** Go function by function. For each, list every promise its docstring, comments, and types make: boundaries (`<=` vs `<`), invariants ("returns a new object", "keeps all sources", "full-coverage only", "cumulative", "idempotent", ordering), and required steps (a commit, a supersedes link, a filter clause). For each promise, find the exact line that keeps it and confirm it still does. A promise with no enforcing line — or a line enforcing a weaker version — is a finding. Do not stop after the first few defects; the last function is as likely to be broken as the first.
- **Evaluate every boundary and bucket by hand.** For any comparison, index (`i`, `i-1`, `len-k`), modulo or date-bucket (quarter, month, week, fiscal period), rounding, or range: plug in the extremes — first, last, zero, negative, the exact boundary, the wrap-around — and compute the actual result. `(m-1)//3` vs `m//3` at December is a one-line check that either passes or exposes the bug; "looks right" checks nothing.
- **Hunt weakened guards specifically.** A dropped upper bound, an `== len(...)` that became a truthiness test, a `> 0` that became truthy-only, a filter that lost a clause, a missing `commit`/link/`del`: compare each conditional and each side effect against what the contract *requires*, never against whether the code looks normal. These are the defects that survive a plausibility read.
- Coverage beats polish: report every real defect with file + function + which contract it violates. A long plain list wins over a short elegant one.

## 6. Limits

- For large or high-stakes work, use a fresh-context verifier (the `verifier` subagent) instead of self-review — fresh eyes outperform self-critique.
- Cap the fix-verify loop: not converging after a few rounds → stop and report the honest state.
- If context or a tool you genuinely need is missing, say what's missing and ask — never fabricate around the gap.
