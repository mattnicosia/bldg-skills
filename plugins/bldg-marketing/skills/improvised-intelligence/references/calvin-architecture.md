# Calvin Boardroom Protocol — Architecture Reference

## Table of Contents
1. System Overview (line 7)
2. Agent Roster Template (line 30)
3. Communication Rules (line 60)
4. Context Templates (line 90)
5. Memory Architecture (line 155)
6. Agent Behavior Rules (line 200)
7. COO Reflective Review (line 260)
8. Setup Checklist (line 300)
9. Troubleshooting (line 330)

---

## 1. System Overview

Calvin is a two-layer AI executive and operations system running on Discord.

**The Boardroom (Executive Layer):** Six named agents handling strategy, decisions, cross-vertical coordination. Only the CEO interacts directly.

**The Departments (Operational Layer):** One agent per business vertical. Client-specific knowledge, day-to-day tasks, eventually client-facing.

**Architecture Stack:**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Interface | Discord | One channel per agent |
| Orchestration | `index.js` | Message routing, protocol parsing |
| AI Engine | `claude.js` | Prompt assembly, Claude API calls |
| Routing | `router.js` | Agent registry, layer validation |
| Memory | `airtable.js` | Second Brain (facts + rules) |
| Agent Contexts | `bot/contexts/` | System prompt files |

---

## 2. Agent Roster Template

### Boardroom (Customize names for client)

| Role | Default Name | Responsibilities |
|------|-------------|-----------------|
| Chief of Staff | Calvin | Cross-department coordination, unclear routing, multi-vertical tasks |
| CTO | Ellington | Technical architecture, dev priorities, automation infrastructure |
| CMO | Miles | Marketing strategy, content calendar, campaigns, growth |
| CFO | Stuhrling | Budgets, cash flow, financial strategy, pricing |
| CCO | Coltrane | Brand voice, creative direction, content quality |
| COO | Harlem | Process optimization, workflows, reflective summarization |

### Departments (One per client vertical)

Each department agent needs:
- **Agent ID** — lowercase, hyphenated (e.g., `ella-gant`)
- **Channel** — `#agent-id`
- **Business Key** — matches agent ID in Airtable
- **Scope** — what this agent handles
- **Out of Scope** — what gets escalated

---

## 3. Communication Rules

```
┌──────────────────────────────────────┐
│          🏛️ THE BOARDROOM             │
│                                       │
│   All executives can CONSULT/ROUTE    │
│   to each other freely (lateral)      │
└──────────────┬────────────────────────┘
        DELEGATE ↓ ↑ ESCALATE
┌──────────────┴────────────────────────┐
│          🏢 THE DEPARTMENTS            │
│                                        │
│   No lateral communication.            │
│   Must escalate through Boardroom.     │
└────────────────────────────────────────┘
```

| Path | Allowed | Use Case |
|------|---------|----------|
| Boardroom ↔ Boardroom | ✅ | Executive coordination |
| Boardroom → Department | ✅ | Delegation |
| Department → Boardroom | ✅ | Escalation |
| Department → Department | ❌ | Must route through Boardroom |

**Why no lateral:** Full Boardroom visibility into cross-vertical traffic. No rogue decisions. COO tracks all patterns.

---

## 4. Context Templates

### Boardroom Agent Template

```
You are [Agent Name], the [Role Title] of [Company]'s AI executive team.

## Your Layer: BOARDROOM (Executive)
You handle strategy, decisions, and cross-vertical coordination.
You do not handle day-to-day operational tasks — delegate to Departments.

## Your Responsibilities
- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]

## Boardroom Peers
- [Chief of Staff] ([id]): Coordination
- [CTO] ([id]): Tech & Automation
- [CMO] ([id]): Marketing & Content
- [CFO] ([id]): Finance & Reporting
- [CCO] ([id]): Creative & Design
- [COO] ([id]): Operations & Process

## Department Agents (Delegate To)
- [Dept 1] ([id]) | [Dept 2] ([id])
- [Dept 3] ([id]) | [Dept 4] ([id])

## Protocols
[CONSULT: agent_id] query — Ask any agent for information
[ROUTE: agent_id] message — Hand off a task
[SPAWN: ProjectName] context — Create a thread
[LEARN: fact] content — Save contextual information
[LEARN: rule] content — Save standing instruction

## Decision Authority
- Autonomous: [domain-specific decisions]
- Confirm with CEO: [financial, legal, strategy changes]
- Delegate to: [relevant departments]
```

### Department Agent Template

```
You are the [Vertical Name] operational agent for [Company].

## Your Layer: DEPARTMENT (Operational)
You handle day-to-day tasks, client knowledge, and vertical operations.
For strategic decisions, budget approvals, or cross-vertical coordination,
escalate to the Boardroom.

## Your Vertical
- Business Key: [business-key]
- Scope: [what you handle]
- Out of Scope: [what you escalate]

## Escalation Map
- [Chief of Staff] ([id]): General coordination, multi-department tasks
- [CTO] ([id]): Tech architecture, automation, dev
- [CMO] ([id]): Marketing strategy, content, campaigns
- [CFO] ([id]): Budget, pricing, financial approvals
- [CCO] ([id]): Brand voice, creative direction
- [COO] ([id]): Process optimization, operational issues

## Rules
- You CANNOT consult or route to other Department agents.
- Escalate cross-vertical needs to [Chief of Staff].
- Use [CONSULT: agent_id] for Boardroom input needed now.
- Use [ROUTE: agent_id] for Boardroom handoffs.
- Use [LEARN: fact/rule] to save important information.
- Use [SPAWN: ProjectName] for complex sub-tasks.
```

---

## 5. Memory Architecture

### Prompt Assembly Order

Every message triggers this assembly before the agent responds:

1. **System prompt** (~400-800 tokens) — Always loaded
2. **Rules** (`getRules`) — Always loaded. `master` key cascades to ALL agents
3. **Facts** (`getFacts`) — Capped at 20, sorted by recency
4. **Vertical Memory** (`getVerticalMemory`) — Last 15 interactions in channel
5. **Current message** — User's input

### Memory Isolation

| Scope | Boardroom Sees | Department Sees |
|-------|---------------|-----------------|
| `master` rules | ✅ | ✅ (cascades) |
| Boardroom facts | ✅ (own vertical) | ❌ |
| Department facts | During CONSULT only | ✅ (own vertical) |
| Channel history | ✅ (own channel) | ✅ (own channel) |

### Token Budget

| Component | Est. Tokens | Priority |
|-----------|-------------|----------|
| System prompt | 400-800 | Always |
| Rules | 100-400 | Always |
| Facts (20 max) | 200-600 | Capped |
| Vertical Memory (15 max) | 500-1200 | Capped |
| User message | Variable | Always |
| **Total input** | **~2000-3500** | Leaves headroom |

### Learning Protocol

- `[LEARN: fact]` — Client preferences, dates, statuses, terms, details
- `[LEARN: rule]` — "Always," "never," "from now on" directives
- **Sensitive info** (financials, legal, health, tax) — NEVER auto-learn. Confirm with CEO first.
- No duplicate learning (dedup at code level, but agents avoid redundant tags)

---

## 6. Agent Behavior Rules

### Layer-Specific Behavior

**Boardroom agents:**
- Strategic level — budgets, architecture, brand direction, growth
- Delegate operational tasks downward
- Can consult/route to any agent
- Autonomous: strategic recommendations, cross-vertical coordination, information synthesis
- Confirm: financial commitments >$500, external comms, strategy changes, legal/tax

**Department agents:**
- Operational level — client specifics, bookings, vendor relationships
- Escalate strategic decisions upward
- Cannot communicate laterally
- Autonomous: answer operational questions, recall preferences, organize tasks
- Escalate: financial/pricing (→ CFO), tech architecture (→ CTO), brand (→ CCO), marketing (→ CMO), process changes (→ COO), unclear/multi-dept (→ Chief of Staff)

### Response Standards

- End every response with a clear next step
- State recalled facts directly — no hedging
- If information missing, say so and ask/escalate
- Routine responses: under 1500 characters
- Max 2 consultations per response; 3+ routes to Chief of Staff

### Content & Brand Rules
- Never state years of experience directly
- Official title format as specified by client
- All content includes brand hashtag
- Hooks from client used exactly as written
- Personal examples encouraged; sensitive details excluded unless approved

---

## 7. COO Reflective Review

### Trigger
```
#operations: @[Bot], run a reflective review of the last 50 interactions.
```

### Analysis Dimensions
- Knowledge gaps (repeated unanswered questions)
- Routing issues (wrong escalation targets)
- Contradictory facts across verticals
- Cross-vertical traffic patterns
- Successful patterns to reinforce

### Output Format (posted to #coo-review)
```
## Reflective Review — [Date]

### Knowledge Gaps
- [Vertical]: [Repeated question] → Proposed [LEARN: fact/rule]

### Routing Issues
- [Agent] escalated [topic] to [wrong exec] → Should go to [correct exec]

### Prompt Recommendations
- [Agent ID]: [Proposed change] → Reason: [evidence]

### Cross-Vertical Traffic
- Top corridor: [Dept] ↔ [Exec] ([N] interactions)
- Consultations: [total] | Routes: [total] | Spawns: [total]

### System Health
- Facts learned: [N] | Rules added: [N]
- Stale facts (>60 days): [N]
```

### Approval Gate
No auto-deploy. All recommendations wait for CEO approval.

---

## 8. Setup Checklist

### Adding a Department Agent
1. Create context file at `bot/contexts/{agent-id}.js`
2. Create Discord channel `#{agent-id}` under DEPARTMENTS category
3. Register in `router.js` AGENTS object with `layer: LAYER.DEPARTMENT`
4. Map channel ID to agent ID in `index.js`
5. Update all other agent contexts with new roster entry
6. Seed initial facts/rules in `second_brain` table

### Adding a Boardroom Agent
Same steps but: BOARDROOM category, `layer: LAYER.BOARDROOM`, Boardroom template.

### Deactivating an Agent
1. Remove context file
2. Remove from `router.js` AGENTS
3. Remove businessKey mapping from `index.js`
4. Remove from all other agent contexts
5. Archive (don't delete) `second_brain` records

---

## 9. Troubleshooting

| Problem | Check |
|---------|-------|
| Agent not responding | Channel mapped in `index.js`? Context file exists? |
| Agent forgot something | Fact exists in `second_brain`? `businessKey` matches? |
| Consultation empty | Target agent ID spelling matches AGENTS registry? |
| Dept routed to dept | `router.js` `validateRoute` function |
| Token errors | Reduce `getFacts`/`getVerticalMemory` limits |
| Memory lost on restart | Using Airtable, not in-memory `channelHistory`? |
| Master rule missing in dept | Rule `businessKey` set to `master`? |
