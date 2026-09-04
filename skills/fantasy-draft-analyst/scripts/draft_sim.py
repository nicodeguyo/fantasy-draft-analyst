#!/usr/bin/env python3
"""
draft_sim.py — Monte Carlo draft simulator for any league.

Reads league.yaml and players.csv, then:
  * builds your pick ladder (snake, with keeper-forfeited rounds removed)
  * derives replacement level per position from the starting lineup
  * evaluates every keeper candidate in points of surplus vs. the pick it costs
  * simulates the draft N times (keepers removed, ADP-noise opponents, lineup-aware you)
  * reports who is on the board at each of your picks ("There %"), sample drafts,
    the most-owned players, and the projected starter-point range

Usage:
  python3 draft_sim.py --league league.yaml --players players.csv --sims 1500 --out sim.json
  python3 draft_sim.py --league league.yaml --players players.csv --keeper "Chase Brown"

Only dependency beyond the standard library is PyYAML (pip install pyyaml). A league.json works too.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

SKILL_POS = ("RB", "WR", "TE")
QB_POS = ("QB",)
LATE_POS = ("K", "DEF")


# ----------------------------------------------------------------------------
# Config loading
# ----------------------------------------------------------------------------

def load_league(path: str) -> dict:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json":
        return json.loads(text)
    try:
        import yaml  # type: ignore
    except ImportError:
        sys.exit("PyYAML is required to read league.yaml (pip install pyyaml), or pass a league.json instead.")
    return yaml.safe_load(text)


def load_players(path: str) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if not r.get("name"):
                continue
            pos = r["pos"].strip().upper()
            if pos in ("DST", "D/ST", "D"):
                pos = "DEF"
            if pos == "PK":
                pos = "K"
            adp = float(r["adp"])
            sd = r.get("adp_sd")
            sd = float(sd) if sd not in (None, "", "nan") else max(4.0, 0.08 * adp)
            rows.append({
                "name": r["name"].strip(),
                "pos": pos,
                "team": (r.get("team") or "").strip(),
                "adp": adp,
                "sd": sd,
                "proj": float(r["proj"]),
                "bye": r.get("bye", ""),
                "note": r.get("note", ""),
            })
    if not rows:
        sys.exit("players.csv is empty")
    return rows


# ----------------------------------------------------------------------------
# League structure
# ----------------------------------------------------------------------------

def starters(cfg: dict) -> dict:
    r = cfg.get("roster", {})
    return {
        "QB": int(r.get("QB", 1)), "RB": int(r.get("RB", 2)), "WR": int(r.get("WR", 2)),
        "TE": int(r.get("TE", 1)), "K": int(r.get("K", 1)), "DEF": int(r.get("DEF", 1)),
        "FLEX": int(r.get("FLEX", 1)), "SUPERFLEX": int(r.get("SUPERFLEX", 0)),
    }


def round_half_up(x: float) -> int:
    """Round .5 up (10 × 0.85 = 8.5 → 9). Python's round() is banker's rounding and would give 8."""
    return int(math.floor(x + 0.5))


def replacement_ranks(cfg: dict, pool: list[dict] | None = None) -> tuple[dict, dict]:
    """How many players at each position are started league-wide (the N in 'Nth best'), and how the
    flex slots get filled.

    Default ("equilibrium"): dedicated slots are filled by position, then every flex slot league-wide
    goes to the best remaining RB/WR/TE regardless of position. That makes the marginal RB and the
    marginal WR worth about the same — which is what actually happens, because nobody flexes a
    95-point back over a 143-point receiver. The old fixed-share model (RB 55% / WR 40% / TE 5%)
    is still available with roster.flex_mode: fixed_share; it can price a position's replacement
    absurdly low when the other position is deeper, which over-values that position's depth.
    """
    teams = int(cfg["league"]["teams"])
    s = starters(cfg)
    roster = cfg.get("roster", {}) or {}
    mode = (roster.get("flex_mode") or ("fixed_share" if roster.get("flex_share") else "equilibrium")).lower()
    # Byes and injuries: someone is always starting a deeper player at RB/WR in deep leagues.
    pad = 2 if teams <= 10 else 3 if teams <= 12 else 4
    ranks = {
        "QB": teams * s["QB"] + round_half_up(teams * s["SUPERFLEX"] * 0.85),
        "K": teams * s["K"],
        "DEF": teams * s["DEF"],
    }
    flex_fill = {"RB": 0, "WR": 0, "TE": 0}
    if mode == "fixed_share" or pool is None:
        share = roster.get("flex_share") or ({"RB": 0.45, "WR": 0.50, "TE": 0.05} if float(cfg.get("scoring", {}).get("reception", 0.5)) >= 1.0
                                            else {"RB": 0.55, "WR": 0.40, "TE": 0.05})
        for pos in ("RB", "WR", "TE"):
            flex_fill[pos] = round_half_up(teams * s["FLEX"] * share.get(pos, 0))
            ranks[pos] = teams * s[pos] + flex_fill[pos]
        ranks["RB"] += pad
        ranks["WR"] += pad
        ranks["TE"] += 1
    else:
        byp = defaultdict(list)
        for p in pool:
            if p["pos"] in ("RB", "WR", "TE"):
                byp[p["pos"]].append(p["proj"])
        for k in byp:
            byp[k].sort(reverse=True)
        taken = {pos: teams * s[pos] for pos in ("RB", "WR", "TE")}
        remaining = []
        for pos in ("RB", "WR", "TE"):
            for i in range(taken[pos], len(byp[pos])):
                remaining.append((byp[pos][i], pos, i))
        remaining.sort(reverse=True)
        n_flex = teams * s["FLEX"] + pad  # pad = extra "virtual" flex starters for byes and injuries
        for v, pos, i in remaining[:n_flex]:
            taken[pos] = max(taken[pos], i + 1)
            flex_fill[pos] += 1
        for pos in ("RB", "WR", "TE"):
            ranks[pos] = max(taken[pos], 1)
        ranks["TE"] = max(ranks["TE"], teams * s["TE"] + 1)
    for k, v in (roster.get("replacement_rank") or {}).items():
        ranks[k.upper()] = int(v)
    return ranks, flex_fill


def replacement_levels(pool: list[dict], ranks: dict) -> dict:
    byp = defaultdict(list)
    for p in pool:
        byp[p["pos"]].append(p["proj"])
    out = {}
    for pos, n in ranks.items():
        vals = sorted(byp.get(pos, []), reverse=True)
        if not vals:
            out[pos] = 0.0
        else:
            out[pos] = vals[min(max(n, 1), len(vals)) - 1]
    return out


def pick_number(round_no: int, slot: int, teams: int) -> int:
    return (round_no - 1) * teams + slot if round_no % 2 == 1 else round_no * teams - slot + 1


def keeper_cost_round(original_round, cfg: dict):
    """Apply the league's cost basis. Returns None if not keepable."""
    k = cfg.get("keepers", {})
    basis = k.get("cost_basis", "same_round")
    if original_round is None:
        return None
    r = int(original_round)
    if basis == "same_round":
        return r
    if basis in ("round_minus_one", "escalating"):
        c = r - 1 - int(k.get("escalation_per_year", 0) or 0) * 0  # escalation applies to future years
        if c < 1:
            return 1 if k.get("round_one_keepable", True) else None
        return c
    if basis == "round_minus_two":
        c = r - 2
        if c < 1:
            return 1 if k.get("round_one_keepable", True) else None
        return c
    if basis == "fixed":
        return int(k.get("fixed_round") or 1)
    return r


def keeper_candidates(cfg: dict, byname: dict) -> list[dict]:
    k = cfg.get("keepers", {})
    if int(k.get("count", 0) or 0) == 0:
        return []
    rounds_total = int(cfg["league"].get("rounds", 15))
    out = []
    for entry in cfg.get("my_roster", []) or []:
        name = entry.get("player")
        acq = (entry.get("acquired") or "draft").lower()
        rnd = entry.get("round")
        cost = None
        if acq == "waiver":
            w = k.get("waiver_pickups", "not_keepable")
            if w == "last_round":
                cost = rounds_total
            elif w == "assigned_round" and rnd:
                cost = keeper_cost_round(rnd, cfg)
            else:
                cost = None
        elif acq == "trade" and k.get("traded_players", "inherit_cost") == "repriced":
            cost = None  # commissioner-priced; user must supply
        else:
            cost = keeper_cost_round(rnd, cfg)
        pl = byname.get(name)
        out.append({"player": name, "pos": entry.get("pos") or (pl["pos"] if pl else "?"),
                    "acquired": acq, "original_round": rnd, "cost_round": cost,
                    "in_pool": pl is not None})
    return out


# ----------------------------------------------------------------------------
# Simulation
# ----------------------------------------------------------------------------

class Sim:
    def __init__(self, cfg: dict, pool: list[dict], keeper_name: str | None, keeper_round: int | None):
        self.cfg = cfg
        self.teams = int(cfg["league"]["teams"])
        self.rounds = int(cfg["league"].get("rounds", 15))
        self.slot = int(cfg["league"].get("draft_slot", 1))
        self.starters = starters(cfg)
        self.flex = self.starters["FLEX"]
        self.superflex = self.starters["SUPERFLEX"]
        self.ranks, self.flex_fill = replacement_ranks(cfg, pool)
        self.repl = replacement_levels(pool, self.ranks)
        self.pool = pool
        for p in self.pool:
            p["vor"] = p["proj"] - self.repl.get(p["pos"], 0.0)
        self.byname = {p["name"]: p for p in pool}
        self.keeper = keeper_name
        self.keeper_round = keeper_round
        self.n_keepers = int(cfg.get("keepers", {}).get("count", 0) or 0)
        self.maxc = {"QB": 2 + self.superflex, "RB": 6, "WR": 7, "TE": 2, "K": 1, "DEF": 1}
        prefs = cfg.get("preferences", {}) or {}
        self.avoid = set(prefs.get("avoid_players") or [])
        self.qb_strategy = prefs.get("qb_strategy", "auto")
        self.te_strategy = prefs.get("te_strategy", "auto")
        self.risk = prefs.get("risk", "balanced")
        self.published_keepers = cfg.get("keepers", {}).get("league_keeper_list") or []
        # Names whose availability must always be reported (the user's own players and targets).
        self.watch = set()
        for e in (cfg.get("my_guys") or []) + (cfg.get("my_roster") or []):
            if isinstance(e, dict) and e.get("player"):
                self.watch.add(e["player"])
            elif isinstance(e, str):
                self.watch.add(e)
        # Expected best surplus still available at each of my picks, by position — learned in a probe
        # run and used as the opportunity cost of waiting ("draft the position that's about to run out").
        self.pos_horizon: dict[int, dict[str, float]] = {}

    # ---- draft order ----
    def pick_order(self, forfeits: dict) -> list[tuple[int, int, int]]:
        order = []
        overall = 0
        for r in range(1, self.rounds + 1):
            slots = range(1, self.teams + 1) if r % 2 == 1 else range(self.teams, 0, -1)
            for t in slots:
                overall += 1
                if r in forfeits.get(t, set()):
                    continue
                order.append((overall, r, t))
        return order

    def my_ladder(self) -> list[tuple[int, int]]:
        forfeit = {self.keeper_round} if self.keeper_round else set()
        return [(pick_number(r, self.slot, self.teams), r) for r in range(1, self.rounds + 1) if r not in forfeit]

    # ---- keepers ----
    def draw_keepers(self, rng: random.Random):
        kept, forfeits = set(), {}
        if self.keeper:
            kept.add(self.keeper)
            forfeits[self.slot] = {self.keeper_round} if self.keeper_round else set()
        if self.n_keepers == 0:
            return kept, forfeits
        opps = [t for t in range(1, self.teams + 1) if t != self.slot]
        if self.published_keepers:
            # Use the league's real list. Assign rounds as given; map teams in order of appearance.
            team_ids = {}
            for entry in self.published_keepers:
                if entry.get("player") == self.keeper:
                    continue
                team = entry.get("team", f"team{len(team_ids)}")
                if team not in team_ids and opps:
                    team_ids[team] = opps.pop(0)
                t = team_ids.get(team)
                if t is None:
                    continue
                kept.add(entry["player"])
                forfeits.setdefault(t, set()).add(int(entry.get("round", 1)))
            return kept, forfeits
        cands = [p for p in self.pool if p["adp"] <= 110 and p["name"] not in kept and p["pos"] in ("RB", "WR", "TE", "QB")]
        weights = [max(1.0, 130 - p["adp"]) for p in cands]
        per_team = self.n_keepers
        for t in opps:
            for _ in range(per_team):
                for _try in range(50):
                    pl = rng.choices(cands, weights=weights)[0]
                    if pl["name"] not in kept:
                        kept.add(pl["name"])
                        break
                a = pl["adp"]
                # keeper cost correlates with how good the player is (cheap keepers are mid-round hits)
                rnd = (rng.choice([1, 1, 1, 2, 2]) if a <= 25 else
                       rng.choice([2, 2, 3, 3, 4]) if a <= 55 else
                       rng.choice([3, 4, 4, 5, 5]) if a <= 80 else
                       rng.choice([5, 6, 6, 7, 8]))
                forfeits.setdefault(t, set()).add(rnd)
        return kept, forfeits

    # ---- lineup scoring ----
    def lineup_pts(self, roster: list[dict], fill_replacement: bool = False):
        """Projected points of the best legal starting lineup.

        With fill_replacement=True, empty starting slots are filled with replacement-level
        points instead of zero. That is the version used for drafting decisions: the
        alternative to drafting a QB now is not 'no QB', it's the QB you can get for free later.
        """
        byp = defaultdict(list)
        for p in roster:
            byp[p["pos"]].append(p)
        for k in byp:
            byp[k].sort(key=lambda x: -x["proj"])
        start, used, total = [], set(), 0.0
        for pos in ("QB", "RB", "WR", "TE", "K", "DEF"):
            n = self.starters[pos]
            chosen = byp[pos][:n]
            for p in chosen:
                start.append(p)
                used.add(id(p))
                total += p["proj"]
            if fill_replacement:
                total += (n - len(chosen)) * self.repl.get(pos, 0.0)
        flex_repl = max(self.repl.get(x, 0.0) for x in SKILL_POS)
        flexpool = sorted([p for p in roster if p["pos"] in SKILL_POS and id(p) not in used], key=lambda x: -x["proj"])
        chosen = [p for p in flexpool[: self.flex] if (not fill_replacement or p["proj"] > flex_repl)]
        for p in chosen:
            start.append(p)
            used.add(id(p))
            total += p["proj"]
        if fill_replacement:
            total += (self.flex - len(chosen)) * flex_repl
        if self.superflex:
            sf_repl = max(flex_repl, self.repl.get("QB", 0.0))
            sfpool = sorted([p for p in roster if p["pos"] in SKILL_POS + QB_POS and id(p) not in used], key=lambda x: -x["proj"])
            chosen = [p for p in sfpool[: self.superflex] if (not fill_replacement or p["proj"] > sf_repl)]
            for p in chosen:
                start.append(p)
                total += p["proj"]
            if fill_replacement:
                total += (self.superflex - len(chosen)) * sf_repl
        return total, start

    # ---- opponents ----
    def opp_pick(self, avail, roster, rnd, rng):
        c = Counter(p["pos"] for p in roster)
        best, bs = None, 1e9
        for p in avail:
            if c[p["pos"]] >= self.maxc[p["pos"]]:
                continue
            if p["pos"] in LATE_POS:
                # Real rooms start taking K/DEF a few rounds from the end; a few managers go earlier.
                if rnd < self.rounds - 4:
                    continue
                early = (self.rounds - 1) - rnd  # 0 in the penultimate round, 3 four rounds out
                if rng.random() > (0.9 - 0.25 * early):
                    continue
            # Noise scaled to each player's observed ADP spread, but capped: a deep sleeper with a
            # 45-pick std dev should not be drafted in round 5 by an ADP-driven opponent.
            sd = max(4.0, min(p["sd"], 0.20 * p["adp"] + 4.0))
            s = p["adp"] + rng.gauss(0, sd)
            if rnd >= 8:
                need = self.starters.get(p["pos"], 0) - c[p["pos"]]
                if need > 0:
                    s -= 12
            if s < bs:
                best, bs = p, s
        return best or avail[0]

    # ---- me ----
    def my_pick(self, avail, roster, rnd, rng, next_pick=None):
        c = Counter(p["pos"] for p in roster)
        base, _ = self.lineup_pts(roster, fill_replacement=True)
        left = self.rounds - rnd
        best, bv = None, -1e9
        for p in avail:
            if p["name"] in self.avoid:
                continue
            if c[p["pos"]] >= self.maxc[p["pos"]]:
                continue
            if p["pos"] in LATE_POS and rnd < self.rounds - 1:
                continue
            gain = self.lineup_pts(roster + [p], fill_replacement=True)[0] - base
            v = gain + 0.40 * p["vor"]
            # Opportunity cost of waiting: if an equally good player at this position is usually still
            # there at my next pick, taking him now is worth less; if the position is about to run out,
            # it's worth more. Learned from the probe run (self.pos_horizon).
            if next_pick is not None and next_pick in self.pos_horizon:
                later = self.pos_horizon[next_pick].get(p["pos"])
                if later is not None:
                    v += 0.6 * (p["vor"] - later)
            if self.risk == "aggressive":
                v += 0.05 * p["sd"]
            elif self.risk == "conservative":
                v -= 0.05 * p["sd"]
            qb_needed = self.starters["QB"] + self.superflex
            if p["pos"] == "QB":
                if c["QB"] < qb_needed and left <= 5:
                    v += 50
                if c["QB"] >= qb_needed:
                    v -= 80
                if self.qb_strategy == "late" and rnd <= 5:
                    v -= 40
                if self.qb_strategy == "early" and rnd <= 4 and c["QB"] == 0:
                    v += 25
            if p["pos"] == "TE":
                if c["TE"] == 0 and left <= 5:
                    v += 45
                if c["TE"] >= 1:
                    v -= 55
                if self.te_strategy == "punt" and rnd <= 6:
                    v -= 40
                if self.te_strategy == "elite" and rnd <= 3 and c["TE"] == 0:
                    v += 25
            # Bench balance: once a player wouldn't start, a fourth backup at one position is worth
            # less than a first backup at another — injuries hit every position.
            if gain <= 0.5 and p["pos"] in SKILL_POS:
                backups = c[p["pos"]] - self.starters[p["pos"]]
                if backups >= 2:
                    v -= 10 * (backups - 1)
            if v > bv:
                best, bv = p, v
        return best or avail[0]

    # ---- one draft ----
    def run(self, seed: int, collect=None, best_avail=None, pos_best=None, min_adp=None):
        rng = random.Random(seed)
        kept, forfeits = self.draw_keepers(rng)
        avail = [p for p in self.pool if p["name"] not in kept]
        rosters = defaultdict(list)
        if self.keeper and self.keeper in self.byname:
            rosters[self.slot].append(self.byname[self.keeper])
        picks = []
        order = self.pick_order(forfeits)
        my_overall = [ov for ov, r, t in order if t == self.slot]
        for overall, rnd, t in order:
            if not avail:
                break
            if t == self.slot:
                if collect is not None:
                    for p in avail:
                        collect[overall][p["name"]] += 1
                if best_avail is not None:
                    top = max(avail, key=lambda x: x["vor"])
                    best_avail[overall].append(top["vor"])
                if pos_best is not None:
                    seen = {}
                    for p in avail:
                        if p["vor"] > seen.get(p["pos"], -1e9):
                            seen[p["pos"]] = p["vor"]
                    for pos, v in seen.items():
                        pos_best[overall][pos].append(v)
                if min_adp is not None:
                    # net inflation: how many more players are gone than the pick number implies
                    gone = sum(1 for p in self.pool if p["pos"] not in LATE_POS) - sum(1 for p in avail if p["pos"] not in LATE_POS)
                    min_adp[overall].append(gone - (overall - 1))
                idx = my_overall.index(overall)
                nxt = my_overall[idx + 1] if idx + 1 < len(my_overall) else None
                p = self.my_pick(avail, rosters[t], rnd, rng, next_pick=nxt)
                picks.append((overall, rnd, p))
            else:
                p = self.opp_pick(avail, rosters[t], rnd, rng)
            rosters[t].append(p)
            avail.remove(p)
        total, start = self.lineup_pts(rosters[self.slot])
        return picks, rosters[self.slot], total, start


# ----------------------------------------------------------------------------
# Reporting
# ----------------------------------------------------------------------------

def fmt_table(rows, headers):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--league", required=True)
    ap.add_argument("--players", required=True)
    ap.add_argument("--sims", type=int, default=1500)
    ap.add_argument("--samples", type=int, default=10, help="full sample drafts to print")
    ap.add_argument("--top", type=int, default=5, help="players to show per pick")
    ap.add_argument("--keeper", default=None, help="override: the player you are keeping")
    ap.add_argument("--keeper-round", type=int, default=None, help="override: the round that keeper costs")
    ap.add_argument("--no-keeper", action="store_true", help="simulate keeping nobody")
    ap.add_argument("--out", default="sim.json")
    ap.add_argument("--seed", type=int, default=1000)
    args = ap.parse_args()

    cfg = load_league(args.league)
    pool = load_players(args.players)
    byname = {p["name"]: p for p in pool}

    # --- keeper evaluation (before choosing) ---
    teams = int(cfg["league"]["teams"])
    slot = int(cfg["league"].get("draft_slot", 1))
    cands = keeper_candidates(cfg, byname)

    # Choose keeper: override > best surplus among eligible candidates > none
    keeper, keeper_round = None, None
    if args.no_keeper:
        pass
    elif args.keeper:
        keeper = args.keeper
        keeper_round = args.keeper_round
        if keeper_round is None:
            for c in cands:
                if c["player"] == keeper:
                    keeper_round = c["cost_round"]
        if keeper not in byname:
            sys.exit(f"Keeper '{keeper}' is not in players.csv")
    else:
        elig = [c for c in cands if c["cost_round"] and c["in_pool"]]
        if elig:
            # provisional: pick by ADP-vs-pick surplus; refined below with the sim
            def surplus_picks(c):
                return pick_number(c["cost_round"], slot, teams) - byname[c["player"]]["adp"]
            best = max(elig, key=surplus_picks)
            keeper, keeper_round = best["player"], best["cost_round"]

    # First pass: simulate with NO keeper to learn what each pick returns (for keeper valuation)
    base_sim = Sim(cfg, [dict(p) for p in pool], None, None)
    best_avail = defaultdict(list)
    n_probe = min(400, args.sims)
    for s in range(n_probe):
        base_sim.run(args.seed + 90000 + s, best_avail=best_avail)
    exp_best_vor = {ov: statistics.mean(v) for ov, v in best_avail.items()}

    keeper_eval = []
    for c in cands:
        pl = byname.get(c["player"])
        row = {**c}
        if pl and c["cost_round"]:
            pk = pick_number(c["cost_round"], slot, teams)
            vor = pl["proj"] - base_sim.repl[pl["pos"]]
            alt = exp_best_vor.get(pk)
            if alt is None:  # nearest simulated pick
                near = min(exp_best_vor, key=lambda k: abs(k - pk))
                alt = exp_best_vor[near]
            row.update({"cost_pick": pk, "adp": pl["adp"], "proj": pl["proj"], "vor": round(vor, 1),
                        "surplus_picks": round(pk - pl["adp"], 1),
                        "expected_alt_vor_at_pick": round(alt, 1),
                        "surplus_points": round(vor - alt, 1)})
        else:
            row.update({"cost_pick": None, "adp": pl["adp"] if pl else None, "proj": pl["proj"] if pl else None,
                        "surplus_points": None, "reason": "not keepable under league rules" if not c["cost_round"] else "not in players.csv"})
        keeper_eval.append(row)
    # Refine keeper choice with points surplus
    if not args.no_keeper and not args.keeper:
        pts = [r for r in keeper_eval if r.get("surplus_points") is not None]
        if pts:
            best = max(pts, key=lambda r: r["surplus_points"])
            if best["surplus_points"] > 0:
                keeper, keeper_round = best["player"], best["cost_round"]
            else:
                keeper, keeper_round = None, None

    sim = Sim(cfg, [dict(p) for p in pool], keeper, keeper_round)

    # --- probe with the chosen keeper: learn the per-position horizon (opportunity cost of waiting)
    pos_best = defaultdict(lambda: defaultdict(list))
    for s in range(min(300, args.sims)):
        sim.run(args.seed + 70000 + s, pos_best=pos_best)
    sim.pos_horizon = {ov: {pos: statistics.mean(v) for pos, v in d.items()} for ov, d in pos_best.items()}

    # --- availability ---
    coll = defaultdict(Counter)
    min_adp = defaultdict(list)
    totals = []
    owned = Counter()
    for s in range(args.sims):
        picks, roster, total, start = sim.run(args.seed + s, collect=coll, min_adp=min_adp)
        totals.append(total)
        for _, r, p in picks:
            if r <= 8:
                owned[p["name"]] += 1
    # Net keeper inflation at each pick: players gone minus (pick − 1), averaged over runs. Keepers add
    # to it; the picks forfeited for keepers subtract from it. Pick p effectively buys the ADP-(p + X) player.
    inflation = {ov: round(max(0.0, statistics.mean(v)), 1) for ov, v in min_adp.items() if ov <= teams * 9}

    ladder = sim.my_ladder()
    avail = {}
    for overall, rnd in ladder:
        if overall not in coll:
            continue
        late = rnd >= sim.rounds - 2
        rows = [(nm, c / args.sims) for nm, c in coll[overall].items()
                if c / args.sims >= 0.15 and (late or sim.byname[nm]["pos"] not in LATE_POS)]
        rows.sort(key=lambda x: -sim.byname[x[0]]["vor"])
        shown, keep, kept_names = Counter(), [], set()
        for nm, pr in rows:
            pos = sim.byname[nm]["pos"]
            if shown[pos] >= 5:
                continue
            shown[pos] += 1
            keep.append((nm, pr))
            kept_names.add(nm)
            if len(keep) >= 24:
                break
        # Always report the user's own players and targets, even when they aren't top-5 at the position.
        for nm in sorted(sim.watch):
            if nm in sim.byname and nm not in kept_names and nm != keeper:
                pr = coll[overall].get(nm, 0) / args.sims
                keep.append((nm, pr))
        avail[overall] = [{"name": nm, "pos": sim.byname[nm]["pos"], "team": sim.byname[nm]["team"],
                           "proj": round(sim.byname[nm]["proj"]), "surplus": round(sim.byname[nm]["vor"]),
                           "there": round(pr * 100), "watch": nm in sim.watch} for nm, pr in keep]

    # --- sample drafts ---
    samples = []
    for i in range(args.samples):
        picks, roster, total, start = sim.run(args.seed + 500000 + i)
        samples.append({"draft": i + 1, "total": round(total),
                        "picks": [{"pick": ov, "round": r, "name": p["name"], "pos": p["pos"], "proj": round(p["proj"])} for ov, r, p in picks],
                        "starters": [{"name": p["name"], "pos": p["pos"], "proj": round(p["proj"])} for p in start]})

    out = {
        "league": {"teams": teams, "slot": slot, "rounds": sim.rounds, "keeper": keeper, "keeper_round": keeper_round,
                   "platform": cfg["league"].get("platform"), "name": cfg["league"].get("name"), "team_name": cfg["league"].get("team_name")},
        "replacement_rank": sim.ranks,
        "replacement": {k: round(v) for k, v in sim.repl.items()},
        "flex_fill": sim.flex_fill,
        "position_plan": {str(ov): {pos: round(v) for pos, v in d.items() if pos in ("QB", "RB", "WR", "TE")}
                          for ov, d in sorted(sim.pos_horizon.items()) if ov <= teams * 10},
        "ladder": [{"pick": ov, "round": r} for ov, r in ladder],
        "keeper_eval": keeper_eval,
        "expected_best_surplus_at_pick": {str(k): round(v, 1) for k, v in sorted(exp_best_vor.items())},
        "inflation_at_pick": {str(k): v for k, v in sorted(inflation.items())},
        "watch": sorted(sim.watch),
        "availability": {str(k): v for k, v in avail.items()},
        "most_owned": [{"name": n, "pct": round(c / args.sims * 100)} for n, c in owned.most_common(15)],
        "totals": {"mean": round(statistics.mean(totals)), "min": round(min(totals)), "max": round(max(totals)),
                   "sd": round(statistics.pstdev(totals), 1)},
        "samples": samples,
        "settings": {"sims": args.sims, "seed": args.seed, "keeper_model": "published list" if sim.published_keepers else "weighted draw"},
    }
    Path(args.out).write_text(json.dumps(out, indent=1), encoding="utf-8")

    # Full name × pick availability matrix (every player, every one of your picks), for lookups.
    mpath = Path(args.out).with_name(Path(args.out).stem + "_availability.csv")
    with open(mpath, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        cols = [ov for ov, _ in ladder if ov in coll]
        w.writerow(["name", "pos", "adp", "proj", "surplus"] + [f"there@{ov}" for ov in cols])
        for p in sorted(sim.pool, key=lambda x: x["adp"]):
            w.writerow([p["name"], p["pos"], p["adp"], round(p["proj"]), round(p["vor"])] +
                       [round(coll[ov].get(p["name"], 0) / args.sims * 100) for ov in cols])

    # --- console summary (markdown) ---
    print(f"# Draft simulation — {teams} teams, slot {slot}, {args.sims} runs")
    print(f"Keeper: {keeper or 'none'}" + (f" (round {keeper_round})" if keeper_round else ""))
    print("\n## Replacement level (position → points of the last weekly starter)")
    print(fmt_table([(k, v, f"{k}{sim.ranks[k]}") for k, v in out["replacement"].items()], ["Pos", "Replacement", "Who"]))
    ff = sim.flex_fill
    print(f"Flex slots league-wide fill as RB {ff['RB']} / WR {ff['WR']} / TE {ff['TE']} (equilibrium: best remaining player takes the flex).")
    print("\n## Position plan — expected best surplus still available at each of your picks, by position")
    pp = out["position_plan"]
    rows = []
    for ov, _ in ladder:
        d = pp.get(str(ov))
        if not d:
            continue
        best = max(d, key=d.get)
        rows.append((ov, d.get("QB", ""), d.get("RB", ""), d.get("WR", ""), d.get("TE", ""), best))
    print(fmt_table(rows, ["Pick", "QB", "RB", "WR", "TE", "Best"]))
    if keeper_eval:
        print("\n## Keeper candidates (surplus in points = your surplus minus what that pick would otherwise return)")
        rows = []
        for r in sorted(keeper_eval, key=lambda x: -(x.get("surplus_points") if x.get("surplus_points") is not None else -999)):
            if r.get("surplus_points") is None:
                rows.append((r["player"], r["pos"], r.get("acquired"), "—", "—", "—", "—", r.get("reason", "")))
            else:
                rows.append((r["player"], r["pos"], f"R{r['cost_round']} → pick {r['cost_pick']}", r["adp"], r["proj"],
                             f"{r['surplus_picks']:+}", f"{r['surplus_points']:+}", ""))
        print(fmt_table(rows, ["Player", "Pos", "Cost", "ADP", "Proj", "Surplus (picks)", "Surplus (pts)", "Note"]))
    print("\n## Your picks")
    print(", ".join(f"{ov} (R{r})" for ov, r in ladder))
    print("\n## Keeper inflation actually in force (pick p buys roughly the ADP-(p + X) player)")
    print(", ".join(f"pick {ov}: X={inflation[ov]:+}" for ov, _ in ladder if ov in inflation and ov <= teams * 8))
    print(f"\n## Top {args.top} at each pick (There % = still available across sims)")
    for ov, r in ladder:
        if str(ov) not in out["availability"] or ov > 130:
            continue
        rows = [(x["name"], x["pos"], x["proj"], f"+{x['surplus']}", f"{x['there']}%") for x in out["availability"][str(ov)][: args.top]]
        print(f"\n### Pick {ov} (R{r})")
        print(fmt_table(rows, ["Player", "Pos", "Proj", "Surplus", "There"]))
    print(f"\n## Sample drafts: projected starter points {out['totals']['min']}–{out['totals']['max']} (mean {out['totals']['mean']})")
    for sdraft in samples:
        line = ", ".join(f"{p['pick']} {p['name']}" for p in sdraft["picks"][:8])
        print(f"- Draft {sdraft['draft']} ({sdraft['total']}): {line}")
    print("\n## Most-owned across runs")
    print(", ".join(f"{m['name']} {m['pct']}%" for m in out["most_owned"][:10]))
    print(f"\nWrote {args.out} and {mpath.name}")


if __name__ == "__main__":
    main()
