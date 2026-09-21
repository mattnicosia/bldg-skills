# NOVATerra profile

Use only when the repo is NOVATerra / BLDG Estimator. Skip for other products.

## Product job

AI takeoff + estimating + project control for contractors. Offline-first. Org / multi-user. Competes with Togal, Beam, Kreo, Outbuild.

## Stack invariants

- React app shell, Gantt, estimate surfaces, landing/signin
- Supabase auth, RLS, realtime, blobs
- IndexedDB sync, optimistic updates, dedup
- One active estimate per project unless the code explicitly changed that
- Vercel deploy

Never trade sync correctness for UI wow. If IDB / realtime / blobs are in play, run `cloud-sync-auditor`.

## Design bar

- Deep charcoal / slate base
- High-sat indigo (`#6366F1`) and amber accents, used with restraint
- Premium tool density, not sparse marketing-SaaS emptiness
- No generic Inter/Roboto system look, no teal default slop, no flat card grids as the whole language
- Signature moments belong on takeoff, Gantt, and landing/signin — not on every settings row

## AI lanes inside this product

Typical call sites to hunt:

- vision / VLM takeoff on plan PDFs
- quantity / assembly suggestion
- agent routing (LangGraph or similar)
- SEO / outbound agents if present in the same monorepo
- embeddings for plan or estimate search

Route vision-heavy takeoff separately from text agents. Do not put both on one flagship call if a vision model plus a cheaper text model is cleaner.
