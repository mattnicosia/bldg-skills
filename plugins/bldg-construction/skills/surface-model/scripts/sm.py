#!/usr/bin/env python3
"""
sm.py -- the surface model command line.

  sm.py init      <model.json> --job E26049
  sm.py build     <model.json> <readings.json> --rev SD-1 [--accept-pairs by]
  sm.py propose   <model.json> <readings.json> --rev DD-1 --out proposal.json
  sm.py accept    <model.json> proposal.json --by matt [--all | --decide 3,5,7] [--accept-pairs by]
  sm.py resolve   <model.json> "L1/*/FLR" [--rev SD-1]
  sm.py pin       <model.json> "L1/GREAT/N" --system estimate --ref "08 54 00" --by matt [--label ..]
  sm.py touches   <model.json> "L1/GREAT/N" [--rev DD-1]
  sm.py review    <model.json> [--rev DD-1]
  sm.py changes   <model.json> --from SD-1 --to DD-1 [--md out.md] [--rates rates.json]
  sm.py export    <model.json> --what surfaces|massing --out file.json [--rev DD-1]
  sm.py report    <model.json> [--rev DD-1]
  sm.py speak     "L2/204/N/W3 @6-12"
  sm.py summary   <model.json>

Every command reads and writes one JSON file. Run with `python3 -I`.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import address as A  # noqa: E402
import build as B  # noqa: E402
import export as X  # noqa: E402
import pins as P  # noqa: E402
import report as R  # noqa: E402
import revise as V  # noqa: E402
import store as S  # noqa: E402


def actor(text: str | None, kind: str = "person") -> dict | None:
    if not text:
        return None
    if ":" in text:
        k, i = text.split(":", 1)
        return {"kind": k, "id": i}
    return {"kind": kind, "id": text}


def jload(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def out(obj, path: str | None = None, md: str | None = None):
    if path:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=1, ensure_ascii=False)
        print(f"wrote {path}")
    elif md is None:
        print(json.dumps(obj, indent=1, ensure_ascii=False))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="sm.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init"); p.add_argument("model"); p.add_argument("--job", required=True)
    p = sub.add_parser("build"); p.add_argument("model"); p.add_argument("readings"); p.add_argument("--rev", required=True); p.add_argument("--accept-pairs")
    p = sub.add_parser("propose"); p.add_argument("model"); p.add_argument("readings"); p.add_argument("--rev", required=True); p.add_argument("--out", required=True)
    p = sub.add_parser("accept"); p.add_argument("model"); p.add_argument("proposal"); p.add_argument("--by", required=True); p.add_argument("--all", action="store_true"); p.add_argument("--decide"); p.add_argument("--accept-pairs")
    p = sub.add_parser("resolve"); p.add_argument("model"); p.add_argument("query"); p.add_argument("--rev")
    p = sub.add_parser("pin"); p.add_argument("model"); p.add_argument("target"); p.add_argument("--system", required=True); p.add_argument("--ref", required=True); p.add_argument("--by", required=True); p.add_argument("--label"); p.add_argument("--state", default="proposed"); p.add_argument("--evidence", action="append")
    p = sub.add_parser("touches"); p.add_argument("model"); p.add_argument("address"); p.add_argument("--rev")
    p = sub.add_parser("review"); p.add_argument("model"); p.add_argument("--rev")
    p = sub.add_parser("changes"); p.add_argument("model"); p.add_argument("--from", dest="rev_a", required=True); p.add_argument("--to", dest="rev_b", required=True); p.add_argument("--md"); p.add_argument("--rates"); p.add_argument("--out")
    p = sub.add_parser("export"); p.add_argument("model"); p.add_argument("--what", choices=["surfaces", "massing"], required=True); p.add_argument("--out", required=True); p.add_argument("--rev")
    p = sub.add_parser("report"); p.add_argument("model"); p.add_argument("--rev"); p.add_argument("--proposal")
    p = sub.add_parser("speak"); p.add_argument("address")
    p = sub.add_parser("summary"); p.add_argument("model")

    a = ap.parse_args(argv)

    if a.cmd == "speak":
        print(A.parse(a.address).canonical())
        print(A.speak(a.address))
        return 0

    if a.cmd == "init":
        if os.path.exists(a.model):
            sys.exit(f"{a.model} exists; refusing to overwrite")
        S.save(S.new_model(a.job), a.model)
        print(f"wrote {a.model}")
        return 0

    m = S.load(a.model)
    rev = getattr(a, "rev", None) or S.current_rev(m)

    if a.cmd == "build":
        res = B.first_build(m, jload(a.readings), a.rev, actor(a.accept_pairs))
        if not res["ok"]:
            print("refused:"); [print(" -", x) for x in res["problems"]]; return 2
        S.save(m, a.model)
        print(f"{a.rev}: {res['spaces']} spaces, {res['surfaces']} surfaces, {res['pairsProposed']} wall pairs proposed, {res['pairsAccepted']} accepted")
        if res["pairs"] and not res["pairsAccepted"]:
            for p in res["pairs"]:
                print(f"   pair {p['a']} | {p['b']}  {p['lengthFt']} ft")
            print("   confirm with --accept-pairs <who>")
        return 0

    if a.cmd == "propose":
        res = V.propose(m, jload(a.readings), a.rev)
        if "problems" in res and not res.get("events"):
            print("refused:"); [print(" -", x) for x in res["problems"]]; return 2
        keep = {k: v for k, v in res.items() if not k.startswith("_")}
        keep["_cand"] = res["_cand"]; keep["_readings"] = res["_readings"]
        out(keep, a.out)
        print(R.proposal_report(m, res))
        return 0 if res["ok"] else 3

    if a.cmd == "accept":
        prop = jload(a.proposal)
        if a.decide:
            prop["decisions"] = [int(x) for x in a.decide.split(",") if x.strip()]
        res = V.accept(m, prop, actor(a.by), a.all, actor(a.accept_pairs))
        if not res["ok"]:
            print("refused:"); [print(" -", x) for x in res["problems"]]; return 2
        S.save(m, a.model)
        print(f"{res['rev']}: {res['counts']}  {res['pairsAccepted']}/{res['pairsProposed']} wall pairs accepted")
        print(R.revision_report(m, res["rev"]))
        return 0

    if a.cmd == "resolve":
        out(P.resolve(m, a.query, rev))
        return 0

    if a.cmd == "pin":
        p = P.pin(m, a.target, a.system, a.ref, actor(a.by), a.label, a.state, a.evidence)
        S.save(m, a.model)
        print(f"{p['id']}: {p['source']['system']} {p['source']['ref']} -> {p['addressSnapshot']} ({p['target']['kind']}, {len(p['target'].get('members', [p['target'].get('key')]))} keys)")
        return 0

    if a.cmd == "touches":
        key = S.key_for_address(m, A.parse(a.address).surface_key_text(), rev)
        if not key:
            sys.exit(f"{a.address} is not live at {rev}")
        for p in P.what_touches(m, key, rev):
            print(f"{p['id']:8} {p['source']['system']:12} {p['source']['ref']:14} {p['status']['status']:12} {p.get('label') or ''}")
        return 0

    if a.cmd == "review":
        q = P.review_queue(m, rev)
        for p in q:
            print(f"{p['id']:8} {p['source']['system']:12} {p['source']['ref']:14} {p['status']['status']:12} was {p['addressSnapshot']}")
        print(f"{len(q)} pins need a person at {rev}")
        return 0

    if a.cmd == "changes":
        cl = R.change_list(m, a.rev_a, a.rev_b)
        rates = jload(a.rates) if a.rates else None
        if a.out:
            out(cl, a.out)
        md = R.change_list_md(m, cl, rates)
        if a.md:
            with open(a.md, "w", encoding="utf-8") as f:
                f.write(md)
            print(f"wrote {a.md}")
        else:
            print(md)
        return 0

    if a.cmd == "export":
        data = X.surfaces_export(m, rev) if a.what == "surfaces" else X.massing_export(m, rev)
        out(data, a.out)
        return 0

    if a.cmd == "report":
        if a.proposal:
            print(R.proposal_report(m, jload(a.proposal)))
        else:
            print(R.revision_report(m, rev))
        return 0

    if a.cmd == "summary":
        print(f"job {m['job']}  revisions {[r['id'] for r in m['revisions']]}")
        for r in m["revisions"]:
            sp = S.live_spaces(m, r["id"]); sf = S.live_surfaces(m, r["id"])
            meas = sum(1 for s in sf if s.get("areaSf") is not None)
            print(f"  {r['id']:8} {len(sp):3} spaces  {len(sf):3} surfaces  {meas:3} with area  pins {sum(1 for p in m['pins'] if S.rev_index(m, p['pinnedAt']) <= S.rev_index(m, r['id']))}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
