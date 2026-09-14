# KEYSTONE-7 Public Surface

How the `/idea-score` scorer, its shareable URLs, OG images, and Dossier
funnel connect. This is the development reference for the public-facing
KEYSTONE-7 product at bldglabs.ai.

## Architecture

```
/idea-score                    Public scorer page (unauthenticated)
/idea-score/[id]               Shareable score page (OG meta tags + scorecard)
/idea-score/[id]/opengraph-image  Server-rendered PNG (Satori/next/og)
/api/keystone-score             POST endpoint (scores + saves)
/api/vantage/dossier/checkout   Stripe Checkout for Dossier upsell
```

## Database

**Table:** `ks7_public_submissions` (Supabase project `nvcgvsstzudjdspxcsoy`)

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Auto-generated, used in share URL |
| `idea_text` | text | The submitted idea |
| `asset_context` | text | Founder's unfair advantage |
| `scorecard` | jsonb | Full Ks7Scorecard object (gates, dims, computed) |
| `final_score` | float | Display score (0-100) |
| `status` | enum | `received`, `scored`, `error` |
| `created_at` | timestamptz | Auto |
| `error` | text | Error detail if status=error |

**DB functions:** `insertPublicSubmission`, `markPublicSubmissionResult`, `getPublicSubmission`, `countPublicScoredToday` — all in `lib/keystone-db.ts`.

## Share Flow

1. User pastes idea + asset context on `/idea-score`
2. Client POSTs to `/api/keystone-score`
3. API saves to `ks7_public_submissions` (status: `received`)
4. API runs KEYSTONE-7 scoring via Anthropic (model: `claude-sonnet-5` by default)
5. API marks submission as `scored` with full scorecard
6. Response includes `{ id, scored: true, scorecard }`
7. Client renders scorecard + share button
8. Share button copies URL: `bldglabs.ai/idea-score/{id}`
9. When shared on X/LinkedIn, OG image auto-renders from `opengraph-image.tsx`
10. Click-through lands on `/idea-score/[id]` with full scorecard + Dossier CTA

## OG Image Generation

Uses `ImageResponse` from `next/og` (Satori). Key constraints:

- **No Tailwind.** Satori supports a subset of CSS. Use inline `style` objects.
- **No external fonts without fetch.** System fonts (`system-ui, sans-serif`) work.
- **Runtime: nodejs.** Required. Edge runtime is possible but untested.
- **Dimensions: 1200x630.** Standard OG size.
- **Colors:** `#62ed02` (lime), `#FF1F3B` (red/kill), `#0a0a0a` (bg), `#ffffff` (light).

### OG Image Layout

```
┌─────────────────────────────────────────────┐
│ KEYSTONE-7  Idea Score        VANTAGE-6 TRACKED │
│                                               │
│                  74.3                         │
│         Real but missing an engine            │
│                                               │
│  ● Dollar  ● Timing  ● Immune  ● Proof  ● Cold │
│                                               │
│  Timing & Substrate  ████████████░░░░░░  6   │
│  Capture             ████████░░░░░░░░░░  4   │
│  Propagation         ██████████░░░░░░░░  5   │
│  ...                                          │
│                                               │
│  bldglabs.ai/idea-score    public batting avg │
└─────────────────────────────────────────────┘
```

## Scoring API

**Endpoint:** `POST /api/keystone-score` (public, outside auth matcher)
**Runtime model:** `claude-sonnet-5` (override: `KEYSTONE_PUBLIC_MODEL` env)
**Daily cap:** 20 scored submissions (past cap, submissions save but skip scoring)
**Honeypot:** Hidden `company` field — if filled, returns fake success (bot caught)

**Request:**
```json
{
  "idea_text": "A marketplace for...",
  "asset_context": "My background, domain access...",
  "company": ""  // leave empty, honeypot
}
```

**Response (scored):**
```json
{
  "ok": true,
  "id": "uuid",
  "scored": true,
  "scorecard": { /* Ks7Scorecard */ }
}
```

**Response (queued — cap hit or scoring error):**
```json
{
  "ok": true,
  "id": "uuid",
  "scored": false,
  "queueNote": "Today's scoring slots are full..."
}
```

## Pitfalls

- **OG image generation fails silently.** If Satori can't render the JSX, it returns a blank image or 500. Always test the OG image URL directly after deploy.
- **Satori flexbox is limited.** No `gap` in older versions, no CSS Grid, no `text-overflow: ellipsis`. Keep layouts simple.
- **Scorecard data shape must match exactly.** The `Ks7Scorecard` type from `components/KeystoneScorecard.tsx` is the canonical shape. The OG generator casts from `sub.scorecard as unknown as Ks7Scorecard`. If the scoring engine changes its output format, both the client component AND the OG generator break.
- **Share URL requires the submission ID.** The scoring API MUST return `id` in the response. The client passes it to the share button. If the API response shape changes and drops `id`, sharing silently breaks.
- **Dossier CTA is score-bucketed.** The copy on the share page changes based on the score band (kill / engine_missing / strong). Don't hardcode a single CTA — use the `nextReading()` function from `public-score-client.tsx`.
