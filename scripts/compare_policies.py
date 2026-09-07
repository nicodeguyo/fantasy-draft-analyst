#!/usr/bin/env python3
"""Internal held-out draft-model comparison of the exact saved-board policy.

Scores the sum of projections for one best legal starting lineup. These are simulated
draft rooms, not seasons, weekly results or a comparison to a platform's actual autopick.
Paired seeds couple randomness; different decisions can change later opponent draws.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'skills/fantasy-draft-analyst/scripts'))
import draft_sim as ds
from board_policy import row_groups, fallback_order, run_board, POLICY_DESCRIPTION, POLICY_VERSION, filled_slots


def summarize(runs):
    base = next(iter(runs.values()))
    out = []
    for name, vals in runs.items():
        diffs = [a-b for a, b in zip(vals, base)]
        half = 1.96 * statistics.stdev(diffs) / math.sqrt(len(diffs)) if len(diffs) > 1 else None
        delta = statistics.mean(diffs)
        out.append({'name': name, 'mean': statistics.mean(vals), 'sd': statistics.pstdev(vals),
                    'vs_baseline': delta, 'paired_half_width': half,
                    'paired_interval': [delta-half, delta+half] if half is not None else None})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for field in ('league', 'players', 'sim'):
        ap.add_argument('--'+field, required=True)
    ap.add_argument('--notes', help='The exact notes used to render the board; default: notes.json beside sim')
    ap.add_argument('--top', type=int, default=5, help='Must match build_board --top')
    ap.add_argument('--drafts', type=int, default=800)
    ap.add_argument('--seed', type=int, default=1000)
    ap.add_argument('--horizon-probes', type=int, default=300)
    ap.add_argument('--output', help='Write machine-readable evidence JSON')
    args = ap.parse_args()
    if args.drafts < 2:
        ap.error('--drafts must be at least 2 for paired uncertainty')
    if args.top < 1 or args.horizon_probes < 1:
        ap.error('--top and --horizon-probes must be positive')
    notes_path = Path(args.notes) if args.notes else Path(args.sim).with_name('notes.json')
    cfg, pool = ds.load_league(args.league), ds.load_players(args.players)
    cfg.setdefault('preferences', {})['draft_policy'] = 'legacy'  # Archived v2 illustration.
    sim = json.loads(Path(args.sim).read_text())
    notes = json.loads(notes_path.read_text())
    if not sim.get('pick_values'):
        ap.error('sim.json needs --pick-values')
    s = ds.Sim(cfg, [dict(p) for p in pool], sim['league'].get('keeper'), sim['league'].get('keeper_round'))
    pos_best = defaultdict(lambda: defaultdict(list))
    for i in range(args.horizon_probes):
        s.run(args.seed + 70000 + i, pos_best=pos_best)
    s.pos_horizon = {ov: {p: statistics.mean(v) for p, v in d.items()} for ov, d in pos_best.items()}
    players = {p['name']: p for p in pool}
    board = {}
    for pick in sim['ladder']:
        pk = int(pick['pick'])
        top, rest, _ = row_groups(sim, notes, players, pk, args.top)
        board[pk] = [r['name'] for r in top+rest]
    fallback = fallback_order(sim, players)
    seeds = [args.seed + 900000 + i for i in range(args.drafts)]
    runs = {'Noisy ADP-based draft bot': [], 'Saved-board policy': [], 'Adaptive heuristic': []}
    complete = {name: 0 for name in runs}
    for seed in seeds:
        results = [run_board(s, seed, board, fallback, adp_baseline=True),
                   run_board(s, seed, board, fallback), s.run(seed)]
        for name, (_, roster, total, _) in zip(runs, results):
            runs[name].append(total)
            complete[name] += filled_slots(roster, s.starters) == sum(s.starters.values())
            if len(roster) != s.rounds or len({p['name'] for p in roster}) != len(roster):
                raise ValueError(f'Invalid roster for {name} at seed {seed}')
    for name in list(runs)[:2]:
        if complete[name] != args.drafts:
            raise ValueError(f'Incomplete starting lineups for primary policy {name}')
    source_paths = {'league': Path(args.league), 'players': Path(args.players), 'sim': Path(args.sim),
                    'notes': notes_path, 'benchmark': Path(__file__),
                    'board_policy': Path(ds.__file__).with_name('board_policy.py'),
                    'renderer': Path(ds.__file__).with_name('build_board.py'), 'simulator': Path(ds.__file__)}
    result = {'schema_version': 1, 'drafts': args.drafts, 'seed': args.seed,
              'evaluation_seed_range': [seeds[0], seeds[-1]], 'horizon_probes': args.horizon_probes,
              'top': args.top, 'policy_version': POLICY_VERSION, 'policy_description': POLICY_DESCRIPTION,
              'complete_lineups': complete,
              'baseline_description': 'Noisy ADP-based draft bot with the same avoid list, position caps and last-pick starter-completion guard as the saved-board policy. Not a platform autopick.',
              'metric': 'Sum of projections for one best legal starting lineup',
              'scope': 'Internal draft-model test on held-out seeds; fixed projections and modeled opponents. Not weekly or real-season gains, model validation, or platform-autopick performance.',
              'interval_scope': 'Approximate 95% normal interval of paired mean differences from draft-sampling variation only; excludes projection, model and selection uncertainty.',
              'source_sha256': {k: hashlib.sha256(p.read_bytes()).hexdigest() for k,p in source_paths.items()},
              'policies': summarize(runs)}
    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2)+'\n')
    print(f"{args.drafts} held-out simulated drafts; paired seed range {seeds[0]}–{seeds[-1]}")
    print(result['metric'])
    for r in result['policies']:
        print(f"{r['name']:<27} {r['mean']:7.1f} (draft SD {r['sd']:.1f}); vs baseline {r['vs_baseline']:+.1f} ± {r['paired_half_width']:.1f}")
    print(result['scope'])
    print(result['interval_scope'])

if __name__ == '__main__':
    main()
