---
name: quant-thesis
description: Use when forming a quant/financial THESIS or forecast from messy, incomplete data — predicting a downstream figure (revenue, price, growth, direction) from upstream signals, lead-lag reads, pass-through, or expectation gaps. Triggers: "what does X imply for Y", "form a thesis/call", "will revenue accelerate", "read-through". NOT for deterministic calculation where the formula and inputs are given (just compute that) and NOT for auditing existing code.
---

<!-- Validated 2026-07-06 (HARDBENCH batch 12): on 11 messy quant-thesis scenarios, blind 3-judge
     panel vs Fable 5, this protocol took Opus from 6:27 (vote-level blowout loss) to 15:18 (near-even)
     — ~86% of the vote-level gap closed, vs 33% for the general discipline skill alone. The quant gap
     was a MISSING-REFLEX problem (Opus can compute 1.14/1.08, it just doesn't reach for it), not raw
     capability — these reflexes inject the habit. Failure mode: on genuinely n=1 data, do NOT force a
     band; rule 3's "direction only" branch is load-bearing — restraint beats false precision. -->

# Quant thesis: technique reflexes

You are forming a quant thesis under messy, incomplete data. The reader is a portfolio manager who will
size a position on your call. Adjectives don't size positions; decomposed numbers do. Apply every reflex
below BEFORE you write the thesis — they are the difference between "I understand the mechanism" and
"here is the number and how confident to be in it."

**1. Decompose before you conclude — and SHOW the arithmetic.** Any reported growth number is a product
of mechanical and organic parts: `reported ≈ organic × FX-translation × price/mix × base-effect`. Divide
out the mechanical parts explicitly and show the division. Reported +14% with an +8pp FX tailwind →
`1.14 / 1.08 ≈ 1.056` → organic ~+5.6%. Revenue +20% with ASP +16% → volume `1.20/1.16 ≈ +3.4%`. Never
report a top-line number you haven't split into "how much is real."

**2. Size every transmission with a coefficient, not an adjective.** When you map an upstream move to a
downstream figure, write the chain as numbers: `share × move × pass-through haircut`. Customer is 60% of
sales, its capex +30% → `0.6 × 30% = +18pp` gross, then haircut for lag/mix/attribution (state the basis)
~50% → ~+9pp contribution. "Modest pass-through" is not an answer; `+18pp haircut to ~+9pp` is.

**3. Deliver a numbered band, never a direction word alone.** Output a point estimate AND a range: "+3%
to +6%, point ~+4%." BUT if the data genuinely support only a sign (n=1 reporter, no elasticity), say so
explicitly — "direction only; magnitude unquantifiable from this, and I won't fabricate a band" — and say
why. Forcing false precision onto thin data is as wrong as giving no number. Match the output to the data.

**4. Two-tier conviction, always split.** State conviction on DIRECTION and on MAGNITUDE separately — they
are usually far apart (e.g., 85% on the sign, 55% on the band). Then name the single thing that caps
magnitude conviction: single-quarter decomposition, spot-rate vs quarter-average-rate, n=1 sample,
unknown inventory level. One reason, the load-bearing one.

**5. Interrogate the base and the stock/flow before you trust a print.**
   - **Base/comp:** is this yoy number lapping an abnormal prior period? If the comp is distorted, drop to
     a 2-year stack or sequential (QoQ) read and lead with THAT trend, not the flattering yoy.
   - **Stock vs flow:** is the "growth" a stock building that must reverse (channel inventory, sell-in
     ahead of sell-through, backlog) or a genuine flow (end-demand, sell-through)? A stock-driven print
     borrows from future quarters — call the reversal.

**6. Rank the caveats; lead with the one that caps conviction most.** Not a list of everything that could
be wrong — the ONE that most limits the call, named first, with the others compressed to a clause. If two
signals conflict (capex up vs competitor read-through soft), say plainly that the conflict itself IS the
low-conviction setup rather than pretending the strong signal wins cleanly.

**Lead/lag discipline (when several series are offered):** the series that governs a forecast at horizon
T+k is the one whose LEAD matches k. A coincident series prices T+0 and carries ~zero information about
T+k — it is the classic trap, not a confirming second vote. Align horizons before you weigh signals; an
"up" coincident index alongside a "down" 2-quarter-leading series is not a contradiction, it is exactly
what a real lead predicts you'd see right before the turn lands.

The thesis you deliver: **directional call with a numbered band (or an explicit "direction only") →
two-tier conviction with the reason magnitude is soft → the transmission mechanism written as arithmetic
→ the single invalidator.** Tight, computed, ranked. If you did the decomposition and it changed nothing
in your word count, you narrated instead of computed.
