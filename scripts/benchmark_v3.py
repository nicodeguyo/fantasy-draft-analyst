import copy,hashlib,json,math,random,statistics,sys,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/fantasy-draft-analyst/scripts'))
import draft_sim as ds
import live_draft
from board_policy import eligible_players,filled_slots
from fantasy_core.roster_value import lineup
OUT=ROOT/'examples/v3-benchmark'
CFG=json.loads((ROOT/'examples/v3-live/league.json').read_text())
POLICIES=['disciplined_adp','noisy_adp','legacy_heuristic','v3_live']

def trial(i):
 slot=i%12+1;seed=2026090700+i
 pool=ds.load_players(str(OUT/'players.csv'))
 cfg=copy.deepcopy(CFG);cfg['league']['draft_slot']=slot
 sims={}
 for name in POLICIES:
  c=copy.deepcopy(cfg);c['preferences']['draft_policy']='legacy' if name=='legacy_heuristic' else 'roster_v2'
  sims[name]=ds.Sim(c,copy.deepcopy(pool),None,None)
 results={}
 for name,sim in sims.items():
  st=sim.start(seed);own=st['my_overall'];picks=[]
  while st['i']<len(st['order']):
   ov,rnd,team=st['order'][st['i']];avail=st['avail'];roster=st['rosters'][team]
   rng=random.Random(seed*1000+ov)
   if team!=slot:p=sim.opp_pick(avail,roster,rnd,rng)
   elif name in ('v3_live','legacy_heuristic'):
    nxt=own[own.index(ov)+1] if ov!=own[-1] else None
    ranked=sim.pick_scores(avail,roster,rnd,nxt)
    p=sorted(ranked,key=lambda x:(-x[0],x[1]['adp'],x[1]['name']))[0][1]
   else:
    choices=eligible_players(avail,roster,sim.starters,sim.maxc,sim.avoid,sim.rounds-rnd+1)
    if name=='disciplined_adp':
     narrowed=[p for p in choices if (p['pos'] not in ('K','DEF') or rnd>=sim.rounds-1) and (p['pos'] not in ('QB','TE') or sum(q['pos']==p['pos'] for q in roster)<sim.starters[p['pos']])]
     p=min(narrowed or choices,key=lambda x:(x['adp'],x['name']))
    else:p=sim.opp_pick(choices,roster,rnd,rng)
   st['rosters'][team].append(p);st['avail'].remove(p);st['i']+=1
   if team==slot:picks.append({'pick':ov,'name':p['name'],'pos':p['pos']})
  roster=st['rosters'][slot]
  assert len(roster)==15 and len({p['player_id'] for p in roster})==15
  complete=filled_slots(roster,sim.starters)==sum(sim.starters.values())
  points,starters=lineup(roster,cfg)
  evaluator=sims['v3_live'];value=evaluator.roster_breakdown(roster,False)
  # Controlled one-week absence: same /17 rates and waiver floor for every roster.
  rates=[dict(p,proj=p['proj']/17) for p in roster];waivers={p:v/17 for p,v in evaluator.repl.items()}
  full=lineup(rates,cfg,waivers)[0];losses=[];bench_gains=[]
  starter_ids={p['player_id'] for p in starters}
  for absent in starters:
   if absent['pos'] not in ('RB','WR','TE'):continue
   remain=[p for p in rates if p['player_id']!=absent['player_id']]
   with_bench=lineup(remain,cfg,waivers)[0]
   without_bench=lineup([p for p in remain if p['player_id'] in starter_ids],cfg,waivers)[0]
   losses.append(full-with_bench);bench_gains.append(with_bench-without_bench)
  results[name]={'starter_points':points,'coverage_utility':value['coverage_points'],'roster_utility':value['total'],'absence_week_loss':statistics.mean(losses),'bench_rescue_points':statistics.mean(bench_gains),'complete':complete,'counts':{pos:sum(p['pos']==pos for p in roster) for pos in ds.POSITIONS} if hasattr(ds,'POSITIONS') else {pos:sum(p['pos']==pos for p in roster) for pos in ['QB','RB','WR','TE','K','DEF']},'picks':picks}
 return {'seed':seed,'slot':slot,'policies':results}

def summarize(rows):
 out={}
 for p in POLICIES:
  out[p]={}
  for metric in ['starter_points','coverage_utility','roster_utility','absence_week_loss','bench_rescue_points']:
   vals=[r['policies'][p][metric] for r in rows];diff=[r['policies'][p][metric]-r['policies']['disciplined_adp'][metric] for r in rows]
   mean=statistics.mean(diff);half=1.96*statistics.stdev(diff)/len(diff)**.5 if len(diff)>1 else 0
   out[p][metric]={'mean':statistics.mean(vals),'delta_vs_disciplined_adp':mean,'paired_95_mc_interval':[mean-half,mean+half]}
  out[p]['complete']=sum(r['policies'][p]['complete'] for r in rows)
 return out

if __name__=='__main__':
 n=int(sys.argv[1]) if len(sys.argv)>1 else 800;t=time.time()
 with ProcessPoolExecutor(max_workers=4) as executor:
  rows=[]
  for r in executor.map(trial,range(n)):
   rows.append(r)
   if len(rows)%100==0:print(len(rows),'rooms',round(time.time()-t,1),'s',flush=True)
 result={'rooms':n,'elapsed_seconds':time.time()-t,'data_as_of':'2026-09-07T04:00:17.778842+00:00','method':'12-team half-PPR no keepers; seats cycled 1–12; same forecasts; common per-pick opponent random seeds; v3 exact live policy scores without offline horizon probes; legacy heuristic is not the archived saved board. No tuning to results.','metrics':'Starter points = projected full-season legal starting lineup. Coverage utility is separate. Absence stress = one RB/WR/TE starter missing one week with /17 point rates and fixed waiver fallback; averages over those starters. Not injury probabilities or actual season outcomes.','summary':summarize(rows),'rows':rows}
 (OUT/f'results-{n}.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result['summary'],indent=2));print('seconds',result['elapsed_seconds'])
