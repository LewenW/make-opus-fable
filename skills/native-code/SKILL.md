---
name: native-code
description: Use when writing or editing code inside an existing file or codebase — the change should read as if the original author wrote it. The failure this prevents is code that works but announces itself: foreign idioms, defensive bloat, and narrating comments that a reviewer has to unwind. Do not use for greenfield files with no surrounding conventions, or for non-code deliverables.
---

# Native code: write it like the file's author would

Correct-but-foreign code is a hidden cost. It passes tests and still makes the codebase worse — the next
reader has to reconcile two styles, and the diff is bigger than the change. A strong model tends to write
*its* idiom (extra abstraction, defensive scaffolding, explanatory prose) instead of *the file's*. Match
the host, and your change disappears into it.

## Before you write — read the neighborhood

Look at the file and its siblings first, and copy what you find:
- **Idiom & style.** Naming (camel vs snake, `is_`/`has_` prefixes), error handling (exceptions vs
  result objects vs early return), how they structure a function, quote style, import grouping. The
  linter/formatter config is the law; the surrounding code is the precedent.
- **Existing helpers.** If the file has a `parse_date`, a logging wrapper, a base class, an error type —
  use it. Don't introduce a second way to do a thing the codebase already does one way.
- **The layer you're in.** A data-access function shouldn't grow UI concerns; match the abstraction level
  of its neighbors.

## What NOT to add

- **No defensive bloat.** Don't add try/except, null guards, input validation, or config knobs for inputs
  that can't occur on this path. Handle the cases the code actually faces; matching the file's existing
  level of defensiveness beats importing your own.
- **No narrating comments.** Comments explain *why* (a non-obvious constraint, a reason), never *what*
  the code already says. `# increment i` and `# loop over the users` are noise; delete them. If the code
  needs a comment to be readable, prefer making the code readable. Match the file's comment density — a
  terse file stays terse.
- **No speculative generality.** No abstraction for a single use, no "flexibility" nobody asked for, no
  renaming or reformatting adjacent code. The smallest diff that solves it is the target.
- **No scope drift.** Build exactly what was asked; if you spot an adjacent improvement, surface it for
  the user to triage — don't fold it into this diff.

## The test

Read your diff as the file's original author. Would they recognize it as their own code, or would they
see "an AI wrote this"? If a reviewer would have to ask "why is this here / why this way", cut or align it
until the change reads as native. Every line should trace to the request; every idiom should trace to the
file.
