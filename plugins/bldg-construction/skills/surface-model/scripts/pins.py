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
  renamed       the key is live under a new space name on the same outline; a person
                confirms the pin still fits (a bath that became a kitchen)
  moved         a person moved the pin to another address (state "moved")
  withdrawn     a person withdrew the pin (state "withdrawn")
"""
from __future__ import annotations

import address as A
from store import (address_map, current_rev, is_live, live_spaces, live_surfaces,
                   now, rev_index, space_at, surface_at)

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
    # a person's decision beats anything derived, from the revision it was made in
    if p.get("state") == "moved" and _reached(model, p.get("movedRev"), rev):
        return {"status": "moved", "to": p.get("movedTo"), "rev": p.get("movedRev")}
    if p.get("state") == "withdrawn" and _reached(model, p.get("withdrawnRev"), rev):
        return {"status": "withdrawn", "rev": p.get("withdrawnRev")}
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
        renamed = _renamed(model, p, key, rev)
        if renamed:
            return {"status": "renamed", "was": p["addressSnapshot"], "now": now_addr, "spaceWas": renamed[0], "spaceNow": renamed[1]}
        return {"status": "readdressed", "was": p["addressSnapshot"], "now": now_addr}
    return {"status": "exact"}


def _reached(model: dict, decided_rev: str | None, rev: str) -> bool:
    """True when `rev` is the revision a person decided in, or later. No revision: always."""
    return decided_rev is None or rev_index(model, rev) >= rev_index(model, decided_rev)


def _renamed(model: dict, p: dict, key: str, rev: str) -> tuple[str, str] | None:
    """(old name, new name) when the pin's space changed name, not just number or face.
    Compares the printed names; with none, the handles, unless both are plain numbers.
    A person who accepted the pin at or after `rev` has already looked at it."""
    if p.get("state") == "accepted" and p.get("acceptedRev") and rev_index(model, p["acceptedRev"]) >= rev_index(model, rev):
        return None
    host = model["surfaces"][key]["host"] if key.startswith("sk") else key
    old, new = space_at(model, host, p["pinnedAt"]), space_at(model, host, rev)
    if not old or not new:
        return None
    nm = lambda s: ((s.get("name") or {}).get("value") or "").strip().upper()  # noqa: E731
    if nm(old) and nm(new):
        return (nm(old), nm(new)) if nm(old) != nm(new) else None
    handle = lambda s: s["address"].split("/")[1] if s["address"].count("/") >= 1 else s["address"]  # noqa: E731
    ho, hn = handle(old), handle(new)
    if ho != hn and not (ho.isdigit() and hn.isdigit()):
        return (ho, hn)
    return None


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


def ancestors(model: dict, key: str) -> set[str]:
    """This key and every key that carried, split or merged into it."""
    out = {key}
    frontier = [key]
    while frontier:
        k = frontier.pop()
        for e in model["lineage"]:
            tos = e.get("to")
            if tos is None or e["kind"] == "retire":
                continue
            if k == tos or (isinstance(tos, list) and k in tos):
                froms = e["from"] if isinstance(e["from"], list) else [e["from"]]
                for f in froms:
                    if f not in out:
                        out.add(f)
                        frontier.append(f)
    return out


def what_touches(model: dict, key: str, rev: str) -> list[dict]:
    """Every pin on this key, its host, its wall, or a set that holds it, with status.
    A pin made on a key that later carried, split or merged into this one counts too."""
    keys = ancestors(model, key)
    if key.startswith("sk"):
        host = model["surfaces"][key]["host"]
        keys |= ancestors(model, host)
        wall = model["surfaces"][key].get("wall")
        if wall:
            keys.add(wall)
    out = []
    for p in model["pins"]:
        t = p["target"]
        hit = t.get("key") in keys or (t["kind"] == "set" and bool(keys & set(t.get("members", []))))
        if not hit and t["kind"] == "set":
            hit = key in resolve(model, t["query"], rev)["keys"]
        if not hit and p.get("state") == "moved" and p.get("movedTo"):
            hit = key in resolve(model, p["movedTo"], rev)["keys"]
        if hit:
            out.append({**p, "status": status(model, p, rev)})
    return out


def review_queue(model: dict, rev: str) -> list[dict]:
    out = []
    for p in model["pins"]:
        st = status(model, p, rev)
        if st["status"] not in ("exact", "readdressed", "moved", "withdrawn"):
            out.append({**p, "status": st})
    return out


def decide(model: dict, pin_id: str, action: str, by: dict, to: str | None = None) -> dict:
    """
    A person decides on a pin. Writes the fields a hand edit used to:
      accept    state accepted, acceptedBy, acceptedAt, acceptedRev
      withdraw  state withdrawn, withdrawnBy, withdrawnAt, withdrawnRev
      move      state moved, movedTo (an address), movedBy, movedAt, movedRev
    The target, source and address snapshot stay as they were; the pin is never deleted.
    """
    rev = current_rev(model)
    p = next((x for x in model["pins"] if x["id"] == pin_id), None)
    if p is None:
        raise SystemExit(f"{pin_id} is not a pin in this model")
    if action == "accept":
        p.update({"state": "accepted", "acceptedBy": by, "acceptedAt": now(), "acceptedRev": rev})
    elif action == "withdraw":
        p.update({"state": "withdrawn", "withdrawnBy": by, "withdrawnAt": now(), "withdrawnRev": rev})
    elif action == "move":
        if not to:
            raise SystemExit("move needs --to <address>")
        res = resolve(model, to, rev)
        if not res["keys"]:
            raise SystemExit(f"{to} resolves to nothing at {rev}")
        p.update({"state": "moved", "movedTo": A.parse(to).canonical(), "movedBy": by, "movedAt": now(), "movedRev": rev})
    else:
        raise SystemExit(f"unknown pin action {action!r}")
    return p
