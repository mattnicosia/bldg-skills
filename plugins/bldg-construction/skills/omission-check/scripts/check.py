#!/usr/bin/env python3
"""Compare drawing requirements against a priced estimate and rank what is missing.

    python3 check.py requirements.json estimate.json [--out DIR] [--limit N]

requirements.json  [{"requirement": str, "source": "SHEET ref", "trade": str,
                     "detail": str (optional)}, ...]
estimate.json      {"project": str, "trades": {trade: [line, ...]}}
                   or {"lines": [str, ...]} if trades are not separated

Every estimate line goes into every request's state, so the pairwise problem
(R requirements x L lines) collapses to R requests. Jev judges coverage. A
keyword scan runs independently as a second opinion.
"""
import argparse
import json
import os
import re
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jev_client import JevError, ask, confidence, value  # noqa: E402

RISK_LEVELS = ["Trivial", "Noticeable", "Material", "Severe"]

STOP = {
    "the", "and", "for", "with", "per", "all", "new", "existing", "shall", "this",
    "that", "from", "into", "each", "any", "are", "not", "provide", "install",
    "work", "contractor", "drawings", "sheet", "system", "systems", "required",
}


def keywords(text, n=4):
    """Longest distinctive words, used only as an independent cross-check."""
    ws = [w for w in re.findall(r"[A-Za-z]{4,}", text.lower()) if w not in STOP]
    return sorted(set(ws), key=len, reverse=True)[:n]


def keyword_hits(req, lines_blob):
    ks = keywords(req)
    return [k for k in ks if k in lines_blob]


def questions(trades):
    q = {
        "covered": {
            "type": "noul",
            "instructions": (
                "Does any line in `estimate_lines` carry the cost of "
                "`requirement`? Judge whether the work is paid for, not whether "
                "the wording matches."
            ),
            "criteria": {
                "true": "A line clearly includes this work",
                "false": "No line covers it, so it is unpriced",
            },
        },
        "partially_covered": {
            "type": "noul",
            "instructions": (
                "Is `requirement` only partly carried, so a line covers some of "
                "it but a material part is unpriced? A wrong material, a wrong "
                "thickness, or a missing component all count."
            ),
        },
        "material_risk": {
            "type": "score",
            "instructions": "If `requirement` is genuinely unpriced, how material is that to the bid?",
            "criteria": list(RISK_LEVELS),
        },
        "rfi_worthy": {
            "type": "noul",
            "instructions": (
                "Should this go back to the design team as an RFI, rather than "
                "simply being added to the estimate?"
            ),
            "criteria": {
                "true": "The drawings are unclear, contradictory, or incomplete",
                "false": "The drawings are clear and the estimate just lacks the line",
            },
        },
    }
    if trades:
        q["likely_trade"] = {
            "type": "choice",
            "instructions": "Which trade in the estimate should carry `requirement`?",
            "criteria": {t: None for t in trades},
        }
    return q


def load_estimate(path):
    with open(path) as f:
        d = json.load(f)
    if "trades" in d:
        lines, trades = [], sorted(d["trades"])
        for t, ls in d["trades"].items():
            lines += [f"[{t}] {l}" for l in ls]
    else:
        lines, trades = list(d.get("lines") or []), []
    if not lines:
        sys.exit("estimate has no lines")
    return d.get("project", "project"), lines, trades


def main():
    p = argparse.ArgumentParser()
    p.add_argument("requirements")
    p.add_argument("estimate")
    p.add_argument("--out")
    p.add_argument("--limit", type=int)
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    with open(a.requirements) as f:
        reqs = json.load(f)
    if a.limit:
        reqs = reqs[: a.limit]
    project, lines, trades = load_estimate(a.estimate)
    blob = " ".join(lines).lower()

    if a.dry_run:
        print(json.dumps(questions(trades), indent=2))
        print(f"\n{len(reqs)} requirements vs {len(lines)} estimate lines "
              f"= {len(reqs)} requests (not {len(reqs) * len(lines)} pairs)")
        return

    out, tin, tout, errors = [], 0, 0, []
    for i, r in enumerate(reqs, 1):
        state = {
            "requirement": r["requirement"],
            "source_sheet": r.get("source", ""),
            "detail": r.get("detail", ""),
            "estimate_lines": lines,
        }
        try:
            ans, usage = ask(state, questions(trades))
        except JevError as e:
            errors.append({"requirement": r["requirement"], "error": str(e)})
            print(f"  [{i}/{len(reqs)}] FAILED {e}", file=sys.stderr)
            continue
        tin += usage.get("input_tokens", 0)
        tout += usage.get("output_tokens", 0)
        j = {k: value(v) for k, v in ans.items()}
        j["material_risk_confidence"] = confidence(ans.get("material_risk"))
        hits = keyword_hits(r["requirement"] + " " + r.get("detail", ""), blob)
        row = {
            **r,
            "jev": j,
            "keyword_hits": hits,
            "miss_score": round(
                (1 - (j.get("covered") or 0))
                + (j.get("material_risk") or 0) / (len(RISK_LEVELS) - 1)
                + (0.3 if not hits else 0.0),
                2,
            ),
            # both methods agree it is absent
            "confirmed_absent": (j.get("covered") or 0) < 0.15 and not hits,
        }
        out.append(row)
        flag = "MISS" if row["confirmed_absent"] else ("part" if (j.get("partially_covered") or 0) > 0.6 else "")
        print(f"  [{i}/{len(reqs)}] {r['requirement'][:48]:50} cov={j.get('covered'):.2f} {flag}")

    out.sort(key=lambda r: -r["miss_score"])
    d = a.out or os.path.dirname(os.path.abspath(a.requirements))
    with open(os.path.join(d, "omission-result.json"), "w") as f:
        json.dump(
            {
                "project": project,
                "date": str(date.today()),
                "requirements": len(reqs),
                "estimate_lines": len(lines),
                "tokens": {"input": tin, "output": tout},
                "errors": errors,
                "results": out,
            },
            f,
            indent=2,
        )
    report(project, out, lines, os.path.join(d, "OMISSION-CHECK.md"))
    print(f"\n{len(out)}/{len(reqs)} judged  tokens {tin} in / {tout} out")
    print(f"report: {os.path.join(d, 'OMISSION-CHECK.md')}")
    if errors:
        print(f"ERRORS: {len(errors)} failed")


def report(project, rows, lines, path):
    absent = [r for r in rows if r["confirmed_absent"]]
    partial = [r for r in rows if not r["confirmed_absent"]
               and (r["jev"].get("partially_covered") or 0) > 0.6]
    # Only an RFI if it is also a real coverage problem. A well-covered line
    # scoring high on rfi_worthy is the model answering "are these drawings
    # ever ambiguous", which is not the question being asked here.
    rfi = [r for r in rows
           if (r["jev"].get("rfi_worthy") or 0) >= 0.5
           and (r["jev"].get("covered") or 0) < 0.6]

    L = [
        f"# Omission check: {project}",
        "",
        f"Generated {date.today()} by `omission-check`. "
        f"{len(rows)} drawing requirements against {len(lines)} priced estimate lines.",
        "",
        "Jev judged coverage; an independent keyword scan ran as a second opinion. "
        "A row is marked **confirmed absent** only when both agree: Jev scored "
        "coverage under 0.15 and no distinctive word appears anywhere in the "
        "estimate. This is a ranked worklist, not a verdict.",
        "",
        "## Bottom line",
        "",
        f"- **{len(absent)}** requirements have no line in the estimate and no keyword match.",
        f"- **{len(partial)}** are partly carried, so a line exists but a material part is unpriced.",
        f"- **{len(rfi)}** should go back to the design team rather than simply be added.",
        "",
    ]

    if absent:
        L += ["## Missing entirely", "",
              "| Miss | Requirement | Sheet | Trade |", "|---:|---|---|---|"]
        for r in absent:
            L.append(f"| {r['miss_score']:.2f} | {r['requirement']} | "
                     f"{r.get('source','')} | {r['jev'].get('likely_trade') or r.get('trade','')} |")
        L.append("")

    if partial:
        L += ["## Carried at the wrong scale or wrong material", "",
              "A line exists, so this will not show up as a hole. That is what makes it dangerous.",
              "", "| Requirement | Sheet | Coverage |", "|---|---|---:|"]
        for r in partial:
            L.append(f"| {r['requirement']} | {r.get('source','')} | "
                     f"{r['jev'].get('covered'):.2f} |")
        L.append("")

    if rfi:
        L += ["## Send to the design team", "",
              "The drawings are unclear, contradictory or incomplete. "
              "Adding a line does not resolve these.", ""]
        for r in rfi:
            L.append(f"- **{r['requirement']}** ({r.get('source','')})")
        L.append("")

    disagree = [r for r in rows
                if (r["jev"].get("covered") or 0) < 0.15 and r["keyword_hits"]]
    if disagree:
        L += ["## The two methods disagreed", "",
              "Jev says unpriced, but a keyword appears in the estimate. Usually a "
              "similarly worded line in a different trade. Read these yourself.",
              ""]
        for r in disagree:
            L.append(f"- **{r['requirement']}** matched `{', '.join(r['keyword_hits'])}`")
        L.append("")

    L += ["## Everything checked", "",
          "| Miss | Requirement | Sheet | Cov | Part | RFI |",
          "|---:|---|---|---:|---:|:-:|"]
    for r in rows:
        j = r["jev"]
        L.append(f"| {r['miss_score']:.2f} | {r['requirement']} | {r.get('source','')} | "
                 f"{j.get('covered'):.2f} | {(j.get('partially_covered') or 0):.2f} | "
                 f"{'yes' if (j.get('rfi_worthy') or 0) >= 0.5 else ''} |")

    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
