#!/usr/bin/env python3
"""Run the scope-gap sweep over a drawing-index index.json.

Asks Jev, per element: which trade, which CSI subdivision, whether one
subcontractor can carry it, whether a sub could price it today, the single
biggest reason they could not, whether an RFI is warranted, and how material a
miss would be.

Jev never sets a quantity, a price, or the element list. Those are human.

    python3 sweep.py <index.json> [--out DIR] [--limit N] [--dry-run]

Writes the enriched index back in place (a .bak is kept) and a SCOPE-GAPS.md
report beside it.
"""
import argparse
import json
import os
import shutil
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jev_client import JevError, ask, confidence, value  # noqa: E402

GAP_KINDS = {
    "quantity_not_stated": "Specified, but no count, length or area is given",
    "deferred_to_another_sheet": "A value a sub needs is sent to another document",
    "owner_selection_pending": "The owner has not selected the product",
    "conditional_on_unknown": "Applies only if something the drawings never state",
    "existing_condition_unknown": "Depends on an undocumented existing condition",
    "design_incomplete": "Named but not designed",
    "scope_absent_entirely": "Not in the drawings at all",
    "none_it_is_priceable": "A subcontractor could price this today",
}

RISK_LEVELS = ["Trivial", "Noticeable", "Material", "Severe"]


def questions(trades, csi_hint):
    """The seven questions, per element. One request answers all of them."""
    q = {
        "priceable_today": {
            "type": "noul",
            "instructions": (
                "Could a subcontractor produce a firm price for this element "
                "from the specifications shown, with no further information?"
            ),
            "criteria": {
                "true": "Every value needed to price it is present",
                "false": "At least one value a sub would need is missing",
            },
        },
        "gap_kind": {
            "type": "choice",
            "instructions": (
                "What is the single biggest reason a subcontractor could not "
                "price this element from these drawings today?"
            ),
            "criteria": dict(GAP_KINDS),
        },
        "rfi_worthy": {
            "type": "noul",
            "instructions": (
                "Should a written RFI go out on this before bidding, rather "
                "than carrying an assumption?"
            ),
            "criteria": {
                "true": "The answer changes the price and only the design team has it",
                "false": "A normal trade assumption covers it",
            },
        },
        "material_risk": {
            "type": "score",
            "instructions": "If this element is missed entirely, how material is it to the bid?",
            "criteria": list(RISK_LEVELS),
        },
        "single_subcontract": {
            "type": "noul",
            "instructions": "Would one subcontractor normally carry this whole element?",
            "criteria": {
                "true": "One trade buys and installs all of it",
                "false": "It crosses trades and must be split before it can be bid",
            },
        },
    }
    if trades:
        q["trade"] = {
            "type": "choice",
            "instructions": "Which trade carries this element?",
            "criteria": {t: None for t in trades},
        }
    if csi_hint:
        q["csi_subdivision"] = {
            "type": "choice",
            "instructions": "Which CSI subdivision does this element belong to?",
            "criteria": {c: None for c in csi_hint},
        }
    return q


def state_for(el):
    """Only what the drawings say. No quantities, no prices, no prior judgments."""
    return {
        "element": el.get("element"),
        "category": el.get("category"),
        "location": el.get("location"),
        "specifications": [
            {"value": s.get("value"), "source": s.get("source")}
            for s in (el.get("specifications") or [])
        ],
        "notes": el.get("notes") or [],
        "source_sheets": el.get("source_sheets") or [],
    }


def miss_risk(j):
    """Rank order, not a verdict. High means look at this first."""
    unpriceable = 1.0 - (j.get("priceable_today") or 0.0)
    risk = (j.get("material_risk") or 0.0) / (len(RISK_LEVELS) - 1)
    rfi = j.get("rfi_worthy") or 0.0
    absent = 0.5 if j.get("gap_kind") == "scope_absent_entirely" else 0.0
    return round(unpriceable + risk + rfi + absent, 2)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("index")
    p.add_argument("--out", help="directory for the report (default: beside the index)")
    p.add_argument("--limit", type=int, help="only sweep the first N elements")
    p.add_argument("--dry-run", action="store_true", help="print the questions and stop")
    a = p.parse_args()

    with open(a.index) as f:
        idx = json.load(f)
    els = idx.get("elements") or []
    if not els:
        sys.exit("index has no elements; run drawing-index first")
    if a.limit:
        els = els[: a.limit]

    trades = sorted({e["trade"] for e in els if e.get("trade")})
    csi = sorted({e["csi_subdivision"] for e in els if e.get("csi_subdivision")})

    if a.dry_run:
        print(json.dumps(questions(trades, csi), indent=2))
        print(f"\nwould judge {len(els)} elements")
        return

    tin = tout = 0
    errors = []
    for i, el in enumerate(els, 1):
        try:
            ans, usage = ask(state_for(el), questions(trades, csi))
        except JevError as e:
            errors.append({"element": el.get("element"), "error": str(e)})
            print(f"  [{i}/{len(els)}] {el.get('element')}: FAILED {e}", file=sys.stderr)
            continue
        tin += usage.get("input_tokens", 0)
        tout += usage.get("output_tokens", 0)
        j = {k: value(v) for k, v in ans.items()}
        for k in ("trade", "csi_subdivision", "gap_kind", "material_risk"):
            if k in ans:
                j[f"{k}_confidence"] = confidence(ans[k])
        j["scope_miss_risk"] = miss_risk(j)
        el["jev"] = j
        print(f"  [{i}/{len(els)}] {el.get('element')[:44]:46} {j.get('gap_kind')}")

    idx["jev_pass"] = {
        "purpose": (
            "Trade and CSI assignment plus a scope-gap sweep. Jev sets no quantity "
            "and no price; those remain human. Judgments are advisory and every one "
            "is reviewable against the element's own specifications."
        ),
        "date": str(date.today()),
        "elements_judged": len(els) - len(errors),
        "questions_per_element": len(questions(trades, csi)),
        "tokens": {"input": tin, "output": tout},
        "errors": errors,
    }

    shutil.copy2(a.index, a.index + ".bak")
    with open(a.index, "w") as f:
        json.dump(idx, f, indent=2)

    out = a.out or os.path.dirname(os.path.abspath(a.index))
    report(idx, els, os.path.join(out, "SCOPE-GAPS.md"))
    print(f"\njudged {len(els) - len(errors)}/{len(els)}  tokens {tin} in / {tout} out")
    print(f"index:  {a.index}")
    print(f"report: {os.path.join(out, 'SCOPE-GAPS.md')}")
    if errors:
        print(f"ERRORS: {len(errors)} element(s) failed, listed in jev_pass.errors")


def report(idx, els, path):
    judged = [e for e in els if e.get("jev")]
    judged.sort(key=lambda e: -e["jev"]["scope_miss_risk"])
    counts = {}
    for e in judged:
        k = e["jev"].get("gap_kind")
        counts[k] = counts.get(k, 0) + 1
    priceable = [e for e in judged if (e["jev"].get("priceable_today") or 0) >= 0.5]
    rfi = [e for e in judged if (e["jev"].get("rfi_worthy") or 0) >= 0.5]

    L = [
        f"# Scope gaps: {idx.get('project', {}).get('name', 'project')}",
        "",
        f"Generated {date.today()} by `scope-gap-sweep` from "
        f"{len(judged)} indexed elements.",
        "",
        "Jev made the coverage judgments. It set no quantity and no price. "
        "This is a ranked worklist, not a verdict: read the element's own "
        "specifications before acting on any row.",
        "",
        "## Bottom line",
        "",
        f"- **{len(priceable)} of {len(judged)}** elements could be priced firm from these drawings.",
        f"- **{len(rfi)}** warrant a written RFI before bidding.",
        "",
        "## Gaps by kind",
        "",
        "| Count | Kind | Means |",
        "|---:|---|---|",
    ]
    for k, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        L.append(f"| {n} | `{k}` | {GAP_KINDS.get(k, '')} |")

    L += [
        "",
        "## Ranked by miss risk",
        "",
        "| Risk | Element | Trade | Gap | RFI |",
        "|---:|---|---|---|:-:|",
    ]
    for e in judged:
        j = e["jev"]
        L.append(
            f"| {j['scope_miss_risk']:.2f} | {e.get('element','')} | "
            f"{j.get('trade') or e.get('trade','')} | `{j.get('gap_kind')}` | "
            f"{'yes' if (j.get('rfi_worthy') or 0) >= 0.5 else ''} |"
        )

    low = [e for e in judged if (e["jev"].get("trade_confidence") or 1) < 0.5]
    if low:
        L += [
            "",
            "## Trade calls Jev was unsure about",
            "",
            "Low confidence here is the model flagging real ambiguity. Check these.",
            "",
        ]
        for e in low:
            L.append(
                f"- **{e.get('element')}** -> {e['jev'].get('trade')} "
                f"({e['jev'].get('trade_confidence'):.2f})"
            )

    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
