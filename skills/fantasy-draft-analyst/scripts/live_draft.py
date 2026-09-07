#!/usr/bin/env python3
"""Local live draft: durable picks and fast recommendations from the shared policy."""
from __future__ import annotations
import argparse
from contextlib import nullcontext
from datetime import datetime, timedelta
import copy
import csv
import json
import math
import random
import statistics
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse
from draft_sim import Sim, load_league, load_players
from fantasy_core import session as state


def read_pool(path,league=None):
    p=Path(path)
    evidence_path=p.with_suffix('.evidence.json')
    evidence=json.loads(evidence_path.read_text()) if evidence_path.exists() else None
    if p.suffix.lower()=='.json':
        data=json.loads(p.read_text())
        players=data if isinstance(data,list) else data['players']
        if isinstance(data,dict): evidence=data.get('evidence',data.get('readiness',evidence))
    else:
        with p.open(newline='') as stream:has_rows=next(csv.DictReader(stream),None) is not None
        players=load_players(str(p)) if has_rows else []
    if evidence and evidence.get('input_snapshot'):
        if evidence.get('period')!='season':raise ValueError('Weekly/rest-of-season snapshots cannot initialize a season draft session')
        known={x['player_id'] for x in players}
        for raw in evidence['input_snapshot'].get('players',[]):
            if raw['player_id'] in known:continue
            placeholder={k:raw.get(k) for k in ('player_id','name','pos','team','bye')}
            placeholder.update(proj=None,evidence_mode='rank-only',rank=None,adp=None)
            price=raw.get('adp',{})
            # Omitted projection rows still retain identity. Only validated current-format prices order them.
            try:
                asof=datetime.fromisoformat(evidence['as_of'].replace('Z','+00:00'))
                updated=datetime.fromisoformat(price['updated_at'].replace('Z','+00:00'))
                value=float(price['value'])
                if price.get('season')==evidence['season'] and price.get('kind','adp')=='adp' and price.get('source') and price.get('format')==(league or {}).get('draft_format','managed-1qb') and timedelta(0)<=asof-updated<=timedelta(days=3) and math.isfinite(value) and value>0:
                    placeholder['adp']=value
            except (KeyError,ValueError,TypeError):pass
            players.append(placeholder)
    return state.normalize_players(players),evidence


def wait_comparison(sim, s, available, roster, candidates, current, next_pick, trials=8):
    """Small conditional two-pick branches from confirmed state; no modeled keepers."""
    if next_pick is None or current != state.replay(s)['current_pick'] or len(candidates)<2:
        return {}
    own=int(s['league']['league']['draft_slot']);teams=int(s['league']['league']['teams'])
    byid={p['player_id']:p for p in sim.pool}
    actual=state.replay(s)['picks'];occupied={p['pick'] for p in actual}
    rosters={i:[byid[p['player_id']] for p in actual if p['owner']==i and p['player_id'] in byid] for i in range(1,teams+1)}
    out={};results={}
    for first in candidates:
        scores=[];survival={p['player_id']:0 for p in candidates if p!=first};next_names={}
        for trial in range(trials):
            rng=random.Random(104729+trial)
            pool=[p for p in available if p['player_id']!=first['player_id']]
            branch={k:list(v) for k,v in rosters.items()};branch[own]=roster+[first]
            for pick in range(current+1,next_pick):
                if pick in occupied or not pool:continue
                owner=state.owner_at(s['league'],pick)
                chosen=sim.opp_pick(pool,branch[owner],(pick-1)//teams+1,rng)
                branch[owner].append(chosen);pool.remove(chosen)
            for pid in survival:
                survival[pid]+=int(any(p['player_id']==pid for p in pool))
            ranked=sim.pick_scores(pool,branch[own],(next_pick-1)//teams+1) if pool else []
            if ranked:
                chosen=max(ranked,key=lambda row:(row[0],-row[1]['adp']))[1]
                branch[own].append(chosen);next_names[chosen['name']]=next_names.get(chosen['name'],0)+1
            scores.append(sim.objective_pts(branch[own]))
        results[first['player_id']]=dict(mean=statistics.mean(scores),scores=scores)
        out[first['player_id']]=dict(trials=trials,next_pick=next_pick,take_now_then_next_mean_utility=round(statistics.mean(scores),3),
            next_choices=next_names,other_candidates_surviving_trials=survival,
            assumptions='Conditional on confirmed rival rosters and platform ADP-noise prior. Eight trials are an illustrative scenario, not calibrated survival probabilities. No outcome uncertainty is sampled.')
    for pid in out:
        alternative=max((k for k in results if k!=pid),key=lambda k:results[k]['mean'])
        paired=[a-b for a,b in zip(results[pid]['scores'],results[alternative]['scores'])]
        out[pid].update(best_pivot_id=alternative,paired_utility_difference=round(statistics.mean(paired),3),
            sampling_standard_error=round(statistics.stdev(paired)/(trials**.5),3) if trials>1 else None)
    return out


def projection_sensitivity(sim, available, roster, ranked, rnd, next_pick, limit=3):
    """Re-rank actual available players under one-at-a-time projection stresses.

    Between-source dispersion measures disagreement, not football outcome risk.
    Where it is unavailable, +/-10% is an explicit analyst stress assumption,
    never a confidence interval. Other player inputs and actual draft state stay
    fixed. At most six fast re-rankings; no additional draft rollouts.
    """
    if not ranked:
        return {}
    available_ids = {p['player_id'] for p in available}
    roster_ids = {p['player_id'] for p in roster}
    baseline_top = ranked[0][1]['player_id']
    result = {}
    for _, candidate in ranked[:min(limit, 3)]:
        raw_sd = candidate.get('projection_sd')
        try:
            spread = float(raw_sd) if raw_sd not in (None, '') else None
            if spread is not None and (not math.isfinite(spread) or spread < 0):
                spread = None
        except (ValueError, TypeError):
            spread = None
        method = 'source_disagreement' if spread is not None else 'analyst_10_percent_stress'
        magnitude = spread if spread is not None else .10 * abs(float(candidate['proj']))
        checks = []
        for direction, multiplier in (('lower', -1), ('higher', 1)):
            changed_pool = copy.deepcopy(sim.pool)
            changed = next(p for p in changed_pool if p['player_id'] == candidate['player_id'])
            changed['proj'] = float(candidate['proj']) + multiplier * magnitude
            alternative = Sim(copy.deepcopy(sim.cfg), changed_pool, None, None)
            alternative.pos_horizon = copy.deepcopy(sim.pos_horizon)
            available_now = [p for p in alternative.pool if p['player_id'] in available_ids]
            roster_now = [p for p in alternative.pool if p['player_id'] in roster_ids]
            scores = sorted(alternative.pick_scores(available_now, roster_now, rnd, next_pick),
                            key=lambda x: (-x[0], x[1]['adp'], x[1]['name']))
            winner = scores[0][1] if scores else None
            candidate_rank = next((i+1 for i, (_, p) in enumerate(scores)
                                   if p['player_id'] == candidate['player_id']), None)
            checks.append(dict(direction=direction, changed_projection=round(changed['proj'], 3),
                               input_shift_points=round(multiplier*magnitude, 3),
                               top_choice=winner['player_id'] if winner else None,
                               top_name=winner['name'] if winner else None,
                               reversed=bool(winner and winner['player_id'] != baseline_top),
                               candidate_rank=candidate_rank,
                               runner_up_gap=round(scores[0][0]-scores[1][0], 3) if len(scores)>1 else None))
        result[candidate['player_id']] = dict(
            method=method, baseline_projection=candidate['proj'],
            magnitude_points=round(magnitude, 3), baseline_top_choice=baseline_top,
            top_choice_reverses=any(check['reversed'] for check in checks), scenarios=checks,
            interpretation=('One-at-a-time change in this player only; all other inputs and availability fixed. '
                            'Source dispersion is disagreement, not outcome variance; the fallback 10% is an '
                            'analyst assumption. Neither is a statistical confidence interval or an exhaustive risk test.'))
    return result


def sensitivity_summary(packet):
    if not packet:
        return 'Sensitivity is bounded to the first three candidates.'
    amount=packet['magnitude_points']
    label=(f'±{amount:g} points from source disagreement' if packet['method']=='source_disagreement'
           else f'±10% analyst projection stress (±{amount:g} points)')
    flips=[f"{row['top_name']} in the {row['direction']} case" for row in packet['scenarios'] if row['reversed']]
    outcome=('Preferred pick changes to '+ '; '.join(flips)) if flips else 'Preferred pick is unchanged in these two cases'
    return label+': '+outcome+'. This is not a confidence interval.'


def recommend(s,limit=3):
    live=state.replay(s)
    own=int(s['league']['league']['draft_slot'])
    pool=copy.deepcopy(s['players'])
    byid={p['player_id']:p for p in pool}
    taken={p['player_id'] for p in live['picks'] if p['player_id']}
    avail=[p for p in pool if p['player_id'] not in taken]
    roster=[byid[p['player_id']] for p in live['picks'] if p['owner']==own and p['player_id'] in byid]
    total=int(s['league']['league']['teams'])*int(s['league']['league']['rounds'])
    occupied={p['pick'] for p in live['picks']}
    turns=[i for i in range(live['current_pick'],total+1) if state.owner_at(s['league'],i)==own and i not in occupied]
    result=dict(state_token=state.token(s),revision=s['revision'],data_revision=s['data_revision'],
                current_pick=live['current_pick'],for_pick=turns[0] if turns else None,
                mode='limited_projection',engine='shared fast deterministic policy',
                warnings=[],candidates=[],evidence=s['evidence'])
    evidence_mode=s.get('evidence',{}).get('mode') if isinstance(s.get('evidence'),dict) else None
    if evidence_mode=='full':result['mode']='full_projection'
    if isinstance(s.get('evidence'),dict):result['warnings'].extend(s['evidence'].get('warnings',[]))
    if not turns: return result
    if live['current_pick']!=turns[0]: result['warnings'].append('Preview only: opponents still pick before your turn; rerun after every pick.')
    if int(s['league'].get('keepers',{}).get('count',0)) and not s['league'].get('keepers',{}).get('league_keeper_list'):
        result['warnings'].append('Keeper declarations are missing. No keepers are invented; confirm declarations before relying on availability.')
    unknown=[p for p in live['picks'] if p['unknown']]
    if unknown: result['warnings'].append('Unmatched picks preserve slots but may hide a player alias; resolve before trusting availability.')
    if any(p['owner']==own and p['unknown'] for p in live['picks']):
        result['warnings'].append('Your roster has unresolved players; point comparisons are disabled.')
        rank_only=True
    else: rank_only=any(p.get('proj') in (None,'') for p in pool)
    if rank_only:
        result['mode']='rank_only'
        ordered=sorted([p for p in avail if p.get('adp') not in (None,'') or p.get('rank') not in (None,'')],key=lambda p:float(p.get('adp') or p.get('rank')))
        result['warnings'].append('Players without validated price/rank remain in the available list but are not ranked; projection comparisons are disabled for incomplete pools.')
        result['candidates']=[dict(player_id=p['player_id'],name=p['name'],pos=p.get('pos','unknown'),
            explanation='Rank-only fallback; workload projections or roster identity are incomplete. No point advantage is claimed.') for p in ordered[:limit]]
        return result
    for p in pool:
        p['proj']=float(p['proj']);p['adp']=float(p.get('adp') or 99999)
        raw_sd=p.get('sd',p.get('adp_sd'))
        p['sd']=float(max(4,.08*p['adp']) if raw_sd in (None,'') else raw_sd)
        if not all(math.isfinite(p[k]) for k in ('proj','adp','sd')): raise ValueError('Player values must be finite')
    cfg=copy.deepcopy(s['league'])
    # Confirmed keepers already occupy their owners' rosters and are removed from availability.
    cfg['keepers']={'count':0,'league_keeper_list':[]}
    sim=Sim(cfg,pool,None,None)
    rnd=(turns[0]-1)//int(cfg['league']['teams'])+1
    nxt=turns[1] if len(turns)>1 else None
    ranked=sorted(sim.pick_scores(avail,roster,rnd,nxt),key=lambda x:(-x[0],x[1]['adp'],x[1]['name']))
    if not ranked: result['warnings'].append('Policy has no eligible candidate; inspect remaining roster requirements.')
    baseline=sim.roster_breakdown(roster) if hasattr(sim,'roster_breakdown') else None
    result['roster_analysis']=dict(counts={pos:sum(p['pos']==pos for p in roster) for pos in ('QB','RB','WR','TE','K','DEF')},requirements=cfg.get('roster',{}),value=baseline)
    sensitivity_checks=projection_sensitivity(sim,avail,roster,ranked,rnd,nxt,limit)
    for score,p in ranked[:limit]:
        detail=sim.roster_breakdown(roster+[p]) if baseline else None
        gains={k:round(detail[k]-baseline[k],3) for k in ('starter_points','coverage_points','upside_points') if k in detail and k in baseline} if detail else {}
        result['candidates'].append(dict(player_id=p['player_id'],name=p['name'],pos=p['pos'],policy_score=round(score,3),
            roster_benefit=gains,adp=p['adp'],projection_disagreement=p.get('projection_sd'),
            source_count=p.get('source_count'),evidence_mode=p.get('evidence_mode','legacy_unverified'),
            evidence=next((e for e in s.get('evidence',{}).get('players',[]) if e.get('player_id')==p['player_id']),{}),
            explanation='Shared roster policy weighs usable starters, coverage and upside; policy score is not a forecast of points or win probability.',
            wait_risk='Price context only: ADP '+str(p['adp'])+'; next own pick '+str(nxt)+'. No calibrated availability probability.',
            sensitivity=sensitivity_summary(sensitivity_checks.get(p['player_id'])),
            sensitivity_cases=sensitivity_checks.get(p['player_id'], {'method':'not_tested'})))
    comparisons=wait_comparison(sim,s,avail,roster,[p for _,p in ranked[:limit]],turns[0],nxt)
    for candidate in result['candidates']:
        if candidate['player_id'] in comparisons:candidate['wait_comparison']=comparisons[candidate['player_id']]
    return result


def validate_explanation(s,candidate_ids,text,claims=None):
    """Optional explainer contract: only packet facts and available candidate IDs accepted."""
    ids={p['player_id'] for p in state.available(s)}
    valid=bool(candidate_ids) and set(candidate_ids)<=ids
    names={p['name']:p['player_id'] for p in s['players']}
    valid=valid and all(pid in candidate_ids for name,pid in names.items() if name.casefold() in text.casefold())
    # Arbitrary generated factual prose cannot be verified locally: require exact packet strings.
    allowed={c['explanation'] for c in recommend(s).get('candidates',[])}
    valid=valid and text in allowed and not claims
    return text if valid else 'Explanation not supported by current evidence. Use the current deterministic shortlist.'


def import_picks(s,rows):
    staged=copy.deepcopy(s)
    for row in rows:
        pick=int(row['pick'])
        value=row.get('player_id') or row.get('name') or row.get('player')
        eid=row.get('event_id') or 'import:'+str(pick)+':'+state.digest(value)[:16]
        occupied=next((p for p in state.replay(staged)['picks'] if p['pick']==pick),None)
        if occupied:
            p=state.resolve(staged,value)
            if occupied['name']==value or (p and occupied['player_id']==p['player_id']): continue
            raise ValueError('Import conflicts with occupied pick '+str(pick))
        rec=recommend(staged) if state.owner_at(staged['league'],pick)==int(staged['league']['league']['draft_slot']) else None
        if rec is not None:rec['receipt_context']='Reconstructed at import time; not evidence of advice available before the original pick.'
        state.record_pick(staged,value,pick=pick,owner=row.get('owner'),event_id=eid,recommendation=rec)
    s.clear();s.update(staged)


def public_state(s):
    return dict(session_id=s['session_id'],revision=s['revision'],data_revision=s['data_revision'],
        league=s['league']['league'],roster_requirements=s['league'].get('roster',{}),current_owner=state.owner_at(s['league'],state.replay(s)['current_pick']),**state.replay(s),available=[{k:p.get(k) for k in ('player_id','name','pos')} for p in state.available(s)],recommendation=recommend(s))


HTML='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Live fantasy draft</title>
<style>body{background:#101923;color:#eef2f6;font:16px system-ui;max-width:1050px;margin:32px auto;padding:20px}button,input,select{font:inherit;padding:10px;margin:6px;border-radius:6px}article{padding:16px;background:#1c2b38;margin:12px 0;border-radius:10px}small{color:#bac8d4}#error{color:#ffb7a7}pre{white-space:pre-wrap}li{margin:8px}</style>
<h1>Live draft room</h1><p>Cached local evidence. Every pick recalculates the shared roster policy.</p><div id="status"></div><p id="error"></p><div id="choices"></div>
<h2>Your roster</h2><div id="roster"></div><p><input id="search" placeholder="Search available players"></p><form id="pickform"><label>Record current pick <select id="player"></select></label><button>Record pick</button></form>
<form id="unknownform"><label>Unmatched player <input id="unknown" placeholder="Exact original name" required></label><button>Record unknown pick</button></form>
<p><label>Refresh cached player JSON <input id="datafile" type="file" accept=".json"></label><button id="upload">Use new snapshot</button></p><p><label>Resolve unmatched pick # <input id="resolvepick" type="number" min="1" style="width:80px"></label><button id="resolve">Assign selected player</button></p><button id="undo">Undo last pick</button><button id="refresh">Refresh analysis</button><a href="/api/export">Export session</a><h2>Draft history</h2><ol id="history"></ol>
<script>
let snapshot;const el=id=>document.getElementById(id);function add(parent,tag,text){const e=document.createElement(tag);e.textContent=text;parent.append(e);return e}
async function call(path,payload){const r=await fetch(path,payload?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}:{});const d=await r.json();if(!r.ok)throw Error(d.error);return d}
async function render(){try{snapshot=await call('/api/state');el('error').textContent='';el('status').textContent=`Pick ${snapshot.current_pick} · team ${snapshot.current_owner} (your slot ${snapshot.league.draft_slot}) · state ${snapshot.revision} · data ${snapshot.data_revision.slice(0,10)} · ${snapshot.recommendation.mode}`;el('choices').replaceChildren();snapshot.recommendation.warnings.forEach(w=>add(el('choices'),'p',w));for(const c of snapshot.recommendation.candidates){const a=add(el('choices'),'article','');add(a,'h2',c.name+' · '+c.pos);if(c.roster_benefit){const b=c.roster_benefit;const signed=n=>(n>=0?'+':'')+Number(n).toFixed(1);add(a,'p',`Starter improvement ${signed(b.starter_points||0)} · Reserve coverage ${signed(b.coverage_points||0)} · Upside ${signed(b.upside_points||0)}`);add(a,'small','Modeled utility components, not a forecast of season points.');}else{add(a,'p',c.explanation);}if(c.adp)add(a,'p','Draft price: ADP '+Number(c.adp).toFixed(1));if(c.wait_comparison){const w=c.wait_comparison;const pivot=snapshot.recommendation.candidates.find(p=>p.player_id===w.best_pivot_id);add(a,'p','Take now, then pick #'+w.next_pick+': '+Number(w.paired_utility_difference).toFixed(1)+' utility versus starting with '+(pivot?pivot.name:'the best alternative')+'.');const choices=Object.entries(w.next_choices||{}).sort((a,b)=>b[1]-a[1]);if(choices.length)add(a,'small','Next-turn possibilities: '+choices.slice(0,3).map(([name,count])=>name+' ('+count+'/'+w.trials+' scenarios)').join(', ')+'. Illustrative, not calibrated odds.');}else if(c.wait_risk){add(a,'small',c.wait_risk);}if(c.sensitivity){if(typeof c.sensitivity==='string'){add(a,'p',c.sensitivity);}else{const v=c.sensitivity;const flips=(v.scenarios||[]).filter(x=>x.reversed);add(a,'p',flips.length?'What changes the choice: '+flips.map(x=>x.direction+' projection case favors '+x.top_name).join('; ')+'.':'The top choice holds in these projection stress cases.');add(a,'small','Projection stress: ±'+Number(v.magnitude_points||0).toFixed(1)+' points ('+(v.method==='source_disagreement'?'observed source disagreement':'explicit 10% assumption')+'), not a confidence interval.');}}const d=add(a,'details','');add(d,'summary','Evidence and assumptions');add(d,'pre',JSON.stringify({source_count:c.source_count,projection_disagreement:c.projection_disagreement,evidence_mode:c.evidence_mode,sensitivity:c.sensitivity,sensitivity_cases:c.sensitivity_cases,wait_comparison:c.wait_comparison,evidence:c.evidence},null,2));}filterPlayers();el('roster').replaceChildren();const yours=snapshot.picks.filter(p=>p.owner===snapshot.league.draft_slot);add(el('roster'),'p','Starting requirements: '+Object.entries(snapshot.roster_requirements).filter(([k,v])=>['QB','RB','WR','TE','FLEX','SUPERFLEX','K','DEF'].includes(k)&&v).map(([k,v])=>v+' '+k).join(' · '));if(snapshot.recommendation.roster_analysis)add(el('roster'),'p','Roster counts: '+Object.entries(snapshot.recommendation.roster_analysis.counts).map(([k,v])=>v+' '+k).join(' · '));yours.forEach(p=>add(el('roster'),'p',p.name+(p.keeper?' (keeper)':'')+(p.unknown?' (unmatched)':'')));if(!yours.length)add(el('roster'),'p','No players drafted yet.');el('history').replaceChildren();snapshot.picks.forEach(p=>add(el('history'),'li',`#${p.pick} · team ${p.owner} · ${p.name}${p.keeper?' (keeper)':''}${p.unknown?' (unmatched)':''}`))}catch(e){el('error').textContent=e.message}}
function filterPlayers(){const q=el('search').value.toLowerCase();el('player').replaceChildren();snapshot.available.filter(p=>(p.name+' '+p.pos).toLowerCase().includes(q)).forEach(p=>{const o=add(el('player'),'option',p.name+' · '+p.pos);o.value=p.player_id})}el('search').oninput=filterPlayers;
async function action(path,data={}){try{await call(path,{...data,state_token:snapshot.recommendation.state_token});await render()}catch(e){el('error').textContent=e.message}}
el('pickform').onsubmit=e=>{e.preventDefault();action('/api/pick',{player:el('player').value,event_id:crypto.randomUUID()})};el('unknownform').onsubmit=e=>{e.preventDefault();action('/api/pick',{player:el('unknown').value,event_id:crypto.randomUUID()})};el('resolve').onclick=()=>action('/api/resolve',{pick:Number(el('resolvepick').value),player:el('player').value});el('upload').onclick=async()=>{try{const f=el('datafile').files[0];if(!f)throw Error('Choose a JSON player snapshot first');const d=JSON.parse(await f.text());await action('/api/refresh',{players:Array.isArray(d)?d:d.players,evidence:d.evidence||d.readiness})}catch(e){el('error').textContent=e.message}};el('undo').onclick=()=>action('/api/undo');el('refresh').onclick=render;render();
</script>'''


def make_server(path,port=8768):
    lock=threading.Lock()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def reply(self,code,value,html=False):
            data=value.encode() if html else json.dumps(value,allow_nan=False).encode()
            self.send_response(code);self.send_header('Content-Type','text/html; charset=utf-8' if html else 'application/json')
            self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(data)
        def valid_host(self):
            return self.headers.get('Host') in ('127.0.0.1:'+str(self.server.server_port),'localhost:'+str(self.server.server_port))
        def do_GET(self):
            if not self.valid_host(): return self.reply(403,{'error':'Invalid host'})
            try:
                with lock:
                    if self.path=='/': return self.reply(200,HTML,True)
                    if self.path=='/api/state': return self.reply(200,public_state(state.load(path)))
                    if self.path=='/api/export': return self.reply(200,state.load(path))
                    self.reply(404,{'error':'Not found'})
            except (ValueError,KeyError,OSError) as e:self.reply(400,{'error':str(e)})
        def do_POST(self):
            origin=self.headers.get('Origin')
            expected={'http://127.0.0.1:'+str(self.server.server_port),'http://localhost:'+str(self.server.server_port)}
            if not self.valid_host() or origin not in expected: return self.reply(403,{'error':'Same-origin local requests only'})
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=4194304: raise ValueError('Invalid request size')
                if self.headers.get('Content-Type')!='application/json': raise ValueError('JSON required')
                data=json.loads(self.rfile.read(size))
                with lock, state.mutation_lock(path):
                    s=state.load(path)
                    if data.get('state_token')!=state.token(s): return self.reply(409,{'error':'State changed; refresh before recording action'})
                    if self.path=='/api/pick':state.record_pick(s,data['player'],event_id=data.get('event_id'),recommendation=recommend(s))
                    elif self.path=='/api/undo':state.undo(s)
                    elif self.path=='/api/refresh':state.refresh(s,data['players'],data.get('evidence'))
                    elif self.path=='/api/resolve':state.resolve_unknown(s,data['pick'],data['player'])
                    else:return self.reply(404,{'error':'Not found'})
                    state.save(s,path);self.reply(200,{'revision':s['revision']})
            except (ValueError,KeyError,TypeError,OSError) as e:self.reply(400,{'error':str(e)})
    return HTTPServer(('127.0.0.1',port),Handler)


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--session',required=True)
    sub=ap.add_subparsers(dest='command',required=True)
    init=sub.add_parser('init');init.add_argument('--league',required=True);init.add_argument('--players',required=True)
    pick=sub.add_parser('pick');pick.add_argument('player');pick.add_argument('--pick',type=int);pick.add_argument('--event-id')
    imp=sub.add_parser('import-picks');imp.add_argument('file')
    sub.add_parser('undo');sub.add_parser('recommend');sub.add_parser('export')
    resolve=sub.add_parser('resolve');resolve.add_argument('pick',type=int);resolve.add_argument('player')
    refresh=sub.add_parser('refresh');refresh.add_argument('--players',required=True)
    serve=sub.add_parser('serve');serve.add_argument('--port',type=int,default=8768)
    args=ap.parse_args(argv)
    try:
        with state.mutation_lock(args.session) if args.command not in ('recommend','export','serve') else nullcontext():
            if args.command=='init':
                if Path(args.session).exists():raise ValueError('Session already exists; use another path or resume it')
                cfg=load_league(args.league);players,evidence=read_pool(args.players,cfg);s=state.create(cfg,players,evidence);state.save(s,args.session)
            elif args.command=='serve':
                state.load(args.session);server=make_server(args.session,args.port);print(f'Live board: http://127.0.0.1:{server.server_port}',flush=True);server.serve_forever();return
            else:
                s=state.load(args.session)
                if args.command=='pick':state.record_pick(s,args.player,pick=args.pick,event_id=args.event_id,recommendation=recommend(s))
                elif args.command=='undo':state.undo(s)
                elif args.command=='resolve':state.resolve_unknown(s,args.pick,args.player)
                elif args.command=='import-picks':
                    p=Path(args.file)
                    rows=json.loads(p.read_text()) if p.suffix=='.json' else list(csv.DictReader(p.open()))
                    import_picks(s,rows)
                elif args.command=='refresh':
                    players,evidence=read_pool(args.players,s['league']);state.refresh(s,players,evidence)
                elif args.command=='recommend':print(json.dumps(recommend(s),indent=2));return
                elif args.command=='export':print(json.dumps(s,indent=2));return
                state.save(s,args.session)
            print(json.dumps({'session':args.session,**state.replay(s),'revision':s['revision']}))
    except (ValueError,KeyError,OSError,TypeError) as e:ap.exit(2,str(e)+'\n')
if __name__=='__main__':main()
