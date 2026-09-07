"""Rendered v2 utility must not be confused with starter point totals or old notes."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / 'examples/sample-league'
RENDER = ROOT / 'skills/fantasy-draft-analyst/scripts/build_board.py'


class BoardMetricTests(unittest.TestCase):
    def render(self, v2):
        sim = json.loads((SAMPLE / 'sim.json').read_text())
        notes = json.loads((SAMPLE / 'notes.json').read_text())
        sim.setdefault('settings', {})['draft_policy'] = 'roster_v2' if v2 else 'legacy'
        sim['roster_utility'] = {'mean': 2222, 'assumptions': ['Synthetic utility fixture']}
        sim['totals']['mean'] = 1111
        notes['plan_total_label'] = 'STALE POINTS HEADER'
        # A legacy note's numeric value may not masquerade as v2 output.
        first = sim['plan_path'][0]
        notes['plan'] = [{'pick': first['pick'], 'player': first['player'], 'value': 9876543}]
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base/'sim.json').write_text(json.dumps(sim))
            (base/'notes.json').write_text(json.dumps(notes))
            command = [sys.executable, str(RENDER), '--league', str(SAMPLE/'league.yaml'),
                       '--players', str(SAMPLE/'players.csv'), '--sim', str(base/'sim.json'),
                       '--notes', str(base/'notes.json'), '--out', str(base/'board.html')]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return (base/'board.html').read_text()

    def test_v2_separates_objective_from_points(self):
        page = self.render(True)
        self.assertIn('2,222 average roster utility across simulated drafts', page)
        self.assertIn('1,111 average projected starter points', page)
        self.assertIn('Preparation mode · roster utility', page)
        self.assertNotIn('STALE POINTS HEADER', page)
        self.assertNotIn('Projected final starting lineup', page)
        self.assertNotIn('9,876,543', page)

    def test_legacy_keeps_original_metric(self):
        page = self.render(False)
        self.assertIn('STALE POINTS HEADER', page)
        self.assertNotIn('Preparation mode · roster utility', page)
        self.assertIn('Projected final starting lineup', page)
        self.assertIn('9,876,543', page)


if __name__ == '__main__':
    unittest.main()
