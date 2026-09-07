"""Late recommendations must not promote unavailable watch/reference rows."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'skills/fantasy-draft-analyst/scripts'))
from board_policy import row_groups

class LateAvailabilityTests(unittest.TestCase):
    def test_reference_stars_and_unlikely_falls_do_not_become_late_choices(self):
        rows = [{'name': n, 'pos': 'WR', 'there': chance, 'surplus': points}
                for n, chance, points in [('early',0,120),('unlikely',14,60),('borderline',15,10),('realistic',90,0)]]
        sim = {'availability': {'132': rows}, 'replacement': {'WR': 100}}
        players = {r['name']: {'pos':'WR','proj':r['surplus']+100} for r in rows}
        notes = {'plan':[{'pick':'132','player':'early'}], 'pick_notes': {'132':'early unlikely'}}
        top, more, target = row_groups(sim, notes, players, 132)
        self.assertEqual([r['name'] for r in top+more], ['borderline','realistic'])
        self.assertIsNone(target)

    def test_notes_cannot_reintroduce_known_unavailable_player(self):
        sim = {'replacement': {'WR':100}}
        notes = {'pick_notes': {'132':'early'}}
        top, more, _ = row_groups(sim,notes,{'early':{'pos':'WR','proj':220}},132,matrix={'early':{132:0}})
        self.assertEqual(top+more,[])

    def test_evaluated_early_round_falls_are_preserved(self):
        rows = [{'name':'fall','pos':'WR','avail_pct':10,'value':1900}]
        sim = {'pick_values': {'20':rows},'replacement':{'WR':100}}
        self.assertEqual(row_groups(sim,{}, {},20)[0],rows)

if __name__ == '__main__': unittest.main()
