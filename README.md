<h1 align="center">Fantasy Draft Analyst</h1>

<p align="center"><b>Every other draft tool ranks players. This one simulates your draft.</b></p>

<p align="center">You're on the clock. Four players you'd be happy with. Ten seconds.<br>
It tells you which one to take — and exactly what it costs you to take a different one.</p>

<p align="center">
<a href="https://github.com/nicodeguyo/fantasy-draft-analyst/stargazers"><img src="https://img.shields.io/github/stars/nicodeguyo/fantasy-draft-analyst?style=flat&labelColor=0B1B33&color=69BE28" alt="Stars"></a>
<a href="LICENSE"><img src="https://img.shields.io/github/license/nicodeguyo/fantasy-draft-analyst?style=flat&labelColor=0B1B33&color=69BE28" alt="License"></a>
<img src="https://img.shields.io/badge/python-3.10%2B-69BE28?style=flat&labelColor=0B1B33" alt="Python 3.10+">
<img src="https://img.shields.io/badge/dependencies-PyYAML%20only-69BE28?style=flat&labelColor=0B1B33" alt="PyYAML only">
<img src="https://img.shields.io/badge/example-fully%20reproducible-69BE28?style=flat&labelColor=0B1B33" alt="Reproducible example">
</p>

<p align="center">
<a href="#what-you-get">What you get</a> · <a href="#why-this-is-different">Why it's different</a> · <a href="#how-it-works">How it works</a> · <a href="#setup">Setup</a> · <a href="#reproduce-every-number">Reproduce it</a>
</p>

<p align="center"><img src="docs/media/board-walkthrough.gif" width="420" alt="The draft-day board in use on a phone: TAKE on the recommended player, crossing players off as they go, the lineup filling in"></p>

<p align="center"><sub>Free · MIT · Python standard library + PyYAML · Claude Code, Claude desktop, claude.ai, Codex, or any assistant</sub></p>

---

## Following it beats autopicking by 109 points

Three drafters, 800 identical simulated drafts, nothing changing but how you pick:

| Drafter in your seat | Projected starting points | Spread |
|---|---|---|
| Autopicking off the platform's rankings | 1,729 | ±81 |
| **Following this board** | **1,838** | **±19** |

**109 points is about six and a half a week, every week.** And look at the spread — autopicking isn't just worse on average, it's four times more erratic. Some seasons it hands you a broken roster and you can't know which one you drew until October.

Reproduce it yourself: `python3 scripts/compare_policies.py`. That is the simulator grading itself under its own assumptions — a fair internal comparison, not a backtest against real drafts. The repo says so wherever the number appears.

---

## See it in action

**One number per player.** `TAKE` is the pick. Everything else is priced against him in points of final starting lineup — `−14` means taking him instead costs fourteen points across the season, about one a week.

<p align="center"><img src="docs/media/board-picks.png" width="480" alt="A pick table ranked by pick value, with TAKE on the recommended player and signed deltas against him"></p>

**When to take which position, measured.** What one more turn of waiting costs you at each position. The outlined cell is the one about to run out.

<p align="center"><img src="docs/media/board-waiting.png" width="480" alt="The cost-of-waiting table: rows are your picks, columns are QB RB WR TE"></p>

**Your shortlist, pressure-tested.** Every player you like, with the case for, the honest risk, what the betting market implies, and a verdict with a price.

<p align="center"><img src="docs/media/board-calls.png" width="480" alt="Shortlist scored with verdict tags and what the betting market thinks"></p>

**And a written analysis you can argue with.** The verdict, the math behind it, the bear case, and the one assumption that would flip it — every source dated.

<p align="center"><img src="docs/media/skill-replay.gif" width="420" alt="The skill answering a keeper question: the verdict in lineup points, the pick-value table, cost of waiting, a pressure test, and the plan"></p>

---

## What you get

**Before the draft**

- **The keeper verdict**, in the same units as everything else. It simulates entire drafts under each scenario — keep him, keep the other guy, keep nobody — and compares the teams you finish with. In the worked example, keeping the round-6 running back is worth 1,864 against 1,810 for keeping nobody: 54 points, 3.2 a week, for one pick.
- **Cost of waiting.** For each of your turns and each position, what one more turn costs you. Waiting on a running back costs 47 points at your first pick and 11 by your fourth. That is the answer to "is this the round for a running back," with a number attached.
- **Tiers with cliffs**, built from real scoring gaps rather than round numbers, so you can see where paying up matters and where four players are interchangeable.
- **Your guys, pressure-tested.** Name six players you like; it checks whether your reason for liking them is actually true. In the worked example, **four of six premises were wrong or misleading** — a coach had publicly said the opposite about one player's role, and a "top-2 tight end finish" was 6th-best per game with three of his five touchdowns in one week.
- **Current data, date-stamped.** Your platform's real ADP (ESPN rooms draft nothing like Sleeper rooms), consensus projections re-scored into your exact rules, the last 72 hours of injury and role news, and betting-market win totals as a sanity check. Every source carries the date it was fetched.

**During the draft**

- **A board in your team's colors**, one HTML file, built for a phone. One green `TAKE` per pick, always the top row, always the player the written recommendation names.
- **"Can I wait on him?"** Every player shows how often he survives to your *next* pick. Under 50% turns amber: take him now or lose him.
- **It tracks your draft.** Tap a row when someone else takes a player and he greys out everywhere. Tap ✓ when you draft him and your starting lineup fills in. Close the browser mid-draft and nothing is lost.

**In writing**

- A full analysis you can argue with: the verdict, the math, the bear case, and the one assumption that would flip it — with every source dated.

---

## Why this is different

For about thirty years, every cheat sheet and draft app has answered the same way: **value-based drafting.** Find the worst player at each position who still has to start every week — "replacement level" — and score everyone by how far above him they are.

It's a genuinely good idea. Here is where it breaks.

**That number isn't measured. It's chosen.** And this year the running back projections have a cliff in them: the 37th-best back projects 132 points, the 40th projects 111. Twenty-one points across three spots.

So move the line three ranks — well inside honest disagreement between two careful analysts — and **every running back on the board gains or loses twenty points at once.**

That's not hypothetical. Two versions of this exact tool, same projections, same league, produced opposite plans. One drafted eight running backs. The other took receivers in rounds 2 and 3. Nothing about the players changed. One guessed number moved.

When your answer swings that far on a parameter nobody can pin down, the parameter is making the decision, not the evidence. The fix isn't to argue harder about where the line goes. It's to stop needing the line.

|  | Ranking tools | This |
|---|---|---|
| **Ranks by** | Value above a chosen baseline | The team you finish the draft with |
| **The baseline** | You pick it. Move it three ranks and every back moves twenty points | There isn't one |
| **Whose draft** | A generic 12-team room | Your league, your slot, your keepers, your scoring |
| **When two picks are equal** | A ranked list implies every gap matters | Says `level` — the simulation can't separate them, and neither should you |
| **Where it's wrong** | Doesn't say | Says, with numbers, in the docs |

That last row is the one I'd defend hardest. A tool that won't tell you where it's weak isn't being confident. It's being quiet.

---

## How it works

### Monte Carlo simulation, in one paragraph

Suppose you want your odds of winning a complicated board game from a particular position. You could work out the probability — but there are too many branches and the math becomes impossible. Or you could **play it out**: finish the game from that position, note who won, and do it a thousand times. The fraction you won *is* your answer, and you never wrote an equation.

That's Monte Carlo simulation: when a system is too tangled to solve directly, simulate it many times with realistic randomness and count what happens. Named after the casino, because it runs on controlled chance.

The randomness has to be realistic or none of it means anything. So the simulated opponents draft roughly the way real people do — following their platform's rankings, with noise sized to how unpredictably each specific player actually goes, a bias toward filling empty roster spots late, and a realistic pattern for when kickers and defenses come off the board.

### The method: rollouts

```
For each of your picks, and each player you might take:
  1. Simulate the draft from the start up to your pick.
  2. Put that player on your roster.
  3. Simulate the remaining ~100 picks to the end.
  4. Add up your best legal starting lineup.
  Repeat 200 times. Average it.
```

That average is the player's **pick value** — the team you end up with if you take him. Rank your options by it. Take the top one.

Notice what disappeared: no replacement level, no baseline, no parameter, no argument. Just "here are two futures, this one ends better." A final lineup total is a fact about a roster, not an opinion about a position.

Steps 1–4 are called a **rollout**, and it's the same family of technique chess and Go engines use when they play a position forward to see which move leads somewhere good. Not a coincidence — same shape of problem.

### The two things that make the numbers trustworthy

**Every candidate faces the same drafts.** Simulate each player separately and one lands in a batch where the board fell kindly while another doesn't — you'd be measuring luck. So the draft up to your pick is simulated *once* and then branched: same keepers gone, same managers making the same reaches, only your pick differs. This is called *common random numbers*, and it's the instinct behind racing two runners on the same track in the same weather.

**Each player is judged against what you'd have done anyway.** A star who falls to you one draft in five only falls when the *whole board* collapsed — the drafts where you'd have done well regardless. Compare raw averages and he gets credit for luck that had nothing to do with him. So every simulation is *also* played out with nobody forced in — a control group, borrowed straight from clinical trials. Each player is scored on the **difference** he makes in his own simulations. The luck sits in both numbers and cancels.

Without both of these the answers are visibly wrong, and there's a wrong answer in this repo's git history to prove it.

### What it optimizes for

One number: **the total points of your best legal starting lineup at the end of the draft.** Not your best player, not your bench, not "value" — the people who actually score for you. Every recommendation on the board is priced in that unit.

The long version, with the evidence: **[docs/how-it-works.md](docs/how-it-works.md)**.

---

## Setup

Everything is markdown and standard-library Python. Any agent that can read files and run code can use it.

**Claude Code**

```bash
git clone https://github.com/nicodeguyo/fantasy-draft-analyst.git
mkdir -p ~/.claude/skills && cp -r fantasy-draft-analyst/skills/fantasy-draft-analyst ~/.claude/skills/
pip install pyyaml
```

Then `/fantasy-draft-analyst`, or just describe your draft. As a plugin instead: `/plugin marketplace add nicodeguyo/fantasy-draft-analyst`, then `/plugin install fantasy-draft-analyst@fantasy-draft-analyst`.

**Claude desktop or claude.ai**

Download [`dist/fantasy-draft-analyst.zip`](dist/fantasy-draft-analyst.zip), then **Customize → Skills → + → Upload a skill**. Turn on **Settings → Capabilities → Code execution** so the simulator can run.

**Codex, or any agent that can run code**

```bash
git clone https://github.com/nicodeguyo/fantasy-draft-analyst.git
cd fantasy-draft-analyst && pip install pyyaml
```

Then point it at the skill and let it work:

> Read `skills/fantasy-draft-analyst/SKILL.md` and follow it for my league. Here are my settings: …

You get the full method including the simulator — the scripts are plain Python with no framework, and `examples/sample-league/` is a complete worked run to check against.

**Any assistant, no code execution**

Paste [`prompt/fantasy-draft-analyst-prompt.md`](prompt/fantasy-draft-analyst-prompt.md) into ChatGPT, Gemini, or a plain chat. Same reasoning, done by hand — it uses a one-pick-ahead approximation instead of full rollouts, and it tells you that's what it did.

Then say something like:

> I'm pick 7 in a 12-team half-PPR keeper league on Yahoo. Here's my roster. Who do I keep, who do I target at each pick, and build me a board for my phone.

Per-surface detail: **[docs/install.md](docs/install.md)**.

---

## What it handles

| | |
|---|---|
| **Formats** | Snake and linear drafts, any number of teams. Redraft and keeper. |
| **Keeper rules** | Same round, round minus one, round minus two, fixed round, escalating. Waiver eligibility, traded players, published keeper lists or a modelled draw. |
| **Scoring** | Standard / half / full PPR, passing-TD value, interception penalty, rushing and receiving TDs, bonuses, TE premium. |
| **Lineups** | Any combination of QB / RB / WR / TE / K / DEF, any number of FLEX, superflex. |
| **Platforms** | ESPN, Yahoo, Sleeper, CBS, NFL.com, Underdog, FFPC — anywhere with a public ADP. |

**Auction** gets a surplus-to-dollars conversion in the methodology, not a bidding engine — the simulator drafts picks, and it will say so rather than pretend. **Dynasty is out of scope**, deliberately: roster value there is age curves, contract years and rookie-pick capital, which is a different model rather than a different setting.

---

## Reproduce every number

[`examples/sample-league/`](examples/sample-league/) is a complete run on a 12-team ESPN half-PPR keeper league — real players, live data, every input and intermediate committed.

```bash
cd examples/sample-league
python3 ../../skills/fantasy-draft-analyst/scripts/draft_sim.py \
    --league league.yaml --players players.csv --sims 1500 \
    --pick-values --keeper-scenarios --out sim.json
```

Same seed, same numbers, every time. About six minutes; `--rollouts 60` gives a rough answer in under two.

[`analysis.md`](examples/sample-league/analysis.md) is the write-up · [`draft-board.html`](examples/sample-league/draft-board.html) is the board · [`RUNLOG.md`](examples/sample-league/RUNLOG.md) says where every number came from.

---

## Where it's weak

Stated here rather than discovered later:

- **Following the written plan scores 26 points below the tool's own adaptive in-draft policy.** Partly that's what committing to a plan in advance costs. Partly it's a real bias: the policy that plays out the rest of each simulation is the same heuristic, so a forced pick leaves it repairing a roster it didn't plan. It's the first thing on the v2.1 list.
- **The projections are the load-bearing assumption.** The rollouts take them as given. If they're systematically wrong, the simulation will build you the wrong roster and report a tight standard error while doing it. Precision is not accuracy.
- **The comparison above is internal.** Same projections and the same model of the room for every row. Valid as a comparison, not a claim about real drafts.

---

## FAQ

**Redraft, no keepers?** Yes — `keepers.count: 0`, or just say so.

**How current is the data?** As current as the day you run it. ADP, projections, news and betting lines are fetched at run time and every source is date-stamped. Re-run the day before your draft.

**Is it right?** It's a model with stated assumptions, not an oracle. It names the assumption everything depends on so you can disagree with it *before* the draft instead of during. Fantasy football is high-variance; a good process loses sometimes.

**Can I share the board with my league?** You can. Whether you *should* is a question for your keeper strategy.

**Why is it free?** Because the tooling to build things like this is now available to anyone, and the best way to show that is to give one away. If it wins you a league, tell someone.

---

## Contributing

Issues and PRs welcome — especially verified data sources, platform ADP quirks with evidence, keeper-rule variants the taxonomy doesn't cover, and a better rest-of-draft policy inside the rollouts (the weakest link, and [we say why](CHANGELOG.md)). See [CONTRIBUTING.md](CONTRIBUTING.md).

## Credits

Built by Nico Neugebauer ([@nicodeguyo](https://github.com/nicodeguyo)) with Claude, for his own 14-team keeper league, then generalized. The projections, simulations and opinions are the model's; the players are real; the leagues in the examples are not. Not affiliated with the NFL, ESPN, Yahoo, Sleeper or any sportsbook. Data sources belong to their owners — read their terms.

MIT License. Use it, fork it, win your league.
