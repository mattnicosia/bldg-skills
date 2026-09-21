#!/usr/bin/env bash
# Scan a repo for likely model IDs and LLM call sites.
# Usage: scan-models.sh <repo-root>
set -euo pipefail

ROOT="${1:-.}"
if [[ ! -d "$ROOT" ]]; then
  echo "Not a directory: $ROOT" >&2
  exit 1
fi

cd "$ROOT"

echo "=== model-ish strings in $ROOT ==="
echo

# Stay cheap. Skip giant / generated trees.
EXCLUDES=(
  --glob '!**/node_modules/**'
  --glob '!**/.git/**'
  --glob '!**/dist/**'
  --glob '!**/build/**'
  --glob '!**/.next/**'
  --glob '!**/coverage/**'
  --glob '!**/vendor/**'
  --glob '!**/*.lock'
)

PATTERNS='claude-|claude_opus|claude_sonnet|claude_haiku|claude-fable|anthropic/|gpt-[0-9]|gpt-4|gpt-5|gpt-6|o1-|o3-|o4-|openai/|grok-|xai/|gemini-|google/gemini|text-embedding|embed-|ollama|lmstudio|ChatAnthropic|ChatOpenAI|ChatGoogle|ChatXAI|generateObject|generateText|streamText|modelId|MODEL_|LLM_|OpenRouter|openrouter'

if command -v rg >/dev/null 2>&1; then
  rg -n -S "${EXCLUDES[@]}" -e "$PATTERNS" \
    -g '*.{ts,tsx,js,jsx,mjs,cjs,py,rb,go,rs,json,yml,yaml,toml,env,md}' \
    . || true
else
  grep -RInE "$PATTERNS" \
    --include='*.ts' --include='*.tsx' --include='*.js' --include='*.jsx' \
    --include='*.mjs' --include='*.cjs' --include='*.py' --include='*.json' \
    --include='*.yml' --include='*.yaml' --include='*.toml' --include='*.env' \
    --include='*.md' \
    --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist \
    --exclude-dir=build --exclude-dir=.next --exclude-dir=coverage \
    . || true
fi

echo
echo "=== done ==="
echo "Record each hit as file:line · raw string · job it serves."
