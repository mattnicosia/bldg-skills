#!/usr/bin/env bash
# Install or symlink skills from this repo into local agent skill dirs.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$ROOT/skills"

LINK=0
LIST=0
CLAUDE=0
ONLY=""
EXTRA_DEST=""

usage() {
  cat <<EOF
Usage: ./install.sh [options]

  --link              Symlink instead of copy (git repo stays source of truth)
  --copy              Copy (default)
  --only NAME         Install one skill
  --list              Print skills in this repo
  --claude            Also install into ~/.claude/skills even if the dir is missing
  (Codex: auto if ~/.codex/skills exists)
  --dest PATH         Extra destination
  -h, --help          Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --link) LINK=1; shift ;;
    --copy) LINK=0; shift ;;
    --only) ONLY="$2"; shift 2 ;;
    --list) LIST=1; shift ;;
    --claude) CLAUDE=1; shift ;;
    --dest) EXTRA_DEST="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

list_skills() {
  for d in "$SKILLS_SRC"/*; do
    [ -d "$d" ] || continue
    basename "$d"
  done | sort
}

if [ "$LIST" -eq 1 ]; then
  echo "Skills in $SKILLS_SRC:"
  list_skills | sed 's/^/  - /'
  exit 0
fi

if [ ! -d "$SKILLS_SRC" ]; then
  echo "No skills/ directory at $SKILLS_SRC" >&2
  exit 1
fi

DEST_LIST=""
add_dest() {
  dest="$1"
  [ -n "$dest" ] || return 0
  case " $DEST_LIST " in
    *" $dest "*) return 0 ;;
  esac
  DEST_LIST="$DEST_LIST $dest"
}

if [ -n "${HOME:-}" ]; then
  add_dest "$HOME/.grok/skills"
  if [ "$CLAUDE" -eq 1 ] || [ -d "$HOME/.claude/skills" ]; then
    add_dest "$HOME/.claude/skills"
  fi
  if [ -d "$HOME/.codex/skills" ]; then
    add_dest "$HOME/.codex/skills"
  fi
fi
if [ -d /home/workdir/.grok ]; then
  add_dest "/home/workdir/.grok/skills"
fi
add_dest "$EXTRA_DEST"

install_one() {
  name="$1"
  src="$SKILLS_SRC/$name"
  if [ ! -f "$src/SKILL.md" ]; then
    echo "Skip $name (no SKILL.md)"
    return 1
  fi

  for dest_dir in $DEST_LIST; do
    mkdir -p "$dest_dir"
    dest="$dest_dir/$name"
    if [ -L "$dest" ] || [ -d "$dest" ] || [ -f "$dest" ]; then
      rm -rf "$dest"
    fi
    if [ "$LINK" -eq 1 ]; then
      ln -s "$src" "$dest"
      echo "linked  $dest -> $src"
    else
      cp -R "$src" "$dest"
      echo "copied  $dest"
    fi
  done
}

if [ -n "$ONLY" ]; then
  install_one "$ONLY"
else
  for name in $(list_skills); do
    install_one "$name"
  done
fi

echo
echo "Done. Start a new agent session so the skill is picked up."
