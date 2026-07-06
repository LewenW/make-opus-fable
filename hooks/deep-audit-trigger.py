#!/usr/bin/env python3
"""Deterministic backstop for the deep-audit skill.

Problem: model-invoked skills UNDER-fire. When you actually want an exhaustive
multi-file bug hunt, a plain "review this" may get a single-reviewer glance
instead of the fan-out that closes the Opus->Fable recall gap (measured 5.5 -> 10/10).

This hook fires on EVERY user prompt (UserPromptSubmit). If the prompt looks like
an exhaustive-audit request over more than a trivial surface, it injects a system
reminder that makes the deep-audit protocol non-optional. The hook guarantees the
*trigger*; the skill body carries the *procedure*.

Install: see hooks/settings-hook.json. This is advisory context injection (exit 0,
additionalContext), never a block — it cannot break a normal turn.
"""
import json, re, sys

# Intent: an audit/recall request. Trivia like "review my one-line fix" is excluded by the
# surface check below, so these can be broad.
INTENT = re.compile(
    r"(deep[-\s]?audit|audit\b|code[-\s]?review"
    r"|review (the |this |my |our )?(whole |entire |full )?(code|repo|package|module|codebase|changes|diff|pr)"
    r"|find (all |every |any )?(the )?bugs?|hunt (for )?bugs?|security review|correctness (pass|review)"
    r"|审计|代码审查|审查代码|找出?(所有|全部)?bug|查(所有)?bug|(所有|全部)\s*bug|逐个文件|全量审查)",
    re.I,
)
# Surface: only escalate when the target is plausibly multi-file (a whole thing), not one snippet.
SURFACE = re.compile(
    r"(repo|package|codebase|whole|entire|all (the )?files|every file|module|project"
    r"|多文件|整个|全部文件|全仓库|每个文件|逐个文件|模块|文件|包|代码库)",
    re.I,
)

REMINDER = (
    "The user is asking for an exhaustive code audit. Recall is the goal, so do NOT rely on a single "
    "reviewer reading everything in one context — that anchors on the first files and misses the rest "
    "(measured: single reviewer 5.5/10 vs per-file fan-out 10/10 on the same bugs). Invoke the "
    "`deep-audit` skill and follow it: (1) mechanically enumerate EVERY file in scope "
    "(`git diff --name-only`, or all source files under the target) — this list is the coverage "
    "contract; (2) run any available deterministic oracles first (mypy --strict, linter, property "
    "tests) and treat their output as free findings; (3) dispatch one fresh-context reviewer subagent "
    "per file, in parallel, each exhaustive on its one file; (4) union all findings, then make ONE "
    "consolidation pass to dedupe and vet each against the actual line + contract before reporting "
    "(fan-out raises false positives — this pass buys precision back)."
)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # never break the turn
    prompt = str(data.get("prompt", "") or data.get("user_prompt", ""))
    if INTENT.search(prompt) and SURFACE.search(prompt):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": REMINDER,
            }
        }))
    sys.exit(0)


if __name__ == "__main__":
    main()
