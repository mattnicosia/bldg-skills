---
name: omission-check
description: Compare what a drawing set requires against what a priced estimate carries, and rank what is missing by how badly it would hurt the bid. Use before an estimate goes out, when asked to review an estimate for scope misses, when a second set of eyes is wanted on someone's numbers, or after an addendum lands on a job already priced. Reads drawing requirements plus the estimate's own line items and writes a ranked omission report separating what is absent, what is carried at the wrong scale, and what needs an RFI. Do NOT use to sweep a drawing set on its own; that is scope-gap-sweep.
---

# Omission check

Answers one question: **what do the drawings require that this estimate does
not carry.**

It separates three outcomes, because they need different responses:

| Outcome | What it means | What you do |
|---|---|---|
| Missing entirely | No line, no keyword match | Add it, or confirm it is excluded |
| Carried at the wrong scale | A line exists but prices the wrong thing | Requote. **This is the dangerous one** |
| Needs an RFI | The drawings are unclear or contradictory | Send it to the design team |

The middle row is the reason this skill exists. A hole is easy to spot. A line
that prices a 4 inch slab when the drawing shows a 9.5 inch pile-supported
structural slab looks complete in every review.

## Before you run it

1. **Establish the current drawing set first.** On a job with addenda, the
   current set is the addendum sheets plus every original sheet not reissued.
   Index the original and the addendum separately, diff the sheet lists, and
   build the merged set. Pricing off the superseded issue is its own failure.
2. `drawing-index` has run over that merged set.
3. `TYPESAFE_API_KEY` is exported.

## Inputs

**`requirements.json`** is what the drawings demand. One object per requirement.

```json
[{"requirement": "Structural slab infill at pile-supported slab",
  "source": "S-100.00 detail 2",
  "trade": "Concrete",
  "detail": "4000 PSI, #6 bar at 8in oc each way, doweled 12in into the existing slab in epoxy, existing rebar reconnected with mechanical couplers."}]
```

`detail` carries the drawing's own words and does most of the work. Without it
a requirement is just a title, and a title cannot be judged against a line item.

Build this from the extracted sheets: schedules, keynotes, general notes, and
any sentence that assigns work to a contractor. The phrases worth hunting are
"shall provide", "by the contractor", "in the bid", "furnish and install",
"whether indicated on the drawings or not".

**`estimate.json`** is the estimate's own line items.

```json
{"project": "Job name",
 "trades": {"Concrete": ["Sawcut Existing 4in Slab 24.08 LF", "..."],
            "Electrical": ["..."]}}
```

Use `{"lines": [...]}` if trades are not separated. Keep the quantity and unit
in the line text: "4in" against "9.5in" is exactly the signal being tested.

## Run it

```bash
python3 scripts/check.py requirements.json estimate.json
```

| Flag | Use |
|---|---|
| `--dry-run` | Print the questions and the request count, call nothing |
| `--limit N` | First N requirements only |
| `--out DIR` | Where the report lands |

Writes `OMISSION-CHECK.md` and `omission-result.json`.

## Why it is affordable

R requirements against L estimate lines is R x L pairs. 65 against 121 is 7,865,
which no reasoning model can read on every job.

**The whole estimate goes into every request's state.** So it is R requests, not
R x L. Sixty-five requirements cost about eight cents.

## Two methods, one flag

Jev judges coverage. Independently, a keyword scan checks whether any
distinctive word from the requirement appears anywhere in the estimate text.

A row is **confirmed absent** only when both agree. One confident method is not
evidence.

When they disagree, the report says so in its own section rather than picking a
winner. On the test run that section caught an AABC test-and-balance requirement
matching the word "ductwork" in an unrelated HVAC line, which is the exact shape
of a false clear.

## Reading the output

**`miss_score` is a sort order.** Uncovered plus material plus a bump when no
keyword matched. It decides reading order, nothing else.

**Check the "wrong scale" section carefully.** Those are items where a line
exists, so no reviewer will notice a hole. Coverage between roughly 0.15 and 0.6
with `partially_covered` high is the signature.

**Report the true negatives too.** On the test run, gypsum board scored 0.96 and
sprinkler relocation 0.97, both correctly cleared. Telling an estimator what
they got right is the difference between a colleague's review and a scolding,
and it is also evidence the check is calibrated rather than just pessimistic.

## Gotchas

> [!WARNING]
> **Give the requirement the drawing's own words.** A requirement with an empty
> `detail` is a title, and the check degrades into keyword matching. The slab
> case only works because the detail carries "9.5in pile supported" for the
> estimate's "4in" to contradict.

> [!WARNING]
> **`rfi_worthy` asks whether the drawings are ambiguous, not whether the item
> is missing.** A fully covered line can score high on it. The report filters
> the RFI section to items also scoring under 0.6 on coverage; without that
> filter a correctly priced sprinkler line appeared in the RFI list.

> [!WARNING]
> **A dangling detail reference is a reason scope goes missing, not a footnote.**
> On the proving job an addendum sheet pointed its slab infill at `1/X-100`, and
> no sheet X-100 existed. The detail was on S-100.00. Anyone chasing that
> reference found nothing, and the scope was priced as an ordinary slab patch.
> When a requirement cites a sheet not in the set, say so in the report.

## Sending the result

If the output goes to the person who wrote the estimate, lead with the drawings
rather than the estimate, and keep the correct calls in. The finding is that a
drawing says something surprising, not that someone failed.

## Files

| Path | What |
|---|---|
| `scripts/check.py` | The comparison, both methods, the report |
| `scripts/jev_client.py` | Minimal System One client, no SDK |

Proven on job 260120, 65 requirements against 121 priced lines across 16 trades.
Reasoning is in `learnings/2026-09-21-ask-jev-what-is-absent.md` in bldg-labs.
