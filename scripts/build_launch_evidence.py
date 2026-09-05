#!/usr/bin/env python3
"""Refresh repeated benchmark claims and record sources for every launch export."""
from pathlib import Path
import hashlib
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]

def replace_section(path, name, body):
    source = path.read_text()
    start, end = f'<!-- {name}:start -->', f'<!-- {name}:end -->'
    if start not in source or end not in source:
        raise ValueError(f'Missing {name} markers in {path}')
    before, rest = source.split(start, 1)
    _, after = rest.split(end, 1)
    path.write_text(before + start + '\n' + body + '\n' + end + after)

def main():
    result = json.loads((ROOT/'examples/sample-league/benchmark.json').read_text())
    policies = result['policies']
    baseline, board, adaptive = policies
    improvement = board['vs_baseline']
    direction = 'more' if improvement >= 0 else 'fewer'
    gain = f'{abs(improvement):,.0f}'
    n = result['drafts']
    interval = board['paired_half_width']
    metric = 'sum of projections for one best legal starting lineup'
    claim = f'Across {n:,} simulated drafts, the saved-board policy produced {gain} {direction} projected starting-lineup points than the noisy ADP-based draft bot, on average.'
    benchmark_rows = ''.join(f'<div class="{("board-result" if i==1 else "")}"><span>{html.escape(p["name"])}</span><b>{p["mean"]:,.0f}</b></div>' for i,p in enumerate(policies))
    fragment = f'''<section class="evidence"><div class="wrap evidence-layout"><div><p class="eyebrow">Internal simulation · reproducible results</p><h2>A model you can<br>check yourself.</h2><p>{html.escape(claim)}</p><p class="caption">Metric: {metric}. Uses the same saved projections and opponent model. This is not a real-world backtest or a comparison with another draft assistant.</p><a class="text-link" href="https://github.com/nicodeguyo/fantasy-draft-analyst#reproduce-every-number">Reproduce the benchmark →</a></div><div class="benchmark" aria-label="Mean projected starting-lineup totals across {n} drafts">{benchmark_rows}<p class="caption">Paired Monte Carlo interval for the board’s difference: ±{interval:.1f} points (approximately 95%). This measures simulation sampling noise, not uncertainty in projections or model assumptions. Weekly substitutions and bench coverage are not scored.</p></div></div></section>'''
    replace_section(ROOT/'index.html','benchmark',fragment)
    md = f'''{claim}\n\n| Drafting policy | Mean projected lineup total |\n|---|---:|\n''' + '\n'.join(f'| {p["name"]} | {p["mean"]:,.0f} |' for p in policies) + f'''\n\n**Internal simulation, not real-season results.** The metric is the {metric}. The paired difference is {improvement:+.1f} ± {interval:.1f} points (approximately 95% Monte Carlo interval). This interval excludes projection and model uncertainty. Weekly substitutions, injury coverage and bench value are not scored. The baseline is our noisy ADP-based draft bot, not verified platform autopick.\n\nThe benchmark follows the same saved player order and documented fallback as the displayed board. It does not model every choice a human user might make. [Exact results and input hashes](examples/sample-league/benchmark.json).'''
    readme=ROOT/'README.md'
    if '<!-- benchmark:start -->' in readme.read_text(): replace_section(readme,'benchmark',md)
    source_paths = ['examples/sample-league/league.yaml','examples/sample-league/players.csv','examples/sample-league/sim.json','examples/sample-league/notes.json','examples/sample-league/benchmark.json','docs/site/pick-comparison.json','skills/fantasy-draft-analyst/scripts/draft_sim.py','skills/fantasy-draft-analyst/scripts/build_board.py','scripts/compare_policies.py']
    manifest = {'sample':'The Sample League','projection_data_date':'2026-09-03 (saved analyst-authored inputs, not a current-data refresh)','metric':metric,'benchmark_claim':claim,'benchmark_source':'examples/sample-league/benchmark.json','comparison_source':'docs/site/pick-comparison.json','availability_definition':'Unconditional frequency before the draft; includes drafts where the player was taken by the simulated user. Not pass-up survival.','sources_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in source_paths},'regeneration_commands':['python3 skills/fantasy-draft-analyst/scripts/draft_sim.py --league examples/sample-league/league.yaml --players examples/sample-league/players.csv --sims 1500 --samples 10 --pick-values --keeper-scenarios --out examples/sample-league/sim.json','python3 scripts/compare_policies.py --league examples/sample-league/league.yaml --players examples/sample-league/players.csv --sim examples/sample-league/sim.json --notes examples/sample-league/notes.json --drafts 800 --output examples/sample-league/benchmark.json','python3 scripts/reproduce_demo.py --repo . --output docs/site/pick-comparison.json','python3 scripts/build_demo.py','python3 scripts/build_launch_evidence.py']}
    (ROOT/'docs/site/launch-evidence.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(claim)

if __name__=='__main__': main()
