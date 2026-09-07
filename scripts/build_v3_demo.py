#!/usr/bin/env python3
"""Reproduce the public v3 walkthrough from frozen public inputs, offline.

The first 18 picks follow eligible ESPN ADP order. The 19th takes the
preview leader, deliberately illustrating a lost target, not a typical draft.
No private league data or hand-authored recommendation scores are used.
"""
import csv
import hashlib
import html
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/fantasy-draft-analyst/scripts'))
import live_draft
from fantasy_core import session
from fantasy_core.evidence import prepare_snapshot
from prepare_data import FIELDS

AS_OF = '2026-09-07T04:00:17.778842+00:00'
BASE = ROOT / 'examples/v3-live'


def packet(s):
    result = live_draft.recommend(s)
    # State tokens include session identifiers; the public demo needs only facts.
    result.pop('state_token', None)
    result.pop('evidence', None)
    byid = {p['player_id']: p for p in s['players']}
    for c in result['candidates']:
        c['projection'] = byid[c['player_id']]['proj']
        for row in c.get('evidence', {}).get('accepted', []):
            row.pop('raw_stats', None)
    result['roster'] = [p['name'] for p in session.replay(s)['picks'] if p['owner'] == 5]
    return result


def cards(rec):
    out = []
    esc = html.escape
    for i, c in enumerate(rec['candidates']):
        gain = c['roster_benefit']
        sources = ''.join('<li><a href="'+esc(r['url'], quote=True)+'">'+esc(r['source'].upper())+'</a>: '+f"{r['league_points']:.1f}"+' projected points</li>' for r in c['evidence']['accepted'])
        w = c.get('wait_comparison', {})
        later = ', '.join(f'{name} ({count}/{w["trials"]} scenarios)' for name, count in sorted(w.get('next_choices', {}).items(), key=lambda x: (-x[1], x[0])))
        out.append(f'''<article class="draft-card {'preferred' if i == 0 else ''}">
<p class="card-rank">{'Model’s first choice' if i == 0 else 'Alternative '+str(i)}</p>
<h3>{esc(c['name'])}</h3><p class="position">{esc(c['pos'])} · ESPN ADP {c['adp']:.1f}</p>
<div class="card-number">{c['projection']:.1f}<span>projected half-PPR points</span></div>
<p class="source-coverage">{len(c['evidence']['accepted'])} source{'s' if len(c['evidence']['accepted']) != 1 else ''} · Limited evidence</p>
<p><b>Roster contribution</b><br>+{gain['starter_points']:.1f} starter value · +{gain['coverage_points']:.1f} coverage</p>
<p class="card-small">Modeled contributions with an incomplete roster; not additional points over the other candidate.</p>
<details><summary>Sources and what could change the call</summary><ul>{sources}</ul><p>{esc(c['sensitivity'])}</p><p>{esc(later)}</p><p>Eight modeled next-turn scenarios, not calibrated odds. Source disagreement is not an injury or performance forecast.</p></details>
</article>''')
    return ''.join(out)


def main():
    league = json.loads((BASE / 'league.json').read_text())
    snapshot = json.loads((BASE / 'evidence.json').read_text())
    rows, report = prepare_snapshot(snapshot, league, now=AS_OF)
    # Use the same CSV loader as the shipped CLI, including missing-value handling.
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'players.csv'
        with path.open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(rows)
        path.with_suffix('.evidence.json').write_text(json.dumps(report))
        pool, evidence = live_draft.read_pool(path, league)
    s = session.create(league, pool, evidence)
    eligible = sorted([p for p in pool if p.get('proj') is not None and p.get('adp') is not None], key=lambda p: (p['adp'], p['name']))
    for p in eligible[:18]:
        session.record_pick(s, p['player_id'])
    before = packet(s)
    target = before['candidates'][0]
    session.record_pick(s, target['player_id'])
    after = packet(s)
    assert before['current_pick'] == 19 and after['current_pick'] == 20
    assert target['player_id'] not in {p['player_id'] for p in after['candidates']}
    assert after['for_pick'] == 20
    payload = dict(as_of=AS_OF, season=2026, evidence_mode=report['mode'],
                   method='First 18 picks by eligible ADP; pick 19 deliberately takes the preview leader. Fictional draft, real saved projections. No search for maximum improvement.',
                   recorded_pick={'pick': 19, 'name': target['name']}, before=before, after=after,
                   picks=session.replay(s)['picks'],
                   input_sha256={name: hashlib.sha256((BASE/name).read_bytes()).hexdigest() for name in ('league.json','evidence.json')})
    (ROOT / 'docs/site/v3-demo.json').write_text(json.dumps(payload, indent=2)+'\n')
    target_name = html.escape(target['name'])
    fragment = f'''<div class="demo-toolbar"><div role="group" aria-label="Saved draft stages"><button type="button" data-stage="before" aria-pressed="false">Before pick 19</button><button type="button" data-stage="after" aria-pressed="true">Record {target_name} at 19 →</button></div><p id="demo-status" role="status">Pick 20: your turn. {target_name} is off the board.</p></div>
<div id="stage-before" hidden><p class="stage-context">Before pick 19 · Preview only: another manager picks before you. Your roster: Jonathan Taylor.</p><div class="draft-cards">{cards(before)}</div></div>
<div id="stage-after"><p class="stage-context">Pick 20 · Your roster: Jonathan Taylor · Next turn: pick 29</p><div class="draft-cards">{cards(after)}</div></div>
<p class="model-note"><b>This is a saved walkthrough of actual v3 engine output.</b> The buttons switch between two reproduced states; this website does not run your draft. Public data fetched September 7, 2026 (UTC); provider update times are unverified. Evidence is limited: player coverage varies and some scoring categories use explicit zero approximations. No news or betting inputs were used in this example. <a href="https://github.com/nicodeguyo/fantasy-draft-analyst/blob/main/docs/site/README.md">Inspect sources, assumptions, and reproduction →</a></p>'''
    path = ROOT / 'index.html'
    start, rest = path.read_text().split('<!-- v3-demo:start -->', 1)
    _, end = rest.split('<!-- v3-demo:end -->', 1)
    path.write_text(start+'<!-- v3-demo:start -->\n'+fragment+'\n<!-- v3-demo:end -->'+end)
    print('Reproduced two v3 states and rendered the public walkthrough.')


if __name__ == '__main__':
    main()
