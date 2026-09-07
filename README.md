<h1 align="center">Fantasy Draft Analyst</h1>

<p align="center"><b>Your next pick shapes your whole team. Plan for it.</b></p>

<p align="center">A free skill you download and run with Claude. Turn your league’s rules into targets, backups, and a board for draft night.</p>

<p align="center">
<b><a href="#setup">Get the skill</a></b> ·
<a href="https://github.com/nicodeguyo/fantasy-draft-analyst/raw/refs/heads/main/dist/fantasy-draft-analyst.zip">Download ZIP (v3.0.0)</a> ·
<a href="https://nicodeguyo.github.io/fantasy-draft-analyst/">See it in action</a>
</p>

<p align="center"><a href="#setup"><img src="docs/media/draft-board-demo.gif" width="480" alt="15-second draft planner tour: compare draft paths, see targets and backups, track picks, explore positional depth and tiers, and inspect an internal test across 800 simulated drafts. Ends with Get the skill. Click for download and setup."></a></p>

<p align="center">Free & open source · No coding needed with Claude · Assistant account and usage limits apply</p>

**Your scoring. Your draft slot. Your keeper—or no keeper.** Describe your league in ordinary language. The skill researches player data, plays out possible drafts, and creates your analysis and downloadable board.

Prepare a downloadable board before your draft, or run the new local live session to recalculate advice after each actual pick. The downloadable board remains a static preparation plan. The live session needs a running local Python process; neither mode syncs with your fantasy platform.

The demo uses a fictional 12-team ESPN half-PPR keeper league with saved 2026 player data. It is an example, not a live feed or advice tailored to your league. [View or download the sample HTML board](examples/sample-league/draft-board.html).

**Want this ready for draft night? [Download the skill and follow the setup](#setup).**

## What is new in v3

- A reusable evidence layer preserves player IDs, scoring, season/week, publication and fetch times, provider disagreement, missing fields and source independence. A stale or incomplete feed cannot silently become fresh consensus.
- Multiple stat projection inputs are scored in your league's rules. News has dated events and supersession links; it supplies evidence and scenarios, not unexplained point bonuses.
- Draft utility includes legal starters and explicit absence coverage. Seven receivers and three backs are no longer evaluated solely through one ideal starting lineup.
- Local live sessions track actual picks, keepers, undo/replay and data revisions. Advice uses the same roster policy and includes conditional next-turn comparisons and evidence-bound explanations.
- The downloadable skill contains its Python core. Future lineup and waiver skills can reuse it; those workflows are not shipped in this release.

[Data contract](skills/fantasy-draft-analyst/references/evidence.md) · [Live session guide](skills/fantasy-draft-analyst/references/live-draft.md) · [Architecture](docs/toolkit-architecture.md)

## What it helps you decide

- **How does this pick shape the team I finish with?** Compare players by modeled roster utility: starting strength plus explicit bench coverage and optional upside, then get a pick-by-pick plan with targets and alternatives.
- **My target’s gone. Who’s next?** Keep prepared backups in view, cross off taken players, and mark your own picks on a board you can use on your phone.
- **Which position can I afford to wait on?** See modeled availability at your picks and the projected drop in talent as the draft progresses. These are pre-draft estimates.
- **Is my keeper worth the pick?** Compare eligible keepers against each other and keeping nobody, including the round each costs. Supports zero or one keeper per team.
- **What am I missing about a player?** Ask the assistant to check role, injury, and usage claims with dated sources—and explain the case against a player you like.

On a new v3 board, `TAKE` marks the recommendation; `−14` means 14 fewer modeled roster utility points under the stated assumptions. Utility is a decision score, not a season-point forecast. The archived v2 example uses projected starting-lineup points. Your marks are saved in that browser when local storage is available.

<p align="center"><img src="docs/media/board-picks.png" width="480" alt="Sample pick table showing the recommended player and projected lineup-point differences for alternatives"></p>

## Setup

**Download the skill. Describe your league. Get your draft plan.**

New to AI tools? Start with Claude in your browser. A *skill* is a package of instructions and scripts you add to Claude. This one guides its research, runs the draft simulator, and builds your board. You describe your league in ordinary language; Claude runs the code.

1. [Follow the upload guide](docs/install.md#claude-in-your-browser-recommended) to enable code execution and upload the [packaged skill](https://github.com/nicodeguyo/fantasy-draft-analyst/raw/refs/heads/main/dist/fantasy-draft-analyst.zip).
2. Paste the league description below, replacing the brackets. “I don't know” is fine; ask Claude to help you find the setting.
3. Review the league settings and data dates, then ask Claude to generate your analysis and downloadable HTML board. Open the board before draft night and try marking a pick.

The project is free. Creating your own plan requires an assistant account and sufficient usage; its plan limits apply. Claude's upload route requires code execution. [Current prerequisites and alternatives](docs/install.md).

```text
Use the fantasy draft analyst skill to make my draft plan.
Ask me about missing settings before you simulate.

Season and draft date: [2026, date and time zone]
Platform: [ESPN / Yahoo / Sleeper / other]
League size: [number of teams]
Draft order: [snake / linear], my pick: [number], rounds: [number]
Scoring: [standard / half-PPR / PPR]
Passing TDs: [4 or 6], interceptions: [penalty]
Other scoring: [bonuses, TE premium, or none]
Starting lineup: [QB, RB, WR, TE, FLEX, superflex, K, DEF counts]
Bench spots: [number]
Keepers: [none, or number allowed and cost rules]
My keeper options: [player and round cost, or none]
Known league keepers: [draft slot, player, round cost for each; or unknown]
Players I like or want to avoid: [names and why, or none]
Draft-room tendencies: [anything I know, or unknown]
Board colors: [favorite NFL team or colors]

Use current public data and show the date and source for each input.
Tell me if any data is unavailable or any result is only an approximation.
Give me keeper advice if relevant, a pick-by-pick plan, the cost of
waiting, and a downloadable HTML board. Explain the assumptions and
which changes would alter your recommendation. Do not use the sample
league's saved player data as current data for my league.
```

Already use a coding assistant? See [Claude Code](docs/install.md#claude-code), [Codex or another coding assistant](docs/install.md#codex-or-another-coding-assistant), or [run the scripts yourself](docs/install.md#running-the-scripts-yourself). For chat without code execution, use the [paste-anywhere prompt](prompt/fantasy-draft-analyst-prompt.md); that route provides an analytical approximation, not the full simulation.

## Historical benchmark, and how we will evaluate v3

<!-- benchmark:start -->
Archived v2 benchmark (does not evaluate v3): across 800 simulated drafts, the saved-board policy produced 90 more projected starting-lineup points than the noisy ADP-based draft bot, on average.

| Drafting policy | Mean projected lineup total |
|---|---:|
| Noisy ADP-based draft bot | 1,761 |
| Saved-board policy | 1,851 |
| Adaptive heuristic | 1,864 |

**Internal simulation, not real-season results.** The metric is the sum of projections for one best legal starting lineup. The paired difference is +90.1 ± 3.5 points (approximately 95% Monte Carlo interval). This interval excludes projection and model uncertainty. Weekly substitutions, injury coverage and bench value are not scored. The baseline is our noisy ADP-based draft bot, not verified platform autopick.

The benchmark follows the same saved player order and documented fallback as the displayed board. It does not model every choice a human user might make. [Exact results and input hashes](examples/sample-league/benchmark.json).
<!-- benchmark:end -->

The saved example and comparison remain historical illustrations. New v3 recommendations include roster coverage, so their utility scores must not be compared numerically to this table. `evaluate_policy.py` supports held-out, timestamped one-pick decisions and weekly lineup choices made before outcomes are read. It is an evaluation harness, not evidence of superiority; no held-out performance result is claimed for this release. See [the architecture and evaluation boundaries](docs/toolkit-architecture.md).

## Make your next pick fit the rest of your draft

The difficult part of a draft is choosing between good players while building a complete team.

Taking a running back now changes the receivers you can target later. Your scoring, draft slot and keeper change those tradeoffs, too.

Fantasy Draft Analyst plays out possible drafts and turns that analysis into a plan: targets, backups and a board you can bring to draft night.

[Get the skill](#setup) to build a plan for your league. Want to see the idea first? The [interactive example](https://nicodeguyo.github.io/fantasy-draft-analyst/#compare) shows two paths from the same starting draft room.

The method depends on projections, modeled opponents, and the policy making later picks. You can inspect those choices and challenge the result. Read [how it works](docs/how-it-works.md), the [interactive demo methodology](docs/site/README.md), the [worked analysis](examples/sample-league/analysis.md), and the [run log with data sources](examples/sample-league/RUNLOG.md).

## What it handles

| Setting | Support |
|---|---|
| Drafts | Snake and linear; redraft and keeper leagues |
| Scoring | Standard, half-PPR, PPR, passing-TD settings and supported TE premium; unsupported bonuses require additional data and cannot be called exact |
| Lineups | QB / RB / WR / TE / K / DEF, FLEX, superflex |
| Keepers | Zero or one per team, with a round cost; compare eligible user candidates and keeping nobody; known keepers use explicit draft slots |
| Platforms | Platform-specific average draft position (ADP), when usable public data is available |

Auction has a pricing approximation in the methodology, **not a bidding simulator**. Multi-keeper optimization, best ball’s weekly scoring, and dynasty are outside the model’s scope. Unusual rules and data sources may require adjustments; the assistant should identify those before promising a complete plan.

## Reproduce every number

Requires Python 3.10+ and PyYAML. From the repository root, create an environment and reproduce the benchmark against the committed sample inputs:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pyyaml
python scripts/compare_policies.py \
  --league examples/sample-league/league.yaml \
  --players examples/sample-league/players.csv \
  --sim examples/sample-league/sim.json \
  --drafts 800
```

This command explicitly runs the legacy policy to inspect the archived comparison. New runs use `roster_v2` by default and will intentionally differ from saved v2 outputs. For new data preparation, live sessions and simulation commands, see the [script guide](docs/install.md#running-the-scripts-yourself).

## Where it can be wrong

- **Projections are assumptions.** Confident simulation results can still be wrong if player projections or the model of your draft room are wrong.
- **The board is a prepared plan.** Its recommendations and availability percentages do not update when you mark picks. An unexpected draft can make the plan less useful.
- **Policies and coverage assumptions matter.** Later picks use a heuristic. Missing expected-games inputs use an explicit default; replacement strength and optional upside assumptions can change the result.
- **Freshness depends on the run.** The assistant researches data when you ask it to; saved boards do not refresh themselves. Check dates and rerun before your draft when injuries or roles change.

## FAQ

**Do I need to code?** No for the recommended Claude upload route. You need an assistant that can execute the bundled scripts to get the full simulation and board.

**Does this connect to my live draft?** You manually enter or import actual picks into the local live session. It recalculates against that state, supports undo and resume, and exports decision receipts. It does not log into your league or sync with ESPN, Yahoo, or Sleeper.

**Redraft with no keepers?** Yes. Say “no keepers” in your league description.

**Can I share my board?** Yes. The HTML file contains your plan, so share it only with people you want to see your strategy. The public demo is safe to share as an example.

**How do I get help?** [Report a bug or setup problem](https://github.com/nicodeguyo/fantasy-draft-analyst/issues/new/choose) with a small example. You do not need to publish your private league details.

## Contributing

Useful contributions include verified public data sources, supported examples for more league formats, clearer setup instructions, and improvements to the model's later-pick policy. See [CONTRIBUTING.md](CONTRIBUTING.md) and the [changelog](CHANGELOG.md).

## Credits

<p align="center">
<a href="https://github.com/nicodeguyo/fantasy-draft-analyst/stargazers"><img src="https://img.shields.io/github/stars/nicodeguyo/fantasy-draft-analyst?style=flat&labelColor=0B1B33&color=69BE28" alt="GitHub stars"></a>
<a href="LICENSE"><img src="https://img.shields.io/github/license/nicodeguyo/fantasy-draft-analyst?style=flat&labelColor=0B1B33&color=69BE28" alt="MIT license"></a>
<img src="https://img.shields.io/badge/python-3.10%2B-69BE28?style=flat&labelColor=0B1B33" alt="Python 3.10 or newer">
<img src="https://img.shields.io/badge/dependencies-PyYAML%20only-69BE28?style=flat&labelColor=0B1B33" alt="Dependencies: PyYAML only">
<img src="https://img.shields.io/badge/example-fully%20reproducible-69BE28?style=flat&labelColor=0B1B33" alt="Fully reproducible example">
</p>

Built by Nico Neugebauer ([@nicodeguyo](https://github.com/nicodeguyo)) with Claude, for his own 14-team keeper league, then generalized. The projections, simulations and opinions are the model's; the players are real; the leagues in the examples are not. Not affiliated with the NFL, ESPN, Yahoo, Sleeper or any sportsbook. Data sources belong to their owners; respect their terms.

[MIT License](LICENSE). Use it, inspect it, improve it.
