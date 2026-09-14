# Adversarial Workflow — full self-assessment protocol

The mandatory method for KEYSTONE-7 self-assessments. An adversarial panel of
independent agents, not one judge. Proven 2026-07-16: a single DeepSeek judge
scored the KEYSTONE-to-market concept at 74; the same concept under this workflow
(on live web search) failed Gate 3 and shadow-scored ~29. The gap is the method.

## When required

- KEYSTONE scoring a BLDG concept (Matt's own idea)
- Any concept where the scorer has attachment or incentive to inflate
- Any high-stakes build/don't-build decision

## When NOT required (use standard mode)

- Scoring a third-party idea (no attachment)
- Quick triage/generate runs where speed matters more than precision
- Concepts that are brand-new and unbuilt, where judge has no stake

## Agent roster (26 total, all independent)

### Phase 1: Research (3 agents)

| Role | Assignment |
|---|---|
| Competitor researcher | Live web search for pre-launch clones, adjacent products, and funded competitors. Return named URLs, user counts if available, launch dates. |
| Market researcher | Live web search for market signals: funding rounds in the space, news, trend pieces, analyst reports. Return dated sources. |
| Social/community researcher | Live search for X/Reddit/IH/HN discussion, demand signals, complaints about existing solutions. Return links with dates. |

These three run in parallel via `delegate_task` with `tasks=[]` batch mode.

### Phase 2: Gate skeptics (5 agents)

One agent per gate. Each is instructed: "Your job is to FAIL this gate. Find every
reason it should not pass. If you cannot find a fatal flaw, report that honestly."

| Gate | Skeptic instruction |
|---|---|
| Dollar Arrow | Find every reason nobody reaches for money here. Challenge the dollar-arrow framing. |
| Timing Window | Find every reason now is NOT the right time. Challenge timing claims with counter-evidence. |
| Incumbent Immunity | Find every way incumbents or fast followers can copy this in under 90 days. Use Phase 1 research. |
| Witnessable Proof | Find every reason the proof is insufficient, misleading, or circular. |
| Cold-Start Viability | Find every reason the first users won't materialize without a platform. Challenge distribution assumptions. |

### Phase 3: Dimension judges (14 agents)

Two independent judges per dimension. Each scores 0-10 with evidence. Neither sees
the other's score. The lower of the two is used in final math.

| Dimension | Judge 1 scope | Judge 2 scope |
|---|---|---|
| Timing & Substrate | Score with evidence | Score with evidence (independent) |
| Capture | Score with evidence | Score with evidence (independent) |
| Propagation | Score with evidence | Score with evidence (independent) |
| Compression | Score with evidence | Score with evidence (independent) |
| Entrenchment | Score with evidence | Score with evidence (independent) |
| Ignition & Distribution | Score with evidence | Score with evidence (independent) |
| Founder-Market Fit | Score with evidence | Score with evidence (independent) |

### Phase 4: Modifier judges (2 agents)

| Role | Assignment |
|---|---|
| Resonance judge | Determine band (dormant/neutral/warm/hot) from 90-day-recent cited evidence. Output the band and the sources that support it. |
| Fragility judge | List every idea-specific weakness. For each: is there a designed mitigation? Output the multiplier (0.75 / 0.9 / 1.0) with named weaknesses. |

### Phase 5: Pressure test (2 agents)

| Role | Assignment |
|---|---|
| Devil's advocate | Find the kill shot. What single structural flaw makes this concept unfixable? If none exists, say so. Check git for same-day ruler edits and disclose if found. |
| Monetization strategist | Identify every plausible dollar arrow, rank by alignment with the concept and founder. Flag any monetization path that would poison the brand or the instrument's credibility. |

## Execution sequence

1. **Phase 1 first** (parallel). Researchers return competitor/market/social data.
2. **Phase 2 + 3 + 4 in parallel** (21 agents). Each gets the Phase 1 research + the
   concept brief + the asset profile. Gate skeptics get their specific FAIL instruction.
   Dimension judges get their dimension's scoring criteria. Modifier judges get the
   resonance/fragility rules.
3. **Phase 5 last** (parallel). The devil's advocate and monetization strategist get
   the full Phase 1-4 output to synthesize.
4. **Host-side deterministic math.** After all agents return, compute in the main loop:
   - Raw sum = sum of (lower judge score × weight) for all 7 dimensions
   - Effective Compression = min(Compression × resonance multiplier, 10)
   - Raw weighted = raw sum / 100
   - Final internal = raw weighted × fragility multiplier
   - Display = final internal × 1.12
   - Verdict band from display score

**Never let a subagent do the multiplication.** Subagents return dimension scores
and evidence. The host computes the final number. This prevents persuasion-in-math.

## Batch structure for delegate_task

```javascript
// Phase 1: research agents (parallel)
const researchResults = await delegate_task({
  tasks: [
    { goal: "Competitor research...", context: brief + "..." },
    { goal: "Market research...", context: brief + "..." },
    { goal: "Social research...", context: brief + "..." },
  ]
});

// Phase 2-4: gates + dimensions + modifiers (parallel, 21 agents)
const panelResults = await delegate_task({
  tasks: [
    // 5 gate skeptics
    { goal: "FAIL Dollar Arrow gate...", context: brief + researchResults },
    // ... (4 more)
    // 14 dimension judges (2 per dimension)
    { goal: "Score Timing & Substrate (Judge 1)...", context: brief + researchResults },
    { goal: "Score Timing & Substrate (Judge 2)...", context: brief + researchResults },
    // ... (12 more)
    // 2 modifier judges
    { goal: "Determine Resonance band...", context: brief + researchResults },
    { goal: "Determine Fragility multiplier...", context: brief + researchResults },
  ]
});

// Phase 5: pressure test (parallel, 2 agents)
const pressureResults = await delegate_task({
  tasks: [
    { goal: "Devil's advocate: find the kill shot...", context: brief + allPriorResults },
    { goal: "Monetization strategist: identify dollar arrows...", context: brief + allPriorResults },
  ]
});
```

Note: `delegate_task` max concurrent children for this user is 3. The phases above
show the logical structure; in practice, fan each phase out across multiple delegate_task
calls with tasks= arrays sized to the concurrency limit. Phase 2-4 (21 agents) will
complete in ~7 sequential waves of 3 concurrent agents each.

## What this catches that single-judge misses

| Failure mode | How adversarial catches it |
|---|---|
| Competitor blindness (model cutoff) | Phase 1 researchers on live web search |
| Founder optimism on distribution | Gate 5 skeptic instructed to FAIL |
| Overrating the dollar arrow | Gate 1 skeptic + monetization strategist |
| Assuming "nobody would share a low score" | Propagation judges must find counter-evidence |
| Ruler edited same day to favor the concept | Phase 5 devil's advocate checks git |
| Single-judge drift toward "find a path to yes" | 26 agents with kill instructions can't all drift |

## Degraded mode (when web search is unavailable)

If live web search is down (no Firecrawl credits, API outage), the adversarial
workflow still runs but sources are DEGRADED. Adapt:

1. **Mark Sources: DEGRADED** in the output header.
2. **Skip Phase 1** (researchers need web). Use model training knowledge as
   fallback, noting that model cutoff = blind spots on recent competitors.
3. **Run Phases 2 and 5** (gate skeptics + pressure test). Adversarial reasoning
   helps even without live data.
4. **Penalize Incumbent Immunity by 1 point** per the skill's degradation rule.
5. **Host-score dimensions** conservatively. Assume competitors exist, distribution
   is harder than it looks, every gate could fail.
6. **Disclose degradation impact** in the verdict: which gates tilt toward
   over-optimism without live data (usually Incumbent Immunity, Propagation).

Tested 2026-07-16 on the BLDG Talent assessment. Gate skeptics + pressure test
agents produced useful adversarial challenge without live competitor data. The
structure prevents worst blind spots even with one data source absent.

## Practical concurrency limits

The full 26-agent roster assumes unlimited parallel subagents. In practice:

- **Hermes `delegate_task`** caps at 3 concurrent per call. Phase 2-4 (21 agents)
  needs ~7 waves. Full run: 5-10 minutes.
- **Degraded mode skips Phase 3** (14 dimension judges) to stay under 5 minutes
  and ~$0.15-0.40 in API fees vs $0.50-1.30 for the full run.

## Provenance

First run: 2026-07-16, KEYSTONE-7 self-assessment (KEYSTONE-to-market concept).
Single-judge DeepSeek score: 74. Adversarial score: 0 (Gate 3 fail), shadow ~29.
The gap was entirely live competitor data + structural adversity, not model quality.
