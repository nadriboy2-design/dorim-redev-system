#!/usr/bin/env bash
# Cloud-only: installs skills and CLIs that plugins cannot carry. Idempotent; never blocks the session.
[ "$CLAUDE_CODE_REMOTE" = "true" ] || exit 0
add() { npx -y skills add "$1" ${2:+--skill "$2"} -g -y --agent claude-code >/dev/null 2>&1 || echo "skill failed: $1 $2" >&2; }
[ -d ~/.claude/skills/find-skills ] || add vercel-labs/skills find-skills
[ -d ~/.claude/skills/grill-me ] || add mattpocock/skills grill-me
[ -d ~/.claude/skills/handoff ] || add mattpocock/skills handoff
[ -d ~/.claude/skills/caveman ] || add JuliusBrussee/caveman
[ -d ~/.claude/skills/agent-browser ] || add vercel-labs/agent-browser
[ -d ~/.claude/skills/remotion-best-practices ] || add remotion-dev/skills remotion-best-practices
[ -d ~/.claude/skills/game-sfx ] || add GhazaGG/Game-Sound-Effect-for-Claude game-sfx
command -v headroom >/dev/null || pip install -q "headroom-ai[all]" >/dev/null 2>&1 || echo "headroom failed" >&2
command -v agent-browser >/dev/null || { npm install -g agent-browser >/dev/null 2>&1 && agent-browser install >/dev/null 2>&1; } || echo "agent-browser failed" >&2
exit 0
