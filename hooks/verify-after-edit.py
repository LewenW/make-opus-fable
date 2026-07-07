#!/usr/bin/env python3
"""Deterministic backstop for the verify-before-done skill.

Problem: `verify-before-done` is a request, and model-invoked skills UNDER-fire —
the model may declare an edit "done" without ever running the tests that would
prove it. Verify-after-edit is the single most-shortchanged engineering habit,
and the eval data says it is NOT reliably fixable by intention (measured
test-after-edit rate: ~60-83% even on strong models, never 100%). So a hook fires
the check whether or not the model remembers.

This is the PostToolUse twin of deep-audit-trigger.py: that hook guarantees the
*trigger* for an audit; this one guarantees the *check* after an edit. On every
Edit / Write / MultiEdit to a code file, it walks up to the project root, runs the
project's real test command, and injects the pass/fail result back into context so
the model must react to it. Non-blocking: it never blocks the edit — an unverified
edit is simply not yet a truthful "done" (the verify-before-done rule, mechanized).

General-purpose by design: it fires on ANY coding task in ANY of the router modes,
not just audits — it is the mechanical floor under "verify before you call it done".

Safety: always exits 0, never raises into the session. Stays silent when there is
no test command, when the edited file isn't code, or when debounced.

Knobs (env):
  MOF_NO_VERIFY_HOOK=1        disable entirely
  MOF_VERIFY_DEBOUNCE=45      min seconds between runs per project root
  MOF_VERIFY_TIMEOUT=90       per-run timeout in seconds
"""
import sys
import os
import json
import time
import shutil
import hashlib
import tempfile
import subprocess

DEBOUNCE = int(os.environ.get("MOF_VERIFY_DEBOUNCE", "45"))
TIMEOUT = int(os.environ.get("MOF_VERIFY_TIMEOUT", "90"))
IS_WINDOWS = os.name == "nt"

# File types that should never trigger a test run (docs, data, config, assets).
SKIP_EXT = {
    ".md", ".markdown", ".txt", ".rst", ".json", ".jsonc", ".lock", ".yaml",
    ".yml", ".toml", ".ini", ".cfg", ".csv", ".tsv", ".svg", ".png", ".jpg",
    ".jpeg", ".gif", ".webp", ".ico", ".pdf",
}


def emit(context):
    """Print a PostToolUse additionalContext payload and exit."""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": context,
        }
    }))
    sys.exit(0)


def find_root_and_cmd(start_dir):
    """Walk up from start_dir; return (root, command_list, label) or (None, None, None)."""
    d = os.path.abspath(start_dir)
    while True:
        # Node / JS-TS
        pkg = os.path.join(d, "package.json")
        if os.path.isfile(pkg):
            try:
                scripts = json.load(open(pkg)).get("scripts", {})
            except Exception:
                scripts = {}
            test = scripts.get("test", "")
            if test and "no test specified" not in test.lower():
                if os.path.isfile(os.path.join(d, "pnpm-lock.yaml")):
                    pm = "pnpm"
                elif os.path.isfile(os.path.join(d, "yarn.lock")):
                    pm = "yarn"
                elif os.path.isfile(os.path.join(d, "bun.lockb")):
                    pm = "bun"
                else:
                    pm = "npm"
                return d, [pm, "test"], f"{pm} test"
        # Python
        if any(os.path.isfile(os.path.join(d, f)) for f in
               ("pyproject.toml", "setup.cfg", "pytest.ini", "tox.ini")) \
                or os.path.isdir(os.path.join(d, "tests")):
            if os.path.isfile(os.path.join(d, "uv.lock")):
                return d, ["uv", "run", "pytest", "-q"], "uv run pytest -q"
            return d, [sys.executable, "-m", "pytest", "-q"], "pytest -q"
        # Rust
        if os.path.isfile(os.path.join(d, "Cargo.toml")):
            return d, ["cargo", "test", "-q"], "cargo test -q"
        # Go
        if os.path.isfile(os.path.join(d, "go.mod")):
            return d, ["go", "test", "./..."], "go test ./..."
        # Make
        mk = os.path.join(d, "Makefile")
        if os.path.isfile(mk):
            try:
                if any(line.startswith("test:") for line in open(mk)):
                    return d, ["make", "test"], "make test"
            except Exception:
                pass
        parent = os.path.dirname(d)
        if parent == d:
            return None, None, None
        d = parent


def debounced(root):
    """True if we ran for this root within DEBOUNCE seconds; else stamp and return False."""
    h = hashlib.sha1(root.encode()).hexdigest()[:16]
    marker = os.path.join(tempfile.gettempdir(), f"mof-verifyhook-{h}")
    now = time.time()
    try:
        if os.path.exists(marker) and now - os.path.getmtime(marker) < DEBOUNCE:
            return True
        open(marker, "w").close()
    except Exception:
        pass
    return False


def main():
    if os.environ.get("MOF_NO_VERIFY_HOOK"):
        return
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    if data.get("tool_name") not in ("Edit", "Write", "MultiEdit"):
        return

    ti = data.get("tool_input") or {}
    fpath = ti.get("file_path") or ti.get("path") or ""
    if not fpath:
        return
    if os.path.splitext(fpath)[1].lower() in SKIP_EXT:
        return

    start = os.path.dirname(fpath) or data.get("cwd") or os.getcwd()
    root, cmd, label = find_root_and_cmd(start)
    if not cmd:
        return  # no test command in this project — stay silent
    if debounced(root):
        return

    # On Windows the interpreter path may contain spaces and several runners
    # (npm/pnpm/yarn/make) are .cmd shims that can't be exec'd directly — use the
    # bare interpreter name and let cmd.exe resolve it via PATHEXT under shell=True.
    prog = cmd[0]
    if IS_WINDOWS and prog == sys.executable:
        prog = "python"
    if not shutil.which(prog):
        return  # runner not installed — silent
    run_args = [prog] + cmd[1:]

    t0 = time.time()
    try:
        if IS_WINDOWS:
            # tokens are bare (no spaces), so a plain join is unambiguous for cmd.exe
            p = subprocess.run(" ".join(run_args), cwd=root, capture_output=True,
                               text=True, timeout=TIMEOUT, shell=True)
        else:
            p = subprocess.run(run_args, cwd=root, capture_output=True, text=True,
                               timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        emit(f"verify-after-edit ⏱ — `{label}` exceeded {TIMEOUT}s in {root}; "
             "result inconclusive, run it manually before declaring done.")
    except FileNotFoundError:
        return  # runner not installed — silent
    except Exception:
        return

    dur = round(time.time() - t0, 1)
    if p.returncode == 0:
        emit(f"verify-after-edit ✓ — `{label}` passed in {root} ({dur}s).")
    else:
        out = (p.stdout or "") + (p.stderr or "")
        tail = "\n".join(out.strip().splitlines()[-25:])
        emit(f"verify-after-edit ✗ — `{label}` FAILED in {root} "
             f"(exit {p.returncode}, {dur}s). An unverified edit is not 'done' "
             f"(see /verify-before-done). Tail:\n{tail}")


if __name__ == "__main__":
    main()
