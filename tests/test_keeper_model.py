"""Keeper ownership, draft accounting and selection regression checks."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / 'examples/sample-league'
SPEC = importlib.util.spec_from_file_location('keeper_test_sim', ROOT / 'skills/fantasy-draft-analyst/scripts/draft_sim.py')
DS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DS)


class KeeperModelTests(unittest.TestCase):
    def setUp(self):
        self.cfg = DS.load_league(str(SAMPLE / 'league.yaml'))
        self.pool = DS.load_players(str(SAMPLE / 'players.csv'))

    def sim(self, keeper='Chase Brown', rnd=6):
        return DS.Sim(self.cfg, copy.deepcopy(self.pool), keeper, rnd)

    def test_random_keepers_have_owners_and_each_consume_one_pick(self):
        sim = self.sim()
        for seed in range(30):
            st = sim.start(seed)
            kept_names = {p['name'] for roster in st['rosters'].values() for p in roster}
            self.assertEqual(len(kept_names), sim.teams)
            self.assertEqual({len(r) for r in st['rosters'].values()}, {1})
            self.assertFalse(kept_names & {p['name'] for p in st['avail']})
            self.assertEqual(len(st['order']), sim.teams * (sim.rounds - 1))
            for slot in range(1, sim.teams + 1):
                self.assertEqual(sum(t == slot for _, _, t in st['order']), sim.rounds - 1)
            sim.play(st)
            self.assertEqual({len(r) for r in st['rosters'].values()}, {sim.rounds})
            drafted = [p['name'] for r in st['rosters'].values() for p in r]
            self.assertEqual(len(drafted), len(set(drafted)))

    def test_published_ownership_uses_slots_not_list_order(self):
        self.cfg['keepers']['league_keeper_list'] = [
            {'team': 'Last in list', 'draft_slot': 12, 'player': 'Lamar Jackson', 'round': 3},
            {'team': 'First slot', 'draft_slot': 1, 'player': 'Bijan Robinson', 'round': 1},
        ]
        sim = self.sim()
        st = sim.start(42)
        self.assertEqual(st['rosters'][12][0]['name'], 'Lamar Jackson')
        self.assertEqual(st['rosters'][1][0]['name'], 'Bijan Robinson')
        self.assertNotIn((DS.pick_number(3, 12, sim.teams, True), 3, 12), st['order'])
        self.cfg['keepers']['league_keeper_list'].reverse()
        other = self.sim().start(42)
        self.assertEqual(st['order'], other['order'])
        self.assertEqual(st['rosters'], other['rosters'])

    def test_own_published_keeper_released_in_alternative_scenarios(self):
        self.cfg['keepers']['league_keeper_list'] = [
            {'draft_slot': self.cfg['league']['draft_slot'], 'player': 'Chase Brown', 'round': 6}]
        st = self.sim(None, None).start(1)
        self.assertIn('Chase Brown', {p['name'] for p in st['avail']})
        self.assertFalse(st['rosters'])
        self.assertEqual(len(st['order']), self.cfg['league']['teams'] * self.cfg['league']['rounds'])

    def test_invalid_keeper_accounting_fails_early(self):
        valid = {'draft_slot': 1, 'player': 'Bijan Robinson', 'round': 1}
        bad_lists = [
            [{'team': 'Missing slot', 'player': 'Bijan Robinson', 'round': 1}],
            [valid, dict(valid, player='Lamar Jackson')],
            [valid, dict(valid, draft_slot=2)],
            [dict(valid, round=0)], [dict(valid, round=99)],
            [dict(valid, player='Missing player')],
            [dict(valid, player='Chase Brown')],
        ]
        for entries in bad_lists:
            with self.subTest(entries=entries):
                self.cfg['keepers']['league_keeper_list'] = entries
                with self.assertRaises(ValueError):
                    self.sim()
        self.cfg['keepers']['league_keeper_list'] = []
        self.cfg['keepers']['count'] = 2
        with self.assertRaisesRegex(ValueError, 'multi-keeper'):
            self.sim()
        self.cfg['keepers']['count'] = 1
        with self.assertRaisesRegex(ValueError, 'cost round'):
            self.sim(rnd=None)

    def test_opponent_picker_receives_the_keeper_on_its_roster(self):
        self.cfg['keepers']['league_keeper_list'] = [
            {'draft_slot': 1, 'player': 'Lamar Jackson', 'round': 3}]
        sim = self.sim()
        st = sim.start(0)
        original = sim.opp_pick
        seen = []
        def spy(avail, roster, rnd, rng):
            seen.append([p['name'] for p in roster])
            return original(avail, roster, rnd, rng)
        with patch.object(sim, 'opp_pick', side_effect=spy):
            sim.play(st, stop_at=2)
        self.assertEqual(seen[0], ['Lamar Jackson'])

    def test_scenario_winner_is_selected_before_building_board_and_overrides_win(self):
        def scenario(cfg, pool, keeper, rnd, sims, seed):
            # Deliberately prefer a keeper different from the isolated-surplus winner.
            return {'keeper': keeper, 'keeper_round': rnd, 'mean': 3000 if keeper == 'Drake London' else 1000,
                    'se': 1, 'sims': sims, 'min': 999, 'max': 3001}
        for override, expected, rnd in [([], 'Drake London', 2), (['--no-keeper'], None, None),
                                       (['--keeper', 'Chase Brown'], 'Chase Brown', 6)]:
            with self.subTest(override=override), tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / 'sim.json'
                argv = ['draft_sim.py', '--league', str(SAMPLE/'league.yaml'), '--players', str(SAMPLE/'players.csv'),
                        '--sims', '2', '--samples', '1', '--no-pick-values', '--keeper-scenarios', 'Drake London,Chase Brown',
                        '--out', str(out), *override]
                with patch.object(sys, 'argv', argv), patch.object(DS, 'scenario_totals', side_effect=scenario), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    DS.main()
                result = json.loads(out.read_text())
                self.assertEqual(result['league']['keeper'], expected)
                self.assertEqual(result['league']['keeper_round'], rnd)
                self.assertEqual(len(result['ladder']), 15 - bool(expected))
                if rnd:
                    self.assertNotIn(rnd, [r['round'] for r in result['ladder']])
                self.assertIn('keeper_selection', result['settings'])

if __name__ == '__main__':
    unittest.main()
