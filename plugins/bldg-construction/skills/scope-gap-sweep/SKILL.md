---
name: scope-gap-sweep
description: Sweep an indexed drawing set for scope a subcontractor could not price, and rank what is missing by how badly it would hurt the bid. Reads a drawing-index index.json, asks Jev a typed question per element, and writes a ranked gap register plus the judgments back into the index. Use after drawing-index and before sow-generator, when the question is "what is missing or undefined in this set", when preparing RFIs off a drawing set, or when someone asks whether a set is complete enough to bid. Do NOT use to compare drawings against a priced estimate; that is omission-check.
---

# Scope gap sweep

Takes an indexed drawing set and answers one question for every element in it:
**could a subcontractor price this today, and if not, why not.**

The output is a ranked worklist of what the drawings do not say, with the reason
named, so each row implies a next step rather than a feeling.

## What it is not

It does not compare drawings against an estimate. That is `omission-check`.

It does not measure, price, or invent scope. Jev never sets a quantity or a
number, and it never decides what the elements are. Those come from the index,
which a reasoning model built.

## Before you run it

1. `drawing-index` has run and `index.json` validates.
2. `TYPESAFE_API_KEY` is exported.
3. Every element carries its `specifications` with sources. The sweep reads only
   what the drawings say. An element with no specifications gets a judgment about
   nothing.

## Run it

```bash
python3 scripts/sweep.py <path-to>/index.json
```

| Flag | Use |
|---|---|
| `--dry-run` | Print the questions and the element count, call nothing |
| `--limit N` | Sweep the first N elements, to check the shape before committing |
| `--out DIR` | Put `SCOPE-GAPS.md` somewhere other than beside the index |

It writes `index.json` back with a `jev` block on every element and a `jev_pass`
block at the top, keeping a `.bak`. It writes `SCOPE-GAPS.md` beside it.

Cost is roughly 1,000 input and 260 output tokens per element, one request each.
Sixty-eight elements came to about a cent.

## The seven questions

One request per element answers all of them.

| Question | Type | What it settles |
|---|---|---|
| `priceable_today` | noul | Could a sub produce a firm price with no further information |
| `gap_kind` | choice | The single biggest reason they could not |
| `rfi_worthy` | noul | Does this need a written RFI, or does a trade assumption cover it |
| `material_risk` | score | How badly a miss would hurt, on four levels |
| `single_subcontract` | noul | Would one sub carry the whole element, or must it be split |
| `trade` | choice | Which trade carries it, chosen from the trades already in the index |
| `csi_subdivision` | choice | Which CSI subdivision, chosen from those already in the index |

`trade` and `csi_subdivision` choose from the values already present in the
index rather than an open list, so the sweep cannot invent a trade the job
does not have.

### The gap kinds

Naming the ways a thing can be missing is what makes the output actionable.
Each kind implies a different next step.

| Kind | Next step |
|---|---|
| `quantity_not_stated` | Measure it, or carry it as a unit price |
| `deferred_to_another_sheet` | Go read that sheet |
| `owner_selection_pending` | Carry an allowance |
| `conditional_on_unknown` | RFI. The condition is never stated |
| `existing_condition_unknown` | Field verify |
| `design_incomplete` | RFI. It is named but not designed |
| `scope_absent_entirely` | Ask whether it is in the contract at all |
| `none_it_is_priceable` | Nothing |

## Reading the output

**`scope_miss_risk` is a sort order, not a verdict.** It combines how
unpriceable the element is, how material a miss would be, whether an RFI is
warranted, and a bump for scope that is absent entirely. Use it to decide what
to read first.

**Low confidence is a signal, not an error.** When `trade_confidence` is under
0.5, the model is telling you the element is genuinely ambiguous. On the test
set every low-confidence call landed on something a person would also argue
about: a framed stair, porch columns, a door opening modification. The report
lists them in their own section.

**Check the element before acting on a row.** Every judgment is reviewable
against the element's own `specifications`, which are cited to a sheet.

## The rule this skill exists for

> [!IMPORTANT]
> Ask about absence directly. The naive framing is a similarity search, which
> finds what is present and is blind to what is missing. A typed Choice over
> named absence modes answers the actual question, and it costs a fraction of a
> cent per element.

> [!WARNING]
> **Gotcha:** a judgment model can only answer questions its state can settle.
> An early version asked whether each element needs an allowance. Every answer
> clustered near 0.5, because allowance against firm is a company policy, not
> something a drawing knows. **When the answers are all near the middle, the
> question is wrong, not the model.** Anything that depends on your own
> standards belongs in code, not in a judgment.

> [!WARNING]
> **Gotcha:** the three primitives return different keys. A noul answers under
> `noul`, a choice under `choice`, a score under `score`. A score returns the
> probability-weighted level **index**, 0 to len(criteria)-1, not a 0 to 1
> fraction, so a four-level rubric returns 0 to 3. Use `jev_client.value()`
> rather than reaching for `["value"]`, which none of them use.

## Files

| Path | What |
|---|---|
| `scripts/sweep.py` | The sweep, the report, the risk ranking |
| `scripts/jev_client.py` | Minimal System One client, no SDK, retries on 429 and 5xx |

Proven on job 260119, 68 elements across 17 trades, 476 judgments.
Reasoning is in `learnings/2026-09-21-ask-jev-what-is-absent.md` in bldg-labs.
