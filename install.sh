#!/usr/bin/env bash
# make-opus-fable — one-command installer.
# Installs the skill suite into your Claude Code config. Safe, idempotent, reversible.
#
#   bash install.sh              # install skills + verifier agent + behavior core
#   bash install.sh --with-hooks # also install the deep-audit trigger hook
#   bash install.sh --uninstall  # remove everything this installer added
#
# Respects $CLAUDE_CONFIG_DIR (defaults to ~/.claude). Never overwrites your files
# except by adding a clearly-marked, removable block to CLAUDE.md.

set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
BEGIN="<!-- BEGIN make-opus-fable (managed; edit above/below, not inside) -->"
END="<!-- END make-opus-fable -->"
MODE="install"; WITH_HOOKS=0
for a in "$@"; do
  case "$a" in
    --uninstall) MODE="uninstall" ;;
    --with-hooks) WITH_HOOKS=1 ;;
    *) echo "unknown arg: $a" >&2; exit 2 ;;
  esac
done

say() { printf '  %s\n' "$*"; }

remove_block() { # strip the managed CLAUDE.md block if present
  local f="$CLAUDE/CLAUDE.md"
  [ -f "$f" ] || return 0
  if grep -qF "$BEGIN" "$f"; then
    python3 - "$f" "$BEGIN" "$END" <<'PY'
import sys
f, b, e = sys.argv[1], sys.argv[2], sys.argv[3]
t = open(f).read()
i, j = t.find(b), t.find(e)
if i != -1 and j != -1:
    t = (t[:i].rstrip() + "\n" + t[j+len(e):].lstrip("\n")).rstrip() + "\n"
    open(f, "w").write(t)
PY
  fi
}

if [ "$MODE" = "uninstall" ]; then
  echo "Uninstalling make-opus-fable from $CLAUDE ..."
  for s in verify-before-done long-horizon-protocol memory-discipline deep-audit; do
    rm -rf "$CLAUDE/skills/$s" && say "removed skill: $s" || true
  done
  rm -f "$CLAUDE/agents/verifier.md" && say "removed agent: verifier" || true
  remove_block && say "removed CLAUDE.md behavior block" || true
  say "note: hook entries in settings.json (if you added --with-hooks) are NOT auto-removed; edit settings.json to remove the deep-audit-trigger entry."
  echo "Done."
  exit 0
fi

echo "Installing make-opus-fable into $CLAUDE ..."
mkdir -p "$CLAUDE/skills" "$CLAUDE/agents"

# 1) skills (additive; overwrites only our own skill dirs)
for s in verify-before-done long-horizon-protocol memory-discipline deep-audit; do
  mkdir -p "$CLAUDE/skills/$s"
  cp "$SRC/skills/$s/SKILL.md" "$CLAUDE/skills/$s/SKILL.md"
  say "skill installed: /$s"
done

# 2) verifier subagent
cp "$SRC/agents/verifier.md" "$CLAUDE/agents/verifier.md"
say "agent installed: verifier"

# 3) behavior core -> a clearly-marked, removable block in CLAUDE.md (idempotent)
CORE="$(awk '/^## Working discipline/{p=1} p' "$SRC/config/CLAUDE-core.md")"
touch "$CLAUDE/CLAUDE.md"
remove_block   # drop any prior version of our block, so re-running updates cleanly
printf '\n%s\n%s\n%s\n' "$BEGIN" "$CORE" "$END" >> "$CLAUDE/CLAUDE.md"
say "behavior core merged into CLAUDE.md (marked block; removable with --uninstall)"

# 4) optional hook
if [ "$WITH_HOOKS" = "1" ]; then
  mkdir -p "$CLAUDE/hooks"
  cp "$SRC/hooks/deep-audit-trigger.py" "$CLAUDE/hooks/deep-audit-trigger.py"
  chmod +x "$CLAUDE/hooks/deep-audit-trigger.py"
  python3 - "$CLAUDE/settings.json" "$CLAUDE/hooks/deep-audit-trigger.py" <<'PY'
import sys, json, os, shutil
settings, hook = sys.argv[1], sys.argv[2]
data = {}
if os.path.exists(settings):
    shutil.copy(settings, settings + ".bak")
    try: data = json.load(open(settings))
    except Exception: data = {}
hooks = data.setdefault("hooks", {})
ups = hooks.setdefault("UserPromptSubmit", [])
cmd = f"python3 {hook}"
already = any(
    isinstance(g, dict) and any(h.get("command") == cmd for h in g.get("hooks", []))
    for g in ups
)
if not already:
    ups.append({"hooks": [{"type": "command", "command": cmd}]})
    json.dump(data, open(settings, "w"), indent=2, ensure_ascii=False)
    print("  hook installed: deep-audit-trigger (settings.json updated; backup at settings.json.bak)")
else:
    print("  hook already present; skipped")
PY
fi

cat <<EOF

Done. Installed into $CLAUDE
  skills:  verify-before-done, long-horizon-protocol, memory-discipline, deep-audit
  agent:   verifier
  core:    behavior discipline block in CLAUDE.md
$([ "$WITH_HOOKS" = "1" ] && echo "  hook:    deep-audit-trigger (UserPromptSubmit)" || echo "  hook:    (skipped; add with --with-hooks)")

Start a new Claude Code session to load them. Try it:
  /deep-audit   review a repo for bugs (fan-out + xhigh)
  /verify-before-done   before declaring work done
Remove anytime:  bash install.sh --uninstall
EOF
