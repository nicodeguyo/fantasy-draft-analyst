"""Policy fidelity and actual draft legality, independent of headline performance."""
import json
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/fantasy-draft-analyst/scripts'
sys.path.insert(0, str(SCRIPTS))
import board_policy as bp
import draft_sim as ds
import build_board as render


class PickRows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.pick = None
        self.rows = {}
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section':
            self.pick = None
        if tag == 'div' and 'data-pick' in attrs:
            self.pick = int(attrs['data-pick'])
            self.rows[self.pick] = []
        if tag == 'tr' and self.pick is not None and 'data-name' in attrs:
            self.rows[self.pick].append(attrs['data-name'])


class BoardPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = ROOT / 'examples/sample-league'
        cls.sim = json.loads((cls.sample/'sim.json').read_text())
        cls.notes = json.loads((cls.sample/'notes.json').read_text())
        cls.players = render.load_players(cls.sample/'players.csv')

    def test_all_rendered_picks_match_executable_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/'board.html'
            subprocess.run([sys.executable, str(SCRIPTS/'build_board.py'),
                            '--league', str(self.sample/'league.yaml'), '--sim', str(self.sample/'sim.json'),
                            '--players', str(self.sample/'players.csv'), '--notes', str(self.sample/'notes.json'),
                            '--out', str(out)], check=True, capture_output=True)
            parser = PickRows()
            parser.feed(out.read_text())
            self.assertEqual(set(parser.rows), {int(r['pick']) for r in self.sim['ladder']})
            for pk, rows in parser.rows.items():
                top, more, target = bp.row_groups(self.sim, self.notes, self.players, pk)
                self.assertEqual(rows, [r['name'] for r in top+more])
                if target:
                    self.assertEqual(rows[0], target)

    def test_evaluated_target_overrides_stale_notes_and_late_target_is_used(self):
        data = {'replacement': {'RB': 0}, 'plan_path': [{'pick': 1, 'player': 'real'}],
                'pick_values': {'1': [{'name': 'raw', 'pos': 'RB', 'value': 20},
                                      {'name': 'real', 'pos': 'RB', 'value': 19}]}}
        players = {n: {'pos': 'RB', 'proj': 1, 'adp': 1} for n in ('raw', 'real', 'late')}
        notes = {'plan': [{'pick': 1, 'player': 'raw'}, {'pick': 99, 'player': 'late'}]}
        self.assertEqual(bp.row_groups(data, notes, players, 1)[0][0]['name'], 'real')
        self.assertEqual(bp.row_groups(data, notes, players, 99)[0][0]['name'], 'late')

    def test_fallback_respects_caps_avoid_and_final_starting_slot(self):
        wr = {'name': 'WR', 'pos': 'WR'}
        qb = {'name': 'QB', 'pos': 'QB'}
        k = {'name': 'K', 'pos': 'K'}
        caps = {'WR': 2, 'QB': 1, 'K': 1}
        choice = bp.choose_player(['WR', 'QB'], ['K'], [wr,qb,k], [qb],
                                  {'QB': 1, 'K': 1}, caps, set(), 1)
        self.assertEqual(choice, k)
        with self.assertRaises(ValueError):
            bp.choose_player(['WR'], ['K'], [wr,k], [qb], {'QB':1, 'K':1}, caps, {'K'}, 1)

    def test_flex_and_superflex_completion(self):
        roster = [{'pos': p} for p in ('QB','RB','RB','WR','TE','QB')]
        self.assertEqual(bp.filled_slots(roster, {'QB':1,'RB':1,'WR':1,'TE':1,'FLEX':1,'SUPERFLEX':1}),6)

    def test_held_out_policy_completes_rosters_and_uses_saved_choices(self):
        cfg = ds.load_league(self.sample/'league.yaml')
        pool = ds.load_players(self.sample/'players.csv')
        engine = ds.Sim(cfg, pool, self.sim['league'].get('keeper'), self.sim['league'].get('keeper_round'))
        board = {}
        for row in self.sim['ladder']:
            pk = int(row['pick'])
            top, more, _ = bp.row_groups(self.sim,self.notes,self.players,pk)
            board[pk] = [r['name'] for r in top+more]
        fallback = bp.fallback_order(self.sim,self.players)
        for seed in (991001,991002,991003,991004,991005):
            for baseline in (False, True):
                picks, roster, total, lineup = bp.run_board(engine, seed, board, fallback, adp_baseline=baseline)
                self.assertEqual(len(roster), engine.rounds)
                self.assertEqual(len({p['name'] for p in roster}), len(roster))
                self.assertEqual(bp.filled_slots(roster, engine.starters), sum(engine.starters.values()))
                self.assertEqual(total, engine.lineup_pts(roster)[0])

if __name__ == '__main__':
    unittest.main()
