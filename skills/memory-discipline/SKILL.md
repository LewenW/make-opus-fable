---
name: memory-discipline
description: Rules for persistent memory across sessions — reading or writing memory files, CLAUDE.md, progress notes, lesson ledgers, or any notes meant for a future session. Use at session start when prior context exists, at the end of substantive work when lessons are worth keeping, and whenever acting on a remembered fact. Memory is the highest-leverage asset an agent has, and the most dangerous one.
---

# Memory discipline: memory is a claim about the past, not a fact about the present

Good memory compounds — every session starts smarter. Bad memory compounds too: one stale "fact" confidently recalled can outvote the live system in front of you.

## Session start

Read the memory/progress notes before doing anything else. Assume interruption is normal: anything not recorded in durable notes did not survive the last session. Then verify the environment still matches the notes (quick health check) before building on them.

## Writing: what deserves persistence

Persist only what a future session cannot rederive:

- **Corrections received.** When the user corrects you, that is the single most valuable thing to persist — with the why, so the future session applies the principle, not just the rule.
- **Decisions and their why.** "Chose X over Y because Z" — the why is the part that evaporates.
- **Non-obvious constraints.** The gotcha that cost an hour; the API that lies; the step that must come first.
- **Confirmed approaches.** What worked and why it mattered.

Do NOT persist what the repo, git history, or docs already record — duplicated memory ages into contradiction. Never persist secrets.

## Writing: how

- One lesson per file (or entry), with a one-line summary at the top.
- Date it: "as of 2026-07-04, X" ages honestly; undated facts rot invisibly.
- Write the trigger with the fact: "when touching the deploy pipeline, remember X" — a future session needs to know when this matters.
- Update the existing note rather than creating a duplicate. Delete notes that turn out to be wrong — fix the memory, don't route around it.
- Small and curated beats large and complete: every stale line taxes every future session. Prune when you add.

## Recall: the verification rule

Remembered facts are point-in-time observations. Before acting on one:

1. Grade its staleness risk: preferences and decisions age slowly; system state (versions, configs, paths, what's deployed) ages fast.
2. Fast-aging fact + consequential action → one live probe first (does the file still exist, is the flag still set, does the endpoint respond).
3. When memory and live state disagree, live state wins — and update the memory in the same breath.
4. Tell the reader the vintage: "per notes from June" vs "verified just now".

## End of substantive work

Before closing out, ask: what did this session learn that the next one shouldn't have to rediscover? Write it — one entry, dated, with its trigger. If the session contradicted an existing note, correct that note now.
