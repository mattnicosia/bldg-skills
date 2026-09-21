# Model registry

Update this file first on every frontier drop, then run audits.

Last updated: 2026-09-13

IDs drift by vendor. Confirm against the provider dashboard before changing production. This table is a routing starting point, not a billing contract.

## Routing classes

| Class | Use for | Do not use for |
|---|---|---|
| Flagship | Architecture, design direction, hard tool-use, takeoff judgment, long ambiguous agents | Classification, bulk extraction, every autocomplete |
| Workhorse | Default product intelligence, most agent steps | The one call that must be best-in-class |
| Fast | Routing, tagging, cheap summaries, UI copy nits | High-stakes quantities or legal/financial text |
| Vision | Plans, screenshots, UI self-check, document pages | Pure text reasoning if a text model is cheaper |
| Embed | Search, dedup, clustering | Generation |
| Local | Offline / privacy / tight loops | Anything that must match hosted quality |

## Current map (Sep 2026)

| Class | Anthropic | OpenAI | xAI | Google | Open / cheap |
|---|---|---|---|---|---|
| Flagship | claude-fable-5-1 | gpt-6-astra | grok-4.6 | gemini-3.1-pro-preview | qwen3.8-max, kimi-k3 |
| Workhorse | claude-opus-5 or claude-sonnet-5 | gpt-5.6-sol or gpt-5.6-terra | grok-4.5 | gemini-3.8-flash | glm-5.3, deepseek-v4-pro |
| Fast | claude-haiku-4-5 | gpt-5.6-luna | grok-code-fast-1 | gemini-3.5-flash-lite | glm-5.3-flash, deepseek-v4-flash |
| Prior flagship still fine | claude-fable-5, claude-opus-4-8 | gpt-5.6-sol | grok-4.5 | gemini-3.7-flash | — |

Treat as **stale / migrate** unless there is a measured reason to keep:

- claude-opus-4-6, claude-sonnet-4-6, claude-opus-4-7
- gpt-4o, gpt-4.1, gpt-5.4, o3, o4-mini
- gemini-1.5-pro, gemini-2.0-flash, gemini-2.5-pro (verify — 2.5 may still be wired)
- grok-2, grok-3, grok-4.3 as a default

## Policy

1. One flagship per workflow max, unless two jobs are truly different (vision takeoff vs code edit).
2. Every hosted call has a fallback ID and a timeout.
3. If a mid-tier now clears the eval, move the call down and keep the flagship as fallback.
4. Embeddings and rerankers are their own row. Do not silently reuse a chat model.
5. After a drop, re-run product evals before flipping production IDs.

## How to edit this file

When a model ships:

1. Put the new ID in the correct class.
2. Demote the previous flagship to "prior" or workhorse.
3. Add old IDs to the stale list.
4. Change **Last updated**.
5. Then run `project-level-up` on money-path repos.
