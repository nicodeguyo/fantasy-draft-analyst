---
name: fantasy-draft-analyst
description: Build a fantasy football draft plan using league-specific projections, simulated draft continuations, pre-draft availability, keeper scenarios, and an interactive HTML board. Use for draft preparation, keeper decisions, pick comparisons, tiers, shortlist research, and draft-board generation. Supports snake or linear redraft and single-keeper leagues with configurable scoring and lineups.
license: MIT
metadata:
  version: "2.0.1"
  author: "Nico Neugebauer"
  homepage: "https://github.com/nicodeguyo/fantasy-draft-analyst"
---

# Fantasy Draft Analyst

Help the user explore what a pick does to the rest of their draft: you judge a pick by **the starting lineup it leaves you with** rather than by the player's raw projection, you price the **market you are actually drafting in** (this platform, this many teams, these keepers gone), and you say the honest bear case out loud before you commit.

Read `references/methodology.md` before the first real analysis — it is the reasoning this skill is built on — and use the other references when the workflow points to them.

## What the user gets

One package, in this order (the full contract with templates is in `references/output-spec.md`):

1. **The keeper verdict** (keeper leagues only) — who to keep, the surplus math for every candidate, what keeping nobody would cost, and the one thing to confirm before committing.
2. **Cost of waiting** — the modeled change in available positional depth between the user's picks. Explain roster fit alongside the estimated projection drop; replacement level and surplus provide context for positional depth.
3. **Pick geometry** — the user's actual pick numbers, the turn structure, and what the keeper removals do to the board.
4. **The board** — top five at each of the user's picks, ranked by **pick value**: the projected final starting lineup if they take that player and draft sensibly afterwards. Each row shows its modeled difference from the prepared target, and pre-draft availability at the following pick. That frequency is unconditional, not a probability of survival after passing on a player who is available now.
5. **Tiers with cliffs** — by position, grouped by gaps in the input projections, with the point drop marked at every cliff.
6. **Your guys, pressure-tested** — every player the user flagged: the case for, the honest risk, what the betting market implies, and a verdict with a price ("take at 48, not before").
7. **Sample drafts and the target build** — several simulated drafts, the roster to aim for, its projected total, and its known weakness.
8. **The late-round plan** — handcuffs, next-year keeper lottery tickets, when to take K/DEF.
9. **Assumptions and sensitivity** — the one assumption that could flip the board, stated plainly.
10. **The draft-day board** (optional, when the user wants something to have open during the draft) — a single HTML page in their team's colors, built with `scripts/build_board.py`.

Deliver 1–9 as a written analysis in chat (or a markdown file if it's long). Offer 10 at the end; build it immediately if they already asked for something to use on draft day.

## Workflow

### Step 1 — Intake (don't analyze until you have these)

Collect the league facts. Most users give half of them; ask for the rest in **one** message, grouped, with sensible defaults offered so they can answer in a sentence. Missing facts change answers: passing-TD points change quarterback projections, extra flex slots change positional demand, and keeper eligibility can eliminate a candidate.

| Fact | Why it matters | Default if unstated |
|---|---|---|
| Platform (ESPN / Yahoo / Sleeper / CBS / NFL / Underdog / FFPC / other) | Determines which ADP to price against — drafters follow their platform's default ranks | Ask |
| Number of teams | Sets pick numbers and replacement level | 12 |
| Draft slot, snake vs linear vs auction | Pick geometry | Ask (auction: see `references/methodology.md` § Auction) |
| Scoring: PPR value, pass TD points, INT penalty, rush/rec TD points, bonuses, TE premium | Projections must be scored in *this* system | Half-PPR, 4-pt pass TD, −2 INT, 6-pt rush/rec TD |
| Starting lineup: QB, RB, WR, TE, FLEX count and eligibility, superflex/OP, K, DEF | Replacement level is derived from it | 1/2/2/1/1 flex/1/1 |
| Keeper rules: how many, cost basis (same round / round earlier / escalating / fixed), waiver-pickup eligibility, trades, max years kept, when keepers are declared | Decides the keeper verdict | No keepers |
| User's current roster with how each player was acquired and the round | Keeper candidates | Needed for keeper leagues |
| Players the user likes ("my guys") | Pressure-test list | Optional |
| Draft date | Governs data freshness | Ask |
| Anything about their leaguemates’ tendencies (QB-early league, homers, etc.) | Context for sensitivity analysis; prose preferences alone do not change the simulator | Optional |

Supported simulator scope: zero or one keeper per team, with one round cost and an explicit draft slot for each published keeper. Multi-keeper, traded keeper-pick costs, best-ball weekly scoring, and auction bidding require a different model; identify the mismatch during intake.

If the user hands you a `league.yaml` (template: `league.example.yaml`), read it and confirm only what's ambiguous.

### Step 2 — Get current data, and say where it came from

Stale data is the most common way this analysis goes wrong; a player's role can change between Tuesday and Thursday of draft week. Pull fresh inputs and date-stamp every source in the appendix. `references/data-sources.md` lists the URLs that work without a login, by platform, with a fetch order and fallbacks.

Minimum set:

- **ADP for the user's platform.** Verify current differences rather than assuming a platform always favors a particular position; `references/data-sources.md` lists source options. If platform ADP isn't reachable, use the format-matched FantasyFootballCalculator ADP and say so.
- **Season projections** with stat lines (FantasyPros consensus works without login), which you then **re-score** into the league's points with `scripts/scoring.py` or by hand — never trust a vendor's point total when the scoring differs.
- **Injury and depth-chart news from the last 72 hours** for every player who appears in the board, tiers, or the user's list.
- **Vegas**: team win totals, and player season props where available — used as a sanity check on medians, not as projections.
- **Usage data** (route share, target share, snap share, red-zone share) for pressure-tested players, from whichever free source is reachable; fall back to 2025 advanced stats.

Write the player pool to `players.csv` (`name,pos,team,adp,adp_sd,proj`) — this is the input every script reads. Include enough depth for the league: at least (teams × 15) players plus a full K and DEF slate. If you started from mock ADP (which gives the spread) and then found the platform's ADP, reprice with `python3 scripts/merge_adp.py --players players.csv --adp adp_platform.csv --out players.csv` — projections stay, prices change, and the appendix should say how deep the platform prices go.

### Step 3 — Build projections in the league's scoring

Start from consensus stat lines, then adjust where you have a reason: a role change, a new coordinator, an injury discount expressed as expected games, a coaching quote about usage. Every adjustment gets a one-line reason. Projections are season totals, not per-game. Run `python3 scripts/scoring.py --league league.yaml --stats stats.csv --out players.csv` when scripts are available; otherwise score by hand and show the formula once.

### Step 4 — Run the rollout engine

This is the step that makes you different from the table. The question at a pick is not "who is worth more" — it is **which of these players leaves me with the best starting lineup once the draft finishes**. Answer it by simulating: draft up to the user's pick, take each candidate in turn, play the rest of the draft out, and score the lineup. That is **pick value**, and its final score is the sum of projections for one best legal starting lineup. Replacement assumptions still influence candidate selection and later drafting decisions.

```
python3 scripts/draft_sim.py --league league.yaml --players players.csv --sims 1500 \
    --pick-values --keeper-scenarios --out sim.json
```

With `--keeper-scenarios`, eligible keeper scenarios run first and automatic selection uses the highest simulated mean among the top four surplus candidates plus nobody. Explicit `--keeper NAME` or `--no-keeper` overrides this. Without scenarios, auto selection uses positive isolated surplus. Inspect the shortlist and evaluate a relevant omitted candidate separately.

Defaults: 200 rollouts per candidate, 8 candidates a pick, through round 9, and a plan target must be available at least half the time (`--rollouts`, `--candidates`, `--through-round`, `--plan-min-avail`). Allow several minutes depending on league size and hardware; `--rollouts 60` is a quicker, noisier estimate, `--no-pick-values` skips the rollouts. It writes `pick_values`, `plan_path` (the greedy plan with a Plan B and an "if he falls" upside per pick), `cost_of_waiting` and `keeper_scenarios`, plus everything v1 produced: the pick ladder with keeper rounds removed, inflation in force at each pick, availability (the user's own players and "my guys" always included), the full name × pick matrix (`sim_availability.csv`), replacement levels and sample drafts.

Three things to read before writing anything. `plan_check` — if it failed the plan doesn't fill a legal lineup and isn't a plan yet. The standard errors describe Monte Carlo noise under the fixed model, not uncertainty in projections. For a small gap, say “no clear model preference”; the board’s “close” label means an absolute gap below one projected point, a rounding convention rather than statistical equivalence. And the scale: a pick value is the lineup projected **at that pick**, measured against a control arm that already assumes the plan was followed to get there, so the column drifts down. Compare candidates within a pick, never across picks, and never against a keeper-scenario total.

Re-run whenever `players.csv` changes; a stale `sim.json` is worse than none. Without scripts, use dynamic VBD and the availability shortcut in `references/methodology.md` §6. Say which method you used.

### Step 5 — The keeper verdict

Lead with `keeper_scenarios`: the mean projected final starting lineup across full drafts under each scenario — keep X, keep Y, keep nobody — with standard errors. Use those separate scenario comparisons to inform the verdict; do not subtract a scenario total from a pick-table value. Inspect differences alongside their Monte Carlo uncertainty and explain fragile choices; scenario marginal SEs alone do not supply a paired significance test.

Then explain it with the per-candidate table: cost (the pick number they'd consume), market value (their ADP on this platform), the keeper inflation estimated at that pick from the current run, and the surplus **in points**, because points-per-pick is steepest at the top of the board. The same number of picks can represent very different projection gaps at different points in the draft.

Then check the things that flip the answer: waiver-pickup eligibility, superflex (which changes quarterback demand), escalating costs, the option to keep nobody. State the verdict first, the math second, the bear case third, and "the one thing you must confirm" last.

### Step 6 — Board, tiers, and the plan by pick

Start with **cost of waiting** (`cost_of_waiting`): the modeled drop in best available positional surplus between each pair of user picks. Describe where the current output shows larger drops and where it shows relatively stable depth. Use these estimates to prepare positional alternatives alongside roster needs; they do not determine a live choice or establish that a position will run out. Recompute for the league's scoring and slots instead of hard-coding a position order. Replacement cancels in the direct difference, but changed assumptions can still affect simulated draft paths.

Then present the top five at each pick **ranked by pick value**, with each row's gap against the player you're recommending and the “pre-draft availability at the next pick” number. Write one decision sentence and a Plan B per pick using the current generated names and pre-draft frequencies. For small estimated gaps, describe limited model preference; the displayed “close” means less than one projected point. Discuss roster fit and role assumptions rather than deciding from the decimal alone. Build tiers from projection gaps, not rounds; mark each cliff with the point drop. The tiers keep the surplus column — labeled "vs. free" — because it is the clearest view of which positions are deep; it is explanation, not the ranking. Note tiers that span broad ADP windows and explain whether that offers useful alternatives under the current inputs.

For a reach, explain the role evidence and opportunity cost of choosing earlier than ADP. Use pre-draft availability as preparation context. A live pass-or-pick decision also depends on the current board, roster needs, and the alternative you would take; unconditional availability does not resolve it.

### Step 7 — Pressure-test the user's guys

For each flagged player, in this order: what the user's premise is and whether it's factually right (fix it if not); the case for, with usage numbers; the honest risk; what Vegas implies (win total, props); and a verdict with a price. Weight metrics by predictive value — `references/metrics.md` ranks them and explains why route share beats yards per route run on small samples. Add two or three names the user didn't list that fit their windows better.

### Step 8 — Sample drafts and the target build

Run the simulator's sample drafts (or reason through three by hand). They are illustrative — the simulated "you" drafts by the math, not by judgment — so read them for the patterns that recur, then write the target build yourself. Report the range of projected starter points, the most-owned players across runs, what happened in essentially every draft (e.g., "QB always waited"), the roster you'd actually target (every pick realistically reachable), why that one, and its known weakness with a hedge.

### Step 9 — Late rounds, assumptions, and the honest close

Late rounds: handcuffs to the user's own starters (defensive value in deep leagues with thin waivers), second-year players with a path to volume, and — in keeper leagues where waiver pickups can't be kept — the reminder that a round-11 breakout becomes next year's cheapest keeper. Make late-round targets explicit in the displayed board. The board-following policy uses displayed order including expanded alternatives, configured exclusions, position caps, and a legal-lineup reservation rule, then the documented shared surplus fallback. The adaptive rollout heuristic is a separate policy that normally delays K/DEF.

Close with the assumption that could flip the board (such as a key projection, keeper rule, or opponent assumption), what would change if it is wrong, and explain how a different opponent strategy could change it. Neither more falling value nor a particular direction of error is guaranteed.

### Step 10 — The draft-day board (optional)

`python3 scripts/build_board.py --league league.yaml --sim sim.json --notes notes.json --players players.csv --out draft-board.html` renders the board. Write `notes.json` first (schema in `references/output-spec.md`): the plan (target at every pick with a Plan B — the renderer fills in the values from `plan_path`), the cost-of-waiting sentence (`waiting_note`), the decision sentence and Plan B per pick, tier commentary and cliffs, shortlist verdicts, Vegas notes, and the assumptions. Use the generated board policy as the source of ordering, including target promotion and late-round fallback. Check every written recommendation against the rendered table; narrative notes can otherwise disagree with generated values. The board opens with a four-step "how to use this on draft day" strip and the plan; it tracks the user's lineup as they tap ✓ on their picks, and saves state when browser storage is available. Test persistence in the intended browser before draft night. The board uses the user's team colors (`theme` in league.yaml, any NFL team or custom hex), provides a print layout, and lets the user tap players to cross them off during the draft.

## How to write it

- Verdict first, then the math, then the bear case, then the caveats. The user is reading this on their phone twenty minutes before the draft.
- Quantify modeled projected-lineup differences. Explain that one fixed lineup is scored; report draft-to-draft variation as draft-model variation. Real weekly gains and season consistency require weekly substitution and injury modeling.
- Every number that came from somewhere gets a source and a date. Projections you built are "mine"; say so.
- Correct the user's premises when they're wrong ("that stat is Luther Burden's, not Flowers'"). They flagged the player because they trust you to check.
- Explain *why* at every decision. The reader should be able to disagree with a specific assumption, not just with the conclusion.
- State frequency and denominator: “Available in 34% of simulated drafts before this pick.” Treat 0% and 100% as finite-sample frequencies, not certainty.
- Never fake freshness. If the newest ADP you could reach is a week old, say so and adjust for it.

## When scripts can't run

Without scripts, provide an explicitly labeled analytical approximation. In a chat-only environment use **dynamic VBD** — the same idea as the rollouts, one pick ahead, by hand: a player's take-now value is his projection minus the projection of the best player *at his own position* you expect to still be there at your next pick, then filtered by which of your lineup slots are still open. Estimate "still be there" with the normal-distribution shortcut in `references/methodology.md` §6. Compute pick numbers and replacement level by hand for the tiers and the explanation, reason through three sample drafts explicitly, and skip the HTML board (offer a printable markdown board instead). Explain the different assumptions; the approximation has not been validated as equivalent to the scripted rollouts.

## Reference files

- `references/methodology.md` — the reasoning: pick value by rollout, cost of waiting, keeper math and inflation, replacement level and surplus (what they still explain), scarcity, tiers and cliffs, pick geometry, reach rules, auction and superflex notes, the availability shortcut and dynamic VBD. **Read first.**
- `references/metrics.md` — which player metrics predict, which don't, how to weight them, how to use Vegas lines.
- `references/data-sources.md` — verified URLs by platform, fetch order, freshness rules, platform ADP quirks.
- `references/keeper-rules.md` — a taxonomy of keeper rules and exactly how each changes the math.
- `references/draft-slot-playbook.md` — what early, middle, and late slots look like in 10/12/14-team leagues, turn by turn.
- `references/output-spec.md` — the full output template, the `notes.json` schema for the board, and worked examples of each section.
- `references/glossary.md` — plain-language definitions for the appendix.
- `league.example.yaml` — the config template with every option documented.

## Scripts

- `scripts/fetch_adp.py` — ADP from FantasyFootballCalculator (with spread), ESPN's API, the Footballguys cross-platform table, or Sleeper trending. Needs network from the shell; when that's unavailable, fetch the pages yourself and write `adp.csv`.
- `scripts/scoring.py` — stat lines → points in the league's scoring, merged with ADP into `players.csv`.
- `scripts/merge_adp.py` — reprice `players.csv` with a platform's ADP, keeping projections and spread.
- `scripts/draft_sim.py` — the Monte Carlo: pick values by rollout, the plan path, cost of waiting, keeper scenarios, replacement levels, inflation, availability, sample drafts. Flags worth knowing: `--pick-values` / `--no-pick-values`, `--rollouts`, `--candidates`, `--through-round`, `--keeper-scenarios`, `--watch`, `--seed`.
- `scripts/build_board.py` — the draft-day board HTML from `sim.json` + `notes.json`.

All are standard library plus PyYAML. Run them with `${CLAUDE_SKILL_DIR}/scripts/...` in Claude Code.
