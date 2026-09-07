#!/usr/bin/env python3
"""Render saved comparison data into the static homepage. Run from any folder."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    data = json.loads((ROOT / 'docs/site/pick-comparison.json').read_text())
    left, right = data['branches']
    assert len(left['starting_lineup']) == len(right['starting_lineup']) == 9
    esc = html.escape
    rows = []
    for a, b in zip(left['starting_lineup'], right['starting_lineup']):
        assert a['slot'] == b['slot']
        rows.append(f'<tr><th scope="row">{esc(a["slot"])}</th><td>{esc(a["name"])}</td><td>{esc(b["name"])}</td></tr>')
    payload = json.dumps(data).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    fragment = '''<section id="compare" class="comparison" data-sc-act="flow"><div class="wrap">
    <div class="comparison-intro"><p class="eyebrow">A worked example · Pick 5 · 12-team half PPR</p><h2>One pick.<br>Two possible teams.</h2><p>You start with the same draft room. Change your first pick, then see the team the simulator builds around it.</p></div>
    <div class="comparison-workspace" id="comparison-workspace" hidden>
    <div class="decision"><h3>Who would you take?</h3><div id="candidate-buttons" class="candidate-buttons" role="group" aria-label="Choose your first pick"></div><div class="immediate-result" aria-live="polite"><span id="result-name"></span><strong id="result-points"></strong><span id="result-difference"></span><small>Projected lineup total · one saved draft</small></div><p class="caption">Both players were available in this saved draft. __KEEPER_CONTEXT__</p><div class="decision-rule"><b>The next picks matter, too.</b><p id="branch-explanation"></p></div><p class="caption">Green rows are players who do not appear in the other starting lineup.</p><button type="button" id="share-example" class="share-button">Copy this example’s link</button><p id="share-status" role="status" class="caption"></p></div>
    <div class="lineup" aria-labelledby="lineup-heading"><div class="lineup-heading"><h3 id="lineup-heading">Your projected starting lineup</h3><span>ONE SIMULATED DRAFT</span></div><div id="lineup-rows"></div><div class="lineup-total"><span>Sum of starting-lineup projections</span><strong id="lineup-total"></strong></div><p id="lineup-status" role="status" class="caption"></p></div></div>
    <details class="saved-lineups" open><summary>See both saved lineups</summary><div class="table-scroll"><table><caption>Two branches of one draft. Projected totals: ''' + f'{left["projected_lineup_points"]:,.0f} with {esc(left["candidate"]["name"])}; {right["projected_lineup_points"]:,.0f} with {esc(right["candidate"]["name"])}.' + '''</caption><thead><tr><th>Slot</th><th>''' + esc(left['candidate']['name']) + '''</th><th>''' + esc(right['candidate']['name']) + '''</th></tr></thead><tbody>''' + ''.join(rows) + '''</tbody></table></div></details>
    <p class="model-note"><b>One example explains the method; it does not tell you which player is best.</b> These are saved projections, not actual season results. The published board averages many simulated drafts and can rank these picks differently. This example uses a fixed seed and the simulator’s adaptive later-pick policy. Later opponent picks can diverge. <a href="https://github.com/nicodeguyo/fantasy-draft-analyst/blob/main/docs/site/README.md">Inputs and reproduction</a>.</p>
    <script id="comparison-data" type="application/json">''' + payload + '''</script></div></section>'''
    keeper = data['league'].get('keeper')
    context = f"{keeper} is already kept in round {data['league']['keeper_round']}." if keeper else 'Your team has no keeper in this example.'
    fragment = fragment.replace('__KEEPER_CONTEXT__', esc(context))
    path = ROOT / 'docs/archive/v2-site.html'
    source = path.read_text()
    start, rest = source.split('<!-- demo:start -->', 1)
    _, end = rest.split('<!-- demo:end -->', 1)
    path.write_text(start + '<!-- demo:start -->\n' + fragment + '\n<!-- demo:end -->' + end)
    print('Rendered comparison into index.html')


if __name__ == '__main__':
    main()
