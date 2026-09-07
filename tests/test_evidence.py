"""Synthetic evidence correctness; no current vendor datasets bundled."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/fantasy-draft-analyst/scripts'
sys.path.insert(0, str(SCRIPTS))
from fantasy_core.evidence import prepare_snapshot
from fantasy_core.identity import IdentityIndex
from fantasy_core.news import ledger, apply_adjustments
from fantasy_core.providers import espn_players, import_projection_csv, parse_projection_html
from scoring import score_row

NOW = '2026-09-06T12:00:00Z'
FIXTURE = ROOT / 'tests/fixtures/evidence/snapshot.json'


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads(FIXTURE.read_text())
        self.league = {'season':2026,'scoring':{'reception':0.5}}

    def prepare(self):
        return prepare_snapshot(self.snapshot,self.league,now=NOW)

    def test_rescores_each_source_before_blending_and_retains_disagreement(self):
        rows, report = self.prepare()
        self.assertEqual(report['mode'],'full')
        self.assertEqual(rows[0]['proj'],214.2)  # 204 and 224.4 half-PPR
        self.assertAlmostEqual(rows[0]['projection_sd'],10.2)
        self.assertEqual(len(report['players'][0]['accepted']),2)
        self.league['scoring']['reception']=1
        self.assertEqual(self.prepare()[0][0]['proj'],235.2)

    def test_missing_malformed_nonfinite_not_zero(self):
        for bad in ('',None,'potato','nan','inf'):
            self.setUp()
            self.snapshot['players'][0]['projections'][0]['stats']['rec']=bad
            rows,report=self.prepare()
            self.assertEqual(report['mode'],'limited')
            self.assertEqual(rows[0]['source_count'],1)
            self.assertTrue(report['players'][0]['rejected'])
        self.setUp()
        self.snapshot['players'][0]['projections'][0]['stats']['rec']=0
        self.assertEqual(self.prepare()[0][0]['source_count'],2)

    def test_stale_wrong_season_week_and_structural_misuse_quarantined(self):
        for field,value in [('season',2025),('period','week'),('updated_at','2026-01-01T00:00:00Z'),('structural_zeros',['rec'])]:
            self.setUp()
            self.snapshot['players'][0]['projections'][0][field]=value
            self.assertEqual(self.prepare()[0][0]['source_count'],1)

    def test_missing_sources_rank_only_has_no_fabricated_points(self):
        self.snapshot['players'][0]['projections']=[]
        rows,report=self.prepare()
        self.assertEqual(rows,[])
        self.assertEqual(report['mode'],'rank-only')
        self.assertFalse(report['engine_eligible'])

    def test_unknown_publication_fresh_fetch_is_not_full_evidence(self):
        for record in self.snapshot['players'][0]['projections']:
            record['updated_at']=None
        self.assertEqual(self.prepare()[1]['mode'],'limited')

    def test_overlap_consensus_counts_as_one_group(self):
        self.snapshot['players'][0]['projections'][1]['constituents']=['example-a','example-c']
        self.assertEqual(self.prepare()[0][0]['independent_sources'],1)

    def test_wrong_format_or_ranking_is_not_draft_price(self):
        for field,value in [('kind','ecr'),('format','best-ball'),('season',2025),('value',0)]:
            self.setUp()
            self.snapshot['players'][0]['adp'][field]=value
            self.assertEqual(self.prepare()[0],[])

    def test_ambiguous_alias_quarantined_not_merged(self):
        other=copy.deepcopy(self.snapshot['players'][0]);other['player_id']='example:rb2'
        index=IdentityIndex([self.snapshot['players'][0],other])
        self.assertEqual(index.resolve(name='Example Runner'),(None,'ambiguous'))
        self.assertEqual(index.resolve(player_id='example:rb1')[1],'matched')

    def test_weekly_snapshot_not_eligible_for_season_engine(self):
        self.snapshot['period']='week';self.snapshot['week']=1
        for record in self.snapshot['players'][0]['projections']:
            record['period']='week';record['week']=1
        self.assertFalse(self.prepare()[1]['engine_eligible'])

    def test_adjustment_cannot_double_count_injury(self):
        adj={'adjustment_id':'a','event_id':'injury','assumption':'games','reason':'confirmed absence','base_includes_event':False,'points_delta':-10}
        with self.assertRaisesRegex(ValueError,'double count'):
            apply_adjustments(200,[adj],[{'incorporated_events':['injury']}])
        with self.assertRaisesRegex(ValueError,'double count'):
            apply_adjustments(200,[adj,adj],[])

    def test_news_syndication_and_confirmed_return_supersede(self):
        event={'event_id':'a','player_id':'rb1','type':'injury','original_source':'team','url':'https://example.com/a','event_at':'2026-09-04T12:00:00Z','published_at':'2026-09-04T13:00:00Z','quality':'confirmed'}
        syndicated=dict(event,event_id='b')
        self.assertEqual(len(ledger([event,syndicated],NOW)['active']),1)
        returned=dict(event,event_id='c',type='return',published_at='2026-09-05T12:00:00Z',supersedes=['a'])
        self.assertEqual(ledger([event,returned],NOW)['inactive_ids'],['a'])
        returned['quality']='speculative'
        self.assertEqual(len(ledger([event,returned],NOW)['active']),2)

    def test_csv_explicit_stat_mapping_and_unknown_identity_audit(self):
        columns={'name':'Player','rush_yd':'Rushing Yards','rush_td':'Rushing TD','rec':'Receptions','rec_yd':'Receiving Yards','rec_td':'Receiving TD','fum':'Fumbles Lost','two_pt':'Two Points'}
        additions,audit=import_projection_csv((FIXTURE.parent/'projections.csv').read_text(),source='fantasypros',independence_group='consensus',season=2026,period='season',fetched_at=NOW,updated_at=NOW,url='https://example.com',registry=self.snapshot['players'],column_map=columns)
        self.assertEqual(additions['example:rb1']['stats']['rec'],'40')
        self.assertEqual(audit['quarantine'][0]['status'],'unknown')

    def test_espn_selects_projection_season_and_preserves_missing(self):
        data={'players':[{'player':{'id':12,'fullName':'Runner','defaultPositionId':2,'ownership':{'averageDraftPosition':23},'stats':[{'seasonId':2025,'statSourceId':1,'statSplitTypeId':0,'stats':{'53':80}},{'seasonId':2026,'statSourceId':1,'statSplitTypeId':0,'stats':{'53':40,'24':1000}}]}}]}
        player=espn_players(data,2026,NOW)[0]
        self.assertEqual(player['projections'][0]['stats']['rec'],40)
        self.assertNotIn('fum',player['projections'][0]['stats'])

    def test_legacy_scoring_rejects_bad_values(self):
        for bad in ('broken','nan','inf'):
            with self.assertRaises(ValueError): score_row({'pos':'RB','rec':bad},{})

    def test_public_fantasypros_parser_validates_season_and_ignores_fpts(self):
        html = (ROOT/'tests/fixtures/evidence/fantasypros-rb.html').read_text()
        additions,audit = parse_projection_html(html,source='fantasypros',pos='RB',season=2026,fetched_at=NOW,registry=self.snapshot['players'])
        self.assertEqual(additions['example:rb1']['stats']['rec'],'40')
        self.assertNotIn('proj',additions['example:rb1'])
        self.assertFalse(additions['example:rb1']['independence_verified'])
        with self.assertRaisesRegex(ValueError,'full-season'):
            parse_projection_html(html.replace('Projections (2026)','Projections - Week 1'),source='fantasypros',pos='RB',season=2026,fetched_at=NOW,registry=self.snapshot['players'])
        with self.assertRaisesRegex(ValueError,'headers'):
            parse_projection_html(html.replace('<th>REC</th>','<th>CHANGED</th>'),source='fantasypros',pos='RB',season=2026,fetched_at=NOW,registry=self.snapshot['players'])

    def test_public_cbs_parser_handles_full_name_and_grouped_headers(self):
        html = (ROOT/'tests/fixtures/evidence/cbs-rb.html').read_text()
        additions,audit = parse_projection_html(html,source='cbs',pos='RB',season=2026,fetched_at=NOW,registry=self.snapshot['players'])
        self.assertEqual(additions['example:rb1']['stats']['rush_yd'],'1000')
        self.assertEqual(additions['example:rb1']['expected_games'],'16')
        self.assertEqual(additions['example:rb1']['stats']['rec_yd'],'320')

    def test_nested_league_season_and_format_are_enforced(self):
        self.league={'league':{'season':2027}}
        with self.assertRaisesRegex(ValueError,'League season'):self.prepare()
        self.league={'league':{'season':2026,'draft_format':'best-ball'}}
        self.assertEqual(self.prepare()[0],[])

    def test_independence_must_be_explicitly_verified(self):
        for record in self.snapshot['players'][0]['projections']:
            record.pop('independence_verified')
        rows,report=self.prepare()
        self.assertEqual(report['mode'],'limited')
        self.assertEqual(rows[0]['independent_sources'],0)

    def test_unsupported_scoring_and_bonus_contract_rejects(self):
        for scoring in ({'reception':0.5,'unknown_bonus':3},{'bonuses':[{'stat':'rush_yard','threshold':100,'points':3}]}):
            self.league['scoring']=scoring
            with self.assertRaises(ValueError):self.prepare()

    def test_usage_denominator_and_market_period_are_required(self):
        self.snapshot['usage']=[{'source':'example','url':'https://example.com','season':2025,'observed_at':NOW,'player_id':'example:rb1','metric':'target_share','value':0.2,'sample':{'games':16}}]
        self.snapshot['markets']=[{'book':'example','url':'https://example.com','season':2026,'observed_at':NOW,'player_id':'example:rb1','kind':'player_prop','line':800}]
        report=self.prepare()[1]
        self.assertEqual(len(report['context']['rejected']),2)
        self.assertEqual(report['context']['usage'],[])

    def test_future_return_stays_scheduled_and_cannot_supersede_injury(self):
        event={'event_id':'a','player_id':'example:rb1','type':'injury','original_source':'team','url':'https://example.com/a','event_at':'2026-09-04T12:00:00Z','published_at':'2026-09-04T13:00:00Z','quality':'confirmed'}
        future=dict(event,event_id='b',type='return',event_at='2026-09-09T12:00:00Z',supersedes=['a'])
        result=ledger([event,future],NOW)
        self.assertEqual([e['event_id'] for e in result['active']],['a'])
        self.assertEqual([e['event_id'] for e in result['scheduled']],['b'])
        self.assertEqual(result['inactive_ids'],[])
        self.snapshot['news']=[event,future]
        self.snapshot['players'][0]['adjustments']=[{'adjustment_id':'a','event_id':'b','assumption':'games','reason':'scheduled return','base_includes_event':False,'points_delta':10}]
        with self.assertRaisesRegex(ValueError,'unknown, superseded'):self.prepare()

    def test_market_period_and_context_identity_fail_closed(self):
        market={'book':'example','url':'https://example.com','season':2026,'observed_at':NOW,'player_id':'example:rb1','kind':'player_prop','line':800,'period':'season','metric':'rush_yd','unit':'yards','over_price':-110}
        self.snapshot['markets']=[market]
        self.assertEqual(len(self.prepare()[1]['context']['markets']),1)
        for mutation in ({'period':'banana'},{'period':'week'},{'player_id':'unresolved'}):
            self.snapshot['markets']=[dict(market,**mutation)]
            self.assertEqual(len(self.prepare()[1]['context']['rejected']),1)

    def test_cli_sidecar_legacy_csv_and_snapshot_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            league=Path(tmp)/'league.json';league.write_text(json.dumps(self.league))
            output=Path(tmp)/'players.csv'
            run=subprocess.run([sys.executable,str(SCRIPTS/'prepare_data.py'),'--league',str(league),'--snapshot',str(FIXTURE),'--out',str(output),'--as-of',NOW],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            report=json.loads(output.with_suffix('.evidence.json').read_text())
            self.assertEqual(report['mode'],'full')
            self.assertEqual(len(report['data_revision']),64)
            self.assertIn('Example Runner',output.read_text())


if __name__=='__main__': unittest.main()
