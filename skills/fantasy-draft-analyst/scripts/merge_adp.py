#!/usr/bin/env python3
"""
merge_adp.py — reprice players.csv with a platform's ADP (ESPN, Yahoo, Sleeper, CBS…) while keeping
the projections and the ADP spread.

Why: the room you draft in follows its platform's rankings. The projections don't change; the prices do.

Usage:
  python3 merge_adp.py --players players.csv --adp adp_espn.csv --out players_espn.csv [--sd-scale 1.0]

adp file columns: name, adp (others ignored). Unmatched players keep their existing ADP and are listed
so you can fix name mismatches (e.g. "Kyle Pitts Sr." vs "Kyle Pitts").
"""
from __future__ import annotations

import argparse
import csv
import re


def norm(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"\b(jr|sr|ii|iii|iv)\b\.?", "", s)
    s = s.replace("d/st", "defense").replace("dst", "defense")
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--players", required=True)
    ap.add_argument("--adp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sd-scale", type=float, default=1.0, help="multiply existing adp_sd by this (platform rooms are often tighter: 0.8)")
    args = ap.parse_args()

    platform = {}
    with open(args.adp, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("name") and r.get("adp") not in (None, ""):
                try:
                    platform[norm(r["name"])] = float(r["adp"])
                except ValueError:
                    pass

    rows, matched, unmatched = [], 0, []
    with open(args.players, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        for r in reader:
            key = norm(r["name"])
            if key in platform:
                r["adp"] = platform[key]
                matched += 1
                if r.get("adp_sd"):
                    r["adp_sd"] = round(float(r["adp_sd"]) * args.sd_scale, 1)
            else:
                unmatched.append(r["name"])
            rows.append(r)
    rows.sort(key=lambda x: float(x["adp"]))
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"Repriced {matched} of {len(rows)} players from {args.adp}; wrote {args.out}")
    if unmatched:
        deep = [n for n in unmatched]
        print(f"{len(unmatched)} kept their previous ADP (not in the platform file): " + ", ".join(deep[:12]) + (" …" if len(deep) > 12 else ""))
        print("There % beyond the platform file's depth mixes two ADP sources — say so in the appendix.")


if __name__ == "__main__":
    main()
