# hooks/ — the deterministic backstop layer

A skill is a *request* — the model may under-fire it. A hook is a *guarantee* — it runs on a fixed
lifecycle event no matter what (Anthropic's own guidance: *"put guardrails in hooks… a skill is a
request, not a guarantee"*). This layer ships two hooks, each backstopping the skill it pairs with:
`deep-audit-trigger.py` backstops `deep-audit` (should this fan out into an audit?), and
`verify-after-edit.py` backstops `verify-before-done` (should the tests run after this edit?). This
layer is **general-purpose** — it doesn't care which task mode you're in; it fires on every code edit.

## deep-audit-trigger.py

- **Event**: `UserPromptSubmit` (before every user message).
- **Logic**: when a message matches both "audit intent" (audit / review the codebase / find all bugs /
  逐个文件…) **and** "multi-file surface" (repo / package / whole / module / 文件…), it injects a system
  reminder that forces the deep-audit protocol (enumerate files → run oracles → per-file fan-out
  reviewers → de-dupe and re-verify). Otherwise it stays completely silent.
- **Why**: fan-out lifts defect recall from bare Opus 5.5/10 toward Fable (synthetic set once hit 10/10;
  on real production code, same-protocol head-to-head is ~43% closed, 7/9 vs Fable 9/9 — closer, not
  closed; batches 6/8 in `evals/HARDBENCH.md`), but model-invoked skills under-fire — a plain "review
  this" can degrade to a single-reviewer glance. The hook guarantees the fan-out actually happens.
- **Safety**: `additionalContext` injection only (`exit 0`), never blocks a turn. Self-tested (multi-file
  intent fires; single-file / trivial / unrelated stay silent; English + Chinese both covered).

## verify-after-edit.py

- **Event**: `PostToolUse`, matcher `Edit|Write|MultiEdit` (after every code edit).
- **Logic**: walks up from the edited file to the project root, auto-detects the test command
  (npm/pnpm/yarn/bun test, pytest, `uv run pytest`, `cargo test`, `go test`, `make test`), runs it, and
  injects the ✓/✗ result (last 25 lines on failure) as `additionalContext` so the model must react to
  it. **Non-blocking** — it never blocks the edit; it just reminds you that an unverified edit isn't
  "done" yet.
- **Why**: verify-after-edit is the most-shortchanged engineering step — measured, even strong models
  run the real tests only ~60–83% of the time and never 100%, and the data says this is **not reliably
  fixable by intention**. So a hook enforces it instead of trusting memory. It's the mechanical backstop
  under the `verify-before-done` skill: the skill says "please remember to verify," the hook makes it
  happen after every edit.
- **General-purpose**: independent of router mode (generation / audit / long-horizon all get it), for any
  language, any code edit — this is the "universal floor," not part of the three capability-axis fixes.
- **Quiet by design**: doc/data/config extensions (`.md`/`.json`/`.yaml`/images…) never trigger it;
  45s debounce per project root (`MOF_VERIFY_DEBOUNCE`); 90s per-run timeout (`MOF_VERIFY_TIMEOUT`, with
  a 120s hook-level timeout as a floor); no test command / runner not installed → silent. Kill switch:
  `MOF_NO_VERIFY_HOOK=1`.
- **Safety**: always `exit 0`; no exception ever propagates into the session. Self-tested: real pytest
  project reports ✓, failing project reports ✗ + failure tail, doc edits / non-edit tools / debounce /
  kill switch / no-test-command all stay silent.

## Install (the easy way)

`bash install.sh --with-hooks` copies both scripts into `~/.claude/hooks/` and writes their absolute
paths into `settings.json` (with a backup, idempotent, reversible via `--uninstall`). Manual install:

```bash
# 1. drop the scripts
mkdir -p ~/.claude/hooks && cp deep-audit-trigger.py verify-after-edit.py ~/.claude/hooks/

# 2. merge the "hooks" block from settings-hook.json into ~/.claude/settings.json
#    (if you already have a hooks key, merge arrays per-event rather than overwriting;
#     fix the absolute script paths for your machine)

# 3. verify — start a new Claude Code session:
#    - send "audit the whole repo for bugs" → you should see the fan-out enumerate files, not a single reviewer;
#    - edit a code file in a project that has tests → you should see verify-after-edit's ✓/✗ report.
```

Tune the audit triggers by editing the `INTENT` / `SURFACE` regexes at the top of `deep-audit-trigger.py`
(commented). Tune verify-after-edit with the `MOF_*` env vars above. To disable a hook temporarily,
remove its block from `settings.json`.
