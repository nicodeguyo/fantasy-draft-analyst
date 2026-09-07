"""Exercise the distributed artifact from an unrelated directory."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]

class PackageTests(unittest.TestCase):
    def test_download_runs_without_repository_and_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            archive = base / 'skill.zip'
            subprocess.run([sys.executable, str(ROOT/'scripts/package.py'), '--out', str(archive)], check=True, capture_output=True)
            first = archive.read_bytes()
            subprocess.run([sys.executable, str(ROOT/'scripts/package.py'), '--out', str(archive)], check=True, capture_output=True)
            self.assertEqual(hashlib.sha256(first).digest(), hashlib.sha256(archive.read_bytes()).digest())
            with zipfile.ZipFile(archive) as z:
                self.assertIsNone(z.testzip())
                self.assertTrue(all(n.startswith('fantasy-draft-analyst/') and '..' not in Path(n).parts for n in z.namelist()))
                z.extractall(base/'installed')
            scripts = base/'installed/fantasy-draft-analyst/scripts'
            env = {k:v for k,v in os.environ.items() if k != 'PYTHONPATH'}
            for script in ('draft_sim.py', 'build_board.py', 'prepare_data.py', 'live_draft.py'):
                result = subprocess.run([sys.executable, str(scripts/script), '--help'], cwd=base, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            # Exercise the shipped evidence and live CLI from an unrelated directory.
            assets = scripts.parent/'assets'
            def run(script, *args):
                result = subprocess.run([sys.executable, str(scripts/script), *map(str,args)], cwd=base, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                return result
            prepared = base/'players.csv'
            run('prepare_data.py', '--league', assets/'example-evidence-league.json', '--snapshot', assets/'example-evidence.json', '--as-of', '2026-09-06T12:00:00Z', '--out', prepared)
            report = json.loads(prepared.with_suffix('.evidence.json').read_text())
            self.assertEqual(report['mode'], 'full')
            cfg = {'league':{'teams':2,'rounds':2,'draft_slot':1,'draft_type':'snake'},'roster':{'QB':0,'RB':1,'WR':0,'TE':0,'FLEX':0,'K':0,'DEF':0,'bench':1},'keepers':{'count':0}}
            league = base/'league.json'; league.write_text(json.dumps(cfg))
            import csv
            with prepared.open() as stream:
                row = next(csv.DictReader(stream))
            # Expand the synthetic observation to a fictional four-player draft.
            players = []
            for i in range(4):
                player = dict(row, player_id=f'fiction:{i}', name=f'Fictional Runner {i}', adp=i+1, proj=float(row['proj'])-i*10)
                players.append(player)
            pool = base/'pool.json';pool.write_text(json.dumps(players))
            session = base/'session.json'
            run('live_draft.py', '--session', session, 'init', '--league', league, '--players', pool)
            run('live_draft.py', '--session', session, 'pick', 'Fictional Runner 0')
            rec = json.loads(run('live_draft.py', '--session', session, 'recommend').stdout)
            self.assertNotIn('fiction:0', [p['player_id'] for p in rec['candidates']])
            run('live_draft.py', '--session', session, 'undo')
            saved = json.loads(session.read_text())
            self.assertTrue(saved['receipts'])
            # Imports must resolve solely through the installed script location.
            code = 'import sys; sys.path.insert(0,sys.argv[1]); import fantasy_core.evidence, fantasy_core.roster_value, fantasy_core.session'
            result = subprocess.run([sys.executable, '-c', code, str(scripts)], cwd=base, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

if __name__ == '__main__':
    unittest.main()
