#!/usr/bin/env bash
#
# Wisdom Council Layer installer
#
# Installs the skill set to a Claude Code discovery location so the
# evaluator skills and council orchestrator are callable by name from
# anywhere.
#
# Usage:
#   ./install.sh            # Global: ~/.claude/skills/ (callable from any project)
#   ./install.sh --local    # Project: .claude/skills/ (this repo only)
#   ./install.sh --uninstall
#
# Installation uses symlinks: the canonical source stays in ./skills/,
# so edits to the repo are reflected immediately.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$REPO_DIR/skills"

MODE="global"
ACTION="install"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --local)    MODE="local" ;;
    --global)   MODE="global" ;;
    --uninstall) ACTION="uninstall" ;;
    -h|--help)
      echo "Usage: ./install.sh [--local|--global] [--uninstall]"
      echo ""
      echo "  --local      Install to .claude/skills/ (this project only)"
      echo "  --global     Install to ~/.claude/skills/ (default; callable from anywhere)"
      echo "  --uninstall  Remove the installed skills (default: global target)"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
  shift
done

if [[ "$MODE" == "local" ]]; then
  TARGET_DIR="$REPO_DIR/.claude/skills"
else
  TARGET_DIR="$HOME/.claude/skills"
fi

if [[ "$ACTION" == "uninstall" ]]; then
  echo "==> Uninstalling Wisdom Council Layer skills from $TARGET_DIR"
  removed=0
  for skill_dir in "$SKILLS_DIR"/*/; do
    name="$(basename "$skill_dir")"
    if [[ -L "$TARGET_DIR/$name" || -e "$TARGET_DIR/$name" ]]; then
      rm -rf "$TARGET_DIR/$name"
      echo "    ✓ removed $name"
      removed=$((removed+1))
    fi
  done
  echo "==> Removed $removed skill(s)."
  exit 0
fi

echo "==> Installing Wisdom Council Layer skills to: $TARGET_DIR"
mkdir -p "$TARGET_DIR"

installed=0
for skill_dir in "$SKILLS_DIR"/*/; do
  name="$(basename "$skill_dir")"
  target="$TARGET_DIR/$name"
  rm -rf "$target"          # remove any previous install (symlink or dir)
  ln -s "$skill_dir" "$target"
  installed=$((installed+1))
  echo "    ✓ $name"
done

# Verify every symlink resolves to a readable SKILL.md
failures=0
for target in "$TARGET_DIR"/*/; do
  if [[ -f "$target/SKILL.md" ]]; then
    :
  else
    echo "    ✗ broken: $target"
    failures=$((failures+1))
  fi
done

echo ""
if [[ $failures -gt 0 ]]; then
  echo "==> $installed installed, $failures broken symlink(s). Check $SKILLS_DIR."
  exit 1
fi

echo "==> Done: $installed skills installed to $TARGET_DIR"
echo ""
echo "    Callable by name from anywhere:"
echo "      Skill: originality"
echo "      Skill: anti-generic-filter"
echo "      Skill: wisdom-council"
echo ""
echo "    Note: restart Claude Code or open /skills once to reload the skill listing."
