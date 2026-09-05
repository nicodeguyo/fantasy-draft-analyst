#!/usr/bin/env python3
"""Reproduce one illustrative, paired draft branch from the public sample league.

python3 scripts/reproduce_demo.py --repo . --output docs/site/pick-comparison.json
No fresh data is fetched. This is an explanation of a rollout, not an estimate
of which first-round pick is best on average. Selection is fixed in advance:
seed 20260905, first pick, highest projected available RB versus WR.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import statistics
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--output', type=Path, default=Path('pick-comparison.json'))
    args = ap.parse_args()
    repo = args.repo.resolve()
    sys.path.insert(0, str(repo / 'skills/fantasy-draft-analyst/scripts'))
    import draft_sim as ds
    sample = repo / 'examples/sample-league'
    cfg = ds.load_league(str(sample / 'league.yaml'))
    source_sim = json.loads((sample / 'sim.json').read_text())
    sim = ds.Sim(cfg, ds.load_players(str(sample / 'players.csv')),
                 source_sim['league']['keeper'], source_sim['league']['keeper_round'])
    horizon = defaultdict(lambda: defaultdict(list))
    for i in range(300):
        sim.run(71000 + i, pos_best=horizon)
    sim.pos_horizon = {ov: {pos: statistics.mean(vals) for pos, vals in positions.items()}
                       for ov, positions in horizon.items()}
    seed = 20260905
    pick, round_number = sim.my_ladder()[0]
    state = sim.start(seed)
    sim.play(state, stop_at=pick)
    assert sim.at_pick(state) == pick
    branches = []
    for position in ('RB', 'WR'):
        candidate = max((p for p in state['avail'] if p['pos'] == position), key=lambda p: p['proj'])
        branch = sim.copy_state(state)
        sim.take(branch, candidate)
        sim.play(branch)
        roster = branch['rosters'][sim.slot]
        total, lineup = sim.lineup_pts(roster)
        assert len(roster) == 15 and len({p['name'] for p in roster}) == 15
        assert len(lineup) == 9 and len({p['name'] for p in lineup}) == 9
        assert abs(total - sum(p['proj'] for p in lineup)) < 0.000001
        counts = Counter()
        rows = []
        for player in lineup:
            pos = player['pos']
            counts[pos] += 1
            slot = pos if counts[pos] <= sim.starters[pos] else 'FLEX'
            if sim.starters.get(slot, 0) > 1:
                slot = f'{slot}{counts[pos]}'
            rows.append({'slot': slot, 'name': player['name'], 'position': pos,
                         'projected_points': player['proj']})
        assert {r['slot'] for r in rows} == {'QB', 'RB1', 'RB2', 'WR1', 'WR2', 'TE', 'K', 'DEF', 'FLEX'}
        rows.sort(key=lambda r: ['QB','RB1','RB2','WR1','WR2','TE','FLEX','K','DEF'].index(r['slot']))
        board_row = next((r for r in source_sim['pick_values'][str(pick)] if r['name'] == candidate['name']), None)
        branches.append({'id': position.lower(), 'candidate': {'name': candidate['name'], 'position': position},
                         'projected_lineup_points': total, 'starting_lineup': rows,
                         'draft_picks': [{'overall': ov, 'round': rd, 'name': p['name'], 'position': p['pos']}
                                         for ov, rd, p in branch['picks']],
                         'bench': [p['name'] for p in roster if p not in lineup],
                         'published_board_average': board_row})
    data = {
        'title': 'One pick. Two possible teams.',
        'description': 'Two branches of one simulated draft. Both candidates were available at pick 5. The remaining draft uses the same adaptive simulator policy.',
        'disclaimer': 'One illustrative draft, not an average, forecast, or recommendation. These are projected full-season starting-lineup points from the saved sample data, not actual points or a promised advantage. The published board averages many rollouts and can rank these picks differently.',
        'method': {'seed': seed, 'overall_pick': pick, 'round': round_number,
                   'horizon_probe_seeds': [71000, 71299], 'horizon_probes': 300,
                   'candidate_rule': 'Highest projected available RB versus highest projected available WR at the first pick; no search for the largest difference.',
                   'pairing': 'Identical state and RNG state before the forced pick; opponent decisions can diverge as the remaining pool changes.',
                   'continuation_policy': 'draft_sim.Sim.play with the adaptive heuristic; no forced later picks'},
        'league': {'name': cfg['league']['name'], 'teams': sim.teams, 'draft_slot': sim.slot,
                   'rounds': sim.rounds, 'scoring': 'Half PPR', 'platform': cfg['league']['platform'],
                   'keeper': sim.keeper, 'keeper_round': sim.keeper_round},
        'inputs_sha256': {f: hashlib.sha256((sample / f).read_bytes()).hexdigest() for f in ('league.yaml','players.csv','sim.json')},
        'branches': branches,
        'wr_minus_rb_projected_points': branches[1]['projected_lineup_points'] - branches[0]['projected_lineup_points'],
    }
    left = {r['slot']: r for r in branches[0]['starting_lineup']}
    right = {r['slot']: r for r in branches[1]['starting_lineup']}
    data['changed_slots'] = [slot for slot in left if left[slot]['name'] != right[slot]['name']]
    args.output.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps({'output': str(args.output), 'branches': [(b['candidate']['name'], b['projected_lineup_points']) for b in branches], 'changed_slots': data['changed_slots']}))

if __name__ == '__main__':
    main()
