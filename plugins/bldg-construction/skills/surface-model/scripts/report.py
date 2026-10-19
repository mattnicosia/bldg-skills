"""
report.py -- the two things a person reads.

  revision report   after an issue drops: every lineage event that needs a decision
                    and every pin whose status is not exact or readdressed, with the
                    quote, so the decision reads "which half of 204 did RFI-031 mean".
  change list       between two revisions: one line per surface whose length or area
                    changed, with before, after and delta, plus spaces added, split,
                    merged or gone. This is the scope list a change order starts from.
                    It carries no price. Rates come from the job's estimate pins, when
                    the job has them; otherwise the line says needs pricing.
"""
from __future__ import annotations

import address as A
from pins import review_queue, status
from store import live_spaces, live_surfaces, rev_index, space_at, surface_at


def proposal_report(model: dict, proposal: dict) -> str:
    lines = [f"# Revision proposal: {proposal['prev']} to {proposal['rev']}", ""]
    if proposal.get("holds"):
        lines.append("## Held")
        lines.extend(f"- {h}" for h in proposal["holds"])
        lines.append("")
    need = [e for e in proposal["events"] if e.get("decision") == "needs_person"]
    auto = [e for e in proposal["events"] if e.get("decision") != "needs_person"]
    lines.append(f"## Decisions needed ({len(need)})")
    for i, e in enumerate(proposal["events"]):
        if e.get("decision") != "needs_person":
            continue
        lines.append(f"- [{i}] {_event_words(e)}")
    lines.append("")
    lines.append(f"## Applied on accept ({len(auto)})")
    for i, e in enumerate(proposal["events"]):
        if e.get("decision") == "needs_person":
            continue
        lines.append(f"- [{i}] {_event_words(e)}")
    lines.append("")
    pins_at_risk = _pins_touching(model, proposal)
    if pins_at_risk:
        lines.append(f"## Pins on spaces that change ({len(pins_at_risk)})")
        lines.extend(f"- {p}" for p in pins_at_risk)
        lines.append("")
    return "\n".join(lines)


def _event_words(e: dict) -> str:
    k = e["kind"]
    if k == "carry":
        tag = []
        if e.get("readdressed"):
            tag.append(f"readdressed to {e['to']}")
        if e.get("moved"):
            tag.append("outline changed")
        return f"carry {e['address']}" + (f" ({', '.join(tag)})" if tag else "")
    if k == "split":
        return f"split {e['address']} into {', '.join(e['to'])}"
    if k == "merge":
        return f"merge {', '.join(e['addresses'])} into {e['to']}"
    if k == "retire":
        return f"retire {e['address']}: {e['reason']}"
    if k == "new":
        return f"new {e['address']}"
    return str(e)


def _pins_touching(model: dict, proposal: dict) -> list[str]:
    out = []
    changing = set()
    for e in proposal["events"]:
        if e["kind"] in ("split", "retire"):
            changing.add(e["from"])
        if e["kind"] == "merge":
            changing.update(e["from"])
    for p in model["pins"]:
        t = p["target"]
        key = t.get("key")
        host = model["surfaces"][key]["host"] if key and key.startswith("sk") else key
        if host in changing:
            out.append(f"{p['source']['system']} {p['source']['ref']} on {p['addressSnapshot']}" + (f": {p['label']}" if p.get("label") else ""))
    return out


def revision_report(model: dict, rev: str) -> str:
    i = rev_index(model, rev)
    prev = model["revisions"][i - 1]["id"] if i > 0 else None
    lines = [f"# Revision report: {rev}" + (f" (after {prev})" if prev else ""), ""]
    ev = [e for e in model["lineage"] if e["rev"] == rev]
    counts = {k: sum(1 for e in ev if e["kind"] == k) for k in ("carry", "split", "merge", "retire")}
    lines.append("| carried | split | merged | retired |")
    lines.append("|---|---|---|---|")
    lines.append(f"| {counts['carry']} | {counts['split']} | {counts['merge']} | {counts['retire']} |")
    lines.append("")
    q = review_queue(model, rev)
    lines.append(f"## Pins to review ({len(q)})")
    for p in q:
        st = p["status"]
        words = {"forked": f"target split; pick one of {st.get('candidates')}",
                 "merged": f"target merged into {st.get('into')}; confirm",
                 "retired": f"target removed: {st.get('reason')}",
                 "span_invalid": f"wall is now {st.get('lengthNow')} ft; the span runs past the end",
                 "renamed": f"space renamed {st.get('spaceWas')} to {st.get('spaceNow')} ({st.get('was')} to {st.get('now')}); confirm the pin still fits",
                 "set_drift": f"members changed: {len(st.get('added', []))} added, {len(st.get('gone', []))} gone"}.get(st["status"], st["status"])
        lines.append(f"- {p['source']['system']} {p['source']['ref']} on {p['addressSnapshot']}: {words}")
    if not q:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def change_list(model: dict, rev_a: str, rev_b: str) -> dict:
    """
    Surfaces whose measured facts changed between two revisions. A surface that split,
    merged or carried to a new key is one row (before on the old side, after summed
    over its successors), so a change order reads "the bedroom's north wall went from
    16 ft to 10 ft plus 5.5 ft", never "a wall vanished and two appeared".
    """
    ia, ib = rev_index(model, rev_a), rev_index(model, rev_b)

    def live(k: str, i: int) -> dict | None:
        meta = model["surfaces"][k]
        if rev_index(model, meta["mintedIn"]) > i:
            return None
        if meta["retiredIn"] and rev_index(model, meta["retiredIn"]) <= i:
            return None
        return surface_at(model, k, model["revisions"][i]["id"])

    # successor links from the lineage between the two revisions
    links: list[tuple[str, str]] = []
    for e in model["lineage"]:
        if not (ia < rev_index(model, e["rev"]) <= ib):
            continue
        if e["kind"] == "carry" and e["from"] != e["to"] and e["from"].startswith("sk"):
            links.append((e["from"], e["to"]))
        elif e["kind"] == "split" and e["from"].startswith("sk"):
            links.extend((e["from"], t) for t in e["to"])
        elif e["kind"] == "merge" and e["to"].startswith("sk"):
            links.extend((f, e["to"]) for f in e["from"])
    parent: dict[str, str] = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for f, t in links:
        parent[find(f)] = find(t)

    # which old spaces were hosts with no faces (a room the set had not laid out yet)
    unlaid = {s["space"] for s in model["spaceRevs"] if rev_index(model, s["rev"]) <= ia and s["kind"] == "host"}

    groups: dict[str, dict] = {}
    for k in sorted(model["surfaces"], key=lambda x: int(x.split("_")[1])):
        before, after = live(k, ia), live(k, ib)
        if not before and not after:
            continue
        g = groups.setdefault(find(k), {"before": [], "after": []})
        if before:
            g["before"].append(before)
        if after:
            g["after"].append(after)

    rows = []
    for g in groups.values():
        bs, as_ = g["before"], g["after"]
        lb, la = _sum_len(bs), _sum_len(as_)
        ab, aa = _sum_area(bs), _sum_area(as_)
        addr_b = ", ".join(s["address"] for s in bs)
        addr_a = ", ".join(s["address"] for s in as_)
        if bs and as_ and lb == la and ab == aa and addr_b == addr_a:
            continue
        if not bs:
            host = model["surfaces"][as_[0]["surface"]]["host"]
            change = "now measured" if host in unlaid else "added"
        elif not as_:
            change = "removed"
        else:
            change = "changed"
        kind = (as_ or bs)[0]["kind"]
        rows.append({"keys": [s["surface"] for s in bs + as_], "kind": kind,
                     "before": addr_b or None, "after": addr_a or None,
                     "lengthBefore": lb, "lengthAfter": la, "areaBefore": ab, "areaAfter": aa,
                     "deltaLengthFt": _delta(lb, la) if change != "now measured" else None,
                     "deltaAreaSf": _delta(ab, aa) if change != "now measured" else None,
                     "sources": sorted({src for s in bs + as_ for src in [((s.get("lengthFt") or {}).get("source"))] if src}),
                     "change": change,
                     "note": ("split" if len(as_) > 1 and len(bs) == 1 else "merged" if len(bs) > 1 and len(as_) == 1 else None)})
    order = {"changed": 0, "removed": 1, "added": 2, "now measured": 3}
    rows.sort(key=lambda r: (order[r["change"]], r["before"] or r["after"]))
    events = [e for e in model["lineage"] if _space_event_between(model, e, ia, ib)]
    space_rows = _space_fact_changes(model, rev_a, rev_b)
    return {"from": rev_a, "to": rev_b, "surfaces": rows, "events": events, "spaces": space_rows,
            "totals": {"changed": sum(1 for r in rows if r["change"] == "changed"),
                       "added": sum(1 for r in rows if r["change"] == "added"),
                       "removed": sum(1 for r in rows if r["change"] == "removed"),
                       "nowMeasured": sum(1 for r in rows if r["change"] == "now measured"),
                       "spaceFacts": len(space_rows),
                       "deltaAreaSf": round(sum(r["deltaAreaSf"] or 0 for r in rows), 2)}}


SPACE_FACTS = (("elevationFt", "elevation", "ft"), ("spotFt", "spot height", "ft"), ("pitch", "pitch", ""))


def _effective(model: dict, row: dict, rev: str, field: str):
    """A space's own value, or for elevation the level's when the space has none."""
    v = (row.get(field) or {}).get("value")
    if v is None and field == "elevationFt":
        lv = (model["revisions"][rev_index(model, rev)].get("levels") or {}).get(row["level"]) or {}
        v = (lv.get("elevationFt") or {}).get("value")
    return v


def _space_fact_changes(model: dict, rev_a: str, rev_b: str) -> list[dict]:
    """Spaces live at both revisions under one key whose elevation, roof spot height or
    pitch changed. A garage slab that rose 2.5 ft is scope even when no wall length moved."""
    after = {s["space"]: s for s in live_spaces(model, rev_b)}
    rows = []
    for b in live_spaces(model, rev_a):
        a = after.get(b["space"])
        if not a:
            continue
        for field, label, unit in SPACE_FACTS:
            vb, va = _effective(model, b, rev_a, field), _effective(model, a, rev_b, field)
            if vb == va or (vb is None and va is None):
                continue
            num = isinstance(vb, (int, float)) and isinstance(va, (int, float))
            rows.append({"key": a["space"], "address": a["address"], "was": b["address"], "field": field, "label": label,
                         "unit": unit, "before": vb, "after": va, "delta": round(va - vb, 3) if num else None,
                         "source": (a.get(field) or {}).get("source")})
    rows.sort(key=lambda r: (r["address"], r["field"]))
    return rows


def _space_event_between(model: dict, e: dict, ia: int, ib: int) -> bool:
    """A split, merge or retire of a space, in the revisions after a and up to b."""
    if not (ia < rev_index(model, e["rev"]) <= ib) or e["kind"] == "carry":
        return False
    froms = e["from"] if isinstance(e["from"], list) else [e["from"]]
    return any(f.startswith("sp") for f in froms)


def _sum_len(rows):
    vals = [((r.get("lengthFt") or {}).get("value")) for r in rows]
    vals = [v for v in vals if v is not None]
    return round(sum(vals), 3) if vals else None


def _sum_area(rows):
    vals = [r.get("areaSf") for r in rows if r.get("areaSf") is not None]
    return round(sum(vals), 2) if vals else None


def _delta(a, b):
    if a is None and b is None:
        return None
    return round((b or 0) - (a or 0), 3)


def change_list_md(model: dict, cl: dict, rates: dict | None = None) -> str:
    """Markdown change list. `rates` maps system:ref to {rate, unit} when the job has an estimate."""
    t = cl["totals"]
    lines = [f"# Change list: {cl['from']} to {cl['to']}", "",
             f"{t['changed']} surfaces changed, {t['added']} added, {t['removed']} removed"
             + (f", {t['nowMeasured']} measured for the first time" if t.get("nowMeasured") else "")
             + (f", {t['spaceFacts']} elevation, spot height or pitch changes" if t.get("spaceFacts") else "")
             + f". Net area {t['deltaAreaSf']:+.2f} SF on the surfaces that changed.", "",
             "| Surface | Was | Now | Length | Area | Pricing |", "|---|---|---|---|---|---|"]
    for r in cl["surfaces"]:
        name = (r["before"] or r["after"]).split(",")[0].strip()
        spoken = A.speak(name)
        if r["note"]:
            spoken += f" ({r['note']})"
        if r["change"] == "now measured":
            spoken += " (first outline)"
        ln = _pair(r["lengthBefore"], r["lengthAfter"], "ft")
        ar = _pair(r["areaBefore"], r["areaAfter"], "SF")
        price = _pricing(model, r, rates)
        lines.append(f"| {spoken} | {r['before'] or ''} | {r['after'] or ''} | {ln} | {ar} | {price} |")
    lines.append("")
    if cl.get("spaces"):
        lines.append("## Levels, roof heights and pitch")
        lines.append("| Space | Fact | Was | Now | Change |")
        lines.append("|---|---|---|---|---|")
        for r in cl["spaces"]:
            u = f" {r['unit']}" if r["unit"] else ""
            ch = f"{r['delta']:+g}{u}" if r["delta"] is not None else ""
            lines.append(f"| {r['address']} | {r['label']} | {_fact(r['before'], u)} | {_fact(r['after'], u)} | {ch} |")
        lines.append("")
    if cl["events"]:
        lines.append("## What happened")
        for e in cl["events"]:
            if e["kind"] == "split":
                lines.append(f"- {_addr(model, e['from'])} split into {', '.join(_addr(model, k) for k in e['to'])}")
            elif e["kind"] == "merge":
                lines.append(f"- {', '.join(_addr(model, k) for k in e['from'])} merged into {_addr(model, e['to'])}")
            elif e["kind"] == "retire":
                lines.append(f"- {_addr(model, e['from'])} removed: {e.get('reason','')}")
        lines.append("")
    return "\n".join(lines)


def _fact(v, unit: str) -> str:
    return "not given" if v is None else f"{v:g}{unit}" if isinstance(v, (int, float)) else f"{v}"


def _addr(model: dict, key: str) -> str:
    table, field = ("spaceRevs", "space") if key.startswith("sp") else ("surfaceRevs", "surface")
    rows = [r for r in model[table] if r[field] == key]
    return rows[-1]["address"] if rows else key


def _pair(a, b, unit):
    if a is None and b is None:
        return "not measured"
    fa = "" if a is None else f"{a:g}"
    fb = "" if b is None else f"{b:g}"
    if a is not None and b is not None:
        return f"{fa} to {fb} {unit} ({b - a:+g})"
    return f"{fa}{fb} {unit}"


def _pricing(model: dict, r: dict, rates: dict | None) -> str:
    """A rate from a pinned estimate line, when one covers this surface; else needs pricing."""
    if not rates:
        return "needs pricing"
    keys = set(r["keys"])
    found = []
    for p in model["pins"]:
        t = p["target"]
        hit = t.get("key") in keys or (t["kind"] == "set" and keys & set(t.get("members", [])))
        if hit:
            rk = f"{p['source']['system']}:{p['source']['ref']}"
            if rk in rates:
                rt = rates[rk]
                d = r["deltaAreaSf"] if rt.get("unit", "SF") == "SF" else r["deltaLengthFt"]
                if d is not None:
                    found.append(f"{p['source']['ref']} at {rt['rate']:.2f}/{rt.get('unit','SF')}: {d * rt['rate']:+,.2f}")
    return "; ".join(found) if found else "needs pricing"
