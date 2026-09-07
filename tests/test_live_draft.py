"""Public CLI and HTTP regressions for recoverable, current-state draft advice."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.request import Request,urlopen
from urllib.error import HTTPError

SCRIPTS=Path(__file__).resolve().parents[1]/'skills/fantasy-draft-analyst/scripts'
sys.path.insert(0,str(SCRIPTS))
import live_draft
from fantasy_core import session


def fixture():
    cfg={'league':{'teams':2,'rounds':5,'draft_slot':1,'draft_type':'snake'},
         'roster':{'QB':1,'RB':1,'WR':1,'TE':0,'FLEX':0,'K':0,'DEF':0,'bench':2},'keepers':{'count':0}}
    pool=[{'player_id':str(i),'name':f'Player {i}','pos':pos,'proj':200-i*3,'adp':i+1,'sd':4} for i,pos in enumerate(['RB','WR','QB','RB','WR','QB','RB','WR','QB','RB','WR','TE'])]
    return cfg,pool

class SessionTests(unittest.TestCase):
    def setUp(self):
        self.cfg,self.pool=fixture();self.s=session.create(self.cfg,self.pool)
    def test_keeper_unavailable_before_consumed_once(self):
        self.cfg['keepers']={'count':1,'league_keeper_list':[{'draft_slot':2,'round':3,'player':'Player 0'}]}
        s=session.create(self.cfg,self.pool)
        self.assertEqual(session.replay(s)['picks'][0]['pick'],6)
        self.assertNotIn('0',[p['player_id'] for p in session.available(s)])
        self.assertEqual(session.replay(s)['current_pick'],1)
        with self.assertRaises(ValueError):session.record_pick(s,'Player 0')
    def test_unknown_idempotency_undo_and_refresh(self):
        session.record_pick(self.s,'Unknown incoming rookie',event_id='same')
        session.record_pick(self.s,'Unknown incoming rookie',event_id='same')
        self.assertEqual(session.replay(self.s)['current_pick'],2)
        old=copy.deepcopy(session.replay(self.s))
        session.refresh(self.s,self.pool[1:])
        self.assertEqual(session.replay(self.s),old)
        session.undo(self.s)
        self.assertEqual(session.replay(self.s)['current_pick'],1)
        self.assertEqual(len(self.s['receipts']),1)
    def test_stale_receipt_and_available_explanation(self):
        rec=live_draft.recommend(self.s)
        session.record_pick(self.s,'Player 0',recommendation=rec)
        with self.assertRaises(ValueError):session.record_pick(self.s,'Player 1',recommendation=rec)
        fresh=live_draft.recommend(self.s)
        self.assertNotIn('0',[c['player_id'] for c in fresh['candidates']])
        self.assertIn('not supported',live_draft.validate_explanation(self.s,['0'],'Draft Player 0'))
        self.assertEqual(self.s['receipts'][0]['recommendation'],rec)
    def test_import_atomic_duplicate_and_conflict(self):
        rows=[{'pick':1,'name':'Player 0'},{'pick':2,'name':'Unknown'}]
        live_draft.import_picks(self.s,rows)
        live_draft.import_picks(self.s,rows)
        self.assertEqual(len(session.replay(self.s)['picks']),2)
        before=copy.deepcopy(self.s)
        with self.assertRaises(ValueError):live_draft.import_picks(self.s,[{'pick':3,'name':'Player 2'},{'pick':1,'name':'Player 3'}])
        self.assertEqual(self.s,before)
    def test_unknown_resolution_preserves_slot_and_blocks_duplicate(self):
        session.record_pick(self.s,'Unmatched player')
        session.record_pick(self.s,'Player 1')
        with self.assertRaises(ValueError):session.resolve_unknown(self.s,1,'Player 1')
        session.resolve_unknown(self.s,1,'Player 0')
        picks=session.replay(self.s)['picks']
        self.assertEqual(picks[0]['pick'],1)
        self.assertEqual(picks[0]['player_id'],'0')
        self.assertFalse(picks[0]['unknown'])
        self.assertEqual(session.replay(self.s)['current_pick'],3)
        self.assertNotIn('0',[p['player_id'] for p in session.available(self.s)])

    def test_raw_refresh_cannot_inherit_old_source_provenance(self):
        self.s['evidence']={'mode':'full','players':[{'player_id':'0','source':'oldsource'}]}
        old=self.s['data_revision']
        session.record_pick(self.s,'Player 0')
        session.refresh(self.s,self.pool[1:])
        self.assertEqual(self.s['evidence']['mode'],'limited')
        self.assertNotIn('players',self.s['evidence'])
        self.assertEqual(self.s['snapshots'][old]['evidence']['mode'],'full')
        self.assertEqual(next(p for p in self.s['players'] if p['player_id']=='0')['evidence_mode'],'retained_stale')
        self.assertTrue(any('stale' in w for w in self.s['evidence']['warnings']))

    def test_rank_only_has_no_fake_point_delta(self):
        self.s['players'][0]['proj']=None
        rec=live_draft.recommend(self.s)
        self.assertEqual(rec['mode'],'rank_only')
        self.assertTrue(all('policy_score' not in p for p in rec['candidates']))
    def test_interprocess_writer_lock_prevents_lost_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'session.json';session.save(self.s,path)
            command=[sys.executable,str(SCRIPTS/'live_draft.py'),'--session',str(path),'pick','Player 0']
            with session.mutation_lock(path):
                staged=session.load(path)
                rival=subprocess.run(command,text=True,capture_output=True)
                self.assertEqual(rival.returncode,2)
                self.assertIn('busy in another writer',rival.stderr)
                session.record_pick(staged,'Player 1')
                session.save(staged,path)
            retry=subprocess.run(command,text=True,capture_output=True)
            self.assertEqual(retry.returncode,0,retry.stderr)
            picks=session.replay(session.load(path))['picks']
            self.assertEqual([(p['pick'],p['player_id']) for p in picks],[(1,'1'),(2,'0')])

    def test_prepared_source_outage_preserves_identity_and_valid_price(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            evidence=json.loads((SCRIPTS.parent/'assets/example-evidence.json').read_text())
            evidence['players'][0]['projections']=[]
            snapshot=root/'evidence.json';snapshot.write_text(json.dumps(evidence))
            output=root/'players.csv'
            result=subprocess.run([sys.executable,str(SCRIPTS/'prepare_data.py'),'--league',str(SCRIPTS.parent/'assets/example-evidence-league.json'),
                '--snapshot',str(snapshot),'--out',str(output),'--as-of','2026-09-06T12:00:00Z'],text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            players,report=live_draft.read_pool(output,self.cfg)
            self.assertEqual(len(players),1)
            self.assertEqual(players[0]['player_id'],'example:rb1')
            self.assertIsNone(players[0]['proj'])
            self.assertEqual(players[0]['adp'],24.5)
            rec=live_draft.recommend(session.create(self.cfg,players,report))
            self.assertEqual(rec['mode'],'rank_only')
            self.assertEqual(rec['candidates'][0]['player_id'],'example:rb1')
            self.assertNotIn('policy_score',rec['candidates'][0])

    def test_cli_resume_refresh_and_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);cfg=root/'league.json';pool=root/'pool.json';saved=root/'session.json'
            cfg.write_text(json.dumps(self.cfg));pool.write_text(json.dumps(self.pool))
            def run(*args):
                p=subprocess.run([sys.executable,str(SCRIPTS/'live_draft.py'),'--session',str(saved),*args],text=True,capture_output=True)
                self.assertEqual(p.returncode,0,p.stderr);return json.loads(p.stdout)
            run('init','--league',str(cfg),'--players',str(pool))
            run('pick','Player 0','--event-id','first')
            run('refresh','--players',str(pool))
            self.assertEqual(run('export')['events'][0]['payload']['player_id'],'0')
            self.assertNotIn('0',[p['player_id'] for p in run('recommend')['candidates']])
            run('undo')
            self.assertEqual(session.replay(session.load(saved))['current_pick'],1)
    def test_http_updates_shared_policy_and_rejects_remote_origin_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'session.json';session.save(self.s,path)
            server=live_draft.make_server(path,0)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            base=f'http://127.0.0.1:{server.server_port}'
            try:
                with urlopen(base+'/api/state') as r: before=json.load(r)
                self.assertEqual(before['recommendation'],live_draft.recommend(session.load(path)))
                payload={'player':'Player 0','event_id':'http','state_token':before['recommendation']['state_token']}
                def post(origin):return urlopen(Request(base+'/api/pick',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Origin':origin}))
                with self.assertRaises(HTTPError) as exc:post('https://evil.example')
                self.assertEqual(exc.exception.code,403);exc.exception.close()
                with post(base) as r:self.assertEqual(r.status,200)
                with self.assertRaises(HTTPError) as exc:post(base)
                self.assertEqual(exc.exception.code,409);exc.exception.close()
                with urlopen(base+'/api/state') as r:after=json.load(r)
                self.assertEqual(after['current_pick'],2)
                self.assertNotEqual(before['recommendation']['state_token'],after['recommendation']['state_token'])
                self.assertNotIn('0',[p['player_id'] for p in after['recommendation']['candidates']])
            finally:server.shutdown();server.server_close();thread.join()

if __name__=='__main__':unittest.main()
