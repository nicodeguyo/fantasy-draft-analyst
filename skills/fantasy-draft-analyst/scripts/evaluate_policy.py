#!/usr/bin/env python3
"""Evaluate fixed-roster, one-pick decisions on user-supplied held-out snapshots.

Not a historical superiority claim or full-draft counterfactual. Weekly forecasts
must be timestamped before lock. Selection never sees realized points. Input JSON:
{schema_version:1, split:'held_out', cases:[{id, decision_at, snapshot_as_of,
league, players:[{name,pos,proj,adp,sd,player_id?}], roster:[id], available:[id],
round, next_pick?, weeks:[{as_of,lock_at,forecasts:{id:points},actuals:{id:points}}]}]}
Each week must supply every selected roster player's forecast and outcome. A
forecast of zero can represent known unavailability; absent data is an error.
"""
from __future__ import annotations
import argparse
import copy
from datetime import datetime
import json
import math
from pathlib import Path
import statistics

from draft_sim import Sim
from fantasy_core.roster_value import identity, lineup


def timestamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Evaluation timestamps must include a timezone')
    return result


def evaluate(document):
    if document.get('schema_version') != 1 or document.get('split') != 'held_out':
        raise ValueError('Require schema_version: 1 and explicit split: held_out')
    if not document.get('cases'):
        raise ValueError('At least one held-out case is required')
    results = []
    policies = ('adp', 'projection_vor', 'legacy', 'roster_v2')
    for case in document['cases']:
        if timestamp(case['snapshot_as_of']) > timestamp(case['decision_at']):
            raise ValueError('Draft input snapshot postdates the decision')
        players = copy.deepcopy(case['players'])
        byid = {identity(p): p for p in players}
        if len(byid) != len(players):
            raise ValueError('Duplicate player IDs in evaluation pool')
        for p in players:
            if p.get('as_of') and timestamp(p['as_of']) > timestamp(case['decision_at']):
                raise ValueError('Player evidence postdates the decision')
            p.setdefault('sd', max(4., float(p['adp']) * .08))
        roster_ids, available_ids = case['roster'], case['available']
        if len(roster_ids) != len(set(roster_ids)) or len(available_ids) != len(set(available_ids)):
            raise ValueError('Duplicate roster or availability IDs')
        if set(roster_ids) & set(available_ids):
            raise ValueError('Drafted players cannot be available')
        if not case.get('weeks'):
            raise ValueError('Realized held-out weeks required; do not infer historical results')
        rows = []
        for policy in policies:
            cfg = copy.deepcopy(case['league'])
            cfg.setdefault('preferences', {})['draft_policy'] = 'legacy' if policy == 'legacy' else 'roster_v2'
            sim = Sim(cfg, copy.deepcopy(players), None, None)
            pool = {identity(p): p for p in sim.pool}
            roster = [pool[pid] for pid in roster_ids]
            available = [pool[pid] for pid in available_ids]
            scores = sim.pick_scores(available, roster, int(case['round']), case.get('next_pick'))
            if not scores:
                raise ValueError('No legal candidates to evaluate')
            legal = [p for _, p in scores]
            if policy == 'adp':
                chosen = min(legal, key=lambda p: (p['adp'], identity(p)))
            elif policy == 'projection_vor':
                chosen = max(legal, key=lambda p: (p['vor'], -p['adp']))
            else:
                chosen = max(scores, key=lambda row: (row[0], -row[1]['adp']))[1]
            complete = roster + [chosen]
            weekly = []
            for week in case['weeks']:
                if timestamp(week['as_of']) > timestamp(week['lock_at']):
                    raise ValueError('Weekly forecast postdates lineup lock')
                if timestamp(week['lock_at']) <= timestamp(case['decision_at']):
                    raise ValueError('Evaluation outcomes must follow the draft decision')
                expected = []
                for p in complete:
                    pid = identity(p)
                    forecast = float(week['forecasts'][pid])
                    actual = float(week['actuals'][pid])
                    if not math.isfinite(forecast) or not math.isfinite(actual):
                        raise ValueError('Weekly values must be finite')
                    expected.append(dict(p, proj=forecast))
                _, selected = lineup(expected, cfg)
                # Outcomes enter only here, after the legal lineup is locked.
                points = sum(float(week['actuals'][identity(p)]) for p in selected)
                weekly.append({'points': points, 'lineup': [identity(p) for p in selected]})
            rows.append({'policy': policy, 'pick': identity(chosen),
                         'actual_points': sum(w['points'] for w in weekly), 'weeks': weekly})
        results.append({'id': case['id'], 'policies': rows})
    summary = {p: {'mean_actual_points': statistics.mean(next(r['actual_points'] for r in case['policies'] if r['policy'] == p) for case in results)} for p in policies}
    return {'schema_version': 1, 'case_count': len(results), 'results': results, 'summary': summary,
            'scope': 'Fixed-roster one-pick comparisons; not full-draft counterfactuals or win probabilities.',
            'limitations': ['Held-out designation is supplied by the evaluator; data independence needs external audit.',
                           'No claim of superiority follows from synthetic fixtures or a small selected sample.',
                           'Availability, forecasts and replacement behavior are only as good as supplied snapshots.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    report = evaluate(json.loads(Path(args.cases).read_text()))
    Path(args.out).write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
