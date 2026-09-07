"""Live projection stress tests must re-rank the actual state, not print boilerplate."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/fantasy-draft-analyst/scripts'))
import live_draft
from fantasy_core import session


def fixture():
    cfg={'league':{'teams':2,'rounds':2,'draft_slot':1,'draft_type':'snake'},
         'roster':{'QB':0,'RB':0,'WR':1,'TE':0,'FLEX':0,'K':0,'DEF':0,'bench':1},
         'keepers':{'count':0},'valuation':{'assumed_missed_games':0}}
    pool=[dict(player_id=name,name=name,pos='WR',proj=points,adp=i+1,sd=4)
          for i,(name,points) in enumerate([('A',100),('B',99),('C',98),('D',40)])]
    return cfg,pool


class LiveSensitivityTests(unittest.TestCase):
    def test_missing_dispersion_uses_explicit_ten_percent_and_detects_flip(self):
        cfg,pool=fixture()
        s=session.create(cfg,pool)
        before=copy.deepcopy(s)
        recommendation=live_draft.recommend(s)
        top=recommendation['candidates'][0]
        self.assertEqual(top['name'],'A')
        self.assertIn('Preferred pick changes',top['sensitivity'])
        self.assertIn('not a confidence interval',top['sensitivity'])
        sensitivity=top['sensitivity_cases']
        self.assertEqual(sensitivity['method'],'analyst_10_percent_stress')
        self.assertEqual(sensitivity['magnitude_points'],10)
        self.assertTrue(sensitivity['top_choice_reverses'])
        lower=sensitivity['scenarios'][0]
        self.assertEqual(lower['changed_projection'],90)
        self.assertEqual(lower['top_choice'],'B')
        self.assertTrue(lower['reversed'])
        self.assertEqual(s,before, 'Stress tests must not mutate the actual session')

    def test_source_disagreement_used_as_input_stress_not_adp(self):
        cfg,pool=fixture()
        pool[0].update(projection_sd=2,sd=1000)
        result=live_draft.recommend(session.create(cfg,pool))
        sensitivity=result['candidates'][0]['sensitivity_cases']
        self.assertEqual(sensitivity['method'],'source_disagreement')
        self.assertEqual(sensitivity['magnitude_points'],2)
        self.assertEqual(sensitivity['scenarios'][0]['changed_projection'],98)
        self.assertTrue(sensitivity['top_choice_reverses'])
        self.assertIn('not outcome variance', sensitivity['interpretation'])

    def test_actual_drafted_player_cannot_reappear_in_stress_winners(self):
        cfg,pool=fixture()
        cfg['league']['draft_slot']=2
        s=session.create(cfg,pool)
        session.record_pick(s,'A')
        result=live_draft.recommend(s)
        for candidate in result['candidates']:
            self.assertNotEqual(candidate['player_id'],'A')
            for scenario in candidate['sensitivity_cases']['scenarios']:
                self.assertNotEqual(scenario['top_choice'],'A')

    def test_zero_observed_dispersion_is_preserved_not_fabricated(self):
        cfg,pool=fixture();pool[0]['projection_sd']=0
        sensitivity=live_draft.recommend(session.create(cfg,pool))['candidates'][0]['sensitivity_cases']
        self.assertEqual(sensitivity['method'],'source_disagreement')
        self.assertEqual(sensitivity['magnitude_points'],0)
        self.assertFalse(sensitivity['top_choice_reverses'])


if __name__=='__main__': unittest.main()
