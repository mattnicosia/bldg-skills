"""
pins.py -- links from outside things to keys, and whether they still hold.

A pin says an estimate line, an RFI, a CO, a SOW item, a selection or a field figure
touches a surface, a wall, a space, or a set picked by a selector. The pin stores the
key and a snapshot of the address and members at pin time. Whether the pin is still
right at a later revision is derived from the lineage log, never stored.

Status at a revision:
  exact         the key is live and its address is unchanged
  readdressed   the key is live under a new address (carry, readdressed)
  forked        the key split; a person picks which child
  merged        the key merged into a new one; a person confirms
  retired       the key is gone; drawn as a ghost on its last geometry
  span_invalid  the wall moved and the pin's span runs past the end
  set_drift     a selector pin's members changed
"""
from __future__ import annotations

import address as A
from store import (address_map, current_rev, is_live, live_spaces, live_surfaces,
                   now, space_at, surface_at)

SYSTEMS = ("estimate", "proest", "procore_rfi", "procore_co", "sow", "selection", "allowance", "field_figure", "note")


def resolve(model: dict, query: str, rev: str) -> dict:
    """A selector or an address -> keys live at rev, with area where measured."""
    q = A.parse(query)
    keys, area, unmeasured = [], 0.0, []
    for s in live_surfaces(model, rev):
        tags = [r.get("assembly", {}).get("value") if isinstance(r.get("assembly"), dict) else r.get("assembly") for r in s.get("runs", [])]
        if A.matches(q, s["address"], [t for t in tags if t]):
            keys.append(s["surface"])
            if s.get("areaSf") is None:
                unmeasured.append(s["surface"])
            else:
                area += s["areaSf"]
    if q.face is None and not q.core:
        for sp in live_spaces(model, rev):
            if A.matches(q, sp["address"]):
                keys.append(sp["space"])
                if sp.get("areaSf") is None:
                    unmeasured.append(sp["space"])
                else:
                    area += sp["areaSf"]
    if q.core and not q.is_selector:
        amap = address_map(model, rev)
        a = amap.get(f"{q.level}/{q.core[0]}")
        b = amap.get(f"{q.level}/{q.core[1]}")
        for s in live_surfaces(model, rev):
            if s["host"] == a and any(adj["opposite"] == b for adj in s.get("adjacency", [])):
                wk = model["surfaces"][s["surface"]].get("wall")
                if wk and wk not in keys:
                    keys.append(wk)
    return {"query": q.canonical(), "keys": keys, "areaSf": round(area, 2) if keys else None, "unmeasured": unmeasured}


def pin(model: dict, target: str, system: str, ref: str, by: dict, label: str | None = None,
        state: str = "proposed", evidence: list[str] | None = None) -> dict:
    """Idempotent on (system, ref, target, rev)."""
    rev = current_rev(model)
    if system not in SYSTEMS:
        raise SystemExit(f"system {system!r} is not one of {SYSTEMS}")
    q = A.parse(target)
    res = resolve(model, target, rev)
    if not res["keys"]:
        raise SystemExit(f"{target} resolves to nothing at {rev}")
    if q.is_selector or "," in target:
        tgt = {"kind": "set", "query": q.canonical(), "members": res["keys"]}
    elif q.core:
        tgt = {"kind": "wall", "key": res["keys"][0]}
    elif q.face is None:
        tgt = {"kind": "space", "key": res["keys"][0]}
    else:
        tgt = {"kind": "surface", "key": res["keys"][0]}
        if q.span:
            tgt["span"] = list(q.span)
        if q.point:
            tgt["point"] = list(q.point)
    for p in model["pins"]:
        if p["source"] == {"system": system, "ref": ref} and p["target"] == tgt and p["pinnedAt"] == rev:
            return p
    model["counters"]["pin"] += 1
    p = {"id": f"pin_{model['counters']['pin']}", "target": tgt, "source": {"system": system, "ref": ref},
         "label": label, "pinnedAt": rev, "addressSnapshot": q.canonical(), "by": by, "state": state,
         "evidence": evidence or [], "at": now()}
    model["pins"].append(p)
    return p


def status(model: dict, p: dict, rev: str) -> dict:
    t = p["target"]
    if t["kind"] == "set":
        res = resolve(model, t["query"], rev)
        added = [k for k in res["keys"] if k not in t["members"]]
        gone = [k for k in t["members"] if k not in res["keys"]]
        if added or gone:
            return {"status": "set_drift", "added": added, "gone": gone, "membersNow": res["keys"]}
        return {"status": "exact"}
    key = t["key"]
    ev = _events_after(model, key, p["pinnedAt"], rev)
    for e in ev:
        if e["kind"] == "split" and e["from"] == key:
            return {"status": "forked", "candidates": e["to"]}
        if e["kind"] == "merge" and key in e["from"]:
            return {"status": "merged", "into": e["to"]}
        if e["kind"] == "retire" and e["from"] == key:
            last = surface_at(model, key, p["pinnedAt"]) if key.startswith("sk") else space_at(model, key, p["pinnedAt"])
            return {"status": "retired", "reason": e["reason"], "lastGeometry": last}
        if e["kind"] == "carry" and e["from"] == key and e["to"] != key:
            # a face that carried to a new key after a split or merge of its host
            return {"status": "readdressed", "was": p["addressSnapshot"], "now": _address(model, e["to"], rev), "key": e["to"]}
    if not is_live(model, key, rev):
        return {"status": "retired", "reason": "key not live", "lastGeometry": None}
    now_addr = _address(model, key, rev)
    if t["kind"] == "surface" and t.get("span"):
        s = surface_at(model, key, rev)
        length = (s or {}).get("lengthFt") or {}
        if length.get("value") is not None and t["span"][1] > float(length["value"]) + 1e-6:
            return {"status": "span_invalid", "lengthNow": length["value"]}
    if now_addr and now_addr != _strip(p["addressSnapshot"]):
        return {"status": "readdressed", "was": p["addressSnapshot"], "now": now_addr}
    return {"status": "exact"}


def _strip(addr: str) -> str:
    a = A.parse(addr)
    return a.surface_key_text()


def _address(model: dict, key: str, rev: str) -> str | None:
    if key.startswith("sk"):
        s = surface_at(model, key, rev)
    elif key.startswith("sp"):
        s = space_at(model, key, rev)
    else:
        return None
    return s["address"] if s else None


def _events_after(model: dict, key: str, pinned_at: str, rev: str) -> list[dict]:
    order = {r["id"]: i for i, r in enumerate(model["revisions"])}
    lo, hi = order[pinned_at], order[rev]
    out = []
    for e in model["lineage"]:
        i = order[e["rev"]]
        if lo < i <= hi and (e.get("from") == key or (isinstance(e.get("from"), list) and key in e["from"])):
            out.append(e)
    return out


def what_touches(model: dict, key: str, rev: str) -> list[dict]:
    """Every pin on this key, its host, its wall, or a set that holds it, with status."""
    host = model["surfaces"][key]["host"] if key.startswith("sk") else None
    wall = model["surfaces"][key].get("wall") if key.startswith("sk") else None
    out = []
    for p in model["pins"]:
        t = p["target"]
        hit = (t.get("key") == key or (host and t.get("key") == host) or (wall and t.get("key") == wall)
               or (t["kind"] == "set" and key in t.get("members", [])))
        if not hit and t["kind"] == "set":
            hit = key in resolve(model, t["query"], rev)["keys"]
        if hit:
            out.append({**p, "status": status(model, p, rev)})
    return out


def review_queue(model: dict, rev: str) -> list[dict]:
    out = []
    for p in model["pins"]:
        st = status(model, p, rev)
        if st["status"] not in ("exact", "readdressed"):
            out.append({**p, "status": st})
    return out
