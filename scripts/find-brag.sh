#!/usr/bin/env bash
# Prints the directory of the installed /brag skill (the one holding its
# SKILL.md), whichever agent installed it. brag-bn is a layer over /brag, so
# the agent runs this first and then reads <printed dir>/SKILL.md.
#
#   bash <brag-bn dir>/scripts/find-brag.sh      # -> /path/to/skills/brag
#
# Looks, in order, at: $BRAG_SKILL_DIR; a sibling of brag-bn (the `skills` CLI
# installs skills side by side); the project's .agents/.opencode/.claude skill
# folders from here up to the repository root; the per-agent global folders;
# the Claude Code plugin cache (newest version). Exits 1, with the install
# command, when there is none.
set -u
here=$(cd "$(dirname "$0")/.." && pwd)

ok() { [ -f "$1/SKILL.md" ] && grep -q '^name: *brag *$' "$1/SKILL.md"; }
pick() { for d in "$@"; do if ok "$d"; then (cd "$d" && pwd); exit 0; fi; done; }

[ -n "${BRAG_SKILL_DIR:-}" ] && pick "$BRAG_SKILL_DIR"
pick "$here/../brag"

dir=$PWD
root=$(git rev-parse --show-toplevel 2>/dev/null || echo /)
while :; do
  pick "$dir/.agents/skills/brag" "$dir/.opencode/skills/brag" "$dir/.opencode/skill/brag" "$dir/.claude/skills/brag" "$dir/skills/brag"
  [ "$dir" = "$root" ] || [ "$dir" = / ] && break
  dir=$(dirname "$dir")
done

pick "$HOME/.agents/skills/brag" "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/brag" "${CODEX_HOME:-$HOME/.codex}/skills/brag" \
  "${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills/brag" "${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skill/brag" \
  "$HOME/.gemini/skills/brag" "$HOME/.gemini/antigravity/skills/brag" "$HOME/.gemini/config/skills/brag" \
  "$HOME/.cursor/skills/brag" "$HOME/.copilot/skills/brag"

# Claude Code plugin install: ~/.claude/plugins/cache/<marketplace>/brag/<version>/skills/brag
newest=$(ls -d "$HOME"/.claude/plugins/cache/*/brag/*/skills/brag 2>/dev/null | sort -V | tail -1)
[ -n "$newest" ] && pick "$newest"

cat >&2 <<'EOF'
The /brag skill is not installed. brag-bn needs it. Install it with:
  npx skills add https://github.com/latent-spaces/brag --skill brag -g
(Claude Code can also use: /plugin marketplace add latent-spaces/brag, then /plugin install brag@brag)
Or point BRAG_SKILL_DIR at a folder that holds brag's SKILL.md.
EOF
exit 1
