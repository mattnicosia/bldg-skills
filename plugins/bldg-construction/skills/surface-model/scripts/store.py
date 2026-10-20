"""
store.py -- the job's surface model file.

One JSON file per job, `surface-model.json`, beside drawing-index's `index.json`. Three
things carry identity (space, wall, surface). Keys are minted once, never reused, never
deleted. Per-revision facts sit in `spaceRevs` and `surfaceRevs`. `lineage` and `pins`
are append-only. Pin status is never stored; `pins.py` derives it.

The file is small for a house and fine for a few hundred rooms. Past that, the same rows
move to SQLite, the way drawing-index's README says for index.json.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

SCHEMA_VERSION = "1.0"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_model(job: str) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "job": job,
        "north": None,
        "wallTolFt": 1.0,
        "revisions": [],
        "spaces": {},
        "walls": {},
        "surfaces": {},
        "spaceRevs": [],
        "surfaceRevs": [],
        "lineage": [],
        "pins": [],
        "rejectedPairs": [],
        "counters": {"sp": 0, "wk": 0, "sk": 0, "pin": 0},
    }


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        m = json.load(f)
    if m.get("schema_version") != SCHEMA_VERSION:
        raise SystemExit(f"{path}: schema {m.get('schema_version')} is not {SCHEMA_VERSION}")
    return m


def save(model: dict, path: str) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(model, f, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# keys
# ---------------------------------------------------------------------------
def mint(model: dict, prefix: str, rev: str, **attrs) -> str:
    model["counters"][prefix] += 1
    key = f"{prefix}_{model['counters'][prefix]}"
    table = {"sp": "spaces", "wk": "walls", "sk": "surfaces"}[prefix]
    row = {"key": key, "job": model["job"], "mintedIn": rev, "retiredIn": None}
    row.update(attrs)
    model[table][key] = row
    return key


def retire(model: dict, key: str, rev: str) -> None:
    table = {"sp": "spaces", "wk": "walls", "sk": "surfaces"}[key[:2]]
    model[table][key]["retiredIn"] = rev


def is_live(model: dict, key: str, rev: str | None = None) -> bool:
    table = {"sp": "spaces", "wk": "walls", "sk": "surfaces"}[key[:2]]
    row = model[table].get(key)
    if row is None:
        return False
    if row["retiredIn"] is None:
        return True
    if rev is None:
        return False
    order = [r["id"] for r in model["revisions"]]
    return order.index(row["retiredIn"]) > order.index(rev)


# ---------------------------------------------------------------------------
# revisions and facts
# ---------------------------------------------------------------------------
def rev_index(model: dict, rev: str) -> int:
    for i, r in enumerate(model["revisions"]):
        if r["id"] == rev:
            return i
    raise KeyError(f"revision {rev!r} is not in the model")


def current_rev(model: dict) -> str | None:
    return model["revisions"][-1]["id"] if model["revisions"] else None


def facts_at(model: dict, table: str, key_field: str, key: str, rev: str) -> dict | None:
    """The latest row for this key at or before `rev`."""
    order = {r["id"]: i for i, r in enumerate(model["revisions"])}
    at = order[rev]
    best = None
    for row in model[table]:
        if row[key_field] != key:
            continue
        i = order[row["rev"]]
        if i <= at and (best is None or i > order[best["rev"]]):
            best = row
    return best


def space_at(model: dict, key: str, rev: str) -> dict | None:
    return facts_at(model, "spaceRevs", "space", key, rev)


def surface_at(model: dict, key: str, rev: str) -> dict | None:
    return facts_at(model, "surfaceRevs", "surface", key, rev)


def live_spaces(model: dict, rev: str) -> list[dict]:
    out = []
    for key in model["spaces"]:
        if is_live(model, key, rev) and rev_index(model, model["spaces"][key]["mintedIn"]) <= rev_index(model, rev):
            row = space_at(model, key, rev)
            if row:
                out.append(row)
    return out


def live_surfaces(model: dict, rev: str) -> list[dict]:
    out = []
    for key in model["surfaces"]:
        if is_live(model, key, rev) and rev_index(model, model["surfaces"][key]["mintedIn"]) <= rev_index(model, rev):
            row = surface_at(model, key, rev)
            if row:
                out.append(row)
    return out


def address_map(model: dict, rev: str) -> dict[str, str]:
    """canonical address -> key, for spaces and surfaces live at rev."""
    out = {}
    for s in live_spaces(model, rev):
        out[s["address"]] = s["space"]
    for s in live_surfaces(model, rev):
        out[s["address"]] = s["surface"]
    return out


def key_for_address(model: dict, address: str, rev: str) -> str | None:
    return address_map(model, rev).get(address)
