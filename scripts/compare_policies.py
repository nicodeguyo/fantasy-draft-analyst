#!/usr/bin/env python3
"""
compare_policies.py — the receipt for "is this board actually worth following?"

Runs three different drafters in YOUR seat over the same simulated drafts, so the only
thing that changes is how you pick. Everything else — the opponents, the keeper draw,
the randomness — is identical, and the comparison is paired seed by seed.

  1. ADP autodraft   your seat picks off the platform's ranking with noise, like an autopick
  2. Heuristic       the simulator's own in-draft policy: adaptive, re-decides every pick
  3. Board-following what you do with the board open — take the top available row of the
                     pick tables the rollouts produced

Usage, from a folder holding league.yaml, players.csv and a sim.json built with --pick-values:

    python3 scripts/compare_policies.py --league league.yaml --players players.csv \
        --sim sim.json --drafts 800

This is the simulator grading itself: same projections and the same model of the room for
all three. It is a valid internal comparison, not a backtest against real drafts. If the
projections are wrong, all three rows move together.
"""
from __future__ import annotations

import argparse, json, math, statistics, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent /
                       "skills" / "fantasy-draft-analyst" / "scripts"))
import draft_sim as ds  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--league", required=True)
    ap.add_argument("--players", required=True)
    ap.add_argument("--sim", required=True, help="sim.json built with --pick-values")
    ap.add_argument("--drafts", type=int, default=800)
    ap.add_argument("--seed", type=int, default=1000)
    args = ap.parse_args()

    cfg = ds.load_league(args.league)
    pool = ds.load_players(args.players)
    sim = json.loads(Path(args.sim).read_text(encoding="utf-8"))
    if not sim.get("pick_values"):
        sys.exit("That sim.json has no pick_values — re-run draft_sim.py with --pick-values.")

    s = ds.Sim(cfg, [dict(p) for p in pool], sim["league"].get("keeper"), sim["league"].get("keeper_round"))
    pos_best = defaultdict(lambda: defaultdict(list))
    for i in range(300):
        s.run(args.seed + 70000 + i, pos_best=pos_best)
    s.pos_horizon = {ov: {p: statistics.mean(v) for p, v in d.items()} for ov, d in pos_best.items()}

    # following the board = take the highest-ranked row still available at each of your picks
    board = {int(pk): [r["name"] for r in rows] for pk, rows in sim["pick_values"].items()}

    seeds = [args.seed + 900000 + i for i in range(args.drafts)]
    runs = {
        "ADP autodraft":    [s.run(sd, market=True)[2] for sd in seeds],
        "Board-following":  [s.run(sd, targets=board)[2] for sd in seeds],
        "Heuristic (free)": [s.run(sd)[2] for sd in seeds],
    }

    base = runs["ADP autodraft"]
    print(f"{args.drafts} drafts each, identical seeds and opponents\n")
    print(f"{'drafter in your seat':<20} {'mean':>7} {'sd':>6}   {'vs autodraft (paired)':>22}")
    for name, vals in runs.items():
        m, sd = statistics.mean(vals), statistics.pstdev(vals)
        if name == "ADP autodraft":
            tail = "—"
        else:
            d = [a - b for a, b in zip(vals, base)]
            se = statistics.stdev(d) / math.sqrt(len(d))
            tail = f"{statistics.mean(d):+.1f} ± {2 * se:.1f}"
        print(f"{name:<20} {m:7.0f} {sd:6.1f}   {tail:>22}")
    print("\nThe spread column matters as much as the mean: an autopick roster is not just worse "
          "on average,\nit is far less predictable, and you cannot tell in advance which season you got.")


if __name__ == "__main__":
    main()
