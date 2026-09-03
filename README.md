<h1 align="center">Fantasy Draft Analyst</h1>

<p align="center"><b>Draft like the person who always wins your league.</b><br>
A free, open-source Claude skill that prepares your fantasy football draft the way a world-class analyst would — for <i>your</i> league, <i>your</i> pick, <i>your</i> guys — and explains every decision.</p>

<p align="center">
<a href="#install-in-60-seconds">Install</a> · <a href="#how-it-thinks">How it thinks</a> · <a href="examples/sample-league/analysis.md">Example analysis</a> · <a href="docs/how-it-works.md">The data science</a> · <a href="prompt/fantasy-draft-analyst-prompt.md">Not on Claude? Use the prompt</a>
</p>

<p align="center"><img src="docs/media/skill-replay.gif" width="640" alt="The skill answering a keeper question: verdict, keeper math, replacement level, the board at pick 20, a pressure test, the target build, and the draft-day board"></p>

## What it does

Give it your league settings, your roster, your draft slot, and the players you like. It comes back with:

1. **The keeper verdict** — who to keep, the surplus math for every candidate (in points, not "he's a round-3 value"), what keeping nobody would cost, and the one thing to confirm before you commit.
2. **The one number** — replacement level per position for your exact league and scoring. It's the number almost nobody at your table has computed, and it decides the whole draft.
3. **Pick geometry** — your actual pick numbers with keeper rounds removed, the turn structure, and the keeper inflation really in force at each pick.
4. **The board** — top players at each of *your* picks, ranked by surplus, with "There %": how often each is still available at that pick across 1,500 simulated drafts.
5. **Tiers with cliffs** — grouped by real scoring gaps, with the point drop marked at every cliff.
6. **Your guys, pressure-tested** — the case for, the honest risk, what Vegas implies, and a verdict with a price ("take at 44, not before"). If your premise is wrong, it tells you.
7. **Sample drafts and the target build** — the roster to aim for, its projected total, and its known weakness with a hedge.
8. **The late-round plan** — handcuffs, next-year keeper lottery tickets, when to take K/DEF.
9. **The assumption that could flip the board** — stated plainly.
10. **A draft-day board** — one HTML page in your team's colors: sticky pick ladder, tap-to-cross-off, tiers, verdicts, appendix. Open it on your phone during the draft.

<p align="center"><img src="docs/media/board-walkthrough.gif" width="400" alt="The draft-day board: pick ladder, surplus-ranked tables with availability bars, tier boards with cliffs, shortlist verdicts"></p>

It pulls **current data** — your platform's ADP (ESPN rooms draft differently from Sleeper rooms), consensus projections re-scored in your settings, the last 72 hours of injury and role news, betting-market win totals (and player props where a free line exists), and whatever usage data is publicly available — and date-stamps every source in an appendix. It never needs a paid data subscription.

## Install in 60 seconds

**Claude.ai or the Claude desktop app (including Cowork)**

1. Download [`dist/fantasy-draft-analyst.zip`](dist/fantasy-draft-analyst.zip).
2. In Claude, open **Customize → Skills → + → Create skill → Upload a skill** and upload the zip. Make sure **Settings → Capabilities → Code execution and file creation** is on so the simulator can run.
3. Start a chat: *"I'm pick 7 in a 12-team half-PPR keeper league on Yahoo. Here's my roster…"*

**Claude Code**

```bash
git clone https://github.com/nicoandmelissa/fantasy-draft-analyst.git
mkdir -p ~/.claude/skills && cp -r fantasy-draft-analyst/skills/fantasy-draft-analyst ~/.claude/skills/
pip install pyyaml
```

Then `/fantasy-draft-analyst` in any session, or just describe your draft. Or install it as a plugin: `/plugin marketplace add nicoandmelissa/fantasy-draft-analyst` then `/plugin install fantasy-draft-analyst@fantasy-draft-analyst`.

**Not on Claude?** Paste [`prompt/fantasy-draft-analyst-prompt.md`](prompt/fantasy-draft-analyst-prompt.md) into ChatGPT, Gemini, or any assistant with web browsing. Same method, pencil-and-paper math instead of the simulator.

Full instructions, including what each surface can and can't run: [docs/install.md](docs/install.md).

## Use it

Describe your league in a sentence and answer the intake questions, or copy [`skills/fantasy-draft-analyst/league.example.yaml`](skills/fantasy-draft-analyst/league.example.yaml), fill it in, and say *"here's my league.yaml"*. Things that change the answer, so it will ask if you don't say: platform, number of teams, your slot, scoring (PPR value, passing-TD points, interception penalty), the starting lineup and flex slots, the keeper rule, how you acquired each player on your roster, and the draft date.

Good prompts:

- *"Who should I keep and why? Explain who I'm sacrificing if I keep nobody."*
- *"Run the draft 10 times from my slot. Which roster are you happiest with and why?"*
- *"Pressure-test these six guys my buddy swears by."*
- *"Build me a draft-day board in Bills colors I can use on my phone."*

## The example

[`examples/sample-league/`](examples/sample-league/) is a complete run on a fictional 12-team half-PPR keeper league on ESPN, pick 5, produced September 3, 2026 with real players and live data:

- [`analysis.md`](examples/sample-league/analysis.md) — the full written analysis (keeper verdict, the one number, the board at every pick, tiers, six pressure tests, sample drafts, the target build, assumptions, sourced appendix).
- [`draft-board.html`](examples/sample-league/draft-board.html) — the draft-day board (download and open; Seahawks colors).
- [`league.yaml`](examples/sample-league/league.yaml), [`players.csv`](examples/sample-league/players.csv), [`sim.json`](examples/sample-league/sim.json), [`notes.json`](examples/sample-league/notes.json) — every input and intermediate, so you can reproduce it.
- [`RUNLOG.md`](examples/sample-league/RUNLOG.md) — where every number came from.

Three things it found in that run, which is roughly what it finds every time: four of the six "my guys" premises were wrong or misleading (the coach had publicly said the opposite about one player's role; a "TE2 finish" was TE6 per game, with three of his five touchdowns in one week); ESPN's room takes tight ends a full round earlier than mock drafts, which turned "wait on TE" into "take one at 20"; and the keeper that *felt* right (a round-2 WR) was 71 points worse than the keeper the math chose (a round-6 RB who became a first-round player).

<p align="center"><img src="docs/media/board-calls.png" width="560" alt="Shortlist scored with verdict tags and what the betting market thinks"></p>

## How it thinks

Five ideas do almost all the work. The long version, with the math and the evidence, is in [docs/how-it-works.md](docs/how-it-works.md).

**Surplus, not projection.** A player's value is how many points he scores *over the player you'd otherwise start*. In a 14-team, two-flex league the 40th running back scores about 111 and the 44th receiver about 139, so a receiver projecting 215 can be a worse pick than a back projecting 211. Every table is ranked by surplus.

**Price the market you're actually in.** ADP is the average drafter's price. Your room follows its platform's default rankings: ESPN drafts elite QBs and TEs a round early and lets receivers slide; Sleeper takes the top QBs early and mid-tier QBs very late; Underdog inflates the late rounds. The skill fetches the ADP for your platform and re-runs the availability model on it.

**Keeper inflation is front-loaded.** With twelve keepers gone, pick 20 buys roughly the ADP-28 player — but a round-6 pick buys a true round-6 player, because every forfeited pick puts someone back on the board. The simulator measures the inflation actually in force at each of your picks instead of guessing.

**Availability is a probability, not a hope.** 1,500 simulated drafts with ADP-noise opponents and realistic keeper removals give a "There %" for every player at every one of your picks. Below 50%, plan for him being gone. Above 80%, don't reach — he'll be there next time.

**Say the bear case out loud.** Every verdict comes with the strongest argument against it and the one fact that would change it. That is how you avoid the season-losing mistake, which is almost always a confident pick made without checking the checkable thing.

## What's under the hood

```
skills/fantasy-draft-analyst/
├── SKILL.md                    the workflow: intake → data → projections → replacement level → keeper verdict → board → pressure tests → sample drafts → board
├── league.example.yaml         every league setting, documented
├── references/
│   ├── methodology.md          the reasoning (replacement level, surplus, keeper math, inflation, tiers, reach rules, superflex, auction)
│   ├── metrics.md              what predicts and what doesn't, how to weight it, how to use Vegas
│   ├── data-sources.md         verified URLs per platform, fetch order, freshness rules, platform quirks
│   ├── keeper-rules.md         the taxonomy of keeper rules and how each changes the math
│   ├── draft-slot-playbook.md  early / middle / late slots, turn by turn
│   ├── output-spec.md          the exact output contract and the board's notes schema
│   └── glossary.md
└── scripts/
    ├── fetch_adp.py            ADP from FantasyFootballCalculator, ESPN, Footballguys (all platforms), Sleeper trending
    ├── scoring.py              stat lines → points in your scoring
    ├── merge_adp.py            reprice a player pool with your platform's ADP
    ├── draft_sim.py            the Monte Carlo: replacement levels, keeper surplus, inflation, availability, sample drafts
    └── build_board.py          the draft-day board (32 NFL team palettes built in)
```

Standard library plus PyYAML. The scripts run in Claude Code and wherever Claude can execute code; without them the skill does the same analysis with an analytical shortcut (a normal-distribution availability estimate), and says so.

## FAQ

**Does it work for redraft leagues with no keepers?** Yes — set `keepers.count: 0` or just say so. Superflex, 2QB, TE-premium, and best ball are handled; auction gets a dollar-conversion section; dynasty is out of scope.

**How current is the data?** As current as the day you run it. It fetches ADP, projections, news, and lines at run time and prints the date of every source. Re-run the day before your draft.

**Is it right?** It's a model with stated assumptions, not an oracle. It will tell you which assumption everything depends on (usually the RB-versus-WR replacement gap) so you can disagree with it before the draft instead of during. Fantasy football is high-variance; a good process loses sometimes.

**Which platforms?** ESPN, Yahoo, Sleeper, CBS, NFL.com, Underdog, FFPC — anywhere with a public ADP. See [`references/data-sources.md`](skills/fantasy-draft-analyst/references/data-sources.md).

**Can I share the board with my league?** You can. Whether you *should* is a question for your keeper strategy.

**Why is it free?** Because the tooling to build things like this is now available to anyone, and the best way to show that is to give one away. If it wins you a league, tell someone.

## Contributing

Issues and PRs welcome — especially new verified data sources, platform ADP quirks with evidence, and keeper-rule variants the taxonomy doesn't cover. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Credits and license

Built by Nico Neugebauer ([@nicoandmelissa](https://github.com/nicoandmelissa)) with Claude, for his own 14-team keeper league, then generalized. The projections, simulations, and opinions are the model's; the players are real; the leagues in the examples are not. Not affiliated with the NFL, ESPN, Yahoo, Sleeper, or any sportsbook. Data sources belong to their owners — read their terms.

MIT License. Use it, fork it, win your league.
