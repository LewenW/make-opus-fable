---
name: deep-audit
description: Exhaustive semantic code review across a whole package or changeset — finding hidden bugs, contract violations, boundary errors, broken invariants, data-integrity hazards. Use when the goal is RECALL (find every defect), not a quick look: pre-merge audits of multi-file changes, "review this module/repo for bugs", regression hunts, security/correctness passes. Trades tokens and wall-clock for coverage. Do not use for a single small function (a direct read is enough) or for writing new code.
effort: xhigh
---

# Deep audit: buy coverage with fan-out, not with effort alone

Auditing for defects is a RECALL problem: the cost is a MISS, not a wasted word. A single reviewer — however careful — anchors on the files it opened first and leaves the rest thin, because holding a whole package in one context exceeds the window where its attention stays uniform. The fix is structural, not motivational: **split the surface so no single unit exceeds the reliable window, review each in a fresh context, then union.** Measured: on a 4-file audit this took recall from 5.5/10 (single reviewer, default effort) to 8/10 (single, xhigh) to 10/10 (per-file fan-out, xhigh).

## The protocol

1. **Enumerate the surface first (mechanical, so it can't be skipped).** List every file in scope: `git diff --name-only` for a changeset, or every source file under the target path for a full audit. This list is the coverage contract — every entry gets its own reviewer. Do not let yourself "focus on the interesting files"; the last file is as likely to be broken as the first.
2. **One fresh-context reviewer per file (or per cohesive unit).** For each file, dispatch a subagent (the `verifier` agent, or a Task) whose ENTIRE job is that one file. Fresh context per file is the point — it recreates the uniform attention a single long context loses. Give each reviewer the intended-contract spec and this instruction: *read this one file line by line (and any files it imports, for context only); report defects located in THIS file; be exhaustive — every docstring/type contract bound to its enforcing line, every boundary and bucket evaluated by hand, every guard checked against what the contract requires (a weakened guard reads exactly like correct code).* Run them in parallel; keep working while they return.
3. **Union the findings.** Collect every reviewer's defects. Coverage now comes from the fan-out, so the union is the recall.
4. **Dedupe and vet — this is where precision is bought back.** Fan-out raises recall but also false positives (independent reviewers with no cross-check). So make one consolidation pass over the union: merge duplicates; for each finding, confirm it against the actual line and the stated contract; drop anything that is not a real violation. Apply the precision discipline from `/verify-before-done` §3 (quote the contract clause and the offending line; a mis-called defect costs credibility). The deliverable is the vetted union: file + function + which contract each defect violates.

## When each layer earns its cost

- Small changeset, one or two files → skip the fan-out; a single xhigh reviewer already lifts recall most of the way.
- Multi-file / whole-package / high-stakes → full fan-out. Cost is roughly (file count) × a single review; that is the price of coverage and it is the point.
- Enumerate-then-fan-out also beats "review everything" as a plain instruction: telling one agent to "review all files" leaves the same coverage gap this skill exists to close — the mechanical file list + per-file dispatch is what makes coverage structural rather than optional.

## Honest limits

- This buys coverage on a splittable surface (files, modules, functions). It does not raise per-unit reasoning: a defect that needs cross-file invariant reasoning can still be missed if no single reviewer sees both sides — for those, add a final whole-system reviewer over just the interface points.
- Deterministic oracles are cheaper than any reviewer where they apply: run the type checker (`mypy --strict`), linter, and any property-based tests first, and treat their output as free findings. Reserve model reviewers for the semantic defects tools can't express.
