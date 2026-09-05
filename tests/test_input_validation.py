"""Fail before expensive simulation when inputs cannot describe a supported draft."""
import copy
import csv
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / 'examples/sample-league'
SCRIPT = ROOT / 'skills/fantasy-draft-analyst/scripts/draft_sim.py'
SPEC = importlib.util.spec_from_file_location('input_test_sim', SCRIPT)
DS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DS)


class InputValidationTests(unittest.TestCase):
    def load_rows(self, rows):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'players.csv'
            with p.open('w') as fh:
                writer = csv.DictWriter(fh, fieldnames=['name', 'pos', 'adp', 'adp_sd', 'proj'])
                writer.writeheader()
                writer.writerows(rows)
            return DS.load_players(str(p))

    def test_duplicate_trimmed_player_names_rejected(self):
        rows = [dict(name=' Player A ', pos='RB', adp=1, adp_sd=4, proj=300),
                dict(name='Player A', pos='WR', adp=2, adp_sd=4, proj=290)]
        with self.assertRaisesRegex(ValueError, '[Dd]uplicate'):
            self.load_rows(rows)

    def test_nonfinite_numeric_inputs_rejected(self):
        for field in ('adp', 'adp_sd', 'proj'):
            for value in ('NaN', 'inf', '-inf'):
                with self.subTest(field=field, value=value):
                    row = dict(name='Player A', pos='RB', adp=1, adp_sd=4, proj=300)
                    row[field] = value
                    with self.assertRaisesRegex(ValueError, 'finite'):
                        self.load_rows([row])

    def test_invalid_player_position_and_adp_rejected(self):
        for field, value in [('pos', 'OL'), ('adp', 0), ('adp_sd', -1)]:
            with self.subTest(field=field):
                row = dict(name='Player A', pos='RB', adp=1, adp_sd=4, proj=300)
                row[field] = value
                with self.assertRaises(ValueError):
                    self.load_rows([row])

    def test_nonpositive_simulation_counts_rejected_before_loading_files(self):
        for flag in ('--sims', '--rollouts'):
            for value in ('0', '-1'):
                with self.subTest(flag=flag, value=value), tempfile.TemporaryDirectory() as tmp:
                    out = Path(tmp) / 'sim.json'
                    proc = subprocess.run([sys.executable, str(SCRIPT), '--league', '/nonexistent-league.json',
                        '--players', '/nonexistent-players.csv', flag, value, '--out', str(out)],
                        capture_output=True, text=True)
                    self.assertEqual(proc.returncode, 2)
                    self.assertIn(flag + ' must be positive', proc.stderr)
                    self.assertNotIn('Traceback', proc.stderr)
                    self.assertFalse(out.exists())

    def test_impossible_starter_or_draft_capacity_rejected(self):
        base = DS.load_league(str(SAMPLE / 'league.yaml'))
        pool = DS.load_players(str(SAMPLE / 'players.csv'))
        mutations = [('roster', 'TE', 3), ('roster', 'RB', -1), ('league', 'rounds', 8),
                     ('league', 'rounds', 25), ('league', 'teams', 0), ('roster', 'FLEX', 20)]
        for section, key, value in mutations:
            with self.subTest(section=section, key=key, value=value):
                cfg = copy.deepcopy(base)
                cfg[section][key] = value
                with self.assertRaisesRegex(ValueError, 'roster|rounds|teams|starter|capacity'):
                    DS.Sim(cfg, copy.deepcopy(pool), None, None)

    def test_standard_sample_remains_supported(self):
        cfg = DS.load_league(str(SAMPLE / 'league.yaml'))
        pool = DS.load_players(str(SAMPLE / 'players.csv'))
        self.assertEqual(DS.Sim(cfg, pool, 'Chase Brown', 6).rounds, 15)

if __name__ == '__main__':
    unittest.main()
