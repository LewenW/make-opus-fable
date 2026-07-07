# Evidence at a glance

Three concrete before/after results, pulled from the full record in [`HARDBENCH.md`](HARDBENCH.md).
Each is a controlled comparison: same task, same target model (Opus 4.8), the only variable is whether
the suite was applied. Numbers are from objective grading (hidden tests, on-disk state, or blind
pairwise panels), not self-assessment.

---

## 1. Quant forecasting — the vote flipped from a blowout to near-even

**Task:** form a quant thesis from messy, incomplete data (predict a downstream figure from upstream
signals — lead/lag, pass-through, expectation gaps). 11 scenarios, blind 3-judge panel, each arm's
thesis judged pairwise against Fable's.

| Arm | Result vs Fable (33 votes) |
| :-- | :-- |
| Bare Opus 4.8 | **6 : 27** — lost decisively |
| Opus + `quant-thesis` skill | **15 : 18 — near-even (86% of the gap closed)** |

**What changed:** the skill forces the technique reflexes a quant-native model has and a code-first model
skips — decompose reported growth and *show the arithmetic* (`1.14 / 1.08 ≈ +5.6% organic`), size
pass-through with a coefficient (`0.6 × 30% = +18pp, haircut to ~+9pp`), deliver a numbered band, split
conviction into direction vs. magnitude. Same model, same data — it just stopped leaving the numbers on
the table.

---

## 2. Defect recall — fan-out closes most of the audit gap

**Task:** find every bug in a multi-file changeset (recall, not a quick look).

| Arm | Bugs found |
| :-- | :-- |
| Bare Opus 4.8, single reviewer | 5.5 / 10 |
| Opus + `deep-audit` (per-file fan-out + xhigh) | near Fable; **~43% of the gap closed** on real code |

A single reviewer reading everything anchors on the first files and misses the rest. `deep-audit`
enumerates every file and dispatches one fresh reviewer per file, then de-dupes and re-verifies. On a
**real production repo** (not a synthetic target), the same orchestration surfaced **1 critical + 8
high-severity bugs, all confirmed real** — including a timezone bug two prior manual reviews had missed
([`AUDIT-PARALLAX.md`](AUDIT-PARALLAX.md)).

---

## 3. Behavioral discipline — plausible-but-wrong gets caught

**Task:** a broad blind eval across 17 different trap-laden tasks, two arms both Opus 4.8, judged blind.

**Result:** Opus + the discipline suite went **15 wins, 2 losses** against bare Opus.

A representative flip: asked for a one-line bug fix, bare Opus bundled in unrequested validation and
self-justified the scope creep. With the suite, the diff stayed one line and the extra findings were
reported separately for the user to triage. The suite's job here isn't raw smarts — it's calibration:
what you claim, when you stop, what you touch, and how you report it.

---

## The honest boundary

Not everything closes. On visual perception and raw knowledge density the gap is **baked into the model
weights** — no skill or structure moves it, and the suite says so plainly. And across a deliberately
exhaustive sweep (coding, terminal repair, instruction-following, retrieval, knowledge, financial
calc), the two models were simply **tied** — clean single-turn tasks don't separate them, so there's
nothing to close. The gains above are exactly the axes where a real gap exists and structure can reach
it. Full detail, including conclusions our own held-out testing overturned, is in
[`HARDBENCH.md`](HARDBENCH.md).
