"""Behavioral checks for legal depth coverage and uncertainty separation."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/fantasy-draft-analyst/scripts'))
from fantasy_core.roster_value import lineup, roster_value
from draft_sim import Sim


def player(name, pos, proj, **kw):
    return dict(name=name, pos=pos, proj=proj, adp=100, sd=10, **kw)


def config(**slots):
    roster = dict(QB=0, RB=0, WR=0, TE=0, K=0, DEF=0, FLEX=0, SUPERFLEX=0)
    roster.update(slots)
    return dict(roster=roster, league=dict(teams=2, rounds=14, draft_slot=1),
                valuation=dict(horizon_games=10, assumed_missed_games=2), keepers=dict(count=0))


class RosterValueTests(unittest.TestCase):
    def test_one_player_cannot_fill_two_slots(self):
        cfg = config(RB=1, FLEX=1, SUPERFLEX=1)
        total, selected = lineup([player('A', 'RB', 100), player('B', 'QB', 90)], cfg)
        self.assertEqual(total, 190)
        self.assertEqual(len(selected), 2)
        with self.assertRaises(ValueError):
            lineup([player('A', 'RB', 100), player('A', 'RB', 100)], cfg)

    def test_two_absent_rbs_one_backup_only_fills_once(self):
        cfg = config(RB=2)
        cfg['valuation'].update(weeks=[5], overlap_share=0)
        roster = [player('A', 'RB', 100, expected_games=9, bye=5),
                  player('B', 'RB', 90, expected_games=9, bye=5),
                  player('C', 'RB', 80, expected_games=10)]
        value = roster_value(roster, cfg, {'RB': 0})
        self.assertAlmostEqual(value['coverage_points'], 8)
        self.assertEqual(value['starter_points'], 190)

    def test_duplicate_or_invalid_weeks_cannot_inflate_bye_coverage(self):
        cfg = config(RB=1)
        cfg['valuation'].update(weeks=[5], overlap_share=0)
        roster = [player('Starter', 'RB', 100, expected_games=9, bye=5),
                  player('Reserve', 'RB', 80, expected_games=10)]
        self.assertEqual(roster_value(roster, cfg, {'RB': 0})['coverage_points'], 8)
        for weeks in ([5, 5], [0], [19], [True], ['5'], '5', None):
            with self.subTest(weeks=weeks):
                cfg['valuation']['weeks'] = weeks
                with self.assertRaises(ValueError):
                    roster_value(roster, cfg, {'RB': 0})
        # Calendar length is configurable independently of projected games.
        cfg['league']['season_weeks'] = 20
        cfg['valuation']['weeks'] = [19]
        self.assertGreaterEqual(roster_value(roster, cfg, {'RB': 0})['coverage_points'], 0)

    def test_known_same_bye_backup_cannot_cover(self):
        cfg = config(RB=1)
        cfg['valuation'].update(weeks=[5], overlap_share=0)
        roster = [player('A', 'RB', 100, expected_games=9, bye=5),
                  player('B', 'RB', 80, expected_games=9, bye=5)]
        self.assertEqual(roster_value(roster, cfg, {'RB': 0})['coverage_points'], 0)

    def test_season_total_not_double_discounted(self):
        cfg = config(RB=1)
        value = roster_value([player('A', 'RB', 100, expected_games=5)], cfg)
        self.assertEqual(value['starter_points'], 100)
        self.assertEqual(value['coverage_points'], 0)
        full = roster_value([player('A', 'RB', 100, expected_games=5,
                                    projection_convention='full_season')], cfg)
        self.assertEqual(full['starter_points'], 50)
        per_game = roster_value([player('A', 'RB', 20, expected_games=5,
                                        projection_convention='per_game')], cfg)
        self.assertEqual(per_game['starter_points'], 100)

    def test_fully_out_player_zero_games_is_valid_but_not_recommended(self):
        cfg = config(RB=1)
        out = player('Out', 'RB', 0, expected_games=0, performance_sd=100)
        good = player('Healthy', 'RB', 100)
        sim = Sim(cfg, [out, good], None, None)
        self.assertEqual(roster_value([out], cfg)['total'], 0)
        self.assertEqual([p['name'] for _, p in sim.pick_scores(sim.pool, [], 10)], ['Healthy'])
        with self.assertRaises(ValueError):
            roster_value([player('Invalid', 'RB', 100, expected_games=0)], cfg)
        converted = Sim(cfg, [player('Full health', 'RB', 100, expected_games=0,
                                    projection_convention='full_season')], None, None)
        self.assertEqual(converted.pool[0]['proj'], 0)

    def test_fourth_rb_vs_seventh_wr_is_conditional(self):
        cfg = config(RB=2, WR=2, FLEX=2)
        roster = [player('RB1', 'RB', 200), player('RB2', 'RB', 160), player('RB3', 'RB', 110)]
        roster += [player(f'WR{i}', 'WR', points) for i, points in enumerate([220, 200, 180, 160, 120, 110])]
        repl = dict(RB=50, WR=50)
        rb = roster_value(roster + [player('RB4', 'RB', 100)], cfg, repl)['total']
        wr = roster_value(roster + [player('WR7', 'WR', 100)], cfg, repl)['total']
        self.assertGreater(rb, wr)
        elite_wr = roster_value(roster + [player('WR7', 'WR', 230)], cfg, repl)['total']
        self.assertGreater(elite_wr, rb)

    def test_adp_and_source_spread_do_not_create_upside(self):
        cfg = config(RB=1)
        roster = [player('A', 'RB', 100), player('B', 'RB', 80)]
        base = roster_value(roster, cfg)
        roster[1].update(sd=1000, projection_sd=1000)
        self.assertEqual(base, roster_value(roster, cfg))
        roster[1]['performance_sd'] = 30
        self.assertGreater(roster_value(roster, cfg)['upside_points'], 0)

    def test_live_and_terminal_use_same_objective(self):
        cfg = config(RB=1, WR=1)
        pool = [player('A', 'RB', 100), player('B', 'WR', 100), player('C', 'RB', 90)]
        sim = Sim(cfg, copy.deepcopy(pool), None, None)
        roster = sim.pool[:2]
        candidate = sim.pool[2]
        delta = sim.objective_pts(roster + [candidate], True) - sim.objective_pts(roster, True)
        score = sim.pick_scores([candidate], roster, 10)[0][0]
        self.assertAlmostEqual(score, delta)
        self.assertEqual(sim.roster_breakdown(roster)['policy'], 'roster_v2')
        cfg['preferences'] = dict(draft_policy='legacy')
        legacy = Sim(cfg, copy.deepcopy(pool), None, None)
        self.assertEqual(legacy.objective_pts(pool), legacy.lineup_pts(pool)[0])

    def test_risk_preference_uses_outcome_sigma_not_adp_or_source_spread(self):
        cfg = config(RB=1)
        cfg['preferences'] = dict(risk='aggressive')
        pool = [player('A', 'RB', 100), player('B', 'RB', 90)]
        sim = Sim(cfg, copy.deepcopy(pool), None, None)
        original = sim.pick_scores([sim.pool[1]], [sim.pool[0]], 10)[0][0]
        sim.pool[1].update(sd=9999, projection_sd=9999)
        self.assertEqual(original, sim.pick_scores([sim.pool[1]], [sim.pool[0]], 10)[0][0])
        # A new snapshot gets a new Sim; input dictionaries are immutable within a run.
        pool[1]['performance_sd'] = 20
        changed = Sim(cfg, copy.deepcopy(pool), None, None)
        self.assertGreater(changed.pick_scores([changed.pool[1]], [changed.pool[0]], 10)[0][0], original)

    def test_sim_normalizes_projection_units_before_replacement_and_reporting(self):
        cfg = config(RB=1)
        pool = [player('A', 'RB', 20, expected_games=5, projection_convention='per_game')]
        sim = Sim(cfg, pool, None, None)
        self.assertEqual(sim.pool[0]['proj'], 100)
        self.assertEqual(sim.lineup_pts(sim.pool)[0], 100)
        self.assertEqual(sim.objective_pts(sim.pool), 100)
        self.assertEqual(sim.repl['RB'], 100)

    def test_realized_weekly_outcomes_are_not_used(self):
        cfg = config(WR=1)
        roster = [player('A', 'WR', 100), player('B', 'WR', 90)]
        original = roster_value(roster, cfg)
        roster[1]['weekly_actual_points'] = [1000] * 10
        self.assertEqual(original, roster_value(roster, cfg))

class EvaluationTests(unittest.TestCase):
    def case(self):
        return {'schema_version': 1, 'split': 'held_out', 'cases': [{
            'id': 'synthetic-not-historical', 'snapshot_as_of': '2026-09-01T00:00:00Z',
            'decision_at': '2026-09-02T00:00:00Z', 'league': config(WR=1),
            'players': [player('A', 'WR', 100), player('B', 'WR', 90)],
            'roster': ['A'], 'available': ['B'], 'round': 10,
            'weeks': [{'as_of': '2026-09-03T00:00:00Z', 'lock_at': '2026-09-04T00:00:00Z',
                       'forecasts': {'A': 10, 'B': 9}, 'actuals': {'A': 1, 'B': 100}}]}]}

    def test_evaluation_does_not_select_hindsight_best(self):
        from evaluate_policy import evaluate
        result = evaluate(self.case())
        for policy in result['results'][0]['policies']:
            self.assertEqual(policy['actual_points'], 1)
            self.assertEqual(policy['weeks'][0]['lineup'], ['A'])

    def test_evaluation_rejects_post_lock_or_post_decision_inputs(self):
        from evaluate_policy import evaluate
        case = self.case()
        case['cases'][0]['weeks'][0]['as_of'] = '2026-09-05T00:00:00Z'
        with self.assertRaises(ValueError):
            evaluate(case)
        case = self.case()
        case['cases'][0]['snapshot_as_of'] = '2026-09-03T00:00:00Z'
        with self.assertRaises(ValueError):
            evaluate(case)


if __name__ == '__main__':
    unittest.main()
