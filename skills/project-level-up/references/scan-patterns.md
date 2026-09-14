# Scan patterns

Run `scripts/scan-models.sh <repo>` first. Then search anything the script cannot see (env vars, dashboards, prompt files outside the repo).

## Globs worth opening

- `**/*.{ts,tsx,js,jsx,mjs,cjs,py,rb,go,rs,json,yml,yaml,toml,env,md}`
- `**/prompts/**`
- `**/*agent*`
- `**/*llm*`
- `**/*model*`

## Strings to hunt

Model IDs and SDK constructors:

- `claude-`, `anthropic`, `opus`, `sonnet`, `haiku`, `fable`
- `gpt-`, `o1`, `o3`, `o4`, `openai`
- `grok-`, `xai`
- `gemini-`, `google-genai`, `@google/generative-ai`
- `gpt-4o`, `gpt-4.1`, `text-embedding`, `embed`
- `ollama`, `vllm`, `lmstudio`, `openai/`
- `ChatAnthropic`, `ChatOpenAI`, `ChatGoogle`, `ChatXAI`
- `generateObject`, `generateText`, `streamText`, `Anthropic(`, `OpenAI(`
- `model:`, `modelId`, `MODEL_`, `LLM_`

LangGraph / Crew / agent graphs:

- `StateGraph`, `createReactAgent`, `ChatPromptTemplate`
- node names that wrap a model

Config:

- `.env`, `vercel.json`, `wrangler.toml`
- OpenRouter `anthropic/`, `openai/`, `x-ai/`, `google/`

## What to record per hit

`file:line` · raw string · provider · apparent class · called from which user job · estimated volume if obvious (hot path vs admin-only).
