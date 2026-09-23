#!/usr/bin/env bash
# Validate a single skill directory. `.github/workflows/validate-skills.yml`
# runs this over every skill in `plugins/*/skills/*` on push and pull request.
#
# Rules follow Claude Code's SKILL.md frontmatter (code.claude.com/docs/en/skills),
# which is what this library actually ships into, and the agentskills.io naming
# spec, which is what it would need to publish outside Claude Code.
#
# Usage:
#   validate-skill.sh <skill-directory>
#
# Hard rules (every violation fails):
#   - SKILL.md exists
#   - Starts and ends with `---` (ASCII hyphens only)
#   - `name`: 2-64 chars, ^[a-z0-9](?:[a-z0-9]|-(?!-))*[a-z0-9]$, matches dir name
#   - `description`: required, non-empty, ≤1024 chars, no leftover TODO
#   - `description` may be a plain, quoted, or block scalar
#     (`description: >` / `|`); whichever it is, the text inside is what
#     gets checked, because that is what reaches the model
#   - `description` contains no ': ' (colon-space) and no '<' / '>'
#   - `compatibility` (if set): ≤500 chars
#   - frontmatter contains only fields Claude Code documents (see
#     ALLOWED_FIELDS below); `version`, `author`, `tags` and `platforms`
#     are not among them and belong under `metadata:`
#   - body is non-empty

set -euo pipefail

die() { echo "FAIL: $*" >&2; exit 1; }

[[ $# -ne 1 ]] && die "Usage: validate-skill.sh <skill-directory>"

SKILL_DIR="$1"
SKILL_MD="$SKILL_DIR/SKILL.md"
EXPECTED_NAME=$(basename "$SKILL_DIR")

[[ -d "$SKILL_DIR" ]] || die "Directory does not exist: $SKILL_DIR"
[[ -f "$SKILL_MD" ]]  || die "SKILL.md not found in $SKILL_DIR"

CONTENT=$(<"$SKILL_MD")

# Check frontmatter delimiter
if [[ "$CONTENT" != ---* ]]; then
  FIRST3=$(echo "$CONTENT" | head -c 12)
  if echo "$FIRST3" | LC_ALL=C grep -qP '[\x{2010}-\x{2015}\x{FE58}\x{FE63}\x{FF0D}]' 2>/dev/null; then
    die "SKILL.md starts with typographic dashes (em-dash/en-dash) instead of three ASCII hyphens (---) — fix the frontmatter delimiter"
  fi
  die "SKILL.md must start with --- (YAML frontmatter)"
fi

# Extract frontmatter (between the first pair of `---` lines)
FRONTMATTER=$(echo "$CONTENT" | awk '/^---$/{n++; next} n==1')
[[ -n "$FRONTMATTER" ]] || die "Empty or malformed frontmatter"

BODY=$(echo "$CONTENT" | awk '/^---$/{n++; next} n>=2')
BODY_TRIMMED=$(echo "$BODY" | sed '/^[[:space:]]*$/d')
[[ -n "$BODY_TRIMMED" ]] || die "SKILL.md body is empty (no content after frontmatter)"

# ── name ─────────────────────────────────────────────────────────────────────
NAME_LINE=$(echo "$FRONTMATTER" | grep -m1 '^name:' || true)
[[ -n "$NAME_LINE" ]] || die "Missing 'name' in frontmatter"
NAME_RAW=$(echo "$NAME_LINE" | sed 's/^name:[[:space:]]*//')

# Reject quoting on name
if [[ "$NAME_RAW" =~ ^\".*\"$ ]] || [[ "$NAME_RAW" =~ ^\'.*\'$ ]]; then
  die "'name' must not be wrapped in quotes — write it as a plain YAML scalar"
fi
NAME="$NAME_RAW"

[[ ${#NAME} -ge 2 ]]  || die "Name '$NAME' is too short (min 2 characters)"
[[ ${#NAME} -le 64 ]] || die "Name '$NAME' is too long (${#NAME} chars, max 64)"
# Strict: lowercase a-z, digits, single hyphens; no consecutive hyphens; must
# start and end with [a-z0-9]. Matches the agentskills.io spec.
if echo "$NAME" | grep -qE '\-\-'; then
  die "Name '$NAME' contains consecutive hyphens — not allowed"
fi
if ! echo "$NAME" | grep -qE '^[a-z0-9][a-z0-9-]*[a-z0-9]$'; then
  die "Name '$NAME' is invalid — use only lowercase a-z, digits 0-9, and single hyphens; must start and end with a letter or digit (e.g. 'my-skill')"
fi
if [[ "$NAME" != "$EXPECTED_NAME" ]]; then
  die "Name '$NAME' must match the parent directory name '$EXPECTED_NAME' (agentskills.io spec)"
fi

# ── description ──────────────────────────────────────────────────────────────
DESC_LINE=$(echo "$FRONTMATTER" | grep -m1 '^description:' || true)
[[ -n "$DESC_LINE" ]] || die "Missing 'description' in frontmatter"
DESC_RAW=$(echo "$DESC_LINE" | sed 's/^description:[[:space:]]*//')

# ── Block scalars ────────────────────────────────────────────────────────────
# `description: >` (folded) and `description: |` (literal), with optional indent
# and chomping indicators, put the real text on the indented lines below. Read
# those lines, or every check below runs against a one-character indicator: `>`
# fails the angle-bracket rule for the wrong reason, and `|` passes every rule
# while checking nothing at all.
DESC_IS_BLOCK=0
DESC_WAS_QUOTED=0
if [[ "$DESC_RAW" =~ ^[\>\|][0-9]*[-+]?$ ]]; then
  DESC_IS_BLOCK=1
  DESC_RAW=$(echo "$FRONTMATTER" | awk '
    /^description:[[:space:]]*[>|]/ { collecting = 1; next }
    collecting && /^[[:space:]]+[^[:space:]]/ { sub(/^[[:space:]]+/, ""); print; next }
    collecting && /^[[:space:]]*$/ { print ""; next }
    collecting { exit }
  ' | tr '\n' ' ' | sed 's/[[:space:]]\{1,\}/ /g; s/^ //; s/ $//')
  [[ -n "$DESC_RAW" ]] || die "'description' uses a block scalar but has no indented text beneath it"
fi

# A quoted scalar is valid YAML and Claude Code reads it correctly, so quoting
# is not rejected. Unwrap it and check the text inside, which is what actually
# reaches the model. An unterminated quote is still an error, because that means
# the description runs past the line the parser thinks it ends on.
if [[ "$DESC_IS_BLOCK" -eq 0 ]]; then
  if [[ "$DESC_RAW" =~ ^\"(.*)\"$ ]] || [[ "$DESC_RAW" =~ ^\'(.*)\'$ ]]; then
    DESC_RAW="${BASH_REMATCH[1]}"
    DESC_WAS_QUOTED=1
  elif [[ "$DESC_RAW" =~ ^[\"\'] ]]; then
    die "'description' opens with a quote that is never closed on the same line — YAML will not read it as you intend"
  fi
fi
DESCRIPTION="$DESC_RAW"
[[ -n "$DESCRIPTION" ]] || die "'description' is empty"

if echo "$DESCRIPTION" | grep -qiE '\bTODO\b'; then
  die "Description still contains the placeholder 'TODO'"
fi

# ': ' (colon-space) is ambiguous only in a bare plain scalar. A block scalar
# and a quoted scalar both carry it as ordinary text.
if [[ "$DESC_IS_BLOCK" -eq 0 ]] && [[ "$DESC_WAS_QUOTED" -eq 0 ]] && \
   echo "$DESCRIPTION" | grep -q ': '; then
  die "Description contains ': ' (colon-space) which breaks plain YAML scalars — reword (e.g. 'X: a, b, c' → 'X — a, b, c' or 'X including a, b, c')"
fi

# Reject angle brackets (interpreted as XML by the system-prompt assembler).
if echo "$DESCRIPTION" | grep -qE '[<>]'; then
  die "Description contains angle brackets (< or >) which inject XML tags into the agent's system prompt — reword without them"
fi

DESC_LEN=${#DESCRIPTION}
if [[ "$DESC_LEN" -gt 1024 ]]; then
  die "Description is too long ($DESC_LEN chars, max 1024)"
fi

# ── compatibility (optional) ─────────────────────────────────────────────────
COMPAT_LINE=$(echo "$FRONTMATTER" | grep -m1 '^compatibility:' || true)
if [[ -n "$COMPAT_LINE" ]]; then
  COMPAT_RAW=$(echo "$COMPAT_LINE" | sed 's/^compatibility:[[:space:]]*//')
  if [[ "$COMPAT_RAW" =~ ^\"(.*)\"$ ]] || [[ "$COMPAT_RAW" =~ ^\'(.*)\'$ ]]; then
    COMPAT_RAW="${BASH_REMATCH[1]}"
  fi
  if [[ ${#COMPAT_RAW} -gt 500 ]]; then
    die "'compatibility' is too long (${#COMPAT_RAW} chars, max 500)"
  fi
fi

# ── Unknown top-level fields ─────────────────────────────────────────────────
# Claude Code's documented SKILL.md frontmatter (code.claude.com/docs/en/skills).
# The first six are also the agentskills.io subset that works outside Claude
# Code; the rest are Claude Code extensions. `version`, `author`, `tags` and
# `platforms` are deliberately absent: the docs do not define them, so they
# belong under `metadata:`.
ALLOWED_FIELDS="name description license compatibility metadata allowed-tools \
disallowed-tools when_to_use argument-hint arguments disable-model-invocation \
user-invocable model effort context agent background hooks paths shell"
while IFS= read -r line; do
  # Only consider lines that start at column 0 with `key:` (skip indented map children).
  if [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_-]*)[[:space:]]*: ]]; then
    KEY="${BASH_REMATCH[1]}"
    if ! echo " $ALLOWED_FIELDS " | grep -q " $KEY "; then
      die "Unknown frontmatter field '$KEY'. Claude Code defines only: $ALLOWED_FIELDS (put custom keys under 'metadata:')"
    fi
  fi
done <<< "$FRONTMATTER"

# ── Tokenizer control tokens in any markdown file under the skill ────────────
# These look like text to a human but the tokenizer turns them into reserved
# IDs the model never sees as text — embedding them in a skill teaches the
# model nothing useful and frequently confuses it.
CONTROL_HITS=$(grep -REn '<\|[A-Za-z][A-Za-z0-9_-]*\|>' --include='*.md' "$SKILL_DIR" 2>/dev/null || true)
if [[ -n "$CONTROL_HITS" ]]; then
  echo "$CONTROL_HITS" | head -5 >&2
  die "Found tokenizer control token(s) shaped like <|...|> in skill markdown — these are special tokens the model cannot read as text; remove or rewrite the examples"
fi

LINE_COUNT=$(echo "$CONTENT" | wc -l | tr -d ' ')
echo "OK: Skill '$NAME' is valid ($LINE_COUNT lines)"
