#!/usr/bin/env bash
# Install or symlink skills from this repo into local agent skill dirs.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$ROOT/skills"
LIBRARY_SRC="$ROOT/library"

LINK=0
LIST=0
LIST_LIBRARY=0
LIBRARY=0
CLAUDE=0
CURSOR=0
ONLY=""
FROM=""
EXTRA_DEST=""

usage() {
  cat <<EOF
Usage: ./install.sh [options]

  --link              Symlink instead of copy (git repo stays source of truth)
  --copy              Copy (default)
  --only NAME         Install one curated skill from skills/
  --list              Print curated skills in skills/
  --list-library      Print every library/ leaf skill path (dirs with SKILL.md)
  --from PATH         Install one skill by path (e.g. library/CONSTRUCTION/ROM_Budget_Range)
  --library           Install all library/ leaf skills except library/_ARCHIVE/
  --claude            Also install into ~/.claude/skills even if the dir is missing
  --cursor            Also install into ~/.cursor/skills (and ~/.agents/skills)
  (Codex: auto if ~/.codex/skills exists)
  --dest PATH         Extra destination
  -h, --help          Show this help

Examples:
  ./install.sh --link
  ./install.sh --list
  ./install.sh --only project-level-up --link
  ./install.sh --list-library
  ./install.sh --from library/CONSTRUCTION/ROM_Budget_Range --dest /tmp/skills --link
  ./install.sh --from "library/CODING/MATT_POCOCK_1.2.2/skills/engineering/to-spec" --link
  ./install.sh --library --link
  ./install.sh --from library/_ARCHIVE/some-old-skill --link
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --link) LINK=1; shift ;;
    --copy) LINK=0; shift ;;
    --only)
      if [[ $# -lt 2 ]]; then echo "Missing value for --only" >&2; exit 1; fi
      ONLY="$2"; shift 2 ;;
    --from)
      if [[ $# -lt 2 ]]; then echo "Missing value for --from" >&2; exit 1; fi
      FROM="$2"; shift 2 ;;
    --list) LIST=1; shift ;;
    --list-library) LIST_LIBRARY=1; shift ;;
    --library) LIBRARY=1; shift ;;
    --claude) CLAUDE=1; shift ;;
    --cursor) CURSOR=1; shift ;;
    --dest)
      if [[ $# -lt 2 ]]; then echo "Missing value for --dest" >&2; exit 1; fi
      EXTRA_DEST="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

list_skills() {
  local d
  for d in "$SKILLS_SRC"/*; do
    [ -d "$d" ] || continue
    basename "$d"
  done | LC_ALL=C sort
}

# Print relative paths (from repo root) of every library/ dir that contains SKILL.md.
list_library_skills() {
  local f rel
  find "$LIBRARY_SRC" -name SKILL.md -print0 2>/dev/null \
    | while IFS= read -r -d '' f; do
        rel="${f#"$ROOT"/}"
        dirname "$rel"
      done | LC_ALL=C sort
}

# Same as list_library_skills but skip library/_ARCHIVE/
list_library_skills_no_archive() {
  local f rel
  find "$LIBRARY_SRC" -name SKILL.md -print0 2>/dev/null \
    | while IFS= read -r -d '' f; do
        rel="${f#"$ROOT"/}"
        case "$rel" in
          library/_ARCHIVE/*) continue ;;
        esac
        dirname "$rel"
      done | LC_ALL=C sort
}

if [ "$LIST" -eq 1 ]; then
  echo "Skills in $SKILLS_SRC:"
  list_skills | sed 's/^/  - /'
  exit 0
fi

if [ "$LIST_LIBRARY" -eq 1 ]; then
  if [ ! -d "$LIBRARY_SRC" ]; then
    echo "No library/ directory at $LIBRARY_SRC" >&2
    exit 1
  fi
  echo "Library leaf skills in $LIBRARY_SRC:"
  list_library_skills | sed 's/^/  - /'
  exit 0
fi

DEST_LIST=()
add_dest() {
  local dest="$1"
  local d
  [ -n "$dest" ] || return 0
  for d in ${DEST_LIST[@]+"${DEST_LIST[@]}"}; do
    [ "$d" = "$dest" ] && return 0
  done
  DEST_LIST+=("$dest")
}

if [ -n "${HOME:-}" ]; then
  add_dest "$HOME/.grok/skills"
  if [ "$CLAUDE" -eq 1 ] || [ -d "$HOME/.claude/skills" ]; then
    add_dest "$HOME/.claude/skills"
  fi
  if [ -d "$HOME/.codex/skills" ]; then
    add_dest "$HOME/.codex/skills"
  fi
  if [ "$CURSOR" -eq 1 ] || [ -d "$HOME/.cursor/skills" ]; then
    add_dest "$HOME/.cursor/skills"
  fi
  if [ "$CURSOR" -eq 1 ] || [ -d "$HOME/.agents/skills" ]; then
    add_dest "$HOME/.agents/skills"
  fi
fi
if [ -d /home/workdir/.grok ]; then
  add_dest "/home/workdir/.grok/skills"
fi
add_dest "$EXTRA_DEST"

if [ ${#DEST_LIST[@]} -eq 0 ]; then
  echo "No install destinations. Pass --dest PATH or ensure ~/.grok exists." >&2
  exit 1
fi

# Install skill directory $src under basename $name into each destination.
install_one_from_src() {
  local name="$1"
  local src="$2"
  local dest_dir dest

  if [ ! -f "$src/SKILL.md" ]; then
    echo "Skip $name (no SKILL.md at $src)" >&2
    return 1
  fi

  for dest_dir in "${DEST_LIST[@]}"; do
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

install_one_curated() {
  local name="$1"
  install_one_from_src "$name" "$SKILLS_SRC/$name"
}

# --- mode: --from PATH ---
if [ -n "$FROM" ]; then
  # Normalize: strip leading ./ ; require path under repo
  FROM="${FROM#./}"
  src_abs="$ROOT/$FROM"
  if [ ! -d "$src_abs" ]; then
    echo "Not a directory: $FROM" >&2
    exit 1
  fi
  if [ ! -f "$src_abs/SKILL.md" ]; then
    echo "No SKILL.md in $FROM" >&2
    exit 1
  fi
  name="$(basename "$FROM")"
  install_one_from_src "$name" "$src_abs"
  echo
  echo "Done. Start a new agent session so the skill is picked up."
  exit 0
fi

# --- mode: --library ---
if [ "$LIBRARY" -eq 1 ]; then
  if [ ! -d "$LIBRARY_SRC" ]; then
    echo "No library/ directory at $LIBRARY_SRC" >&2
    exit 1
  fi

  seen_file="$(mktemp "${TMPDIR:-/tmp}/bldg-skills-seen.XXXXXX")"
  trap 'rm -f "$seen_file"' EXIT

  while IFS= read -r rel || [ -n "$rel" ]; do
    [ -n "$rel" ] || continue
    name="$(basename "$rel")"
    prev="$(awk -F'\t' -v n="$name" '$1 == n { print $2; exit }' "$seen_file")"
    if [ -n "$prev" ]; then
      echo "warn: basename collision '$name': already installing from $prev; skipping $rel" >&2
      continue
    fi
    printf '%s\t%s\n' "$name" "$rel" >> "$seen_file"
    install_one_from_src "$name" "$ROOT/$rel"
  done < <(list_library_skills_no_archive)

  echo
  echo "Done. Start a new agent session so the skill is picked up."
  exit 0
fi

# --- curated skills/ (default / --only) ---
if [ ! -d "$SKILLS_SRC" ]; then
  echo "No skills/ directory at $SKILLS_SRC" >&2
  exit 1
fi

if [ -n "$ONLY" ]; then
  install_one_curated "$ONLY"
else
  while IFS= read -r name || [ -n "$name" ]; do
    [ -n "$name" ] || continue
    install_one_curated "$name"
  done < <(list_skills)
fi

echo
echo "Done. Start a new agent session so the skill is picked up."
