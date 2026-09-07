#!/usr/bin/env python3
"""
scoring.py — turn raw stat-line projections into points in YOUR league's scoring,
and merge them with ADP into the players.csv the simulator reads.

Why this exists: no vendor's point total is right for your league unless the scoring matches.
A −2 INT, 4-point-passing-TD league reorders the quarterbacks; TE premium reorders the tight ends.

Usage:
  python3 scoring.py --league league.yaml --stats stats.csv --adp adp.csv --out players.csv
  python3 scoring.py --league league.yaml --stats stats.csv --out players.csv     # ADP already in stats.csv

Legacy sparse stats.csv columns (missing fields assume zero; use prepare_data.py for strict evidence validation):
  name,pos,team,pass_yd,pass_td,int,rush_yd,rush_td,rec,rec_yd,rec_td,fum,two_pt,
  fg,fg_miss,xp,  (kickers)
  sacks,def_int,fum_rec,def_td,safety,pts_allowed,  (defenses — see DEF scoring below)
  adp,adp_sd,bye  (optional; or supply --adp)

adp.csv columns: name,adp[,adp_sd][,pos][,team]

Name matching is forgiving (case, punctuation, suffixes like Jr./III, and "D/ST" vs "Defense").
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path


def load_league(path: str) -> dict:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json":
        return json.loads(text)
    try:
        import yaml  # type: ignore
    except ImportError:
        sys.exit("PyYAML is required (pip install pyyaml), or pass league.json")
    return yaml.safe_load(text)


def norm_name(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"\b(jr|sr|ii|iii|iv)\b\.?", "", s)
    s = s.replace("d/st", "defense").replace("dst", "defense")
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def f(row: dict, key: str) -> float:
    v = row.get(key)
    if v in (None, "", "-", "—"):
        return 0.0
    try:
        result = float(str(v).replace(",", ""))
    except (ValueError, TypeError):
        raise ValueError(f"Malformed numeric stat {key}: {v!r}") from None
    if not math.isfinite(result):
        raise ValueError(f"Stat {key} must be finite")
    return result


def score_row(row: dict, sc: dict) -> float:
    pos = row.get("pos", "").upper()
    pts = 0.0
    pts += f(row, "pass_yd") * float(sc.get("pass_yard", 0.04))
    pts += f(row, "pass_td") * float(sc.get("pass_td", 4))
    pts += f(row, "int") * float(sc.get("interception", -2))
    pts += f(row, "rush_yd") * float(sc.get("rush_yard", 0.1))
    pts += f(row, "rush_td") * float(sc.get("rush_td", 6))
    rec_pts = float(sc.get("reception", 0.5))
    if pos == "TE":
        rec_pts += float(sc.get("te_premium", 0) or 0)
    pts += f(row, "rec") * rec_pts
    pts += f(row, "rec_yd") * float(sc.get("rec_yard", 0.1))
    pts += f(row, "rec_td") * float(sc.get("rec_td", 6))
    pts += f(row, "fum") * float(sc.get("fumble_lost", -2))
    pts += f(row, "two_pt") * float(sc.get("two_point", 2))
    # bonuses: [{stat: rec_yard, threshold: 100, points: 3}] are per-game bonuses; approximate
    # over a season as (season stat / 17 games) crossing the threshold on average is rare, so we
    # apply a soft expectation: points × max(0, min(1, (per_game − 0.7×threshold) / (0.6×threshold))) × 17
    for b in sc.get("bonuses") or []:
        stat = {"rec_yard": "rec_yd", "rush_yard": "rush_yd", "pass_yard": "pass_yd"}.get(b.get("stat"), b.get("stat"))
        per_game = f(row, stat) / 17.0
        th = float(b.get("threshold", 100))
        frac = max(0.0, min(1.0, (per_game - 0.7 * th) / (0.6 * th)))
        pts += frac * 17 * float(b.get("points", 0))
    # kickers
    if pos == "K":
        pts += f(row, "fg") * float(sc.get("fg", 3.3)) + f(row, "xp") * float(sc.get("xp", 1)) + f(row, "fg_miss") * float(sc.get("fg_miss", -1))
    # defenses: simple standard model unless league overrides
    if pos == "DEF":
        pts += f(row, "sacks") * float(sc.get("sack", 1)) + f(row, "def_int") * float(sc.get("def_int", 2))
        pts += f(row, "fum_rec") * float(sc.get("fum_rec", 2)) + f(row, "def_td") * float(sc.get("def_td", 6))
        pts += f(row, "safety") * float(sc.get("safety", 2))
        pa = f(row, "pts_allowed")
        if row.get("pts_allowed") not in (None, "", "-", "—"):
            # ESPN/Yahoo-style points-allowed buckets, per game, approximated over a season
            per_game = pa / 17.0
            bucket = 10 if per_game == 0 else 7 if per_game < 7 else 4 if per_game < 14 else 1 if per_game < 21 else 0 if per_game < 28 else -1 if per_game < 35 else -4
            pts += bucket * 17
    return round(pts, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--league", required=True)
    ap.add_argument("--stats", required=True)
    ap.add_argument("--adp", default=None)
    ap.add_argument("--out", default="players.csv")
    args = ap.parse_args()

    cfg = load_league(args.league)
    sc = cfg.get("scoring", {})

    adp = {}
    if args.adp:
        with open(args.adp, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("name"):
                    adp[norm_name(r["name"])] = r

    out_rows, unmatched = [], []
    with open(args.stats, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if not r.get("name"):
                continue
            pos = (r.get("pos") or "").upper().replace("D/ST", "DEF").replace("DST", "DEF")
            r["pos"] = pos
            pts = score_row(r, sc)
            a = r.get("adp") or ""
            sd = r.get("adp_sd") or ""
            team = r.get("team") or ""
            bye = r.get("bye") or ""
            if not a and adp:
                m = adp.get(norm_name(r["name"]))
                if m:
                    a = m.get("adp", "")
                    sd = m.get("adp_sd", "") or sd
                    team = team or m.get("team", "")
                    bye = bye or m.get("bye", "")
            if not a:
                unmatched.append(r["name"])
                continue
            out_rows.append({"name": r["name"].strip(), "pos": pos, "team": team, "adp": a, "adp_sd": sd,
                             "proj": pts, "bye": bye, "note": r.get("note", "")})

    out_rows.sort(key=lambda x: float(x["adp"]))
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["name", "pos", "team", "adp", "adp_sd", "proj", "bye", "note"])
        w.writeheader()
        w.writerows(out_rows)
    print(f"Wrote {len(out_rows)} players to {args.out} using scoring: "
          f"{sc.get('reception', 0.5)} PPR, {sc.get('pass_td', 4)}-pt pass TD, {sc.get('interception', -2)} INT"
          + (f", TE premium +{sc.get('te_premium')}" if sc.get('te_premium') else ""))
    if unmatched:
        print(f"{len(unmatched)} players had no ADP and were skipped (add them to adp.csv if they matter): "
              + ", ".join(unmatched[:15]) + (" …" if len(unmatched) > 15 else ""))


if __name__ == "__main__":
    main()
